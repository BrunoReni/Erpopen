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
