# API Endpoints - Módulo Financeiro Avançado

## Base URL
```
http://localhost:8000/financeiro
```

## Autenticação
Todos os endpoints requerem autenticação via Bearer Token:
```
Authorization: Bearer {token}
```

---

## 📍 Conciliação Bancária

### Listar Movimentações Pendentes (com filtro de data)
```http
GET /financeiro/conciliacao/{conta_id}
```

**Query Parameters:**
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| data_inicio | string | Não | Data inicial (YYYY-MM-DD) |
| data_fim | string | Não | Data final (YYYY-MM-DD) |

**Exemplo:**
```bash
curl -X GET "http://localhost:8000/financeiro/conciliacao/1?data_inicio=2024-01-01&data_fim=2024-12-31" \
  -H "Authorization: Bearer {token}"
```

**Resposta (200 OK):**
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

### Conciliar Movimentações
```http
POST /financeiro/conciliacao/{conta_id}/conciliar
```

**Request Body:**
```json
[1, 2, 3, 4, 5]
```

**Resposta (200 OK):**
```json
{
  "message": "5 movimentações conciliadas com sucesso",
  "movimentacoes_conciliadas": 5
}
```

---

## 📍 Parcelamento

### Criar Conta Parcelada (A Pagar)
```http
POST /financeiro/contas-pagar/parcelada
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
  "numero_documento": "NF-12345",
  "observacoes": "Parcelamento em 12x sem juros"
}
```

**Resposta (200 OK):**
```json
{
  "id": 100,
  "descricao": "Compra de equipamentos",
  "valor_original": 12000.00,
  "tipo_parcelamento": "parcelado",
  "quantidade_parcelas": 12,
  "status": "pendente",
  ...
}
```

### Criar Conta Parcelada (A Receber)
```http
POST /financeiro/contas-receber/parcelada
```

**Request Body:** (mesma estrutura, substituindo `fornecedor_id` por `cliente_id`)

### Listar Parcelas de Conta a Pagar
```http
GET /financeiro/contas-pagar/{conta_id}/parcelas
```

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "numero_parcela": 1,
    "total_parcelas": 12,
    "data_vencimento": "2024-01-15T00:00:00",
    "valor": 1000.00,
    "valor_pago": 0.00,
    "status": "pendente",
    "juros": 0.00,
    "desconto": 0.00
  },
  ...
]
```

### Listar Parcelas de Conta a Receber
```http
GET /financeiro/contas-receber/{conta_id}/parcelas
```

### Baixar Parcela (A Pagar)
```http
POST /financeiro/contas-pagar/{conta_id}/parcelas/{parcela_id}/baixar
```

**Request Body:**
```json
{
  "conta_bancaria_id": 1,
  "valor_pago": 1000.00,
  "data_pagamento": "2024-01-15T10:30:00",
  "juros": 0.00,
  "desconto": 0.00,
  "observacoes": "Pagamento em dia"
}
```

### Baixar Parcela (A Receber)
```http
POST /financeiro/contas-receber/{conta_id}/parcelas/{parcela_id}/baixar
```

**Request Body:** (mesma estrutura, substituindo `valor_pago` por `valor_recebido`)

### Reagendar Parcela
```http
PUT /financeiro/contas-pagar/{conta_id}/parcelas/{parcela_id}/reagendar?nova_data=2024-02-15
PUT /financeiro/contas-receber/{conta_id}/parcelas/{parcela_id}/reagendar?nova_data=2024-02-15
```

**Query Parameters:**
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| nova_data | string | Sim | Nova data de vencimento (YYYY-MM-DD) |

**Resposta (200 OK):**
```json
{
  "message": "Parcela reagendada com sucesso",
  "parcela_id": 1
}
```

---

## 📍 Compensação de Contas

### Realizar Compensação
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

**Resposta (200 OK):**
```json
{
  "message": "Compensação realizada com sucesso",
  "valor_compensado": 5000.00,
  "contas_pagar_afetadas": 3,
  "contas_receber_afetadas": 2
}
```

**Erros:**
- `400 Bad Request`: Contas não informadas ou sem valor para compensação
- `404 Not Found`: Alguma conta não encontrada
- `500 Internal Server Error`: Erro ao processar compensação

### Listar Compensações
```http
GET /financeiro/compensacao
```

**Query Parameters:**
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| skip | integer | Não | Offset para paginação (padrão: 0) |
| limit | integer | Não | Limite de registros (padrão: 100) |

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "data_compensacao": "2024-12-09",
    "valor_compensado": 5000.00,
    "conta_pagar_id": 10,
    "conta_receber_id": 50,
    "observacao": "Compensação mensal",
    "created_at": "2024-12-09T10:30:00",
    "created_by": 1
  },
  ...
]
```

---

## 📍 Baixa Múltipla

### Realizar Baixa Múltipla
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
  ],
  "conta_bancaria_destino_id": 1,
  "observacao": "Venda parcelada no cartão - Pedido #1234"
}
```

**Campos:**
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| conta_id | integer | Sim | ID da conta original |
| tipo_conta | string | Sim | "PAGAR" ou "RECEBER" |
| parcelas_geradas | array | Sim | Array de parcelas a gerar |
| conta_bancaria_destino_id | integer | Sim | ID da conta bancária |
| observacao | string | Não | Observações adicionais |

**Resposta (200 OK):**
```json
{
  "message": "Baixa múltipla realizada com sucesso",
  "conta_original_id": 100,
  "movimentacao_bancaria_id": 500,
  "contas_geradas": 10,
  "contas_geradas_ids": [201, 202, 203, 204, 205, 206, 207, 208, 209, 210],
  "valor_total": 10000.00
}
```

**Erros:**
- `400 Bad Request`: Parcelas não informadas ou valor total divergente
- `404 Not Found`: Conta ou conta bancária não encontrada
- `500 Internal Server Error`: Erro ao processar baixa múltipla

---

## 📍 Histórico de Liquidação

### Listar Histórico
```http
GET /financeiro/historico-liquidacao
```

**Query Parameters:**
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| tipo_operacao | string | Não | Filtrar por tipo: COMPENSACAO, BAIXA_MULTIPLA, BAIXA_SIMPLES |
| skip | integer | Não | Offset para paginação (padrão: 0) |
| limit | integer | Não | Limite de registros (padrão: 100) |

**Exemplo:**
```bash
curl -X GET "http://localhost:8000/financeiro/historico-liquidacao?tipo_operacao=BAIXA_MULTIPLA&limit=50" \
  -H "Authorization: Bearer {token}"
```

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "tipo_operacao": "BAIXA_MULTIPLA",
    "data_operacao": "2024-12-09T10:30:00",
    "valor_total": 10000.00,
    "conta_origem_id": 100,
    "tipo_conta_origem": "RECEBER",
    "contas_geradas_ids": [201, 202, 203, 204, 205, 206, 207, 208, 209, 210],
    "movimentacao_bancaria_id": 500,
    "observacao": "Venda parcelada no cartão",
    "created_by": 1,
    "created_at": "2024-12-09T10:30:00"
  },
  ...
]
```

---

## 🔒 Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado com sucesso |
| 400 | Bad Request - Dados inválidos ou faltantes |
| 401 | Unauthorized - Token de autenticação inválido ou ausente |
| 403 | Forbidden - Usuário sem permissão para a operação |
| 404 | Not Found - Recurso não encontrado |
| 500 | Internal Server Error - Erro no servidor |

---

## 🔐 Permissões Necessárias

| Endpoint | Permissão |
|----------|-----------|
| GET (consultas) | `financeiro:read` |
| POST (criação) | `financeiro:create` |
| PUT (atualização) | `financeiro:update` |
| DELETE (exclusão) | `financeiro:delete` |

---

## 📝 Notas Importantes

1. **Datas:** Sempre use formato ISO 8601 (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)
2. **Valores:** Use ponto (.) como separador decimal, não vírgula
3. **Paginação:** Todos os endpoints de listagem suportam `skip` e `limit`
4. **Transações:** Operações complexas são atômicas (rollback automático em erro)
5. **Validação:** Todos os dados são validados via Pydantic schemas

---

**Última atualização:** 09/12/2024
**Versão da API:** 1.0.0
