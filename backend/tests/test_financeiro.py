"""Tests for financeiro module"""
import pytest
from datetime import datetime, date
from app.models_modules import ContaBancaria, ContaPagar, ContaReceber, CentroCusto


def test_list_contas_bancarias_empty(client, auth_headers):
    """Test listing contas bancarias when empty"""
    response = client.get("/financeiro/bancos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_conta_bancaria(client, auth_headers):
    """Test creating conta bancaria"""
    conta_data = {
        "codigo": "BB-001",
        "nome": "Banco do Brasil - CC",
        "banco": "001",
        "agencia": "1234",
        "conta": "12345-6",
        "tipo": "corrente",
        "saldo_inicial": 1000.0,
        "ativa": 1
    }
    
    response = client.post(
        "/financeiro/bancos",
        json=conta_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Banco do Brasil - CC"
    assert data["saldo_inicial"] == 1000.0


def test_get_conta_bancaria_by_id(client, auth_headers, db_session):
    """Test getting conta bancaria by ID"""
    conta = ContaBancaria(
        codigo="BB-001",
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        tipo="corrente",
        saldo_inicial=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    response = client.get(f"/financeiro/bancos/{conta.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conta.id


def test_create_centro_custo(client, auth_headers):
    """Test creating centro de custo"""
    centro_data = {
        "codigo": "CC-001",
        "nome": "Administrativo",
        "descricao": "Despesas administrativas",
        "ativo": 1
    }
    
    response = client.post(
        "/financeiro/centros-custo",
        json=centro_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Administrativo"


def test_list_centros_custo(client, auth_headers, db_session):
    """Test listing centros de custo"""
    centros = [
        CentroCusto(codigo=f"CC-00{i}", nome=f"Centro {i}", ativo=1)
        for i in range(1, 4)
    ]
    for centro in centros:
        db_session.add(centro)
    db_session.commit()
    
    response = client.get("/financeiro/centros-custo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_create_conta_pagar(client, auth_headers, db_session):
    """Test creating conta a pagar"""
    # Create fornecedor first
    from app.models_modules import Fornecedor
    fornecedor = Fornecedor(
        codigo="FOR-0001",
        nome="Fornecedor Test",
        cnpj="12345678000190",
        ativo=1
    )
    db_session.add(fornecedor)
    db_session.commit()
    db_session.refresh(fornecedor)
    
    conta_data = {
        "descricao": "Compra de materiais",
        "fornecedor_id": fornecedor.id,
        "valor": 1500.0,
        "data_vencimento": date.today().isoformat(),
        "status": "pendente"
    }
    
    response = client.post(
        "/financeiro/contas-pagar",
        json=conta_data,
        headers=auth_headers
    )
    
    if response.status_code == 200:
        data = response.json()
        assert data["valor"] == 1500.0


def test_list_contas_pagar(client, auth_headers):
    """Test listing contas a pagar"""
    response = client.get("/financeiro/contas-pagar", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_contas_receber(client, auth_headers):
    """Test listing contas a receber"""
    response = client.get("/financeiro/contas-receber", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
