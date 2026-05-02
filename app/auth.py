"""
app/auth.py
Autenticacao JWT. Usa bcrypt diretamente (sem passlib) para compatibilidade
com Python 3.14.
"""
import os, json, bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Cookie
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY   = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM    = os.getenv("ALGORITHM", "HS256")
EXPIRE_MIN   = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))


def _load_users() -> list[dict]:
    try:
        return json.loads(os.getenv("USERS_JSON", "[]"))
    except Exception:
        return []


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def authenticate_user(username: str, password: str) -> Optional[dict]:
    for user in _load_users():
        if user["username"] == username and verify_password(password, user["password_hash"]):
            return user
    return None


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
