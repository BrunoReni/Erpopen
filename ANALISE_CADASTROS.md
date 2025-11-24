# 📊 Estrutura de Cadastros - ERP Open

## Análise Completa dos Módulos

---

## 🛒 MÓDULO DE COMPRAS

### ✅ Cadastros Já Implementados (Backend)
1. **Fornecedores** ✅
   - Nome, Razão Social, CNPJ
   - Email, Telefone
   - Endereço completo
   - Status (Ativo/Inativo)

2. **Pedidos de Compra** ✅
   - Número do pedido
   - Fornecedor
   - Data do pedido
   - Data de entrega prevista
   - Status (Rascunho, Solicitado, Aprovado, etc)
   - Valor total
   - Itens do pedido

### ❌ Cadastros FALTANDO (Necessários em ERPs)

3. **Compradores/Usuários** (usa sistema de auth existente)
   - Nome
   - Email
   - Perfil/Cargo
   - Departamento
   - Limite de aprovação

4. **Aprovadores de Pedidos** ⚠️ (lógica não implementada)
   - Hierarquia de aprovação
   - Limites de valor
   - Regras de aprovação automática
   - Fluxo de aprovação (workflow)

5. **Categorias de Fornecedores** ⚠️ (não existe)
   - Tipo (Matéria-prima, Serviços, etc)
   - Classificação ABC
   - Rating/Avaliação

6. **Condições de Pagamento** ⚠️ (não existe)
   - Prazo
   - Forma de pagamento
   - Desconto por antecipação
   - Juros por atraso

7. **Cotações** ⚠️ (não existe)
   - Solicitação de cotação
   - Comparativo de preços
   - Múltiplos fornecedores
   - Histórico de cotações

---

## 💰 MÓDULO FINANCEIRO

### Subdivisão: CONTAS A PAGAR

#### ✅ Cadastros Já Implementados
1. **Contas a Pagar** ✅
   - Descrição
   - Fornecedor
   - Pedido de compra (opcional)
   - Centro de custo
   - Data emissão/vencimento/pagamento
   - Valor original/pago
   - Status (Pendente, Parcial, Pago, Atrasado)

2. **Centros de Custo** ✅
   - Código
   - Nome
   - Descrição
   - Status (Ativo/Inativo)

#### ❌ Cadastros FALTANDO

3. **Plano de Contas** ⚠️ (não existe)
   - Código contábil
   - Descrição
   - Tipo (Receita, Despesa, Ativo, Passivo)
   - Conta pai (hierarquia)

4. **Formas de Pagamento** ⚠️ (não existe)
   - Tipo (Dinheiro, Boleto, Transferência, Cartão, Cheque)
   - Taxas associadas
   - Prazos

5. **Contas Bancárias** ✅
   - Nome, Banco, Agência, Conta
   - Saldo inicial/atual
   - Status (Ativa/Inativa)

6. **Categorias de Despesas** ⚠️ (usar Centros de Custo)
   - Tipo de despesa
   - Obrigatoriedade
   - Recorrência

### Subdivisão: CONTAS A RECEBER

#### ✅ Cadastros Já Implementados
1. **Contas a Receber** ✅
   - Descrição
   - Cliente (string por enquanto)
   - Centro de custo
   - Data emissão/vencimento/recebimento
   - Valor original/recebido
   - Status

#### ❌ Cadastros FALTANDO

2. **Clientes** ⚠️ (não existe - usar string)
   - Nome/Razão Social
   - CPF/CNPJ
   - Email, Telefone
   - Endereço completo
   - Limite de crédito
   - Status

3. **Condições de Recebimento** ⚠️ (não existe)
   - Prazo
   - Forma de recebimento
   - Desconto
   - Juros

---

## 📦 MÓDULO DE MATERIAIS/ESTOQUE

### ✅ Cadastros Já Implementados
1. **Materiais** ✅
   - Código único
   - Nome, Descrição
   - Categoria
   - Unidade de medida
   - Estoque mínimo/máximo/atual
   - Preço médio
   - Localização
   - Status (Ativo/Inativo)

2. **Categorias de Material** ✅
   - Nome
   - Descrição
   - Status

3. **Movimentos de Estoque** ✅
   - Material
   - Tipo (Entrada, Saída, Ajuste, Transferência)
   - Quantidade
   - Data
   - Documento
   - Observação
   - Usuário

### ❌ Cadastros FALTANDO

4. **Locais de Armazenamento** ⚠️ (usa string no Material)
   - Depósito/Almoxarifado
   - Prédio/Andar
   - Corredor
   - Prateleira
   - Posição

5. **Unidades de Medida** ⚠️ (usa string no Material)
   - Sigla (UN, KG, M, L)
   - Descrição completa
   - Fator de conversão

---

## 🎯 PRIORIDADES DE IMPLEMENTAÇÃO

### Fase 1: ESSENCIAIS (Fazer Agora)
1. ✅ Fornecedores (já existe)
2. ✅ Materiais (já existe)
3. ✅ Pedidos de Compra (já existe)
4. ✅ Contas a Pagar (já existe)
5. ✅ Contas a Receber (já existe)
6. ✅ Centros de Custo (já existe)
7. ✅ Contas Bancárias (já existe)

### Fase 2: IMPORTANTES (Próxima iteração)
1. ❌ Clientes
2. ❌ Plano de Contas
3. ❌ Formas de Pagamento
4. ❌ Condições de Pagamento
5. ❌ Locais de Armazenamento

### Fase 3: AVANÇADAS (Futuro)
1. ❌ Cotações
2. ❌ Workflow de Aprovação
3. ❌ Categorias de Fornecedores
4. ❌ Fluxo de Caixa Projetado
5. ❌ Relatórios Analíticos

---

## 📋 PERMISSÕES NECESSÁRIAS

Para você ter acesso completo (read/write), precisa ter:

### Compras
- `compras:read`
- `compras:create`
- `compras:update`
- `compras:delete`

### Financeiro
- `financeiro:read`
- `financeiro:create`
- `financeiro:update`
- `financeiro:delete`

### Materiais
- `materiais:read`
- `materiais:create`
- `materiais:update`
- `materiais:delete`

---

## 🔧 AÇÕES IMEDIATAS

1. **Verificar permissões do usuário admin@erp.com**
2. **Implementar telas frontend para cadastros existentes:**
   - Fornecedores (Create/Read/Update/Delete)
   - Materiais (Create/Read/Update/Delete)
   - Pedidos de Compra (Create/Read/Update/Delete)
   - Contas a Pagar (Create/Read/Update/Delete)
   - Contas a Receber (Create/Read/Update/Delete)
   - Centros de Custo (Create/Read/Update/Delete)
   - Contas Bancárias (Create/Read/Update/Delete)

3. **Corrigir navegação frontend** (módulos desaparecem quando clica)

---

**Conclusão**: O backend já tem os principais cadastros implementados! O problema está no frontend que não está exibindo as telas corretamente.
