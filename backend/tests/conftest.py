"""Pytest configuration and fixtures"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.models import User, Role, Permission
from app.models_modules import (
    Fornecedor, Material, Cliente, ContaPagar, ContaReceber,
    ContaBancaria, CentroCusto, UnidadeMedida, LocalEstoque
)
from app.security import get_password_hash
from main import app


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with dependency injection"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """Create admin user with all permissions"""
    # Create permissions
    permissions = [
        Permission(module="users", action="read"),
        Permission(module="users", action="create"),
        Permission(module="users", action="update"),
        Permission(module="users", action="delete"),
        Permission(module="compras", action="read"),
        Permission(module="compras", action="create"),
        Permission(module="compras", action="update"),
        Permission(module="compras", action="delete"),
        Permission(module="financeiro", action="read"),
        Permission(module="financeiro", action="create"),
        Permission(module="financeiro", action="update"),
        Permission(module="financeiro", action="delete"),
        Permission(module="materiais", action="read"),
        Permission(module="materiais", action="create"),
        Permission(module="materiais", action="update"),
        Permission(module="materiais", action="delete"),
        Permission(module="vendas", action="read"),
        Permission(module="vendas", action="create"),
        Permission(module="vendas", action="update"),
        Permission(module="vendas", action="delete"),
        Permission(module="dashboard", action="read"),
    ]
    
    for perm in permissions:
        db_session.add(perm)
    db_session.commit()
    
    # Create admin role
    admin_role = Role(name="admin", description="Administrator")
    admin_role.permissions = permissions
    db_session.add(admin_role)
    db_session.commit()
    
    # Create admin user
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin Test",
        is_active=True
    )
    user.roles = [admin_role]
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def auth_headers(client, admin_user):
    """Get authentication headers with valid token"""
    response = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "admin123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
