from fastapi import APIRouter
from app.api.endpoints import document

api_router = APIRouter()
api_router.include_router(document.router, prefix="/documents", tags=["documents"])