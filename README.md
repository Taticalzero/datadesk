# DataDesk · Reports App

Web app de relatórios com autenticação JWT, conexão MySQL e export CSV.  
Stack: **FastAPI + aiomysql + Jinja2 + JWT via python-jose**, gerenciado com **uv**.

---

## Estrutura do projeto

```
reports-app/
├── main.py                  # Entry-point FastAPI
├── pyproject.toml           # Dependências (uv)
├── .env                     # Variáveis de ambiente (NÃO commitar)
├── .env.example             # Modelo do .env
├── hash_password.py         # Helper para gerar hash de senha
├── app/
│   ├── auth.py              # JWT + verificação de usuário
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

## Configurar usuários

```bash
# Gera o hash bcrypt da senha
uv run hash_password.py

# Cole o resultado no .env em USERS_JSON:
USERS_JSON=[{"username":"admin","password_hash":"$2b$12$...","role":"admin"}]

# Para múltiplos usuários:
USERS_JSON=[
  {"username":"admin","password_hash":"$2b$12$...","role":"admin"},
  {"username":"joao","password_hash":"$2b$12$...","role":"user"}
]
```

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
    └─► autentica via USERS_JSON no .env
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
| `DB_HOST` | Host MySQL |
| `DB_PORT` | Porta (padrão 3306) |
| `DB_USER` | Usuário MySQL |
| `DB_PASSWORD` | Senha MySQL |
| `DB_NAME` | Nome do banco |
| `SECRET_KEY` | Chave secreta JWT (gere com `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `ALGORITHM` | Algoritmo JWT (padrão HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token (padrão 480 = 8h) |
| `USERS_JSON` | Lista de usuários em JSON |
