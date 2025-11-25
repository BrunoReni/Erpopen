from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db import get_session
from app.dependencies import require_permission
from app.schemas_modules import (
    CotacaoCreate, CotacaoRead, CotacaoUpdate,
    RespostaFornecedorCreate, RespostaFornecedorRead,
    StatusCotacao
)
from app.models_modules import (
    Cotacao, ItemCotacao, RespostaFornecedor, ItemRespostaFornecedor,
    PedidoCompra, ItemPedidoCompra, Fornecedor
)
from app.helpers import gerar_proximo_codigo

router = APIRouter()


# =============================================================================
# COTAÇÕES
# =============================================================================

@router.get("/cotacoes", response_model=List[CotacaoRead])
def list_cotacoes(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:read"))
):
    """Lista todas as cotações com filtros opcionais"""
    query = session.query(Cotacao)
    
    if status:
        query = query.filter(Cotacao.status == status)
    
    cotacoes = query.order_by(Cotacao.created_at.desc()).offset(skip).limit(limit).all()
    return cotacoes


@router.post("/cotacoes", response_model=CotacaoRead)
def create_cotacao(
    cotacao: CotacaoCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:create"))
):
    """Cria uma nova cotação"""
    # Gerar número sequencial
    numero = gerar_proximo_codigo(session, Cotacao, "COT")
    
    # Criar cotação
    db_cotacao = Cotacao(
        numero=numero,
        descricao=cotacao.descricao,
        data_limite_resposta=cotacao.data_limite_resposta,
        observacoes=cotacao.observacoes,
        status=StatusCotacao.RASCUNHO
    )
    session.add(db_cotacao)
    session.flush()
    
    # Adicionar itens
    for item in cotacao.itens:
        db_item = ItemCotacao(
            cotacao_id=db_cotacao.id,
            **item.dict()
        )
        session.add(db_item)
    
    session.commit()
    session.refresh(db_cotacao)
    return db_cotacao


@router.get("/cotacoes/{cotacao_id}", response_model=CotacaoRead)
def get_cotacao(
    cotacao_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:read"))
):
    """Busca uma cotação por ID"""
    cotacao = session.query(Cotacao).filter(Cotacao.id == cotacao_id).first()
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    return cotacao


@router.put("/cotacoes/{cotacao_id}", response_model=CotacaoRead)
def update_cotacao(
    cotacao_id: int,
    cotacao_update: CotacaoUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:update"))
):
    """Atualiza uma cotação"""
    db_cotacao = session.query(Cotacao).filter(Cotacao.id == cotacao_id).first()
    if not db_cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    # Atualizar campos
    for key, value in cotacao_update.dict(exclude_unset=True).items():
        setattr(db_cotacao, key, value)
    
    db_cotacao.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(db_cotacao)
    return db_cotacao


@router.delete("/cotacoes/{cotacao_id}")
def delete_cotacao(
    cotacao_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:delete"))
):
    """Deleta uma cotação"""
    db_cotacao = session.query(Cotacao).filter(Cotacao.id == cotacao_id).first()
    if not db_cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    session.delete(db_cotacao)
    session.commit()
    return {"message": "Cotação deletada com sucesso"}


# =============================================================================
# RESPOSTAS DE FORNECEDORES
# =============================================================================

@router.post("/cotacoes/{cotacao_id}/respostas", response_model=RespostaFornecedorRead)
def create_resposta_fornecedor(
    cotacao_id: int,
    resposta: RespostaFornecedorCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:create"))
):
    """Adiciona resposta de um fornecedor a uma cotação"""
    # Verificar se cotação existe
    cotacao = session.query(Cotacao).filter(Cotacao.id == cotacao_id).first()
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    # Verificar se fornecedor existe
    fornecedor = session.query(Fornecedor).filter(Fornecedor.id == resposta.fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    # Criar resposta
    db_resposta = RespostaFornecedor(
        cotacao_id=cotacao_id,
        fornecedor_id=resposta.fornecedor_id,
        prazo_entrega_dias=resposta.prazo_entrega_dias,
        condicao_pagamento=resposta.condicao_pagamento,
        observacoes=resposta.observacoes
    )
    session.add(db_resposta)
    session.flush()
    
    # Adicionar itens da resposta e calcular total
    valor_total = 0.0
    for item in resposta.itens:
        preco_total = item.preco_unitario * session.query(ItemCotacao).filter(
            ItemCotacao.id == item.item_cotacao_id
        ).first().quantidade
        
        db_item = ItemRespostaFornecedor(
            resposta_id=db_resposta.id,
            item_cotacao_id=item.item_cotacao_id,
            preco_unitario=item.preco_unitario,
            preco_total=preco_total,
            marca=item.marca,
            observacoes=item.observacoes
        )
        session.add(db_item)
        valor_total += preco_total
    
    db_resposta.valor_total = valor_total
    
    # Atualizar status da cotação
    if cotacao.status == StatusCotacao.RASCUNHO or cotacao.status == StatusCotacao.ENVIADA:
        cotacao.status = StatusCotacao.RESPONDIDA
    
    session.commit()
    session.refresh(db_resposta)
    return db_resposta


@router.get("/cotacoes/{cotacao_id}/respostas", response_model=List[RespostaFornecedorRead])
def list_respostas_cotacao(
    cotacao_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:read"))
):
    """Lista todas as respostas de uma cotação"""
    respostas = session.query(RespostaFornecedor).filter(
        RespostaFornecedor.cotacao_id == cotacao_id
    ).all()
    return respostas


@router.post("/cotacoes/{cotacao_id}/selecionar-fornecedor/{resposta_id}")
def selecionar_fornecedor(
    cotacao_id: int,
    resposta_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:update"))
):
    """Seleciona a melhor resposta de fornecedor"""
    cotacao = session.query(Cotacao).filter(Cotacao.id == cotacao_id).first()
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    resposta = session.query(RespostaFornecedor).filter(
        RespostaFornecedor.id == resposta_id,
        RespostaFornecedor.cotacao_id == cotacao_id
    ).first()
    if not resposta:
        raise HTTPException(status_code=404, detail="Resposta não encontrada")
    
    # Desmarcar todas as outras respostas
    session.query(RespostaFornecedor).filter(
        RespostaFornecedor.cotacao_id == cotacao_id
    ).update({"selecionada": 0})
    
    # Marcar a selecionada
    resposta.selecionada = 1
    cotacao.melhor_fornecedor_id = resposta.fornecedor_id
    cotacao.status = StatusCotacao.APROVADA
    
    session.commit()
    return {"message": "Fornecedor selecionado com sucesso"}


# =============================================================================
# CONVERSÃO PARA PEDIDO DE COMPRA
# =============================================================================

@router.post("/cotacoes/{cotacao_id}/converter-pedido", response_model=dict)
def converter_cotacao_para_pedido(
    cotacao_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:create"))
):
    """Converte uma cotação aprovada em pedido de compra"""
    cotacao = session.query(Cotacao).filter(Cotacao.id == cotacao_id).first()
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    if cotacao.status != StatusCotacao.APROVADA:
        raise HTTPException(status_code=400, detail="Cotação precisa estar aprovada")
    
    if not cotacao.melhor_fornecedor_id:
        raise HTTPException(status_code=400, detail="Nenhum fornecedor selecionado")
    
    if cotacao.convertida_pedido_id:
        raise HTTPException(status_code=400, detail="Cotação já foi convertida")
    
    # Buscar resposta selecionada
    resposta_selecionada = session.query(RespostaFornecedor).filter(
        RespostaFornecedor.cotacao_id == cotacao_id,
        RespostaFornecedor.selecionada == 1
    ).first()
    
    if not resposta_selecionada:
        raise HTTPException(status_code=400, detail="Nenhuma resposta selecionada")
    
    # Gerar número do pedido
    numero_pedido = gerar_proximo_codigo(session, PedidoCompra, "PC")
    
    # Criar pedido de compra
    db_pedido = PedidoCompra(
        numero=numero_pedido,
        fornecedor_id=cotacao.melhor_fornecedor_id,
        valor_total=resposta_selecionada.valor_total,
        observacoes=f"Pedido gerado da cotação {cotacao.numero}\n{cotacao.observacoes or ''}"
    )
    session.add(db_pedido)
    session.flush()
    
    # Adicionar itens do pedido
    for item_resposta in resposta_selecionada.itens_resposta:
        item_cotacao = session.query(ItemCotacao).filter(
            ItemCotacao.id == item_resposta.item_cotacao_id
        ).first()
        
        db_item = ItemPedidoCompra(
            pedido_id=db_pedido.id,
            material_id=item_cotacao.material_id,
            descricao=item_cotacao.descricao,
            quantidade=item_cotacao.quantidade,
            unidade=item_cotacao.unidade,
            preco_unitario=item_resposta.preco_unitario,
            preco_total=item_resposta.preco_total
        )
        session.add(db_item)
    
    # Atualizar cotação
    cotacao.convertida_pedido_id = db_pedido.id
    cotacao.status = StatusCotacao.CONVERTIDA
    
    session.commit()
    session.refresh(db_pedido)
    
    return {
        "message": "Cotação convertida com sucesso",
        "pedido_id": db_pedido.id,
        "numero_pedido": db_pedido.numero
    }


# =============================================================================
# COMPARATIVO DE FORNECEDORES
# =============================================================================

@router.get("/cotacoes/{cotacao_id}/comparativo")
def comparativo_fornecedores(
    cotacao_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:read"))
):
    """Gera comparativo entre respostas de fornecedores"""
    cotacao = session.query(Cotacao).filter(Cotacao.id == cotacao_id).first()
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    respostas = session.query(RespostaFornecedor).filter(
        RespostaFornecedor.cotacao_id == cotacao_id
    ).all()
    
    if not respostas:
        return {"message": "Nenhuma resposta cadastrada ainda"}
    
    # Montar comparativo
    comparativo = {
        "cotacao": {
            "numero": cotacao.numero,
            "descricao": cotacao.descricao
        },
        "fornecedores": []
    }
    
    for resposta in respostas:
        fornecedor_data = {
            "fornecedor_id": resposta.fornecedor_id,
            "fornecedor_nome": resposta.fornecedor.nome,
            "valor_total": resposta.valor_total,
            "prazo_entrega_dias": resposta.prazo_entrega_dias,
            "condicao_pagamento": resposta.condicao_pagamento,
            "selecionada": resposta.selecionada == 1,
            "itens": []
        }
        
        for item_resp in resposta.itens_resposta:
            item_cot = item_resp.item_cotacao
            fornecedor_data["itens"].append({
                "descricao": item_cot.descricao,
                "quantidade": item_cot.quantidade,
                "unidade": item_cot.unidade,
                "preco_unitario": item_resp.preco_unitario,
                "preco_total": item_resp.preco_total,
                "marca": item_resp.marca
            })
        
        comparativo["fornecedores"].append(fornecedor_data)
    
    # Ordenar por valor total
    comparativo["fornecedores"].sort(key=lambda x: x["valor_total"])
    
    return comparativo
