from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db import get_session
from app.dependencies import require_permission
from app.schemas_modules import (
    ContaBancariaCreate, ContaBancariaRead,
    CentroCustoCreate, CentroCustoRead,
    ContaPagarCreate, ContaPagarRead, ContaPagarUpdate,
    ContaReceberCreate, ContaReceberRead, ContaReceberUpdate
)
from app.models_modules import (
    ContaBancaria, CentroCusto, ContaPagar, ContaReceber
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
    db_conta = ContaBancaria(**conta.dict(), saldo_atual=conta.saldo_inicial)
    session.add(db_conta)
    session.commit()
    session.refresh(db_conta)
    return db_conta


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
