# 🧭 Guia de Interface (v2)

Este documento descreve **as telas principais, classes/componentes e fluxos de uso** do sistema atual.

---

## 1) Telas principais

### Login
- **Caminho:** `/`
- **Componente:** `LoginForm`
- **Objetivo:** autenticação via Supabase (JWT) e redirecionamento para o dashboard.

### Dashboard
- **Caminho:** `/dashboard`
- **Componentes:**
  - `DossierForm` (geração individual)
  - `BatchProcessor` (lote)
  - `DossiersList` (histórico)
- **Objetivo:** gerar e listar dossiês da empresa logada.

### Dossiê
- **Caminho:** `/dossier/[id]`
- **Renderiza:** dados salvos no `report_data` (snapshot, sem nova consulta).
- **Seções:**
  - Dados básicos
  - Endereço
  - Quadro societário (accordion)
  - Sanções (CEIS/CNEP/CEPIM)
  - Análise de risco (IA)

### Monitoramento
- **Caminho:** `/monitoring`
- **Objetivo:** registrar documentos para monitoramento contínuo e visualizar mudanças recentes.
- **Seções:**
  - Estatísticas
  - Mudanças recentes
  - Tabela de monitoramento

---

## 2) Componentes principais

### `Header`
- Navegação e identidade visual.

### `LoginForm`
- Formulário de login e armazenamento de token.

### `DossierForm`
- Geração de dossiê individual.
- Checa duplicidade antes de gerar.

### `BatchProcessor`
- Geração em lote (batch) com processamento em background.

### `DossiersList`
- Histórico com link para cada dossiê.

---

## 3) Serviços de frontend (API Client)

- `services/api.ts` → Axios configurado com JWT.
- `services/auth.ts` → login/logout e user/company.
- `services/dossiers.ts` → CRUD de dossiês.
- `services/monitoring.ts` → monitoramento e stats.

---

## 4) Casos de uso atuais

### UC-01: Gerar dossiê individual
1. Usuário loga
2. Digita CPF/CNPJ
3. Sistema gera snapshot (dossiê) e salva no Supabase
4. Redireciona para `/dossier/[id]`

### UC-02: Consultar dossiê histórico
1. Usuário acessa dashboard
2. Escolhe dossiê na lista
3. Visualiza dados persistidos

### UC-03: Geração em lote
1. Usuário envia lista de documentos
2. Backend processa em background
3. Registros aparecem no histórico

### UC-04: Monitorar documentos
1. Usuário adiciona CPF/CNPJ
2. Sistema salva em `monitoring_targets`
3. Usuário pode atualizar manualmente ou em lote

### UC-05: Visualizar mudanças recentes
1. Usuário abre `/monitoring`
2. Sistema lista registros atualizados recentemente

---

## 5) Padrões de interface

- Estilo COAF com cards, badges e dados estruturados
- Accordion para QSA e detalhes extensos
- Estados de loading e erro
- Textos claros e neutros (compliance)

---

## 6) Observações atuais

- Dossiês são **snapshot persistente** e não reconsultam APIs no “ver dossiê”.
- Sanções são filtradas localmente para o documento consultado.
- Monitoramento é multi-tenant (company_id).

---

© 2026 Vinicius Matsumoto
