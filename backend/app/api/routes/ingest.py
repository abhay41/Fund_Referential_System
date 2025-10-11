from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
from pathlib import Path

import data_ingestion
import sys
from pathlib import Path as _Path

# Ensure backend root is on sys.path so we can import top-level modules when running under uvicorn
_project_root = _Path(__file__).parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from data_ingestion import DataIngestion

router = APIRouter()

ALLOWED_TARGETS = {
    'management_entities': 'ingest_management_entities',
    'master_funds': 'ingest_funds',
    'subfunds': 'ingest_subfunds',
    'legal_entities': 'ingest_legal_entities',
    'share_classes': 'ingest_share_classes'
}


@router.post('/ingest/upload')
async def upload_and_ingest(file: UploadFile = File(...), target: str = Form(...)):
    """Upload a CSV and ingest it into Neo4j using the existing ingestion methods.
    target must be one of the keys in ALLOWED_TARGETS.
    """
    if target not in ALLOWED_TARGETS:
        raise HTTPException(status_code=400, detail="Invalid target dataset")

    # save to a temporary file in backend/data
    data_dir = Path(__file__).parents[3] / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    dest = data_dir / f"upload_{target}.csv"

    try:
        with open(dest, 'wb') as out_file:
            shutil.copyfileobj(file.file, out_file)
    finally:
        file.file.close()

    # call the appropriate ingestion method
    ingestion = DataIngestion()
    try:
        func_name = ALLOWED_TARGETS[target]
        func = getattr(ingestion, func_name, None)
        if not func:
            raise HTTPException(status_code=500, detail='Ingestion function not implemented')

        func(str(dest))
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    finally:
        ingestion.close()

    return {"detail": "Ingested", "target": target}
