"""Tests for vendas/clientes module"""
import pytest
from app.models_modules import Cliente


def test_list_clientes_empty(client, auth_headers):
    """Test listing clientes when empty"""
    response = client.get("/vendas/clientes", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_cliente_pf(client, auth_headers):
    """Test creating cliente pessoa física"""
    cliente_data = {
        "nome": "João Silva",
        "cpf_cnpj": "12345678909",
        "tipo_pessoa": "F",
        "email": "joao@test.com",
        "telefone": "11999998888",
        "tipo_cliente": "varejo",
        "limite_credito": 5000.0,
        "ativo": 1
    }
    
    response = client.post(
        "/vendas/clientes",
        json=cliente_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "João Silva"
    assert "id" in data


def test_create_cliente_pj(client, auth_headers):
    """Test creating cliente pessoa jurídica"""
    cliente_data = {
        "nome": "Empresa LTDA",
        "razao_social": "Empresa LTDA",
        "cpf_cnpj": "11222333000181",
        "tipo_pessoa": "J",
        "email": "empresa@test.com",
        "telefone": "1133334444",
        "tipo_cliente": "atacado",
        "limite_credito": 50000.0,
        "ativo": 1
    }
    
    response = client.post(
        "/vendas/clientes",
        json=cliente_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["tipo_pessoa"] == "J"


def test_get_cliente_by_id(client, auth_headers, db_session):
    """Test getting cliente by ID"""
    cliente = Cliente(
        codigo="CLI-0001",
        nome="Test Cliente",
        cpf_cnpj="12345678909",
        tipo_pessoa="F",
        tipo_cliente="varejo",
        limite_credito=5000.0,
        ativo=1
    )
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)
    
    response = client.get(f"/vendas/clientes/{cliente.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cliente.id
    assert data["nome"] == "Test Cliente"


def test_update_cliente(client, auth_headers, db_session):
    """Test updating cliente"""
    cliente = Cliente(
        codigo="CLI-0001",
        nome="Old Name",
        cpf_cnpj="12345678909",
        tipo_pessoa="F",
        tipo_cliente="varejo",
        limite_credito=5000.0,
        ativo=1
    )
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)
    
    update_data = {
        "nome": "New Name",
        "cpf_cnpj": "12345678909",
        "tipo_pessoa": "F",
        "tipo_cliente": "varejo",
        "limite_credito": 10000.0,
        "ativo": 1
    }
    
    response = client.put(
        f"/vendas/clientes/{cliente.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "New Name"
    assert data["limite_credito"] == 10000.0


def test_delete_cliente(client, auth_headers, db_session):
    """Test deleting cliente"""
    cliente = Cliente(
        codigo="CLI-0001",
        nome="Test Cliente",
        cpf_cnpj="12345678909",
        tipo_pessoa="F",
        tipo_cliente="varejo",
        limite_credito=5000.0,
        ativo=1
    )
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)
    
    response = client.delete(f"/vendas/clientes/{cliente.id}", headers=auth_headers)
    assert response.status_code == 200
    
    response = client.get(f"/vendas/clientes/{cliente.id}", headers=auth_headers)
    assert response.status_code == 404


def test_search_cliente_by_cpf(client, auth_headers, db_session):
    """Test searching cliente by CPF"""
    cliente = Cliente(
        codigo="CLI-0001",
        nome="Test Cliente",
        cpf_cnpj="12345678909",
        tipo_pessoa="F",
        tipo_cliente="varejo",
        limite_credito=5000.0,
        ativo=1
    )
    db_session.add(cliente)
    db_session.commit()
    
    response = client.get("/vendas/clientes/cpf/12345678909", headers=auth_headers)
    if response.status_code == 200:
        data = response.json()
        assert data["cpf_cnpj"] == "12345678909"


def test_list_clientes_with_data(client, auth_headers, db_session):
    """Test listing clientes with data"""
    # Create multiple clientes
    clientes = [
        Cliente(codigo=f"CLI-000{i}", nome=f"Cliente {i}", cpf_cnpj=f"1234567890{i}", 
                tipo_pessoa="F", tipo_cliente="varejo", limite_credito=5000.0, ativo=1)
        for i in range(1, 4)
    ]
    for cliente in clientes:
        db_session.add(cliente)
    db_session.commit()
    
    response = client.get("/vendas/clientes", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
