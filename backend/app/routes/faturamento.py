from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db import get_session
from app.dependencies import require_permission
from app.schemas_modules import (
    NotaFiscalCreate, NotaFiscalRead, NotaFiscalUpdate,
    StatusNotaFiscal, TipoNotaFiscal
)
from app.models_modules import NotaFiscal, ItemNotaFiscal, Cliente, Fornecedor, Material, MovimentoEstoque
from app.helpers import processar_movimentacao_estoque

router = APIRouter()


# =============================================================================
# NOTAS FISCAIS
# =============================================================================

def gerar_numero_nf(db: Session, serie: str = "1") -> str:
    """Gera número sequencial de nota fiscal"""
    ultima_nf = db.query(NotaFiscal).filter(
        NotaFiscal.serie == serie
    ).order_by(NotaFiscal.id.desc()).first()
    
    if ultima_nf and ultima_nf.numero:
        try:
            ultimo_numero = int(ultima_nf.numero)
            return str(ultimo_numero + 1).zfill(9)
        except:
            pass
    
    return "000000001"


def calcular_totais_nf(nf_data: dict, itens: list) -> dict:
    """Calcula os totais da nota fiscal"""
    valor_produtos = sum(item.get('valor_total', 0) for item in itens)
    valor_icms = sum(item.get('valor_icms', 0) for item in itens)
    valor_ipi = sum(item.get('valor_ipi', 0) for item in itens)
    
    # Valores adicionais da NF
    valor_frete = nf_data.get('valor_frete', 0)
    valor_seguro = nf_data.get('valor_seguro', 0)
    valor_desconto = nf_data.get('valor_desconto', 0)
    valor_outras_despesas = nf_data.get('valor_outras_despesas', 0)
    
    # Total = Produtos + IPI + Frete + Seguro + Outras - Desconto
    valor_total = (
        valor_produtos + valor_ipi + valor_frete + 
        valor_seguro + valor_outras_despesas - valor_desconto
    )
    
    return {
        'valor_produtos': valor_produtos,
        'valor_icms': valor_icms,
        'valor_ipi': valor_ipi,
        'valor_pis': 0.0,  # Implementar quando necessário
        'valor_cofins': 0.0,  # Implementar quando necessário
        'valor_total': valor_total
    }


@router.get("/notas-fiscais", response_model=List[NotaFiscalRead])
def list_notas_fiscais(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[TipoNotaFiscal] = Query(None),
    status: Optional[StatusNotaFiscal] = Query(None),
    cliente_id: Optional[int] = Query(None),
    data_inicial: Optional[str] = Query(None),
    data_final: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("vendas:read"))
):
    """Lista todas as notas fiscais com filtros"""
    query = session.query(NotaFiscal)
    
    if tipo:
        query = query.filter(NotaFiscal.tipo == tipo)
    
    if status:
        query = query.filter(NotaFiscal.status == status)
    
    if cliente_id:
        query = query.filter(NotaFiscal.cliente_id == cliente_id)
    
    if data_inicial:
        query = query.filter(NotaFiscal.data_emissao >= data_inicial)
    
    if data_final:
        query = query.filter(NotaFiscal.data_emissao <= data_final)
    
    notas = query.order_by(NotaFiscal.data_emissao.desc()).offset(skip).limit(limit).all()
    return notas


@router.post("/notas-fiscais", response_model=NotaFiscalRead)
def create_nota_fiscal(
    nf: NotaFiscalCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("vendas:create"))
):
    """Cria uma nova nota fiscal"""
    
    # Validações
    if nf.tipo == TipoNotaFiscal.SAIDA and not nf.cliente_id:
        raise HTTPException(status_code=400, detail="Cliente é obrigatório para NF de saída")
    
    if nf.tipo == TipoNotaFiscal.ENTRADA and not nf.fornecedor_id:
        raise HTTPException(status_code=400, detail="Fornecedor é obrigatório para NF de entrada")
    
    if not nf.itens or len(nf.itens) == 0:
        raise HTTPException(status_code=400, detail="Nota fiscal deve ter pelo menos um item")
    
    # Gerar número da NF se não informado
    numero_nf = nf.numero or gerar_numero_nf(session, nf.serie)
    
    # Preparar itens com totais calculados
    itens_data = []
    for item_input in nf.itens:
        item_dict = item_input.dict()
        
        # Calcular valor total do item
        valor_base = item_dict['quantidade'] * item_dict['valor_unitario']
        valor_total = (
            valor_base +
            item_dict.get('valor_frete', 0) +
            item_dict.get('valor_seguro', 0) +
            item_dict.get('valor_outras_despesas', 0) -
            item_dict.get('valor_desconto', 0)
        )
        item_dict['valor_total'] = valor_total
        
        # Se não informou valor_icms, calcular
        if item_dict.get('aliquota_icms', 0) > 0 and item_dict.get('valor_icms', 0) == 0:
            item_dict['valor_icms'] = valor_base * (item_dict['aliquota_icms'] / 100)
        
        # Se não informou valor_ipi, calcular
        if item_dict.get('aliquota_ipi', 0) > 0 and item_dict.get('valor_ipi', 0) == 0:
            item_dict['valor_ipi'] = valor_base * (item_dict['aliquota_ipi'] / 100)
        
        itens_data.append(item_dict)
    
    # Calcular totais da NF
    nf_dict = nf.dict(exclude={'itens'})
    totais = calcular_totais_nf(nf_dict, itens_data)
    
    # Criar NF
    db_nf = NotaFiscal(
        numero=numero_nf,
        **nf_dict,
        **totais,
        data_emissao=datetime.utcnow() if not nf.data_emissao else nf.data_emissao,
        status=StatusNotaFiscal.RASCUNHO
    )
    session.add(db_nf)
    session.flush()
    
    # Criar itens
    for item_dict in itens_data:
        db_item = ItemNotaFiscal(
            nota_fiscal_id=db_nf.id,
            **item_dict
        )
        session.add(db_item)
    
    session.commit()
    session.refresh(db_nf)
    return db_nf


@router.get("/notas-fiscais/{nf_id}", response_model=NotaFiscalRead)
def get_nota_fiscal(
    nf_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("vendas:read"))
):
    """Busca uma nota fiscal por ID"""
    nf = session.query(NotaFiscal).filter(NotaFiscal.id == nf_id).first()
    if not nf:
        raise HTTPException(status_code=404, detail="Nota fiscal não encontrada")
    return nf


@router.put("/notas-fiscais/{nf_id}", response_model=NotaFiscalRead)
def update_nota_fiscal(
    nf_id: int,
    nf_update: NotaFiscalUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("vendas:update"))
):
    """Atualiza uma nota fiscal"""
    db_nf = session.query(NotaFiscal).filter(NotaFiscal.id == nf_id).first()
    if not db_nf:
        raise HTTPException(status_code=404, detail="Nota fiscal não encontrada")
    
    # Não pode editar NF autorizada ou cancelada
    if db_nf.status in [StatusNotaFiscal.AUTORIZADA, StatusNotaFiscal.CANCELADA]:
        raise HTTPException(
            status_code=400, 
            detail=f"Não é possível editar nota fiscal com status {db_nf.status}"
        )
    
    update_data = nf_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_nf, key, value)
    
    session.commit()
    session.refresh(db_nf)
    return db_nf


@router.delete("/notas-fiscais/{nf_id}")
def delete_nota_fiscal(
    nf_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("vendas:delete"))
):
    """Cancela uma nota fiscal"""
    db_nf = session.query(NotaFiscal).filter(NotaFiscal.id == nf_id).first()
    if not db_nf:
        raise HTTPException(status_code=404, detail="Nota fiscal não encontrada")
    
    # Apenas rascunhos podem ser excluídos
    if db_nf.status != StatusNotaFiscal.RASCUNHO:
        # Cancelar ao invés de excluir
        db_nf.status = StatusNotaFiscal.CANCELADA
        session.commit()
        return {"message": "Nota fiscal cancelada com sucesso"}
    
    session.delete(db_nf)
    session.commit()
    return {"message": "Nota fiscal excluída com sucesso"}


@router.post("/notas-fiscais/{nf_id}/emitir")
def emitir_nota_fiscal(
    nf_id: int,
    baixar_estoque: bool = Query(True),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("vendas:update"))
):
    """Emite a nota fiscal e opcionalmente baixa o estoque"""
    db_nf = session.query(NotaFiscal).filter(NotaFiscal.id == nf_id).first()
    if not db_nf:
        raise HTTPException(status_code=404, detail="Nota fiscal não encontrada")
    
    if db_nf.status != StatusNotaFiscal.RASCUNHO:
        raise HTTPException(
            status_code=400,
            detail="Apenas notas em rascunho podem ser emitidas"
        )
    
    # Baixar estoque (se for NF de saída)
    if baixar_estoque and db_nf.tipo == TipoNotaFiscal.SAIDA:
        for item in db_nf.itens:
            if item.material_id:
                # Processar saída de estoque
                resultado = processar_movimentacao_estoque(
                    material_id=item.material_id,
                    tipo_movimento="SAIDA",
                    quantidade=item.quantidade,
                    db=session
                )
                
                if not resultado["sucesso"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Erro ao baixar estoque: {resultado['mensagem']}"
                    )
                
                # Registrar movimento
                movimento = MovimentoEstoque(
                    material_id=item.material_id,
                    tipo_movimento="SAIDA",
                    quantidade=item.quantidade,
                    documento=f"NF {db_nf.numero}",
                    observacao=f"Emissão da NF {db_nf.numero} - {item.descricao}"
                )
                session.add(movimento)
    
    # Dar entrada no estoque (se for NF de entrada)
    if baixar_estoque and db_nf.tipo == TipoNotaFiscal.ENTRADA:
        for item in db_nf.itens:
            if item.material_id:
                resultado = processar_movimentacao_estoque(
                    material_id=item.material_id,
                    tipo_movimento="ENTRADA",
                    quantidade=item.quantidade,
                    db=session
                )
                
                if not resultado["sucesso"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Erro ao dar entrada no estoque: {resultado['mensagem']}"
                    )
                
                movimento = MovimentoEstoque(
                    material_id=item.material_id,
                    tipo_movimento="ENTRADA",
                    quantidade=item.quantidade,
                    documento=f"NF {db_nf.numero}",
                    observacao=f"Recebimento da NF {db_nf.numero} - {item.descricao}"
                )
                session.add(movimento)
    
    # Atualizar status
    db_nf.status = StatusNotaFiscal.EMITIDA
    db_nf.data_emissao = datetime.utcnow()
    
    session.commit()
    session.refresh(db_nf)
    
    return {
        "message": "Nota fiscal emitida com sucesso",
        "numero": db_nf.numero,
        "status": db_nf.status,
        "estoque_baixado": baixar_estoque
    }


@router.get("/notas-fiscais/estatisticas/resumo")
def get_estatisticas_nf(
    data_inicial: Optional[str] = Query(None),
    data_final: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("vendas:read"))
):
    """Retorna estatísticas das notas fiscais"""
    query = session.query(NotaFiscal)
    
    if data_inicial:
        query = query.filter(NotaFiscal.data_emissao >= data_inicial)
    if data_final:
        query = query.filter(NotaFiscal.data_emissao <= data_final)
    
    notas = query.all()
    
    # Estatísticas
    total_nfs = len(notas)
    nfs_emitidas = len([nf for nf in notas if nf.status == StatusNotaFiscal.EMITIDA])
    nfs_autorizadas = len([nf for nf in notas if nf.status == StatusNotaFiscal.AUTORIZADA])
    nfs_canceladas = len([nf for nf in notas if nf.status == StatusNotaFiscal.CANCELADA])
    
    valor_total = sum(nf.valor_total for nf in notas if nf.status != StatusNotaFiscal.CANCELADA)
    
    # Por tipo
    nfs_saida = len([nf for nf in notas if nf.tipo == TipoNotaFiscal.SAIDA])
    nfs_entrada = len([nf for nf in notas if nf.tipo == TipoNotaFiscal.ENTRADA])
    
    return {
        "total_notas": total_nfs,
        "emitidas": nfs_emitidas,
        "autorizadas": nfs_autorizadas,
        "canceladas": nfs_canceladas,
        "valor_total": valor_total,
        "notas_saida": nfs_saida,
        "notas_entrada": nfs_entrada
    }
