[README_DJANGO.md](https://github.com/user-attachments/files/25192555/README_DJANGO.md)
# Cadastro de Pessoas (Django) 🌐👥

Este repositório é a versão **web** (com frontend) do projeto **Cadastro de Pessoas (CLI)**.

> ✅ **Importante:** este projeto em **Django é um complemento** do meu projeto em **CLI** — a ideia é manter **as mesmas opções e regras** do menu do terminal, porém com:
> - interface web
> - **persistência em banco de dados** (Django ORM)
> - exportação por download no navegador

---

## ✨ O que este projeto entrega

### Tudo que existe no CLI, agora no navegador
- **Menu de filtros**
- **Editar cadastro** (adicionar, editar por CPF, excluir)
- **Exibir estatísticas**
- **Opções de exportação** (CSV, XLSX, JSON)
- Páginas equivalentes ao menu “**O que deseja editar?**” (editar nome/sobrenome/nascimento/sexo/cpf)

### Extras do Django (além do CLI)
- Persistência real via **SQLite** (por padrão) — ou PostgreSQL/MySQL se você quiser
- **Busca** na listagem por **CPF** ou **nome/sobrenome**
- Templates com **Bootstrap 5** + visual “glass”
- Gráficos com **Chart.js** (CDN)

---

## ✅ Requisitos

- **Python 3.10+** (recomendado)
- Dependências:
  - `Django`
  - `openpyxl` (exportação XLSX)

> As dependências estão listadas em `requirements.txt`.

---

## 🚀 Como rodar

### 1) Criar e ativar venv
**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependências
```bash
pip install -r requirements.txt
```

### 3) Migrar o banco
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4) Popular com dados de exemplo (opcional)
Este comando popula o banco com a mesma ideia do `seed()` do projeto CLI:

```bash
python manage.py seed_pessoas
```

### 5) Subir o servidor
```bash
python manage.py runserver
```

Abra no navegador:
- `http://127.0.0.1:8000/`

---

## 🧠 Relação com o projeto CLI

O **CLI** é o projeto “original” no terminal: menus interativos, cadastro e exportação (em memória).  
Este **Django** é um **complemento**: replica as **mesmas opções** no frontend web, mas com banco de dados.

- CLI: dados ficam em memória durante a execução e você exporta para arquivos.
- Django: dados ficam salvos no **banco** (persistência) e as exportações viram **downloads**.


---

## 🧭 Mapa de menus e páginas (CLI → Web)

### Menu Principal (Dashboard)
- `/` → Menu principal (atalhos e resumo)

### Menus (iguais ao CLI)
- `/filtros/` → Menu de filtros
- `/cadastro/` → Editar cadastro
- `/estatisticas/` → Exibir estatísticas
- `/exportacao/` → Opções de exportação
- `/sair/` → “Sair” (página informativa)

### Cadastros (CRUD)
- `/pessoas/` → Listar todos os cadastros (+ busca)
- `/pessoas/nova/` → Adicionar mais pessoas
- `/pessoas/<id>/` → Detalhe de uma pessoa

### Buscar por CPF (replica os fluxos do CLI)
Página única que redireciona conforme o “destino”:
- `/cadastro/buscar/?destino=detalhe`
- `/cadastro/buscar/?destino=editar`
- `/cadastro/buscar/?destino=excluir`

### Edição por campo (menu “O que deseja editar?”)
- `/pessoas/<id>/editar/` → menu de edição
- `/pessoas/<id>/editar/nome/`
- `/pessoas/<id>/editar/sobrenome/`
- `/pessoas/<id>/editar/nascimento/`
- `/pessoas/<id>/editar/sexo/`
- `/pessoas/<id>/editar/cpf/`

### Filtros (equivalentes ao CLI)
- `/filtros/homens/`
- `/filtros/mulheres/`
- `/filtros/mais-velha/`
- `/filtros/mais-nova/`
- `/filtros/menores/`
- `/filtros/acima-media/`
- `/filtros/aniversariantes/` (formulário por mês)

### Estatísticas (equivalentes ao CLI)
- `/estatisticas/total/`
- `/estatisticas/sexo/`
- `/estatisticas/media-idade/`
- `/estatisticas/maiores-menores/`
- `/estatisticas/faixa-etaria/`
- `/estatisticas/maior-menor-idade/`
- `/estatisticas/aniversariantes-mes/`

### Exportação (download)
- `/exportacao/csv/`
- `/exportacao/xlsx/`
- `/exportacao/json/`

---

## 🗄️ Banco de dados

Por padrão, o Django usa **SQLite** e cria o arquivo:
- `db.sqlite3`

Isso já é “persistência de dados linkada ao banco”.

### Trocar para PostgreSQL (opcional)
No arquivo `cadastro_pessoas/settings.py`, troque o bloco `DATABASES` por algo assim:

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

Depois rode:
```bash
python manage.py migrate
```

---

## 📦 Exportação (CSV / XLSX / JSON)

No CLI os arquivos iam para a pasta **Documents** do usuário.  
No Django, ao clicar/exportar, o arquivo é gerado e baixado pelo navegador:

- CSV usa delimitador `;`
- XLSX é gerado com `openpyxl`
- JSON vem formatado (`indent=2`)

---

## 🧱 Estrutura do projeto

```
.
├─ manage.py
├─ requirements.txt
├─ cadastro_pessoas/
│  ├─ settings.py
│  ├─ urls.py
│  └─ ...
└─ pessoas/
   ├─ models.py
   ├─ views.py
   ├─ forms.py
   ├─ urls.py
   ├─ templates/pessoas/
   ├─ static/pessoas/
   └─ management/commands/seed_pessoas.py
```

---

## 🔐 Admin do Django (opcional)

Se quiser administrar registros pelo admin:

```bash
python manage.py createsuperuser
```

Depois acesse:
- `http://127.0.0.1:8000/admin/`

---


