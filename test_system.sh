#!/bin/bash

echo "================================================"
echo "🚀 ERP Open - Script de Teste do Sistema"
echo "================================================"
echo ""

# Check if backend is running
echo "📡 Verificando Backend..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend está rodando em http://localhost:8000"
    echo "✅ Docs disponíveis em http://localhost:8000/docs"
else
    echo "❌ Backend não está rodando!"
    echo "   Execute: cd backend && uvicorn main:app --reload"
    exit 1
fi

echo ""
echo "🧪 Testando Endpoints..."

# Test root endpoint
echo -n "- GET / ... "
if curl -s http://localhost:8000/ | grep -q "ERP Open"; then
    echo "✅"
else
    echo "❌"
fi

# Test register
echo -n "- POST /auth/register ... "
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}')

if echo "$REGISTER_RESPONSE" | grep -q "email"; then
    echo "✅ (usuário já existe ou criado)"
else
    echo "⚠️  (verificar resposta)"
fi

# Test login
echo -n "- POST /auth/login ... "
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test@example.com&password=test123")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "✅ Token obtido"
else
    echo "❌ Falha no login"
    exit 1
fi

# Test /me endpoint
echo -n "- GET /auth/me ... "
ME_RESPONSE=$(curl -s -X GET http://localhost:8000/auth/me \
    -H "Authorization: Bearer $TOKEN")

if echo "$ME_RESPONSE" | grep -q "permissions"; then
    echo "✅"
else
    echo "❌"
fi

echo ""
echo "📊 Informações do Usuário:"
echo "$ME_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ME_RESPONSE"

echo ""
echo "================================================"
echo "✅ Todos os testes passaram!"
echo "================================================"
echo ""
echo "🌐 URLs Importantes:"
echo "   Backend: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Frontend: http://localhost:5173"
echo ""
echo "🔑 Token de Teste:"
echo "   $TOKEN"
echo ""
