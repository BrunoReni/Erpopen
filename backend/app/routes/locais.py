from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db import get_session
from app.dependencies import require_permission
from app.schemas_modules import (
    LocalEstoqueCreate, LocalEstoqueRead, LocalEstoqueUpdate
)
from app.models_modules import LocalEstoque, EstoquePorLocal, Material
from app.helpers import gerar_codigo_local_estoque

router = APIRouter()


# =============================================================================
# LOCAIS DE ESTOQUE (ARMAZÉNS)
# =============================================================================

@router.get("/locais", response_model=List[LocalEstoqueRead])
def list_locais(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Lista todos os locais de estoque"""
    query = session.query(LocalEstoque)
    
    if ativo is not None:
        query = query.filter(LocalEstoque.ativo == ativo)
    
    if tipo:
        query = query.filter(LocalEstoque.tipo == tipo)
    
    locais = query.order_by(LocalEstoque.padrao.desc(), LocalEstoque.nome).offset(skip).limit(limit).all()
    return locais


@router.post("/locais", response_model=LocalEstoqueRead)
def create_local(
    local: LocalEstoqueCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:create"))
):
    """Cria um novo local de estoque"""
    # Gerar código sequencial
    codigo = gerar_codigo_local_estoque(session)
    
    # Se marcado como padrão, desmarcar outros
    if local.padrao == 1:
        session.query(LocalEstoque).update({"padrao": 0})
    
    # Criar local
    db_local = LocalEstoque(
        codigo=codigo,
        **local.dict()
    )
    session.add(db_local)
    session.commit()
    session.refresh(db_local)
    return db_local


@router.get("/locais/{local_id}", response_model=LocalEstoqueRead)
def get_local(
    local_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Busca um local de estoque por ID"""
    local = session.query(LocalEstoque).filter(LocalEstoque.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return local


@router.put("/locais/{local_id}", response_model=LocalEstoqueRead)
def update_local(
    local_id: int,
    local_update: LocalEstoqueUpdate,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:update"))
):
    """Atualiza um local de estoque"""
    db_local = session.query(LocalEstoque).filter(LocalEstoque.id == local_id).first()
    if not db_local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    
    update_data = local_update.dict(exclude_unset=True)
    
    # Se marcado como padrão, desmarcar outros
    if update_data.get('padrao') == 1:
        session.query(LocalEstoque).filter(LocalEstoque.id != local_id).update({"padrao": 0})
    
    # Atualizar campos
    for key, value in update_data.items():
        setattr(db_local, key, value)
    
    session.commit()
    session.refresh(db_local)
    return db_local


@router.delete("/locais/{local_id}")
def delete_local(
    local_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:delete"))
):
    """Deleta um local de estoque (desativa)"""
    db_local = session.query(LocalEstoque).filter(LocalEstoque.id == local_id).first()
    if not db_local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    
    # Verificar se há estoque neste local
    tem_estoque = session.query(EstoquePorLocal).filter(
        EstoquePorLocal.local_id == local_id,
        EstoquePorLocal.quantidade > 0
    ).first()
    
    if tem_estoque:
        raise HTTPException(
            status_code=400, 
            detail="Não é possível excluir local com estoque. Transfira os materiais primeiro."
        )
    
    # Não pode excluir o local padrão
    if db_local.padrao == 1:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir o local padrão. Defina outro local como padrão primeiro."
        )
    
    # Desativar ao invés de deletar
    db_local.ativo = 0
    session.commit()
    return {"message": "Local desativado com sucesso"}


@router.get("/locais/{local_id}/estoque")
def get_estoque_local(
    local_id: int,
    skip: int = 0,
    limit: int = 100,
    busca: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Lista o estoque de um local específico"""
    # Verificar se o local existe
    local = session.query(LocalEstoque).filter(LocalEstoque.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    
    # Buscar estoque do local
    query = session.query(
        EstoquePorLocal, Material
    ).join(
        Material, EstoquePorLocal.material_id == Material.id
    ).filter(
        EstoquePorLocal.local_id == local_id
    )
    
    # Filtro de busca
    if busca:
        query = query.filter(
            (Material.nome.ilike(f"%{busca}%")) |
            (Material.codigo.ilike(f"%{busca}%"))
        )
    
    # Paginação
    estoques = query.offset(skip).limit(limit).all()
    
    # Formatar resposta
    result = {
        "local": {
            "id": local.id,
            "codigo": local.codigo,
            "nome": local.nome,
            "tipo": local.tipo
        },
        "itens": []
    }
    
    for estoque, material in estoques:
        result["itens"].append({
            "material_id": material.id,
            "material_codigo": material.codigo,
            "material_nome": material.nome,
            "quantidade": estoque.quantidade,
            "estoque_minimo": estoque.estoque_minimo,
            "estoque_maximo": estoque.estoque_maximo,
            "localizacao_fisica": estoque.localizacao_fisica,
            "unidade": material.unidade_medida,
            "status": "critico" if estoque.quantidade < estoque.estoque_minimo else "normal"
        })
    
    return result


@router.post("/locais/{local_id}/transferir")
def transferir_estoque(
    local_id: int,
    destino_id: int,
    material_id: int,
    quantidade: float,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:update"))
):
    """Transfere estoque entre locais"""
    from app.helpers import processar_movimentacao_estoque
    
    # Validações
    if local_id == destino_id:
        raise HTTPException(status_code=400, detail="Local de origem e destino não podem ser iguais")
    
    if quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    
    # Verificar se os locais existem
    local_origem = session.query(LocalEstoque).filter(LocalEstoque.id == local_id).first()
    local_destino = session.query(LocalEstoque).filter(LocalEstoque.id == destino_id).first()
    
    if not local_origem:
        raise HTTPException(status_code=404, detail="Local de origem não encontrado")
    if not local_destino:
        raise HTTPException(status_code=404, detail="Local de destino não encontrado")
    
    # Verificar se o material existe
    material = session.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    
    # Processar transferência
    resultado = processar_movimentacao_estoque(
        material_id=material_id,
        tipo_movimento="TRANSFERENCIA",
        quantidade=quantidade,
        local_origem_id=local_id,
        local_destino_id=destino_id,
        db=session
    )
    
    if not resultado["sucesso"]:
        raise HTTPException(status_code=400, detail=resultado["mensagem"])
    
    # Registrar movimentação
    from app.models_modules import MovimentoEstoque
    movimento = MovimentoEstoque(
        material_id=material_id,
        tipo_movimento="TRANSFERENCIA",
        quantidade=quantidade,
        local_origem_id=local_id,
        local_destino_id=destino_id,
        observacao=f"Transferência de {local_origem.nome} para {local_destino.nome}"
    )
    session.add(movimento)
    session.commit()
    
    return {
        "message": "Transferência realizada com sucesso",
        "material": material.nome,
        "origem": local_origem.nome,
        "destino": local_destino.nome,
        "quantidade": quantidade,
        "estoque_total": resultado["estoque_total"]
    }


@router.get("/locais/{local_id}/estatisticas")
def get_estatisticas_local(
    local_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:read"))
):
    """Retorna estatísticas de um local de estoque"""
    # Verificar se o local existe
    local = session.query(LocalEstoque).filter(LocalEstoque.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    
    # Total de itens diferentes
    total_itens = session.query(EstoquePorLocal).filter(
        EstoquePorLocal.local_id == local_id
    ).count()
    
    # Total de itens com estoque
    itens_com_estoque = session.query(EstoquePorLocal).filter(
        EstoquePorLocal.local_id == local_id,
        EstoquePorLocal.quantidade > 0
    ).count()
    
    # Itens zerados
    itens_zerados = session.query(EstoquePorLocal).filter(
        EstoquePorLocal.local_id == local_id,
        EstoquePorLocal.quantidade == 0
    ).count()
    
    # Itens críticos (abaixo do mínimo)
    itens_criticos = session.query(EstoquePorLocal).filter(
        EstoquePorLocal.local_id == local_id,
        EstoquePorLocal.quantidade < EstoquePorLocal.estoque_minimo,
        EstoquePorLocal.estoque_minimo > 0
    ).count()
    
    return {
        "local": {
            "id": local.id,
            "codigo": local.codigo,
            "nome": local.nome,
            "tipo": local.tipo
        },
        "estatisticas": {
            "total_itens": total_itens,
            "itens_com_estoque": itens_com_estoque,
            "itens_zerados": itens_zerados,
            "itens_criticos": itens_criticos
        }
    }


@router.post("/locais/definir-padrao/{local_id}")
def definir_local_padrao(
    local_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("materiais:update"))
):
    """Define um local como padrão do sistema"""
    local = session.query(LocalEstoque).filter(LocalEstoque.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    
    if not local.ativo:
        raise HTTPException(status_code=400, detail="Não é possível definir local inativo como padrão")
    
    # Desmarcar todos os outros
    session.query(LocalEstoque).update({"padrao": 0})
    
    # Marcar este como padrão
    local.padrao = 1
    session.commit()
    
    return {"message": f"Local '{local.nome}' definido como padrão"}
