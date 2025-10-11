from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from app.database.connection import get_db

router = APIRouter(prefix="/management", tags=["management"])

@router.get("/search")
async def search_management_entities(
    mgmt_id: Optional[str] = Query(None),
    registration_no: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    domicile: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Searches management entities using multiple optional filters with pagination support.
    Supports partial matching on mgmt_id and registration_no, returns entities with legal entity information.
    """
    
    where_clauses = []
    params = {}
    
    if mgmt_id:
        where_clauses.append("m.mgmt_id CONTAINS $mgmt_id")
        params['mgmt_id'] = mgmt_id
    
    if registration_no:
        where_clauses.append("m.registration_no CONTAINS $registration_no")
        params['registration_no'] = registration_no
    
    if entity_type:
        where_clauses.append("m.entity_type = $entity_type")
        params['entity_type'] = entity_type
    
    if domicile:
        where_clauses.append("m.domicile = $domicile")
        params['domicile'] = domicile
    
    if status:
        where_clauses.append("m.status = $status")
        params['status'] = status
    
    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Calculate skip
    skip = (page - 1) * page_size
    params['skip'] = skip
    params['limit'] = page_size
    
    # Get total count
    count_query = f"""
    MATCH (m:ManagementEntity)
    WHERE {where_clause}
    RETURN count(m) as total
    """
    
    count_result = db.run(count_query, **params)
    total = count_result.single()['total']
    
    # Get data
    query = f"""
    MATCH (m:ManagementEntity)
    WHERE {where_clause}
    OPTIONAL MATCH (m)-[:HAS_LEGAL_ENTITY]->(le:LegalEntity)
    RETURN m, le
    ORDER BY m.mgmt_id
    SKIP $skip
    LIMIT $limit
    """
    
    result = db.run(query, **params)
    
    entities = []
    for record in result:
        mgmt = dict(record['m'])
        mgmt['legal_entity'] = dict(record['le']) if record['le'] else None
        entities.append(mgmt)
    
    return {
        'management_entities': entities,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }

@router.get("/")
async def list_management_entities(
    skip: int = 0,
    limit: int = 10,
    db = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Retrieves all management entities with basic pagination using skip and limit parameters.
    Returns list of management entities with their associated legal entity information.
    """
    query = """
    MATCH (m:ManagementEntity)
    OPTIONAL MATCH (m)-[:HAS_LEGAL_ENTITY]->(le:LegalEntity)
    RETURN m, le
    ORDER BY m.mgmt_id
    SKIP $skip
    LIMIT $limit
    """
    
    result = db.run(query, skip=skip, limit=limit)
    
    entities = []
    for record in result:
        mgmt = dict(record['m'])
        mgmt['legal_entity'] = dict(record['le']) if record['le'] else None
        entities.append(mgmt)
    
    return entities

@router.get("/{mgmt_id}")
async def get_management_entity(mgmt_id: str, db = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves a specific management entity by ID with complete relationship data.
    Returns management entity with legal entity and all managed funds or raises 404 if not found.
    """
    query = """
    MATCH (m:ManagementEntity {mgmt_id: $mgmt_id})
    OPTIONAL MATCH (m)-[:HAS_LEGAL_ENTITY]->(le:LegalEntity)
    OPTIONAL MATCH (f:Fund)-[:MANAGED_BY]->(m)
    RETURN m, le, collect(DISTINCT f) as funds
    """
    
    result = db.run(query, mgmt_id=mgmt_id)
    record = result.single()
    
    if not record:
        raise HTTPException(status_code=404, detail="Management entity not found")
    
    mgmt = dict(record['m'])
    mgmt['legal_entity'] = dict(record['le']) if record['le'] else None
    mgmt['funds'] = [dict(f) for f in record['funds'] if f]
    
    return mgmt

@router.get("/{mgmt_id}/funds")
async def get_management_entity_funds(
    mgmt_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retrieves all funds managed by a specific management entity with pagination.
    Returns paginated list of funds sorted by fund_id with total count and page information.
    """
    
    # Calculate skip
    skip = (page - 1) * page_size
    
    # Get total count
    count_query = """
    MATCH (f:Fund)-[:MANAGED_BY]->(m:ManagementEntity {mgmt_id: $mgmt_id})
    RETURN count(f) as total
    """
    
    count_result = db.run(count_query, mgmt_id=mgmt_id)
    total = count_result.single()['total']
    
    # Get data
    query = """
    MATCH (f:Fund)-[:MANAGED_BY]->(m:ManagementEntity {mgmt_id: $mgmt_id})
    RETURN f
    ORDER BY f.fund_id
    SKIP $skip
    LIMIT $limit
    """
    
    result = db.run(query, mgmt_id=mgmt_id, skip=skip, limit=page_size)
    funds = [dict(record['f']) for record in result]
    
    return {
        'funds': funds,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }