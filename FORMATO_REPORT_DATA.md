# 📊 Formato do report_data - Sistema KYC

## ✅ Estrutura Atualizada e Funcionando

O campo `report_data` (JSONB) na tabela `dossiers` agora segue esta estrutura para compatibilidade total com o frontend:

```json
{
  "metadata": {
    "document_type": "CNPJ",
    "generated_at": "2026-02-08T21:48:00.000Z"
  },

  "technical_report": {
    "input": {
      "document": "33000167000101",
      "type": "CNPJ"
    },

    "sources": {
      "brasilapi_cnpj": {
        "ok": true,
        "data": {
          "success": true,
          "razao_social": "BANCO BRADESCO S.A.",
          "nome_fantasia": "BRADESCO",
          "cnpj": "33.000.167/0001-01",
          "situacao_cadastral": "ATIVA",
          "data_abertura": "1943-03-10",
          "porte": "DEMAIS",
          "natureza_juridica": "Sociedade Anônima Aberta",
          "endereco": {
            "logradouro": "Cidade de Deus Vila Yara",
            "numero": "S/N",
            "complemento": "",
            "bairro": "Vila Yara",
            "municipio": "Osasco",
            "uf": "SP",
            "cep": "06029-900"
          },
          "telefone": "1136844000",
          "email": "",
          "capital_social": 67000000000.0,
          "qsa": [
            {
              "nome": "BRADESCO S.A.",
              "qualificacao": "Presidente"
            }
          ]
        }
      },

      "transparencia_ceis": {
        "ok": true,
        "data": []
      },

      "transparencia_cnep": {
        "ok": true,
        "data": []
      },

      "transparencia_cepim": {
        "ok": true,
        "data": []
      }
    },

    "derived": {
      "company_summary": {
        "razao_social": "BANCO BRADESCO S.A.",
        "nome_fantasia": "BRADESCO",
        "situacao_cadastral": "ATIVA"
      },
      "qsa_enriched": [
        {
          "nome": "BRADESCO S.A.",
          "qualificacao": "Presidente"
        }
      ]
    }
  },

  "sanctions": {
    "success": true,
    "ceis": [],
    "cnep": [],
    "cepim": [],
    "total_sanctions": 0
  },

  "ai_analysis": null
}
```

---

## 🎯 Mapeamento Frontend ↔ Backend

### Dados Básicos (CNPJ)

| Campo no Frontend | Caminho no report_data |
|-------------------|------------------------|
| Razão Social | `technical_report.derived.company_summary.razao_social` |
| Nome Fantasia | `technical_report.derived.company_summary.nome_fantasia` |
| Situação Cadastral | `technical_report.derived.company_summary.situacao_cadastral` |
| Data de Abertura | `technical_report.sources.brasilapi_cnpj.data.data_abertura` |
| Capital Social | `technical_report.sources.brasilapi_cnpj.data.capital_social` |
| Porte | `technical_report.sources.brasilapi_cnpj.data.porte` |

### Endereço

| Campo | Caminho |
|-------|---------|
| Logradouro | `technical_report.sources.brasilapi_cnpj.data.endereco.logradouro` |
| Número | `technical_report.sources.brasilapi_cnpj.data.endereco.numero` |
| Complemento | `technical_report.sources.brasilapi_cnpj.data.endereco.complemento` |
| Bairro | `technical_report.sources.brasilapi_cnpj.data.endereco.bairro` |
| Município | `technical_report.sources.brasilapi_cnpj.data.endereco.municipio` |
| UF | `technical_report.sources.brasilapi_cnpj.data.endereco.uf` |
| CEP | `technical_report.sources.brasilapi_cnpj.data.endereco.cep` |

### Quadro Societário (QSA)

Array em: `technical_report.derived.qsa_enriched`

Cada item contém:
- `nome` - Nome do sócio
- `qualificacao` - Qualificação (Sócio, Administrador, etc.)
- `cpf_cnpj` - CPF/CNPJ do sócio (se disponível)

### Sanções

| Tipo | Caminho |
|------|---------|
| CEIS | `technical_report.sources.transparencia_ceis.data` (array) |
| CNEP | `technical_report.sources.transparencia_cnep.data` (array) |
| CEPIM | `technical_report.sources.transparencia_cepim.data` (array) |
| Total | `sanctions.total_sanctions` |

---

## 🔄 Fluxo de Criação

1. **Frontend** envia documento (CPF/CNPJ)
2. **Backend** chama `kyc_engine.run_kyc_check()`
3. **KYC Engine** consulta:
   - BrasilAPI (CNPJ)
   - ViaCEP (CEP)
   - Portal da Transparência (Sanções)
4. **Dossier Service** monta `report_data` no formato correto
5. **Supabase** salva dossiê com snapshot completo
6. **Frontend** renderiza dados do `report_data`

---

## ✅ Vantagens da Estrutura

1. **Snapshot Completo** - Dados não mudam após criação
2. **Compatibilidade** - Frontend reconhece automaticamente
3. **Rastreabilidade** - Metadata com timestamp
4. **Escalável** - Fácil adicionar novas fontes
5. **Flexível** - JSONB permite queries complexas no PostgreSQL

---

## 🧪 Teste

Para ver um exemplo real do `report_data`:

```bash
cd C:\Users\Vinicius\Projetos\KYC
python test_apis.py
cat resultado_kyc_teste.json
```

---

**Sistema 100% compatível com frontend e backend!** 🚀
