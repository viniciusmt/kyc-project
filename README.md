# 🔍 Sistema KYC - Dossiês e Monitoramento (v2)

Sistema profissional de **Know Your Customer (KYC)** focado em compliance e análise de risco, com **frontend em React/Next.js** e **backend em FastAPI** integrado ao Supabase. O projeto é multi-tenant (isolamento por empresa) e gera **dossiês persistentes** com “fotografia” dos dados no momento da consulta.

---

## ✨ Principais recursos

- Dossiê de CPF/CNPJ com dados cadastrais e sanções
- **Fluxo de decisão de diretoria** (aprovação/reprovação de clientes)
- Monitoramento contínuo com atualização de registros
- Multi-tenant por empresa (company_id)
- URLs únicas por dossiê (acesso histórico)
- Processamento em lote (batch)
- Integração com APIs públicas (BrasilAPI, ViaCEP, Portal da Transparência)

---

## ✅ Melhorias recentes (Fev/2026)

- Monitoramento: resposta idempotente no `POST /api/monitoring/` quando o documento já existe (retorna sucesso em vez de erro).
- Monitoramento: normalização de `data_json` no backend para preencher `entity_name`, `notes`, `status` e `last_check`.
- Monitoramento: cálculo de status (CNPJ: ATIVO/INATIVO/DESCONHECIDO; CPF: REGULAR/IRREGULAR).
- KYC engine: tolerância a variações de campos da BrasilAPI (`razao_social`, `nome_fantasia`, `nome_empresarial`, `nome`).
- KYC engine: retry com backoff quando BrasilAPI retorna `429` (rate limit).
- KYC engine: fallback automático para ReceitaWS quando a BrasilAPI falha.
- Dossiê: normalização do `cadastral_data` antes de salvar em `report_data` para garantir campos básicos no frontend.
- Dossiê: fallback de `entity_name` ao listar/buscar dossiês usando `report_data` quando o nome não existe.
- Dossiê: fallback de **data de abertura** via ReceitaWS quando BrasilAPI retornar `data_inicio_atividade` vazio.
- Frontend: aumento de timeout específico para Dossiê e Monitoramento (30s) para evitar falsos erros em consultas lentas.
- Frontend: correção de hidratação no Header (nome da empresa/e-mail só após mount).

---

## 🚀 Quick start (v2)

### Backend (FastAPI)
```bash
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

### Frontend (Next.js)
```bash
cd frontend
npm run dev
```

**URLs**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

---

## 🧱 Estrutura do projeto (v2)

```
KYC/
├── backend/                 # FastAPI + Supabase
│   └── app/
│       ├── main.py
│       ├── core/            # config/env
│       ├── routers/         # rotas auth/dossiers/monitoring
│       └── services/        # wrappers dos serviços
├── frontend/                # Next.js (App Router)
│   └── src/
│       ├── app/             # pages (login, dashboard, dossier, monitoring)
│       ├── components/      # UI components
│       ├── services/        # API clients
│       └── types/           # Tipos TS
├── kyc_engine.py            # Motor de consultas (APIs públicas)
├── dossier_service.py       # Dossiês persistentes (Supabase)
├── monitoring_engine.py     # Monitoramento contínuo
└── docs/                    # Documentação interna
```

---

## 📄 Documentação interna

- `docs/INTERFACE_GUIA.md` – guia de interface (telas, classes e casos de uso)
- `docs/STACK_TECNICO.md` – stack técnica, integrações e dependências

---

## 🔐 Observações de segurança

- Todas as rotas de backend usam JWT via Supabase.
- Operações são filtradas por `company_id` para garantir isolamento.
- Tokens são armazenados no localStorage no frontend (SPA).

---

## 📌 Nota sobre sanções

A API do Portal da Transparência não garante filtro perfeito por CPF/CNPJ. O sistema aplica **filtro local** no backend para exibir apenas sanções relacionadas ao documento consultado.

---

## ⚖️ Fluxo de Governança e Decisão

O sistema possui um fluxo completo para decisão de diretoria sobre dossiês:

### Funcionalidades:
- **Parecer Técnico do Compliance** - Campo obrigatório para análise técnica
- **Justificativa da Diretoria** - Campo opcional para contextualizar a decisão
- **Aprovação/Reprovação** - Botões estilizados para decisão final
- **Status Visual** - Badges coloridos no histórico:
  - 🟢 **APROVADO** - Cliente aprovado
  - 🔴 **REPROVADO** - Cliente reprovado
  - ⏳ **PENDENTE** - Aguardando decisão
- **Modo Somente Leitura** - Após decisão, campos ficam bloqueados
- **Segurança Multi-Tenant** - Validação por `company_id`

### Campos no Banco (Supabase):
```sql
-- Tabela dossiers
parecer_tecnico_compliance  TEXT
status_decisao              TEXT (APROVADO/REPROVADO/PENDENTE)
aprovado_por_diretoria      BOOLEAN
justificativa_diretoria     TEXT
data_decisao                TIMESTAMPTZ
```

### API Endpoint:
```
PUT /api/dossiers/{id}/decide
{
  "parecer_tecnico": "string",
  "aprovado": boolean,
  "justificativa": "string" (opcional)
}
```

---

## 🧩 Próximos passos

Se desejar, podemos adicionar:
- Histórico detalhado de mudanças (change history)
- Exportação em PDF/CSV
- Interface COAF com modos de impressão
- Assinatura digital nas decisões

---

© 2026 Vinicius Matsumoto
