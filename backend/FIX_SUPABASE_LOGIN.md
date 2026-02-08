# 🔐 Como Resolver o Problema de Login no Supabase

## ❌ Problema Identificado

Seu banco Supabase está **vazio** - não tem empresas nem usuários cadastrados!

```
✅ Conexão OK
❌ 0 empresas (companies)
❌ 0 usuários (profiles)
```

---

## ✅ Solução: Criar Dados Iniciais

Você tem 3 opções:

### 🔹 Opção 1: Pelo Dashboard do Supabase (MAIS FÁCIL)

#### Passo 1: Criar uma Empresa

1. Acesse https://supabase.com/dashboard
2. Selecione seu projeto
3. Vá em **Table Editor** → `companies`
4. Clique em **Insert** → **Insert row**
5. Preencha:
   ```
   id: (deixe auto-gerar)
   name: "Minha Empresa"
   created_at: (deixe auto)
   ```
6. **Salvar**
7. **COPIE O ID** da empresa criada (UUID)

#### Passo 2: Criar um Usuário

1. Vá em **Authentication** → **Users**
2. Clique em **Add user** → **Create new user**
3. Preencha:
   ```
   Email: seu@email.com
   Password: SuaSenha123!
   ```
4. **Enviar** (pode demorar alguns segundos)
5. **COPIE O UUID DO USUÁRIO** criado

#### Passo 3: Criar um Profile

1. Volte em **Table Editor** → `profiles`
2. Clique em **Insert** → **Insert row**
3. Preencha:
   ```
   id: (COLE O UUID DO USUÁRIO do passo 2)
   company_id: (COLE O UUID DA EMPRESA do passo 1)
   role: admin
   full_name: Seu Nome Completo
   created_at: (deixe auto)
   ```
4. **Salvar**

#### Passo 4: Testar Login

Agora você pode fazer login com:
- **Email:** `seu@email.com`
- **Senha:** `SuaSenha123!`

---

### 🔹 Opção 2: Via SQL (Supabase Dashboard)

1. Acesse https://supabase.com/dashboard
2. Vá em **SQL Editor**
3. Cole e execute este SQL:

```sql
-- 1. Criar empresa
INSERT INTO companies (id, name, created_at)
VALUES (
  'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', -- Substitua por um UUID qualquer
  'Minha Empresa',
  NOW()
);

-- 2. Criar usuário (via SQL não funciona para auth.users)
-- Use a interface de Authentication > Users para criar o usuário

-- 3. Após criar o usuário no Authentication, crie o profile:
INSERT INTO profiles (id, company_id, role, full_name, created_at)
VALUES (
  'USER_UUID_AQUI', -- SUBSTITUA pelo UUID do usuário criado
  'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', -- UUID da empresa acima
  'admin',
  'Administrador',
  NOW()
);
```

**⚠️ IMPORTANTE:** Você ainda precisa criar o usuário em **Authentication > Users** manualmente!

---

### 🔹 Opção 3: Desabilitar RLS Temporariamente (AVANÇADO)

⚠️ **NÃO recomendado para produção!**

1. Vá em **SQL Editor** no Supabase
2. Execute:

```sql
-- Desabilitar RLS temporariamente
ALTER TABLE companies DISABLE ROW LEVEL SECURITY;
ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;
```

3. Execute o script Python:
```bash
cd backend
python setup_initial_data.py
```

4. **REABILITE O RLS:**
```sql
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
```

---

## 🧪 Testar se Funcionou

### Teste 1: Verificar dados no banco

```bash
cd backend
python test_supabase_connection.py
```

Deve mostrar:
```
Encontradas 1 empresa(s)
Encontrados 1 perfil(is)
```

### Teste 2: Testar login via API

1. Certifique-se que o backend está rodando:
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

2. Abra outro terminal e teste:
```bash
curl -X POST http://localhost:8000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"seu@email.com\",\"password\":\"SuaSenha123!\"}"
```

Deve retornar um token JWT!

### Teste 3: Login pelo frontend

1. Acesse: http://localhost:3000
2. Digite:
   - Email: `seu@email.com`
   - Senha: `SuaSenha123!`
3. Clicar em **Entrar**
4. Deve redirecionar para o dashboard!

---

## 📝 Estrutura Necessária no Supabase

### Tabela: `companies`
```
Colunas:
- id (uuid, PK)
- name (text)
- created_at (timestamptz)
```

### Tabela: `profiles`
```
Colunas:
- id (uuid, PK) → FK para auth.users(id)
- company_id (uuid) → FK para companies(id)
- role (text) → ex: 'admin', 'user'
- full_name (text)
- created_at (timestamptz)
```

### Authentication Users
- Criados em **Authentication > Users**
- Cada usuário precisa ter um `profile` correspondente

---

## 🎯 Resumo dos Passos

1. ✅ Criar 1 empresa na tabela `companies`
2. ✅ Criar 1 usuário em `Authentication > Users`
3. ✅ Criar 1 profile na tabela `profiles` vinculando user + company
4. ✅ Testar login

---

## 🆘 Ainda com Erro?

### Erro: "Invalid login credentials"
- ✅ Usuário foi criado em Authentication > Users?
- ✅ Email e senha estão corretos?
- ✅ Usuário foi confirmado (não está pendente)?

### Erro: "Perfil não encontrado"
- ✅ Existe um registro na tabela `profiles`?
- ✅ O `id` do profile é IGUAL ao UUID do usuário?
- ✅ O `company_id` está preenchido?

### Erro: "Usuário sem empresa vinculada"
- ✅ O `company_id` no profile aponta para uma empresa válida?
- ✅ A empresa existe na tabela `companies`?

---

## 📧 Dados de Teste Sugeridos

Use estes dados para teste:

**Empresa:**
```
name: "Empresa Teste KYC"
```

**Usuário:**
```
email: admin@teste.local
password: Admin@123456
```

**Profile:**
```
role: admin
full_name: Administrador Sistema
```

---

**💡 Dica:** Depois de criar os dados, use a **Opção 1 (Dashboard)** para verificar visualmente se tudo está criado corretamente!
