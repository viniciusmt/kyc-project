# 📊 Schema Atual do Banco - Sistema KYC

## ✅ Tabela: dossiers (Confirmado e Funcionando)

```sql
CREATE TABLE public.dossiers (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL,
  document_value TEXT NOT NULL,
  entity_name TEXT NULL,
  risk_level TEXT NULL,
  report_data JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now()),
  parecer_tecnico_compliance TEXT NULL,
  status_decisao TEXT NULL DEFAULT 'PENDENTE'::text,
  aprovado_por_diretoria BOOLEAN NULL DEFAULT false,
  justificativa_diretoria TEXT NULL,
  data_decisao TIMESTAMP WITH TIME ZONE NULL,
  decisor_id UUID NULL,
  CONSTRAINT dossiers_pkey PRIMARY KEY (id),
  CONSTRAINT dossiers_company_id_fkey FOREIGN KEY (company_id) REFERENCES companies(id)
) TABLESPACE pg_default;
```

### Campos e Descrição

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | ID único do dossiê (PK) |
| `company_id` | UUID | ID da empresa (multi-tenant) |
| `document_value` | TEXT | CPF ou CNPJ (apenas números) |
| `entity_name` | TEXT | Nome da pessoa/empresa |
| `risk_level` | TEXT | Nível de risco: BAIXO, MÉDIO ou ALTO |
| `report_data` | JSONB | **Snapshot completo** da consulta KYC |
| `created_at` | TIMESTAMPTZ | Data de criação do dossiê |
| `parecer_tecnico_compliance` | TEXT | Parecer técnico do compliance |
| `status_decisao` | TEXT | PENDENTE, APROVADO ou REPROVADO |
| `aprovado_por_diretoria` | BOOLEAN | Se foi aprovado (true/false) |
| `justificativa_diretoria` | TEXT | Justificativa da decisão |
| `data_decisao` | TIMESTAMPTZ | Data/hora da decisão |
| `decisor_id` | UUID | ID do usuário que tomou a decisão |

---

## 📦 Estrutura do report_data (JSONB)

O campo `report_data` armazena um **snapshot completo** dos dados no momento da consulta:

```json
{
  "document": "06990590000123",
  "doc_type": "CNPJ",
  "risk_level": "BAIXO",
  "generated_at": "2026-02-08T21:30:00.000Z",

  "cadastral_data": {
    "success": true,
    "razao_social": "GOOGLE BRASIL INTERNET LTDA.",
    "nome_fantasia": "GOOGLE",
    "cnpj": "06.990.590/0001-23",
    "situacao_cadastral": "ATIVA",
    "data_abertura": "2003-06-03",
    "porte": "DEMAIS",
    "natureza_juridica": "Sociedade Empresária Limitada",
    "endereco": {
      "logradouro": "Avenida Brigadeiro Faria Lima",
      "numero": "3477",
      "complemento": "7 andar",
      "bairro": "Itaim Bibi",
      "municipio": "São Paulo",
      "uf": "SP",
      "cep": "04538-133"
    },
    "telefone": "1133323300",
    "email": "",
    "capital_social": 81800000.0,
    "qsa": [
      {
        "nome": "GOOGLE LLC",
        "qual": "Sócio"
      }
    ]
  },

  "sanctions": {
    "success": true,
    "ceis": [],
    "cnep": [],
    "cepim": [],
    "total_sanctions": 0
  },

  "address_data": {
    "success": true,
    "cep": "04538-133",
    "logradouro": "Avenida Brigadeiro Faria Lima",
    "bairro": "Itaim Bibi",
    "localidade": "São Paulo",
    "uf": "SP"
  },

  "ai_analysis": null
}
```

---

## 🔄 Fluxo de Dados

### 1. Criação do Dossiê

```
Usuario -> Frontend -> Backend -> KYC Engine -> APIs Externas
                                               ├─ BrasilAPI (CNPJ)
                                               ├─ ViaCEP (CEP)
                                               └─ Portal Transparência (Sanções)

                           Backend <- report_data (snapshot)
                           Backend -> Supabase (salva dossiê)
```

### 2. Decisão de Diretoria

```
Usuario -> Frontend -> Backend -> Supabase
   (preenche parecer e justificativa)

   UPDATE dossiers SET
     parecer_tecnico_compliance = '...',
     status_decisao = 'APROVADO',
     aprovado_por_diretoria = true,
     justificativa_diretoria = '...',
     data_decisao = NOW(),
     decisor_id = user_id
   WHERE id = dossier_id AND company_id = user_company_id
```

---

## ✅ Sistema Adaptado e Funcionando

O código foi **adaptado para o schema existente** da tabela `dossiers`:

- ✅ Não usa coluna `document_type` separada (tipo fica dentro do `report_data`)
- ✅ Todos os campos de decisão estão incluídos
- ✅ Compatível com a estrutura atual do banco
- ✅ APIs externas testadas e funcionando

---

## 🧪 Teste Rápido

Para testar a geração de dossiê:

```bash
cd C:\Users\Vinicius\Projetos\KYC
python test_apis.py
```

Resultado esperado:
- ✅ BrasilAPI funcionando
- ✅ ViaCEP funcionando
- ✅ Portal da Transparência funcionando
- ✅ Consulta KYC completa funcionando

---

**Sistema pronto para uso!** 🚀
