from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/share-classes", tags=["share_classes"])

@router.get("/")
async def list_share_classes() -> List[Dict[str, Any]]:
    """List all share classes - placeholder"""
    return [{"message": "Share classes endpoint - placeholder"}]