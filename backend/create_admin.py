#!/usr/bin/env python
"""Script para criar o usuário admin inicial"""

from app.db import SessionLocal, init_db
from app.models import User, Role
from app.security import get_password_hash

def create_admin_user():
    """Cria o usuário admin se não existir"""
    db = SessionLocal()
    
    try:
        # Verificar se já existe um admin
        existing_admin = db.query(User).filter(User.email == "admin@erp.com").first()
        
        if existing_admin:
            print("✅ Usuário admin já existe!")
            print(f"   Email: {existing_admin.email}")
            return
        
        # Buscar role admin
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        
        if not admin_role:
            print("❌ Role 'admin' não encontrada. Execute init_db() primeiro.")
            return
        
        # Criar usuário admin
        admin_user = User(
            email="admin@erp.com",
            full_name="Administrador",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        
        admin_user.roles.append(admin_role)
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Usuário admin criado com sucesso!")
        print(f"   Email: admin@erp.com")
        print(f"   Senha: admin123")
        print(f"   Roles: {[r.name for r in admin_user.roles]}")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🔧 Inicializando banco de dados...")
    init_db()
    print("✅ Banco de dados inicializado!")
    
    print("\n👤 Criando usuário admin...")
    create_admin_user()
    
    print("\n🎉 Setup concluído!")
