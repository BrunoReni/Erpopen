"""Tests for dashboard module"""
import pytest
from app.models_modules import (
    Fornecedor, Cliente, Material, PedidoVenda, ItemPedidoVenda,
    PedidoCompra, ContaPagar, ContaReceber, LocalEstoque
)
from datetime import datetime, timedelta


def test_dashboard_stats_empty(client, auth_headers):
    """Test dashboard stats with empty database"""
    response = client.get("/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert "resumo" in data
    assert "vendas" in data
    assert "compras" in data
    assert "financeiro" in data
    assert "estoque" in data
    assert "pedidos_recentes" in data

    # With empty db (except admin user), counts should be minimal
    assert data["resumo"]["total_clientes"] == 0
    assert data["resumo"]["total_fornecedores"] == 0
    assert data["resumo"]["total_materiais"] == 0
    assert data["resumo"]["total_usuarios"] >= 1  # admin user exists


def test_dashboard_stats_with_data(client, auth_headers, db_session):
    """Test dashboard stats with real data"""
    # Create fornecedores
    for i in range(3):
        db_session.add(Fornecedor(
            codigo=f"FOR-{i+1:04d}", nome=f"Fornecedor {i+1}",
            razao_social=f"Fornecedor {i+1} LTDA", cnpj=f"1234567800{i:04d}", ativo=1
        ))

    # Create clientes
    for i in range(5):
        db_session.add(Cliente(
            codigo=f"CLI-{i+1:04d}", nome=f"Cliente {i+1}",
            tipo_pessoa="PJ", cpf_cnpj=f"9876543200{i:04d}", ativo=1
        ))

    # Create materiais
    for i in range(4):
        db_session.add(Material(
            codigo=f"MAT-{i+1:04d}", nome=f"Material {i+1}",
            unidade_medida="UN", estoque_atual=10.0, estoque_minimo=5.0
        ))

    db_session.commit()

    response = client.get("/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["resumo"]["total_clientes"] == 5
    assert data["resumo"]["total_fornecedores"] == 3
    assert data["resumo"]["total_materiais"] == 4


def test_dashboard_stats_unauthorized(client):
    """Test dashboard stats without authentication"""
    response = client.get("/dashboard/stats")
    assert response.status_code == 401


def test_dashboard_financeiro_stats(client, auth_headers, db_session):
    """Test dashboard financial statistics"""
    # Create requisite data
    fornecedor = Fornecedor(
        codigo="FOR-0001", nome="Fornecedor 1",
        razao_social="Fornecedor LTDA", cnpj="12345678000100", ativo=1
    )
    db_session.add(fornecedor)

    cliente = Cliente(
        codigo="CLI-0001", nome="Cliente 1",
        tipo_pessoa="PJ", cpf_cnpj="98765432000100", ativo=1
    )
    db_session.add(cliente)
    db_session.commit()

    # Create contas a pagar
    db_session.add(ContaPagar(
        descricao="Conta Teste 1", fornecedor_id=fornecedor.id,
        data_vencimento=datetime.utcnow() + timedelta(days=30),
        valor_original=1000.0, valor_pago=0.0, status="pendente"
    ))
    db_session.add(ContaPagar(
        descricao="Conta Vencida", fornecedor_id=fornecedor.id,
        data_vencimento=datetime.utcnow() - timedelta(days=5),
        valor_original=500.0, valor_pago=0.0, status="pendente"
    ))

    # Create contas a receber
    db_session.add(ContaReceber(
        descricao="Receber Teste 1", cliente_id=cliente.id,
        data_vencimento=datetime.utcnow() + timedelta(days=15),
        valor_original=2000.0, valor_recebido=0.0, status="pendente"
    ))
    db_session.commit()

    response = client.get("/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["financeiro"]["contas_pagar_pendentes"] == 2
    assert data["financeiro"]["valor_pagar_pendente"] == 1500.0
    assert data["financeiro"]["contas_receber_pendentes"] == 1
    assert data["financeiro"]["valor_receber_pendente"] == 2000.0
    assert data["financeiro"]["contas_pagar_vencidas"] == 1
