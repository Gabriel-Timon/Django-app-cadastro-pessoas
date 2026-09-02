# Cadastro de Pessoas

[![CI](https://github.com/Gabriel-Timon/Django-app-cadastro-pessoas/actions/workflows/ci.yml/badge.svg)](https://github.com/Gabriel-Timon/Django-app-cadastro-pessoas/actions/workflows/ci.yml)
[![Vercel](https://img.shields.io/badge/demo-Vercel-black?logo=vercel)](https://django-app-cadastro-pessoas.vercel.app/accounts/login/)

Aplicação web de gestão de pessoas construída com Django. O projeto demonstra CRUD, filtros, estatísticas e exportação de dados em uma interface responsiva, com controles de acesso e configuração pronta para execução serverless na Vercel.

**Aplicação em produção:** <https://django-app-cadastro-pessoas.vercel.app/>. Qualquer visitante pode criar uma conta de consulta sem privilégios.

> Projeto educacional de portfólio. Use somente dados sintéticos; não cadastre informações pessoais reais.

## Funcionalidades

- cadastro, consulta, edição por campo e exclusão;
- auto cadastro de contas somente leitura para demonstração pública;
- 50 pessoas sintéticas, balanceadas entre os dois gêneros suportados e todas as faixas etárias do dashboard;
- busca protegida por CPF e pesquisa por nome ou sobrenome;
- filtros por sexo, idade e mês de aniversário;
- estatísticas e gráficos por faixa etária, sexo e aniversário;
- exportação autorizada para CSV, XLSX e JSON;
- painel administrativo do Django;
- interface responsiva com Bootstrap 5.

## Segurança

- autenticação obrigatória em todas as páginas de dados;
- signup com privilégio mínimo: somente `view_pessoa`, sem acesso administrativo, mutações ou exportações;
- leitores enxergam exclusivamente registros marcados tecnicamente como demonstração;
- rate limiting distribuído no PostgreSQL e honeypot no cadastro de contas;
- permissões separadas para visualizar, cadastrar, alterar, excluir e exportar;
- CPF validado e mascarado em páginas, admin, mensagens e exportações;
- proteção contra formula injection em CSV e XLSX;
- CSRF, cookies `Secure`, HSTS, redirecionamento HTTPS e proxy seguro em produção;
- CSP, SRI para dependências do CDN, proteção contra iframe e bloqueio de cache de PII;
- chave secreta e banco obrigatórios no ambiente Vercel;
- dependências fixadas, auditadas e atualizadas pelo Dependabot;
- CI com testes, auditoria de vulnerabilidades, migrações, estáticos e `check --deploy`.

Consulte [SECURITY.md](SECURITY.md) para a política de segurança e privacidade do projeto.

## Tecnologias

- Python 3.13
- Django 5.2.17 LTS
- PostgreSQL em produção e SQLite somente no desenvolvimento
- Bootstrap 5, Bootstrap Icons e Chart.js
- openpyxl para exportação XLSX
- GitHub Actions e Dependabot
- Vercel Python Functions com detecção nativa de Django

## Executando localmente

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py createsuperuser
python manage.py runserver
```

No Linux ou macOS, ative o ambiente com `source .venv/bin/activate`. A aplicação estará em <http://127.0.0.1:8000/> e redirecionará para a página de login.

As configurações locais podem ser copiadas de `.env.example` para `.env`. Arquivos `.env`, `.env.local`, bancos SQLite e a pasta `.vercel` não são versionados.

## Testes e qualidade

```bash
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
python manage.py check --deploy
python -m pip check
python -m pip_audit --requirement requirements.txt
```

A suíte roda sobre PostgreSQL no CI e cobre regras do modelo, CPF, signup, rate limiting, privilégio mínimo, isolamento dos 50 IDs demo canônicos, seed idempotente, CRUD, filtros, estatísticas, headers de segurança, mascaramento e exportações.

## Deploy na Vercel

A Vercel detecta `manage.py` e `cadastro_pessoas.wsgi.application` automaticamente. Não são necessárias rotas `/api`; o `vercel.json` define somente a região `gru1` para manter a Function próxima ao PostgreSQL em São Paulo.

O deploy de produção usa PostgreSQL serverless Neon no plano gratuito. Os previews recebem branches isoladas do banco por meio da integração gerenciada.

O ambiente de produção exige:

```text
DJANGO_SECRET_KEY=<chave longa e aleatória>
DJANGO_DEBUG=False
DATABASE_URL=<PostgreSQL gerenciado com TLS>
DJANGO_DB_SSL_REQUIRE=True
```

Para domínio próprio, configure também `DJANGO_ALLOWED_HOSTS` e `DJANGO_CSRF_TRUSTED_ORIGINS` com os hosts e origens exatos. Migrações são executadas como uma etapa controlada de release, nunca em cada cold start ou requisição.

O procedimento operacional completo está em [DEPLOYMENT.md](DEPLOYMENT.md).

## Rotas principais

| Área | Rotas |
| --- | --- |
| Login | `/accounts/login/` |
| Criar conta de consulta | `/accounts/signup/` |
| Dashboard | `/` |
| Cadastros | `/pessoas/`, `/pessoas/nova/`, `/pessoas/<id>/` |
| Busca protegida | `/cadastro/buscar/` |
| Filtros | `/filtros/` |
| Estatísticas | `/estatisticas/` |
| Exportações | `/exportacao/` |
| Administração | `/admin/` |

## Estrutura

```text
cadastro_pessoas/       # settings, URLs e entrypoints WSGI/ASGI
pessoas/                # domínio, views, forms, templates e estáticos
  migrations/           # evolução versionada do schema
  management/commands/  # geração idempotente dos dados fictícios
  static/               # CSS e JavaScript próprios
  templates/            # interface e página de login
.github/                # CI e atualizações automatizadas
manage.py               # comandos administrativos do Django
requirements.txt        # dependências reproduzíveis
```

## Próximas evoluções

Para uso além de portfólio: verificação de e-mail, MFA e rate limiting no login, trilha de auditoria, criptografia de CPF com índice HMAC, paginação, política formal de retenção e restauração periódica de backup.
