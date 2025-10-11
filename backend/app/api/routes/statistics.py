from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.database.connection import get_db

router = APIRouter(prefix="/statistics", tags=["statistics"])

@router.get("/funds")
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

@router.get("/management")
async def get_management_statistics(db = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves management entity statistics including total count and status breakdown.
    Returns aggregated data for dashboard display.
    """
    
    # Get total management entity count
    total_query = """
    MATCH (m:ManagementEntity)
    RETURN count(m) as total
    """
    total_result = db.run(total_query)
    total_management_entities = total_result.single()['total']
    
    # Get counts by status
    status_query = """
    MATCH (m:ManagementEntity)
    RETURN m.status as status, count(m) as count
    """
    status_result = db.run(status_query)
    status_counts = {}
    
    for record in status_result:
        status = record['status'] or 'UNKNOWN'
        count = record['count']
        status_counts[status] = count
    
    return {
        'total_management_entities': total_management_entities,
        'status_breakdown': status_counts
    }

@router.get("/dashboard")
async def get_dashboard_statistics(db = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves all statistics needed for the dashboard in a single API call.
    Returns combined fund and management entity statistics for optimal performance.
    """
    
    fund_stats = await get_fund_statistics(db)
    mgmt_stats = await get_management_statistics(db)
    
    return {
        **fund_stats,
        **mgmt_stats
    }
