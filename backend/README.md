# ERP Open - Backend (inicial)

Este diretório contém um scaffold inicial do backend para o projeto "ERP Open".

Características iniciais:
- FastAPI
- SQLModel (SQLite para desenvolvimento)
 - SQLite (SQLAlchemy para desenvolvimento)
- Autenticação JWT (registro, login, rota /auth/me)

Como rodar (local, dev):

1. Criar e ativar um ambiente virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependências:

```bash
pip install -r requirements.txt
```

3. Rodar a aplicação:

```bash
uvicorn main:app --reload
```

O banco SQLite (`dev.db`) será criado automaticamente na primeira execução.

Próximos passos:
- Implementar RBAC com tabelas Role/Permission
- Adicionar testes automatizados
- Acrescentar migrações com Alembic
- Criar frontend (React) consumindo o API

Rodando com Docker (recomendado se você não tiver Python 3.11 localmente):

```bash
# construir e subir a API (no diretório backend)
docker compose up --build

# depois acesse http://127.0.0.1:8000
```

O `Dockerfile` usa Python 3.11 para garantir compatibilidade com dependências específicas (quando necessário).
