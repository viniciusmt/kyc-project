"""
FastAPI Main Application - KYC System
======================================
Sistema de análise de risco (KYC) com FastAPI + Next.js

Author: Vinicius Matsumoto
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, dossiers, monitoring

# Inicializa FastAPI
app = FastAPI(
    title="KYC System API",
    description="API para sistema de análise de risco (KYC)",
    version="2.0.0"
)

# CORS - Permite requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dossiers.router, prefix="/api/dossiers", tags=["Dossiers"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "version": "2.0.0",
        "service": "KYC System API"
    }


@app.get("/health")
async def health_check():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "database": "connected",
        "apis": "available"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
