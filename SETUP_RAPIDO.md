# 🚀 Setup Rápido - Sistema KYC

## ✅ Status das APIs Externas

**Todas as APIs estão funcionando!**

- ✅ **BrasilAPI** - Consulta CNPJ (gratuita, sem limite)
- ✅ **ViaCEP** - Consulta CEP (gratuita, sem limite)
- ✅ **Portal da Transparência** - Sanções CEIS/CNEP/CEPIM (gratuita, precisa de API key)

---

## 📋 Pré-requisitos

1. Conta no Supabase: https://supabase.com
2. API Key do Portal da Transparência (já configurada no `.env`)
3. Python 3.13+ instalado
4. Node.js 18+ instalado

---

## 🔧 Configuração do Supabase

### Passo 1: Executar Script SQL

1. Acesse: https://supabase.com/dashboard/project/hfjuotgjxchuspcfgnkv/sql
2. Copie todo o conteúdo de `setup_database.sql`
3. Cole no SQL Editor e execute (Run)

Isso criará:
- ✅ Tabela `companies` (empresas)
- ✅ Tabela `profiles` (perfis de usuários)
- ✅ Tabela `dossiers` (dossiês KYC)
- ✅ Tabela `monitoring_targets` (monitoramento contínuo)
- ✅ RLS (Row Level Security) configurado
- ✅ Índices de performance

### Passo 2: Criar Usuário de Teste

1. Vá em: **Authentication** → **Users** → **Add User**
2. Preencha:
   - Email: `seu-email@exemplo.com`
   - Password: `senha-forte-123`
   - Email Confirm: ✅ (marcar)

3. Anote o **User ID** gerado (UUID)

### Passo 3: Vincular Usuário à Empresa

Execute este SQL (substituindo `<USER_ID>` pelo ID do passo 2):

```sql
-- Vincular usuário à empresa demo
INSERT INTO public.profiles (id, company_id, full_name, role)
VALUES (
  '<USER_ID>',  -- Cole o User ID aqui
  '00000000-0000-0000-0000-000000000001',
  'Admin Demo',
  'admin'
);
```

### Passo 4: Atualizar .env (Opcional)

Se quiser, obtenha o JWT Secret:
1. Vá em **Settings** → **API** → **JWT Secret**
2. Copie e cole em `.env`:

```env
SUPABASE_JWT_SECRET=seu-jwt-secret-aqui
```

---

## 🎯 Iniciar Sistema

### Backend
```bash
cd C:\Users\Vinicius\Projetos\KYC\backend
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd C:\Users\Vinicius\Projetos\KYC\frontend
npm run dev
```

---

## 🔐 Fazer Login

1. Acesse: http://localhost:3000
2. Use as credenciais criadas no Passo 2:
   - Email: `seu-email@exemplo.com`
   - Senha: `senha-forte-123`

---

## 🧪 Testar APIs

Execute o script de teste:

```bash
cd C:\Users\Vinicius\Projetos\KYC
python test_apis.py
```

Resultado esperado:
```
[1] Testando BrasilAPI (CNPJ)...
OK - BrasilAPI funcionando!
   Razao Social: GOOGLE BRASIL INTERNET LTDA.
   CNPJ: 06990590000123
   Situacao: ATIVA

[2] Testando ViaCEP...
OK - ViaCEP funcionando!

[3] Testando Portal da Transparencia (Sancoes)...
OK - Portal da Transparencia funcionando!

[4] Testando Consulta KYC Completa...
OK - Consulta KYC completa funcionando!
```

---

## 📊 Funcionalidades Disponíveis

Após login você terá acesso a:

1. **Dashboard** - Visão geral
2. **Dossiês** - Gerar dossiês de CPF/CNPJ
   - Consulta dados cadastrais (CNPJ via BrasilAPI)
   - Consulta sanções (Portal da Transparência)
   - Análise de risco automática
   - Fluxo de aprovação/reprovação
3. **Monitoramento** - Monitoramento contínuo
   - Adicionar CPF/CNPJ para monitorar
   - Atualização periódica
   - Alertas de mudanças

---

## 🐛 Troubleshooting

### Erro: "document_type column not found"
- Execute o script `setup_database.sql` no Supabase

### Erro: "Invalid login credentials"
- Verifique se criou o usuário no Supabase Auth
- Verifique se executou o INSERT em `profiles`

### Erro: "No module named 'supabase'"
- Backend: `cd backend && pip install -r requirements.txt`

### Erro: "Cannot find module"
- Frontend: `cd frontend && npm install`

---

## 📞 Suporte

Projeto desenvolvido por **Vinicius Matsumoto**

URLs:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Supabase: https://supabase.com/dashboard/project/hfjuotgjxchuspcfgnkv
