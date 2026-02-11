"""
Monitoring Router
=================
Rotas para monitoramento contínuo de documentos
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.auth_service import AuthService
from app.services.monitoring_service import MonitoringService

router = APIRouter()

def get_auth_service():
    return AuthService()

def get_monitoring_service():
    return MonitoringService()

def get_current_user(auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.get_current_user


class AddMonitoringRequest(BaseModel):
    document: str
    notes: Optional[str] = ""


@router.post("/")
async def add_to_monitoring(
    request: AddMonitoringRequest,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    user=Depends(get_current_user)
):
    """Adiciona documento ao monitoramento contínuo"""
    result = monitoring_service.add_record(
        document=request.document,
        company_id=user["company_id"],
        notes=request.notes
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/")
async def list_monitored(
    page: int = 1,
    page_size: int = 10,
    doc_type: Optional[str] = None,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    user=Depends(get_current_user)
):
    """Lista documentos monitorados"""
    result = monitoring_service.get_all_records(
        company_id=user["company_id"],
        page=page,
        page_size=page_size,
        filter_type=doc_type
    )

    return {
        "records": result.get("records", []),
        "total": result.get("total", 0),
        "page": page,
        "page_size": page_size
    }


@router.get("/stats")
async def get_monitoring_stats(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    user=Depends(get_current_user)
):
    """Retorna estatísticas do monitoramento"""
    stats = monitoring_service.get_stats(
        company_id=user["company_id"]
    )

    return stats


@router.put("/{document}")
async def update_monitored(
    document: str,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    user=Depends(get_current_user)
):
    """Atualiza um documento monitorado"""
    result = monitoring_service.update_single(
        document=document,
        company_id=user["company_id"]
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.put("/all")
async def update_all_monitored(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    user=Depends(get_current_user)
):
    """Atualiza todos os documentos monitorados"""
    result = monitoring_service.update_all(
        company_id=user["company_id"]
    )

    return result


@router.delete("/{document}")
async def remove_from_monitoring(
    document: str,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    user=Depends(get_current_user)
):
    """Remove documento do monitoramento"""
    result = monitoring_service.remove_record(
        document=document,
        company_id=user["company_id"]
    )

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/changes/recent")
async def get_recent_changes(
    days: int = 2,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    user=Depends(get_current_user)
):
    """Retorna mudanças recentes detectadas"""
    result = monitoring_service.get_recent_changes(
        company_id=user["company_id"],
        days=days
    )

    if isinstance(result, dict):
        changes = result.get("changes", [])
    else:
        changes = result or []

    return {"changes": changes, "total": len(changes)}
