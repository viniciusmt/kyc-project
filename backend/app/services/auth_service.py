"""
Authentication Service
======================
Serviço de autenticação usando Supabase
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from supabase import create_client, Client

from app.core.config import settings

security = HTTPBearer()


class AuthService:
    """Serviço de autenticação"""

    def __init__(self):
        # Cria cliente Supabase diretamente
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )

    def sign_in(self, email: str, password: str) -> dict:
        """
        Realiza login e retorna JWT token

        Returns:
            dict com access_token, user, company_id, company_name
        """
        try:
            # Autentica no Supabase
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not auth_response.user:
                return {
                    "success": False,
                    "error": "Credenciais inválidas"
                }

            user_id = auth_response.user.id

            # Busca profile
            profile_response = self.client.table("profiles").select(
                "id, company_id, role, full_name, companies(id, name)"
            ).eq("id", user_id).single().execute()

            if not profile_response.data:
                return {
                    "success": False,
                    "error": "Perfil não encontrado"
                }

            profile = profile_response.data
            company_id = profile.get("company_id")

            if not company_id:
                return {
                    "success": False,
                    "error": "Usuário sem empresa vinculada"
                }

            # Extrai nome da empresa
            company_name = "N/A"
            companies_data = profile.get("companies")
            if companies_data and isinstance(companies_data, dict):
                company_name = companies_data.get("name", "N/A")

            # Gera JWT token customizado
            access_token = self._create_access_token(
                data={
                    "sub": user_id,
                    "email": auth_response.user.email,
                    "company_id": company_id
                }
            )

            return {
                "success": True,
                "access_token": access_token,
                "user": {
                    "id": user_id,
                    "email": auth_response.user.email
                },
                "company_id": company_id,
                "company_name": company_name
            }

        except Exception as e:
            error_msg = str(e)

            # Log do erro para debug
            print(f"❌ Erro no login: {error_msg}")

            if "Invalid login credentials" in error_msg:
                return {"success": False, "error": "Email ou senha incorretos"}
            elif "Invalid" in error_msg or "credentials" in error_msg.lower():
                return {"success": False, "error": "Email ou senha incorretos"}
            else:
                return {"success": False, "error": f"Erro ao fazer login: {error_msg}"}

    def _create_access_token(self, data: dict) -> str:
        """Cria JWT token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Dependency para rotas protegidas"""
        token = credentials.credentials

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            user_id: str = payload.get("sub")
            company_id: str = payload.get("company_id")

            if user_id is None or company_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )

            return {
                "id": user_id,
                "email": payload.get("email"),
                "company_id": company_id
            }

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
