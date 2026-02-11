"""
Dossiers Router
===============
Rotas para gerenciamento de dossies
"""

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.services.auth_service import AuthService, security
from app.services.dossier_service import DossierService

router = APIRouter()


def get_auth_service():
    return AuthService()


def get_dossier_service():
    return DossierService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.get_current_user(credentials)


class CreateDossierRequest(BaseModel):
    document: str
    enable_ai: bool = False
    cep: Optional[str] = None


class BatchDossiersRequest(BaseModel):
    documents: List[str]
    enable_ai: bool = False


class DossierDecisionRequest(BaseModel):
    parecer_tecnico: str
    aprovado: bool
    justificativa: Optional[str] = ""


class DossierResponse(BaseModel):
    id: str
    document_value: str
    entity_name: str
    risk_level: Optional[str]
    created_at: str
    report_data: Optional[dict] = None
    status_decisao: Optional[str] = None
    aprovado_por_diretoria: Optional[bool] = None
    parecer_tecnico_compliance: Optional[str] = None
    justificativa_diretoria: Optional[str] = None
    data_decisao: Optional[str] = None


@router.post("/", status_code=201)
async def create_dossier(
    request: CreateDossierRequest,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user),
):
    result = dossier_service.generate_and_save(
        document=request.document,
        company_id=user["company_id"],
        enable_ai=request.enable_ai,
        cep=request.cep,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/batch")
async def create_batch_dossiers(
    request: BatchDossiersRequest,
    background_tasks: BackgroundTasks,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user),
):
    background_tasks.add_task(
        dossier_service.process_batch,
        documents=request.documents,
        company_id=user["company_id"],
        enable_ai=request.enable_ai,
    )

    return {
        "message": f"Processamento iniciado para {len(request.documents)} documento(s)",
        "total": len(request.documents),
        "status": "processing",
    }


@router.get("/", response_model=List[DossierResponse])
async def list_dossiers(
    page: int = 1,
    page_size: int = 20,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user),
):
    dossiers, total = dossier_service.list_dossiers(
        company_id=user["company_id"],
        page=page,
        page_size=page_size,
    )

    return dossiers


@router.get("/check-duplicate")
async def check_duplicate(
    document: str,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user),
):
    existing_id = dossier_service.check_duplicate(
        document=document,
        company_id=user["company_id"],
    )

    return {
        "exists": existing_id is not None,
        "dossier_id": existing_id,
    }


@router.get("/{dossier_id}", response_model=DossierResponse)
async def get_dossier(
    dossier_id: str,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user),
):
    dossier = dossier_service.get_by_id(
        dossier_id=dossier_id,
        company_id=user["company_id"],
    )

    if not dossier:
        raise HTTPException(status_code=404, detail="Dossie nao encontrado")

    return dossier


@router.put("/{dossier_id}/decide")
async def decide_dossier(
    dossier_id: str,
    request: DossierDecisionRequest,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user),
):
    dossier = dossier_service.get_by_id(
        dossier_id=dossier_id,
        company_id=user["company_id"],
    )

    if not dossier:
        raise HTTPException(status_code=404, detail="Dossie nao encontrado")

    result = dossier_service.update_decision(
        dossier_id=dossier_id,
        company_id=user["company_id"],
        parecer_tecnico=request.parecer_tecnico,
        aprovado=request.aprovado,
        justificativa=request.justificativa,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Erro ao atualizar decisao"))

    return {
        "success": True,
        "message": "Decisao registrada com sucesso",
        "status_decisao": result.get("status_decisao"),
    }
