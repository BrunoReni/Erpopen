"""Rotas para o módulo de Vendas/Comercial"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db import get_session
from app.models_modules import Cliente, PedidoVenda, ItemPedidoVenda, Material, ContaReceber, MovimentoEstoque, LocalEstoque, TipoMovimento
from app.schemas_modules import (
    ClienteCreate, ClienteUpdate, ClienteRead,
    PedidoVendaCreate, PedidoVendaUpdate, PedidoVendaRead,
    ItemPedidoVendaCreate, ItemPedidoVendaUpdate, ItemPedidoVendaRead
)
from app.helpers import gerar_codigo_cliente, gerar_codigo_pedido_venda, validar_cpf, validar_cnpj, processar_movimentacao_estoque

router = APIRouter()


@router.get("/clientes", response_model=List[ClienteRead])
def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    busca: Optional[str] = None,
    ativo: Optional[int] = None,
    db: Session = Depends(get_session)
):
    """Lista todos os clientes com filtros opcionais"""
    query = db.query(Cliente)
    
    # Filtro de busca
    if busca:
        query = query.filter(
            (Cliente.nome.contains(busca)) |
            (Cliente.razao_social.contains(busca)) |
            (Cliente.cpf_cnpj.contains(busca)) |
            (Cliente.codigo.contains(busca))
        )
    
    # Filtro por status
    if ativo is not None:
        query = query.filter(Cliente.ativo == ativo)
    
    clientes = query.offset(skip).limit(limit).all()
    return clientes


@router.get("/clientes/{cliente_id}", response_model=ClienteRead)
def buscar_cliente(cliente_id: int, db: Session = Depends(get_session)):
    """Busca um cliente específico por ID"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente


@router.post("/clientes", response_model=ClienteRead)
def criar_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_session)):
    """Cria um novo cliente"""
    
    # Validar CPF/CNPJ
    if cliente_data.cpf_cnpj:
        cpf_cnpj_limpo = ''.join(filter(str.isdigit, cliente_data.cpf_cnpj))
        
        if len(cpf_cnpj_limpo) == 11:  # CPF
            if not validar_cpf(cpf_cnpj_limpo):
                raise HTTPException(status_code=400, detail="CPF inválido")
        elif len(cpf_cnpj_limpo) == 14:  # CNPJ
            if not validar_cnpj(cpf_cnpj_limpo):
                raise HTTPException(status_code=400, detail="CNPJ inválido")
        else:
            raise HTTPException(status_code=400, detail="CPF/CNPJ deve ter 11 ou 14 dígitos")
    
    # Verificar se CPF/CNPJ já existe
    if cliente_data.cpf_cnpj:
        existe = db.query(Cliente).filter(Cliente.cpf_cnpj == cliente_data.cpf_cnpj).first()
        if existe:
            raise HTTPException(status_code=400, detail="CPF/CNPJ já cadastrado")
    
    # Gerar código automático
    codigo = gerar_codigo_cliente(db)
    
    # Criar cliente
    cliente = Cliente(
        codigo=codigo,
        **cliente_data.dict()
    )
    
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    
    return cliente


@router.put("/clientes/{cliente_id}", response_model=ClienteRead)
def atualizar_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdate,
    db: Session = Depends(get_session)
):
    """Atualiza um cliente existente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Validar CPF/CNPJ se foi alterado
    if cliente_data.cpf_cnpj and cliente_data.cpf_cnpj != cliente.cpf_cnpj:
        cpf_cnpj_limpo = ''.join(filter(str.isdigit, cliente_data.cpf_cnpj))
        
        if len(cpf_cnpj_limpo) == 11:  # CPF
            if not validar_cpf(cpf_cnpj_limpo):
                raise HTTPException(status_code=400, detail="CPF inválido")
        elif len(cpf_cnpj_limpo) == 14:  # CNPJ
            if not validar_cnpj(cpf_cnpj_limpo):
                raise HTTPException(status_code=400, detail="CNPJ inválido")
        
        # Verificar se já existe outro cliente com esse CPF/CNPJ
        existe = db.query(Cliente).filter(
            Cliente.cpf_cnpj == cliente_data.cpf_cnpj,
            Cliente.id != cliente_id
        ).first()
        if existe:
            raise HTTPException(status_code=400, detail="CPF/CNPJ já cadastrado para outro cliente")
    
    # Atualizar campos
    update_data = cliente_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cliente, key, value)
    
    db.commit()
    db.refresh(cliente)
    
    return cliente


@router.delete("/clientes/{cliente_id}")
def desativar_cliente(cliente_id: int, db: Session = Depends(get_session)):
    """Desativa (soft delete) um cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    cliente.ativo = 0
    db.commit()
    
    return {"message": "Cliente desativado com sucesso"}


@router.post("/clientes/{cliente_id}/ativar")
def ativar_cliente(cliente_id: int, db: Session = Depends(get_session)):
    """Reativa um cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    cliente.ativo = 1
    db.commit()
    
    return {"message": "Cliente ativado com sucesso"}


@router.get("/clientes/buscar/codigo/{codigo}", response_model=ClienteRead)
def buscar_cliente_por_codigo(codigo: str, db: Session = Depends(get_session)):
    """Busca um cliente por código"""
    cliente = db.query(Cliente).filter(Cliente.codigo == codigo).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente


# =============================================================================
# PEDIDOS DE VENDA
# =============================================================================

@router.get("/pedidos", response_model=List[PedidoVendaRead])
def listar_pedidos_venda(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    cliente_id: Optional[int] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    db: Session = Depends(get_session)
):
    """Lista pedidos de venda com filtros opcionais"""
    query = db.query(PedidoVenda)
    
    if status:
        query = query.filter(PedidoVenda.status == status)
    
    if cliente_id:
        query = query.filter(PedidoVenda.cliente_id == cliente_id)
    
    if data_inicio:
        try:
            data_inicio_dt = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
            query = query.filter(PedidoVenda.data_pedido >= data_inicio_dt)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim_dt = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
            query = query.filter(PedidoVenda.data_pedido <= data_fim_dt)
        except ValueError:
            pass
    
    pedidos = query.order_by(PedidoVenda.created_at.desc()).offset(skip).limit(limit).all()
    return pedidos


@router.post("/pedidos", response_model=PedidoVendaRead)
def criar_pedido_venda(pedido_data: PedidoVendaCreate, db: Session = Depends(get_session)):
    """Cria um novo pedido de venda"""
    
    # Validar cliente
    cliente = db.query(Cliente).filter(Cliente.id == pedido_data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if not cliente.ativo:
        raise HTTPException(status_code=400, detail="Cliente inativo")
    
    # Gerar código automático
    codigo = gerar_codigo_pedido_venda(db)
    
    # Calcular totais
    valor_produtos = 0.0
    valor_desconto_total = 0.0
    
    # Criar pedido
    pedido = PedidoVenda(
        codigo=codigo,
        cliente_id=pedido_data.cliente_id,
        vendedor_id=pedido_data.vendedor_id,
        data_entrega_prevista=pedido_data.data_entrega_prevista,
        condicao_pagamento=pedido_data.condicao_pagamento,
        valor_frete=pedido_data.valor_frete,
        observacoes=pedido_data.observacoes,
        status="orcamento"
    )
    
    # Adicionar itens
    for item_data in pedido_data.itens:
        # Validar material
        material = db.query(Material).filter(Material.id == item_data.material_id).first()
        if not material:
            raise HTTPException(status_code=404, detail=f"Material {item_data.material_id} não encontrado")
        
        # Calcular valores do item
        valor_bruto = item_data.quantidade * item_data.preco_unitario
        valor_desconto = valor_bruto * (item_data.percentual_desconto / 100)
        subtotal = valor_bruto - valor_desconto
        
        item = ItemPedidoVenda(
            material_id=item_data.material_id,
            quantidade=item_data.quantidade,
            preco_unitario=item_data.preco_unitario,
            percentual_desconto=item_data.percentual_desconto,
            valor_desconto=valor_desconto,
            subtotal=subtotal,
            observacao=item_data.observacao
        )
        
        pedido.itens.append(item)
        valor_produtos += valor_bruto
        valor_desconto_total += valor_desconto
    
    # Atualizar totais do pedido
    pedido.valor_produtos = valor_produtos
    pedido.valor_desconto = valor_desconto_total
    pedido.valor_total = valor_produtos - valor_desconto_total + pedido_data.valor_frete
    
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    
    return pedido


@router.get("/pedidos/{pedido_id}", response_model=PedidoVendaRead)
def buscar_pedido_venda(pedido_id: int, db: Session = Depends(get_session)):
    """Busca um pedido de venda por ID"""
    pedido = db.query(PedidoVenda).filter(PedidoVenda.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@router.put("/pedidos/{pedido_id}", response_model=PedidoVendaRead)
def atualizar_pedido_venda(
    pedido_id: int,
    pedido_data: PedidoVendaUpdate,
    db: Session = Depends(get_session)
):
    """Atualiza um pedido de venda (somente se estiver em orçamento)"""
    pedido = db.query(PedidoVenda).filter(PedidoVenda.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if pedido.status != "orcamento":
        raise HTTPException(
            status_code=400, 
            detail="Apenas pedidos em orçamento podem ser editados"
        )
    
    # Atualizar campos
    update_data = pedido_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pedido, key, value)
    
    pedido.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(pedido)
    
    return pedido


@router.delete("/pedidos/{pedido_id}")
def deletar_pedido_venda(pedido_id: int, db: Session = Depends(get_session)):
    """Deleta um pedido de venda (somente se estiver em orçamento)"""
    pedido = db.query(PedidoVenda).filter(PedidoVenda.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if pedido.status != "orcamento":
        raise HTTPException(
            status_code=400,
            detail="Apenas pedidos em orçamento podem ser excluídos"
        )
    
    db.delete(pedido)
    db.commit()
    
    return {"message": "Pedido excluído com sucesso"}


@router.post("/pedidos/{pedido_id}/itens", response_model=ItemPedidoVendaRead)
def adicionar_item_pedido(
    pedido_id: int,
    item_data: ItemPedidoVendaCreate,
    db: Session = Depends(get_session)
):
    """Adiciona um item ao pedido"""
    pedido = db.query(PedidoVenda).filter(PedidoVenda.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if pedido.status != "orcamento":
        raise HTTPException(status_code=400, detail="Apenas pedidos em orçamento podem ser editados")
    
    # Validar material
    material = db.query(Material).filter(Material.id == item_data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    
    # Calcular valores
    valor_bruto = item_data.quantidade * item_data.preco_unitario
    valor_desconto = valor_bruto * (item_data.percentual_desconto / 100)
    subtotal = valor_bruto - valor_desconto
    
    item = ItemPedidoVenda(
        pedido_id=pedido_id,
        material_id=item_data.material_id,
        quantidade=item_data.quantidade,
        preco_unitario=item_data.preco_unitario,
        percentual_desconto=item_data.percentual_desconto,
        valor_desconto=valor_desconto,
        subtotal=subtotal,
        observacao=item_data.observacao
    )
    
    db.add(item)
    
    # Recalcular totais do pedido
    pedido.valor_produtos += valor_bruto
    pedido.valor_desconto += valor_desconto
    pedido.valor_total = pedido.valor_produtos - pedido.valor_desconto + pedido.valor_frete
    pedido.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(item)
    
    return item


@router.put("/pedidos/{pedido_id}/itens/{item_id}", response_model=ItemPedidoVendaRead)
def atualizar_item_pedido(
    pedido_id: int,
    item_id: int,
    item_data: ItemPedidoVendaUpdate,
    db: Session = Depends(get_session)
):
    """Atualiza um item do pedido"""
    pedido = db.query(PedidoVenda).filter(PedidoVenda.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if pedido.status != "orcamento":
        raise HTTPException(status_code=400, detail="Apenas pedidos em orçamento podem ser editados")
    
    item = db.query(ItemPedidoVenda).filter(
        ItemPedidoVenda.id == item_id,
        ItemPedidoVenda.pedido_id == pedido_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    # Subtrair valores antigos
    pedido.valor_produtos -= item.quantidade * item.preco_unitario
    pedido.valor_desconto -= item.valor_desconto
    
    # Atualizar item
    update_data = item_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    
    # Recalcular valores do item
    valor_bruto = item.quantidade * item.preco_unitario
    item.valor_desconto = valor_bruto * (item.percentual_desconto / 100)
    item.subtotal = valor_bruto - item.valor_desconto
    
    # Adicionar novos valores
    pedido.valor_produtos += valor_bruto
    pedido.valor_desconto += item.valor_desconto
    pedido.valor_total = pedido.valor_produtos - pedido.valor_desconto + pedido.valor_frete
    pedido.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(item)
    
    return item


@router.delete("/pedidos/{pedido_id}/itens/{item_id}")
def remover_item_pedido(
    pedido_id: int,
    item_id: int,
    db: Session = Depends(get_session)
):
    """Remove um item do pedido"""
    pedido = db.query(PedidoVenda).filter(PedidoVenda.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if pedido.status != "orcamento":
        raise HTTPException(status_code=400, detail="Apenas pedidos em orçamento podem ser editados")
    
    item = db.query(ItemPedidoVenda).filter(
        ItemPedidoVenda.id == item_id,
        ItemPedidoVenda.pedido_id == pedido_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    # Subtrair valores do pedido
    pedido.valor_produtos -= item.quantidade * item.preco_unitario
    pedido.valor_desconto -= item.valor_desconto
    pedido.valor_total = pedido.valor_produtos - pedido.valor_desconto + pedido.valor_frete
    pedido.updated_at = datetime.utcnow()
    
    db.delete(item)
    db.commit()
    
    return {"message": "Item removido com sucesso"}


@router.post("/pedidos/{pedido_id}/aprovar")
def aprovar_pedido_venda(pedido_id: int, db: Session = Depends(get_session)):
    """Aprova um pedido de venda (valida estoque)"""
    pedido = db.query(PedidoVenda).filter(PedidoVenda.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if pedido.status != "orcamento":
        raise HTTPException(status_code=400, detail="Apenas pedidos em orçamento podem ser aprovados")
    
    # Validar estoque disponível para todos os itens
    for item in pedido.itens:
        material = db.query(Material).filter(Material.id == item.material_id).first()
        if material.estoque_atual < item.quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente para {material.nome}. Disponível: {material.estoque_atual}, Solicitado: {item.quantidade}"
            )
    
    pedido.status = "aprovado"
    pedido.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(pedido)
    
    return {"message": "Pedido aprovado com sucesso", "pedido": pedido}


@router.post("/pedidos/{pedido_id}/faturar")
def faturar_pedido_venda(pedido_id: int, db: Session = Depends(get_session)):
    """
    Fatura um pedido de venda:
    - Valida status = APROVADO
    - Valida estoque
    - Baixa estoque
    - Gera Conta a Receber
    - Atualiza status para FATURADO
    """
    pedido = db.query(PedidoVenda).filter(PedidoVenda.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if pedido.status != "aprovado":
        raise HTTPException(status_code=400, detail="Apenas pedidos aprovados podem ser faturados")
    
    try:
        # Obter local padrão
        local_padrao = db.query(LocalEstoque).filter(LocalEstoque.padrao == 1).first()
        if not local_padrao:
            # Se não houver local padrão, pegar o primeiro ativo
            local_padrao = db.query(LocalEstoque).filter(LocalEstoque.ativo == 1).first()
        
        if not local_padrao:
            raise HTTPException(status_code=400, detail="Nenhum local de estoque ativo encontrado")
        
        # Validar e baixar estoque para cada item
        for item in pedido.itens:
            material = db.query(Material).filter(Material.id == item.material_id).first()
            
            # Validar estoque novamente
            if material.estoque_atual < item.quantidade:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estoque insuficiente para {material.nome}"
                )
            
            # Criar movimentação de saída
            movimento = MovimentoEstoque(
                material_id=item.material_id,
                tipo_movimento=TipoMovimento.SAIDA,
                quantidade=item.quantidade,
                data_movimento=datetime.utcnow(),
                documento=pedido.codigo,
                observacao=f"Faturamento do pedido {pedido.codigo}",
                local_origem_id=local_padrao.id
            )
            db.add(movimento)
            
            # Processar movimentação (atualiza estoque)
            resultado = processar_movimentacao_estoque(
                material_id=item.material_id,
                tipo_movimento="SAIDA",
                quantidade=item.quantidade,
                local_origem_id=local_padrao.id,
                db=db
            )
            
            if not resultado["sucesso"]:
                raise HTTPException(status_code=400, detail=resultado["mensagem"])
        
        # Gerar Conta a Receber
        cliente = pedido.cliente
        data_vencimento = datetime.utcnow()
        
        # Calcular data de vencimento baseado nos dias do cliente
        from datetime import timedelta
        data_vencimento = data_vencimento + timedelta(days=cliente.dias_vencimento)
        
        conta_receber = ContaReceber(
            descricao=f"Faturamento do pedido {pedido.codigo}",
            cliente_id=pedido.cliente_id,
            cliente_nome=cliente.nome,
            pedido_venda_id=pedido.id,
            data_vencimento=data_vencimento,
            valor_original=pedido.valor_total,
            observacoes=f"Gerado automaticamente do pedido {pedido.codigo}"
        )
        db.add(conta_receber)
        
        # Atualizar pedido
        pedido.status = "faturado"
        pedido.data_faturamento = datetime.utcnow()
        pedido.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(pedido)
        
        return {
            "message": "Pedido faturado com sucesso",
            "pedido": pedido,
            "conta_receber_id": conta_receber.id
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao faturar pedido: {str(e)}")


@router.post("/pedidos/{pedido_id}/cancelar")
def cancelar_pedido_venda(pedido_id: int, db: Session = Depends(get_session)):
    """Cancela um pedido de venda"""
    pedido = db.query(PedidoVenda).filter(PedidoVenda.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if pedido.status == "faturado":
        raise HTTPException(status_code=400, detail="Pedidos faturados não podem ser cancelados")
    
    pedido.status = "cancelado"
    pedido.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(pedido)
    
    return {"message": "Pedido cancelado com sucesso", "pedido": pedido}
