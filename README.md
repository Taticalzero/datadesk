# DataDesk · Reports App

Web app de relatórios com autenticação JWT, conexão MySQL e export CSV.  
Stack: **FastAPI + aiomysql + Jinja2 + JWT via python-jose**, gerenciado com **uv**.  
Usuários da aplicação ficam num banco **SQLite** local.

---

## Estrutura do projeto

```
reports-app/
├── main.py                  # Entry-point FastAPI
├── manage_users.py          # CLI para criar/editar/remover usuarios (SQLite)
├── pyproject.toml           # Dependências (uv)
├── .env                     # Variáveis de ambiente 
├── .env.example             # Modelo do .env
├── users.db                 # Banco SQLite de usuarios
├── app/
│   ├── auth.py              # JWT + autenticação
│   ├── users_db.py          # Acesso ao SQLite de usuarios
│   ├── database.py          # Pool aiomysql + run_query()
│   ├── reports_config.py    # ← ADICIONE SEUS RELATÓRIOS AQUI
│   └── routers/
│       ├── auth.py          # Rotas /login /logout
│       └── reports.py       # Rotas / e /report/{id}
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    └── report.html
```

---

## Instalação

```bash
# 1. Clone ou copie o projeto
cd reports-app

# 2. Instale as dependências com uv
uv sync

# 3. Copie o .env e preencha com seus dados
cp .env.example .env
```

---

## Configurar usuários (SQLite)

Os usuários ficam num banco SQLite (`users.db` por padrão; configurável via `USERS_DB_PATH` no `.env`). Use o CLI `manage_users.py` para gerenciá-los — o hash bcrypt é gerado automaticamente:

```bash
# Criar um usuario admin (a senha sera pedida de forma oculta):
uv run manage_users.py create admin --role admin

# Criar um usuario comum:
uv run manage_users.py create joao --role user

# Passando a senha direto na linha (evita o prompt):
uv run manage_users.py create admin --role admin --password minhasenha

# Atualizar a senha de um usuario:
uv run manage_users.py set-password admin

# Remover um usuario:
uv run manage_users.py delete joao

# Listar todos os usuarios cadastrados:
uv run manage_users.py list
```

A tabela é criada automaticamente na primeira execução (tanto pelo CLI quanto pelo `main.py`).

> **Migração do `USERS_JSON`:** o fluxo antigo (hash via `hash_password.py` + colar no `.env`) foi removido. Recrie cada usuário com `manage_users.py create`.

---

## Adicionar relatórios

Edite `app/reports_config.py`:

```python
REPORTS = {
    "meu_relatorio": {
        "title":       "Título do Relatório",
        "description": "Descrição breve.",
        "icon":        "📊",
        "sql": """
            SELECT coluna1, coluna2
            FROM minha_tabela
            WHERE status = 'ativo'
        """,
        "params": [],   # parâmetros fixos no SQL (%s)
    },

    # Relatório com filtro digitado pelo usuário:
    "vendas_mes": {
        "title":          "Vendas por Mês",
        "description":    "Filtro pelo mês desejado.",
        "icon":           "📅",
        "sql":            "SELECT * FROM vendas WHERE mes = %s",
        "query_param":    "mes",          # chave na URL (?mes=...)
        "param_label":    "Mês (MM/YYYY)",
        "param_placeholder": "01/2025",
    },
}
```

---

## Rodar

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: **http://localhost:8000**

---

## Fluxo de autenticação

```
POST /login (form: username + password)
    └─► consulta users.db (SQLite) e valida bcrypt
    └─► gera JWT (expira em ACCESS_TOKEN_EXPIRE_MINUTES)
    └─► salva token em cookie HttpOnly "access_token"

Todas as rotas protegidas leem o cookie e validam o JWT.
Se inválido/expirado → redirect para /login.

GET /logout → apaga o cookie → redirect /login
```

---

## Variáveis de ambiente (.env)

| Variável | Descrição |
|---|---|
| `MOCK_MODE` | Se `true`, usa dados fictícios (sem MySQL real) |
| `DB_HOST` | Host MySQL |
| `DB_PORT` | Porta (padrão 3306) |
| `DB_USER` | Usuário MySQL |
| `DB_PASSWORD` | Senha MySQL |
| `DB_NAME` | Nome do banco |
| `SECRET_KEY` | Chave secreta JWT (gere com `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `ALGORITHM` | Algoritmo JWT (padrão HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token (padrão 480 = 8h) |
| `USERS_DB_PATH` | Caminho do arquivo SQLite de usuários (padrão `users.db`) |
