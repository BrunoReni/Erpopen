from sqlalchemy.orm import Session
from typing import List, Tuple
from app import models
from app.security import get_password_hash, verify_password


def create_user(db: Session, email: str, password: str, full_name: str = None):
    user = models.User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign default 'user' role if exists
    default_role = db.query(models.Role).filter(models.Role.name == "user").first()
    if default_role:
        user.roles.append(default_role)
        db.commit()
        db.refresh(user)
    
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_roles_and_permissions(db: Session, user_id: int) -> Tuple[List[str], List[str]]:
    """Returns tuple of (role_names, permission_strings)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return [], []
    
    role_names = [role.name for role in user.roles]
    permissions_set = set()
    
    for role in user.roles:
        for perm in role.permissions:
            permissions_set.add(f"{perm.module}:{perm.action}")
    
    return role_names, list(permissions_set)


def create_permission(db: Session, module: str, action: str, description: str = None):
    perm = models.Permission(module=module, action=action, description=description)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


def create_role(db: Session, name: str, description: str = None, permission_ids: List[int] = None):
    role = models.Role(name=name, description=description)
    db.add(role)
    db.flush()
    
    if permission_ids:
        permissions = db.query(models.Permission).filter(models.Permission.id.in_(permission_ids)).all()
        role.permissions.extend(permissions)
    
    db.commit()
    db.refresh(role)
    return role


def init_default_permissions_and_roles(db: Session):
    """Initialize default permissions and roles for the ERP system"""
    
    # Check if already initialized
    if db.query(models.Permission).count() > 0:
        return
    
    # Define modules and their actions
    modules = {
        "users": ["create", "read", "update", "delete"],
        "roles": ["create", "read", "update", "delete"],
        "dashboard": ["read"],
        "compras": ["create", "read", "update", "delete"],
        "fornecedores": ["create", "read", "update", "delete"],
        "financeiro": ["create", "read", "update", "delete"],
        "materiais": ["create", "read", "update", "delete"],
        "reports": ["read", "export"],
    }
    
    # Create permissions
    created_permissions = {}
    for module, actions in modules.items():
        for action in actions:
            perm = create_permission(db, module, action, f"Permission to {action} {module}")
            created_permissions[f"{module}:{action}"] = perm.id
    
    # Create default roles
    # Admin role - all permissions
    admin_perms = list(created_permissions.values())
    create_role(db, "admin", "Administrator with full access", admin_perms)
    
    # Manager role - most permissions except critical admin functions
    manager_perms = [
        pid for key, pid in created_permissions.items() 
        if not key.startswith("users:") and not key.startswith("roles:")
    ] + [created_permissions.get("users:read")]
    create_role(db, "manager", "Manager with operational access", manager_perms)
    
    # Comprador role - purchasing and materials
    comprador_perms = [
        created_permissions.get("dashboard:read"),
        created_permissions.get("compras:create"),
        created_permissions.get("compras:read"),
        created_permissions.get("compras:update"),
        created_permissions.get("fornecedores:create"),
        created_permissions.get("fornecedores:read"),
        created_permissions.get("fornecedores:update"),
        created_permissions.get("materiais:read"),
    ]
    create_role(db, "comprador", "Purchasing agent with buying permissions", [p for p in comprador_perms if p])
    
    # Financeiro role - financial operations
    financeiro_perms = [
        created_permissions.get("dashboard:read"),
        created_permissions.get("financeiro:create"),
        created_permissions.get("financeiro:read"),
        created_permissions.get("financeiro:update"),
        created_permissions.get("compras:read"),
        created_permissions.get("fornecedores:read"),
        created_permissions.get("reports:read"),
        created_permissions.get("reports:export"),
    ]
    create_role(db, "financeiro", "Financial operations access", [p for p in financeiro_perms if p])
    
    # Almoxarife role - materials and inventory
    almoxarife_perms = [
        created_permissions.get("dashboard:read"),
        created_permissions.get("materiais:create"),
        created_permissions.get("materiais:read"),
        created_permissions.get("materiais:update"),
        created_permissions.get("compras:read"),
    ]
    create_role(db, "almoxarife", "Warehouse keeper with materials access", [p for p in almoxarife_perms if p])
    
    # User role - basic read access
    user_perms = [
        created_permissions.get("dashboard:read"),
        created_permissions.get("compras:read"),
        created_permissions.get("materiais:read"),
    ]
    create_role(db, "user", "Basic user with limited access", [p for p in user_perms if p])

