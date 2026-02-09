"""
KYC Engine - Motor de Consultas
================================
Motor de consultas para APIs públicas (BrasilAPI, ViaCEP, Portal da Transparência)
Autor: Vinicius Matsumoto
"""

import requests
import time
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

TRANSPARENCIA_API_KEY = os.getenv("TRANSPARENCIA_API_KEY")
TRANSPARENCIA_BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"


def validate_document(document: str) -> Dict[str, any]:
    """
    Valida e identifica tipo de documento (CPF ou CNPJ)

    Args:
        document: Documento a ser validado (CPF ou CNPJ)

    Returns:
        Dict com success, doc_type e clean_document
    """
    # Remove caracteres especiais
    clean_doc = ''.join(filter(str.isdigit, document))

    if len(clean_doc) == 11:
        return {"success": True, "doc_type": "CPF", "clean_document": clean_doc}
    elif len(clean_doc) == 14:
        return {"success": True, "doc_type": "CNPJ", "clean_document": clean_doc}
    else:
        return {"success": False, "error": "Documento inválido. Use CPF (11 dígitos) ou CNPJ (14 dígitos)"}


def query_cnpj(cnpj: str) -> Dict[str, any]:
    """
    Consulta dados de CNPJ via BrasilAPI

    Args:
        cnpj: CNPJ limpo (14 dígitos)

    Returns:
        Dict com dados da empresa ou erro
    """
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        response = requests.get(url, timeout=10)
        if response.status_code == 429:
            for delay in (1, 2, 4):
                time.sleep(delay)
                response = requests.get(url, timeout=10)
                if response.status_code != 429:
                    break

        if response.status_code == 200:
            data = response.json()
            data_inicio_atividade = data.get("data_inicio_atividade") or data.get("data_abertura") or ""

            # Se a BrasilAPI não trouxer data de abertura, tenta ReceitaWS para preencher
            if not data_inicio_atividade:
                fallback = query_cnpj_receitaws(cnpj)
                if fallback.get("success"):
                    data_inicio_atividade = (
                        fallback.get("data_abertura")
                        or fallback.get("data_inicio_atividade")
                        or ""
                    )
                    if not data.get("razao_social"):
                        data["razao_social"] = fallback.get("razao_social")
                    if not data.get("nome_fantasia"):
                        data["nome_fantasia"] = fallback.get("nome_fantasia")
                    if not data.get("descricao_situacao_cadastral"):
                        data["descricao_situacao_cadastral"] = fallback.get("situacao_cadastral")
                    if not data.get("situacao_cadastral"):
                        data["situacao_cadastral"] = fallback.get("situacao_cadastral")

            razao_social = (
                data.get("razao_social")
                or data.get("razaoSocial")
                or data.get("nome_empresarial")
                or data.get("nomeEmpresarial")
                or data.get("nome")
            )
            nome_fantasia = (
                data.get("nome_fantasia")
                or data.get("nomeFantasia")
                or data.get("fantasia")
            )

            return {
                "success": True,
                "razao_social": razao_social or "",
                "nome_fantasia": nome_fantasia or "",
                "cnpj": data.get("cnpj", cnpj),
                "situacao_cadastral": data.get("descricao_situacao_cadastral", data.get("situacao_cadastral", "")),
                "data_abertura": data_inicio_atividade or "",
                "porte": data.get("porte", ""),
                "natureza_juridica": data.get("natureza_juridica", ""),
                "endereco": {
                    "logradouro": data.get("logradouro", ""),
                    "numero": data.get("numero", ""),
                    "complemento": data.get("complemento", ""),
                    "bairro": data.get("bairro", ""),
                    "municipio": data.get("municipio", ""),
                    "uf": data.get("uf", ""),
                    "cep": data.get("cep", "")
                },
                "telefone": data.get("ddd_telefone_1", ""),
                "email": data.get("email", ""),
                "capital_social": data.get("capital_social", 0),
                "qsa": data.get("qsa", [])
            }
        else:
            # Fallback para ReceitaWS quando BrasilAPI falhar
            fallback = query_cnpj_receitaws(cnpj)
            if fallback.get("success"):
                return fallback
            return {"success": False, "error": f"CNPJ não encontrado (status {response.status_code})"}

    except Exception as e:
        return {"success": False, "error": f"Erro ao consultar CNPJ: {str(e)}"}


def query_cnpj_receitaws(cnpj: str) -> Dict[str, any]:
    """
    Fallback de consulta de CNPJ via ReceitaWS (sem chave)
    """
    try:
        url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
        response = requests.get(url, timeout=15, headers={"User-Agent": "KYC-System"})
        if response.status_code != 200:
            return {"success": False, "error": f"ReceitaWS erro (status {response.status_code})"}

        data = response.json()
        if data.get("status") == "ERROR":
            return {"success": False, "error": data.get("message", "Erro ReceitaWS")}

        razao_social = data.get("nome") or data.get("razao_social") or data.get("nome_empresarial")
        nome_fantasia = data.get("fantasia") or data.get("nome_fantasia")
        situacao = data.get("situacao") or data.get("situacao_cadastral")

        return {
            "success": True,
            "razao_social": razao_social or "",
            "nome_fantasia": nome_fantasia or "",
            "cnpj": data.get("cnpj", cnpj),
            "situacao_cadastral": situacao or "",
            "data_abertura": data.get("abertura", ""),
            "porte": data.get("porte", ""),
            "natureza_juridica": data.get("natureza_juridica", ""),
            "endereco": {
                "logradouro": data.get("logradouro", ""),
                "numero": data.get("numero", ""),
                "complemento": data.get("complemento", ""),
                "bairro": data.get("bairro", ""),
                "municipio": data.get("municipio", data.get("cidade", "")),
                "uf": data.get("uf", ""),
                "cep": data.get("cep", "")
            },
            "telefone": data.get("telefone", ""),
            "email": data.get("email", ""),
            "capital_social": data.get("capital_social", 0),
            "qsa": data.get("qsa", [])
        }

    except Exception as e:
        return {"success": False, "error": f"Erro ao consultar ReceitaWS: {str(e)}"}


def query_cep(cep: str) -> Dict[str, any]:
    """
    Consulta CEP via ViaCEP

    Args:
        cep: CEP limpo (8 dígitos)

    Returns:
        Dict com dados do endereço ou erro
    """
    try:
        clean_cep = ''.join(filter(str.isdigit, cep))
        url = f"https://viacep.com.br/ws/{clean_cep}/json/"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "erro" not in data:
                return {
                    "success": True,
                    "cep": data.get("cep", ""),
                    "logradouro": data.get("logradouro", ""),
                    "complemento": data.get("complemento", ""),
                    "bairro": data.get("bairro", ""),
                    "localidade": data.get("localidade", ""),
                    "uf": data.get("uf", ""),
                    "ibge": data.get("ibge", "")
                }
            else:
                return {"success": False, "error": "CEP não encontrado"}
        else:
            return {"success": False, "error": f"Erro na consulta (status {response.status_code})"}

    except Exception as e:
        return {"success": False, "error": f"Erro ao consultar CEP: {str(e)}"}


def query_sanctions(document: str, doc_type: str) -> Dict[str, any]:
    """
    Consulta sanções no Portal da Transparência (CEIS, CNEP, CEPIM)

    Args:
        document: CPF ou CNPJ limpo
        doc_type: 'CPF' ou 'CNPJ'

    Returns:
        Dict com listas de sanções encontradas
    """
    if not TRANSPARENCIA_API_KEY:
        return {"success": False, "error": "API Key do Portal da Transparência não configurada"}

    headers = {"chave-api-dados": TRANSPARENCIA_API_KEY}
    results = {
        "success": True,
        "ceis": [],
        "cnep": [],
        "cepim": [],
        "total_sanctions": 0
    }

    # CEIS - Cadastro de Empresas Inidôneas e Suspensas
    try:
        param_name = "codigoCpfCnpj" if doc_type == "CNPJ" else "cpfCnpj"
        url = f"{TRANSPARENCIA_BASE_URL}/ceis?{param_name}={document}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Filtro local para garantir que é o documento correto
            filtered = [item for item in data if str(item.get("cpfCnpjSancionado", "")).replace("***", "") == document or
                       str(item.get("cnpjSancionado", "")) == document]
            results["ceis"] = filtered
    except:
        pass

    # CNEP - Cadastro Nacional de Empresas Punidas
    try:
        param_name = "codigoCnpj" if doc_type == "CNPJ" else "cpf"
        url = f"{TRANSPARENCIA_BASE_URL}/cnep?{param_name}={document}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            filtered = [item for item in data if str(item.get("cnpjCpfSancionado", "")) == document]
            results["cnep"] = filtered
    except:
        pass

    # CEPIM - Cadastro de Entidades Privadas Sem Fins Lucrativos Impedidas
    try:
        url = f"{TRANSPARENCIA_BASE_URL}/cepim?cnpj={document}" if doc_type == "CNPJ" else None
        if url:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                filtered = [item for item in data if str(item.get("cnpj", "")) == document]
                results["cepim"] = filtered
    except:
        pass

    results["total_sanctions"] = len(results["ceis"]) + len(results["cnep"]) + len(results["cepim"])

    return results


def run_kyc_check(document: str, cep: Optional[str] = None) -> Dict[str, any]:
    """
    Executa verificação KYC completa

    Args:
        document: CPF ou CNPJ
        cep: CEP opcional para consulta adicional

    Returns:
        Dict com todos os dados coletados
    """
    # 1. Valida documento
    validation = validate_document(document)
    if not validation["success"]:
        return validation

    doc_type = validation["doc_type"]
    clean_document = validation["clean_document"]

    result = {
        "success": True,
        "document": clean_document,
        "doc_type": doc_type,
        "cadastral_data": {},
        "sanctions": {},
        "address_data": {}
    }

    # 2. Consulta dados cadastrais (apenas CNPJ via BrasilAPI)
    if doc_type == "CNPJ":
        cnpj_data = query_cnpj(clean_document)
        result["cadastral_data"] = cnpj_data

        # Se CNPJ tem CEP, usa ele
        if cnpj_data.get("success") and cnpj_data.get("endereco", {}).get("cep"):
            cep = cnpj_data["endereco"]["cep"]

    # 3. Consulta CEP se fornecido
    if cep:
        cep_data = query_cep(cep)
        result["address_data"] = cep_data

    # 4. Consulta sanções
    sanctions = query_sanctions(clean_document, doc_type)
    result["sanctions"] = sanctions

    # 5. Calcula nível de risco básico
    total_sanctions = sanctions.get("total_sanctions", 0)
    if total_sanctions > 0:
        result["risk_level"] = "ALTO"
    elif doc_type == "CNPJ":
        situacao = result["cadastral_data"].get("situacao_cadastral", "").upper()
        if "ATIVA" in situacao:
            result["risk_level"] = "BAIXO"
        else:
            result["risk_level"] = "MÉDIO"
    else:
        result["risk_level"] = "BAIXO"

    return result


# Funções auxiliares para compatibilidade
def get_entity_name(kyc_data: Dict) -> str:
    """Extrai nome da entidade do resultado KYC"""
    if kyc_data.get("doc_type") == "CNPJ":
        cadastral = kyc_data.get("cadastral_data", {})
        return (
            cadastral.get("razao_social")
            or cadastral.get("nome_fantasia")
            or cadastral.get("nome_empresarial")
            or cadastral.get("nome")
            or "Empresa não identificada"
        )
    else:
        return f"CPF {kyc_data.get('document', '')}"
