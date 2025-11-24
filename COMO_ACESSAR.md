# 🚀 Como Acessar o Sistema ERPOpen

## ✅ Status dos Servidores

**Backend**: ✅ Rodando em http://localhost:8000  
**Frontend**: ✅ Rodando em http://localhost:5173

---

## 🔐 Credenciais de Acesso

```
URL: http://localhost:5173
Email: admin@erp.com
Senha: admin123
```

---

## 📝 Passo a Passo para Login

1. **Abra seu navegador** (Chrome, Firefox, Edge, etc.)

2. **Acesse a URL**:
   ```
   http://localhost:5173
   ```

3. **Faça o login** com:
   - **Email**: `admin@erp.com`
   - **Senha**: `admin123`

4. **Clique em "Entrar"**

5. Você será redirecionado para o **Dashboard** do sistema

---

## 🔧 Se os Servidores Não Estiverem Rodando

### Iniciar Backend
```bash
cd /home/pc/Documentos/Erpopen/backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Iniciar Frontend
```bash
cd /home/pc/Documentos/Erpopen/frontend
npm run dev
```

---

## 🎯 O Que Você Pode Fazer Após Login

### 📦 Módulo de Compras
- **Fornecedores**: Cadastre e gerencie fornecedores
- **Pedidos de Compra**: Crie pedidos com múltiplos itens

### 💰 Módulo Financeiro
- **Contas a Pagar**: Gerencie despesas e pagamentos
- **Contas a Receber**: Controle recebimentos
- **Contas Bancárias**: Configure suas contas bancárias
- **Centros de Custo**: Organize despesas por centro de custo

### 📊 Módulo de Materiais
- **Cadastro de Materiais**: Gerencie produtos e materiais
- **Movimentação de Estoque**: Registre entradas, saídas e ajustes

### 👥 Módulo de Sistema
- **Usuários**: Gerencie usuários e permissões

---

## ✅ Verificação Rápida

### Testar Backend
```bash
curl http://localhost:8000/
```

Deve retornar:
```json
{
  "status": "ok",
  "service": "ERP Open Backend",
  "version": "1.0.0",
  ...
}
```

### Testar Frontend
Abra no navegador: http://localhost:5173

Deve aparecer a **tela de login**

### Testar Login (via API)
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@erp.com&password=admin123"
```

Deve retornar um **access_token**

---

## 🐛 Resolução de Problemas

### Problema: "Credenciais inválidas"

**Solução 1**: Verifique se está digitando corretamente:
- Email: `admin@erp.com` (tudo minúsculo, sem espaços)
- Senha: `admin123` (sem espaços)

**Solução 2**: Recrie o usuário admin:
```bash
cd /home/pc/Documentos/Erpopen/backend
source .venv/bin/activate
python create_admin.py
```

**Solução 3**: Verifique se o backend está rodando:
```bash
curl http://localhost:8000/
```

### Problema: "Cannot connect to server"

**Causa**: Backend não está rodando

**Solução**: Inicie o backend:
```bash
cd /home/pc/Documentos/Erpopen/backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Problema: Página não carrega (frontend)

**Causa**: Frontend não está rodando

**Solução**: Inicie o frontend:
```bash
cd /home/pc/Documentos/Erpopen/frontend
npm run dev
```

---

## 📱 Acesso pelos Outros Dispositivos na Rede

Se quiser acessar de outro computador/celular na mesma rede:

1. Descubra o IP da sua máquina:
```bash
hostname -I | awk '{print $1}'
```

2. Acesse pelo IP (exemplo):
```
http://192.168.1.100:5173
```

---

## 🎉 Tudo Funcionando?

Se conseguiu fazer login, você está pronto para usar o sistema!

**Explore os módulos:**
- Clique no menu lateral para navegar
- Cada módulo tem um índice com cards clicáveis
- Use os botões "Novo" para criar registros
- Use os ícones de lápis para editar
- Use os ícones de lixeira para excluir

---

**Última Atualização**: 2025-11-24  
**Versão do Sistema**: 1.0.0
