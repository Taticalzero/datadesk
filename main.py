"""
reports-app · main.py
Ponto de entrada da aplicação FastAPI.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.database import init_pool, close_pool
from app.users_db import init_users_db
from app.routers import auth, reports

# Garante que a pasta static existe (necessário para StaticFiles)
Path("static").mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_users_db()
    await init_pool()
    yield
    await close_pool()


app = FastAPI(title="Reports App", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(reports.router)
