from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from app.database.connection import get_db

router = APIRouter(prefix="/funds", tags=["funds"])

@router.get("/search")
async def search_funds(
    fund_code: Optional[str] = Query(None),
    fund_id: Optional[str] = Query(None),
    isin: Optional[str] = Query(None),
    fund_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    mgmt_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Searches funds using multiple optional filters with pagination support.
    Supports partial matching on fund_code and isin, exact matching on other fields.
    """
    
    where_clauses = []
    params = {}
    
    if fund_code:
        where_clauses.append("f.fund_code CONTAINS $fund_code")
        params['fund_code'] = fund_code
    
    if fund_id:
        where_clauses.append("f.fund_id = $fund_id")
        params['fund_id'] = fund_id
    
    if isin:
        where_clauses.append("f.isin_master CONTAINS $isin")
        params['isin'] = isin
    
    if fund_type:
        where_clauses.append("f.fund_type = $fund_type")
        params['fund_type'] = fund_type
    
    if status:
        where_clauses.append("f.status = $status")
        params['status'] = status
    
    if mgmt_id:
        where_clauses.append("f.mgmt_id = $mgmt_id")
        params['mgmt_id'] = mgmt_id
    
    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Calculate skip
    skip = (page - 1) * page_size
    params['skip'] = skip
    params['limit'] = page_size
    
    # Get total count
    count_query = f"""
    MATCH (f:Fund)
    WHERE {where_clause}
    RETURN count(f) as total
    """
    
    count_result = db.run(count_query, **params)
    total = count_result.single()['total']
    
    # Get data
    query = f"""
    MATCH (f:Fund)
    WHERE {where_clause}
    OPTIONAL MATCH (f)-[:MANAGED_BY]->(m:ManagementEntity)
    RETURN f, m
    ORDER BY f.fund_id
    SKIP $skip
    LIMIT $limit
    """
    
    result = db.run(query, **params)
    
    funds = []
    for record in result:
        fund = dict(record['f'])
        fund['management_entity'] = dict(record['m']) if record['m'] else None
        funds.append(fund)
    
    return {
        'funds': funds,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }

@router.get("/")
async def list_funds(skip: int = 0, limit: int = 10, db = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Retrieves all funds with basic pagination using skip and limit parameters.
    Returns list of funds with their associated management entities.
    """
    query = """
    MATCH (f:Fund)
    OPTIONAL MATCH (f)-[:MANAGED_BY]->(m:ManagementEntity)
    RETURN f, m
    ORDER BY f.fund_id
    SKIP $skip
    LIMIT $limit
    """
    
    result = db.run(query, skip=skip, limit=limit)
    
    funds = []
    for record in result:
        fund = dict(record['f'])
        fund['management_entity'] = dict(record['m']) if record['m'] else None
        funds.append(fund)
    
    return funds

@router.get("/code/{fund_code}")
async def get_fund_by_code(fund_code: str, db = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves a specific fund by its unique fund code with complete related data.
    Returns fund with management entity, legal entity, share classes, and subfunds.
    """
    query = """
    MATCH (f:Fund {fund_code: $fund_code})
    OPTIONAL MATCH (f)-[:MANAGED_BY]->(m:ManagementEntity)
    OPTIONAL MATCH (f)-[:HAS_LEGAL_ENTITY]->(le:LegalEntity)
    OPTIONAL MATCH (f)-[:HAS_SHARE_CLASS]->(sc:ShareClass)
    OPTIONAL MATCH (sf:SubFund)-[:PARENT_FUND]->(f)
    RETURN f, m, le, collect(DISTINCT sc) as share_classes, collect(DISTINCT sf) as subfunds
    """
    
    result = db.run(query, fund_code=fund_code)
    record = result.single()
    
    if not record:
        raise HTTPException(status_code=404, detail=f"Fund with code {fund_code} not found")
    
    fund = dict(record['f'])
    fund['management_entity'] = dict(record['m']) if record['m'] else None
    fund['legal_entity'] = dict(record['le']) if record['le'] else None
    fund['share_classes'] = [dict(sc) for sc in record['share_classes'] if sc]
    fund['subfunds'] = [dict(sf) for sf in record['subfunds'] if sf]
    
    return fund

@router.get("/statistics")
async def get_fund_statistics(db = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves comprehensive fund statistics including total counts, status breakdown, and type distribution.
    Returns aggregated data for dashboard display without pagination.
    """
    
    # Get total fund count
    total_query = """
    MATCH (f:Fund)
    RETURN count(f) as total
    """
    total_result = db.run(total_query)
    total_funds = total_result.single()['total']
    
    # Get counts by status
    status_query = """
    MATCH (f:Fund)
    RETURN f.status as status, count(f) as count
    """
    status_result = db.run(status_query)
    status_counts = {}
    active_funds = 0
    inactive_funds = 0
    
    for record in status_result:
        status = record['status']
        count = record['count']
        status_counts[status] = count
        if status == 'ACTIVE':
            active_funds = count
        else:
            inactive_funds += count
    
    # Get counts by fund type
    type_query = """
    MATCH (f:Fund)
    RETURN f.fund_type as fund_type, count(f) as count
    ORDER BY count DESC
    """
    type_result = db.run(type_query)
    funds_by_type = []
    
    for record in type_result:
        funds_by_type.append({
            'name': record['fund_type'],
            'value': record['count']
        })
    
    return {
        'total_funds': total_funds,
        'active_funds': active_funds,
        'inactive_funds': inactive_funds,
        'status_breakdown': status_counts,
        'funds_by_type': funds_by_type
    }

@router.get("/{fund_id}/hierarchy/children")
async def get_fund_hierarchy_children(fund_id: str, depth: int = 1, db = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves hierarchical tree of child subfunds for a fund up to specified depth.
    Returns root fund, list of children with depth levels, and share classes.
    """
    query = f"""
    MATCH (f:Fund {{fund_id: $fund_id}})
    OPTIONAL MATCH path = (f)<-[:PARENT_FUND*1..{depth}]-(sf:SubFund)
    WITH f, collect(DISTINCT {{
        subfund: sf,
        depth: length(path)
    }}) as subfunds_with_depth
    OPTIONAL MATCH (f)-[:HAS_SHARE_CLASS]->(sc:ShareClass)
    RETURN f, subfunds_with_depth, collect(DISTINCT sc) as share_classes
    """
    
    result = db.run(query, fund_id=fund_id)
    record = result.single()
    
    if not record:
        raise HTTPException(status_code=404, detail=f"Fund with ID {fund_id} not found")
    
    fund = dict(record['f'])
    subfunds = []
    
    for item in record['subfunds_with_depth']:
        if item['subfund']:
            subfund_data = dict(item['subfund'])
            subfund_data['depth'] = item['depth']
            subfunds.append(subfund_data)
    
    fund['share_classes'] = [dict(sc) for sc in record['share_classes'] if sc]
    
    return {
        'root': fund,
        'children': subfunds,
        'depth': depth
    }

@router.get("/{fund_id}")
async def get_fund(fund_id: str, db = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves a specific fund by its unique fund ID with all relationships.
    Returns fund with management entity, legal entity, share classes, and subfunds.
    """
    query = """
    MATCH (f:Fund {fund_id: $fund_id})
    OPTIONAL MATCH (f)-[:MANAGED_BY]->(m:ManagementEntity)
    OPTIONAL MATCH (f)-[:HAS_LEGAL_ENTITY]->(le:LegalEntity)
    OPTIONAL MATCH (f)-[:HAS_SHARE_CLASS]->(sc:ShareClass)
    OPTIONAL MATCH (sf:SubFund)-[:PARENT_FUND]->(f)
    RETURN f, m, le, collect(DISTINCT sc) as share_classes, collect(DISTINCT sf) as subfunds
    """
    
    result = db.run(query, fund_id=fund_id)
    record = result.single()
    
    if not record:
        raise HTTPException(status_code=404, detail="Fund not found")
    
    fund = dict(record['f'])
    fund['management_entity'] = dict(record['m']) if record['m'] else None
    fund['legal_entity'] = dict(record['le']) if record['le'] else None
    fund['share_classes'] = [dict(sc) for sc in record['share_classes'] if sc]
    fund['subfunds'] = [dict(sf) for sf in record['subfunds'] if sf]
    
    return fund