# 🧱 Stack Técnica (v2)

Documento técnico para onboarding e contexto rápido do projeto.

---

## 1) Frontend

- **Framework:** Next.js (App Router)
- **Linguagem:** TypeScript
- **Estilo:** Tailwind CSS
- **HTTP client:** Axios
- **Auth:** JWT armazenado no localStorage

### Pastas-chave
- `frontend/src/app` → páginas
- `frontend/src/components` → UI
- `frontend/src/services` → integração API
- `frontend/src/types` → tipos TS

---

## 2) Backend

- **Framework:** FastAPI
- **Auth:** Supabase Auth + JWT
- **Banco:** Supabase (PostgreSQL + RLS)
- **Serviços core:**
  - `dossier_service.py` (dossiês)
  - `monitoring_engine.py` (monitoramento)
  - `kyc_engine.py` (consultas públicas)

### Pastas-chave
- `backend/app/main.py` → FastAPI entry
- `backend/app/routers` → auth/dossiers/monitoring
- `backend/app/services` → wrappers
- `backend/app/core/config.py` → settings/env

---

## 3) APIs externas

- **BrasilAPI (CNPJ)**
- **ViaCEP (CEP)**
- **Portal da Transparência** (CEIS/CNEP/CEPIM)

> Observação: sanções são filtradas localmente por CPF/CNPJ.

---

## 4) Supabase (schema básico)

### Tabela `dossiers`
- `id` (UUID)
- `company_id`
- `document_value`
- `entity_name`
- `risk_level`
- `report_data` (JSONB)
- `created_at`

### Tabela `monitoring_targets`
- `id` (UUID)
- `company_id`
- `document`
- `document_type` ou `doc_type`
- `status` ou `current_status`
- `restriction_count`
- `data_json` (JSONB)
- `created_at`, `updated_at`

RLS ativo para isolamento por empresa.

---

## 5) Execução local

### Backend
```bash
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

---

## 6) Observações importantes

- Dossiê = snapshot persistido (não reconsulta APIs ao abrir)
- Monitoramento usa atualização manual ou em lote
- JWT no frontend, validação no backend

---

© 2026 Vinicius Matsumoto
