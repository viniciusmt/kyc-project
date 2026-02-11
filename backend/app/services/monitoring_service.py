"""
Monitoring Service - Wrapper
=============================
Wrapper para o monitoring_engine.py existente
"""

import json

from app.monitoring_engine import (
    add_monitored_record,
    remove_monitored_record,
    get_monitored_record,
    get_all_monitored_records,
    get_monitoring_stats,
    update_single_record,
    update_all_records,
    get_recent_changes,
    compute_status
)


class MonitoringService:
    """Serviço de monitoramento (wrapper)"""

    def add_record(self, document: str, company_id: str, notes: str = ""):
        """Adiciona registro ao monitoramento"""
        return add_monitored_record(document, notes, company_id)

    def remove_record(self, document: str, company_id: str):
        """Remove registro"""
        return remove_monitored_record(document, company_id)

    def get_record(self, document: str, company_id: str):
        """Obtém registro específico"""
        return get_monitored_record(document, company_id)

    def get_all_records(self, company_id: str, page: int = 1, page_size: int = 10, filter_type: str = None):
        """Lista todos os registros com dados extraídos do data_json"""
        result = get_all_monitored_records(
            page=page,
            page_size=page_size,
            filter_type=filter_type,
            company_id=company_id
        )

        # Extrai dados do data_json e normaliza campos (compatibilidade com frontend)
        if result.get("success") and result.get("records"):
            enriched_records = []
            for record in result["records"]:
                data_json = record.get("data_json", {}) or {}
                if isinstance(data_json, str):
                    try:
                        data_json = json.loads(data_json)
                    except Exception:
                        data_json = {}
                restriction_count = data_json.get("restriction_count", 0)
                doc_type = record.get("doc_type") or data_json.get("doc_type") or data_json.get("document_type")

                entity_name = data_json.get("entity_name")
                if not entity_name or entity_name == "Empresa não identificada":
                    if (data_json.get("doc_type") or doc_type) == "CNPJ":
                        cadastral = data_json.get("cadastral_data", {}) or {}
                        entity_name = (
                            cadastral.get("razao_social")
                            or cadastral.get("nome_fantasia")
                            or cadastral.get("nome_empresarial")
                            or cadastral.get("nome")
                            or data_json.get("razao_social")
                            or data_json.get("nome_fantasia")
                        )
                    if not entity_name:
                        if (data_json.get("doc_type") or doc_type) == "CNPJ":
                            entity_name = f"CNPJ {record.get('document', '')}"
                        else:
                            entity_name = f"CPF {record.get('document', '')}"

                notes = data_json.get("notes")

                last_check_at = data_json.get("last_check_at") or record.get("updated_at")

                current_status = record.get("current_status") or compute_status(doc_type, data_json)

                enriched = {
                    **record,
                    "entity_name": entity_name,
                    "notes": notes,
                    "restriction_count": restriction_count,
                    "last_check_at": last_check_at,
                    # Campos esperados pelo frontend
                    "document_type": doc_type,
                    "status": current_status,
                    "last_check": last_check_at,
                    "added_date": record.get("created_at"),
                    "has_restrictions": restriction_count > 0
                }
                enriched_records.append(enriched)
            result["records"] = enriched_records

        return result

    def get_stats(self, company_id: str):
        """Obtém estatísticas"""
        return get_monitoring_stats(company_id)

    def update_single(self, document: str, company_id: str):
        """Atualiza registro único"""
        return update_single_record(document, company_id)

    def update_all(self, company_id: str):
        """Atualiza todos os registros"""
        return update_all_records(company_id)

    def get_recent_changes(self, company_id: str, days: int = 2):
        """Obtém mudanças recentes"""
        return get_recent_changes(days=days, company_id=company_id)
