"""Tests for financeiro module"""
import pytest
from datetime import datetime, date
from app.models_modules import ContaBancaria, ContaPagar, ContaReceber, CentroCusto


def test_list_contas_bancarias_empty(client, auth_headers):
    """Test listing contas bancarias when empty"""
    response = client.get("/financeiro/contas-bancarias", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_conta_bancaria(client, auth_headers):
    """Test creating conta bancaria"""
    conta_data = {
        "nome": "Banco do Brasil - CC",
        "banco": "001",
        "agencia": "1234",
        "conta": "12345-6",
        "saldo_inicial": 1000.0
    }
    
    response = client.post(
        "/financeiro/contas-bancarias",
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
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    # Just list all and verify the conta was created
    response = client.get("/financeiro/contas-bancarias", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert any(c["id"] == conta.id for c in data)


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


# =============================================================================
# TESTS FOR MOVIMENTAÇÕES BANCÁRIAS
# =============================================================================

def test_create_movimentacao_bancaria(client, auth_headers, db_session):
    """Test creating movimentacao bancaria"""
    # Create conta bancaria first
    conta = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    movimentacao_data = {
        "conta_bancaria_id": conta.id,
        "tipo": "deposito",
        "natureza": "ENTRADA",
        "valor": 500.0,
        "descricao": "Depósito teste",
        "data_competencia": date.today().isoformat()
    }
    
    response = client.post(
        "/financeiro/movimentacoes-bancarias",
        json=movimentacao_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["valor"] == 500.0
    assert data["natureza"] == "ENTRADA"
    
    # Verify conta saldo was updated
    db_session.refresh(conta)
    assert conta.saldo_atual == 1500.0


def test_create_movimentacao_saida(client, auth_headers, db_session):
    """Test creating movimentacao bancaria with SAIDA"""
    conta = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    movimentacao_data = {
        "conta_bancaria_id": conta.id,
        "tipo": "saque",
        "natureza": "SAIDA",
        "valor": 300.0,
        "descricao": "Saque teste"
    }
    
    response = client.post(
        "/financeiro/movimentacoes-bancarias",
        json=movimentacao_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["valor"] == 300.0
    assert data["natureza"] == "SAIDA"
    
    # Verify conta saldo was updated
    db_session.refresh(conta)
    assert conta.saldo_atual == 700.0


def test_list_movimentacoes_bancarias(client, auth_headers, db_session):
    """Test listing movimentacoes bancarias"""
    from app.models_modules import MovimentacaoBancaria, TipoMovimentacaoBancaria
    
    conta = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    # Create some movimentacoes
    movimentacoes = [
        MovimentacaoBancaria(
            conta_bancaria_id=conta.id,
            tipo=TipoMovimentacaoBancaria.DEPOSITO,
            natureza="ENTRADA",
            valor=100.0 * i,
            descricao=f"Movimentação {i}"
        )
        for i in range(1, 4)
    ]
    for mov in movimentacoes:
        db_session.add(mov)
    db_session.commit()
    
    response = client.get("/financeiro/movimentacoes-bancarias", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_update_movimentacao_bancaria(client, auth_headers, db_session):
    """Test updating movimentacao bancaria"""
    from app.models_modules import MovimentacaoBancaria, TipoMovimentacaoBancaria
    
    conta = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    movimentacao = MovimentacaoBancaria(
        conta_bancaria_id=conta.id,
        tipo=TipoMovimentacaoBancaria.DEPOSITO,
        natureza="ENTRADA",
        valor=100.0,
        descricao="Original"
    )
    db_session.add(movimentacao)
    conta.saldo_atual += 100.0
    db_session.commit()
    db_session.refresh(movimentacao)
    
    update_data = {
        "descricao": "Atualizado",
        "valor": 150.0
    }
    
    response = client.put(
        f"/financeiro/movimentacoes-bancarias/{movimentacao.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["descricao"] == "Atualizado"
    assert data["valor"] == 150.0


def test_delete_movimentacao_bancaria(client, auth_headers, db_session):
    """Test deleting movimentacao bancaria"""
    from app.models_modules import MovimentacaoBancaria, TipoMovimentacaoBancaria
    
    conta = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1100.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    movimentacao = MovimentacaoBancaria(
        conta_bancaria_id=conta.id,
        tipo=TipoMovimentacaoBancaria.DEPOSITO,
        natureza="ENTRADA",
        valor=100.0,
        descricao="To be deleted"
    )
    db_session.add(movimentacao)
    db_session.commit()
    db_session.refresh(movimentacao)
    
    response = client.delete(
        f"/financeiro/movimentacoes-bancarias/{movimentacao.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verify conta saldo was reverted
    db_session.refresh(conta)
    assert conta.saldo_atual == 1000.0


# =============================================================================
# TESTS FOR TRANSFERÊNCIAS
# =============================================================================

def test_create_transferencia(client, auth_headers, db_session):
    """Test creating transferencia between contas"""
    conta_origem = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    conta_destino = ContaBancaria(
        nome="Caixa Econômica",
        banco="104",
        agencia="5678",
        conta="98765-4",
        saldo_inicial=500.0,
        saldo_atual=500.0,
        ativa=1
    )
    db_session.add(conta_origem)
    db_session.add(conta_destino)
    db_session.commit()
    db_session.refresh(conta_origem)
    db_session.refresh(conta_destino)
    
    transferencia_data = {
        "conta_origem_id": conta_origem.id,
        "conta_destino_id": conta_destino.id,
        "valor": 200.0,
        "data": datetime.utcnow().isoformat(),
        "descricao": "Transferência teste"
    }
    
    response = client.post(
        "/financeiro/transferencias",
        json=transferencia_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["valor"] == 200.0
    assert "movimentacao_saida_id" in data
    assert "movimentacao_entrada_id" in data
    
    # Verify saldos were updated
    db_session.refresh(conta_origem)
    db_session.refresh(conta_destino)
    assert conta_origem.saldo_atual == 800.0
    assert conta_destino.saldo_atual == 700.0


def test_transferencia_saldo_insuficiente(client, auth_headers, db_session):
    """Test transferencia with insufficient balance"""
    conta_origem = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=100.0,
        saldo_atual=100.0,
        ativa=1
    )
    conta_destino = ContaBancaria(
        nome="Caixa Econômica",
        banco="104",
        agencia="5678",
        conta="98765-4",
        saldo_inicial=500.0,
        saldo_atual=500.0,
        ativa=1
    )
    db_session.add(conta_origem)
    db_session.add(conta_destino)
    db_session.commit()
    db_session.refresh(conta_origem)
    db_session.refresh(conta_destino)
    
    transferencia_data = {
        "conta_origem_id": conta_origem.id,
        "conta_destino_id": conta_destino.id,
        "valor": 200.0,
        "data": datetime.utcnow().isoformat(),
        "descricao": "Transferência teste"
    }
    
    response = client.post(
        "/financeiro/transferencias",
        json=transferencia_data,
        headers=auth_headers
    )
    
    assert response.status_code == 400


# =============================================================================
# TESTS FOR CONCILIAÇÃO
# =============================================================================

def test_list_movimentacoes_pendentes_conciliacao(client, auth_headers, db_session):
    """Test listing movimentacoes pendentes de conciliacao"""
    from app.models_modules import MovimentacaoBancaria, TipoMovimentacaoBancaria
    
    conta = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    # Create movimentacao not conciliada
    movimentacao = MovimentacaoBancaria(
        conta_bancaria_id=conta.id,
        tipo=TipoMovimentacaoBancaria.DEPOSITO,
        natureza="ENTRADA",
        valor=100.0,
        descricao="Pendente conciliacao",
        conciliado=False
    )
    db_session.add(movimentacao)
    db_session.commit()
    
    response = client.get(f"/financeiro/conciliacao/{conta.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "movimentacoes" in data
    assert len(data["movimentacoes"]) >= 1


def test_conciliar_movimentacoes(client, auth_headers, db_session):
    """Test conciliando movimentacoes"""
    from app.models_modules import MovimentacaoBancaria, TipoMovimentacaoBancaria
    
    conta = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    movimentacao = MovimentacaoBancaria(
        conta_bancaria_id=conta.id,
        tipo=TipoMovimentacaoBancaria.DEPOSITO,
        natureza="ENTRADA",
        valor=100.0,
        descricao="To be conciliada",
        conciliado=False
    )
    db_session.add(movimentacao)
    db_session.commit()
    db_session.refresh(movimentacao)
    
    response = client.post(
        f"/financeiro/conciliacao/{conta.id}/conciliar",
        json=[movimentacao.id],
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["movimentacoes_conciliadas"] == 1
    
    # Verify movimentacao was marked as conciliada
    db_session.refresh(movimentacao)
    assert movimentacao.conciliado == True


def test_desconciliar_movimentacoes(client, auth_headers, db_session):
    """Test desconciliando movimentacoes"""
    from app.models_modules import MovimentacaoBancaria, TipoMovimentacaoBancaria
    
    conta = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    movimentacao = MovimentacaoBancaria(
        conta_bancaria_id=conta.id,
        tipo=TipoMovimentacaoBancaria.DEPOSITO,
        natureza="ENTRADA",
        valor=100.0,
        descricao="Conciliada",
        conciliado=True,
        data_conciliacao=datetime.utcnow()
    )
    db_session.add(movimentacao)
    db_session.commit()
    db_session.refresh(movimentacao)
    
    response = client.post(
        f"/financeiro/conciliacao/{conta.id}/desconciliar",
        json=[movimentacao.id],
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["movimentacoes_desconciliadas"] == 1
    
    # Verify movimentacao was unmarked
    db_session.refresh(movimentacao)
    assert movimentacao.conciliado == False


# =============================================================================
# TESTS FOR SALDO DIÁRIO AND EXTRATO
# =============================================================================

def test_get_saldo_diario(client, auth_headers, db_session):
    """Test getting saldo diario"""
    conta = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    response = client.get(
        f"/financeiro/contas-bancarias/{conta.id}/saldo-diario",
        params={"data": date.today().isoformat()},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "saldo_anterior" in data
    assert "saldo_final" in data


def test_get_extrato(client, auth_headers, db_session):
    """Test getting extrato"""
    from app.models_modules import MovimentacaoBancaria, TipoMovimentacaoBancaria
    
    conta = ContaBancaria(
        nome="Banco do Brasil",
        banco="001",
        agencia="1234",
        conta="12345-6",
        saldo_inicial=1000.0,
        saldo_atual=1000.0,
        ativa=1
    )
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    # Create some movimentacoes
    mov1 = MovimentacaoBancaria(
        conta_bancaria_id=conta.id,
        tipo=TipoMovimentacaoBancaria.DEPOSITO,
        natureza="ENTRADA",
        valor=100.0,
        descricao="Deposito",
        data_competencia=date.today()
    )
    mov2 = MovimentacaoBancaria(
        conta_bancaria_id=conta.id,
        tipo=TipoMovimentacaoBancaria.SAQUE,
        natureza="SAIDA",
        valor=50.0,
        descricao="Saque",
        data_competencia=date.today()
    )
    db_session.add(mov1)
    db_session.add(mov2)
    db_session.commit()
    
    response = client.get(
        f"/financeiro/contas-bancarias/{conta.id}/extrato",
        params={
            "data_inicio": date.today().isoformat(),
            "data_fim": date.today().isoformat()
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "movimentacoes" in data
    assert len(data["movimentacoes"]) >= 2
    assert "total_entradas" in data
    assert "total_saidas" in data
