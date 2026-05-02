"""
app/database.py
Gerencia o pool de conexoes aiomysql.
Se MOCK_MODE=true no .env, usa dados ficticios sem precisar de banco.
"""
import os
import aiomysql
from dotenv import load_dotenv
from app.mock_data import get_mock_result

load_dotenv()

MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

_pool: aiomysql.Pool | None = None


async def init_pool():
    if MOCK_MODE:
        print("  MOCK_MODE ativado - nenhuma conexao MySQL sera feita.")
        return
    global _pool
    _pool = await aiomysql.create_pool(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        charset="utf8mb4",
        autocommit=True,
        minsize=1,
        maxsize=10,
    )


async def close_pool():
    if _pool:
        _pool.close()
        await _pool.wait_closed()


async def get_pool() -> aiomysql.Pool:
    return _pool


async def run_query(sql: str, params: tuple = ()) -> tuple[list[dict], list[str]]:
    """Executa uma query e retorna (rows_as_dicts, column_names).
    Em MOCK_MODE, retorna dados ficticios baseados na SQL."""
    if MOCK_MODE:
        return get_mock_result(sql, params)

    async with _pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql, params)
            rows = await cur.fetchall()
            columns = [d[0] for d in cur.description] if cur.description else []
            return [dict(r) for r in rows], columns
