# Cadastro de Pessoas (Django)

Este projeto é a versão **web (frontend)** do meu sistema de cadastro em CLI.

Ele replica **todas as opções** dos menus originais no frontend:
- Menu de filtros
- Editar cadastro (adicionar, editar por CPF, excluir)
- Exibir estatísticas
- Opções de exportação (CSV, XLSX, JSON)

## 1) Como rodar

> Requisitos: Python 3.10+ (recomendado), pip

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_pessoas   # opcional: popula com dados de exemplo
python manage.py runserver
```

Abra no navegador: `http://127.0.0.1:8000/`

## 2) Banco de dados

Por padrão o Django usa **SQLite** (`db.sqlite3`)

Se quiser Postgres, edite `cadastro_pessoas/settings.py` e troque `DATABASES`.
Exemplo (Postgres):

```python
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "cadastro",
    "USER": "postgres",
    "PASSWORD": "sua_senha",
    "HOST": "localhost",
    "PORT": "5432",
  }
}
```

## 3) Admin do Django (opcional)

Crie um superusuário:

```bash
python manage.py createsuperuser
```

Acesse: `http://127.0.0.1:8000/admin/`
