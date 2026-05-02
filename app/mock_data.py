"""
app/mock_data.py
Dados ficticios para MOCK_MODE=true.
Detecta qual relatorio esta sendo consultado pelo conteudo da SQL
e retorna um dataset coerente com aquele relatorio.
"""
import re
import random
from datetime import date, timedelta

# ── helpers ────────────────────────────────────────────────────────────────────

def _rand_date(start="2023-01-01", end="2024-12-31") -> str:
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    return (s + timedelta(days=random.randint(0, (e - s).days))).strftime("%d/%m/%Y")

def _detect(sql: str, *keywords: str) -> bool:
    sql_lower = sql.lower()
    return any(k in sql_lower for k in keywords)

# ── datasets ───────────────────────────────────────────────────────────────────

CLIENTES = [
    {"id": i, "nome": n, "email": f"{n.split()[0].lower()}@email.com",
     "cidade": c, "estado": e, "telefone": f"(85) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
     "status": "ativo", "cadastro": _rand_date()}
    for i, (n, c, e) in enumerate([
        ("Ana Lima",        "Fortaleza",    "CE"),
        ("Bruno Soares",    "São Paulo",    "SP"),
        ("Carla Mendes",    "Recife",       "PE"),
        ("Diego Ferreira",  "Curitiba",     "PR"),
        ("Erika Nunes",     "Salvador",     "BA"),
        ("Felipe Castro",   "Belo Horizonte","MG"),
        ("Gabriela Rocha",  "Manaus",       "AM"),
        ("Henrique Alves",  "Porto Alegre", "RS"),
        ("Isabela Martins", "Brasília",     "DF"),
        ("João Cardoso",    "Fortaleza",    "CE"),
        ("Karen Oliveira",  "Natal",        "RN"),
        ("Lucas Pereira",   "Florianópolis","SC"),
        ("Mariana Silva",   "Rio de Janeiro","RJ"),
        ("Nicolas Batista", "Goiânia",      "GO"),
        ("Paula Ribeiro",   "Belém",        "PA"),
        ("Rafael Costa",    "Maceió",       "AL"),
        ("Sandra Teixeira", "São Luís",     "MA"),
        ("Thiago Gomes",    "Teresina",     "PI"),
        ("Ursula Lemos",    "João Pessoa",  "PB"),
        ("Vinícius Araújo", "Fortaleza",    "CE"),
    ], start=1001)
]

PRODUTOS = [
    {"id": p, "nome": n, "categoria": c, "preco_unit": v, "estoque": random.randint(5, 200)}
    for p, (n, c, v) in enumerate([
        ("Notebook Pro 15",     "Informática",   4299.90),
        ("Mouse Ergonômico",    "Informática",    189.90),
        ("Teclado Mecânico",    "Informática",    349.00),
        ("Monitor 27\" 4K",     "Informática",   2199.00),
        ("Cadeira Gamer",       "Móveis",        1589.00),
        ("Headset Bluetooth",   "Áudio",          299.90),
        ("Webcam Full HD",      "Informática",    219.00),
        ("Hub USB-C 7 portas",  "Informática",    129.90),
        ("SSD 1TB NVMe",        "Informática",    459.00),
        ("Impressora Laser",    "Informática",    899.00),
        ("Mesa de Escritório",  "Móveis",         749.00),
        ("Luminária LED",       "Utilidades",      89.90),
    ], start=1)
]

_MESES = ["2024-01","2024-02","2024-03","2024-04","2024-05","2024-06",
          "2024-07","2024-08","2024-09","2024-10","2024-11","2024-12"]

def _vendas_rows(mes_filtro: str | None = None):
    rows = []
    for i in range(80):
        mes = mes_filtro or random.choice(_MESES)
        prod = random.choice(PRODUTOS)
        cli  = random.choice(CLIENTES)
        qtd  = random.randint(1, 5)
        rows.append({
            "id":           1000 + i,
            "produto":      prod["nome"],
            "categoria":    prod["categoria"],
            "cliente":      cli["nome"],
            "cidade":       cli["cidade"],
            "quantidade":   qtd,
            "valor_unit":   prod["preco_unit"],
            "valor_total":  round(prod["preco_unit"] * qtd, 2),
            "mes":          mes,
            "data_venda":   f"{mes}-{random.randint(1,28):02d}",
        })
    if mes_filtro:
        rows = [r for r in rows if r["mes"] == mes_filtro]
    return rows

def _inadimplentes():
    rows = []
    for i, cli in enumerate(random.sample(CLIENTES, 7)):
        rows.append({
            "id":           cli["id"],
            "nome":         cli["nome"],
            "email":        cli["email"],
            "cidade":       cli["cidade"],
            "dias_atraso":  random.randint(5, 180),
            "valor_devido": round(random.uniform(150, 8000), 2),
            "vencimento":   _rand_date("2024-01-01", "2024-06-30"),
        })
    return sorted(rows, key=lambda r: r["dias_atraso"], reverse=True)

def _estoque_baixo():
    return [
        {**p, "alerta": "⚠ Crítico" if p["estoque"] < 20 else "Baixo"}
        for p in sorted(PRODUTOS, key=lambda x: x["estoque"])
        if p["estoque"] < 50
    ]

def _resumo_vendas_produto():
    resumo: dict[str, dict] = {}
    for v in _vendas_rows():
        k = v["produto"]
        if k not in resumo:
            resumo[k] = {"produto": k, "categoria": v["categoria"],
                         "qtd_total": 0, "receita_total": 0.0, "pedidos": 0}
        resumo[k]["qtd_total"]    += v["quantidade"]
        resumo[k]["receita_total"] = round(resumo[k]["receita_total"] + v["valor_total"], 2)
        resumo[k]["pedidos"]      += 1
    return sorted(resumo.values(), key=lambda r: r["receita_total"], reverse=True)

def _resumo_por_cidade():
    resumo: dict[str, dict] = {}
    for v in _vendas_rows():
        k = v["cidade"]
        if k not in resumo:
            resumo[k] = {"cidade": k, "pedidos": 0, "receita": 0.0, "clientes_unicos": set()}
        resumo[k]["pedidos"]  += 1
        resumo[k]["receita"]   = round(resumo[k]["receita"] + v["valor_total"], 2)
        resumo[k]["clientes_unicos"].add(v["cliente"])
    result = []
    for r in resumo.values():
        result.append({**r, "clientes_unicos": len(r["clientes_unicos"])})
    return sorted(result, key=lambda r: r["receita"], reverse=True)

# ── router principal ────────────────────────────────────────────────────────────

def get_mock_result(sql: str, params: tuple = ()) -> tuple[list[dict], list[str]]:
    """Detecta o tipo de query pela SQL e devolve dados ficticios."""
    random.seed(42)  # resultado sempre igual para mesma query

    # ── clientes ─────────────────────────────
    if _detect(sql, "from clientes", "clientes where"):
        rows = CLIENTES
        cols = list(rows[0].keys()) if rows else []
        return rows, cols

    # ── vendas com filtro de mes ──────────────
    if _detect(sql, "from vendas", "data_venda") and params:
        mes = params[0] if params else None
        rows = _vendas_rows(mes_filtro=mes)
        cols = list(rows[0].keys()) if rows else []
        return rows, cols

    # ── vendas sem filtro ─────────────────────
    if _detect(sql, "from vendas", "vendas v"):
        rows = _vendas_rows()
        cols = list(rows[0].keys()) if rows else []
        return rows, cols

    # ── produtos / estoque ────────────────────
    if _detect(sql, "from produtos", "estoque"):
        if _detect(sql, "estoque <", "estoque baixo", "alerta"):
            rows = _estoque_baixo()
        else:
            rows = PRODUTOS
        cols = list(rows[0].keys()) if rows else []
        return rows, cols

    # ── resumo por produto ────────────────────
    if _detect(sql, "sum(", "group by p.nome", "group by produto"):
        rows = _resumo_vendas_produto()
        cols = list(rows[0].keys()) if rows else []
        return rows, cols

    # ── resumo por cidade ─────────────────────
    if _detect(sql, "cidade", "group by cidade", "group by v.cidade"):
        rows = _resumo_por_cidade()
        cols = list(rows[0].keys()) if rows else []
        return rows, cols

    # ── inadimplentes ─────────────────────────
    if _detect(sql, "inadimp", "atraso", "vencimento"):
        rows = _inadimplentes()
        cols = list(rows[0].keys()) if rows else []
        return rows, cols

    # ── fallback generico ─────────────────────
    rows = [
        {"id": 1, "descricao": "Dado mock generico A", "valor": 100.0, "data": "01/01/2024"},
        {"id": 2, "descricao": "Dado mock generico B", "valor": 250.0, "data": "15/03/2024"},
        {"id": 3, "descricao": "Dado mock generico C", "valor": 430.0, "data": "22/06/2024"},
    ]
    return rows, list(rows[0].keys())
