from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, timedelta
from app.db import get_session
from app.dependencies import require_permission
from app.schemas_modules import (
    ContaBancariaCreate, ContaBancariaRead, ContaBancariaUpdate,
    CentroCustoCreate, CentroCustoRead,
    ContaPagarCreate, ContaPagarRead, ContaPagarUpdate,
    ContaReceberCreate, ContaReceberRead, ContaReceberUpdate,
    MovimentacaoBancariaCreate, MovimentacaoBancariaRead, MovimentacaoBancariaUpdate,
    SaldoDiarioRead, TransferenciaCreate,
    BaixaContaPagar, BaixaContaReceber,
    ParcelaContaPagarCreate, ParcelaContaPagarRead, ParcelaContaPagarUpdate,
    ParcelaContaReceberCreate, ParcelaContaReceberRead, ParcelaContaReceberUpdate,
    ContaPagarParceladaCreate, ContaReceberParceladaCreate,
    ContaRecorrenteCreate, ContaRecorrenteRead, ContaRecorrenteUpdate,
    CategoriaFinanceiraCreate, CategoriaFinanceiraRead, CategoriaFinanceiraUpdate
)
from app.models_modules import (
    ContaBancaria, CentroCusto, ContaPagar, ContaReceber,
    MovimentacaoBancaria, SaldoDiario, TipoMovimentacaoBancaria,
    StatusPagamento, ParcelaContaPagar, ParcelaContaReceber,
    ContaRecorrente, CategoriaFinanceira, TipoParcelamento
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


@router.get("/contas-bancarias/{conta_id}", response_model=ContaBancariaRead)
def get_conta_bancaria(
    conta_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Busca uma conta bancária por ID"""
    conta = session.query(ContaBancaria).filter(ContaBancaria.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    return conta


@router.put("/contas-bancarias/{conta_id}", response_model=ContaBancariaRead)
def update_conta_bancaria(
    conta_id: int,
    conta_update: ContaBancariaUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Atualiza uma conta bancária"""
    db_conta = session.query(ContaBancaria).filter(ContaBancaria.id == conta_id).first()
    if not db_conta:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    
    update_data = conta_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_conta, key, value)
    
    session.commit()
    session.refresh(db_conta)
    return db_conta


@router.delete("/contas-bancarias/{conta_id}")
def delete_conta_bancaria(
    conta_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:delete"))
):
    """Desativa uma conta bancária"""
    db_conta = session.query(ContaBancaria).filter(ContaBancaria.id == conta_id).first()
    if not db_conta:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    
    db_conta.ativa = 0
    session.commit()
    return {"message": "Conta bancária desativada com sucesso"}


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


@router.post("/contas-pagar/{conta_id}/baixar", response_model=ContaPagarRead)
def baixar_conta_pagar(
    conta_id: int,
    baixa: BaixaContaPagar,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """
    Realizar baixa (pagamento) de uma conta a pagar
    - Atualiza valor pago, juros e desconto
    - Atualiza status da conta (pendente/parcial/pago)
    - Cria movimentação bancária automática (débito)
    - Atualiza saldo da conta bancária
    """
    # Buscar conta a pagar
    conta = session.query(ContaPagar).filter(ContaPagar.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    # Buscar conta bancária
    conta_bancaria = session.query(ContaBancaria).filter(
        ContaBancaria.id == baixa.conta_bancaria_id
    ).first()
    if not conta_bancaria:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    
    # Validar valor pago
    if baixa.valor_pago <= 0:
        raise HTTPException(status_code=400, detail="Valor pago deve ser maior que zero")
    
    # Calcular saldo devedor atual
    saldo_devedor = conta.valor_original + conta.juros - conta.desconto - conta.valor_pago
    
    # Validar se o valor pago não excede o saldo devedor
    if baixa.valor_pago > saldo_devedor:
        raise HTTPException(
            status_code=400,
            detail=f"Valor pago (R$ {baixa.valor_pago:.2f}) não pode ser maior que o saldo devedor (R$ {saldo_devedor:.2f})"
        )
    
    # Verificar saldo suficiente na conta bancária
    if conta_bancaria.saldo_atual < baixa.valor_pago:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente na conta bancária. Saldo atual: R$ {conta_bancaria.saldo_atual:.2f}"
        )
    
    try:
        # Atualizar conta a pagar
        conta.valor_pago += baixa.valor_pago
        conta.juros += baixa.juros
        conta.desconto += baixa.desconto
        
        # Definir data de pagamento
        data_pagamento = baixa.data_pagamento or datetime.utcnow()
        if not conta.data_pagamento:
            conta.data_pagamento = data_pagamento
        
        # Atualizar observações se fornecidas
        if baixa.observacoes:
            if conta.observacoes:
                conta.observacoes = f"{conta.observacoes}\n{baixa.observacoes}"
            else:
                conta.observacoes = baixa.observacoes
        
        # Atualizar status
        novo_saldo_devedor = conta.valor_original + conta.juros - conta.desconto - conta.valor_pago
        if novo_saldo_devedor <= 0.01:  # Tolerância de 1 centavo
            conta.status = StatusPagamento.PAGO
        elif conta.valor_pago > 0:
            conta.status = StatusPagamento.PARCIAL
        
        # Criar movimentação bancária (débito)
        descricao_mov = f"Pagamento: {conta.descricao}"
        if baixa.juros > 0:
            descricao_mov += f" (Juros: R$ {baixa.juros:.2f})"
        if baixa.desconto > 0:
            descricao_mov += f" (Desconto: R$ {baixa.desconto:.2f})"
        
        movimentacao = MovimentacaoBancaria(
            conta_bancaria_id=baixa.conta_bancaria_id,
            tipo=TipoMovimentacaoBancaria.OUTROS,
            natureza="SAIDA",
            data_movimentacao=data_pagamento,
            data_competencia=data_pagamento.date() if data_pagamento else datetime.utcnow().date(),
            valor=baixa.valor_pago,
            descricao=descricao_mov,
            conciliado=False
        )
        session.add(movimentacao)
        
        # Atualizar saldo da conta bancária
        conta_bancaria.saldo_atual -= baixa.valor_pago
        
        session.commit()
        session.refresh(conta)
        
        return conta
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao realizar baixa: {str(e)}")


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


@router.post("/contas-receber/{conta_id}/baixar", response_model=ContaReceberRead)
def baixar_conta_receber(
    conta_id: int,
    baixa: BaixaContaReceber,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """
    Realizar baixa (recebimento) de uma conta a receber
    - Atualiza valor recebido, juros e desconto
    - Atualiza status da conta (pendente/parcial/pago)
    - Cria movimentação bancária automática (crédito)
    - Atualiza saldo da conta bancária
    """
    # Buscar conta a receber
    conta = session.query(ContaReceber).filter(ContaReceber.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    # Buscar conta bancária
    conta_bancaria = session.query(ContaBancaria).filter(
        ContaBancaria.id == baixa.conta_bancaria_id
    ).first()
    if not conta_bancaria:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    
    # Validar valor recebido
    if baixa.valor_recebido <= 0:
        raise HTTPException(status_code=400, detail="Valor recebido deve ser maior que zero")
    
    # Calcular saldo a receber atual
    saldo_receber = conta.valor_original + conta.juros - conta.desconto - conta.valor_recebido
    
    # Validar se o valor recebido não excede o saldo a receber
    if baixa.valor_recebido > saldo_receber:
        raise HTTPException(
            status_code=400,
            detail=f"Valor recebido (R$ {baixa.valor_recebido:.2f}) não pode ser maior que o saldo a receber (R$ {saldo_receber:.2f})"
        )
    
    try:
        # Atualizar conta a receber
        conta.valor_recebido += baixa.valor_recebido
        conta.juros += baixa.juros
        conta.desconto += baixa.desconto
        
        # Definir data de recebimento
        data_recebimento = baixa.data_recebimento or datetime.utcnow()
        if not conta.data_recebimento:
            conta.data_recebimento = data_recebimento
        
        # Atualizar observações se fornecidas
        if baixa.observacoes:
            if conta.observacoes:
                conta.observacoes = f"{conta.observacoes}\n{baixa.observacoes}"
            else:
                conta.observacoes = baixa.observacoes
        
        # Atualizar status
        novo_saldo_receber = conta.valor_original + conta.juros - conta.desconto - conta.valor_recebido
        if novo_saldo_receber <= 0.01:  # Tolerância de 1 centavo
            conta.status = StatusPagamento.PAGO
        elif conta.valor_recebido > 0:
            conta.status = StatusPagamento.PARCIAL
        
        # Criar movimentação bancária (crédito)
        descricao_mov = f"Recebimento: {conta.descricao}"
        if baixa.juros > 0:
            descricao_mov += f" (Juros: R$ {baixa.juros:.2f})"
        if baixa.desconto > 0:
            descricao_mov += f" (Desconto: R$ {baixa.desconto:.2f})"
        
        movimentacao = MovimentacaoBancaria(
            conta_bancaria_id=baixa.conta_bancaria_id,
            tipo=TipoMovimentacaoBancaria.DEPOSITO,
            natureza="ENTRADA",
            data_movimentacao=data_recebimento,
            data_competencia=data_recebimento.date() if data_recebimento else datetime.utcnow().date(),
            valor=baixa.valor_recebido,
            descricao=descricao_mov,
            conciliado=False
        )
        session.add(movimentacao)
        
        # Atualizar saldo da conta bancária
        conta_bancaria.saldo_atual += baixa.valor_recebido
        
        session.commit()
        session.refresh(conta)
        
        return conta
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao realizar baixa: {str(e)}")


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


# =============================================================================
# CONTAS A PAGAR PARCELADAS
# =============================================================================

@router.post("/contas-pagar/parcelada", response_model=ContaPagarRead)
def create_conta_pagar_parcelada(
    conta: ContaPagarParceladaCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """Cria uma conta a pagar com parcelas"""
    # Criar conta a pagar principal
    db_conta = ContaPagar(
        descricao=conta.descricao,
        fornecedor_id=conta.fornecedor_id,
        centro_custo_id=conta.centro_custo_id,
        pedido_compra_id=conta.pedido_compra_id,
        categoria_id=conta.categoria_id,
        data_emissao=datetime.utcnow(),
        data_vencimento=conta.data_primeira_parcela,
        valor_original=conta.valor_total,
        tipo_parcelamento=TipoParcelamento.PARCELADO,
        quantidade_parcelas=conta.quantidade_parcelas,
        forma_pagamento=conta.forma_pagamento,
        numero_documento=conta.numero_documento,
        observacoes=conta.observacoes,
        status=StatusPagamento.PENDENTE
    )
    session.add(db_conta)
    session.flush()
    
    # Criar parcelas
    # NOTE: Using simple division for now. For production, consider using Decimal for precise financial calculations
    valor_parcela = round(conta.valor_total / conta.quantidade_parcelas, 2)
    for i in range(conta.quantidade_parcelas):
        data_vencimento = conta.data_primeira_parcela + timedelta(days=i * conta.intervalo_dias)
        parcela = ParcelaContaPagar(
            conta_pagar_id=db_conta.id,
            numero_parcela=i + 1,
            total_parcelas=conta.quantidade_parcelas,
            data_vencimento=data_vencimento,
            valor=valor_parcela,
            status=StatusPagamento.PENDENTE
        )
        session.add(parcela)
    
    session.commit()
    session.refresh(db_conta)
    return db_conta


@router.post("/contas-receber/parcelada", response_model=ContaReceberRead)
def create_conta_receber_parcelada(
    conta: ContaReceberParceladaCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """Cria uma conta a receber com parcelas"""
    # Criar conta a receber principal
    db_conta = ContaReceber(
        descricao=conta.descricao,
        cliente_id=conta.cliente_id,
        centro_custo_id=conta.centro_custo_id,
        pedido_venda_id=conta.pedido_venda_id,
        categoria_id=conta.categoria_id,
        data_emissao=datetime.utcnow(),
        data_vencimento=conta.data_primeira_parcela,
        valor_original=conta.valor_total,
        tipo_parcelamento=TipoParcelamento.PARCELADO,
        quantidade_parcelas=conta.quantidade_parcelas,
        forma_pagamento=conta.forma_pagamento,
        numero_documento=conta.numero_documento,
        observacoes=conta.observacoes,
        status=StatusPagamento.PENDENTE
    )
    session.add(db_conta)
    session.flush()
    
    # Criar parcelas
    # NOTE: Using simple division for now. For production, consider using Decimal for precise financial calculations
    valor_parcela = round(conta.valor_total / conta.quantidade_parcelas, 2)
    for i in range(conta.quantidade_parcelas):
        data_vencimento = conta.data_primeira_parcela + timedelta(days=i * conta.intervalo_dias)
        parcela = ParcelaContaReceber(
            conta_receber_id=db_conta.id,
            numero_parcela=i + 1,
            total_parcelas=conta.quantidade_parcelas,
            data_vencimento=data_vencimento,
            valor=valor_parcela,
            status=StatusPagamento.PENDENTE
        )
        session.add(parcela)
    
    session.commit()
    session.refresh(db_conta)
    return db_conta


@router.get("/contas-pagar/{conta_id}/parcelas", response_model=List[ParcelaContaPagarRead])
def list_parcelas_conta_pagar(
    conta_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Lista as parcelas de uma conta a pagar"""
    conta = session.query(ContaPagar).filter(ContaPagar.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a pagar não encontrada")
    
    return session.query(ParcelaContaPagar).filter(
        ParcelaContaPagar.conta_pagar_id == conta_id
    ).order_by(ParcelaContaPagar.numero_parcela).all()


@router.get("/contas-receber/{conta_id}/parcelas", response_model=List[ParcelaContaReceberRead])
def list_parcelas_conta_receber(
    conta_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Lista as parcelas de uma conta a receber"""
    conta = session.query(ContaReceber).filter(ContaReceber.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta a receber não encontrada")
    
    return session.query(ParcelaContaReceber).filter(
        ParcelaContaReceber.conta_receber_id == conta_id
    ).order_by(ParcelaContaReceber.numero_parcela).all()


@router.post("/contas-pagar/{conta_id}/parcelas/{parcela_id}/baixar")
def baixar_parcela_conta_pagar(
    conta_id: int,
    parcela_id: int,
    baixa: BaixaContaPagar,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Baixa uma parcela individual de conta a pagar"""
    parcela = session.query(ParcelaContaPagar).filter(
        ParcelaContaPagar.id == parcela_id,
        ParcelaContaPagar.conta_pagar_id == conta_id
    ).first()
    
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    
    if parcela.status == StatusPagamento.PAGO:
        raise HTTPException(status_code=400, detail="Parcela já está paga")
    
    # Atualizar parcela
    parcela.data_pagamento = baixa.data_pagamento or datetime.utcnow()
    parcela.valor_pago = baixa.valor_pago
    parcela.juros = baixa.juros
    parcela.desconto = baixa.desconto
    parcela.status = StatusPagamento.PAGO
    
    # Criar movimentação bancária
    movimentacao = MovimentacaoBancaria(
        conta_bancaria_id=baixa.conta_bancaria_id,
        tipo=TipoMovimentacaoBancaria.SAQUE,
        natureza="SAIDA",
        data_movimentacao=parcela.data_pagamento,
        valor=baixa.valor_pago,
        descricao=f"Pagamento parcela {parcela.numero_parcela}/{parcela.total_parcelas} - Conta: {parcela.conta_pagar_id}",
        conta_pagar_id=conta_id
    )
    session.add(movimentacao)
    
    # Atualizar saldo da conta bancária
    conta_bancaria = session.query(ContaBancaria).filter(
        ContaBancaria.id == baixa.conta_bancaria_id
    ).first()
    if conta_bancaria:
        conta_bancaria.saldo_atual -= baixa.valor_pago
    
    # Verificar se todas as parcelas foram pagas
    conta = session.query(ContaPagar).filter(ContaPagar.id == conta_id).first()
    todas_parcelas = session.query(ParcelaContaPagar).filter(
        ParcelaContaPagar.conta_pagar_id == conta_id
    ).all()
    
    if all(p.status == StatusPagamento.PAGO for p in todas_parcelas):
        conta.status = StatusPagamento.PAGO
        conta.data_pagamento = datetime.utcnow()
        conta.valor_pago = sum(p.valor_pago for p in todas_parcelas)
    else:
        valor_total_pago = sum(p.valor_pago for p in todas_parcelas if p.status == StatusPagamento.PAGO)
        if valor_total_pago > 0:
            conta.status = StatusPagamento.PARCIAL
            conta.valor_pago = valor_total_pago
    
    session.commit()
    
    return {"message": "Parcela baixada com sucesso", "parcela_id": parcela_id}


@router.post("/contas-receber/{conta_id}/parcelas/{parcela_id}/baixar")
def baixar_parcela_conta_receber(
    conta_id: int,
    parcela_id: int,
    baixa: BaixaContaReceber,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Baixa uma parcela individual de conta a receber"""
    parcela = session.query(ParcelaContaReceber).filter(
        ParcelaContaReceber.id == parcela_id,
        ParcelaContaReceber.conta_receber_id == conta_id
    ).first()
    
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    
    if parcela.status == StatusPagamento.PAGO:
        raise HTTPException(status_code=400, detail="Parcela já está paga")
    
    # Atualizar parcela
    parcela.data_recebimento = baixa.data_recebimento or datetime.utcnow()
    parcela.valor_recebido = baixa.valor_recebido
    parcela.juros = baixa.juros
    parcela.desconto = baixa.desconto
    parcela.status = StatusPagamento.PAGO
    
    # Criar movimentação bancária
    movimentacao = MovimentacaoBancaria(
        conta_bancaria_id=baixa.conta_bancaria_id,
        tipo=TipoMovimentacaoBancaria.DEPOSITO,
        natureza="ENTRADA",
        data_movimentacao=parcela.data_recebimento,
        valor=baixa.valor_recebido,
        descricao=f"Recebimento parcela {parcela.numero_parcela}/{parcela.total_parcelas} - Conta: {parcela.conta_receber_id}",
        conta_receber_id=conta_id
    )
    session.add(movimentacao)
    
    # Atualizar saldo da conta bancária
    conta_bancaria = session.query(ContaBancaria).filter(
        ContaBancaria.id == baixa.conta_bancaria_id
    ).first()
    if conta_bancaria:
        conta_bancaria.saldo_atual += baixa.valor_recebido
    
    # Verificar se todas as parcelas foram recebidas
    conta = session.query(ContaReceber).filter(ContaReceber.id == conta_id).first()
    todas_parcelas = session.query(ParcelaContaReceber).filter(
        ParcelaContaReceber.conta_receber_id == conta_id
    ).all()
    
    if all(p.status == StatusPagamento.PAGO for p in todas_parcelas):
        conta.status = StatusPagamento.PAGO
        conta.data_recebimento = datetime.utcnow()
        conta.valor_recebido = sum(p.valor_recebido for p in todas_parcelas)
    else:
        valor_total_recebido = sum(p.valor_recebido for p in todas_parcelas if p.status == StatusPagamento.PAGO)
        if valor_total_recebido > 0:
            conta.status = StatusPagamento.PARCIAL
            conta.valor_recebido = valor_total_recebido
    
    session.commit()
    
    return {"message": "Parcela recebida com sucesso", "parcela_id": parcela_id}


@router.put("/contas-pagar/{conta_id}/parcelas/{parcela_id}/reagendar")
def reagendar_parcela_conta_pagar(
    conta_id: int,
    parcela_id: int,
    nova_data: datetime,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Reagenda uma parcela de conta a pagar"""
    parcela = session.query(ParcelaContaPagar).filter(
        ParcelaContaPagar.id == parcela_id,
        ParcelaContaPagar.conta_pagar_id == conta_id
    ).first()
    
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    
    if parcela.status == StatusPagamento.PAGO:
        raise HTTPException(status_code=400, detail="Não é possível reagendar parcela já paga")
    
    parcela.data_vencimento = nova_data
    session.commit()
    
    return {"message": "Parcela reagendada com sucesso", "parcela_id": parcela_id}


# =============================================================================
# CONTAS RECORRENTES
# =============================================================================

@router.get("/contas-recorrentes", response_model=List[ContaRecorrenteRead])
def list_contas_recorrentes(
    tipo: str = Query(None, description="Filtrar por tipo: pagar ou receber"),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Lista todas as contas recorrentes"""
    query = session.query(ContaRecorrente)
    if tipo:
        query = query.filter(ContaRecorrente.tipo == tipo)
    return query.filter(ContaRecorrente.ativa == 1).all()


@router.post("/contas-recorrentes", response_model=ContaRecorrenteRead)
def create_conta_recorrente(
    conta: ContaRecorrenteCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """Cria uma conta recorrente"""
    # Validar que fornecedor_id ou cliente_id está presente
    if conta.tipo == "pagar" and not conta.fornecedor_id:
        raise HTTPException(status_code=400, detail="fornecedor_id é obrigatório para contas a pagar")
    if conta.tipo == "receber" and not conta.cliente_id:
        raise HTTPException(status_code=400, detail="cliente_id é obrigatório para contas a receber")
    
    # Validar dia_vencimento
    if conta.dia_vencimento < 1 or conta.dia_vencimento > 28:
        raise HTTPException(status_code=400, detail="dia_vencimento deve estar entre 1 e 28")
    
    db_conta = ContaRecorrente(**conta.model_dump())
    session.add(db_conta)
    session.commit()
    session.refresh(db_conta)
    return db_conta


@router.get("/contas-recorrentes/{conta_id}", response_model=ContaRecorrenteRead)
def get_conta_recorrente(
    conta_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Busca uma conta recorrente por ID"""
    conta = session.query(ContaRecorrente).filter(ContaRecorrente.id == conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta recorrente não encontrada")
    return conta


@router.put("/contas-recorrentes/{conta_id}", response_model=ContaRecorrenteRead)
def update_conta_recorrente(
    conta_id: int,
    conta_update: ContaRecorrenteUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Atualiza uma conta recorrente"""
    db_conta = session.query(ContaRecorrente).filter(ContaRecorrente.id == conta_id).first()
    if not db_conta:
        raise HTTPException(status_code=404, detail="Conta recorrente não encontrada")
    
    update_data = conta_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_conta, key, value)
    
    session.commit()
    session.refresh(db_conta)
    return db_conta


@router.delete("/contas-recorrentes/{conta_id}")
def delete_conta_recorrente(
    conta_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:delete"))
):
    """Desativa uma conta recorrente"""
    db_conta = session.query(ContaRecorrente).filter(ContaRecorrente.id == conta_id).first()
    if not db_conta:
        raise HTTPException(status_code=404, detail="Conta recorrente não encontrada")
    
    db_conta.ativa = 0
    session.commit()
    return {"message": "Conta recorrente desativada com sucesso"}


@router.post("/contas-recorrentes/{conta_id}/pausar")
def pausar_conta_recorrente(
    conta_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Pausa uma conta recorrente"""
    db_conta = session.query(ContaRecorrente).filter(ContaRecorrente.id == conta_id).first()
    if not db_conta:
        raise HTTPException(status_code=404, detail="Conta recorrente não encontrada")
    
    db_conta.ativa = 0
    session.commit()
    return {"message": "Conta recorrente pausada com sucesso"}


@router.post("/contas-recorrentes/{conta_id}/ativar")
def ativar_conta_recorrente(
    conta_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Ativa uma conta recorrente"""
    db_conta = session.query(ContaRecorrente).filter(ContaRecorrente.id == conta_id).first()
    if not db_conta:
        raise HTTPException(status_code=404, detail="Conta recorrente não encontrada")
    
    db_conta.ativa = 1
    session.commit()
    return {"message": "Conta recorrente ativada com sucesso"}


@router.post("/contas-recorrentes/gerar-mensal")
def gerar_contas_recorrentes_mensal(
    mes: int = Query(..., ge=1, le=12, description="Mês (1-12)"),
    ano: int = Query(..., ge=2000, description="Ano"),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """Gera contas a pagar/receber do mês baseado nas contas recorrentes ativas"""
    data_referencia = date(ano, mes, 1)
    contas_geradas = []
    
    # Buscar contas recorrentes ativas
    contas_recorrentes = session.query(ContaRecorrente).filter(
        ContaRecorrente.ativa == 1,
        ContaRecorrente.data_inicio <= data_referencia
    ).all()
    
    for conta_rec in contas_recorrentes:
        # Verificar se já foi gerada neste mês
        if conta_rec.ultima_geracao and conta_rec.ultima_geracao.month == mes and conta_rec.ultima_geracao.year == ano:
            continue
        
        # Verificar se está dentro do período
        if conta_rec.data_fim and data_referencia > conta_rec.data_fim:
            continue
        
        # Calcular data de vencimento
        data_vencimento = date(ano, mes, min(conta_rec.dia_vencimento, 28))
        
        if conta_rec.tipo == "pagar":
            nova_conta = ContaPagar(
                descricao=conta_rec.descricao,
                fornecedor_id=conta_rec.fornecedor_id,
                centro_custo_id=conta_rec.centro_custo_id,
                conta_recorrente_id=conta_rec.id,
                data_emissao=datetime.utcnow(),
                data_vencimento=datetime.combine(data_vencimento, datetime.min.time()),
                valor_original=conta_rec.valor,
                tipo_parcelamento=TipoParcelamento.RECORRENTE,
                observacoes=f"Gerada automaticamente - {conta_rec.observacoes or ''}",
                status=StatusPagamento.PENDENTE
            )
            session.add(nova_conta)
            contas_geradas.append({"tipo": "pagar", "descricao": conta_rec.descricao})
        elif conta_rec.tipo == "receber":
            nova_conta = ContaReceber(
                descricao=conta_rec.descricao,
                cliente_id=conta_rec.cliente_id,
                centro_custo_id=conta_rec.centro_custo_id,
                conta_recorrente_id=conta_rec.id,
                data_emissao=datetime.utcnow(),
                data_vencimento=datetime.combine(data_vencimento, datetime.min.time()),
                valor_original=conta_rec.valor,
                tipo_parcelamento=TipoParcelamento.RECORRENTE,
                observacoes=f"Gerada automaticamente - {conta_rec.observacoes or ''}",
                status=StatusPagamento.PENDENTE
            )
            session.add(nova_conta)
            contas_geradas.append({"tipo": "receber", "descricao": conta_rec.descricao})
        
        # Atualizar última geração
        conta_rec.ultima_geracao = data_referencia
    
    session.commit()
    
    return {
        "message": f"{len(contas_geradas)} contas geradas para {mes}/{ano}",
        "contas_geradas": contas_geradas
    }


# =============================================================================
# CATEGORIAS FINANCEIRAS
# =============================================================================

@router.get("/categorias-financeiras", response_model=List[CategoriaFinanceiraRead])
def list_categorias_financeiras(
    tipo: str = Query(None, description="Filtrar por tipo: receita ou despesa"),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Lista todas as categorias financeiras"""
    query = session.query(CategoriaFinanceira).filter(CategoriaFinanceira.ativa == 1)
    if tipo:
        query = query.filter(CategoriaFinanceira.tipo == tipo)
    return query.all()


@router.post("/categorias-financeiras", response_model=CategoriaFinanceiraRead)
def create_categoria_financeira(
    categoria: CategoriaFinanceiraCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:create"))
):
    """Cria uma categoria financeira"""
    # Verificar se código já existe
    existe = session.query(CategoriaFinanceira).filter(
        CategoriaFinanceira.codigo == categoria.codigo
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="Código já existe")
    
    db_categoria = CategoriaFinanceira(**categoria.model_dump())
    session.add(db_categoria)
    session.commit()
    session.refresh(db_categoria)
    return db_categoria


@router.get("/categorias-financeiras/{categoria_id}", response_model=CategoriaFinanceiraRead)
def get_categoria_financeira(
    categoria_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Busca uma categoria financeira por ID"""
    categoria = session.query(CategoriaFinanceira).filter(
        CategoriaFinanceira.id == categoria_id
    ).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria


@router.put("/categorias-financeiras/{categoria_id}", response_model=CategoriaFinanceiraRead)
def update_categoria_financeira(
    categoria_id: int,
    categoria_update: CategoriaFinanceiraUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:update"))
):
    """Atualiza uma categoria financeira"""
    db_categoria = session.query(CategoriaFinanceira).filter(
        CategoriaFinanceira.id == categoria_id
    ).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    update_data = categoria_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_categoria, key, value)
    
    session.commit()
    session.refresh(db_categoria)
    return db_categoria


@router.delete("/categorias-financeiras/{categoria_id}")
def delete_categoria_financeira(
    categoria_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:delete"))
):
    """Desativa uma categoria financeira"""
    db_categoria = session.query(CategoriaFinanceira).filter(
        CategoriaFinanceira.id == categoria_id
    ).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    db_categoria.ativa = 0
    session.commit()
    return {"message": "Categoria desativada com sucesso"}


# =============================================================================
# RELATÓRIOS
# =============================================================================

@router.get("/financeiro/dre")
def relatorio_dre(
    mes: int = Query(..., ge=1, le=12, description="Mês (1-12)"),
    ano: int = Query(..., ge=2000, description="Ano"),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("financeiro:read"))
):
    """Relatório DRE simplificado (Demonstrativo de Resultado do Exercício)"""
    from calendar import monthrange
    
    # Calcular primeiro e último dia do mês
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
    
    # Buscar receitas (contas receber pagas)
    receitas = session.query(ContaReceber).filter(
        ContaReceber.status == StatusPagamento.PAGO,
        ContaReceber.data_recebimento >= datetime.combine(primeiro_dia, datetime.min.time()),
        ContaReceber.data_recebimento <= datetime.combine(ultimo_dia, datetime.max.time())
    ).all()
    
    total_receitas = sum(c.valor_recebido for c in receitas)
    
    # Buscar despesas (contas pagar pagas)
    despesas = session.query(ContaPagar).filter(
        ContaPagar.status == StatusPagamento.PAGO,
        ContaPagar.data_pagamento >= datetime.combine(primeiro_dia, datetime.min.time()),
        ContaPagar.data_pagamento <= datetime.combine(ultimo_dia, datetime.max.time())
    ).all()
    
    total_despesas = sum(c.valor_pago for c in despesas)
    
    resultado = total_receitas - total_despesas
    
    return {
        "periodo": f"{mes:02d}/{ano}",
        "receitas": {
            "total": total_receitas,
            "quantidade": len(receitas)
        },
        "despesas": {
            "total": total_despesas,
            "quantidade": len(despesas)
        },
        "resultado": resultado,
        "resultado_percentual": (resultado / total_receitas * 100) if total_receitas > 0 else 0
    }
