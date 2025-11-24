#!/bin/bash

# Script para criar issues no GitHub via gh CLI
# Requer: gh CLI instalado e autenticado (gh auth login)

REPO="BrunoReni/Erpopen"
MILESTONE="v1.0-mvp"

echo "🚀 Criando issues para ERP Open"
echo "================================"
echo ""

# Verificar se gh CLI está instalado
if ! command -v gh &> /dev/null; then
    echo "❌ gh CLI não está instalado!"
    echo "   Instale: https://cli.github.com/"
    exit 1
fi

# Verificar autenticação
if ! gh auth status &> /dev/null; then
    echo "❌ Não está autenticado no GitHub!"
    echo "   Execute: gh auth login"
    exit 1
fi

echo "✅ gh CLI configurado"
echo ""

# Função para criar issue
create_issue() {
    local title="$1"
    local body="$2"
    local labels="$3"
    
    echo "📝 Criando: $title"
    
    gh issue create \
        --repo "$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels" \
        --milestone "$MILESTONE"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Issue criada com sucesso!"
    else
        echo "   ❌ Erro ao criar issue"
    fi
    echo ""
}

# ==============================================================================
# ISSUE #1: Testes Backend
# ==============================================================================

create_issue \
"[CRÍTICO] Configurar Testes Backend com Pytest" \
"## 📝 Descrição
Implementar testes automatizados no backend usando Pytest.

## ✅ Tarefas
- [ ] Instalar \`pytest\`, \`pytest-asyncio\`, \`pytest-cov\`, \`httpx\`
- [ ] Criar estrutura \`backend/tests/\`
- [ ] Criar \`conftest.py\` com fixtures reutilizáveis
- [ ] Implementar testes para autenticação (test_auth.py)
- [ ] Implementar testes para módulo de compras (test_compras.py)
- [ ] Implementar testes para módulo financeiro (test_financeiro.py)
- [ ] Implementar testes para módulo de materiais (test_materiais.py)
- [ ] Implementar testes para módulo de vendas (test_vendas.py)
- [ ] Implementar testes para helpers (test_helpers.py)
- [ ] Configurar coverage mínimo de 80%
- [ ] Adicionar comando \`pytest --cov\` ao README

## 🎯 Critérios de Aceitação
- ✅ Pelo menos 50 testes implementados
- ✅ Coverage mínimo de 80%
- ✅ Todos os testes passando
- ✅ Executar em < 30 segundos

## 📚 Recursos
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

**Estimativa:** 8 horas" \
"testing,backend,critical,good first issue"

# ==============================================================================
# ISSUE #2: Testes Frontend
# ==============================================================================

create_issue \
"[CRÍTICO] Configurar Testes Frontend com Vitest" \
"## 📝 Descrição
Implementar testes automatizados no frontend usando Vitest e React Testing Library.

## ✅ Tarefas
- [ ] Instalar \`vitest\`, \`@testing-library/react\`, \`@testing-library/jest-dom\`, \`jsdom\`
- [ ] Configurar \`vitest.config.ts\`
- [ ] Criar estrutura \`frontend/src/__tests__/\`
- [ ] Implementar testes de componentes (Button, Modal, Form)
- [ ] Implementar testes de páginas (Login, Clientes, Materiais)
- [ ] Implementar testes de hooks customizados
- [ ] Implementar testes de utils/helpers
- [ ] Configurar coverage mínimo de 70%
- [ ] Adicionar scripts \`npm test\` e \`npm run test:coverage\`

## 🎯 Critérios de Aceitação
- ✅ Pelo menos 30 testes implementados
- ✅ Coverage mínimo de 70%
- ✅ Todos os testes passando
- ✅ Componentes críticos testados (Login, Form, List)

## 📚 Recursos
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)

**Estimativa:** 8 horas" \
"testing,frontend,critical"

# ==============================================================================
# ISSUE #3: Variáveis de Ambiente
# ==============================================================================

create_issue \
"[CRÍTICO] Implementar Variáveis de Ambiente Seguras" \
"## 📝 Descrição
Configurar variáveis de ambiente corretamente para evitar exposição de secrets.

## ✅ Tarefas
- [ ] Criar \`backend/.env.example\` documentado
- [ ] Criar \`frontend/.env.example\` documentado
- [ ] Remover hardcoded secrets do código
- [ ] Atualizar \`.gitignore\` para garantir que \`.env\` não seja versionado
- [ ] Criar script de setup (\`setup.sh\`) que copia \`.env.example\` para \`.env\`
- [ ] Atualizar documentação com instruções de configuração
- [ ] Gerar SECRET_KEY aleatória no primeiro setup

## 🎯 Critérios de Aceitação
- ✅ Sem secrets hardcoded no código
- ✅ \`.env.example\` documentados
- ✅ Script de setup funcional
- ✅ Documentação atualizada

**Estimativa:** 2 horas" \
"security,backend,frontend,critical"

# ==============================================================================
# ISSUE #4: Error Handling
# ==============================================================================

create_issue \
"[CRÍTICO] Implementar Tratamento de Erros Padronizado" \
"## 📝 Descrição
Criar sistema de tratamento de erros consistente em todo o sistema.

## ✅ Tarefas Backend
- [ ] Criar \`app/core/exceptions.py\` com classes customizadas
- [ ] Implementar \`ERPException\`, \`NotFoundException\`, \`DuplicateException\`
- [ ] Criar exception handlers globais no FastAPI
- [ ] Substituir \`raise HTTPException\` por exceptions customizadas
- [ ] Adicionar logs de erros
- [ ] Retornar erros em formato padronizado JSON

## ✅ Tarefas Frontend
- [ ] Criar \`src/utils/errorHandler.ts\`
- [ ] Implementar interceptor Axios para erros
- [ ] Criar componente Toast/Notification para exibir erros
- [ ] Padronizar mensagens de erro
- [ ] Implementar error boundaries para erros de React

## 🎯 Critérios de Aceitação
- ✅ Todos os erros seguem formato padrão
- ✅ Mensagens amigáveis ao usuário
- ✅ Logs de erros estruturados
- ✅ Error boundaries implementados

**Estimativa:** 4 horas" \
"enhancement,backend,frontend,critical"

# ==============================================================================
# ISSUE #5: Logging
# ==============================================================================

create_issue \
"[CRÍTICO] Implementar Logging Estruturado" \
"## 📝 Descrição
Configurar sistema de logging profissional para facilitar debug e monitoramento.

## ✅ Tarefas
- [ ] Criar \`backend/app/core/logging.py\`
- [ ] Configurar logger com níveis (DEBUG, INFO, WARNING, ERROR)
- [ ] Implementar RotatingFileHandler (10MB, 5 backups)
- [ ] Criar pasta \`logs/\` no backend
- [ ] Adicionar logging em todas as rotas (request/response)
- [ ] Adicionar logging em operações críticas (auth, db)
- [ ] Formato: \`timestamp - level - module - message\`
- [ ] Remover print statements do código

## 🎯 Critérios de Aceitação
- ✅ Logs estruturados e legíveis
- ✅ Rotação automática de arquivos
- ✅ Console e arquivo simultâneos
- ✅ Sem print statements no código

**Estimativa:** 3 horas" \
"observability,backend,critical"

# ==============================================================================
# ISSUE #6: CI/CD
# ==============================================================================

create_issue \
"[CRÍTICO] Configurar CI/CD com GitHub Actions" \
"## 📝 Descrição
Automatizar testes e build a cada push/PR usando GitHub Actions.

## ✅ Tarefas
- [ ] Criar \`.github/workflows/backend-tests.yml\`
- [ ] Criar \`.github/workflows/frontend-tests.yml\`
- [ ] Configurar job de testes backend (pytest)
- [ ] Configurar job de testes frontend (vitest)
- [ ] Configurar job de build frontend
- [ ] Upload de coverage para Codecov
- [ ] Badges no README (build status, coverage)
- [ ] Configurar branch protection (require tests)

## 🎯 Critérios de Aceitação
- ✅ Workflows funcionando no GitHub
- ✅ Badges no README
- ✅ Testes rodando automaticamente
- ✅ PRs bloqueados se testes falharem

**Estimativa:** 4 horas" \
"devops,ci-cd,critical"

# ==============================================================================
# ISSUE #7: Pedidos de Venda Backend
# ==============================================================================

create_issue \
"[ALTO] Implementar Pedidos de Venda - Backend" \
"## 📝 Descrição
Criar módulo completo de Pedidos de Venda no backend.

## ✅ Tarefas
- [ ] Criar model \`PedidoVenda\` e \`ItensPedidoVenda\`
- [ ] Criar schemas Pydantic com validações
- [ ] Implementar CRUD completo (8 endpoints)
- [ ] Gerar código automático (PV-XXXX)
- [ ] Calcular totais automaticamente
- [ ] Status: ORCAMENTO, APROVADO, FATURADO, CANCELADO
- [ ] Vincular com Cliente (FK)
- [ ] Adicionar itens com Material (FK)
- [ ] Validar estoque disponível ao adicionar item

## 🎯 Critérios de Aceitação
- ✅ CRUD completo funcionando
- ✅ Código automático gerado
- ✅ Validações implementadas
- ✅ Testes com 80% coverage

**Estimativa:** 6 horas" \
"feature,backend,vendas,high-priority"

# ==============================================================================
# ISSUE #8: Pedidos de Venda Frontend
# ==============================================================================

create_issue \
"[ALTO] Implementar Pedidos de Venda - Frontend" \
"## 📝 Descrição
Criar interface completa para gerenciar Pedidos de Venda.

## ✅ Tarefas
- [ ] Criar página \`/vendas/pedidos\`
- [ ] Componente de listagem com busca
- [ ] Modal de criação/edição
- [ ] Formulário com seleção de cliente
- [ ] Tabela de itens com adicionar/remover
- [ ] Cálculo automático de totais
- [ ] Badges de status coloridos
- [ ] Ações: Aprovar, Faturar, Cancelar
- [ ] Validações de estoque no frontend
- [ ] Adicionar rota no menu lateral

## 🎯 Critérios de Aceitação
- ✅ Interface completa e responsiva
- ✅ Todas as operações funcionando
- ✅ Validações implementadas
- ✅ UX fluida e intuitiva

**Estimativa:** 6 horas" \
"feature,frontend,vendas,high-priority"

# ==============================================================================
# ISSUE #9: Integração Compra
# ==============================================================================

create_issue \
"[ALTO] Integração Pedido de Compra → Conta a Pagar" \
"## 📝 Descrição
Automatizar criação de Conta a Pagar a partir de Pedido de Compra.

## ✅ Tarefas
- [ ] Criar endpoint \`POST /compras/pedidos/{id}/gerar-conta\`
- [ ] Validar status do pedido (deve estar APROVADO)
- [ ] Criar Conta a Pagar vinculada ao pedido
- [ ] Copiar valores e data de vencimento
- [ ] Atualizar status do pedido para FATURADO
- [ ] Adicionar campo \`pedido_compra_id\` em ContaPagar
- [ ] Implementar botão no frontend
- [ ] Validar que não pode gerar duas vezes
- [ ] Adicionar logs da operação

## 🎯 Critérios de Aceitação
- ✅ Conta criada automaticamente
- ✅ Vínculo entre pedido e conta
- ✅ Validações implementadas
- ✅ Botão funcional no frontend

**Estimativa:** 3 horas" \
"feature,backend,integration,high-priority"

# ==============================================================================
# ISSUE #10: Integração Venda
# ==============================================================================

create_issue \
"[ALTO] Integração Pedido de Venda → Conta a Receber" \
"## 📝 Descrição
Automatizar criação de Conta a Receber a partir de Pedido de Venda (faturamento).

## ✅ Tarefas
- [ ] Implementar lógica no endpoint \`POST /vendas/pedidos/{id}/faturar\`
- [ ] Criar Conta a Receber automaticamente
- [ ] Baixar estoque automaticamente
- [ ] Criar movimentação de estoque SAIDA
- [ ] Validar estoque disponível antes de faturar
- [ ] Atualizar status do pedido para FATURADO
- [ ] Transação atômica (rollback se falhar)
- [ ] Implementar botão no frontend

## 🎯 Critérios de Aceitação
- ✅ Conta criada automaticamente
- ✅ Estoque baixado corretamente
- ✅ Transação atômica
- ✅ Validações implementadas

**Estimativa:** 3 horas" \
"feature,backend,integration,high-priority"

# ==============================================================================
# Resumo
# ==============================================================================

echo "================================"
echo "✅ Issues criadas com sucesso!"
echo ""
echo "📊 Resumo:"
echo "   - CRÍTICO: 6 issues"
echo "   - ALTO: 4 issues"
echo "   - Total: 10 issues"
echo ""
echo "🔗 Ver issues: https://github.com/$REPO/issues"
echo ""
echo "📝 Próximo passo:"
echo "   1. Revisar issues no GitHub"
echo "   2. Criar Project Board"
echo "   3. Começar desenvolvimento!"
echo ""
