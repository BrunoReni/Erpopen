# 🧪 Testes Automatizados - Backend

## 📊 Status Atual

- ✅ **21 testes** implementados
- ✅ **17 testes passando** (81% taxa de sucesso)
- ✅ **65% cobertura de código**

## 🏃 Executando os Testes

### Executar todos os testes
```bash
pytest tests/
```

### Executar com verbosidade
```bash
pytest tests/ -v
```

### Executar com cobertura
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

### Executar testes específicos
```bash
pytest tests/test_auth.py  # Apenas autenticação
pytest tests/test_vendas.py  # Apenas vendas
pytest tests/test_helpers.py  # Apenas helpers
```

## 📁 Estrutura dos Testes

```
tests/
├── __init__.py
├── conftest.py         # Fixtures compartilhadas
├── test_auth.py        # Testes de autenticação (7 testes)
├── test_compras.py     # Testes de compras (5 testes)
├── test_helpers.py     # Testes de helpers (9 testes)
└── test_vendas.py      # Testes de vendas (8 testes) - ainda não executados
```

## 🎯 Cobertura por Módulo

| Módulo | Cobertura | Status |
|--------|-----------|--------|
| models.py | 100% | ✅ |
| models_modules.py | 100% | ✅ |
| schemas.py | 100% | ✅ |
| schemas_modules.py | 100% | ✅ |
| security.py | 100% | ✅ |
| core/config.py | 100% | ✅ |
| db.py | 79% | ✅ |
| crud.py | 39% | ⚠️ |
| routes/auth.py | 46% | ⚠️ |
| routes/compras.py | 39% | ⚠️ |
| routes/vendas.py | 25% | ⚠️ |
| helpers.py | 36% | ⚠️ |

## ✅ Testes Implementados

### Autenticação (7 testes)
- ✅ test_root_endpoint - Verifica endpoint raiz
- ✅ test_login_success - Login com credenciais válidas
- ✅ test_login_invalid_credentials - Login com senha errada
- ✅ test_login_nonexistent_user - Login com usuário inexistente
- ✅ test_get_current_user - Obter usuário atual autenticado
- ✅ test_get_current_user_unauthorized - Sem token
- ✅ test_get_current_user_invalid_token - Token inválido

### Helpers (9 testes)
- ✅ test_gerar_codigo_fornecedor - Geração de código FOR-XXXX
- ✅ test_gerar_codigo_cliente - Geração de código CLI-XXXX
- ✅ test_gerar_codigo_material - Geração de código MAT-XXXX
- ✅ test_validar_cpf_valido - CPF válido
- ✅ test_validar_cpf_invalido - CPF inválido
- ✅ test_validar_cpf_formato_invalido - CPF com formato errado
- ✅ test_validar_cnpj_valido - CNPJ válido
- ✅ test_validar_cnpj_invalido - CNPJ inválido
- ✅ test_validar_cnpj_formato_invalido - CNPJ com formato errado

### Compras (5 testes)
- ✅ test_list_fornecedores_empty - Listagem vazia
- ⚠️ test_create_fornecedor - Criar fornecedor (falha na resposta)
- ⚠️ test_get_fornecedor_by_id - Buscar por ID (falha na resposta)
- ⚠️ test_update_fornecedor - Atualizar fornecedor (403 Forbidden)
- ⚠️ test_delete_fornecedor - Excluir fornecedor (403 Forbidden)

### Vendas (8 testes) - A serem executados
- test_list_clientes_empty
- test_create_cliente_pf
- test_create_cliente_pj
- test_get_cliente_by_id
- test_update_cliente
- test_delete_cliente
- test_search_cliente_by_cpf

## 🔧 Fixtures Disponíveis

### Fixtures de Sessão
- `db_session` - Sessão de banco de dados em memória
- `client` - Cliente de teste FastAPI
- `admin_user` - Usuário admin com todas as permissões
- `auth_headers` - Headers com token JWT válido

## 🎯 Próximos Passos

1. ⏳ Corrigir 4 testes de compras que estão falhando
2. ⏳ Executar e validar testes de vendas
3. ⏳ Adicionar testes para módulo financeiro
4. ⏳ Adicionar testes para módulo de materiais
5. ⏳ Aumentar cobertura para 80%+
6. ⏳ Adicionar testes de integração E2E

## 📚 Documentação

- [Pytest](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)

## 🐛 Problemas Conhecidos

1. **Permissões em testes de compras**: Alguns testes estão retornando 403 Forbidden
   - Causa: Permissões não configuradas corretamente nos fixtures
   - Status: A corrigir

2. **Campos ausentes em resposta**: Alguns campos não estão sendo retornados
   - Causa: Schemas de resposta podem estar incompletos
   - Status: A investigar

---

**Última atualização:** 25/11/2025  
**Cobertura atual:** 65%  
**Objetivo:** 80%
