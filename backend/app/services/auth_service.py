"""
Authentication Service
======================
Servico de autenticacao usando Supabase
"""

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import JWTError, jwt
from supabase import Client, create_client

from app.core.config import settings

security = HTTPBearer()


class AuthService:
    """Servico de autenticacao"""

    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def sign_in(self, email: str, password: str) -> dict:
        """
        Realiza login e retorna JWT token.

        Returns:
            dict com access_token, user, company_id, company_name
        """
        try:
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })

            if not auth_response.user:
                return {"success": False, "error": "Credenciais invalidas"}

            user_id = auth_response.user.id
            profile = self._get_user_profile(user_id)

            if not profile:
                return {"success": False, "error": "Perfil nao encontrado"}

            company_id = profile.get("company_id")
            if not company_id:
                return {"success": False, "error": "Usuario sem empresa vinculada"}

            company_name = self._resolve_company_name(profile, company_id)

            access_token = self._create_access_token(
                data={
                    "sub": user_id,
                    "email": auth_response.user.email,
                    "company_id": company_id,
                }
            )

            return {
                "success": True,
                "access_token": access_token,
                "user": {"id": user_id, "email": auth_response.user.email},
                "company_id": company_id,
                "company_name": company_name,
            }

        except Exception as e:
            error_msg = str(e)
            print(f"Erro no login: {error_msg}")

            if "Invalid login credentials" in error_msg:
                return {"success": False, "error": "Email ou senha incorretos"}
            if "Invalid" in error_msg or "credentials" in error_msg.lower():
                return {"success": False, "error": "Email ou senha incorretos"}
            return {"success": False, "error": f"Erro ao fazer login: {error_msg}"}

    def _get_user_profile(self, user_id: str):
        """
        Busca profile do usuario.
        Tenta com join em companies e faz fallback sem join para schemas diferentes.
        """
        try:
            response = self.client.table("profiles").select(
                "id, company_id, role, full_name, companies(id, name)"
            ).eq("id", user_id).single().execute()
            return response.data
        except Exception:
            fallback = self.client.table("profiles").select(
                "id, company_id, role, full_name"
            ).eq("id", user_id).single().execute()
            return fallback.data

    def _resolve_company_name(self, profile: dict, company_id: str) -> str:
        """Resolve company_name mesmo quando nested relation nao vier no profile."""
        companies_data = profile.get("companies")
        if companies_data and isinstance(companies_data, dict):
            return companies_data.get("name", "N/A")

        try:
            company_response = self.client.table("companies").select("name").eq("id", company_id).single().execute()
            if company_response.data and company_response.data.get("name"):
                return company_response.data["name"]
        except Exception:
            pass

        return "N/A"

    def _create_access_token(self, data: dict) -> str:
        """Cria JWT token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Dependency para rotas protegidas."""
        token = credentials.credentials

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

            user_id: str = payload.get("sub")
            company_id: str = payload.get("company_id")

            if user_id is None or company_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

            return {"id": user_id, "email": payload.get("email"), "company_id": company_id}

        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido ou expirado")
