from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class StatusCompra(str, Enum):
    RASCUNHO = "rascunho"
    SOLICITADO = "solicitado"
    APROVADO = "aprovado"
    PEDIDO_ENVIADO = "pedido_enviado"
    RECEBIDO = "recebido"
    CANCELADO = "cancelado"


class StatusPagamento(str, Enum):
    PENDENTE = "pendente"
    PARCIAL = "parcial"
    PAGO = "pago"
    ATRASADO = "atrasado"


class TipoMovimento(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"
    TRANSFERENCIA = "transferencia"


# =============================================================================
# MÓDULO DE COMPRAS - SCHEMAS
# =============================================================================

# Fornecedor
class FornecedorBase(BaseModel):
    nome: str
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    ativo: int = 1


class FornecedorCreate(FornecedorBase):
    pass


class FornecedorUpdate(BaseModel):
    nome: Optional[str] = None
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    ativo: Optional[int] = None


class FornecedorRead(FornecedorBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Item Pedido Compra
class ItemPedidoCompraBase(BaseModel):
    material_id: Optional[int] = None
    descricao: str
    quantidade: float
    unidade: Optional[str] = "UN"
    preco_unitario: float


class ItemPedidoCompraCreate(ItemPedidoCompraBase):
    pass


class ItemPedidoCompraRead(ItemPedidoCompraBase):
    id: int
    pedido_id: int
    preco_total: float
    
    class Config:
        from_attributes = True


# Pedido Compra
class PedidoCompraBase(BaseModel):
    fornecedor_id: int
    data_entrega_prevista: Optional[datetime] = None
    observacoes: Optional[str] = None


class PedidoCompraCreate(PedidoCompraBase):
    itens: List[ItemPedidoCompraCreate]


class PedidoCompraUpdate(BaseModel):
    fornecedor_id: Optional[int] = None
    data_entrega_prevista: Optional[datetime] = None
    status: Optional[StatusCompra] = None
    observacoes: Optional[str] = None


class PedidoCompraRead(PedidoCompraBase):
    id: int
    numero: str
    data_pedido: datetime
    status: StatusCompra
    valor_total: float
    created_at: datetime
    itens: List[ItemPedidoCompraRead] = []
    
    class Config:
        from_attributes = True


# =============================================================================
# MÓDULO FINANCEIRO - SCHEMAS
# =============================================================================

# Conta Bancária
class ContaBancariaBase(BaseModel):
    nome: str
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    saldo_inicial: float = 0.0


class ContaBancariaCreate(ContaBancariaBase):
    pass


class ContaBancariaRead(ContaBancariaBase):
    id: int
    saldo_atual: float
    ativa: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Centro de Custo
class CentroCustoBase(BaseModel):
    codigo: str
    nome: str
    descricao: Optional[str] = None


class CentroCustoCreate(CentroCustoBase):
    pass


class CentroCustoRead(CentroCustoBase):
    id: int
    ativo: int
    
    class Config:
        from_attributes = True


# Conta a Pagar
class ContaPagarBase(BaseModel):
    descricao: str
    fornecedor_id: Optional[int] = None
    centro_custo_id: Optional[int] = None
    data_vencimento: datetime
    valor_original: float
    observacoes: Optional[str] = None


class ContaPagarCreate(ContaPagarBase):
    pass


class ContaPagarUpdate(BaseModel):
    data_pagamento: Optional[datetime] = None
    valor_pago: Optional[float] = None
    status: Optional[StatusPagamento] = None
    observacoes: Optional[str] = None


class ContaPagarRead(ContaPagarBase):
    id: int
    pedido_compra_id: Optional[int]
    data_emissao: datetime
    data_pagamento: Optional[datetime]
    valor_pago: float
    status: StatusPagamento
    created_at: datetime
    
    class Config:
        from_attributes = True


# Conta a Receber
class ContaReceberBase(BaseModel):
    descricao: str
    cliente: str
    centro_custo_id: Optional[int] = None
    data_vencimento: datetime
    valor_original: float
    observacoes: Optional[str] = None


class ContaReceberCreate(ContaReceberBase):
    pass


class ContaReceberUpdate(BaseModel):
    data_recebimento: Optional[datetime] = None
    valor_recebido: Optional[float] = None
    status: Optional[StatusPagamento] = None
    observacoes: Optional[str] = None


class ContaReceberRead(ContaReceberBase):
    id: int
    data_emissao: datetime
    data_recebimento: Optional[datetime]
    valor_recebido: float
    status: StatusPagamento
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# MÓDULO DE MATERIAIS - SCHEMAS
# =============================================================================

# Categoria Material
class CategoriaMaterialBase(BaseModel):
    nome: str
    descricao: Optional[str] = None


class CategoriaMaterialCreate(CategoriaMaterialBase):
    pass


class CategoriaMaterialRead(CategoriaMaterialBase):
    id: int
    ativa: int
    
    class Config:
        from_attributes = True


# Material
class MaterialBase(BaseModel):
    codigo: str
    nome: str
    descricao: Optional[str] = None
    categoria_id: Optional[int] = None
    unidade_medida: str
    estoque_minimo: float = 0.0
    estoque_maximo: float = 0.0
    localizacao: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    categoria_id: Optional[int] = None
    unidade_medida: Optional[str] = None
    estoque_minimo: Optional[float] = None
    estoque_maximo: Optional[float] = None
    localizacao: Optional[str] = None
    ativo: Optional[int] = None


class MaterialRead(MaterialBase):
    id: int
    estoque_atual: float
    preco_medio: float
    ativo: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Movimento Estoque
class MovimentoEstoqueBase(BaseModel):
    material_id: int
    tipo_movimento: TipoMovimento
    quantidade: float
    documento: Optional[str] = None
    observacao: Optional[str] = None


class MovimentoEstoqueCreate(MovimentoEstoqueBase):
    pass


class MovimentoEstoqueRead(MovimentoEstoqueBase):
    id: int
    data_movimento: datetime
    usuario_id: Optional[int]
    
    class Config:
        from_attributes = True
