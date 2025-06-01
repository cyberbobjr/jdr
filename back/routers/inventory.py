from fastapi import APIRouter
from back.utils.logger import log_debug

router = APIRouter()

@router.get("/example")
async def example_endpoint():
    log_debug("Appel endpoint inventory/example_endpoint")
    return {"message": "Example endpoint for inventory"}

# Endpoints REST (FastAPI "router")
