"""
Authentication Router
=====================
Rotas de autenticação (login, logout, user info)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.auth_service import AuthService

router = APIRouter()

def get_auth_service():
    """Lazy initialization of AuthService"""
    return AuthService()


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
    Login do usuário

    Retorna access_token JWT e informações do usuário/empresa
    """
    result = auth_service.sign_in(credentials.email, credentials.password)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"]
        )

    return LoginResponse(
        access_token=result["access_token"],
        user=result["user"],
        company_id=result["company_id"],
        company_name=result["company_name"]
    )


@router.post("/logout")
async def logout():
    """Logout do usuário (client-side apenas remove token)"""
    return {"message": "Logout successful"}


@router.get("/me")
async def get_current_user(auth_service: AuthService = Depends(get_auth_service)):
    """Retorna informações do usuário autenticado"""
    user = await auth_service.get_current_user()
    return user
