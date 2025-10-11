from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.database.connection import get_db

router = APIRouter(prefix="/management", tags=["management"])

@router.get("/{mgmt_id}")
async def get_management_entity(mgmt_id: str, db = Depends(get_db)) -> Dict[str, Any]:
    """Get management entity by ID"""
    query = """
    MATCH (m:ManagementEntity {mgmt_id: $mgmt_id})
    OPTIONAL MATCH (m)-[:HAS_LEGAL_ENTITY]->(le:LegalEntity)
    RETURN m, le
    """
    
    session = next(db)
    result = session.run(query, mgmt_id=mgmt_id)
    record = result.single()
    
    if not record:
        raise HTTPException(status_code=404, detail="Management entity not found")
    
    mgmt = dict(record['m'])
    mgmt['legal_entity'] = dict(record['le']) if record['le'] else None
    
    return mgmt

@router.get("/")
async def list_management_entities(skip: int = 0, limit: int = 10, db = Depends(get_db)) -> List[Dict[str, Any]]:
    """List all management entities"""
    query = """
    MATCH (m:ManagementEntity)
    RETURN m
    SKIP $skip
    LIMIT $limit
    """
    
    session = next(db)
    result = session.run(query, skip=skip, limit=limit)
    
    entities = [dict(record['m']) for record in result]
    return entities