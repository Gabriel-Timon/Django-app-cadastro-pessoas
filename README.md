# Cadastro de Pessoas

Aplicação web para cadastro e gestão de pessoas, construída com Django. O projeto transforma um fluxo originalmente executado em linha de comando em uma interface web com persistência em banco de dados, filtros, estatísticas e exportação de dados.

## Visão geral

O sistema oferece um CRUD completo de pessoas e reúne as principais operações em um dashboard responsivo:

- cadastro, consulta, edição por campo e exclusão;
- busca por nome, sobrenome ou CPF;
- filtros por sexo, idade e mês de aniversário;
- estatísticas de total, média de idade, faixas etárias e distribuição por mês;
- exportação para CSV, XLSX e JSON;
- painel administrativo do Django;
- comando de gerenciamento para popular um ambiente local com dados de demonstração.

## Tecnologias

- Python 3.10+
- Django 5.x (compatível com Django 4.2 até antes da 6.0)
- SQLite para desenvolvimento
- Bootstrap 5 e Bootstrap Icons
- openpyxl para exportação XLSX
- Testes com o framework nativo do Django

## Executando localmente

### 1. Criar e ativar o ambiente virtual

No Windows PowerShell:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

No Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
python -m pip install -r requirements.txt
```

### 3. Configurar o banco

```bash
python manage.py migrate
```

O SQLite é criado localmente como `db.sqlite3` e não é versionado. Para inserir registros fictícios e explorar a aplicação:

```bash
python manage.py seed_pessoas
```

O comando é idempotente: executar novamente não duplica registros pelo CPF.

### 4. Iniciar o servidor

```bash
python manage.py runserver
```

Acesse <http://127.0.0.1:8000/>.

## Testes e verificações

Execute a suíte automatizada com:

```bash
python manage.py test
```

Para validar a configuração do projeto:

```bash
python manage.py check
```

## Configuração por ambiente

As configurações sensíveis e específicas do ambiente podem ser definidas por variáveis de ambiente. Consulte `.env.example` como referência:

```text
DJANGO_SECRET_KEY=chave-local-de-desenvolvimento
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Em produção, use uma chave secreta exclusiva, defina `DJANGO_DEBUG=False`, configure `DJANGO_ALLOWED_HOSTS` e substitua o SQLite por um banco adequado ao ambiente.

## Painel administrativo

Para criar um usuário administrador:

```bash
python manage.py createsuperuser
```

Depois, acesse <http://127.0.0.1:8000/admin/>.

## Estrutura principal

```text
cadastro_pessoas/       # configurações e URLs do projeto Django
pessoas/                # domínio da aplicação
  management/           # comandos de gerenciamento, incluindo seed
  migrations/           # histórico versionado do schema
  templates/            # páginas HTML
  static/               # estilos da aplicação
  forms.py              # validação e normalização de entradas
  models.py             # entidade Pessoa e regras de domínio
  views.py              # CRUD, filtros, estatísticas e exportações
manage.py               # ponto de entrada dos comandos Django
```

## Próximos passos

Para evoluir o projeto em um cenário de produção, os próximos incrementos naturais são autenticação e autorização de usuários, paginação da listagem, validação completa dos dígitos verificadores do CPF, cobertura contínua em CI e configuração de um banco PostgreSQL.
