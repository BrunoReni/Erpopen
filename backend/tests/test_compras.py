"""Tests for compras module"""
import pytest
from app.models_modules import Fornecedor


def test_list_fornecedores_empty(client, auth_headers):
    """Test listing fornecedores when empty"""
    response = client.get("/compras/fornecedores", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_fornecedor(client, auth_headers):
    """Test creating fornecedor"""
    fornecedor_data = {
        "nome": "Fornecedor Test",
        "razao_social": "Fornecedor Test LTDA",
        "cnpj": "12345678000190",
        "email": "fornecedor@test.com",
        "telefone": "1133334444",
        "ativo": 1
    }
    
    response = client.post(
        "/compras/fornecedores",
        json=fornecedor_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Fornecedor Test"
    assert data["codigo"].startswith("FOR-")


def test_get_fornecedor_by_id(client, auth_headers, db_session):
    """Test getting fornecedor by ID"""
    fornecedor = Fornecedor(
        codigo="FOR-0001",
        nome="Test Fornecedor",
        razao_social="Test Fornecedor LTDA",
        cnpj="12345678000190",
        ativo=1
    )
    db_session.add(fornecedor)
    db_session.commit()
    db_session.refresh(fornecedor)
    
    response = client.get(f"/compras/fornecedores/{fornecedor.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == fornecedor.id
    assert data["codigo"] == "FOR-0001"


def test_update_fornecedor(client, auth_headers, db_session):
    """Test updating fornecedor"""
    fornecedor = Fornecedor(
        codigo="FOR-0001",
        nome="Old Name",
        razao_social="Old Name LTDA",
        cnpj="12345678000190",
        ativo=1
    )
    db_session.add(fornecedor)
    db_session.commit()
    db_session.refresh(fornecedor)
    
    update_data = {
        "nome": "New Name",
        "razao_social": "New Name LTDA",
        "cnpj": "12345678000190",
        "ativo": 1
    }
    
    response = client.put(
        f"/compras/fornecedores/{fornecedor.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "New Name"


def test_delete_fornecedor(client, auth_headers, db_session):
    """Test deleting fornecedor"""
    fornecedor = Fornecedor(
        codigo="FOR-0001",
        nome="Test Fornecedor",
        razao_social="Test LTDA",
        cnpj="12345678000190",
        ativo=1
    )
    db_session.add(fornecedor)
    db_session.commit()
    db_session.refresh(fornecedor)
    
    response = client.delete(f"/compras/fornecedores/{fornecedor.id}", headers=auth_headers)
    assert response.status_code == 200
    
    response = client.get(f"/compras/fornecedores/{fornecedor.id}", headers=auth_headers)
    assert response.status_code == 404
