from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db import get_session
from app.dependencies import require_permission
from app.schemas_modules import (
    CategoriaMaterialCreate, CategoriaMaterialRead,
    MaterialCreate, MaterialRead, MaterialUpdate,
    MovimentoEstoqueCreate, MovimentoEstoqueRead
)
from app.models_modules import CategoriaMaterial, Material, MovimentoEstoque, TipoMovimento

router = APIRouter()


# =============================================================================
# CATEGORIAS
# =============================================================================

@router.get("/categorias", response_model=List[CategoriaMaterialRead])
def list_categorias(
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Lista todas as categorias de materiais"""
    return session.query(CategoriaMaterial).filter(CategoriaMaterial.ativa == 1).all()


@router.post("/categorias", response_model=CategoriaMaterialRead)
def create_categoria(
    categoria: CategoriaMaterialCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:create"))
):
    """Cria uma nova categoria de material"""
    db_categoria = CategoriaMaterial(**categoria.dict())
    session.add(db_categoria)
    session.commit()
    session.refresh(db_categoria)
    return db_categoria


# =============================================================================
# MATERIAIS
# =============================================================================

@router.get("/materiais", response_model=List[MaterialRead])
def list_materiais(
    skip: int = 0,
    limit: int = 100,
    categoria_id: int = Query(None),
    ativo: int = Query(None),
    busca: str = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Lista todos os materiais"""
    query = session.query(Material)
    
    if categoria_id:
        query = query.filter(Material.categoria_id == categoria_id)
    
    if ativo is not None:
        query = query.filter(Material.ativo == ativo)
    
    if busca:
        query = query.filter(
            (Material.codigo.ilike(f"%{busca}%")) |
            (Material.nome.ilike(f"%{busca}%"))
        )
    
    return query.offset(skip).limit(limit).all()


@router.post("/materiais", response_model=MaterialRead)
def create_material(
    material: MaterialCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:create"))
):
    """Cria um novo material"""
    # Verificar se código já existe
    existing = session.query(Material).filter(Material.codigo == material.codigo).first()
    if existing:
        raise HTTPException(status_code=400, detail="Código de material já existe")
    
    db_material = Material(**material.dict())
    session.add(db_material)
    session.commit()
    session.refresh(db_material)
    return db_material


@router.get("/materiais/{material_id}", response_model=MaterialRead)
def get_material(
    material_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Busca um material por ID"""
    material = session.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    return material


@router.put("/materiais/{material_id}", response_model=MaterialRead)
def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:update"))
):
    """Atualiza um material"""
    material = session.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    
    for key, value in material_data.dict(exclude_unset=True).items():
        setattr(material, key, value)
    
    session.commit()
    session.refresh(material)
    return material


@router.delete("/materiais/{material_id}")
def delete_material(
    material_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:delete"))
):
    """Desativa um material"""
    material = session.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    
    material.ativo = 0
    session.commit()
    return {"message": "Material desativado com sucesso"}


# =============================================================================
# MOVIMENTOS DE ESTOQUE
# =============================================================================

@router.get("/movimentos", response_model=List[MovimentoEstoqueRead])
def list_movimentos(
    skip: int = 0,
    limit: int = 100,
    material_id: int = Query(None),
    tipo_movimento: str = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Lista todos os movimentos de estoque"""
    query = session.query(MovimentoEstoque)
    
    if material_id:
        query = query.filter(MovimentoEstoque.material_id == material_id)
    
    if tipo_movimento:
        query = query.filter(MovimentoEstoque.tipo_movimento == tipo_movimento)
    
    return query.order_by(MovimentoEstoque.data_movimento.desc()).offset(skip).limit(limit).all()


@router.post("/movimentos", response_model=MovimentoEstoqueRead)
def create_movimento(
    movimento: MovimentoEstoqueCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:create"))
):
    """Registra um movimento de estoque"""
    # Verificar se material existe
    material = session.query(Material).filter(Material.id == movimento.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    
    # Criar movimento
    db_movimento = MovimentoEstoque(**movimento.dict())
    session.add(db_movimento)
    
    # Atualizar estoque do material
    if movimento.tipo_movimento in [TipoMovimento.ENTRADA, TipoMovimento.AJUSTE]:
        material.estoque_atual += movimento.quantidade
    elif movimento.tipo_movimento in [TipoMovimento.SAIDA]:
        if material.estoque_atual < movimento.quantidade:
            raise HTTPException(status_code=400, detail="Estoque insuficiente")
        material.estoque_atual -= movimento.quantidade
    
    session.commit()
    session.refresh(db_movimento)
    return db_movimento


@router.get("/estoque-baixo")
def list_estoque_baixo(
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Lista materiais com estoque abaixo do mínimo"""
    materiais = session.query(Material).filter(
        Material.ativo == 1,
        Material.estoque_atual < Material.estoque_minimo
    ).all()
    
    return [
        {
            "id": m.id,
            "codigo": m.codigo,
            "nome": m.nome,
            "estoque_atual": m.estoque_atual,
            "estoque_minimo": m.estoque_minimo,
            "deficit": m.estoque_minimo - m.estoque_atual
        }
        for m in materiais
    ]


@router.get("/materiais/{material_id}/historico")
def get_historico_material(
    material_id: int,
    skip: int = 0,
    limit: int = 50,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Retorna o histórico de movimentações de um material"""
    material = session.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    
    movimentos = session.query(MovimentoEstoque).filter(
        MovimentoEstoque.material_id == material_id
    ).order_by(MovimentoEstoque.data_movimento.desc()).offset(skip).limit(limit).all()
    
    return {
        "material": {
            "id": material.id,
            "codigo": material.codigo,
            "nome": material.nome,
            "estoque_atual": material.estoque_atual
        },
        "movimentos": [
            {
                "id": m.id,
                "tipo_movimento": m.tipo_movimento,
                "quantidade": m.quantidade,
                "data_movimento": m.data_movimento,
                "documento": m.documento,
                "observacao": m.observacao
            }
            for m in movimentos
        ]
    }


# =============================================================================
# SALDO E ESTOQUE POR LOCAL
# =============================================================================

@router.get("/materiais/{material_id}/saldo")
def get_saldo_material(
    material_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Retorna o saldo total e por local de um material"""
    from app.models_modules import EstoquePorLocal, LocalEstoque
    from app.helpers import calcular_estoque_total
    
    material = session.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    
    # Buscar estoques por local
    estoques_locais = session.query(
        EstoquePorLocal, LocalEstoque
    ).join(
        LocalEstoque, EstoquePorLocal.local_id == LocalEstoque.id
    ).filter(
        EstoquePorLocal.material_id == material_id
    ).all()
    
    # Calcular total
    total = calcular_estoque_total(material_id, session)
    
    return {
        "material": {
            "id": material.id,
            "codigo": material.codigo,
            "nome": material.nome,
            "unidade_medida": material.unidade_medida
        },
        "estoque_total": total,
        "estoques_por_local": [
            {
                "local_id": estoque.local_id,
                "local_codigo": local.codigo,
                "local_nome": local.nome,
                "quantidade": estoque.quantidade,
                "updated_at": estoque.updated_at
            }
            for estoque, local in estoques_locais
        ]
    }


@router.get("/locais/{local_id}/estoque")
def get_estoque_por_local(
    local_id: int,
    skip: int = 0,
    limit: int = 100,
    busca: str = None,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Lista todos os materiais com estoque em um local específico"""
    from app.models_modules import EstoquePorLocal, LocalEstoque
    
    # Verificar se local existe
    local = session.query(LocalEstoque).filter(LocalEstoque.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local de estoque não encontrado")
    
    # Buscar estoques
    query = session.query(
        EstoquePorLocal, Material
    ).join(
        Material, EstoquePorLocal.material_id == Material.id
    ).filter(
        EstoquePorLocal.local_id == local_id,
        EstoquePorLocal.quantidade > 0  # Apenas com saldo
    )
    
    # Filtro de busca
    if busca:
        query = query.filter(
            (Material.codigo.contains(busca)) |
            (Material.nome.contains(busca))
        )
    
    estoques = query.offset(skip).limit(limit).all()
    
    return {
        "local": {
            "id": local.id,
            "codigo": local.codigo,
            "nome": local.nome,
            "tipo": local.tipo
        },
        "materiais": [
            {
                "material_id": material.id,
                "codigo": material.codigo,
                "nome": material.nome,
                "unidade_medida": material.unidade_medida,
                "quantidade": estoque.quantidade,
                "estoque_minimo": material.estoque_minimo,
                "estoque_maximo": material.estoque_maximo,
                "updated_at": estoque.updated_at
            }
            for estoque, material in estoques
        ]
    }


@router.post("/movimentacoes/processar")
def processar_movimentacao(
    movimento_data: MovimentoEstoqueCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:write"))
):
    """
    Processa uma movimentação de estoque
    Atualiza automaticamente os saldos por local e estoque total
    """
    from app.helpers import processar_movimentacao_estoque
    
    # Processar movimentação
    resultado = processar_movimentacao_estoque(
        material_id=movimento_data.material_id,
        tipo_movimento=movimento_data.tipo_movimento.value,
        quantidade=movimento_data.quantidade,
        local_origem_id=movimento_data.local_origem_id,
        local_destino_id=movimento_data.local_destino_id,
        db=session,
        permitir_negativo=False  # Não permite estoque negativo por padrão
    )
    
    if not resultado["sucesso"]:
        raise HTTPException(status_code=400, detail=resultado["mensagem"])
    
    # Criar registro de movimentação
    movimento = MovimentoEstoque(
        material_id=movimento_data.material_id,
        tipo_movimento=movimento_data.tipo_movimento,
        quantidade=movimento_data.quantidade,
        documento=movimento_data.documento,
        observacao=movimento_data.observacao,
        local_origem_id=movimento_data.local_origem_id,
        local_destino_id=movimento_data.local_destino_id,
        data_movimento=movimento_data.data_movimento or datetime.utcnow()
    )
    
    session.add(movimento)
    session.commit()
    session.refresh(movimento)
    
    return {
        "mensagem": resultado["mensagem"],
        "estoque_total": resultado["estoque_total"],
        "movimento": {
            "id": movimento.id,
            "tipo_movimento": movimento.tipo_movimento,
            "quantidade": movimento.quantidade,
            "data_movimento": movimento.data_movimento
        }
    }


@router.get("/relatorios/posicao-estoque")
def relatorio_posicao_estoque(
    local_id: int = None,
    categoria_id: int = None,
    apenas_zerados: bool = False,
    apenas_criticos: bool = False,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """
    Relatório de posição de estoque com diversos filtros
    """
    from app.models_modules import EstoquePorLocal
    from sqlalchemy import func
    
    if local_id:
        # Posição por local específico
        query = session.query(
            Material,
            EstoquePorLocal.quantidade
        ).join(
            EstoquePorLocal, Material.id == EstoquePorLocal.material_id
        ).filter(
            EstoquePorLocal.local_id == local_id
        )
    else:
        # Posição consolidada (usa estoque_atual do material)
        query = session.query(Material, Material.estoque_atual)
    
    # Filtro por categoria
    if categoria_id:
        query = query.filter(Material.categoria_id == categoria_id)
    
    # Filtro por zerados
    if apenas_zerados:
        if local_id:
            query = query.filter(EstoquePorLocal.quantidade == 0)
        else:
            query = query.filter(Material.estoque_atual == 0)
    
    # Filtro por críticos (abaixo do mínimo)
    if apenas_criticos:
        if local_id:
            query = query.filter(EstoquePorLocal.quantidade < Material.estoque_minimo)
        else:
            query = query.filter(Material.estoque_atual < Material.estoque_minimo)
    
    # Apenas ativos
    query = query.filter(Material.ativo == 1)
    
    materiais = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": material.id,
            "codigo": material.codigo,
            "nome": material.nome,
            "unidade_medida": material.unidade_medida,
            "quantidade": quantidade,
            "estoque_minimo": material.estoque_minimo,
            "estoque_maximo": material.estoque_maximo,
            "status": "CRÍTICO" if quantidade < material.estoque_minimo 
                     else "ZERADO" if quantidade == 0 
                     else "NORMAL",
            "categoria": material.categoria.nome if material.categoria else None
        }
        for material, quantidade in materiais
    ]
