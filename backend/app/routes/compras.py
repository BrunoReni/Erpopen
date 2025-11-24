from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db import get_session
from app.dependencies import require_permission
from app.schemas_modules import (
    FornecedorCreate, FornecedorRead, FornecedorUpdate,
    PedidoCompraCreate, PedidoCompraRead, PedidoCompraUpdate
)
from app.models_modules import Fornecedor, PedidoCompra, ItemPedidoCompra
from datetime import datetime

router = APIRouter()


# =============================================================================
# FORNECEDORES
# =============================================================================

@router.get("/fornecedores", response_model=List[FornecedorRead])
def list_fornecedores(
    skip: int = 0,
    limit: int = 100,
    ativo: int = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:read"))
):
    """Lista todos os fornecedores"""
    query = session.query(Fornecedor)
    
    if ativo is not None:
        query = query.filter(Fornecedor.ativo == ativo)
    
    fornecedores = query.offset(skip).limit(limit).all()
    return fornecedores


@router.post("/fornecedores", response_model=FornecedorRead)
def create_fornecedor(
    fornecedor: FornecedorCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:create"))
):
    """Cria um novo fornecedor"""
    db_fornecedor = Fornecedor(**fornecedor.dict())
    session.add(db_fornecedor)
    session.commit()
    session.refresh(db_fornecedor)
    return db_fornecedor


@router.get("/fornecedores/{fornecedor_id}", response_model=FornecedorRead)
def get_fornecedor(
    fornecedor_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:read"))
):
    """Busca um fornecedor por ID"""
    fornecedor = session.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return fornecedor


@router.put("/fornecedores/{fornecedor_id}", response_model=FornecedorRead)
def update_fornecedor(
    fornecedor_id: int,
    fornecedor_data: FornecedorUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:update"))
):
    """Atualiza um fornecedor"""
    fornecedor = session.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    for key, value in fornecedor_data.dict(exclude_unset=True).items():
        setattr(fornecedor, key, value)
    
    session.commit()
    session.refresh(fornecedor)
    return fornecedor


@router.delete("/fornecedores/{fornecedor_id}")
def delete_fornecedor(
    fornecedor_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:delete"))
):
    """Desativa um fornecedor"""
    fornecedor = session.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    fornecedor.ativo = 0
    session.commit()
    return {"message": "Fornecedor desativado com sucesso"}


# =============================================================================
# PEDIDOS DE COMPRA
# =============================================================================

@router.get("/pedidos", response_model=List[PedidoCompraRead])
def list_pedidos(
    skip: int = 0,
    limit: int = 100,
    fornecedor_id: int = Query(None),
    status: str = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:read"))
):
    """Lista todos os pedidos de compra"""
    query = session.query(PedidoCompra)
    
    if fornecedor_id:
        query = query.filter(PedidoCompra.fornecedor_id == fornecedor_id)
    
    if status:
        query = query.filter(PedidoCompra.status == status)
    
    pedidos = query.order_by(PedidoCompra.created_at.desc()).offset(skip).limit(limit).all()
    return pedidos


@router.post("/pedidos", response_model=PedidoCompraRead)
def create_pedido(
    pedido: PedidoCompraCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:create"))
):
    """Cria um novo pedido de compra"""
    # Verificar se fornecedor existe
    fornecedor = session.query(Fornecedor).filter(Fornecedor.id == pedido.fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    # Gerar número do pedido
    ultimo_pedido = session.query(PedidoCompra).order_by(PedidoCompra.id.desc()).first()
    proximo_numero = 1 if not ultimo_pedido else int(ultimo_pedido.numero.split('-')[-1]) + 1
    numero_pedido = f"PC-{datetime.now().year}-{proximo_numero:05d}"
    
    # Criar pedido
    db_pedido = PedidoCompra(
        numero=numero_pedido,
        fornecedor_id=pedido.fornecedor_id,
        data_entrega_prevista=pedido.data_entrega_prevista,
        observacoes=pedido.observacoes
    )
    
    # Adicionar itens e calcular total
    valor_total = 0.0
    for item_data in pedido.itens:
        preco_total = item_data.quantidade * item_data.preco_unitario
        valor_total += preco_total
        
        item = ItemPedidoCompra(
            **item_data.dict(),
            preco_total=preco_total
        )
        db_pedido.itens.append(item)
    
    db_pedido.valor_total = valor_total
    
    session.add(db_pedido)
    session.commit()
    session.refresh(db_pedido)
    return db_pedido


@router.get("/pedidos/{pedido_id}", response_model=PedidoCompraRead)
def get_pedido(
    pedido_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:read"))
):
    """Busca um pedido de compra por ID"""
    pedido = session.query(PedidoCompra).filter(PedidoCompra.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@router.put("/pedidos/{pedido_id}", response_model=PedidoCompraRead)
def update_pedido(
    pedido_id: int,
    pedido_data: PedidoCompraUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:update"))
):
    """Atualiza um pedido de compra"""
    pedido = session.query(PedidoCompra).filter(PedidoCompra.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    for key, value in pedido_data.dict(exclude_unset=True).items():
        setattr(pedido, key, value)
    
    pedido.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(pedido)
    return pedido


@router.delete("/pedidos/{pedido_id}")
def delete_pedido(
    pedido_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:delete"))
):
    """Cancela um pedido de compra"""
    pedido = session.query(PedidoCompra).filter(PedidoCompra.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    pedido.status = "cancelado"
    session.commit()
    return {"message": "Pedido cancelado com sucesso"}


@router.post("/pedidos/{pedido_id}/aprovar")
def aprovar_pedido(
    pedido_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("compras:update"))
):
    """Aprova um pedido de compra"""
    pedido = session.query(PedidoCompra).filter(PedidoCompra.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if pedido.status != "solicitado":
        raise HTTPException(status_code=400, detail="Apenas pedidos solicitados podem ser aprovados")
    
    pedido.status = "aprovado"
    session.commit()
    return {"message": "Pedido aprovado com sucesso"}
