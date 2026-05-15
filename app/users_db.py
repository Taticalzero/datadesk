"""
app/users_db.py
Gerencia o banco SQLite de usuarios.

Tabela:
    users(id, username UNIQUE, password_hash, role, created_at)

Path do arquivo configurado via env var USERS_DB_PATH (default: users.db).
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import bcrypt
from dotenv import load_dotenv

load_dotenv()

USERS_DB_PATH = os.getenv("USERS_DB_PATH", "users.db")


def _connect() -> sqlite3.Connection:
    Path(USERS_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(USERS_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def _cursor():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_users_db() -> None:
    """Cria a tabela de usuarios se ainda nao existir."""
    with _cursor() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                role          TEXT    NOT NULL DEFAULT 'user',
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False


def get_user(username: str) -> Optional[dict]:
    """Retorna o usuario (dict) ou None se nao existir."""
    with _cursor() as conn:
        row = conn.execute(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return dict(row) if row else None


def create_user(username: str, password: str, role: str = "user") -> None:
    """Insere um novo usuario. Lanca ValueError se ja existir."""
    init_users_db()
    with _cursor() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hash_password(password), role),
            )
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Usuario '{username}' ja existe.") from e


def set_password(username: str, new_password: str) -> bool:
    """Atualiza a senha. Retorna True se o usuario existia."""
    with _cursor() as conn:
        cur = conn.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (hash_password(new_password), username),
        )
        return cur.rowcount > 0


def delete_user(username: str) -> bool:
    """Remove o usuario. Retorna True se algo foi removido."""
    with _cursor() as conn:
        cur = conn.execute("DELETE FROM users WHERE username = ?", (username,))
        return cur.rowcount > 0


def list_users() -> list[dict]:
    """Lista todos os usuarios (sem o hash da senha)."""
    with _cursor() as conn:
        rows = conn.execute(
            "SELECT username, role, created_at FROM users ORDER BY username"
        ).fetchall()
        return [dict(r) for r in rows]


def authenticate(username: str, password: str) -> Optional[dict]:
    """Valida usuario+senha. Retorna o dict do usuario ou None."""
    user = get_user(username)
    if user and verify_password(password, user["password_hash"]):
        return user
    return None
