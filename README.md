# 🚀 ERP Open

Sistema ERP Open Source - Modular, escalável e completo para gestão empresarial.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org/)

---

## 📋 Sobre o Projeto

**ERP Open** é um sistema completo de gestão empresarial (ERP) desenvolvido com tecnologias modernas:

- 🔹 **Backend**: FastAPI (Python) + SQLAlchemy + SQLite
- 🔹 **Frontend**: React + TypeScript + Tailwind CSS + Vite
- 🔹 **Autenticação**: JWT com sistema de permissões granulares
- 🔹 **Arquitetura**: Modular e escalável

---

## ✨ Funcionalidades Implementadas

### 🔐 Sistema de Autenticação
- Login seguro com JWT
- Sistema de permissões granulares (RBAC)
- Gerenciamento de usuários e roles

### 📦 Módulo de Compras
- ✅ **Fornecedores** - Cadastro completo com código automático (FOR-XXXX)
- ✅ **Pedidos de Compra** - Gestão completa do ciclo de compras
- ⚙️ **Cotações** - Em desenvolvimento

### 💰 Módulo Financeiro
- ✅ **Contas a Pagar** - Controle de pagamentos a fornecedores
- ✅ **Contas a Receber** - Controle de recebimentos de clientes
- ✅ **Contas Bancárias** - Gestão de contas e saldos
- ✅ **Centros de Custo** - Organização contábil

### 📊 Módulo de Materiais
- ✅ **Produtos** - Cadastro de materiais com código automático
- ✅ **Movimentação de Estoque** - Entradas, saídas e transferências
- ✅ **Categorias** - Organização de produtos
- ✅ **Unidades de Medida** - 15 unidades padrão (UN, KG, L, M, etc)
- ✅ **Locais de Estoque** - Múltiplos armazéns/almoxarifados
- ✅ **Estoque por Local** - Controle de saldo por armazém

### 🤝 Módulo de Vendas (NOVO!)
- ✅ **Clientes** - Cadastro completo com código automático (CLI-XXXX)
  - CPF/CNPJ com validação
  - Tipo de pessoa (PF/PJ)
  - Endereço completo
  - Limite de crédito
  - Dias de vencimento padrão
- ⏳ **Pedidos de Venda** - Em desenvolvimento
- ⏳ **Faturamento** - Em desenvolvimento

---

## 🎯 Diferenciais

### Códigos Automáticos
Todos os cadastros geram códigos sequenciais automaticamente:
- **FOR-0001** (Fornecedores)
- **CLI-0001** (Clientes)
- **MAT-0001** (Materiais)

### Validações
- ✅ CPF e CNPJ com algoritmo verificador
- ✅ Unicidade de documentos
- ✅ Campos obrigatórios por tipo (PF/PJ)

### Estoque Multi-Local
- Controle de estoque por armazém
- Transferências entre locais
- Estoque total consolidado

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- npm ou yarn

### 1️⃣ Clone o repositório
```bash
git clone https://github.com/BrunoReni/Erpopen.git
cd Erpopen
```

### 2️⃣ Backend (FastAPI)
```bash
cd backend

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados e seed
python seed_data.py

# Executar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend rodando em**: http://localhost:8000  
**Documentação API**: http://localhost:8000/docs

### 3️⃣ Frontend (React)
```bash
cd frontend

# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev
```

**Frontend rodando em**: http://localhost:5173

---

## 🔐 Acesso Padrão

**Email**: `admin@erp.com`  
**Senha**: `admin123`

---

## 📁 Estrutura do Projeto

```
Erpopen/
├── backend/               # API FastAPI
│   ├── app/
│   │   ├── routes/       # Endpoints da API
│   │   ├── models.py     # Modelos de autenticação
│   │   ├── models_modules.py  # Modelos dos módulos
│   │   ├── schemas_modules.py # Schemas Pydantic
│   │   ├── helpers.py    # Funções auxiliares
│   │   └── db.py         # Configuração do banco
│   ├── seed_data.py      # Dados iniciais
│   └── main.py           # Aplicação principal
│
├── frontend/             # React + TypeScript
│   ├── src/
│   │   ├── modules/      # Módulos do ERP
│   │   │   ├── compras/  # Fornecedores, Pedidos
│   │   │   ├── financeiro/  # Contas, Bancos
│   │   │   ├── materiais/   # Produtos, Estoque
│   │   │   └── vendas/   # Clientes (NOVO!)
│   │   ├── components/   # Componentes reutilizáveis
│   │   └── contexts/     # Contexts (Auth, etc)
│   └── package.json
│
└── README.md
```

---

## 🗄️ Banco de Dados

**Tecnologia**: SQLite (desenvolvimento) / PostgreSQL (produção - futuro)

### Tabelas (19 no total):
- `users`, `roles`, `permissions` - Autenticação
- `fornecedores`, `pedidos_compra`, `itens_pedido_compra` - Compras
- `contas_pagar`, `contas_receber`, `contas_bancarias`, `centros_custo` - Financeiro
- `materiais`, `categorias_material`, `movimentos_estoque` - Materiais
- `unidades_medida`, `locais_estoque`, `estoque_por_local` - Estoque
- `clientes` - Vendas (NOVO!)

---

## 📊 Status do Projeto

### ✅ Completo
- [x] Sistema de autenticação (JWT + RBAC)
- [x] Módulo de Compras (Fornecedores + Pedidos)
- [x] Módulo Financeiro (Contas + Bancos + Centros Custo)
- [x] Módulo de Materiais (Produtos + Estoque)
- [x] Códigos automáticos (FOR, CLI, MAT)
- [x] Unidades de Medida (15 padrão)
- [x] Locais de Estoque (multi-armazém)
- [x] API de Clientes (CRUD completo)
- [x] Frontend de Clientes (tela completa)

### 🔨 Em Desenvolvimento (30% concluído - 7h de 30h)
- [ ] Cotações (Backend + Frontend)
- [ ] Controle de Saldo em Estoque (cálculo automático)
- [ ] API de Armazéns
- [ ] Frontend de Armazéns
- [ ] Pedidos de Venda
- [ ] Módulo de Faturamento

### 📅 Planejado
- [ ] Relatórios e Dashboards
- [ ] Notas Fiscais (integração)
- [ ] Inventário
- [ ] Produção (básico)
- [ ] Exportação de dados

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validação de dados
- **Python-Jose** - JWT
- **Passlib** - Hash de senhas
- **SQLite** - Banco de dados

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool
- **Tailwind CSS** - Estilização
- **Lucide React** - Ícones
- **Axios** - Cliente HTTP
- **React Router** - Roteamento

---

## 📝 Próximos Passos

1. **SPRINT 4**: Saldo em Estoque (3h)
2. **SPRINT 5**: Cotações Backend (4h)
3. **SPRINT 6**: Cotações Frontend (4h)
4. **SPRINT 7**: API de Armazéns (2h)
5. **SPRINT 8**: Frontend de Armazéns (3h)
6. **SPRINT 9**: Faturamento Backend (5h)
7. **SPRINT 10**: Faturamento Frontend (3h)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Bruno Reni**  
GitHub: [@BrunoReni](https://github.com/BrunoReni)

---

## 📞 Suporte

Se você tiver alguma dúvida ou sugestão, abra uma [issue](https://github.com/BrunoReni/Erpopen/issues).

---

## ⭐ Agradecimentos

Se este projeto te ajudou, considere dar uma ⭐ no repositório!

---

**Desenvolvido com ❤️ e ☕**
