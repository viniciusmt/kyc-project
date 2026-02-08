"""
Dossier Service - Wrapper
==========================
Wrapper para o dossier_service.py existente
"""

import os
import sys

# Adiciona diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Importa funções existentes
from dossier_service import (
    generate_and_save_dossier,
    list_dossiers,
    get_dossier_by_id,
    check_duplicate_dossier,
    process_batch,
    update_dossier_decision
)


class DossierService:
    """Serviço de dossiês (wrapper para funções existentes)"""

    def generate_and_save(self, document: str, company_id: str, enable_ai: bool = False, cep: str = None) -> dict:
        """Gera e salva dossiê"""
        return generate_and_save_dossier(
            document=document,
            company_id=company_id,
            enable_ai=enable_ai,
            cep=cep
        )

    def list_dossiers(self, company_id: str, page: int = 1, page_size: int = 20):
        """Lista dossiês"""
        return list_dossiers(
            company_id=company_id,
            page=page,
            page_size=page_size
        )

    def get_by_id(self, dossier_id: str, company_id: str):
        """Obtém dossiê por ID"""
        return get_dossier_by_id(dossier_id, company_id)

    def check_duplicate(self, document: str, company_id: str):
        """Verifica duplicata"""
        return check_duplicate_dossier(document, company_id)

    def process_batch(self, documents: list, company_id: str, enable_ai: bool = False):
        """Processa lote"""
        return process_batch(
            documents=documents,
            company_id=company_id,
            enable_ai=enable_ai,
            delay_seconds=2
        )

    def update_decision(self, dossier_id: str, company_id: str, parecer_tecnico: str, aprovado: bool, justificativa: str):
        """Atualiza decisão de diretoria"""
        return update_dossier_decision(
            dossier_id=dossier_id,
            company_id=company_id,
            parecer_tecnico=parecer_tecnico,
            aprovado=aprovado,
            justificativa=justificativa
        )
