# ERP Open

Sistema ERP modular com controle de acesso baseado em permissões (RBAC).

## 📋 Estrutura do Projeto

```
Erpopen/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── core/    # Configurações
│   │   ├── routes/  # Rotas da API
│   │   ├── models.py # Modelos SQLAlchemy
│   │   ├── schemas.py # Schemas Pydantic
│   │   ├── crud.py  # Operações de banco
│   │   ├── security.py # JWT & Passwords
│   │   ├── dependencies.py # Middleware de permissões
│   │   └── db.py    # Database setup
│   ├── main.py      # Entry point
│   └── requirements.txt
│
└── frontend/         # React + TypeScript frontend
    ├── src/
    │   ├── components/  # Componentes React
    │   ├── contexts/    # React Contexts
    │   ├── services/    # API services
    │   ├── types/       # TypeScript types
    │   └── modules/     # Módulos do ERP
    └── package.json
```

## 🚀 Como Rodar

### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
uvicorn main:app --reload
```

Backend: http://localhost:8000
Docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Rodar em desenvolvimento
npm run dev
```

Frontend: http://localhost:5173

## 🔐 Sistema de Permissões (RBAC)

O sistema implementa controle de acesso baseado em:

- **Roles (Perfis)**: admin, manager, user
- **Permissions (Permissões)**: `module:action` (ex: `users:read`, `products:create`)

### Permissões por Módulo

- **dashboard**: read
- **users**: create, read, update, delete
- **roles**: create, read, update, delete
- **products**: create, read, update, delete
- **customers**: create, read, update, delete
- **sales**: create, read, update, delete
- **inventory**: create, read, update, delete
- **reports**: read, export

### Perfis Padrão

**Admin**: Acesso total a tudo
**Manager**: Acesso operacional (sem gerenciar usuários/roles)
**User**: Acesso básico de leitura

## 📦 Tecnologias

### Backend
- FastAPI
- SQLAlchemy
- JWT Authentication
- Pydantic V2
- Python 3.11+

### Frontend
- React 18
- TypeScript
- Vite
- React Router
- Axios
- Zustand
- Tailwind CSS
- Lucide React (icons)

## 🔧 Desenvolvimento

### Adicionar Novo Módulo

#### Backend:
1. Criar rotas em `backend/app/routes/[module].py`
2. Adicionar permissões em `crud.init_default_permissions_and_roles()`
3. Registrar router em `main.py`

#### Frontend:
1. Criar componentes em `frontend/src/modules/[module]/`
2. Adicionar rotas em `App.tsx`
3. Adicionar item no menu em `Sidebar.tsx`
4. Usar `<ProtectedRoute>` com permissões necessárias

## 📝 Próximos Passos

- [ ] Implementar módulo de Usuários completo
- [ ] Implementar módulo de Produtos
- [ ] Implementar módulo de Clientes
- [ ] Implementar módulo de Vendas
- [ ] Implementar módulo de Inventário
- [ ] Implementar módulo de Relatórios
- [ ] Adicionar testes automatizados
- [ ] Implementar migrações com Alembic
- [ ] Deploy em produção

## 📄 Licença

MIT
