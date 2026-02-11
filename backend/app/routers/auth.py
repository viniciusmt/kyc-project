"""
Authentication Router
=====================
Rotas de autenticacao (login, logout, user info)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from app.services.auth_service import AuthService, security

router = APIRouter()


def get_auth_service():
    """Lazy initialization of AuthService"""
    return AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.get_current_user(credentials)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    company_id: str
    company_name: str


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """
    Login do usuario.

    Retorna access_token JWT e informacoes do usuario/empresa.
    """
    result = auth_service.sign_in(credentials.email, credentials.password)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"],
        )

    return LoginResponse(
        access_token=result["access_token"],
        user=result["user"],
        company_id=result["company_id"],
        company_name=result["company_name"],
    )


@router.post("/logout")
async def logout():
    """Logout do usuario (client-side remove token)."""
    return {"message": "Logout successful"}


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    """Retorna informacoes do usuario autenticado."""
    return current_user
