from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/legal-entities", tags=["legal_entities"])

@router.get("/")
async def list_legal_entities() -> List[Dict[str, Any]]:
    """List all legal entities - placeholder"""
    return [{"message": "Legal entities endpoint - placeholder"}]