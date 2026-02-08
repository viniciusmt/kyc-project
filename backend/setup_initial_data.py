"""
Setup Initial Data - Supabase
==============================
Cria dados iniciais: empresa e usuario admin
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import uuid

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print('ERRO: Configure SUPABASE_URL e SUPABASE_KEY no .env')
    sys.exit(1)

# Dados para criar
COMPANY_NAME = "Empresa Teste"
USER_EMAIL = "admin@teste.com"
USER_PASSWORD = "senha123"  # ALTERE ISSO!

print('='*60)
print('Setup Inicial - Supabase')
print('='*60)
print()

client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # 1. Criar empresa
    print('1. Criando empresa...')
    company_data = {
        'id': str(uuid.uuid4()),
        'name': COMPANY_NAME
    }
    
    company_result = client.table('companies').insert(company_data).execute()
    company_id = company_result.data[0]['id']
    print(f'   OK: Empresa criada com ID: {company_id}')
    print()
    
    # 2. Criar usuario de autenticacao
    print('2. Criando usuario de autenticacao...')
    print(f'   Email: {USER_EMAIL}')
    print(f'   Senha: {USER_PASSWORD}')
    
    auth_result = client.auth.sign_up({
        'email': USER_EMAIL,
        'password': USER_PASSWORD
    })
    
    if not auth_result.user:
        print('   ERRO: Falha ao criar usuario')
        sys.exit(1)
    
    user_id = auth_result.user.id
    print(f'   OK: Usuario criado com ID: {user_id}')
    print()
    
    # 3. Criar profile
    print('3. Criando profile...')
    profile_data = {
        'id': user_id,
        'company_id': company_id,
        'role': 'admin',
        'full_name': 'Administrador Teste'
    }
    
    profile_result = client.table('profiles').insert(profile_data).execute()
    print(f'   OK: Profile criado')
    print()
    
    print('='*60)
    print('SUCESSO! Dados iniciais criados')
    print('='*60)
    print()
    print('CREDENCIAIS DE LOGIN:')
    print(f'  Email: {USER_EMAIL}')
    print(f'  Senha: {USER_PASSWORD}')
    print()
    print('Use essas credenciais para fazer login no sistema!')
    
except Exception as e:
    print(f'ERRO: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
