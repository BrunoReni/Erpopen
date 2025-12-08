# Sales Orders Module - Implementation Summary

## Overview
This implementation adds a complete Sales Orders (Pedidos de Venda) module to the ERP system, integrating with existing Cliente, Material, ContaReceber, and MovimentoEstoque modules.

## Backend Implementation

### Models (`backend/app/models_modules.py`)

#### PedidoVenda Model
- **Table**: `pedidos_venda`
- **Columns**: 16 total
  - `id`, `codigo` (auto-generated PV-0001, PV-0002, etc.)
  - `cliente_id`, `vendedor_id`
  - `data_pedido`, `data_entrega_prevista`, `data_faturamento`
  - `status` (orcamento, aprovado, faturado, cancelado)
  - `condicao_pagamento`, `observacoes`
  - `valor_produtos`, `valor_desconto`, `valor_frete`, `valor_total`
  - `created_at`, `updated_at`
- **Relationships**:
  - `cliente` → Cliente (many-to-one)
  - `itens` → ItemPedidoVenda (one-to-many, cascade delete)
  - `contas_receber` → ContaReceber (one-to-many)

#### ItemPedidoVenda Model
- **Table**: `itens_pedido_venda`
- **Columns**: 9 total
  - `id`, `pedido_id`, `material_id`
  - `quantidade`, `preco_unitario`
  - `percentual_desconto`, `valor_desconto`
  - `subtotal`, `observacao`
- **Relationships**:
  - `pedido` → PedidoVenda (many-to-one)
  - `material` → Material (many-to-one)

### Schemas (`backend/app/schemas_modules.py`)

Added Pydantic schemas for validation:
- `StatusPedidoVenda` enum
- `ItemPedidoVendaCreate`, `ItemPedidoVendaUpdate`, `ItemPedidoVendaRead`
- `PedidoVendaCreate`, `PedidoVendaUpdate`, `PedidoVendaRead`

### Helpers (`backend/app/helpers.py`)

- `gerar_codigo_pedido_venda(db)`: Generates sequential codes (PV-0001, PV-0002, etc.)

### Routes (`backend/app/routes/vendas.py`)

Added 11 new endpoints for sales orders:

#### CRUD Operations
1. `GET /vendas/pedidos` - List pedidos with filters (status, cliente_id, date range)
2. `POST /vendas/pedidos` - Create new pedido with items
3. `GET /vendas/pedidos/{id}` - Get pedido details
4. `PUT /vendas/pedidos/{id}` - Update pedido (only if status=orcamento)
5. `DELETE /vendas/pedidos/{id}` - Delete pedido (only if status=orcamento)

#### Item Management
6. `POST /vendas/pedidos/{id}/itens` - Add item to pedido
7. `PUT /vendas/pedidos/{id}/itens/{item_id}` - Update item
8. `DELETE /vendas/pedidos/{id}/itens/{item_id}` - Remove item

#### Workflow Actions
9. `POST /vendas/pedidos/{id}/aprovar` - Approve pedido (validates stock)
10. `POST /vendas/pedidos/{id}/faturar` - Invoice pedido:
    - Validates stock availability
    - Creates MovimentoEstoque (SAIDA)
    - Updates Material.estoque_atual
    - Creates ContaReceber
    - Updates status to "faturado"
    - All in a single transaction
11. `POST /vendas/pedidos/{id}/cancelar` - Cancel pedido

## Frontend Implementation

### Components

#### PedidosVendaList.tsx
Location: `frontend/src/modules/vendas/PedidosVendaList.tsx`

Features:
- Table view with columns: Código, Cliente, Data, Status, Valor Total, Ações
- Filters:
  - Search by código or cliente name
  - Filter by status (all, orcamento, aprovado, faturado, cancelado)
  - Filter by cliente_id
- Status badges with colors:
  - Orçamento: Yellow
  - Aprovado: Blue
  - Faturado: Green
  - Cancelado: Red
- Actions per status:
  - Orçamento: Ver, Editar, Aprovar, Excluir, Cancelar
  - Aprovado: Ver, Faturar, Cancelar
  - Faturado: Ver only
  - Cancelado: Ver only

#### PedidoVendaForm.tsx
Location: `frontend/src/modules/vendas/PedidoVendaForm.tsx`

Features:
- Form sections:
  1. **Dados do Pedido**: Cliente*, Data Entrega, Condição Pagamento*, Valor Frete, Observações
  2. **Adicionar Item**: Material*, Quantidade*, Preço Unitário*, Desconto %
  3. **Lista de Itens**: Table showing all added items with subtotals
  4. **Resumo**: Subtotal Produtos, Descontos, Frete, Total
- Dynamic calculations:
  - Auto-fills preco_unitario from Material.preco_venda
  - Calculates subtotal per item: (quantidade × preco) - desconto
  - Updates pedido totals in real-time
- Validation:
  - Cliente required
  - At least one item required
  - Quantity and price must be > 0

### Routes (`frontend/src/App.tsx`)

Added 4 new routes:
- `/vendas/pedidos` → PedidosVendaList (requires vendas:read)
- `/vendas/pedidos/novo` → PedidoVendaForm (requires vendas:create)
- `/vendas/pedidos/:id` → PedidoVendaForm (requires vendas:read, view mode)
- `/vendas/pedidos/:id/editar` → PedidoVendaForm (requires vendas:update)

### Updated Components
- `VendasIndex.tsx`: Enabled "Pedidos de Venda" menu item (removed disabled flag)

## Integration Points

### With Clientes Module
- PedidoVenda references Cliente.id
- Cliente model now has `pedidos_venda` relationship
- Form loads active clientes for selection

### With Materiais Module
- ItemPedidoVenda references Material.id
- Form loads active materiais with stock info
- Stock validation before approval and invoicing
- Automatic stock deduction on invoicing

### With Financeiro Module
- ContaReceber now has `pedido_venda_id` field
- Automatic ContaReceber creation on invoicing:
  - Description: "Faturamento do pedido {codigo}"
  - Cliente from pedido
  - Vencimento: current_date + cliente.dias_vencimento
  - Valor: pedido.valor_total

### With Estoque Module
- MovimentoEstoque creation on invoicing
- Type: SAIDA
- Documento: pedido.codigo
- Updates EstoquePorLocal for each item

## Status Workflow

```
ORCAMENTO → APROVADO → FATURADO
    ↓
CANCELADO
```

### Orcamento
- Initial status
- Can be edited, deleted
- Can be approved (with stock validation)
- Can be canceled

### Aprovado
- Stock has been validated
- Cannot be edited
- Can be invoiced
- Can be canceled

### Faturado
- Stock has been deducted
- ContaReceber has been created
- Cannot be edited, canceled, or deleted
- Final state

### Cancelado
- Pedido was canceled
- No financial or stock impact
- Cannot be changed
- Final state

## Testing Results

### Backend Tests
✅ Models imported successfully (16 columns PedidoVenda, 9 columns ItemPedidoVenda)
✅ Relationships verified (cliente, itens, contas_receber, pedidos_venda)
✅ Schemas validated (StatusPedidoVenda enum with 4 values)
✅ Helper function works (generates PV-0001, PV-0002, etc.)
✅ 18 routes loaded (7 clientes + 11 pedidos)

### Frontend Tests
✅ TypeScript compilation successful (0 errors)
✅ All components properly typed
✅ Routes configured correctly

### Security Tests
✅ CodeQL scan completed
✅ 0 alerts found (Python and JavaScript)

### Code Review
✅ 6 issues identified and fixed:
- Moved timedelta import to top of file
- Changed dict() to model_dump() for Pydantic v2
- Added NaN handling for parseInt
- Updated .gitignore for __pycache__

## Key Features

1. **Automatic Code Generation**: Sequential PV-0001, PV-0002, etc.
2. **Stock Validation**: Before approval and invoicing
3. **Financial Integration**: Automatic ContaReceber generation
4. **Stock Management**: Automatic deduction on invoicing
5. **Status Workflow**: Clear progression with validations
6. **Multi-item Support**: Add, edit, remove items dynamically
7. **Real-time Calculations**: Totals update as items are added
8. **Filtering**: By status, cliente, and date range
9. **Transactional Safety**: All operations in database transactions
10. **Permission-based Access**: Integrated with existing permission system

## Database Changes

New tables will be created automatically on first run via `Base.metadata.create_all()`:
- `pedidos_venda` (16 columns)
- `itens_pedido_venda` (9 columns)

Updated tables:
- `clientes`: No schema changes, only relationship added in code
- `contas_receber`: New column `pedido_venda_id` (nullable, for backward compatibility)

## Files Modified

### Backend (4 files)
- `backend/app/models_modules.py` (+67 lines)
- `backend/app/schemas_modules.py` (+86 lines)
- `backend/app/helpers.py` (+28 lines)
- `backend/app/routes/vendas.py` (+445 lines)

### Frontend (4 files)
- `frontend/src/modules/vendas/PedidosVendaList.tsx` (NEW, 413 lines)
- `frontend/src/modules/vendas/PedidoVendaForm.tsx` (NEW, 540 lines)
- `frontend/src/modules/vendas/VendasIndex.tsx` (+2 lines modified)
- `frontend/src/App.tsx` (+32 lines)

### Configuration (1 file)
- `.gitignore` (+6 lines for Python cache)

## Total Impact
- **Backend**: +626 lines of new code
- **Frontend**: +987 lines of new code
- **Total**: +1,613 lines of production code
- **Tests**: All validation tests passed
- **Security**: 0 vulnerabilities found

## Usage Instructions

### Creating a Sales Order
1. Navigate to Vendas → Pedidos de Venda
2. Click "Novo Pedido"
3. Select Cliente, fill dates, payment terms
4. Add items: Select material, quantity, price, discount
5. Review totals
6. Click "Salvar Pedido"

### Approving a Sales Order
1. Open the pedido (status: orcamento)
2. Click "Aprovar" (checkmark icon)
3. System validates stock availability
4. Status changes to "aprovado"

### Invoicing a Sales Order
1. Open the pedido (status: aprovado)
2. Click "Faturar" (document icon)
3. System:
   - Validates stock again
   - Creates stock movement (SAIDA)
   - Updates stock levels
   - Creates ContaReceber
4. Status changes to "faturado"

## Next Steps (Optional Enhancements)

1. Add PDF export for pedidos
2. Add email notification on status changes
3. Add partial invoicing support
4. Add payment installments configuration
5. Add discount rules and approval workflow
6. Add pedido duplication feature
7. Add delivery tracking
8. Add integration with nota fiscal emission
9. Add sales analytics dashboard
10. Add sales reports (by period, cliente, material, etc.)
