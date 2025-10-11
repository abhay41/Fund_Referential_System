from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/subfunds", tags=["subfunds"])

@router.get("/")
async def list_subfunds() -> List[Dict[str, Any]]:
    """List all subfunds - placeholder"""
    return [{"message": "SubFunds endpoint - placeholder"}]