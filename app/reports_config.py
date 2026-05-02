"""
app/reports_config.py
Configuracao dos relatorios.
Em MOCK_MODE=true os dados sao gerados por app/mock_data.py automaticamente.
Quando voce tiver o banco real, so trocar as SQLs - nada mais muda.
"""

REPORTS: dict[str, dict] = {

    "clientes_ativos": {
        "title":       "Clientes Ativos",
        "description": "Lista completa de clientes cadastrados com status ativo.",
        "icon":        "👥",
        "sql": """
            SELECT id, nome, email, cidade, estado, telefone, cadastro
            FROM clientes
            WHERE status = 'ativo'
            ORDER BY nome
        """,
        "params": [],
    },

    "vendas_por_periodo": {
        "title":       "Vendas por Periodo",
        "description": "Detalhe de todas as vendas no mes informado (formato YYYY-MM).",
        "icon":        "📅",
        "sql": """
            SELECT produto, categoria, cliente, cidade,
                   quantidade, valor_unit, valor_total, data_venda
            FROM vendas v
            WHERE DATE_FORMAT(v.data_venda, '%%Y-%%m') = %s
            ORDER BY data_venda DESC
        """,
        "params":            [],
        "query_param":       "mes",
        "param_label":       "Mes (YYYY-MM)",
        "param_placeholder": "2024-03",
    },

    "ranking_produtos": {
        "title":       "Ranking de Produtos",
        "description": "Produtos ordenados por receita total gerada.",
        "icon":        "🏆",
        "sql": """
            SELECT p.nome AS produto, p.categoria,
                   SUM(v.quantidade) AS qtd_total,
                   SUM(v.valor_total) AS receita_total,
                   COUNT(*) AS pedidos
            FROM vendas v
            JOIN produtos p ON p.id = v.produto_id
            GROUP BY p.nome, p.categoria
            ORDER BY receita_total DESC
        """,
        "params": [],
    },

    "vendas_por_cidade": {
        "title":       "Vendas por Cidade",
        "description": "Receita e numero de pedidos agrupados por cidade do cliente.",
        "icon":        "🗺️",
        "sql": """
            SELECT c.cidade,
                   COUNT(*) AS pedidos,
                   SUM(v.valor_total) AS receita,
                   COUNT(DISTINCT v.cliente_id) AS clientes_unicos
            FROM vendas v
            JOIN clientes c ON c.id = v.cliente_id
            GROUP BY c.cidade
            ORDER BY receita DESC
        """,
        "params": [],
    },

    "estoque_baixo": {
        "title":       "Estoque Critico",
        "description": "Produtos com quantidade em estoque abaixo do minimo.",
        "icon":        "⚠️",
        "sql": """
            SELECT id, nome, categoria, preco_unit, estoque, alerta
            FROM produtos
            WHERE estoque < 50
            ORDER BY estoque ASC
        """,
        "params": [],
    },

    "inadimplentes": {
        "title":       "Clientes Inadimplentes",
        "description": "Clientes com parcelas em atraso ordenados por dias de atraso.",
        "icon":        "🔴",
        "sql": """
            SELECT c.id, c.nome, c.email, c.cidade,
                   p.dias_atraso, p.valor_devido, p.vencimento
            FROM parcelas p
            JOIN clientes c ON c.id = p.cliente_id
            WHERE p.status = 'inadimplente'
            ORDER BY p.dias_atraso DESC
        """,
        "params": [],
    },
}
