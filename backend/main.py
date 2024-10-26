# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import GlobalSettings
from app.api.router import api_router

app = FastAPI(title="Document RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=GlobalSettings.CORS_ORIGINS,
    allow_credentials=GlobalSettings.CORS_CREDENTIALS,
    allow_methods=GlobalSettings.CORS_METHODS,
    allow_headers=GlobalSettings.CORS_HEADERS,
)

app.include_router(api_router)