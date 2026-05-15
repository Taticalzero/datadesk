"""
app/auth.py
Autenticacao JWT. Usuarios sao lidos do banco SQLite (app/users_db.py).
Bcrypt usado diretamente (sem passlib) para compatibilidade com Python 3.14.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, Cookie
from dotenv import load_dotenv

from app.users_db import authenticate as _authenticate_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Valida credenciais contra o banco SQLite de usuarios."""
    return _authenticate_db(username, password)


def create_access_token(data: dict) -> str:
    payload = {**data, "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MIN)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_current_user(access_token: str = Cookie(default=None)) -> dict:
    if not access_token:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    try:
        payload = decode_token(access_token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=302, headers={"Location": "/login"})
        return {"username": username, "role": payload.get("role", "user")}
    except JWTError:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
