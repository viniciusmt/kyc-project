"""
Monitoring Engine - Motor de Monitoramento Contínuo
====================================================
Gerencia monitoramento contínuo de CPF/CNPJ com atualização periódica
Autor: Vinicius Matsumoto
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import kyc_engine

load_dotenv()

# Inicializa Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def compute_status(doc_type: Optional[str], kyc_data: Dict) -> str:
    """
    Calcula status do documento com base nos dados KYC.

    CNPJ: ATIVO / INATIVO / DESCONHECIDO
    CPF: REGULAR / IRREGULAR
    """
    doc_type = (doc_type or kyc_data.get("doc_type") or "").upper()

    if doc_type == "CNPJ":
        situacao = (kyc_data.get("cadastral_data", {}) or {}).get("situacao_cadastral", "")
        situacao_upper = str(situacao).upper()
        if "ATIVA" in situacao_upper:
            return "ATIVO"
        if situacao_upper:
            return "INATIVO"
        return "DESCONHECIDO"

    # CPF: usa sanÃ§Ãµes como indicador de irregularidade
    sanctions = (kyc_data.get("sanctions", {}) or {})
    total_sanctions = sanctions.get("total_sanctions", 0)
    if total_sanctions and total_sanctions > 0:
        return "IRREGULAR"
    return "REGULAR"


def add_monitored_record(document: str, notes: str, company_id: str) -> Dict[str, any]:
    """
    Adiciona documento ao monitoramento contínuo

    Args:
        document: CPF ou CNPJ
        notes: Observações sobre o monitoramento
        company_id: ID da empresa

    Returns:
        Dict com success e dados do registro
    """
    try:
        # Valida documento
        validation = kyc_engine.validate_document(document)
        if not validation["success"]:
            return {"success": False, "error": validation.get("error")}

        clean_doc = validation["clean_document"]
        doc_type = validation["doc_type"]

        # Verifica se já existe (idempotente)
        existing = (
            supabase.table("monitoring_targets")
            .select("id,document,doc_type,current_status,data_json")
            .eq("document", clean_doc)
            .eq("company_id", company_id)
            .execute()
        )

        if existing.data and len(existing.data) > 0:
            existing_record = existing.data[0]
            data_json = existing_record.get("data_json", {}) or {}
            entity_name = data_json.get("entity_name") or ""
            restriction_count = data_json.get("restriction_count", 0)
            return {
                "success": True,
                "record_id": existing_record.get("id"),
                "document": clean_doc,
                "entity_name": entity_name,
                "restriction_count": restriction_count,
                "already_exists": True
            }

        # Faz primeira consulta
        kyc_data = kyc_engine.run_kyc_check(clean_doc)
        entity_name = kyc_engine.get_entity_name(kyc_data)
        if entity_name == "Empresa não identificada":
            entity_name = ""

        # Conta restrições iniciais
        sanctions = kyc_data.get("sanctions", {})
        restriction_count = sanctions.get("total_sanctions", 0)

        # Define status inicial
        current_status = compute_status(doc_type, kyc_data)

        # Cria registro (adaptado ao schema real da tabela)
        # Campos que não existem na tabela vão para dentro do data_json
        kyc_data["entity_name"] = entity_name
        kyc_data["notes"] = notes
        kyc_data["restriction_count"] = restriction_count
        kyc_data["last_check_at"] = datetime.utcnow().isoformat()

        record = {
            "company_id": company_id,
            "document": clean_doc,
            "doc_type": doc_type,
            "current_status": current_status,
            "data_json": kyc_data
        }

        response = supabase.table("monitoring_targets").insert(record).execute()

        if getattr(response, "error", None):
            return {"success": False, "error": f"Erro ao salvar registro: {response.error}"}

        if response.data and len(response.data) > 0:
            return {
                "success": True,
                "record_id": response.data[0]["id"],
                "document": clean_doc,
                "entity_name": entity_name,
                "restriction_count": restriction_count
            }
        else:
            # Alguns clientes do Supabase nÃ£o retornam data no insert, mas o registro Ã© criado
            return {
                "success": True,
                "record_id": None,
                "document": clean_doc,
                "entity_name": entity_name,
                "restriction_count": restriction_count
            }

    except Exception as e:
        return {"success": False, "error": f"Erro ao adicionar monitoramento: {str(e)}"}


def remove_monitored_record(document: str, company_id: str) -> Dict[str, any]:
    """
    Remove documento do monitoramento

    Args:
        document: CPF ou CNPJ
        company_id: ID da empresa

    Returns:
        Dict com success
    """
    try:
        clean_doc = ''.join(filter(str.isdigit, document))

        response = supabase.table("monitoring_targets").delete().eq("document", clean_doc).eq("company_id", company_id).execute()

        return {"success": True, "message": "Registro removido do monitoramento"}

    except Exception as e:
        return {"success": False, "error": f"Erro ao remover monitoramento: {str(e)}"}


def get_monitored_record(document: str, company_id: str) -> Optional[Dict]:
    """
    Busca registro específico de monitoramento

    Args:
        document: CPF ou CNPJ
        company_id: ID da empresa

    Returns:
        Dict com dados do registro ou None
    """
    try:
        clean_doc = ''.join(filter(str.isdigit, document))

        response = supabase.table("monitoring_targets").select("*").eq("document", clean_doc).eq("company_id", company_id).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            return None

    except Exception as e:
        print(f"Erro ao buscar registro: {str(e)}")
        return None


def get_all_monitored_records(
    page: int = 1,
    page_size: int = 10,
    filter_type: Optional[str] = None,
    company_id: str = None
) -> Dict[str, any]:
    """
    Lista todos os registros monitorados

    Args:
        page: Página atual
        page_size: Itens por página
        filter_type: Filtro por tipo (CPF ou CNPJ)
        company_id: ID da empresa

    Returns:
        Dict com records e total
    """
    try:
        offset = (page - 1) * page_size

        # Monta query
        query = supabase.table("monitoring_targets").select("*", count="exact")

        if company_id:
            query = query.eq("company_id", company_id)

        if filter_type:
            query = query.eq("doc_type", filter_type.upper())

        # Conta total
        count_response = query.execute()
        total = count_response.count if hasattr(count_response, 'count') else 0

        # Busca registros
        query = supabase.table("monitoring_targets").select("*")
        if company_id:
            query = query.eq("company_id", company_id)
        if filter_type:
            query = query.eq("doc_type", filter_type.upper())

        response = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()

        records = response.data if response.data else []

        return {
            "success": True,
            "records": records,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    except Exception as e:
        return {"success": False, "error": f"Erro ao listar registros: {str(e)}", "records": [], "total": 0}


def get_monitoring_stats(company_id: str) -> Dict[str, any]:
    """
    Obtém estatísticas do monitoramento

    Args:
        company_id: ID da empresa

    Returns:
        Dict com estatísticas
    """
    try:
        # Total de registros
        response = supabase.table("monitoring_targets").select("*", count="exact").eq("company_id", company_id).execute()
        total = response.count if hasattr(response, 'count') else 0

        # Registros com restrições (precisa buscar data_json)
        all_records = supabase.table("monitoring_targets").select("data_json").eq("company_id", company_id).execute()
        total_with_restrictions = sum(1 for r in (all_records.data or []) if r.get("data_json", {}).get("restriction_count", 0) > 0)

        # Registros ativos
        active = supabase.table("monitoring_targets").select("id", count="exact").eq("company_id", company_id).eq("current_status", "ATIVO").execute()
        total_active = active.count if hasattr(active, 'count') else 0

        # Contagem por tipo
        cpf = supabase.table("monitoring_targets").select("id", count="exact").eq("company_id", company_id).eq("doc_type", "CPF").execute()
        total_cpf = cpf.count if hasattr(cpf, 'count') else 0
        cnpj = supabase.table("monitoring_targets").select("id", count="exact").eq("company_id", company_id).eq("doc_type", "CNPJ").execute()
        total_cnpj = cnpj.count if hasattr(cnpj, 'count') else 0

        return {
            "success": True,
            "total_monitored": total,
            "with_restrictions": total_with_restrictions,
            "active": total_active,
            "inactive": total - total_active,
            "by_type": {
                "CPF": total_cpf,
                "CNPJ": total_cnpj
            }
        }

    except Exception as e:
        return {"success": False, "error": f"Erro ao obter estatísticas: {str(e)}"}


def update_single_record(document: str, company_id: str) -> Dict[str, any]:
    """
    Atualiza um único registro de monitoramento

    Args:
        document: CPF ou CNPJ
        company_id: ID da empresa

    Returns:
        Dict com success e dados atualizados
    """
    try:
        clean_doc = ''.join(filter(str.isdigit, document))

        # Busca registro atual
        current = get_monitored_record(clean_doc, company_id)
        if not current:
            return {"success": False, "error": "Registro não encontrado"}

        # Faz nova consulta
        kyc_data = kyc_engine.run_kyc_check(clean_doc)
        if not kyc_data.get("success"):
            return {"success": False, "error": "Erro na consulta KYC"}

        # Calcula mudanças
        old_data = current.get("data_json", {})
        old_restrictions = old_data.get("restriction_count", 0)
        new_restrictions = kyc_data.get("sanctions", {}).get("total_sanctions", 0)
        has_changes = old_restrictions != new_restrictions

        # Adiciona metadados ao kyc_data (preserva campos salvos)
        entity_name = kyc_engine.get_entity_name(kyc_data)
        if not entity_name or entity_name == "Empresa não identificada":
            entity_name = old_data.get("entity_name")
        notes = old_data.get("notes")
        kyc_data["restriction_count"] = new_restrictions
        if entity_name:
            kyc_data["entity_name"] = entity_name
        if notes is not None:
            kyc_data["notes"] = notes
        kyc_data["last_check_at"] = datetime.utcnow().isoformat()
        kyc_data["has_changes"] = has_changes

        # Atualiza status
        current_status = compute_status(current.get("doc_type"), kyc_data)

        # Atualiza registro (data_json + status)
        update_data = {
            "data_json": kyc_data,
            "current_status": current_status
        }

        response = supabase.table("monitoring_targets").update(update_data).eq("document", clean_doc).eq("company_id", company_id).execute()

        return {
            "success": True,
            "document": clean_doc,
            "old_restrictions": old_restrictions,
            "new_restrictions": new_restrictions,
            "has_changes": has_changes
        }

    except Exception as e:
        return {"success": False, "error": f"Erro ao atualizar registro: {str(e)}"}


def update_all_records(company_id: str) -> Dict[str, any]:
    """
    Atualiza todos os registros de monitoramento da empresa

    Args:
        company_id: ID da empresa

    Returns:
        Dict com estatísticas da atualização
    """
    try:
        # Busca todos os registros
        response = supabase.table("monitoring_targets").select("document").eq("company_id", company_id).execute()

        if not response.data:
            return {"success": True, "total": 0, "updated": 0, "errors": 0}

        total = len(response.data)
        updated = 0
        errors = 0

        for record in response.data:
            result = update_single_record(record["document"], company_id)
            if result.get("success"):
                updated += 1
            else:
                errors += 1

        return {
            "success": True,
            "total": total,
            "updated": updated,
            "errors": errors
        }

    except Exception as e:
        return {"success": False, "error": f"Erro ao atualizar registros: {str(e)}"}


def get_recent_changes(days: int = 2, company_id: str = None) -> Dict[str, any]:
    """
    Obtém registros que tiveram mudanças recentes

    Args:
        days: Número de dias para buscar
        company_id: ID da empresa

    Returns:
        Dict com registros que mudaram
    """
    try:
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        # Busca todos os registros e filtra por data no data_json
        query = supabase.table("monitoring_targets").select("*")

        if company_id:
            query = query.eq("company_id", company_id)

        response = query.order("created_at", desc=True).execute()

        # Filtra localmente por has_changes e last_check_at dentro do data_json
        records = []
        for r in (response.data or []):
            data_json = r.get("data_json", {})
            if data_json.get("has_changes") and data_json.get("last_check_at", "") >= cutoff_date:
                records.append(r)

        return {
            "success": True,
            "changes": records,
            "total": len(records)
        }

    except Exception as e:
        return {"success": False, "error": f"Erro ao buscar mudanças: {str(e)}", "changes": []}
