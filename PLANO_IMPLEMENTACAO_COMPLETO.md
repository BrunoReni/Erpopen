# 🎯 PLANO DE IMPLEMENTAÇÃO COMPLETO

**Data**: 2025-11-24  
**Objetivo**: Completar módulos faltantes críticos

---

## 📋 MÓDULOS A IMPLEMENTAR

### 1️⃣ COTAÇÕES (Backend + Frontend)
**Status**: ❌ NÃO EXISTE

#### Backend:
- [ ] Modelo: `Cotacao` (com itens)
- [ ] Modelo: `ItemCotacao`
- [ ] Schemas Pydantic
- [ ] Rotas API CRUD
- [ ] Lógica: Comparar cotações

#### Frontend:
- [ ] Lista de Cotações
- [ ] Formulário de Nova Cotação
- [ ] Adicionar múltiplos fornecedores por item
- [ ] Comparativo de preços
- [ ] Gerar Pedido de Compra a partir da cotação

**Campos**:
```python
Cotacao:
  - numero
  - data_cotacao
  - data_validade
  - material_id
  - quantidade
  - observacoes
  - status (pendente, aprovado, vencido)
  
ItemCotacao:
  - cotacao_id
  - fornecedor_id
  - preco_unitario
  - prazo_entrega
  - condicoes_pagamento
  - vencedor (bool)
```

---

### 2️⃣ CADASTRO DE CLIENTES (Frontend)
**Status**: ⚠️ Backend OK, Frontend FALTA

#### Backend:
- [x] Modelo existe
- [x] Schemas existem
- [ ] **Rotas API CRUD** ← FAZER

#### Frontend:
- [ ] Lista de Clientes
- [ ] Formulário Criar/Editar Cliente
- [ ] Busca/Filtros
- [ ] Integração com Contas a Receber

---

### 3️⃣ CÓDIGOS AUTOMÁTICOS
**Status**: ❌ NÃO IMPLEMENTADO

#### Fornecedor:
- [ ] Adicionar campo `codigo` (ex: FOR-0001)
- [ ] Geração automática sequencial
- [ ] Unique constraint

#### Cliente:
- [ ] Adicionar campo `codigo` (ex: CLI-0001)
- [ ] Geração automática sequencial
- [ ] Unique constraint

#### Implementação:
```python
def gerar_codigo_fornecedor(db):
    ultimo = db.query(Fornecedor).order_by(Fornecedor.id.desc()).first()
    if ultimo and ultimo.codigo:
        num = int(ultimo.codigo.split('-')[1]) + 1
    else:
        num = 1
    return f"FOR-{num:04d}"
```

---

### 4️⃣ MÓDULO DE FATURAMENTO
**Status**: ❌ NÃO EXISTE

#### O que é:
Sistema para gerar Notas Fiscais e vincular com Pedidos de Venda

#### Backend:
- [ ] Modelo: `Faturamento` ou `NotaFiscal`
- [ ] Relacionamento: Pedido Venda → Faturamento → Conta Receber
- [ ] Campos: número NF, série, data emissão, valor total
- [ ] Lógica: Baixar estoque ao faturar
- [ ] Lógica: Gerar conta a receber automaticamente

#### Frontend:
- [ ] Botão "Faturar" no Pedido de Venda
- [ ] Modal de confirmação de faturamento
- [ ] Visualizar nota fiscal gerada
- [ ] Lista de faturamentos

**Fluxo**:
```
Pedido Venda (aprovado) 
    ↓
[Botão Faturar]
    ↓
Gera Faturamento/NF
    ↓
Baixa Estoque Automático
    ↓
Gera Conta a Receber
    ↓
Status: Faturado
```

---

### 5️⃣ CONTROLE DE ARMAZÉNS
**Status**: ⚠️ Backend OK, Frontend FALTA

#### Backend:
- [x] Modelo `LocalEstoque` existe
- [x] Modelo `EstoquePorLocal` existe
- [ ] **Rotas API CRUD** ← FAZER

#### Frontend:
- [ ] CRUD de Locais de Estoque
- [ ] Visualizar estoque por local na tela de Material
- [ ] Movimentação entre locais (transferência)
- [ ] Dashboard de estoque por armazém

---

### 6️⃣ SALDO EM ESTOQUE
**Status**: ⚠️ PARCIALMENTE IMPLEMENTADO

#### Melhorias Necessárias:

##### Backend:
- [ ] Função: Calcular estoque total (soma de todos os locais)
- [ ] Função: Atualizar estoque ao criar movimentação
- [ ] Validação: Não permitir venda sem estoque
- [ ] API: Endpoint para consultar estoque disponível

##### Frontend:
- [ ] Indicador visual de estoque na lista de materiais
- [ ] Card de resumo: Estoque total / Por local
- [ ] Alerta de estoque baixo (vermelho/amarelo/verde)
- [ ] Gráfico de estoque por local

**Cálculo**:
```python
def atualizar_estoque_material(material_id, db):
    total = db.query(
        func.sum(EstoquePorLocal.quantidade)
    ).filter(
        EstoquePorLocal.material_id == material_id
    ).scalar() or 0.0
    
    material = db.query(Material).get(material_id)
    material.estoque_atual = total
    db.commit()
```

---

## 🎯 PRIORIZAÇÃO

### 🔴 CRÍTICO (Fazer Agora):

1. **Códigos Automáticos** (1-2h)
   - Essencial para organização
   - Impacto: Alto
   - Esforço: Baixo

2. **API de Clientes** (2h)
   - Bloqueando frontend de clientes
   - Impacto: Alto
   - Esforço: Médio

3. **Frontend de Clientes** (3-4h)
   - Necessário para vendas
   - Impacto: Alto
   - Esforço: Médio

4. **Saldo em Estoque** (2-3h)
   - Crítico para operação
   - Impacto: Alto
   - Esforço: Médio

### 🟡 IMPORTANTE (Esta Semana):

5. **Cotações Completas** (6-8h)
   - Melhora processo de compras
   - Impacto: Médio/Alto
   - Esforço: Alto

6. **API de Locais de Estoque** (2h)
   - Backend pronto, falta API
   - Impacto: Médio
   - Esforço: Baixo

7. **Frontend de Armazéns** (4h)
   - Controle multi-local
   - Impacto: Médio
   - Esforço: Médio

### 🟢 DESEJÁVEL (Próxima Semana):

8. **Módulo de Faturamento** (8-12h)
   - Complexo mas importante
   - Impacto: Alto
   - Esforço: Alto

---

## 📊 ORDEM DE IMPLEMENTAÇÃO RECOMENDADA

### DIA 1 (4-6h):
1. ✅ Códigos automáticos (Fornecedor + Cliente)
2. ✅ API CRUD de Clientes
3. ✅ Frontend de Clientes (Lista + Form)

### DIA 2 (4-6h):
4. ✅ Saldo em Estoque (cálculo + atualização)
5. ✅ API de Locais de Estoque
6. ✅ Frontend básico de Armazéns

### DIA 3 (6-8h):
7. ✅ Cotações Backend (Models + API)
8. ✅ Cotações Frontend (Lista + Form básico)

### DIA 4 (4-6h):
9. ✅ Cotações Frontend (Comparativo)
10. ✅ Melhorias visuais estoque

### DIA 5+ (Opcional):
11. ⏳ Módulo de Faturamento completo

---

## 🚀 VAMOS COMEÇAR?

**Proposta**: Implementar na ordem acima, começando por:

### FASE 2A - CÓDIGOS + CLIENTES (4-6h):
1. Adicionar códigos automáticos
2. Criar rotas API de Clientes
3. Criar telas frontend de Clientes

**Posso começar agora?**

Ou você prefere que eu implemente tudo de uma vez em outra ordem?

