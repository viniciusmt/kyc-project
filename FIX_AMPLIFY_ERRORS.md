# Correção de Erros 404 e 401 no AWS Amplify

## Alterações Realizadas

### 1. Configuração do Next.js para Exportação Estática
**Arquivo**: `frontend/next.config.js`

Adicionado:
- `output: 'export'` - Gera exportação estática
- `images: { unoptimized: true }` - Necessário para export
- `trailingSlash: true` - Melhora compatibilidade com Amplify

### 2. Configuração do Amplify Build
**Arquivo**: `frontend/amplify.yml`

Alterado:
- `baseDirectory: out` (antes era `.next`)
- Removido cache de `.next/cache`

## Próximos Passos

### 1. Testar Build Localmente
```bash
cd frontend
npm run build
```

Verifique se a pasta `out` foi criada com sucesso.

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
- Verifique se o `amplify.yml` na raiz do projeto aponta para `frontend/out`
- Confirme que a build gerou a pasta `out`

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
├── out/              ← Gerado pelo Next.js (arquivos estáticos)
│   ├── index.html
│   ├── _next/
│   └── ...
├── amplify.yml       ← Configuração do Amplify (aponta para 'out')
└── next.config.js    ← Configuração do Next.js (output: 'export')
```

## Referências
- [Next.js Static Exports](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
- [AWS Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/getting-started.html)
