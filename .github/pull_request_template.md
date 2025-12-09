# 📋 Pull Request Description

## 🎯 Objetivo

<!-- Descreva brevemente o objetivo deste PR -->

## 🔗 Issues Relacionadas

<!-- Liste as issues relacionadas: Closes #123, Relates to #456 -->

---

## ✅ Checklist de Definition of Done

### 🔧 Backend

- [ ] Endpoint(s) implementado(s) e documentado(s)
- [ ] Model/Schema criado e validado
- [ ] Validações de entrada implementadas
- [ ] Testes unitários escritos e passando
- [ ] Swagger/OpenAPI atualizado
- [ ] Tratamento de erros adequado
- [ ] Logs apropriados adicionados

### 🎨 Frontend

- [ ] Componente(s) React criado(s)
- [ ] Integração com API funcional
- [ ] Validações de formulário implementadas
- [ ] Feedback visual (loading, erros, sucesso)
- [ ] Interface responsiva (mobile, tablet, desktop)
- [ ] Acessibilidade (ARIA labels quando necessário)
- [ ] Estados de erro tratados adequadamente

### 🔗 Integração Backend/Frontend

- [ ] Feature registrada em `backend/app/feature_flags.py`
- [ ] Status da feature atualizado (has_backend, has_frontend, etc)
- [ ] Rota adicionada ao frontend (`App.tsx`)
- [ ] Item de menu adicionado (se aplicável)
- [ ] Permissões configuradas corretamente
- [ ] Teste E2E realizado (se aplicável)

### 🧪 Testes

- [ ] Testes unitários backend (pytest)
- [ ] Testes de integração (se aplicável)
- [ ] Testes manuais realizados
- [ ] Testado em diferentes navegadores (Chrome, Firefox, Safari)
- [ ] Testado em dispositivos móveis

### 📚 Documentação

- [ ] README atualizado (se necessário)
- [ ] CHANGELOG atualizado (se necessário)
- [ ] Documentação técnica atualizada
- [ ] Comentários no código (quando necessário)
- [ ] API endpoints documentados

### 🔒 Segurança

- [ ] Validação de entrada no backend
- [ ] Sanitização de dados
- [ ] Controle de acesso/permissões verificado
- [ ] Sem credenciais hardcoded
- [ ] Vulnerabilidades conhecidas verificadas

### 📊 Quality Gates

- [ ] Build do frontend passa sem erros
- [ ] Testes do backend passam (pytest)
- [ ] Linter passa sem erros
- [ ] Feature Completeness Check passou
- [ ] Sem warnings críticos

---

## 🧪 Como Testar

### Backend
```bash
cd backend
python -m pytest tests/
# Ou testar endpoint específico:
curl -X GET http://localhost:8000/[seu-endpoint]
```

### Frontend
```bash
cd frontend
npm run dev
# Acessar: http://localhost:5173/[sua-rota]
```

### Validação de Feature
```bash
# Verificar completude da feature
cd backend
python -c "from app.feature_flags import get_feature_by_id; print(get_feature_by_id('[feature_id]').to_dict())"
```

---

## 📸 Screenshots

<!-- Adicione screenshots da interface, se aplicável -->

### Antes
<!-- Screenshot do estado anterior (se houver) -->

### Depois
<!-- Screenshot do novo estado -->

---

## 🔄 Mudanças Técnicas

### Arquivos Modificados
<!-- Liste os principais arquivos modificados e por quê -->

### Dependências Adicionadas
<!-- Liste novas dependências, se houver -->

### Breaking Changes
<!-- Liste breaking changes, se houver -->

---

## ✨ Melhorias Futuras

<!-- Liste possíveis melhorias que podem ser feitas no futuro -->

---

## 👥 Revisores Sugeridos

<!-- Mencione revisores específicos, se necessário -->
- @BrunoReni (PO/PM) - Validação de negócio
- Backend Developer - Validação técnica backend
- Frontend Developer - Validação técnica frontend

---

## 📝 Notas Adicionais

<!-- Informações adicionais que os revisores devem saber -->

---

**⚠️ LEMBRETE**: Este PR segue o padrão de Quality Gates. Certifique-se de que:
1. ✅ Toda feature backend tem frontend correspondente
2. ✅ Feature está registrada em `feature_flags.py`
3. ✅ Testes estão passando
4. ✅ Documentação está atualizada
