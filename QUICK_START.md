# 🚀 Guia Rápido de Inicialização - ERP Open

## ✅ Status Atual
**Ambos os serviços estão RODANDO!**

---

## 🌐 URLs Disponíveis

| Serviço          | URL                          |
|------------------|------------------------------|
| 🎨 Frontend      | http://localhost:5173        |
| 📦 Backend API   | http://localhost:8000        |
| 📚 Documentação  | http://localhost:8000/docs   |

---

## 🔧 Comandos para Iniciar os Serviços

### Backend (Terminal 1)
```bash
cd /home/pc/Documentos/Erpopen/backend
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Terminal 2)
```bash
cd /home/pc/Documentos/Erpopen/frontend
npm run dev
```

---

## 🔍 Verificar Status dos Serviços

Execute este comando a qualquer momento:
```bash
/home/pc/Documentos/Erpopen/check_services.sh
```

Este script verifica:
- ✅ Se os processos estão rodando
- ✅ Se as portas estão respondendo
- ✅ Se o CORS está configurado
- ✅ Se a comunicação entre frontend e backend funciona

---

## 🛑 Parar os Serviços

### Método 1: Ctrl+C
Pressione `Ctrl+C` nos terminais onde os serviços estão rodando

### Método 2: Kill por processo
```bash
# Parar backend
pkill -f "uvicorn main:app"

# Parar frontend
pkill -f "vite"
```

---

## 🔑 Credenciais de Teste

**Email:** `admin@erp.com`  
**Senha:** `admin123`

---

## ⚠️ Correções Aplicadas

1. ✅ **Deprecation Warning do FastAPI resolvido**
   - Migrado de `@app.on_event("startup")` para `lifespan`
   - Código atualizado para FastAPI moderno

2. ✅ **Script de verificação criado**
   - Verifica backend e frontend automaticamente
   - Mostra status detalhado de cada serviço

---

## 📋 Checklist de Funcionamento

Execute após iniciar os serviços:

```bash
# 1. Verificar serviços
/home/pc/Documentos/Erpopen/check_services.sh

# 2. Testar backend diretamente
curl http://localhost:8000/

# 3. Testar frontend
curl -s http://localhost:5173/ | grep "<title>"

# 4. Abrir no navegador
# Acesse: http://localhost:5173
```

---

## 🐛 Próximos Passos para Testes

1. **Abrir no navegador**: http://localhost:5173
2. **Abrir DevTools**: Pressione F12
3. **Verificar Console**: Procurar por erros em vermelho
4. **Testar Login**: Usar credenciais acima
5. **Reportar erros**: Copiar mensagens de erro do console

---

## 💡 Dicas

- Sempre verifique os serviços com `check_services.sh` antes de testar
- Mantenha 2 terminais abertos (um para backend, outro para frontend)
- O backend com `--reload` reinicia automaticamente ao editar código
- O frontend (Vite) também tem hot reload automático

---

**Última atualização:** 2025-11-18 23:29 UTC
