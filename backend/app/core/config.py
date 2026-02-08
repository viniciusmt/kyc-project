"""
Configurações da Aplicação
===========================
Carrega variáveis de ambiente e configurações
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configurações do sistema"""

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "KYC System"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js dev
        "http://localhost:8000",  # FastAPI dev
        "https://your-production-domain.com"  # Production
    ]

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str

    # APIs Externas
    TRANSPARENCIA_API_KEY: str
    GEMINI_API_KEY: str

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
