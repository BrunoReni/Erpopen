#!/bin/bash
# ERP Open - Setup Script
set -e
echo "🚀 Setting up ERP Open..."
cd backend
[ ! -f .env ] && cp .env.example .env && echo "✅ Backend .env created"
cd ../frontend  
[ ! -f .env ] && cp .env.example .env && echo "✅ Frontend .env created"
cd ..
echo "✅ Setup complete! Edit .env files and run: ./check_services.sh"
