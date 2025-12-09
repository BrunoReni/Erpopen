# 🤝 Guia de Contribuição - ERP Open

Obrigado pelo interesse em contribuir com o **ERP Open**! Este documento fornece diretrizes para garantir qualidade e consistência no desenvolvimento.

---

## 📋 Table of Contents

- [Definition of Done (DoD)](#definition-of-done-dod)
- [Fluxo de Trabalho](#fluxo-de-trabalho)
- [Commits Semânticos](#commits-semânticos)
- [Processo de Code Review](#processo-de-code-review)
- [Boas Práticas](#boas-práticas)
- [Como Evitar Gaps Backend/Frontend](#como-evitar-gaps-backendfrontend)
- [Sistema de Feature Flags](#sistema-de-feature-flags)
- [Dev Tools Dashboard](#dev-tools-dashboard)

---

## ✅ Definition of Done (DoD)

Uma feature/task é considerada **"DONE"** quando atende **TODOS** os critérios abaixo:

### Backend
- ✅ Endpoint implementado e testado
- ✅ Model/Schema criado e validado
- ✅ Validações de entrada implementadas
- ✅ Tratamento de erros adequado
- ✅ Testes unitários escritos e passando
- ✅ Swagger/OpenAPI atualizado
- ✅ Logs apropriados

### Frontend
- ✅ Componente React criado
- ✅ Integração com API funcional
- ✅ Validações de formulário
- ✅ Feedback visual (loading, erros)
- ✅ Interface responsiva
- ✅ Acessibilidade básica

### Integração
- ✅ Feature registrada em `backend/app/feature_flags.py`
- ✅ Rota configurada no frontend
- ✅ Menu/navegação atualizado (se aplicável)
- ✅ Permissões configuradas
- ✅ Teste E2E (se aplicável)

### Documentação
- ✅ Código documentado (comentários quando necessário)
- ✅ README atualizado (se aplicável)
- ✅ API endpoints documentados

### Quality Gates
- ✅ Build passa sem erros
- ✅ Todos os testes passando
- ✅ Linter sem erros críticos
- ✅ Feature Completeness Check passou
- ✅ Code review aprovado

---

## 🔄 Fluxo de Trabalho

### 1. Criar Issue
- Descreva claramente o problema ou feature
- Use labels apropriados (bug, feature, enhancement)
- Defina acceptance criteria

### 2. Criar Branch
```bash
# Para features
git checkout -b feature/nome-da-feature

# Para bugs
git checkout -b fix/nome-do-bug

# Para melhorias
git checkout -b enhancement/nome-da-melhoria
```

### 3. Desenvolvimento

#### Backend First (se aplicável)
1. Criar modelos e schemas
2. Implementar endpoints
3. Escrever testes
4. Registrar em `feature_flags.py` com `has_backend=True, has_frontend=False`

#### Frontend Implementation
1. Criar componentes React
2. Integrar com API
3. Adicionar validações
4. Testar responsividade
5. Atualizar `feature_flags.py` com `has_frontend=True`

#### Integration
1. Adicionar rota em `App.tsx`
2. Adicionar item de menu (se aplicável)
3. Configurar permissões
4. Testar fluxo completo
5. Atualizar `feature_flags.py` para `has_tests=True, has_docs=True`

### 4. Commits
Use commits semânticos (veja seção abaixo)

### 5. Pull Request
- Preencha o template completamente
- Marque todos os checkboxes aplicáveis
- Adicione screenshots (se UI)
- Solicite reviewers apropriados

### 6. Code Review
- Responda a todos os comentários
- Faça alterações solicitadas
- Re-solicite review após mudanças

### 7. Merge
- Certifique-se de que CI/CD está verde
- Merge após aprovação
- Delete a branch após merge

---

## 📝 Commits Semânticos

Siga o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<escopo>): <descrição curta>

[corpo opcional]

[rodapé opcional]
```

### Tipos Permitidos
- `feat`: Nova feature
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação, missing semi colons, etc
- `refactor`: Refatoração de código
- `test`: Adição de testes
- `chore`: Manutenção, configs, etc
- `perf`: Melhorias de performance

### Exemplos
```bash
feat(financeiro): adicionar endpoint de compensação

fix(vendas): corrigir cálculo de desconto em pedidos

docs(readme): atualizar instruções de instalação

refactor(auth): simplificar lógica de autenticação

test(materiais): adicionar testes para movimentação de estoque
```

---

## 👀 Processo de Code Review

### Para Reviewers

#### Checklist de Review
- [ ] Código segue padrões do projeto
- [ ] Lógica está correta e eficiente
- [ ] Testes cobrem casos principais
- [ ] Sem código comentado desnecessário
- [ ] Sem credenciais hardcoded
- [ ] Documentação adequada
- [ ] Feature completa (backend + frontend)
- [ ] Sem breaking changes não documentados

#### Tipos de Comentários
- **🔴 Blocker**: Deve ser corrigido antes do merge
- **🟡 Suggestion**: Pode ser melhorado mas não é blocker
- **💡 Nitpick**: Sugestão opcional de melhoria
- **❓ Question**: Pedido de esclarecimento

### Para Contributors
- Responda a todos os comentários
- Explique decisões técnicas quando necessário
- Marque comentários como resolvidos
- Seja aberto a sugestões

---

## 🎨 Boas Práticas

### Backend (Python/FastAPI)

#### Estrutura de Endpoints
```python
@router.get("/items", response_model=List[ItemRead])
def list_items(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("items:read"))
):
    """Lista items com paginação"""
    return session.query(Item).offset(skip).limit(limit).all()
```

#### Validações
```python
from pydantic import BaseModel, validator

class ItemCreate(BaseModel):
    name: str
    price: float
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```

#### Tratamento de Erros
```python
from fastapi import HTTPException

if not item:
    raise HTTPException(
        status_code=404,
        detail="Item not found"
    )
```

### Frontend (React/TypeScript)

#### Componentes
```typescript
interface Props {
  title: string;
  onSave: (data: FormData) => void;
}

export function MyComponent({ title, onSave }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Component logic
}
```

#### API Calls
```typescript
const loadData = async () => {
  try {
    setLoading(true);
    setError(null);
    const response = await api.get('/endpoint');
    setData(response.data);
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Error loading data');
  } finally {
    setLoading(false);
  }
};
```

#### Estados de Loading/Error
```typescript
if (loading) return <LoadingSpinner />;
if (error) return <ErrorMessage message={error} />;
return <ActualContent />;
```

---

## 🚫 Como Evitar Gaps Backend/Frontend

### ❌ NÃO FAÇA
```python
# Implementar apenas backend
@router.post("/new-feature")
def new_feature():
    # Implementação completa
    pass

# E depois esquecer o frontend!
```

### ✅ FAÇA
```python
# 1. Implementar backend
@router.post("/new-feature")
def new_feature():
    pass

# 2. Registrar em feature_flags.py
Feature(
    id="new_feature",
    name="Nova Feature",
    has_backend=True,
    has_frontend=False,  # ⚠️ Marcar como incompleto!
    ...
)

# 3. Implementar frontend
function NewFeatureComponent() {
    // Implementação
}

# 4. Atualizar feature_flags.py
Feature(
    id="new_feature",
    has_backend=True,
    has_frontend=True,  # ✅ Agora completo!
    ...
)
```

### Pipeline de Desenvolvimento
```
1. Issue Created
   ↓
2. Backend Implementation
   ↓
3. Register in feature_flags.py (backend_only)
   ↓
4. Frontend Implementation
   ↓
5. Update feature_flags.py (complete)
   ↓
6. Integration Tests
   ↓
7. Pull Request
   ↓
8. Code Review
   ↓
9. Feature Completeness Check (CI/CD)
   ↓
10. Merge
```

---

## 🏴‍☠️ Sistema de Feature Flags

### Localização
`backend/app/feature_flags.py`

### Estrutura
```python
Feature(
    id="unique_feature_id",
    name="Nome Legível",
    module="nome_modulo",  # financeiro, vendas, compras, materiais
    description="Descrição da feature",
    has_backend=True/False,
    has_frontend=True/False,
    has_tests=True/False,
    has_docs=True/False,
    backend_endpoints=["POST /endpoint"],
    frontend_components=["ComponentName"],
    test_files=["test_module.py"],
    doc_files=["DOC.md"],
    issue_number=123,  # Opcional
    pr_number=456,     # Opcional
)
```

### Status Automático
O sistema calcula automaticamente o status:
- `complete`: Tudo implementado
- `backend_only`: ⚠️ Apenas backend (CRÍTICO)
- `frontend_only`: Apenas frontend
- `partial`: Implementação parcial
- `disabled`: Planejado/desabilitado

### Como Adicionar Nova Feature
```python
# 1. Adicionar ao FEATURES_REGISTRY em feature_flags.py
FEATURES_REGISTRY.append(
    Feature(
        id="my_new_feature",
        name="Minha Nova Feature",
        module="financeiro",
        description="Feature incrível que faz X",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=False,  # TODO: adicionar docs
        backend_endpoints=["GET /api/my-feature"],
        frontend_components=["MyFeatureComponent"],
        test_files=["test_my_feature.py"],
    )
)
```

---

## 🔧 Dev Tools Dashboard

### Acesso
- URL: `http://localhost:5173/dev/integration`
- Permissão: `admin:read` (apenas admins)

### Funcionalidades
- 📊 Métricas de completude
- 📋 Lista de todas as features
- 🔍 Filtros (completas, incompletas, só backend)
- ✅ Indicadores visuais de status
- 📈 Barras de progresso por feature

### Como Usar
1. Faça login como admin
2. Acesse menu "🔧 Dev Tools"
3. Visualize status de todas as features
4. Identifique gaps (features incompletas)
5. Priorize implementações

### API Endpoints
```bash
# Listar todas features
GET /dev/features

# Estatísticas
GET /dev/features/stats

# Gaps críticos
GET /dev/features/gaps

# Feature específica
GET /dev/features/{feature_id}

# Features de um módulo
GET /dev/features/modules/{module}
```

---

## 🧪 Testando Localmente

### Backend
```bash
cd backend

# Instalar dependências
pip install -r requirements.txt

# Rodar testes
python -m pytest tests/ -v

# Verificar completude de features
python -c "from app.feature_flags import get_features_statistics; print(get_features_statistics())"

# Iniciar servidor
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Rodar em dev mode
npm run dev

# Build para produção
npm run build
```

### Validação de Feature
```bash
cd backend
python << EOF
from app.feature_flags import get_feature_by_id

feature = get_feature_by_id('my_feature_id')
print(f"Status: {feature.status}")
print(f"Completude: {feature.completeness_percentage}%")
print(f"Backend: {feature.has_backend}")
print(f"Frontend: {feature.has_frontend}")
EOF
```

---

## 🆘 Precisa de Ajuda?

- **Issues**: Crie uma issue no GitHub
- **Dúvidas**: Comente na issue relacionada
- **Bugs**: Use o template de bug report
- **Features**: Use o template de feature request

---

## 📚 Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Feature Toggles Pattern](https://martinfowler.com/articles/feature-toggles.html)
- [Definition of Done](https://www.agilealliance.org/glossary/definition-of-done/)

---

**🎉 Obrigado por contribuir com o ERP Open!**

Sua contribuição ajuda a construir o primeiro ERP opensource brasileiro adaptado à nova reforma fiscal. 🇧🇷
