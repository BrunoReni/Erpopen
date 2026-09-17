"""Tests for gerar conta a pagar from pedido de compra"""
import pytest
from app.models_modules import (
    Fornecedor, PedidoCompra, ItemPedidoCompra, ContaPagar
)
from datetime import datetime, timedelta


def _create_fornecedor(db_session):
    """Helper to create a fornecedor"""
    fornecedor = Fornecedor(
        codigo="FOR-0001", nome="Fornecedor Teste",
        razao_social="Fornecedor Teste LTDA",
        cnpj="12345678000190", ativo=1
    )
    db_session.add(fornecedor)
    db_session.commit()
    db_session.refresh(fornecedor)
    return fornecedor


def _create_pedido_aprovado(db_session, fornecedor_id):
    """Helper to create an approved purchase order"""
    pedido = PedidoCompra(
        numero="PC-2025-00001",
        fornecedor_id=fornecedor_id,
        data_entrega_prevista=datetime.utcnow() + timedelta(days=15),
        status="aprovado",
        valor_total=1500.0,
        observacoes="Pedido de teste"
    )
    db_session.add(pedido)
    db_session.commit()
    db_session.refresh(pedido)
    return pedido


def test_gerar_conta_pagar_sucesso(client, auth_headers, db_session):
    """Test successful generation of conta a pagar from pedido"""
    fornecedor = _create_fornecedor(db_session)
    pedido = _create_pedido_aprovado(db_session, fornecedor.id)

    response = client.post(
        f"/compras/pedidos/{pedido.id}/gerar-conta",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Conta a pagar gerada com sucesso"
    assert data["conta_pagar_id"] is not None
    assert data["valor"] == 1500.0

    # Verify conta was created in DB
    conta = db_session.query(ContaPagar).filter(
        ContaPagar.pedido_compra_id == pedido.id
    ).first()
    assert conta is not None
    assert conta.valor_original == 1500.0
    assert conta.fornecedor_id == fornecedor.id

    # Verify pedido status changed
    db_session.refresh(pedido)
    assert pedido.status.value == "recebido"


def test_gerar_conta_pedido_nao_aprovado(client, auth_headers, db_session):
    """Test cannot generate conta from non-approved pedido"""
    fornecedor = _create_fornecedor(db_session)
    pedido = PedidoCompra(
        numero="PC-2025-00002",
        fornecedor_id=fornecedor.id,
        status="solicitado",
        valor_total=500.0,
    )
    db_session.add(pedido)
    db_session.commit()
    db_session.refresh(pedido)

    response = client.post(
        f"/compras/pedidos/{pedido.id}/gerar-conta",
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "aprovados" in response.json()["detail"]


def test_gerar_conta_duplicada(client, auth_headers, db_session):
    """Test cannot generate duplicate conta for same pedido"""
    fornecedor = _create_fornecedor(db_session)
    pedido = _create_pedido_aprovado(db_session, fornecedor.id)

    # First call - should succeed
    response = client.post(
        f"/compras/pedidos/{pedido.id}/gerar-conta",
        headers=auth_headers
    )
    assert response.status_code == 200

    # Reset pedido status for second attempt (simulate trying again)
    pedido.status = "aprovado"
    db_session.commit()

    # Second call - should fail (duplicate)
    response = client.post(
        f"/compras/pedidos/{pedido.id}/gerar-conta",
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Já existe" in response.json()["detail"]


def test_gerar_conta_pedido_inexistente(client, auth_headers):
    """Test gerar conta for non-existent pedido"""
    response = client.post(
        "/compras/pedidos/99999/gerar-conta",
        headers=auth_headers
    )
    assert response.status_code == 404
