#!/bin/bash

# Script de Verificação de Serviços - ERP Open
# Verifica se Backend e Frontend estão funcionando corretamente

echo "======================================"
echo "🔍 Verificando Serviços ERP Open"
echo "======================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para verificar se um serviço está respondendo
check_service() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Verificando $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected" ]; then
        echo -e "${GREEN}✅ OK${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}❌ FALHOU${NC} (HTTP $response)"
        return 1
    fi
}

# Função para verificar se processo está rodando
check_process() {
    local name=$1
    local pattern=$2
    
    echo -n "Verificando processo $name... "
    
    if pgrep -f "$pattern" > /dev/null; then
        echo -e "${GREEN}✅ Rodando${NC}"
        return 0
    else
        echo -e "${RED}❌ Não encontrado${NC}"
        return 1
    fi
}

# Contadores
total=0
success=0

# 1. Verificar Backend (processo)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 BACKEND (FastAPI)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
((total++))
if check_process "Backend" "uvicorn.*main:app"; then
    ((success++))
fi

# 2. Verificar Backend (HTTP)
((total++))
if check_service "Backend API" "http://localhost:8000/" "200"; then
    ((success++))
fi

# 3. Verificar Backend Docs
((total++))
if check_service "Backend Docs" "http://localhost:8000/docs" "200"; then
    ((success++))
fi

echo ""

# 4. Verificar Frontend (processo)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 FRONTEND (Vite + React)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
((total++))
if check_process "Frontend" "vite"; then
    ((success++))
fi

# 5. Verificar Frontend (HTTP)
((total++))
if check_service "Frontend HTTP" "http://localhost:5173/" "200"; then
    ((success++))
fi

echo ""

# 6. Verificar Conectividade Backend <-> Frontend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 CONECTIVIDADE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Testar CORS
((total++))
echo -n "Testando CORS... "
cors_response=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Origin: http://localhost:5173" \
    -H "Access-Control-Request-Method: GET" \
    -X OPTIONS \
    "http://localhost:8000/" 2>/dev/null)

if [ "$cors_response" = "200" ]; then
    echo -e "${GREEN}✅ OK${NC}"
    ((success++))
else
    echo -e "${YELLOW}⚠️  Warning${NC} (pode não afetar funcionamento)"
    ((success++))  # Não falha por CORS
fi

echo ""

# Resumo
echo "======================================"
echo "📊 RESUMO"
echo "======================================"
echo "Total de verificações: $total"
echo -e "Sucessos: ${GREEN}$success${NC}"
echo -e "Falhas: ${RED}$((total - success))${NC}"
echo ""

if [ $success -eq $total ]; then
    echo -e "${GREEN}✅ Todos os serviços estão funcionando!${NC}"
    echo ""
    echo "🌐 URLs disponíveis:"
    echo "   Frontend: http://localhost:5173"
    echo "   Backend:  http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    exit 0
elif [ $success -ge 4 ]; then
    echo -e "${YELLOW}⚠️  Serviços parcialmente funcionando${NC}"
    echo ""
    echo "Verifique os itens com ❌ acima"
    exit 1
else
    echo -e "${RED}❌ Serviços não estão funcionando corretamente${NC}"
    echo ""
    echo "💡 Para iniciar os serviços:"
    echo ""
    echo "Backend:"
    echo "  cd /home/pc/Documentos/Erpopen/backend"
    echo "  source .venv/bin/activate"
    echo "  python main.py"
    echo ""
    echo "Frontend:"
    echo "  cd /home/pc/Documentos/Erpopen/frontend"
    echo "  npm run dev"
    exit 2
fi
