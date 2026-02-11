"""
Configurações da Aplicação
===========================
Carrega variáveis de ambiente e configurações
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Configurações do sistema"""

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "KYC System"

    # CORS - aceita string separada por vírgula ou lista
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,https://main.d1pcg3lkjfaxct.amplifyapp.com,https://main.d1a6bdu7v29m3g.amplifyapp.com")

    # Supabase (virão do SSM no App Runner)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_JWT_SECRET: Optional[str] = os.getenv("SUPABASE_JWT_SECRET")

    # APIs Externas (virão do SSM no App Runner)
    TRANSPARENCIA_API_KEY: str = os.getenv("TRANSPARENCIA_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Converte CORS_ORIGINS de string para lista"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS


settings = Settings()
