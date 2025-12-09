# Módulo Financeiro Avançado - ERP Open

## 📋 Visão Geral

Este documento descreve as funcionalidades avançadas implementadas no módulo financeiro do ERP Open, incluindo sistema de parcelas, contas recorrentes, relacionamentos obrigatórios e melhorias gerais.

---

## 🎯 Funcionalidades Implementadas

### 1. Sistema de Parcelas

#### 1.1 Modelos de Dados

**ParcelaContaPagar** e **ParcelaContaReceber**
- Cada parcela rastreia individualmente:
  - Número da parcela (ex: 3/12)
  - Data de vencimento específica
  - Valor da parcela
  - Valor pago/recebido
  - Juros e descontos aplicados
  - Status individual (pendente, pago, atrasado)

**Campos adicionados em ContaPagar/ContaReceber:**
- `tipo_parcelamento`: AVISTA, PARCELADO, RECORRENTE
- `quantidade_parcelas`: Número total de parcelas
- `dia_vencimento_fixo`: Para contas recorrentes

#### 1.2 Endpoints

**Criar conta parcelada:**
```
POST /financeiro/contas-pagar/parcelada
POST /financeiro/contas-receber/parcelada
```

Payload:
```json
{
  "descricao": "Compra de equipamento",
  "fornecedor_id": 1,
  "valor_total": 12000.00,
  "quantidade_parcelas": 12,
  "data_primeira_parcela": "2024-01-15",
  "intervalo_dias": 30,
  "forma_pagamento": "boleto",
  "numero_documento": "NF-12345"
}
```

**Listar parcelas:**
```
GET /financeiro/contas-pagar/{conta_id}/parcelas
GET /financeiro/contas-receber/{conta_id}/parcelas
```

**Baixar parcela individual:**
```
POST /financeiro/contas-pagar/{conta_id}/parcelas/{parcela_id}/baixar
POST /financeiro/contas-receber/{conta_id}/parcelas/{parcela_id}/baixar
```

Payload:
```json
{
  "valor_pago": 1000.00,
  "juros": 10.00,
  "desconto": 0.00,
  "conta_bancaria_id": 1,
  "data_pagamento": "2024-01-15"
}
```

**Reagendar parcela:**
```
PUT /financeiro/contas-pagar/{conta_id}/parcelas/{parcela_id}/reagendar?nova_data=2024-02-15
```

---

### 2. Contas Recorrentes

#### 2.1 Modelo de Dados

**ContaRecorrente**
- `tipo`: "pagar" ou "receber"
- `descricao`: Descrição da conta
- `fornecedor_id` ou `cliente_id`: Relacionamento obrigatório
- `valor`: Valor fixo mensal
- `dia_vencimento`: Dia do mês (1-28)
- `periodicidade`: mensal, trimestral, anual
- `data_inicio` / `data_fim`: Período de validade
- `ativa`: Flag para ativar/desativar
- `ultima_geracao`: Controle de geração automática

#### 2.2 Endpoints

**CRUD básico:**
```
GET    /financeiro/contas-recorrentes
POST   /financeiro/contas-recorrentes
GET    /financeiro/contas-recorrentes/{id}
PUT    /financeiro/contas-recorrentes/{id}
DELETE /financeiro/contas-recorrentes/{id}
```

**Gerar contas do mês:**
```
POST /financeiro/contas-recorrentes/gerar-mensal?mes=1&ano=2024
```

**Pausar/Ativar:**
```
POST /financeiro/contas-recorrentes/{id}/pausar
POST /financeiro/contas-recorrentes/{id}/ativar
```

#### 2.3 Exemplo de Uso

Criar despesa recorrente (aluguel):
```json
{
  "tipo": "pagar",
  "descricao": "Aluguel do galpão",
  "fornecedor_id": 5,
  "centro_custo_id": 2,
  "valor": 5000.00,
  "dia_vencimento": 10,
  "periodicidade": "mensal",
  "data_inicio": "2024-01-01"
}
```

---

### 3. Relacionamentos Obrigatórios

#### 3.1 Foreign Keys Obrigatórias

Implementadas as seguintes restrições:

**ContaPagar:**
- `fornecedor_id`: Obrigatório (nullable=False)
- Validação no schema e no modelo

**ContaReceber:**
- `cliente_id`: Obrigatório (nullable=False)
- Campo legado `cliente_nome` removido

**PedidoCompra:**
- `fornecedor_id`: Obrigatório

**ItemPedidoCompra:**
- `material_id`: Obrigatório

#### 3.2 Índices de Performance

Criados índices compostos:
```python
# ContaPagar
Index('ix_contas_pagar_fornecedor_status', 'fornecedor_id', 'status')
Index('ix_contas_pagar_vencimento', 'data_vencimento')

# ContaReceber
Index('ix_contas_receber_cliente_status', 'cliente_id', 'status')
Index('ix_contas_receber_vencimento', 'data_vencimento')
```

---

### 4. Categorias Financeiras

#### 4.1 Modelo de Dados

**CategoriaFinanceira**
- `codigo`: Código único (ex: "DESP-001")
- `nome`: Nome da categoria
- `tipo`: "receita" ou "despesa"
- `categoria_pai_id`: Para hierarquia de categorias
- `ativa`: Flag de ativação

#### 4.2 Endpoints

```
GET    /financeiro/categorias-financeiras?tipo=despesa
POST   /financeiro/categorias-financeiras
GET    /financeiro/categorias-financeiras/{id}
PUT    /financeiro/categorias-financeiras/{id}
DELETE /financeiro/categorias-financeiras/{id}
```

#### 4.3 Exemplo

Criar categoria:
```json
{
  "codigo": "DESP-001",
  "nome": "Despesas Operacionais",
  "tipo": "despesa",
  "categoria_pai_id": null
}
```

---

### 5. Formas de Pagamento

#### 5.1 Enum FormaPagamento

```python
class FormaPagamento(str, Enum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    BOLETO = "boleto"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    TRANSFERENCIA = "transferencia"
    CHEQUE = "cheque"
```

Adicionado aos modelos:
- ContaPagar
- ContaReceber

---

### 6. Validações de CPF/CNPJ

#### 6.1 Funções Utilitárias

Arquivo: `app/utils/validators.py`

```python
from app.utils.validators import validate_cpf, validate_cnpj, validate_cpf_cnpj

# Valida CPF
if validate_cpf("123.456.789-09"):
    print("CPF válido")

# Valida CNPJ
if validate_cnpj("12.345.678/0001-90"):
    print("CNPJ válido")

# Valida automaticamente
if validate_cpf_cnpj("12345678909"):
    print("Documento válido")
```

#### 6.2 Validação nos Schemas

As validações são aplicadas automaticamente ao criar/atualizar:

**Cliente:**
- Valida CPF ou CNPJ no campo `cpf_cnpj`

**Fornecedor:**
- Valida CNPJ no campo `cnpj`

---

### 7. Relatório DRE Simplificado

#### 7.1 Endpoint

```
GET /financeiro/financeiro/dre?mes=1&ano=2024
```

#### 7.2 Resposta

```json
{
  "periodo": "01/2024",
  "receitas": {
    "total": 50000.00,
    "quantidade": 25
  },
  "despesas": {
    "total": 35000.00,
    "quantidade": 18
  },
  "resultado": 15000.00,
  "resultado_percentual": 30.0
}
```

---

## 📊 Fluxos de Trabalho

### Fluxo 1: Criar Compra Parcelada

1. **Criar pedido de compra** com fornecedor
2. **Criar conta a pagar parcelada**:
   ```
   POST /financeiro/contas-pagar/parcelada
   ```
3. Sistema cria automaticamente:
   - Conta a pagar principal
   - 12 parcelas com vencimentos distribuídos
4. **Baixar parcelas individualmente** conforme pagamento
5. Sistema atualiza automaticamente:
   - Status da parcela
   - Status da conta principal
   - Saldo da conta bancária

### Fluxo 2: Configurar Despesas Recorrentes

1. **Criar contas recorrentes**:
   - Aluguel
   - Salários
   - Energia, água, internet
2. **No início do mês**, executar:
   ```
   POST /contas-recorrentes/gerar-mensal?mes=1&ano=2024
   ```
3. Sistema gera automaticamente todas as contas do mês
4. Contas aparecem no contas a pagar para baixa

### Fluxo 3: Análise Financeira

1. **Categorizar todas as contas**:
   - Atribuir `categoria_id` nas contas
2. **Gerar DRE mensal**:
   ```
   GET /financeiro/dre?mes=1&ano=2024
   ```
3. Analisar receitas vs despesas
4. Identificar categorias com maior impacto

---

## 🔒 Segurança e Integridade

### Validações Implementadas

1. **Foreign Keys obrigatórias**: Garante integridade referencial
2. **Validação de CPF/CNPJ**: Impede documentos inválidos
3. **Status de parcelas**: Controla ciclo de vida
4. **Índices compostos**: Otimiza consultas frequentes

### Constraints de Banco

- ON DELETE RESTRICT: Impede exclusão de entidades com relacionamentos
- Unique constraints em códigos
- Not null em campos obrigatórios

---

## 🚀 Próximos Passos

### Melhorias Futuras Sugeridas

1. **Migração de Banco de Dados**
   - Criar migration Alembic para aplicar todas as mudanças
   - Script de migração de dados existentes

2. **Funcionalidades Adicionais**
   - Simulação de parcelamento (preview)
   - Cancelamento de parcelas
   - Adição de parcelas extras
   - Relatório de parcelas por período
   - Histórico detalhado de geração de recorrentes

3. **Integrações**
   - Integração com APIs bancárias
   - Geração automática de boletos
   - Notificações de vencimento
   - Dashboard de análise financeira

4. **Auditoria**
   - Log de todas as operações financeiras
   - Rastreamento de alterações
   - Relatório de auditoria

---

## 📝 Notas de Migração

### Para Dados Existentes

Se você tem dados existentes no sistema:

1. **Backup do banco de dados** antes de aplicar mudanças
2. **Relacionamentos obrigatórios**:
   - Verificar se todas as contas têm fornecedor/cliente
   - Completar dados faltantes antes de aplicar constraint
3. **Campo cliente_nome**:
   - Migrar para relacionamento com cliente_id
   - Criar clientes se necessário

### Script de Exemplo

```python
# Migrar contas_receber sem cliente_id
contas = session.query(ContaReceber).filter(
    ContaReceber.cliente_id == None,
    ContaReceber.cliente_nome != None
).all()

for conta in contas:
    # Buscar ou criar cliente
    cliente = session.query(Cliente).filter(
        Cliente.nome == conta.cliente_nome
    ).first()
    
    if not cliente:
        cliente = Cliente(nome=conta.cliente_nome)
        session.add(cliente)
        session.flush()
    
    conta.cliente_id = cliente.id

session.commit()
```

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação da API
2. Verifique os exemplos de uso
3. Entre em contato com a equipe de desenvolvimento

---

**Versão:** 1.0  
**Data:** Dezembro 2024  
**Status:** Implementado
