# Módulo Financeiro - Funcionalidades Avançadas

## Visão Geral

Este documento descreve as funcionalidades avançadas implementadas no módulo financeiro do sistema ERP.

## 📋 Funcionalidades Implementadas

### 1. Conciliação Bancária com Filtros de Data

A conciliação bancária agora suporta filtros por período, permitindo visualizar apenas as movimentações dentro de um intervalo de datas específico.

#### Funcionalidades:
- Filtro por Data Inicial e Data Final
- Cálculo automático de totais para o período filtrado
- Seleção múltipla de movimentações
- Conciliação em lote
- Visualização de diferença entre saldo ERP e extrato bancário

#### Como Usar:
1. Acesse **Financeiro > Conciliação Bancária**
2. Selecione a conta bancária desejada
3. Defina o intervalo de datas (Data Inicial e Data Final)
4. Clique em **Filtrar** para visualizar as movimentações do período
5. Selecione as movimentações que constam no extrato bancário
6. Clique em **Conciliar Selecionadas**

#### Endpoint API:
```http
GET /financeiro/conciliacao/{conta_id}?data_inicio=2024-01-01&data_fim=2024-12-31
```

**Query Parameters:**
- `data_inicio` (opcional): Data inicial no formato YYYY-MM-DD
- `data_fim` (opcional): Data final no formato YYYY-MM-DD

**Resposta:**
```json
{
  "conta": {
    "id": 1,
    "nome": "Conta Corrente",
    "saldo_atual": 10000.00
  },
  "periodo": {
    "data_inicio": "2024-01-01",
    "data_fim": "2024-12-31"
  },
  "total_entradas_pendentes": 5000.00,
  "total_saidas_pendentes": 3000.00,
  "saldo_pendente": 2000.00,
  "movimentacoes": [...]
}
```

---

### 2. Interface de Parcelamento

Sistema completo para criação e gestão de contas parceladas, com visualização individual de parcelas e ações específicas.

#### Funcionalidades:
- Criação de contas parceladas (a pagar e a receber)
- Preview de parcelas antes de salvar
- Configuração de intervalo entre parcelas (dias)
- Distribuição automática de valores
- Visualização de lista de parcelas expandível
- Baixa individual de parcelas
- Reagendamento de parcelas
- Status individual por parcela

#### Como Usar - Criar Parcelamento:
1. Acesse **Financeiro > Contas a Pagar** ou **Contas a Receber**
2. Clique em **Novo Parcelamento**
3. Preencha os dados:
   - Descrição
   - Fornecedor/Cliente
   - Valor Total
   - Quantidade de Parcelas
   - Data da Primeira Parcela
   - Intervalo entre parcelas (padrão: 30 dias)
4. Visualize o preview das parcelas
5. Clique em **Criar Parcelamento**

#### Como Usar - Gerenciar Parcelas:
1. Na lista de contas, identifique contas parceladas pelo ícone e indicação (Nx)
2. Clique na seta para expandir e visualizar as parcelas
3. Para cada parcela, você pode:
   - **Baixar:** Registrar pagamento/recebimento individual
   - **Reagendar:** Alterar a data de vencimento
   - **Ver Detalhes:** Visualizar informações completas

#### Endpoints API:

**Criar Conta Parcelada:**
```http
POST /financeiro/contas-pagar/parcelada
POST /financeiro/contas-receber/parcelada
```

**Request Body:**
```json
{
  "descricao": "Compra de equipamentos",
  "fornecedor_id": 10,
  "valor_total": 12000.00,
  "quantidade_parcelas": 12,
  "data_primeira_parcela": "2024-01-15",
  "intervalo_dias": 30,
  "forma_pagamento": "boleto",
  "centro_custo_id": 5,
  "observacoes": "Parcelamento em 12x sem juros"
}
```

**Listar Parcelas:**
```http
GET /financeiro/contas-pagar/{conta_id}/parcelas
GET /financeiro/contas-receber/{conta_id}/parcelas
```

**Baixar Parcela:**
```http
POST /financeiro/contas-pagar/{conta_id}/parcelas/{parcela_id}/baixar
POST /financeiro/contas-receber/{conta_id}/parcelas/{parcela_id}/baixar
```

**Reagendar Parcela:**
```http
PUT /financeiro/contas-pagar/{conta_id}/parcelas/{parcela_id}/reagendar?nova_data=2024-02-15
```

---

### 3. Compensação de Contas (Encontro de Contas)

Funcionalidade para compensar contas a pagar com contas a receber do mesmo fornecedor/cliente, sem movimentação bancária.

#### Funcionalidades:
- Compensação entre múltiplas contas a pagar e a receber
- Cálculo automático do valor de compensação
- Baixa parcial ou total das contas envolvidas
- Registro de histórico de compensação
- Não gera movimentação bancária (compensação contábil)

#### Como Funciona:
1. O sistema identifica contas a pagar e contas a receber que podem ser compensadas
2. Calcula o valor mínimo disponível para compensação
3. Realiza baixa parcial ou total nas contas envolvidas
4. Registra a operação no histórico de compensações

#### Exemplo de Uso:
**Cenário:** Empresa tem:
- Conta a pagar: R$ 5.000 para Fornecedor A
- Conta a receber: R$ 8.000 do Fornecedor A (que também é cliente)

**Resultado da Compensação:**
- Conta a pagar: Quitada (R$ 5.000 compensados)
- Conta a receber: Saldo de R$ 3.000 (R$ 5.000 compensados)
- Nenhuma movimentação bancária gerada

#### Endpoint API:

```http
POST /financeiro/compensacao
```

**Request Body:**
```json
{
  "contas_pagar_ids": [10, 11, 12],
  "contas_receber_ids": [50, 51],
  "data_compensacao": "2024-12-09",
  "observacao": "Compensação mensal com Fornecedor A"
}
```

**Resposta:**
```json
{
  "message": "Compensação realizada com sucesso",
  "valor_compensado": 5000.00,
  "contas_pagar_afetadas": 3,
  "contas_receber_afetadas": 2
}
```

**Listar Compensações:**
```http
GET /financeiro/compensacao
```

---

### 4. Baixa Múltipla com Geração de Parcelas

Funcionalidade para baixar um título gerando múltiplas novas contas. Útil para cenários como vendas no cartão com repasse parcelado.

#### Funcionalidades:
- Baixa de conta original
- Geração automática de múltiplas novas contas
- Criação de movimentação bancária
- Registro no histórico de liquidação
- Inversão de tipo de conta (receber → pagar ou pagar → receber)

#### Exemplo de Uso:
**Cenário:** Venda de R$ 10.000 no cartão de crédito
- Operadora repassa em 10 parcelas mensais de R$ 1.000

**Processo:**
1. Sistema baixa a conta a receber de R$ 10.000
2. Cria entrada no caixa de R$ 10.000
3. Gera 10 contas a receber (repasse da operadora) de R$ 1.000 cada
4. Registra tudo no histórico de liquidação

#### Endpoint API:

```http
POST /financeiro/baixa-multipla
```

**Request Body:**
```json
{
  "conta_id": 100,
  "tipo_conta": "RECEBER",
  "parcelas_geradas": [
    {
      "valor": 1000.00,
      "vencimento": "2024-02-01",
      "descricao": "Repasse 1/10 - Operadora Cartão"
    },
    {
      "valor": 1000.00,
      "vencimento": "2024-03-01",
      "descricao": "Repasse 2/10 - Operadora Cartão"
    }
    // ... mais 8 parcelas
  ],
  "conta_bancaria_destino_id": 1,
  "observacao": "Venda parcelada no cartão - Pedido #1234"
}
```

**Resposta:**
```json
{
  "message": "Baixa múltipla realizada com sucesso",
  "conta_original_id": 100,
  "movimentacao_bancaria_id": 500,
  "contas_geradas": 10,
  "contas_geradas_ids": [201, 202, 203, ...],
  "valor_total": 10000.00
}
```

---

### 5. Histórico de Liquidação

Registro completo de todas as operações de liquidação realizadas no sistema.

#### Tipos de Operação:
- `COMPENSACAO`: Compensação entre contas
- `BAIXA_MULTIPLA`: Baixa com geração de múltiplas contas
- `BAIXA_SIMPLES`: Baixa simples de conta

#### Endpoint API:

```http
GET /financeiro/historico-liquidacao?tipo_operacao=BAIXA_MULTIPLA
```

**Query Parameters:**
- `tipo_operacao` (opcional): Filtrar por tipo de operação
- `skip`: Paginação (offset)
- `limit`: Quantidade de registros

**Resposta:**
```json
[
  {
    "id": 1,
    "tipo_operacao": "BAIXA_MULTIPLA",
    "data_operacao": "2024-12-09T10:30:00",
    "valor_total": 10000.00,
    "conta_origem_id": 100,
    "tipo_conta_origem": "RECEBER",
    "contas_geradas_ids": [201, 202, 203, ...],
    "movimentacao_bancaria_id": 500,
    "observacao": "Venda parcelada no cartão",
    "created_by": 1,
    "created_at": "2024-12-09T10:30:00"
  }
]
```

---

## 🗄️ Migrações de Banco de Dados

Para aplicar as novas tabelas ao banco de dados, execute:

```bash
psql -U seu_usuario -d nome_do_banco -f backend/migrations/add_compensacao_liquidacao.sql
```

### Tabelas Criadas:

#### compensacoes_contas
- Registro de compensações entre contas a pagar e receber
- Campos: id, data_compensacao, valor_compensado, conta_pagar_id, conta_receber_id, observacao, created_at, created_by

#### historico_liquidacao
- Histórico de operações de liquidação
- Campos: id, tipo_operacao, data_operacao, valor_total, conta_origem_id, tipo_conta_origem, contas_geradas_ids, movimentacao_bancaria_id, observacao, created_by, created_at

---

## 🔒 Permissões

Todas as funcionalidades respeitam o sistema de permissões existente:

- `financeiro:read` - Visualizar dados financeiros
- `financeiro:create` - Criar contas, parcelamentos, compensações
- `financeiro:update` - Atualizar contas, conciliar movimentações
- `financeiro:delete` - Excluir registros

---

## 🧪 Testes Manuais Sugeridos

### Teste 1: Conciliação com Filtro de Data
1. Criar movimentações bancárias em diferentes datas
2. Acessar Conciliação Bancária
3. Aplicar filtro de data
4. Verificar que apenas movimentações do período aparecem
5. Conciliar movimentações selecionadas

### Teste 2: Criar Parcelamento
1. Clicar em "Novo Parcelamento" em Contas a Pagar
2. Preencher: 10 parcelas de R$ 1.000
3. Verificar preview
4. Salvar
5. Confirmar que 10 parcelas foram criadas com valores e datas corretas
6. Expandir a conta e visualizar parcelas

### Teste 3: Compensação
1. Criar conta a pagar de R$ 5.000 para Fornecedor A
2. Criar conta a receber de R$ 8.000 do Fornecedor A
3. Realizar compensação via API ou frontend (quando implementado)
4. Verificar que:
   - Conta a pagar foi quitada
   - Conta a receber ficou com saldo de R$ 3.000
   - Compensação registrada no histórico

### Teste 4: Baixa Múltipla
1. Criar conta a receber de R$ 10.000 (venda no cartão)
2. Realizar baixa múltipla via API gerando 10 parcelas
3. Verificar que:
   - Conta original foi baixada
   - Entrada de R$ 10.000 no caixa
   - 10 novas contas criadas (repasse da operadora)
   - Histórico registrado

---

## 📝 Considerações Técnicas

### Performance
- Índices criados em campos de busca frequente
- Queries otimizadas para grandes volumes de dados
- Paginação implementada em todos os listados

### Segurança
- Validações de permissão em todos os endpoints
- Transações atômicas para operações complexas
- Rollback automático em caso de erro

### Manutenibilidade
- Código documentado com comentários
- Estrutura modular e extensível
- Schemas Pydantic para validação de dados
- Separação clara entre camadas (rotas, modelos, schemas)

---

## 🔧 Stack Técnica

### Backend
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Validação:** Pydantic
- **Banco de Dados:** PostgreSQL

### Frontend
- **Framework:** React 18
- **Linguagem:** TypeScript
- **Estilização:** TailwindCSS
- **Ícones:** lucide-react
- **HTTP Client:** Axios

---

## 📚 Referências

- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

---

## 🆘 Suporte

Para dúvidas ou problemas com as funcionalidades implementadas, consulte:
1. Esta documentação
2. Comentários no código
3. Issues no repositório do projeto

---

**Última atualização:** 09/12/2024
**Versão:** 1.0.0
