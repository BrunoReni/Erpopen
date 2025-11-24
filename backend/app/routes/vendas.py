"""Rotas para o módulo de Vendas/Comercial"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_session
from app.models_modules import Cliente
from app.schemas_modules import ClienteCreate, ClienteUpdate, ClienteRead
from app.helpers import gerar_codigo_cliente, validar_cpf, validar_cnpj

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
