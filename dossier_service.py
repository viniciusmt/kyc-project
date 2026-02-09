"""
Dossier Service - Gerenciamento de Dossiês
===========================================
Gerencia dossiês persistentes no Supabase com snapshot dos dados
Autor: Vinicius Matsumoto
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from supabase import create_client, Client
from dotenv import load_dotenv
import kyc_engine
import time
try:
    import google.generativeai as genai
except Exception:
    genai = None

load_dotenv()

# Inicializa Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def _build_ai_prompt(kyc_data: Dict, report_data: Dict) -> str:
    doc = kyc_data.get("document", "")
    doc_type = kyc_data.get("doc_type", "")
    risk = kyc_data.get("risk_level", "DESCONHECIDO")
    cadastral = kyc_data.get("cadastral_data", {}) or {}
    sanctions = kyc_data.get("sanctions", {}) or {}
    total_sanctions = sanctions.get("total_sanctions", 0)
    name = (
        cadastral.get("razao_social")
        or cadastral.get("nome_fantasia")
        or cadastral.get("nome")
        or f"{doc_type} {doc}"
    )
    situacao = (
        cadastral.get("situacao_cadastral")
        or cadastral.get("descricao_situacao_cadastral")
        or cadastral.get("situacao")
        or "N/A"
    )

    return (
        "Você é um analista de compliance. Gere uma análise curta (4-6 linhas) e objetiva.\n"
        f"Documento: {doc} ({doc_type})\n"
        f"Entidade: {name}\n"
        f"Situação cadastral: {situacao}\n"
        f"Nível de risco calculado: {risk}\n"
        f"Total de sanções encontradas: {total_sanctions}\n"
        "Inclua uma recomendação final simples (Aprovar / Revisar / Reprovar) com base nos dados.\n"
    )


def _generate_ai_analysis(kyc_data: Dict, report_data: Dict) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "IA não configurada: defina GEMINI_API_KEY para habilitar a análise."
    if genai is None:
        return "IA indisponível: biblioteca google-generativeai não está instalada."

    try:
        genai.configure(api_key=api_key)
        preferred_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        fallback_models = [
            preferred_model,
            "gemini-2.0-flash",
            "gemini-1.5-flash",
        ]
        prompt = _build_ai_prompt(kyc_data, report_data)
        last_error = None
        for model_name in fallback_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = getattr(response, "text", None)
                if text:
                    return text.strip()
                last_error = "IA retornou resposta vazia."
            except Exception as e:
                last_error = str(e)
                continue
        return f"IA falhou ao gerar análise: {last_error}"
    except Exception as e:
        return f"IA falhou ao gerar análise: {str(e)}"

def _normalize_cnpj_cadastral(cadastral: Dict) -> Dict[str, any]:
    if not cadastral:
        return {}

    razao_social = (
        cadastral.get("razao_social")
        or cadastral.get("razaoSocial")
        or cadastral.get("nome_empresarial")
        or cadastral.get("nomeEmpresarial")
        or cadastral.get("nome")
    )
    nome_fantasia = (
        cadastral.get("nome_fantasia")
        or cadastral.get("nomeFantasia")
        or cadastral.get("fantasia")
    )
    situacao_cadastral = (
        cadastral.get("descricao_situacao_cadastral")
        or cadastral.get("situacao_cadastral")
        or cadastral.get("situacao")
    )
    data_abertura = cadastral.get("data_inicio_atividade") or cadastral.get("abertura")
    capital_social = cadastral.get("capital_social")
    porte = cadastral.get("porte")
    natureza_juridica = cadastral.get("natureza_juridica")

    endereco = cadastral.get("endereco", {}) or {}
    if not endereco:
        endereco = {
            "logradouro": cadastral.get("logradouro", ""),
            "numero": cadastral.get("numero", ""),
            "complemento": cadastral.get("complemento", ""),
            "bairro": cadastral.get("bairro", ""),
            "municipio": cadastral.get("municipio", cadastral.get("cidade", "")),
            "uf": cadastral.get("uf", ""),
            "cep": cadastral.get("cep", ""),
        }

    return {
        "razao_social": razao_social or "",
        "nome_fantasia": nome_fantasia or "",
        "situacao_cadastral": situacao_cadastral or "",
        "descricao_situacao_cadastral": situacao_cadastral or "",
        "data_abertura": data_abertura or "",
        "data_inicio_atividade": data_abertura or "",
        "capital_social": capital_social or "",
        "porte": porte or "",
        "natureza_juridica": natureza_juridica or "",
        "endereco": endereco,
        "qsa": cadastral.get("qsa", []),
        "success": cadastral.get("success", False),
    }


def _fallback_entity_name(dossier: Dict) -> str:
    entity_name = dossier.get("entity_name")
    if entity_name and entity_name != "Empresa não identificada":
        return entity_name

    report_data = dossier.get("report_data", {}) or {}
    if isinstance(report_data, str):
        return entity_name or ""

    technical = report_data.get("technical_report", {}) or {}
    derived = technical.get("derived", {}) or {}
    company_summary = derived.get("company_summary", {}) or {}

    name = (
        company_summary.get("razao_social")
        or company_summary.get("nome_fantasia")
        or company_summary.get("nome_empresarial")
        or company_summary.get("nome")
    )

    if not name:
        doc = dossier.get("document_value") or ""
        name = f"CNPJ {doc}" if len(str(doc)) == 14 else f"CPF {doc}"

    return name


def generate_and_save_dossier(
    document: str,
    company_id: str,
    enable_ai: bool = False,
    cep: Optional[str] = None
) -> Dict[str, any]:
    """
    Gera e salva dossiê no Supabase

    Args:
        document: CPF ou CNPJ
        company_id: ID da empresa (multi-tenant)
        enable_ai: Se deve executar análise de IA (Gemini)
        cep: CEP opcional

    Returns:
        Dict com success, dossier_id e dados
    """
    try:
        # 1. Executa consulta KYC
        kyc_data = kyc_engine.run_kyc_check(document, cep)

        if not kyc_data.get("success"):
            return {"success": False, "error": kyc_data.get("error", "Erro na consulta KYC")}

        # 2. Extrai informações principais
        entity_name = kyc_engine.get_entity_name(kyc_data)
        if not entity_name or entity_name == "Empresa não identificada":
            if kyc_data.get("doc_type") == "CNPJ":
                cadastral = kyc_data.get("cadastral_data", {}) or {}
                entity_name = (
                    cadastral.get("razao_social")
                    or cadastral.get("nome_fantasia")
                    or cadastral.get("nome_empresarial")
                    or cadastral.get("nome")
                )
            if not entity_name:
                if kyc_data.get("doc_type") == "CNPJ":
                    entity_name = f"CNPJ {kyc_data.get('document', '')}"
                else:
                    entity_name = f"CPF {kyc_data.get('document', '')}"
        risk_level = kyc_data.get("risk_level", "BAIXO")

        # 3. Monta report_data (formato esperado pelo frontend)
        cadastral = kyc_data.get("cadastral_data", {})
        normalized_cadastral = _normalize_cnpj_cadastral(cadastral) if kyc_data.get("doc_type") == "CNPJ" else {}
        receitaws_data = {}
        if kyc_data.get("doc_type") == "CNPJ" and not normalized_cadastral.get("data_abertura"):
            receitaws_data = kyc_engine.query_cnpj_receitaws(kyc_data.get("document", "")) or {}
            if receitaws_data.get("success"):
                # Preenche campos faltantes com fallback ReceitaWS
                for key in [
                    "razao_social",
                    "nome_fantasia",
                    "situacao_cadastral",
                    "data_abertura",
                    "capital_social",
                    "porte",
                    "natureza_juridica",
                    "endereco",
                    "qsa",
                ]:
                    if not normalized_cadastral.get(key):
                        normalized_cadastral[key] = receitaws_data.get(key, normalized_cadastral.get(key))
                normalized_cadastral["success"] = True
        sanctions_data = kyc_data.get("sanctions", {})

        # Estrutura compatível com o frontend
        report_data = {
            "metadata": {
                "document_type": kyc_data.get("doc_type"),
                "generated_at": datetime.utcnow().isoformat()
            },
            "technical_report": {
                "input": {
                    "document": kyc_data.get("document"),
                    "type": kyc_data.get("doc_type")
                },
                "sources": {
                    "brasilapi_cnpj": {
                        "ok": bool(normalized_cadastral) and normalized_cadastral.get("success", False),
                        "data": normalized_cadastral if normalized_cadastral else {}
                    },
                    "receitaws_cnpj": {
                        "ok": bool(receitaws_data) and receitaws_data.get("success", False),
                        "data": receitaws_data if receitaws_data else {}
                    },
                    "transparencia_ceis": {
                        "ok": sanctions_data.get("success", False),
                        "data": sanctions_data.get("ceis", [])
                    },
                    "transparencia_cnep": {
                        "ok": sanctions_data.get("success", False),
                        "data": sanctions_data.get("cnep", [])
                    },
                    "transparencia_cepim": {
                        "ok": sanctions_data.get("success", False),
                        "data": sanctions_data.get("cepim", [])
                    }
                },
                "derived": {
                    "company_summary": {
                        "razao_social": normalized_cadastral.get("razao_social"),
                        "nome_fantasia": normalized_cadastral.get("nome_fantasia"),
                        "situacao_cadastral": normalized_cadastral.get("situacao_cadastral"),
                        "data_abertura": normalized_cadastral.get("data_abertura"),
                        "capital_social": normalized_cadastral.get("capital_social"),
                        "porte": normalized_cadastral.get("porte"),
                        "natureza_juridica": normalized_cadastral.get("natureza_juridica"),
                    },
                    "qsa_enriched": normalized_cadastral.get("qsa", [])
                }
            },
            "sanctions": sanctions_data,
            "ai_analysis": None
        }

        # 4. Análise de IA (se habilitada)
        if enable_ai:
            report_data["ai_analysis"] = _generate_ai_analysis(kyc_data, report_data)

        # 5. Salva no Supabase (schema correto da tabela)
        dossier_record = {
            "company_id": company_id,
            "document_value": kyc_data.get("document"),
            "entity_name": entity_name,
            "risk_level": risk_level,
            "report_data": report_data,
            "status_decisao": "PENDENTE",
            "aprovado_por_diretoria": False,
            "parecer_tecnico_compliance": None,
            "justificativa_diretoria": None,
            "data_decisao": None,
            "decisor_id": None
        }

        response = supabase.table("dossiers").insert(dossier_record).execute()

        if response.data and len(response.data) > 0:
            dossier_id = response.data[0]["id"]
            return {
                "success": True,
                "dossier_id": dossier_id,
                "entity_name": entity_name,
                "risk_level": risk_level,
                "document": kyc_data.get("document"),
                "doc_type": kyc_data.get("doc_type")
            }
        else:
            return {"success": False, "error": "Erro ao salvar dossiê no banco"}

    except Exception as e:
        return {"success": False, "error": f"Erro ao gerar dossiê: {str(e)}"}


def list_dossiers(
    company_id: str,
    page: int = 1,
    page_size: int = 20
) -> Tuple[List[Dict], int]:
    """
    Lista dossiês da empresa com paginação

    Args:
        company_id: ID da empresa
        page: Página atual
        page_size: Itens por página

    Returns:
        Tuple (lista de dossiês, total de registros)
    """
    try:
        offset = (page - 1) * page_size

        # Conta total
        count_response = supabase.table("dossiers").select("id", count="exact").eq("company_id", company_id).execute()
        total = count_response.count if hasattr(count_response, 'count') else 0

        # Busca registros paginados
        response = supabase.table("dossiers").select("*").eq("company_id", company_id).order("created_at", desc=True).range(offset, offset + page_size - 1).execute()

        dossiers = response.data if response.data else []
        for d in dossiers:
            d["entity_name"] = _fallback_entity_name(d)

        return dossiers, total

    except Exception as e:
        print(f"Erro ao listar dossiês: {str(e)}")
        return [], 0


def get_dossier_by_id(dossier_id: str, company_id: str) -> Optional[Dict]:
    """
    Busca dossiê por ID (com validação de empresa)

    Args:
        dossier_id: ID do dossiê
        company_id: ID da empresa (segurança multi-tenant)

    Returns:
        Dossiê ou None
    """
    try:
        response = supabase.table("dossiers").select("*").eq("id", dossier_id).eq("company_id", company_id).execute()

        if response.data and len(response.data) > 0:
            dossier = response.data[0]
            dossier["entity_name"] = _fallback_entity_name(dossier)
            return dossier
        else:
            return None

    except Exception as e:
        print(f"Erro ao buscar dossiê: {str(e)}")
        return None


def check_duplicate_dossier(document: str, company_id: str) -> Optional[str]:
    """
    Verifica se já existe dossiê para o documento

    Args:
        document: CPF ou CNPJ
        company_id: ID da empresa

    Returns:
        ID do dossiê existente ou None
    """
    try:
        # Limpa documento
        clean_doc = ''.join(filter(str.isdigit, document))

        response = supabase.table("dossiers").select("id").eq("document_value", clean_doc).eq("company_id", company_id).limit(1).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
        else:
            return None

    except Exception as e:
        print(f"Erro ao verificar duplicata: {str(e)}")
        return None


def process_batch(
    documents: List[str],
    company_id: str,
    enable_ai: bool = False,
    delay_seconds: int = 2
) -> Dict[str, any]:
    """
    Processa múltiplos dossiês em lote

    Args:
        documents: Lista de CPF/CNPJ
        company_id: ID da empresa
        enable_ai: Se deve usar IA
        delay_seconds: Delay entre requisições

    Returns:
        Dict com resultados do processamento
    """
    results = {
        "total": len(documents),
        "success_count": 0,
        "error_count": 0,
        "dossiers": [],
        "errors": []
    }

    for idx, document in enumerate(documents):
        try:
            # Verifica duplicata
            existing_id = check_duplicate_dossier(document, company_id)
            if existing_id:
                results["errors"].append({
                    "document": document,
                    "error": "Dossiê já existe",
                    "existing_id": existing_id
                })
                results["error_count"] += 1
                continue

            # Gera dossiê
            result = generate_and_save_dossier(document, company_id, enable_ai)

            if result.get("success"):
                results["dossiers"].append(result)
                results["success_count"] += 1
            else:
                results["errors"].append({
                    "document": document,
                    "error": result.get("error", "Erro desconhecido")
                })
                results["error_count"] += 1

            # Delay entre requisições (evita rate limit)
            if idx < len(documents) - 1:
                time.sleep(delay_seconds)

        except Exception as e:
            results["errors"].append({
                "document": document,
                "error": str(e)
            })
            results["error_count"] += 1

    return results


def update_dossier_decision(
    dossier_id: str,
    company_id: str,
    parecer_tecnico: str,
    aprovado: bool,
    justificativa: str = ""
) -> Dict[str, any]:
    """
    Atualiza decisão de diretoria no dossiê

    Args:
        dossier_id: ID do dossiê
        company_id: ID da empresa
        parecer_tecnico: Parecer do compliance
        aprovado: Se foi aprovado
        justificativa: Justificativa da diretoria

    Returns:
        Dict com success e dados atualizados
    """
    try:
        update_data = {
            "parecer_tecnico_compliance": parecer_tecnico,
            "aprovado_por_diretoria": aprovado,
            "status_decisao": "APROVADO" if aprovado else "REPROVADO",
            "justificativa_diretoria": justificativa,
            "data_decisao": datetime.utcnow().isoformat()
        }

        response = supabase.table("dossiers").update(update_data).eq("id", dossier_id).eq("company_id", company_id).execute()

        if response.data and len(response.data) > 0:
            return {
                "success": True,
                "status_decisao": update_data["status_decisao"],
                "data_decisao": update_data["data_decisao"]
            }
        else:
            return {"success": False, "error": "Dossiê não encontrado ou sem permissão"}

    except Exception as e:
        return {"success": False, "error": f"Erro ao atualizar decisão: {str(e)}"}
