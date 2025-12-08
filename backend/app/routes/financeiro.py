from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from app.db import get_session
from app.dependencies import require_permission
from app.schemas_modules import (
    ContaBancariaCreate, ContaBancariaRead,
    CentroCustoCreate, CentroCustoRead,
    ContaPagarCreate, ContaPagarRead, ContaPagarUpdate,
    ContaReceberCreate, ContaReceberRead, ContaReceberUpdate,
    MovimentacaoBancariaCreate, MovimentacaoBancariaRead, MovimentacaoBancariaUpdate,
    SaldoDiarioRead, TransferenciaCreate
)
from app.models_modules import (
    ContaBancaria, CentroCusto, ContaPagar, ContaReceber,
    MovimentacaoBancaria, SaldoDiario, TipoMovimentacaoBancaria
)

router = APIRouter()


# =============================================================================
# CONTAS BANCÁRIAS
# =============================================================================

@router.get("/contas-bancarias", response_model=List[ContaBancariaRead])
def list_contas_bancarias(
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Lista todas as contas bancárias"""
    return session.query(ContaBancaria).filter(ContaBancaria.ativa == 1).all()


@router.post("/contas-bancarias", response_model=ContaBancariaRead)
def create_conta_bancaria(
    conta: ContaBancariaCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """Cria uma nova conta bancária"""
    db_conta = ContaBancaria(**conta.model_dump(), saldo_atual=conta.saldo_inicial)
    session.add(db_conta)
    session.commit()
    session.refresh(db_conta)
    return db_conta


@router.get("/contas-bancarias/{conta_id}/saldo-diario")
def get_saldo_data(
    conta_id: int,
    data: date = Query(...),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Retorna o saldo em uma data específica"""
    conta = session.query(ContaBancaria).filter(ContaBancaria.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    
    # Buscar saldo diário da data
    saldo_diario = session.query(SaldoDiario).filter(
        SaldoDiario.conta_bancaria_id == conta_id,
        SaldoDiario.data == data
    ).first()
    
    if saldo_diario:
        return {
            "conta_id": conta_id,
            "data": data,
            "saldo_anterior": saldo_diario.saldo_anterior,
            "total_entradas": saldo_diario.total_entradas,
            "total_saidas": saldo_diario.total_saidas,
            "saldo_final": saldo_diario.saldo_final
        }
    
    # Se não existir saldo diário registrado, calcular baseado nas movimentações
    # Obter saldo anterior (último saldo antes da data)
    ultimo_saldo = session.query(SaldoDiario).filter(
        SaldoDiario.conta_bancaria_id == conta_id,
        SaldoDiario.data < data
    ).order_by(SaldoDiario.data.desc()).first()
    
    saldo_anterior = ultimo_saldo.saldo_final if ultimo_saldo else conta.saldo_inicial
    
    # Calcular movimentações do dia
    movimentacoes_dia = session.query(MovimentacaoBancaria).filter(
        MovimentacaoBancaria.conta_bancaria_id == conta_id,
        MovimentacaoBancaria.data_competencia == data
    ).all()
    
    total_entradas = sum(m.valor for m in movimentacoes_dia if m.natureza == "ENTRADA")
    total_saidas = sum(m.valor for m in movimentacoes_dia if m.natureza == "SAIDA")
    saldo_final = saldo_anterior + total_entradas - total_saidas
    
    return {
        "conta_id": conta_id,
        "data": data,
        "saldo_anterior": saldo_anterior,
        "total_entradas": total_entradas,
        "total_saidas": total_saidas,
        "saldo_final": saldo_final
    }


@router.get("/contas-bancarias/{conta_id}/extrato")
def get_extrato(
    conta_id: int,
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Retorna o extrato da conta com movimentações do período"""
    conta = session.query(ContaBancaria).filter(ContaBancaria.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    
    # Buscar movimentações do período
    movimentacoes = session.query(MovimentacaoBancaria).filter(
        MovimentacaoBancaria.conta_bancaria_id == conta_id,
        MovimentacaoBancaria.data_competencia >= data_inicio,
        MovimentacaoBancaria.data_competencia <= data_fim
    ).order_by(MovimentacaoBancaria.data_competencia, MovimentacaoBancaria.created_at).all()
    
    # Calcular totais
    total_entradas = sum(m.valor for m in movimentacoes if m.natureza == "ENTRADA")
    total_saidas = sum(m.valor for m in movimentacoes if m.natureza == "SAIDA")
    
    # Calcular saldo inicial do período
    movimentacoes_anteriores = session.query(MovimentacaoBancaria).filter(
        MovimentacaoBancaria.conta_bancaria_id == conta_id,
        MovimentacaoBancaria.data_competencia < data_inicio
    ).all()
    
    saldo_inicial_periodo = conta.saldo_inicial
    for m in movimentacoes_anteriores:
        if m.natureza == "ENTRADA":
            saldo_inicial_periodo += m.valor
        else:
            saldo_inicial_periodo -= m.valor
    
    return {
        "conta": {
            "id": conta.id,
            "nome": conta.nome,
            "banco": conta.banco,
            "agencia": conta.agencia,
            "conta": conta.conta
        },
        "periodo": {
            "inicio": data_inicio,
            "fim": data_fim
        },
        "saldo_inicial": saldo_inicial_periodo,
        "total_entradas": total_entradas,
        "total_saidas": total_saidas,
        "saldo_final": saldo_inicial_periodo + total_entradas - total_saidas,
        "movimentacoes": [
            {
                "id": m.id,
                "data": m.data_competencia or m.data_movimentacao.date(),
                "tipo": m.tipo.value,
                "natureza": m.natureza,
                "descricao": m.descricao,
                "valor": m.valor,
                "conciliado": m.conciliado
            }
            for m in movimentacoes
        ]
    }


# =============================================================================
# CENTROS DE CUSTO
# =============================================================================

@router.get("/centros-custo", response_model=List[CentroCustoRead])
def list_centros_custo(
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Lista todos os centros de custo"""
    return session.query(CentroCusto).filter(CentroCusto.ativo == 1).all()


@router.post("/centros-custo", response_model=CentroCustoRead)
def create_centro_custo(
    centro: CentroCustoCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """Cria um novo centro de custo"""
    db_centro = CentroCusto(**centro.dict())
    session.add(db_centro)
    session.commit()
    session.refresh(db_centro)
    return db_centro


# =============================================================================
# CONTAS A PAGAR
# =============================================================================

@router.get("/contas-pagar", response_model=List[ContaPagarRead])
def list_contas_pagar(
    skip: int = 0,
    limit: int = 100,
    status: str = Query(None),
    fornecedor_id: int = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Lista todas as contas a pagar"""
    query = session.query(ContaPagar)
    
    if status:
        query = query.filter(ContaPagar.status == status)
    
    if fornecedor_id:
        query = query.filter(ContaPagar.fornecedor_id == fornecedor_id)
    
    return query.order_by(ContaPagar.data_vencimento).offset(skip).limit(limit).all()


@router.post("/contas-pagar", response_model=ContaPagarRead)
def create_conta_pagar(
    conta: ContaPagarCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """Cria uma nova conta a pagar"""
    db_conta = ContaPagar(**conta.dict())
    session.add(db_conta)
    session.commit()
    session.refresh(db_conta)
    return db_conta


@router.put("/contas-pagar/{conta_id}", response_model=ContaPagarRead)
def update_conta_pagar(
    conta_id: int,
    conta_data: ContaPagarUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Atualiza uma conta a pagar"""
    conta = session.query(ContaPagar).filter(ContaPagar.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    for key, value in conta_data.dict(exclude_unset=True).items():
        setattr(conta, key, value)
    
    # Atualizar status baseado no pagamento
    if conta.valor_pago >= conta.valor_original:
        conta.status = "pago"
    elif conta.valor_pago > 0:
        conta.status = "parcial"
    
    session.commit()
    session.refresh(conta)
    return conta


# =============================================================================
# CONTAS A RECEBER
# =============================================================================

@router.get("/contas-receber", response_model=List[ContaReceberRead])
def list_contas_receber(
    skip: int = 0,
    limit: int = 100,
    status: str = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Lista todas as contas a receber"""
    query = session.query(ContaReceber)
    
    if status:
        query = query.filter(ContaReceber.status == status)
    
    return query.order_by(ContaReceber.data_vencimento).offset(skip).limit(limit).all()


@router.post("/contas-receber", response_model=ContaReceberRead)
def create_conta_receber(
    conta: ContaReceberCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """Cria uma nova conta a receber"""
    db_conta = ContaReceber(**conta.dict())
    session.add(db_conta)
    session.commit()
    session.refresh(db_conta)
    return db_conta


@router.put("/contas-receber/{conta_id}", response_model=ContaReceberRead)
def update_conta_receber(
    conta_id: int,
    conta_data: ContaReceberUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Atualiza uma conta a receber"""
    conta = session.query(ContaReceber).filter(ContaReceber.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    for key, value in conta_data.dict(exclude_unset=True).items():
        setattr(conta, key, value)
    
    # Atualizar status baseado no recebimento
    if conta.valor_recebido >= conta.valor_original:
        conta.status = "pago"
    elif conta.valor_recebido > 0:
        conta.status = "parcial"
    
    session.commit()
    session.refresh(conta)
    return conta


@router.get("/fluxo-caixa")
def get_fluxo_caixa(
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Retorna o fluxo de caixa para um período"""
    # Converter strings para datetime
    try:
        dt_inicio = datetime.fromisoformat(data_inicio)
        dt_fim = datetime.fromisoformat(data_fim)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use ISO format")
    
    # Contas a pagar no período
    contas_pagar = session.query(ContaPagar).filter(
        ContaPagar.data_vencimento >= dt_inicio,
        ContaPagar.data_vencimento <= dt_fim
    ).all()
    
    # Contas a receber no período
    contas_receber = session.query(ContaReceber).filter(
        ContaReceber.data_vencimento >= dt_inicio,
        ContaReceber.data_vencimento <= dt_fim
    ).all()
    
    total_pagar = sum(c.valor_original - c.valor_pago for c in contas_pagar)
    total_receber = sum(c.valor_original - c.valor_recebido for c in contas_receber)
    
    return {
        "periodo": {"inicio": data_inicio, "fim": data_fim},
        "contas_pagar": {
            "total": total_pagar,
            "quantidade": len(contas_pagar)
        },
        "contas_receber": {
            "total": total_receber,
            "quantidade": len(contas_receber)
        },
        "saldo_previsto": total_receber - total_pagar
    }


# =============================================================================
# MOVIMENTAÇÕES BANCÁRIAS
# =============================================================================

@router.get("/movimentacoes-bancarias", response_model=List[MovimentacaoBancariaRead])
def list_movimentacoes_bancarias(
    skip: int = 0,
    limit: int = 100,
    conta_id: int = Query(None),
    conciliado: bool = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Lista todas as movimentações bancárias"""
    query = session.query(MovimentacaoBancaria)
    
    if conta_id:
        query = query.filter(MovimentacaoBancaria.conta_bancaria_id == conta_id)
    
    if conciliado is not None:
        query = query.filter(MovimentacaoBancaria.conciliado == conciliado)
    
    return query.order_by(MovimentacaoBancaria.data_movimentacao.desc()).offset(skip).limit(limit).all()


@router.post("/movimentacoes-bancarias", response_model=MovimentacaoBancariaRead)
def create_movimentacao_bancaria(
    movimentacao: MovimentacaoBancariaCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """Cria uma nova movimentação bancária"""
    # Verificar se a conta bancária existe
    conta = session.query(ContaBancaria).filter(ContaBancaria.id == movimentacao.conta_bancaria_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    
    # Criar a movimentação
    db_movimentacao = MovimentacaoBancaria(**movimentacao.model_dump())
    session.add(db_movimentacao)
    
    # Atualizar saldo da conta
    if movimentacao.natureza == "ENTRADA":
        conta.saldo_atual += movimentacao.valor
    else:  # SAIDA
        conta.saldo_atual -= movimentacao.valor
    
    session.commit()
    session.refresh(db_movimentacao)
    return db_movimentacao


@router.get("/movimentacoes-bancarias/{movimentacao_id}", response_model=MovimentacaoBancariaRead)
def get_movimentacao_bancaria(
    movimentacao_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Retorna uma movimentação bancária específica"""
    movimentacao = session.query(MovimentacaoBancaria).filter(
        MovimentacaoBancaria.id == movimentacao_id
    ).first()
    
    if not movimentacao:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    
    return movimentacao


@router.put("/movimentacoes-bancarias/{movimentacao_id}", response_model=MovimentacaoBancariaRead)
def update_movimentacao_bancaria(
    movimentacao_id: int,
    movimentacao_data: MovimentacaoBancariaUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Atualiza uma movimentação bancária"""
    movimentacao = session.query(MovimentacaoBancaria).filter(
        MovimentacaoBancaria.id == movimentacao_id
    ).first()
    
    if not movimentacao:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    
    # Se a movimentação já foi conciliada, não pode ser alterada
    if movimentacao.conciliado:
        raise HTTPException(status_code=400, detail="Movimentação já conciliada não pode ser alterada")
    
    # Buscar a conta para reverter e aplicar novo saldo
    conta = session.query(ContaBancaria).filter(
        ContaBancaria.id == movimentacao.conta_bancaria_id
    ).first()
    
    # Reverter o saldo anterior
    if movimentacao.natureza == "ENTRADA":
        conta.saldo_atual -= movimentacao.valor
    else:
        conta.saldo_atual += movimentacao.valor
    
    # Aplicar as atualizações
    for key, value in movimentacao_data.model_dump(exclude_unset=True).items():
        setattr(movimentacao, key, value)
    
    # Aplicar o novo saldo
    if movimentacao.natureza == "ENTRADA":
        conta.saldo_atual += movimentacao.valor
    else:
        conta.saldo_atual -= movimentacao.valor
    
    session.commit()
    session.refresh(movimentacao)
    return movimentacao


@router.delete("/movimentacoes-bancarias/{movimentacao_id}")
def delete_movimentacao_bancaria(
    movimentacao_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:delete"))
):
    """Deleta uma movimentação bancária"""
    movimentacao = session.query(MovimentacaoBancaria).filter(
        MovimentacaoBancaria.id == movimentacao_id
    ).first()
    
    if not movimentacao:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    
    # Se a movimentação já foi conciliada, não pode ser deletada
    if movimentacao.conciliado:
        raise HTTPException(status_code=400, detail="Movimentação conciliada não pode ser deletada")
    
    # Buscar a conta para reverter o saldo
    conta = session.query(ContaBancaria).filter(
        ContaBancaria.id == movimentacao.conta_bancaria_id
    ).first()
    
    # Reverter o saldo
    if movimentacao.natureza == "ENTRADA":
        conta.saldo_atual -= movimentacao.valor
    else:
        conta.saldo_atual += movimentacao.valor
    
    session.delete(movimentacao)
    session.commit()
    
    return {"message": "Movimentação deletada com sucesso"}


# =============================================================================
# TRANSFERÊNCIAS ENTRE CONTAS
# =============================================================================

@router.post("/transferencias")
def criar_transferencia(
    transferencia: TransferenciaCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """
    Cria transferência entre contas:
    1. MovimentacaoBancaria SAIDA na conta origem
    2. MovimentacaoBancaria ENTRADA na conta destino
    3. Vincula as movimentações
    4. Transação atômica
    """
    # Validar contas
    if transferencia.conta_origem_id == transferencia.conta_destino_id:
        raise HTTPException(status_code=400, detail="Conta origem e destino devem ser diferentes")
    
    conta_origem = session.query(ContaBancaria).filter(
        ContaBancaria.id == transferencia.conta_origem_id
    ).first()
    
    if not conta_origem:
        raise HTTPException(status_code=404, detail="Conta origem não encontrada")
    
    conta_destino = session.query(ContaBancaria).filter(
        ContaBancaria.id == transferencia.conta_destino_id
    ).first()
    
    if not conta_destino:
        raise HTTPException(status_code=404, detail="Conta destino não encontrada")
    
    # Verificar saldo suficiente
    if conta_origem.saldo_atual < transferencia.valor:
        raise HTTPException(status_code=400, detail="Saldo insuficiente na conta origem")
    
    try:
        # Criar movimentação de saída na conta origem
        movimentacao_saida = MovimentacaoBancaria(
            conta_bancaria_id=transferencia.conta_origem_id,
            tipo=TipoMovimentacaoBancaria.TRANSFERENCIA_SAIDA,
            natureza="SAIDA",
            data_movimentacao=transferencia.data,
            data_competencia=transferencia.data.date() if transferencia.data else datetime.utcnow().date(),
            valor=transferencia.valor,
            descricao=f"Transferência para {conta_destino.nome} - {transferencia.descricao}",
            conciliado=False
        )
        session.add(movimentacao_saida)
        session.flush()  # Para obter o ID
        
        # Criar movimentação de entrada na conta destino
        movimentacao_entrada = MovimentacaoBancaria(
            conta_bancaria_id=transferencia.conta_destino_id,
            tipo=TipoMovimentacaoBancaria.TRANSFERENCIA_ENTRADA,
            natureza="ENTRADA",
            data_movimentacao=transferencia.data,
            data_competencia=transferencia.data.date() if transferencia.data else datetime.utcnow().date(),
            valor=transferencia.valor,
            descricao=f"Transferência de {conta_origem.nome} - {transferencia.descricao}",
            transferencia_vinculada_id=movimentacao_saida.id,
            conciliado=False
        )
        session.add(movimentacao_entrada)
        session.flush()
        
        # Vincular a movimentação de saída com a de entrada
        movimentacao_saida.transferencia_vinculada_id = movimentacao_entrada.id
        
        # Atualizar saldos
        conta_origem.saldo_atual -= transferencia.valor
        conta_destino.saldo_atual += transferencia.valor
        
        session.commit()
        session.refresh(movimentacao_saida)
        session.refresh(movimentacao_entrada)
        
        return {
            "message": "Transferência realizada com sucesso",
            "movimentacao_saida_id": movimentacao_saida.id,
            "movimentacao_entrada_id": movimentacao_entrada.id,
            "valor": transferencia.valor,
            "conta_origem": {
                "id": conta_origem.id,
                "nome": conta_origem.nome,
                "saldo_atual": conta_origem.saldo_atual
            },
            "conta_destino": {
                "id": conta_destino.id,
                "nome": conta_destino.nome,
                "saldo_atual": conta_destino.saldo_atual
            }
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao realizar transferência: {str(e)}")


# =============================================================================
# CONCILIAÇÃO BANCÁRIA
# =============================================================================

@router.get("/conciliacao/{conta_id}")
def listar_pendentes_conciliacao(
    conta_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Lista movimentações pendentes de conciliação"""
    conta = session.query(ContaBancaria).filter(ContaBancaria.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    
    # Buscar movimentações não conciliadas
    movimentacoes = session.query(MovimentacaoBancaria).filter(
        MovimentacaoBancaria.conta_bancaria_id == conta_id,
        MovimentacaoBancaria.conciliado == False
    ).order_by(MovimentacaoBancaria.data_movimentacao.desc()).all()
    
    total_entradas = sum(m.valor for m in movimentacoes if m.natureza == "ENTRADA")
    total_saidas = sum(m.valor for m in movimentacoes if m.natureza == "SAIDA")
    
    return {
        "conta": {
            "id": conta.id,
            "nome": conta.nome,
            "saldo_atual": conta.saldo_atual
        },
        "total_entradas_pendentes": total_entradas,
        "total_saidas_pendentes": total_saidas,
        "saldo_pendente": total_entradas - total_saidas,
        "movimentacoes": [
            {
                "id": m.id,
                "data": m.data_competencia or m.data_movimentacao.date(),
                "tipo": m.tipo.value,
                "natureza": m.natureza,
                "descricao": m.descricao,
                "valor": m.valor,
                "conciliado": m.conciliado
            }
            for m in movimentacoes
        ]
    }


@router.post("/conciliacao/{conta_id}/conciliar")
def conciliar_movimentacoes(
    conta_id: int,
    movimentacao_ids: List[int],
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Marca movimentações como conciliadas"""
    conta = session.query(ContaBancaria).filter(ContaBancaria.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    
    if not movimentacao_ids:
        raise HTTPException(status_code=400, detail="Nenhuma movimentação selecionada")
    
    # Buscar e marcar movimentações
    movimentacoes = session.query(MovimentacaoBancaria).filter(
        MovimentacaoBancaria.id.in_(movimentacao_ids),
        MovimentacaoBancaria.conta_bancaria_id == conta_id
    ).all()
    
    if len(movimentacoes) != len(movimentacao_ids):
        raise HTTPException(status_code=404, detail="Algumas movimentações não foram encontradas")
    
    for movimentacao in movimentacoes:
        movimentacao.conciliado = True
        movimentacao.data_conciliacao = datetime.utcnow()
    
    session.commit()
    
    return {
        "message": f"{len(movimentacoes)} movimentações conciliadas com sucesso",
        "movimentacoes_conciliadas": len(movimentacoes)
    }


@router.post("/conciliacao/{conta_id}/desconciliar")
def desconciliar_movimentacoes(
    conta_id: int,
    movimentacao_ids: List[int],
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Remove marca de conciliação das movimentações"""
    conta = session.query(ContaBancaria).filter(ContaBancaria.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    
    if not movimentacao_ids:
        raise HTTPException(status_code=400, detail="Nenhuma movimentação selecionada")
    
    # Buscar e desmarcar movimentações
    movimentacoes = session.query(MovimentacaoBancaria).filter(
        MovimentacaoBancaria.id.in_(movimentacao_ids),
        MovimentacaoBancaria.conta_bancaria_id == conta_id
    ).all()
    
    if len(movimentacoes) != len(movimentacao_ids):
        raise HTTPException(status_code=404, detail="Algumas movimentações não foram encontradas")
    
    for movimentacao in movimentacoes:
        movimentacao.conciliado = False
        movimentacao.data_conciliacao = None
    
    session.commit()
    
    return {
        "message": f"{len(movimentacoes)} movimentações desconciliadas com sucesso",
        "movimentacoes_desconciliadas": len(movimentacoes)
    }
