# 📚 Documentação Completa - ERP Open

## 🎯 Visão Geral

Sistema ERP modular com controle de acesso baseado em permissões (RBAC) desenvolvido com:
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: React + TypeScript + Vite + Tailwind CSS

---

## 🏗️ Módulos Implementados

### 1. **COMPRAS** (`/compras`)
Gerenciamento completo de fornecedores e pedidos de compra.

#### Funcionalidades:
- ✅ Cadastro de Fornecedores (CNPJ, contatos, endereço)
- ✅ Criação de Pedidos de Compra
- ✅ Itens do Pedido com cálculo automático
- ✅ Status do Pedido (rascunho, solicitado, aprovado, recebido, cancelado)
- ✅ Aprovação de Pedidos
- ✅ Filtros por fornecedor e status

#### Endpoints:
```
GET    /compras/fornecedores
POST   /compras/fornecedores
GET    /compras/fornecedores/{id}
PUT    /compras/fornecedores/{id}
DELETE /compras/fornecedores/{id}

GET    /compras/pedidos
POST   /compras/pedidos
GET    /compras/pedidos/{id}
PUT    /compras/pedidos/{id}
DELETE /compras/pedidos/{id}
POST   /compras/pedidos/{id}/aprovar
```

#### Permissões:
- `compras:create` - Criar pedidos e fornecedores
- `compras:read` - Visualizar pedidos e fornecedores
- `compras:update` - Atualizar e aprovar pedidos
- `compras:delete` - Cancelar pedidos
- `fornecedores:create/read/update/delete` - Gestão de fornecedores

---

### 2. **FINANCEIRO** (`/financeiro`)
Gestão financeira completa com contas a pagar e receber.

#### Funcionalidades:
- ✅ Contas Bancárias (múltiplas contas)
- ✅ Centros de Custo
- ✅ Contas a Pagar (com vínculo a fornecedores)
- ✅ Contas a Receber
- ✅ Status de Pagamento (pendente, parcial, pago, atrasado)
- ✅ Fluxo de Caixa por Período
- ✅ Cálculo automático de saldos

#### Endpoints:
```
GET  /financeiro/contas-bancarias
POST /financeiro/contas-bancarias

GET  /financeiro/centros-custo
POST /financeiro/centros-custo

GET  /financeiro/contas-pagar
POST /financeiro/contas-pagar
PUT  /financeiro/contas-pagar/{id}

GET  /financeiro/contas-receber
POST /financeiro/contas-receber
PUT  /financeiro/contas-receber/{id}

GET  /financeiro/fluxo-caixa?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD
```

#### Permissões:
- `financeiro:create` - Criar contas e lançamentos
- `financeiro:read` - Visualizar movimentações financeiras
- `financeiro:update` - Atualizar contas e pagamentos
- `financeiro:delete` - Excluir lançamentos

---

### 3. **MATERIAIS** (`/materiais`)
Controle de estoque e movimentações de materiais.

#### Funcionalidades:
- ✅ Cadastro de Materiais (código, nome, categoria)
- ✅ Categorias de Materiais
- ✅ Controle de Estoque (mínimo, máximo, atual)
- ✅ Movimentações (entrada, saída, ajuste, transferência)
- ✅ Histórico completo por material
- ✅ Alertas de Estoque Baixo
- ✅ Cálculo automático de preço médio

#### Endpoints:
```
GET    /materiais/categorias
POST   /materiais/categorias

GET    /materiais/materiais
POST   /materiais/materiais
GET    /materiais/materiais/{id}
PUT    /materiais/materiais/{id}
DELETE /materiais/materiais/{id}

GET    /materiais/movimentos
POST   /materiais/movimentos

GET    /materiais/estoque-baixo
GET    /materiais/materiais/{id}/historico
```

#### Permissões:
- `materiais:create` - Cadastrar materiais e movimentações
- `materiais:read` - Visualizar estoque
- `materiais:update` - Atualizar materiais
- `materiais:delete` - Desativar materiais

---

## 🔐 Sistema de Permissões

### Perfis Padrão:

#### 1. **Admin**
Acesso total ao sistema
- Todas as permissões

#### 2. **Manager**
Gestão operacional
- Todas exceto users/roles admin

#### 3. **Comprador**
Agente de compras
- ✅ compras:create, read, update
- ✅ fornecedores:create, read, update
- ✅ materiais:read

#### 4. **Financeiro**
Operações financeiras
- ✅ financeiro:create, read, update
- ✅ compras:read (ver pedidos)
- ✅ reports:read, export

#### 5. **Almoxarife**
Controle de estoque
- ✅ materiais:create, read, update
- ✅ compras:read
- ✅ dashboard:read

#### 6. **User**
Acesso básico
- ✅ dashboard:read
- ✅ compras:read
- ✅ materiais:read

---

## 📊 Modelos de Dados

### Compras

**Fornecedor**
```python
- id: int
- nome: str
- razao_social: str
- cnpj: str (único)
- email: str
- telefone: str
- endereco, cidade, estado, cep: str
- ativo: bool
```

**PedidoCompra**
```python
- id: int
- numero: str (único, formato: PC-YYYY-XXXXX)
- fornecedor_id: FK
- data_pedido: datetime
- data_entrega_prevista: datetime
- status: enum (rascunho|solicitado|aprovado|recebido|cancelado)
- valor_total: float
- observacoes: text
```

**ItemPedidoCompra**
```python
- id: int
- pedido_id: FK
- material_id: FK (opcional)
- descricao: str
- quantidade: float
- unidade: str
- preco_unitario: float
- preco_total: float (calculado)
```

### Financeiro

**ContaBancaria**
```python
- id: int
- nome: str
- banco, agencia, conta: str
- saldo_inicial: float
- saldo_atual: float (calculado)
- ativa: bool
```

**CentroCusto**
```python
- id: int
- codigo: str (único)
- nome: str
- descricao: text
- ativo: bool
```

**ContaPagar / ContaReceber**
```python
- id: int
- descricao: str
- fornecedor_id/cliente: FK/str
- centro_custo_id: FK
- data_emissao: datetime
- data_vencimento: datetime
- data_pagamento/recebimento: datetime
- valor_original: float
- valor_pago/recebido: float
- status: enum (pendente|parcial|pago|atrasado)
```

### Materiais

**CategoriaMaterial**
```python
- id: int
- nome: str (único)
- descricao: text
- ativa: bool
```

**Material**
```python
- id: int
- codigo: str (único)
- nome: str
- descricao: text
- categoria_id: FK
- unidade_medida: str (UN, KG, M, L...)
- estoque_minimo: float
- estoque_maximo: float
- estoque_atual: float (calculado)
- preco_medio: float (calculado)
- localizacao: str
- ativo: bool
```

**MovimentoEstoque**
```python
- id: int
- material_id: FK
- tipo_movimento: enum (entrada|saida|ajuste|transferencia)
- quantidade: float
- data_movimento: datetime
- documento: str
- observacao: text
- usuario_id: int
```

---

## 🚀 Como Usar

### 1. Iniciar Backend

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Iniciar Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Acessar

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📝 Fluxos de Trabalho

### Fluxo de Compras

1. **Cadastrar Fornecedor**
   ```
   POST /compras/fornecedores
   {
     "nome": "Fornecedor XYZ",
     "cnpj": "12.345.678/0001-90",
     "email": "contato@fornecedor.com"
   }
   ```

2. **Criar Pedido de Compra**
   ```
   POST /compras/pedidos
   {
     "fornecedor_id": 1,
     "data_entrega_prevista": "2024-12-31",
     "itens": [
       {
         "material_id": 1,
         "descricao": "Parafuso M6",
         "quantidade": 100,
         "unidade": "UN",
         "preco_unitario": 0.50
       }
     ]
   }
   ```

3. **Aprovar Pedido**
   ```
   POST /compras/pedidos/1/aprovar
   ```

4. **Receber Materiais**
   - Pedido muda para status "recebido"
   - Cria movimentação de entrada no estoque

### Fluxo Financeiro

1. **Cadastrar Conta a Pagar** (vinculada ao pedido)
   ```
   POST /financeiro/contas-pagar
   {
     "descricao": "Pagamento Pedido PC-2024-00001",
     "fornecedor_id": 1,
     "pedido_compra_id": 1,
     "data_vencimento": "2024-12-15",
     "valor_original": 50.00
   }
   ```

2. **Registrar Pagamento**
   ```
   PUT /financeiro/contas-pagar/1
   {
     "data_pagamento": "2024-12-14",
     "valor_pago": 50.00,
     "status": "pago"
   }
   ```

3. **Consultar Fluxo de Caixa**
   ```
   GET /financeiro/fluxo-caixa?data_inicio=2024-12-01&data_fim=2024-12-31
   ```

### Fluxo de Materiais

1. **Cadastrar Material**
   ```
   POST /materiais/materiais
   {
     "codigo": "MAT-001",
     "nome": "Parafuso M6",
     "categoria_id": 1,
     "unidade_medida": "UN",
     "estoque_minimo": 50,
     "estoque_maximo": 500
   }
   ```

2. **Entrada de Estoque**
   ```
   POST /materiais/movimentos
   {
     "material_id": 1,
     "tipo_movimento": "entrada",
     "quantidade": 100,
     "documento": "PC-2024-00001"
   }
   ```

3. **Consultar Estoque Baixo**
   ```
   GET /materiais/estoque-baixo
   ```

---

## 🔧 Desenvolvimento

### Adicionar Nova Funcionalidade

#### Backend:
1. Adicionar modelo em `models_modules.py`
2. Criar schema em `schemas_modules.py`
3. Criar rota em `routes/[modulo].py`
4. Registrar router em `main.py`

#### Frontend:
1. Criar componente em `modules/[modulo]/`
2. Adicionar rota em `App.tsx`
3. Adicionar no menu `Sidebar.tsx`

---

## 📄 API Completa

Acesse a documentação interativa completa em:
**http://localhost:8000/docs**

---

## ✅ Checklist de Implementação

### Backend
- [x] Módulo de Compras completo
- [x] Módulo Financeiro completo
- [x] Módulo de Materiais completo
- [x] Sistema RBAC com 6 perfis
- [x] Documentação OpenAPI
- [ ] Testes automatizados
- [ ] Migrations com Alembic

### Frontend
- [x] Tela de login moderna
- [x] Dashboard funcional
- [x] Menu dinâmico por permissões
- [ ] Módulo Compras (UI)
- [ ] Módulo Financeiro (UI)
- [ ] Módulo Materiais (UI)
- [ ] Formulários e validações
- [ ] Gráficos e relatórios

---

## 🎯 Próximos Passos

1. **Implementar UI dos Módulos** (Compras, Financeiro, Materiais)
2. **Adicionar Validações** no frontend
3. **Implementar Dashboard** com gráficos
4. **Criar Relatórios** em PDF
5. **Adicionar Testes** (backend e frontend)
6. **Migração para PostgreSQL**
7. **Deploy em produção**

---

**Status**: ✅ Backend completo e funcional | Frontend base pronto
