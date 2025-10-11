from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from app.database.connection import get_db

router = APIRouter(prefix="/share-classes", tags=["share_classes"])

@router.get("/search")
async def search_share_classes(
    sc_id: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    distribution: Optional[str] = Query(None),
    fund_id: Optional[str] = Query(None),
    subfund_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Searches share classes using multiple optional filters with pagination support.
    Returns share classes with associated fund and subfund information based on filter criteria.
    """
    
    where_clauses = []
    params = {}
    
    if sc_id:
        where_clauses.append("sc.sc_id CONTAINS $sc_id")
        params['sc_id'] = sc_id
    
    if currency:
        where_clauses.append("sc.currency = $currency")
        params['currency'] = currency
    
    if distribution:
        where_clauses.append("sc.distribution = $distribution")
        params['distribution'] = distribution
    
    if fund_id:
        where_clauses.append("f.fund_id = $fund_id")
        params['fund_id'] = fund_id
    
    if subfund_id:
        where_clauses.append("sf.subfund_id = $subfund_id")
        params['subfund_id'] = subfund_id
    
    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Calculate skip
    skip = (page - 1) * page_size
    params['skip'] = skip
    params['limit'] = page_size
    
    # Get total count
    count_query = f"""
    MATCH (sc:ShareClass)
    OPTIONAL MATCH (f:Fund)-[:HAS_SHARE_CLASS]->(sc)
    OPTIONAL MATCH (sf:SubFund)-[:HAS_SHARE_CLASS]->(sc)
    WHERE {where_clause}
    RETURN count(DISTINCT sc) as total
    """
    
    count_result = db.run(count_query, **params)
    total = count_result.single()['total']
    
    # Get data
    query = f"""
    MATCH (sc:ShareClass)
    OPTIONAL MATCH (f:Fund)-[:HAS_SHARE_CLASS]->(sc)
    OPTIONAL MATCH (sf:SubFund)-[:HAS_SHARE_CLASS]->(sc)
    WHERE {where_clause}
    RETURN sc, f, sf
    ORDER BY sc.sc_id
    SKIP $skip
    LIMIT $limit
    """
    
    result = db.run(query, **params)
    
    share_classes = []
    for record in result:
        sc = dict(record['sc'])
        sc['fund'] = dict(record['f']) if record['f'] else None
        sc['subfund'] = dict(record['sf']) if record['sf'] else None
        share_classes.append(sc)
    
    return {
        'share_classes': share_classes,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }

@router.get("/")
async def list_share_classes(
    skip: int = 0,
    limit: int = 10,
    db = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Retrieves all share classes with basic pagination using skip and limit parameters.
    Returns list of share classes with their associated fund and subfund relationships.
    """
    query = """
    MATCH (sc:ShareClass)
    OPTIONAL MATCH (f:Fund)-[:HAS_SHARE_CLASS]->(sc)
    OPTIONAL MATCH (sf:SubFund)-[:HAS_SHARE_CLASS]->(sc)
    RETURN sc, f, sf
    ORDER BY sc.sc_id
    SKIP $skip
    LIMIT $limit
    """
    
    result = db.run(query, skip=skip, limit=limit)
    
    share_classes = []
    for record in result:
        sc = dict(record['sc'])
        sc['fund'] = dict(record['f']) if record['f'] else None
        sc['subfund'] = dict(record['sf']) if record['sf'] else None
        share_classes.append(sc)
    
    return share_classes

@router.get("/{sc_id}")
async def get_share_class(sc_id: str, db = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves a specific share class by ID with complete relationship data.
    Returns share class with fund, subfund, and management entity information or raises 404 if not found.
    """
    query = """
    MATCH (sc:ShareClass {sc_id: $sc_id})
    OPTIONAL MATCH (f:Fund)-[:HAS_SHARE_CLASS]->(sc)
    OPTIONAL MATCH (sf:SubFund)-[:HAS_SHARE_CLASS]->(sc)
    OPTIONAL MATCH (f)-[:MANAGED_BY]->(m:ManagementEntity)
    RETURN sc, f, sf, m
    """
    
    result = db.run(query, sc_id=sc_id)
    record = result.single()
    
    if not record:
        raise HTTPException(status_code=404, detail=f"Share class with ID {sc_id} not found")
    
    sc = dict(record['sc'])
    sc['fund'] = dict(record['f']) if record['f'] else None
    sc['subfund'] = dict(record['sf']) if record['sf'] else None
    sc['management_entity'] = dict(record['m']) if record['m'] else None
    
    return sc