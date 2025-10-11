from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from app.database.connection import get_db

router = APIRouter(prefix="/legal-entities", tags=["legal_entities"])

@router.get("/search")
async def search_legal_entities(
    le_id: Optional[str] = Query(None),
    lei: Optional[str] = Query(None),
    entity_name: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Searches legal entities using optional filters for le_id, lei, and entity_name with pagination.
    Supports partial matching on all string fields and returns paginated results.
    """
    
    where_clauses = []
    params = {}
    
    if le_id:
        where_clauses.append("le.le_id CONTAINS $le_id")
        params['le_id'] = le_id
    
    if lei:
        where_clauses.append("le.lei CONTAINS $lei")
        params['lei'] = lei
    
    if entity_name:
        where_clauses.append("le.entity_name CONTAINS $entity_name")
        params['entity_name'] = entity_name
    
    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Calculate skip
    skip = (page - 1) * page_size
    params['skip'] = skip
    params['limit'] = page_size
    
    # Get total count
    count_query = f"""
    MATCH (le:LegalEntity)
    WHERE {where_clause}
    RETURN count(le) as total
    """
    
    count_result = db.run(count_query, **params)
    total = count_result.single()['total']
    
    # Get data
    query = f"""
    MATCH (le:LegalEntity)
    WHERE {where_clause}
    RETURN le
    ORDER BY le.le_id
    SKIP $skip
    LIMIT $limit
    """
    
    result = db.run(query, **params)
    
    legal_entities = [dict(record['le']) for record in result]
    
    return {
        'legal_entities': legal_entities,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }

@router.get("/")
async def list_legal_entities(
    skip: int = 0,
    limit: int = 10,
    db = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Retrieves all legal entities with basic pagination using skip and limit parameters.
    Returns sorted list of legal entities ordered by le_id.
    """
    query = """
    MATCH (le:LegalEntity)
    RETURN le
    ORDER BY le.le_id
    SKIP $skip
    LIMIT $limit
    """
    
    result = db.run(query, skip=skip, limit=limit)
    return [dict(record['le']) for record in result]

@router.get("/{le_id}")
async def get_legal_entity(le_id: str, db = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves a specific legal entity by ID with all associated fund relationships.
    Returns legal entity with list of funds that have this legal entity or raises 404 if not found.
    """
    query = """
    MATCH (le:LegalEntity {le_id: $le_id})
    OPTIONAL MATCH (f:Fund)-[:HAS_LEGAL_ENTITY]->(le)
    RETURN le, collect(DISTINCT f) as funds
    """
    
    result = db.run(query, le_id=le_id)
    record = result.single()
    
    if not record:
        raise HTTPException(status_code=404, detail=f"Legal entity with ID {le_id} not found")
    
    le = dict(record['le'])
    le['funds'] = [dict(f) for f in record['funds'] if f]
    
    return le