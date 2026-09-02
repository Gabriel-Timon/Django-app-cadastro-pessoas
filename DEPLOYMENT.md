# Deploy seguro na Vercel

Este projeto usa a detecção nativa de Django da Vercel. O repositório deve permanecer conectado ao GitHub para que pushes em `main` gerem novos deployments.

## 1. Criar o projeto e o banco

1. Importe `Gabriel-Timon/Django-app-cadastro-pessoas` na Vercel.
2. Adicione uma integração PostgreSQL pelo Vercel Marketplace.
3. Crie o banco na região São Paulo (`gru1`), a mesma definida para a Function em `vercel.json`.
4. Confirme que a integração criou `DATABASE_URL` nos ambientes Production e Preview necessários.

SQLite não deve ser usado na Vercel: o filesystem das Functions é somente leitura e não fornece persistência compartilhada.

## 2. Variáveis de ambiente

Gere uma chave sem reutilizar a chave local:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Cadastre na Vercel:

```text
DJANGO_SECRET_KEY=<valor gerado>
DJANGO_DEBUG=False
DATABASE_URL=<fornecida pela integração PostgreSQL>
DJANGO_DB_SSL_REQUIRE=True
```

Os hosts `*.vercel.app` são reconhecidos no ambiente Vercel. Para domínio próprio, defina valores exatos:

```text
DJANGO_ALLOWED_HOSTS=app.exemplo.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://app.exemplo.com
```

HSTS com `includeSubDomains` e `preload` é ativado por padrão na Vercel. Antes de usar um domínio próprio na raiz, confirme que todos os seus subdomínios suportam HTTPS ou desative explicitamente essas duas opções.

## 3. Primeiro deploy e migrações

Após vincular a CLI ao projeto:

```bash
vercel link
```

Como variáveis marcadas como `Sensitive` não são reveladas novamente pela CLI, use uma chave efêmera apenas no processo administrativo local. No PowerShell:

```powershell
vercel env pull .env.local --environment=production
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$env:DJANGO_DEBUG = "False"
python manage.py migrate --noinput
python manage.py seed_demo_data
python manage.py createsuperuser
Remove-Item Env:DJANGO_SECRET_KEY
Remove-Item Env:DJANGO_DEBUG
```

O `manage.py` carrega `.env.local`, que permanece ignorado pelo Git. Execute migrações uma única vez por release, após revisar `python manage.py migrate --plan`; para migrações, prefira a conexão direta `DATABASE_URL_UNPOOLED` fornecida pelo Neon. Elas não rodam automaticamente no build para evitar concorrência entre previews e produção.

`seed_demo_data` é o único seed aprovado para produção deste portfólio. Ele é atômico e idempotente: restaura os 50 registros canônicos marcados como demo sem apagar cadastros que não pertencem à demonstração.

Depois, publique pela interface, integração Git ou CLI:

```bash
vercel deploy --prod
```

## 4. Smoke test

Verifique após cada release:

- `/` redireciona visitantes anônimos para `/accounts/login/`;
- login e logout funcionam, e logout aceita apenas POST;
- `/accounts/signup/` cria uma conta não staff com somente `pessoas.view_pessoa`;
- a conta de consulta vê os 50 registros demo, filtros e dashboards, mas recebe `403` em mutações e exportações;
- `/static/pessoas/css/styles.css` e os estáticos do admin respondem;
- respostas autenticadas possuem `Cache-Control: no-store` e CSP;
- CRUD persiste após novo acesso e novo deployment;
- usuários sem permissão recebem `403`;
- exportações exigem a permissão `pessoas.export_pessoa` e não contêm CPF completo;
- logs não exibem CPF, senha, chave secreta ou URL completa do banco.

## 5. Operação

- Em produção, execute somente `seed_demo_data`; não carregue dados pessoais reais.
- Mantenha backup e restauração habilitados no provedor PostgreSQL.
- Revise e aplique os PRs do Dependabot.
- O GitHub Actions deve permanecer verde antes de promover uma release.
- Rotacione imediatamente qualquer segredo exposto e faça redeploy.
