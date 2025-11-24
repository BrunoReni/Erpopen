# 🚀 COMANDOS PARA EXECUTAR O SISTEMA

**Data**: 2025-11-19 01:57 UTC

---

## ▶️ INICIAR BACKEND

```bash
cd /home/pc/Documentos/Erpopen/backend
source .venv/bin/activate
python main.py
```

**OU** (em background):
```bash
cd /home/pc/Documentos/Erpopen/backend
source .venv/bin/activate
nohup python main.py > /tmp/backend.log 2>&1 &
```

---

## ▶️ INICIAR FRONTEND

```bash
cd /home/pc/Documentos/Erpopen/frontend
npm run dev
```

**OU** (em background):
```bash
cd /home/pc/Documentos/Erpopen/frontend
nohup npm run dev > /tmp/frontend.log 2>&1 &
```

---

## ✅ VERIFICAR SERVIÇOS

```bash
/home/pc/Documentos/Erpopen/check_services.sh
```

---

## 🌐 ACESSAR O SISTEMA

**URL**: http://localhost:5173

**Login**:
- Email: `admin@erp.com`
- Senha: `admin123`

---

## 📊 CADASTROS DISPONÍVEIS

1. **Compras** → Fornecedores
2. **Materiais** → Cadastro de Materiais
3. **Financeiro** → Contas a Pagar
4. **Financeiro** → Contas a Receber
5. **Usuários** (menu lateral)

---

## 🛑 PARAR SERVIÇOS

### Parar Frontend
```bash
pkill -f "node.*vite"
```

### Parar Backend
```bash
pkill -f "python.*main.py"
```

### Parar Tudo
```bash
pkill -f "vite"
pkill -f "python.*main.py"
```

---

## 🔍 VER LOGS

### Backend
```bash
tail -f /tmp/backend.log
```

### Frontend
```bash
tail -f /tmp/frontend.log
```

---

## ✅ STATUS ATUAL

**Frontend**: ✅ Rodando (porta 5173)  
**Backend**: ✅ Rodando (porta 8000)

Acesse: http://localhost:5173
