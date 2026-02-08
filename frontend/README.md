# KYC System - Frontend

Frontend da aplicação KYC (Know Your Customer) construído com Next.js 14, React, TypeScript e Tailwind CSS.

## 🚀 Tecnologias

- **Next.js 14** - Framework React com App Router
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Framework CSS utility-first
- **Axios** - Cliente HTTP com interceptors
- **SWR** - Data fetching e cache

## 📁 Estrutura de Diretórios

```
frontend/
├── src/
│   ├── app/                    # Pages (App Router)
│   │   ├── page.tsx           # Login page
│   │   ├── dashboard/         # Dashboard principal
│   │   ├── dossier/[id]/      # Página individual de dossiê
│   │   └── monitoring/        # Página de monitoramento
│   ├── components/            # Componentes reutilizáveis
│   │   ├── Header.tsx
│   │   ├── LoginForm.tsx
│   │   ├── DossierForm.tsx
│   │   ├── BatchProcessor.tsx
│   │   └── DossiersList.tsx
│   ├── services/              # Serviços de API
│   │   ├── api.ts             # Axios instance
│   │   ├── auth.ts            # Autenticação
│   │   ├── dossiers.ts        # Dossiês
│   │   └── monitoring.ts      # Monitoramento
│   └── types/                 # TypeScript types
│       └── index.ts
├── public/                    # Assets estáticos
├── tailwind.config.ts         # Configuração Tailwind
├── next.config.js             # Configuração Next.js
└── package.json
```

## 🔧 Instalação

### 1. Instalar dependências

```bash
cd frontend
npm install
```

### 2. Configurar variáveis de ambiente

Crie o arquivo `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Executar em desenvolvimento

```bash
npm run dev
```

A aplicação estará disponível em: **http://localhost:3000**

## 📦 Build para Produção

```bash
npm run build
npm start
```

## 🎯 Funcionalidades Implementadas

### ✅ Autenticação
- Login com email/senha via Supabase
- JWT Token management com localStorage
- Interceptors Axios para adicionar token automaticamente
- Redirecionamento automático em 401

### ✅ Dashboard
- Geração de dossiê individual
- Geração em lote (batch) com múltiplos documentos
- Checkbox opcional para análise com IA (Gemini)
- Verificação de duplicatas antes de gerar
- Lista de histórico de dossiês gerados

### ✅ Dossiê Individual
- Página única para cada dossiê (URL: `/dossier/{id}`)
- Visualização completa de todos os dados:
  - Dados básicos (CPF/CNPJ)
  - Endereço
  - Quadro societário (QSA)
  - PEP (Pessoa Politicamente Exposta)
  - Sanções
  - Análise de risco com IA
  - Mídia negativa
  - Recomendações

### ✅ Monitoramento
- Adicionar documentos ao monitoramento contínuo
- Lista de registros monitorados
- Estatísticas (total, CPFs, CNPJs)
- Atualização individual ou em lote
- Mudanças recentes (últimos 7 dias)
- Remover documentos do monitoramento

## 🔐 Fluxo de Autenticação

1. **Login** → POST `/api/auth/login`
2. **Recebe JWT token** → Armazena em `localStorage`
3. **Todas as requisições** → Axios interceptor adiciona `Authorization: Bearer {token}`
4. **Token inválido/expirado** → Interceptor captura 401 e redireciona para login

## 🎨 Design System

### Cores Principais (Tailwind)

```typescript
colors: {
  primary: {
    DEFAULT: '#1e3c72',  // Azul escuro COAF
    light: '#2a5298',
    dark: '#16284d',
  }
}
```

### Componentes de UI

- **Botões**: Classes base com hover states
- **Cards**: Bordas arredondadas com shadow
- **Tabelas**: Striped rows com hover
- **Formulários**: Focus ring primary
- **Badges**: Coloridos por tipo/risco

## 📡 Serviços de API

### Auth Service
```typescript
authService.login(email, password)
authService.logout()
authService.isAuthenticated()
authService.getCurrentUser()
authService.getCompanyName()
```

### Dossiers Service
```typescript
dossiersService.create({ document, enable_ai, cep? })
dossiersService.processBatch({ documents, enable_ai })
dossiersService.list(page, pageSize)
dossiersService.getById(id)
dossiersService.checkDuplicate(document)
```

### Monitoring Service
```typescript
monitoringService.add(document, notes?)
monitoringService.list(page, pageSize, docType?)
monitoringService.getStats()
monitoringService.update(document)
monitoringService.updateAll()
monitoringService.remove(document)
monitoringService.getRecentChanges(days)
```

## 🔄 Integração com Backend

O frontend consome a API FastAPI rodando em `http://localhost:8000`.

**Certifique-se de que o backend está rodando antes de iniciar o frontend:**

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 📝 TypeScript Types

Todos os tipos estão definidos em `src/types/index.ts`:

- `User` - Usuário autenticado
- `LoginRequest` / `LoginResponse`
- `Dossier` - Dossiê completo
- `MonitoringRecord` - Registro de monitoramento
- `MonitoringStats` - Estatísticas
- `MonitoringChange` - Mudanças detectadas

## 🚦 Próximos Passos

- [ ] Implementar paginação na lista de dossiês
- [ ] Adicionar filtros (CPF/CNPJ, data, risco)
- [ ] Implementar busca de dossiês
- [ ] Adicionar gráficos e dashboards
- [ ] Implementar export PDF de dossiês
- [ ] Adicionar notificações toast
- [ ] Implementar modo escuro
- [ ] Adicionar testes unitários (Jest + React Testing Library)

## 📄 Licença

Uso interno - Sistema KYC
