from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, compras, financeiro, materiais
from app.db import init_db
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (se necessário adicionar cleanup no futuro)


app = FastAPI(
    title="ERP Open - Backend",
    description="Sistema ERP modular com controle de acesso baseado em permissões",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(compras.router, prefix="/compras", tags=["compras"])
app.include_router(financeiro.router, prefix="/financeiro", tags=["financeiro"])
app.include_router(materiais.router, prefix="/materiais", tags=["materiais"])


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "ERP Open Backend",
        "version": "1.0.0",
        "modules": ["auth", "compras", "financeiro", "materiais"],
        "docs": "/docs"
    }
