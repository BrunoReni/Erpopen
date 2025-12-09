from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
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


class StatusCotacao(str, Enum):
    RASCUNHO = "rascunho"
    ENVIADA = "enviada"
    RESPONDIDA = "respondida"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    CONVERTIDA = "convertida"
    CANCELADA = "cancelada"


class StatusNotaFiscal(str, Enum):
    RASCUNHO = "rascunho"
    EMITIDA = "emitida"
    AUTORIZADA = "autorizada"
    CANCELADA = "cancelada"
    DENEGADA = "denegada"


class TipoNotaFiscal(str, Enum):
    SAIDA = "saida"
    ENTRADA = "entrada"
    DEVOLUCAO = "devolucao"


class TipoMovimentacaoBancaria(str, Enum):
    DEPOSITO = "deposito"
    SAQUE = "saque"
    TARIFA = "tarifa"
    TRANSFERENCIA_ENTRADA = "transferencia_entrada"
    TRANSFERENCIA_SAIDA = "transferencia_saida"
    JUROS = "juros"
    ESTORNO = "estorno"
    OUTROS = "outros"


class StatusPedidoVenda(str, Enum):
    ORCAMENTO = "orcamento"
    APROVADO = "aprovado"
    FATURADO = "faturado"
    CANCELADO = "cancelado"


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
    data_saldo_inicial: Optional[date] = None


class ContaBancariaCreate(ContaBancariaBase):
    @field_validator('saldo_inicial')
    @classmethod
    def saldo_nao_negativo(cls, v):
        if v < 0:
            raise ValueError('Saldo inicial não pode ser negativo')
        return v


class ContaBancariaUpdate(BaseModel):
    nome: Optional[str] = None
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    ativa: Optional[int] = None


class ContaBancariaRead(ContaBancariaBase):
    id: int
    saldo_atual: float
    ativa: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Saldo Diário
class SaldoDiarioBase(BaseModel):
    conta_bancaria_id: int
    data: date
    saldo_anterior: float = 0.0
    total_entradas: float = 0.0
    total_saidas: float = 0.0
    saldo_final: float = 0.0


class SaldoDiarioRead(SaldoDiarioBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Movimentação Bancária
class MovimentacaoBancariaBase(BaseModel):
    conta_bancaria_id: int
    tipo: TipoMovimentacaoBancaria
    natureza: str  # ENTRADA ou SAIDA
    valor: float
    descricao: str
    data_movimentacao: Optional[datetime] = None
    data_competencia: Optional[date] = None
    conta_pagar_id: Optional[int] = None
    conta_receber_id: Optional[int] = None
    transferencia_vinculada_id: Optional[int] = None


class MovimentacaoBancariaCreate(MovimentacaoBancariaBase):
    @field_validator('valor')
    @classmethod
    def valor_positivo(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser positivo')
        return v
    
    @field_validator('natureza')
    @classmethod
    def natureza_valida(cls, v):
        if v not in ['ENTRADA', 'SAIDA']:
            raise ValueError('Natureza deve ser ENTRADA ou SAIDA')
        return v


class MovimentacaoBancariaUpdate(BaseModel):
    tipo: Optional[TipoMovimentacaoBancaria] = None
    natureza: Optional[str] = None
    valor: Optional[float] = None
    descricao: Optional[str] = None
    data_movimentacao: Optional[datetime] = None
    data_competencia: Optional[date] = None
    conta_pagar_id: Optional[int] = None
    conta_receber_id: Optional[int] = None


class MovimentacaoBancariaRead(MovimentacaoBancariaBase):
    id: int
    conciliado: bool
    data_conciliacao: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Transferência entre contas
class TransferenciaCreate(BaseModel):
    conta_origem_id: int
    conta_destino_id: int
    valor: float
    data: datetime
    descricao: str
    
    @field_validator('valor')
    @classmethod
    def valor_positivo(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser positivo')
        return v


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
    juros: float
    desconto: float
    status: StatusPagamento
    created_at: datetime
    
    class Config:
        from_attributes = True


# Conta a Receber
class ContaReceberBase(BaseModel):
    descricao: str
    cliente_id: int
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
    cliente_nome: Optional[str] = None
    data_emissao: datetime
    data_recebimento: Optional[datetime]
    valor_recebido: float
    juros: float
    desconto: float
    status: StatusPagamento
    created_at: datetime
    
    class Config:
        from_attributes = True


# Baixa Conta a Pagar
class BaixaContaPagar(BaseModel):
    valor_pago: float
    juros: Optional[float] = 0.0
    desconto: Optional[float] = 0.0
    conta_bancaria_id: int
    data_pagamento: Optional[datetime] = None
    observacoes: Optional[str] = None


# Baixa Conta a Receber
class BaixaContaReceber(BaseModel):
    valor_recebido: float
    juros: Optional[float] = 0.0
    desconto: Optional[float] = 0.0
    conta_bancaria_id: int
    data_recebimento: Optional[datetime] = None
    observacoes: Optional[str] = None


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


# =============================================================================
# NOVOS SCHEMAS - FASE 1
# =============================================================================

# -----------------------------------------------------------------------------
# CLIENTES
# -----------------------------------------------------------------------------

class ClienteBase(BaseModel):
    nome: str
    razao_social: Optional[str] = None
    cpf_cnpj: str
    tipo_pessoa: str = "PF"
    email: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    tipo_cliente: str = "varejo"
    limite_credito: float = 0.0
    dias_vencimento: int = 30
    parceiro_vinculado_id: Optional[int] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    razao_social: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    tipo_pessoa: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    tipo_cliente: Optional[str] = None
    limite_credito: Optional[float] = None
    dias_vencimento: Optional[int] = None
    ativo: Optional[int] = None


class ClienteRead(ClienteBase):
    id: int
    codigo: str
    ativo: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# -----------------------------------------------------------------------------
# PEDIDOS DE VENDA
# -----------------------------------------------------------------------------

# Item Pedido Venda
class ItemPedidoVendaBase(BaseModel):
    material_id: int
    quantidade: float
    preco_unitario: float
    percentual_desconto: float = 0.0
    observacao: Optional[str] = None


class ItemPedidoVendaCreate(ItemPedidoVendaBase):
    pass


class ItemPedidoVendaUpdate(BaseModel):
    quantidade: Optional[float] = None
    preco_unitario: Optional[float] = None
    percentual_desconto: Optional[float] = None
    observacao: Optional[str] = None


class ItemPedidoVendaRead(ItemPedidoVendaBase):
    id: int
    pedido_id: int
    valor_desconto: float
    subtotal: float
    
    class Config:
        from_attributes = True


# Pedido Venda
class PedidoVendaBase(BaseModel):
    cliente_id: int
    vendedor_id: Optional[int] = None
    data_entrega_prevista: Optional[datetime] = None
    condicao_pagamento: Optional[str] = None
    valor_frete: float = 0.0
    observacoes: Optional[str] = None


class PedidoVendaCreate(PedidoVendaBase):
    itens: List[ItemPedidoVendaCreate]


class PedidoVendaUpdate(BaseModel):
    cliente_id: Optional[int] = None
    vendedor_id: Optional[int] = None
    data_entrega_prevista: Optional[datetime] = None
    condicao_pagamento: Optional[str] = None
    valor_frete: Optional[float] = None
    observacoes: Optional[str] = None
    status: Optional[StatusPedidoVenda] = None


class PedidoVendaRead(PedidoVendaBase):
    id: int
    codigo: str
    data_pedido: datetime
    data_faturamento: Optional[datetime] = None
    status: str
    valor_produtos: float
    valor_desconto: float
    valor_total: float
    created_at: datetime
    updated_at: datetime
    itens: List[ItemPedidoVendaRead] = []
    
    class Config:
        from_attributes = True



# -----------------------------------------------------------------------------
# UNIDADES DE MEDIDA
# -----------------------------------------------------------------------------

class UnidadeMedidaBase(BaseModel):
    sigla: str
    nome: str
    tipo: Optional[str] = None
    permite_decimal: int = 1
    unidade_base_id: Optional[int] = None
    fator_conversao: float = 1.0


class UnidadeMedidaCreate(UnidadeMedidaBase):
    pass


class UnidadeMedidaUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    permite_decimal: Optional[int] = None
    ativa: Optional[int] = None


class UnidadeMedidaRead(UnidadeMedidaBase):
    id: int
    ativa: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# -----------------------------------------------------------------------------
# LOCAIS DE ESTOQUE
# -----------------------------------------------------------------------------

class LocalEstoqueBase(BaseModel):
    codigo: str
    nome: str
    tipo: str = "almoxarifado"
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    responsavel: Optional[str] = None
    telefone: Optional[str] = None
    padrao: int = 0


class LocalEstoqueCreate(LocalEstoqueBase):
    pass


class LocalEstoqueUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    responsavel: Optional[str] = None
    telefone: Optional[str] = None
    padrao: Optional[int] = None
    ativo: Optional[int] = None


class LocalEstoqueRead(LocalEstoqueBase):
    id: int
    ativo: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# -----------------------------------------------------------------------------
# LOCAIS DE ESTOQUE (ARMAZÉNS)
# -----------------------------------------------------------------------------

class LocalEstoqueBase(BaseModel):
    nome: str
    tipo: str = "almoxarifado"  # almoxarifado, loja, deposito, producao
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    responsavel: Optional[str] = None
    telefone: Optional[str] = None
    ativo: int = 1
    padrao: int = 0


class LocalEstoqueCreate(LocalEstoqueBase):
    pass


class LocalEstoqueUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    responsavel: Optional[str] = None
    telefone: Optional[str] = None
    ativo: Optional[int] = None
    padrao: Optional[int] = None


class LocalEstoqueRead(LocalEstoqueBase):
    id: int
    codigo: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# -----------------------------------------------------------------------------
# ESTOQUE POR LOCAL
# -----------------------------------------------------------------------------

class EstoquePorLocalBase(BaseModel):
    material_id: int
    local_id: int
    quantidade: float = 0.0
    estoque_minimo: float = 0.0
    estoque_maximo: float = 0.0
    localizacao_fisica: Optional[str] = None


class EstoquePorLocalCreate(EstoquePorLocalBase):
    pass


class EstoquePorLocalUpdate(BaseModel):
    quantidade: Optional[float] = None
    estoque_minimo: Optional[float] = None
    estoque_maximo: Optional[float] = None
    localizacao_fisica: Optional[str] = None


class EstoquePorLocalRead(EstoquePorLocalBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# MÓDULO DE COTAÇÕES - SCHEMAS
# =============================================================================

# Item Cotação
class ItemCotacaoBase(BaseModel):
    material_id: Optional[int] = None
    descricao: str
    quantidade: float
    unidade: str = "UN"
    observacoes: Optional[str] = None


class ItemCotacaoCreate(ItemCotacaoBase):
    pass


class ItemCotacaoRead(ItemCotacaoBase):
    id: int
    cotacao_id: int
    
    class Config:
        from_attributes = True


# Item Resposta Fornecedor
class ItemRespostaFornecedorBase(BaseModel):
    item_cotacao_id: int
    preco_unitario: float
    marca: Optional[str] = None
    observacoes: Optional[str] = None


class ItemRespostaFornecedorCreate(ItemRespostaFornecedorBase):
    pass


class ItemRespostaFornecedorRead(ItemRespostaFornecedorBase):
    id: int
    resposta_id: int
    preco_total: float
    
    class Config:
        from_attributes = True


# Resposta Fornecedor
class RespostaFornecedorBase(BaseModel):
    fornecedor_id: int
    prazo_entrega_dias: Optional[int] = None
    condicao_pagamento: Optional[str] = None
    observacoes: Optional[str] = None


class RespostaFornecedorCreate(RespostaFornecedorBase):
    itens: List[ItemRespostaFornecedorCreate]


class RespostaFornecedorRead(RespostaFornecedorBase):
    id: int
    cotacao_id: int
    data_resposta: datetime
    valor_total: float
    selecionada: int
    itens_resposta: List[ItemRespostaFornecedorRead] = []
    
    class Config:
        from_attributes = True


# Cotação
class CotacaoBase(BaseModel):
    descricao: str
    data_limite_resposta: Optional[datetime] = None
    observacoes: Optional[str] = None


class CotacaoCreate(CotacaoBase):
    itens: List[ItemCotacaoCreate]


class CotacaoUpdate(BaseModel):
    descricao: Optional[str] = None
    data_limite_resposta: Optional[datetime] = None
    status: Optional[StatusCotacao] = None
    observacoes: Optional[str] = None


class CotacaoRead(CotacaoBase):
    id: int
    numero: str
    data_solicitacao: datetime
    status: StatusCotacao
    convertida_pedido_id: Optional[int] = None
    melhor_fornecedor_id: Optional[int] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    itens: List[ItemCotacaoRead] = []
    respostas: List[RespostaFornecedorRead] = []
    
    class Config:
        from_attributes = True


# =============================================================================
# MÓDULO DE FATURAMENTO / NOTAS FISCAIS - SCHEMAS
# =============================================================================

# Item Nota Fiscal
class ItemNotaFiscalBase(BaseModel):
    material_id: Optional[int] = None
    codigo_produto: Optional[str] = None
    descricao: str
    ncm: Optional[str] = None
    unidade: str
    quantidade: float
    valor_unitario: float
    valor_desconto: float = 0.0
    valor_frete: float = 0.0
    valor_seguro: float = 0.0
    valor_outras_despesas: float = 0.0
    aliquota_icms: float = 0.0
    valor_icms: float = 0.0
    aliquota_ipi: float = 0.0
    valor_ipi: float = 0.0
    cfop: Optional[str] = None


class ItemNotaFiscalCreate(ItemNotaFiscalBase):
    pass


class ItemNotaFiscalRead(ItemNotaFiscalBase):
    id: int
    nota_fiscal_id: int
    valor_total: float
    
    class Config:
        from_attributes = True


# Nota Fiscal
class NotaFiscalBase(BaseModel):
    numero: Optional[str] = None
    serie: str = "1"
    tipo: TipoNotaFiscal = TipoNotaFiscal.SAIDA
    data_emissao: Optional[datetime] = None
    data_saida: Optional[datetime] = None
    cliente_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    pedido_venda_id: Optional[int] = None
    pedido_compra_id: Optional[int] = None
    valor_frete: float = 0.0
    valor_seguro: float = 0.0
    valor_desconto: float = 0.0
    valor_outras_despesas: float = 0.0
    natureza_operacao: str = "Venda de mercadoria"
    cfop: Optional[str] = None
    observacao: Optional[str] = None
    informacoes_adicionais: Optional[str] = None


class NotaFiscalCreate(NotaFiscalBase):
    itens: List[ItemNotaFiscalCreate]


class NotaFiscalUpdate(BaseModel):
    numero: Optional[str] = None
    serie: Optional[str] = None
    data_emissao: Optional[datetime] = None
    data_saida: Optional[datetime] = None
    valor_frete: Optional[float] = None
    valor_seguro: Optional[float] = None
    valor_desconto: Optional[float] = None
    valor_outras_despesas: Optional[float] = None
    natureza_operacao: Optional[str] = None
    cfop: Optional[str] = None
    observacao: Optional[str] = None
    informacoes_adicionais: Optional[str] = None
    status: Optional[StatusNotaFiscal] = None


class NotaFiscalRead(NotaFiscalBase):
    id: int
    valor_produtos: float
    valor_icms: float
    valor_ipi: float
    valor_pis: float
    valor_cofins: float
    valor_total: float
    chave_acesso: Optional[str] = None
    protocolo_autorizacao: Optional[str] = None
    status: StatusNotaFiscal
    usuario_emissao_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    itens: List[ItemNotaFiscalRead] = []
    
    class Config:
        from_attributes = True

