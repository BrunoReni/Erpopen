# 📋 Funcionalidades por Módulo - ERPOpen

**Versão**: 1.0.0  
**Data**: 2025-11-24

---

## 📦 MÓDULO DE COMPRAS

### 1. Fornecedores
**Rota**: `/compras/fornecedores`

#### Funcionalidades:
- ✅ **Listar Fornecedores**
  - Visualização em tabela
  - Busca por nome, razão social ou CNPJ
  - Filtro por status (ativo/inativo)
  - Paginação automática
  
- ✅ **Criar Fornecedor**
  - Formulário completo
  - Validação de CNPJ único
  - Campos: Nome, Razão Social, CNPJ, Email, Telefone, Endereço, Cidade, Estado, CEP
  
- ✅ **Editar Fornecedor**
  - Modal/Página de edição
  - Atualização de todos os campos
  - Preservação de dados relacionados
  
- ✅ **Desativar Fornecedor**
  - Soft delete (não remove do banco)
  - Confirmação antes de desativar
  - Mantém histórico de pedidos

#### APIs Disponíveis:
```
GET    /compras/fornecedores          - Listar
POST   /compras/fornecedores          - Criar
GET    /compras/fornecedores/{id}     - Buscar por ID
PUT    /compras/fornecedores/{id}     - Atualizar
DELETE /compras/fornecedores/{id}     - Desativar
```

---

### 2. Pedidos de Compra
**Rota**: `/compras/pedidos`

#### Funcionalidades:
- ✅ **Listar Pedidos**
  - Visualização em tabela
  - Busca por número ou fornecedor
  - Filtro por status
  - Badges coloridos por status
  - Ordenação por data
  
- ✅ **Criar Pedido de Compra**
  - Seleção de fornecedor
  - Adição de múltiplos itens
  - Seleção de material do catálogo
  - Ou digitação livre de descrição
  - Cálculo automático de totais
  - Definição de data de entrega
  - Campo de observações
  
- ✅ **Editar Pedido**
  - Edição de cabeçalho
  - Edição de itens
  - Atualização de fornecedor
  - Recálculo de totais
  
- ✅ **Visualizar Pedido**
  - Modal com todos os detalhes
  - Lista completa de itens
  - Totais calculados
  - Informações do fornecedor
  
- ✅ **Aprovar Pedido**
  - Mudança de status: Solicitado → Aprovado
  - Confirmação obrigatória
  - Registro de aprovação
  
- ✅ **Cancelar Pedido**
  - Mudança de status para Cancelado
  - Confirmação obrigatória
  - Não permite cancelar pedidos recebidos

#### Status de Pedido:
- 🔵 **Rascunho** - Em elaboração
- 🔵 **Solicitado** - Aguardando aprovação
- 🟢 **Aprovado** - Aprovado para envio
- 🟣 **Enviado** - Pedido enviado ao fornecedor
- 🟢 **Recebido** - Material recebido
- 🔴 **Cancelado** - Pedido cancelado

#### APIs Disponíveis:
```
GET    /compras/pedidos               - Listar
POST   /compras/pedidos               - Criar
GET    /compras/pedidos/{id}          - Buscar por ID
PUT    /compras/pedidos/{id}          - Atualizar
DELETE /compras/pedidos/{id}          - Cancelar
POST   /compras/pedidos/{id}/aprovar  - Aprovar
```

---

## 💰 MÓDULO FINANCEIRO

### 1. Contas a Pagar
**Rota**: `/financeiro/contas-pagar`

#### Funcionalidades:
- ✅ **Listar Contas a Pagar**
  - Visualização em tabela
  - Busca por descrição
  - Filtro por status
  - Filtro por fornecedor
  - Destaque para contas vencidas
  - Ordenação por vencimento
  
- ✅ **Criar Conta a Pagar**
  - Descrição da conta
  - Seleção de fornecedor
  - Seleção de centro de custo
  - Data de emissão e vencimento
  - Valor
  - Observações
  - Possibilidade de vincular a pedido de compra
  
- ✅ **Editar Conta**
  - Atualização de todos os campos
  - Não permite editar contas pagas
  
- ✅ **Baixar Pagamento**
  - Registro de data de pagamento
  - Valor pago (parcial ou total)
  - Mudança de status
  - Cálculo de juros/descontos (se aplicável)
  
- ✅ **Excluir Conta**
  - Confirmação obrigatória
  - Não permite excluir contas pagas

#### Status de Conta:
- 🔴 **Pendente** - Aguardando pagamento
- 🟡 **Parcial** - Pagamento parcial
- 🟢 **Pago** - Totalmente pago
- 🔴 **Atrasado** - Vencido e não pago

#### APIs Disponíveis:
```
GET    /financeiro/contas-pagar            - Listar
POST   /financeiro/contas-pagar            - Criar
GET    /financeiro/contas-pagar/{id}       - Buscar por ID
PUT    /financeiro/contas-pagar/{id}       - Atualizar
DELETE /financeiro/contas-pagar/{id}       - Excluir
POST   /financeiro/contas-pagar/{id}/baixar - Baixar pagamento
```

---

### 2. Contas a Receber
**Rota**: `/financeiro/contas-receber`

#### Funcionalidades:
- ✅ **Listar Contas a Receber**
  - Visualização em tabela
  - Busca por descrição ou cliente
  - Filtro por status
  - Destaque para contas vencidas
  - Ordenação por vencimento
  - Design em verde para diferenciar de contas a pagar
  
- ✅ **Criar Conta a Receber**
  - Descrição da conta
  - Nome do cliente
  - Seleção de centro de custo
  - Data de emissão e vencimento
  - Valor
  - Observações
  
- ✅ **Editar Conta**
  - Atualização de todos os campos
  - Não permite editar contas recebidas
  
- ✅ **Baixar Recebimento**
  - Registro de data de recebimento
  - Valor recebido (parcial ou total)
  - Mudança de status
  - Cálculo de juros/descontos (se aplicável)
  
- ✅ **Excluir Conta**
  - Confirmação obrigatória
  - Não permite excluir contas recebidas

#### Status de Conta:
- 🟢 **Pendente** - Aguardando recebimento
- 🟡 **Parcial** - Recebimento parcial
- 🟢 **Pago** - Totalmente recebido
- 🔴 **Atrasado** - Vencido e não recebido

#### APIs Disponíveis:
```
GET    /financeiro/contas-receber              - Listar
POST   /financeiro/contas-receber              - Criar
GET    /financeiro/contas-receber/{id}         - Buscar por ID
PUT    /financeiro/contas-receber/{id}         - Atualizar
DELETE /financeiro/contas-receber/{id}         - Excluir
POST   /financeiro/contas-receber/{id}/baixar  - Baixar recebimento
```

---

### 3. Contas Bancárias
**Rota**: `/financeiro/bancos`

#### Funcionalidades:
- ✅ **Listar Contas Bancárias**
  - Visualização em tabela
  - Card destacado com saldo total de todas as contas
  - Busca por nome ou banco
  - Visualização de saldo individual
  - Indicador visual de saldo positivo/negativo
  - Ícone de banco para cada conta
  
- ✅ **Criar Conta Bancária**
  - Nome da conta
  - Banco
  - Agência
  - Número da conta
  - Saldo inicial
  - Saldo atual (calculado automaticamente)
  
- ✅ **Editar Conta**
  - Atualização de dados cadastrais
  - Não permite editar saldos diretamente
  
- ✅ **Desativar Conta**
  - Soft delete
  - Mantém histórico de movimentações
  - Confirmação obrigatória

#### Recursos Especiais:
- 💰 **Card de Saldo Total** - Soma de todas as contas ativas
- 🎨 **Cor por Saldo** - Verde para positivo, vermelho para negativo
- 🏦 **Ícone Visual** - Cada conta tem ícone de banco

#### APIs Disponíveis:
```
GET    /financeiro/contas-bancarias       - Listar
POST   /financeiro/contas-bancarias       - Criar
GET    /financeiro/contas-bancarias/{id}  - Buscar por ID
PUT    /financeiro/contas-bancarias/{id}  - Atualizar
DELETE /financeiro/contas-bancarias/{id}  - Desativar
```

---

### 4. Centros de Custo
**Rota**: `/financeiro/centros-custo`

#### Funcionalidades:
- ✅ **Listar Centros de Custo**
  - Visualização em tabela
  - Busca por código ou nome
  - Código formatado em monospace
  
- ✅ **Criar Centro de Custo**
  - Modal de criação
  - Código único
  - Nome
  - Descrição detalhada
  
- ✅ **Editar Centro de Custo**
  - Modal de edição
  - Atualização de todos os campos
  - Validação de código único
  
- ✅ **Desativar Centro de Custo**
  - Soft delete
  - Mantém vínculos com contas
  - Confirmação obrigatória

#### Uso:
Os centros de custo são utilizados em:
- Contas a Pagar
- Contas a Receber
- Relatórios financeiros (futuro)
- Análise de custos por departamento (futuro)

#### APIs Disponíveis:
```
GET    /financeiro/centros-custo       - Listar
POST   /financeiro/centros-custo       - Criar
GET    /financeiro/centros-custo/{id}  - Buscar por ID
PUT    /financeiro/centros-custo/{id}  - Atualizar
DELETE /financeiro/centros-custo/{id}  - Desativar
```

---

## 📊 MÓDULO DE MATERIAIS

### 1. Cadastro de Materiais
**Rota**: `/materiais/produtos`

#### Funcionalidades:
- ✅ **Listar Materiais**
  - Visualização em tabela
  - Busca por código ou nome
  - Filtro por status
  - Alerta visual para estoque baixo
  - Código em negrito
  - Badge de status de estoque
  
- ✅ **Criar Material**
  - Código único
  - Nome
  - Descrição
  - Unidade de medida (UN, KG, M, L, etc)
  - Estoque mínimo
  - Estoque máximo
  - Estoque atual
  - Preço médio
  - Localização no almoxarifado
  
- ✅ **Editar Material**
  - Atualização de todos os campos cadastrais
  - Não permite editar estoque diretamente (usar movimentação)
  
- ✅ **Desativar Material**
  - Soft delete
  - Mantém histórico de movimentações
  - Confirmação obrigatória

#### Alertas e Indicadores:
- 🔴 **Estoque Crítico** - Abaixo do mínimo
- 🟡 **Estoque Baixo** - Próximo ao mínimo
- 🟢 **Estoque OK** - Entre mínimo e máximo
- 🔵 **Estoque Alto** - Acima do máximo

#### APIs Disponíveis:
```
GET    /materiais/produtos       - Listar
POST   /materiais/produtos       - Criar
GET    /materiais/produtos/{id}  - Buscar por ID
PUT    /materiais/produtos/{id}  - Atualizar
DELETE /materiais/produtos/{id}  - Desativar
```

---

### 2. Movimentação de Estoque
**Rota**: `/materiais/estoque`

#### Funcionalidades:
- ✅ **Listar Movimentações**
  - Visualização em tabela cronológica
  - Busca por material
  - Filtros por tipo de movimento
  - Botões de filtro rápido (Todos, Entradas, Saídas, Ajustes)
  - Ícones coloridos por tipo
  - Quantidade com sinal (+/-)
  - Data e hora completas
  
- ✅ **Registrar Entrada**
  - Seleção de material do catálogo
  - Visualização do estoque atual
  - Quantidade de entrada
  - Observações
  - Cálculo automático do novo estoque
  
- ✅ **Registrar Saída**
  - Seleção de material do catálogo
  - Visualização do estoque atual
  - Quantidade de saída
  - Validação de estoque disponível
  - Observações
  - Cálculo automático do novo estoque
  
- ✅ **Registrar Ajuste**
  - Para correções de inventário
  - Pode ser positivo ou negativo
  - Observação obrigatória
  
- ✅ **Registrar Transferência**
  - Entre locais do almoxarifado
  - Observações sobre destino

#### Tipos de Movimento:
- 🟢 **Entrada** - Compra, devolução, produção
- 🔴 **Saída** - Venda, consumo, requisição
- 🔵 **Ajuste** - Correção de inventário
- 🟣 **Transferência** - Entre locais

#### Recursos Especiais:
- 📊 **Resumo ao Criar** - Mostra estoque atual, mudança e novo estoque
- ✅ **Atualização Automática** - Estoque do material é atualizado automaticamente
- 🎨 **Visual por Tipo** - Ícones e cores diferentes para cada tipo

#### APIs Disponíveis:
```
GET    /materiais/movimentos       - Listar
POST   /materiais/movimentos       - Criar movimento
GET    /materiais/movimentos/{id}  - Buscar por ID
```

---

## 👥 MÓDULO DE SISTEMA / USUÁRIOS

### 1. Gestão de Usuários
**Rota**: `/users`

#### Funcionalidades:
- ✅ **Listar Usuários**
  - Visualização em tabela
  - Busca por nome ou email
  - Badges coloridos de perfis
  - Indicador de status (Ativo/Inativo)
  - Data de criação
  
- ✅ **Criar Usuário**
  - Nome completo
  - Email único
  - Senha (obrigatória na criação)
  - Seleção múltipla de perfis/roles
  - Checkbox para cada perfil disponível
  - Status ativo por padrão
  
- ✅ **Editar Usuário**
  - Atualização de nome e email
  - Senha opcional (deixar em branco = não altera)
  - Modificação de perfis
  - Alteração de status
  
- ✅ **Ativar/Desativar Usuário**
  - Botão de cadeado para alternar status
  - Não exclui do banco (soft delete)
  - Usuário inativo não pode fazer login
  - Confirmação obrigatória

#### Perfis Disponíveis:
- 👑 **admin** - Administrador (todas as permissões)
- 👔 **manager** - Gerente (operações gerais)
- 👤 **user** - Usuário básico (leitura)
- 🛒 **comprador** - Compras e materiais
- 💰 **financeiro** - Operações financeiras
- 📦 **almoxarife** - Gestão de estoque

#### Recursos Especiais:
- 🎨 **Badges de Perfis** - Cada perfil exibido como badge azul
- 🔐 **Gestão de Permissões** - Baseado em perfis
- ✅ **Seleção Múltipla** - Usuário pode ter vários perfis

#### APIs Disponíveis:
```
GET    /users           - Listar
POST   /users           - Criar
GET    /users/{id}      - Buscar por ID
PUT    /users/{id}      - Atualizar
DELETE /users/{id}      - Desativar
POST   /auth/login      - Fazer login
GET    /auth/me         - Dados do usuário logado
POST   /auth/register   - Registrar novo usuário
```

---

## 🎯 RESUMO GERAL

### Totais por Módulo:

| Módulo | Telas | Funcionalidades | APIs |
|--------|-------|-----------------|------|
| **Compras** | 2 | 15+ | 11 |
| **Financeiro** | 4 | 25+ | 20 |
| **Materiais** | 2 | 12+ | 7 |
| **Sistema** | 1 | 8+ | 6 |
| **TOTAL** | **9** | **60+** | **44** |

---

## 🔐 SISTEMA DE PERMISSÕES

Todas as funcionalidades respeitam o sistema de permissões baseado em perfis (roles).

### Estrutura de Permissões:
```
{modulo}:{acao}

Exemplos:
- compras:read
- compras:create
- compras:update
- compras:delete
- financeiro:read
- materiais:read
```

### Verificação de Acesso:
- ✅ Frontend verifica permissões antes de exibir rotas/botões
- ✅ Backend valida permissões em cada endpoint
- ✅ Usuário sem permissão não vê opções bloqueadas

---

## 📱 RECURSOS GERAIS

### Interface:
- ✅ Design responsivo (mobile, tablet, desktop)
- ✅ Tailwind CSS para estilização
- ✅ Ícones Lucide React
- ✅ Feedback visual em todas as ações
- ✅ Loading states
- ✅ Mensagens de erro amigáveis

### Funcionalidades Comuns:
- ✅ Busca em tempo real
- ✅ Filtros dinâmicos
- ✅ Confirmação de ações críticas
- ✅ Formatação de moeda (R$)
- ✅ Formatação de datas (pt-BR)
- ✅ Validação de formulários
- ✅ Paginação automática

---

**Documento gerado em**: 2025-11-24  
**Versão do Sistema**: 1.0.0
