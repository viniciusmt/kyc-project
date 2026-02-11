# Correção de Erros 404 e 401 no AWS Amplify

## Alterações Realizadas

### 1. Configuração do Next.js para SSR (Standalone)
**Arquivo**: `frontend/next.config.js`

Ajustado para:
- `output: 'standalone'` - Build otimizado para SSR no Amplify
- `trailingSlash: true` - Melhora compatibilidade com Amplify

**Importante**: Não usamos `output: 'export'` porque temos rotas dinâmicas (`/dossier/[id]`) que precisam de SSR.

### 2. Configuração do Amplify Build
**Arquivo**: `frontend/amplify.yml` e buildSpec no console

Mantido:
- `baseDirectory: .next` - Pasta padrão do Next.js
- Cache de `node_modules` e `.next/cache`

## Próximos Passos

### 1. Testar Build Localmente
```bash
cd frontend
npm run build
```

Verifique se a pasta `.next` foi criada com sucesso.

### 2. Configurar Variável de Ambiente no AWS Amplify

No Console do AWS Amplify:
1. Acesse sua aplicação
2. Vá em **App settings** → **Environment variables**
3. Adicione:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://8sjfki7vgc.us-east-2.awsapprunner.com`

### 3. Fazer Commit e Push
```bash
git add frontend/next.config.js frontend/amplify.yml
git commit -m "fix: Configurar Next.js para exportação estática no Amplify"
git push origin main
```

### 4. Verificar Deploy no Amplify
- O build será executado automaticamente
- Aguarde a conclusão
- Acesse: https://main.d1pcg3lkjfaxct.amplifyapp.com

## Solução de Problemas

### Erro 404 Persiste
- Verifique se o buildSpec aponta para `frontend/.next`
- Confirme que a build gerou a pasta `.next`
- Verifique se o Amplify está usando plataforma WEB com SSR

### Erro 401 Persiste
1. **Variável de Ambiente**: Confirme que `NEXT_PUBLIC_API_URL` está configurada
2. **CORS no Backend**: Já configurado em `backend/app/core/config.py` (linha 20)
3. **Token JWT**: Faça logout e login novamente

### Verificar CORS no Backend
O backend já aceita requisições de:
- http://localhost:3000
- http://localhost:8000
- https://main.d1pcg3lkjfaxct.amplifyapp.com

Se mudou o domínio do Amplify, atualize a variável `CORS_ORIGINS` no App Runner.

## Estrutura de Build

```
frontend/
├── .next/            ← Gerado pelo Next.js (SSR)
│   ├── standalone/
│   ├── static/
│   └── ...
├── amplify.yml       ← Configuração do Amplify (aponta para '.next')
└── next.config.js    ← Configuração do Next.js (output: 'standalone')
```

## Referências
- [Next.js Static Exports](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
- [AWS Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/getting-started.html)
