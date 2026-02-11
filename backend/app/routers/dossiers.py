"""
Dossiers Router
===============
Rotas para gerenciamento de dossiês
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from app.services.auth_service import AuthService
from app.services.dossier_service import DossierService

router = APIRouter()

def get_auth_service():
    return AuthService()

def get_dossier_service():
    return DossierService()

def get_current_user(auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.get_current_user


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
    user=Depends(get_current_user)
):
    """
    Gera e salva um novo dossiê

    - Consulta APIs públicas (BrasilAPI, Transparência)
    - Opcionalmente executa análise de IA
    - Salva no Supabase
    - Retorna dossier_id para acesso
    """
    result = dossier_service.generate_and_save(
        document=request.document,
        company_id=user["company_id"],
        enable_ai=request.enable_ai,
        cep=request.cep
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/batch")
async def create_batch_dossiers(
    request: BatchDossiersRequest,
    background_tasks: BackgroundTasks,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user)
):
    """
    Processa múltiplos dossiês em background

    - Recebe lista de documentos
    - Processa em background com delay de 2s
    - Retorna task_id para acompanhamento
    """
    # Adiciona task em background
    background_tasks.add_task(
        dossier_service.process_batch,
        documents=request.documents,
        company_id=user["company_id"],
        enable_ai=request.enable_ai
    )

    return {
        "message": f"Processamento iniciado para {len(request.documents)} documento(s)",
        "total": len(request.documents),
        "status": "processing"
    }


@router.get("/", response_model=List[DossierResponse])
async def list_dossiers(
    page: int = 1,
    page_size: int = 20,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user)
):
    """Lista dossiês da empresa (paginado)"""
    dossiers, total = dossier_service.list_dossiers(
        company_id=user["company_id"],
        page=page,
        page_size=page_size
    )

    return dossiers


@router.get("/check-duplicate")
async def check_duplicate(
    document: str,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user)
):
    """Verifica se já existe dossiê para o documento"""
    existing_id = dossier_service.check_duplicate(
        document=document,
        company_id=user["company_id"]
    )

    return {
        "exists": existing_id is not None,
        "dossier_id": existing_id
    }


@router.get("/{dossier_id}", response_model=DossierResponse)
async def get_dossier(
    dossier_id: str,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user)
):
    """
    Retorna dossiê completo por ID

    Modo leitura: carrega dados salvos (sem reprocessamento)
    """
    dossier = dossier_service.get_by_id(
        dossier_id=dossier_id,
        company_id=user["company_id"]
    )

    if not dossier:
        raise HTTPException(
            status_code=404,
            detail="Dossiê não encontrado"
        )

    return dossier


@router.put("/{dossier_id}/decide")
async def decide_dossier(
    dossier_id: str,
    request: DossierDecisionRequest,
    dossier_service: DossierService = Depends(get_dossier_service),
    user=Depends(get_current_user)
):
    """
    Registra a decisão de diretoria sobre o dossiê

    - Valida que o dossiê pertence à empresa do usuário (multi-tenant)
    - Atualiza parecer técnico, status de decisão e justificativa
    - Registra data/hora da decisão
    """
    # Valida que o dossiê existe e pertence à empresa
    dossier = dossier_service.get_by_id(
        dossier_id=dossier_id,
        company_id=user["company_id"]
    )

    if not dossier:
        raise HTTPException(
            status_code=404,
            detail="Dossiê não encontrado"
        )

    # Atualiza a decisão
    result = dossier_service.update_decision(
        dossier_id=dossier_id,
        company_id=user["company_id"],
        parecer_tecnico=request.parecer_tecnico,
        aprovado=request.aprovado,
        justificativa=request.justificativa
    )

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Erro ao atualizar decisão")
        )

    return {
        "success": True,
        "message": "Decisão registrada com sucesso",
        "status_decisao": result.get("status_decisao")
    }
