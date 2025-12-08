from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum, UniqueConstraint, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db import Base


class StatusCompra(str, enum.Enum):
    RASCUNHO = "rascunho"
    SOLICITADO = "solicitado"
    APROVADO = "aprovado"
    PEDIDO_ENVIADO = "pedido_enviado"
    RECEBIDO = "recebido"
    CANCELADO = "cancelado"


class StatusPagamento(str, enum.Enum):
    PENDENTE = "pendente"
    PARCIAL = "parcial"
    PAGO = "pago"
    ATRASADO = "atrasado"


class TipoMovimento(str, enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"
    TRANSFERENCIA = "transferencia"


class StatusVenda(str, enum.Enum):
    ORCAMENTO = "orcamento"
    APROVADO = "aprovado"
    FATURADO = "faturado"
    CANCELADO = "cancelado"
    ENTREGUE = "entregue"


class StatusCotacao(str, enum.Enum):
    RASCUNHO = "rascunho"
    ENVIADA = "enviada"
    RESPONDIDA = "respondida"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    CONVERTIDA = "convertida"
    CANCELADA = "cancelada"


class StatusNotaFiscal(str, enum.Enum):
    RASCUNHO = "rascunho"
    EMITIDA = "emitida"
    AUTORIZADA = "autorizada"
    CANCELADA = "cancelada"
    DENEGADA = "denegada"


class TipoNotaFiscal(str, enum.Enum):
    SAIDA = "saida"  # Venda
    ENTRADA = "entrada"  # Compra
    DEVOLUCAO = "devolucao"


class TipoMovimentacaoBancaria(str, enum.Enum):
    DEPOSITO = "deposito"
    SAQUE = "saque"
    TARIFA = "tarifa"
    TRANSFERENCIA_ENTRADA = "transferencia_entrada"
    TRANSFERENCIA_SAIDA = "transferencia_saida"
    JUROS = "juros"
    ESTORNO = "estorno"
    OUTROS = "outros"


# =============================================================================
# MÓDULO DE COMPRAS
# =============================================================================

class Fornecedor(Base):
    __tablename__ = "fornecedores"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True)  # FOR-0001, FOR-0002...
    nome = Column(String, nullable=False, index=True)
    razao_social = Column(String)
    cnpj = Column(String, unique=True, index=True)
    email = Column(String)
    telefone = Column(String)
    endereco = Column(String)
    cidade = Column(String)
    estado = Column(String(2))
    cep = Column(String)
    ativo = Column(Integer, default=1)  # 1=ativo, 0=inativo
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    pedidos = relationship("PedidoCompra", back_populates="fornecedor")


class PedidoCompra(Base):
    __tablename__ = "pedidos_compra"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True, nullable=False)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"))
    data_pedido = Column(DateTime, default=datetime.utcnow)
    data_entrega_prevista = Column(DateTime)
    status = Column(SQLEnum(StatusCompra), default=StatusCompra.RASCUNHO)
    valor_total = Column(Float, default=0.0)
    observacoes = Column(Text)
    created_by = Column(Integer)  # ID do usuário que criou
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    fornecedor = relationship("Fornecedor", back_populates="pedidos")
    itens = relationship("ItemPedidoCompra", back_populates="pedido", cascade="all, delete-orphan")


class ItemPedidoCompra(Base):
    __tablename__ = "itens_pedido_compra"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos_compra.id"))
    material_id = Column(Integer, ForeignKey("materiais.id"))
    descricao = Column(String, nullable=False)
    quantidade = Column(Float, nullable=False)
    unidade = Column(String)
    preco_unitario = Column(Float, nullable=False)
    preco_total = Column(Float, nullable=False)
    
    # Relacionamentos
    pedido = relationship("PedidoCompra", back_populates="itens")
    material = relationship("Material")


class Cotacao(Base):
    __tablename__ = "cotacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True, nullable=False)  # COT-0001
    descricao = Column(String, nullable=False)
    data_solicitacao = Column(DateTime, default=datetime.utcnow)
    data_limite_resposta = Column(DateTime)
    status = Column(SQLEnum(StatusCotacao), default=StatusCotacao.RASCUNHO)
    observacoes = Column(Text)
    
    # Controle de conversão
    convertida_pedido_id = Column(Integer, ForeignKey("pedidos_compra.id"), nullable=True)
    melhor_fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    
    created_by = Column(Integer)  # ID do usuário que criou
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    itens = relationship("ItemCotacao", back_populates="cotacao", cascade="all, delete-orphan")
    respostas = relationship("RespostaFornecedor", back_populates="cotacao", cascade="all, delete-orphan")
    melhor_fornecedor = relationship("Fornecedor", foreign_keys=[melhor_fornecedor_id])


class ItemCotacao(Base):
    __tablename__ = "itens_cotacao"
    
    id = Column(Integer, primary_key=True, index=True)
    cotacao_id = Column(Integer, ForeignKey("cotacoes.id"))
    material_id = Column(Integer, ForeignKey("materiais.id"), nullable=True)
    descricao = Column(String, nullable=False)
    quantidade = Column(Float, nullable=False)
    unidade = Column(String, default="UN")
    observacoes = Column(Text)
    
    # Relacionamentos
    cotacao = relationship("Cotacao", back_populates="itens")
    material = relationship("Material")
    respostas = relationship("ItemRespostaFornecedor", back_populates="item_cotacao")


class RespostaFornecedor(Base):
    __tablename__ = "respostas_fornecedor"
    
    id = Column(Integer, primary_key=True, index=True)
    cotacao_id = Column(Integer, ForeignKey("cotacoes.id"))
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"))
    data_resposta = Column(DateTime, default=datetime.utcnow)
    prazo_entrega_dias = Column(Integer)
    condicao_pagamento = Column(String)
    observacoes = Column(Text)
    valor_total = Column(Float, default=0.0)
    selecionada = Column(Integer, default=0)  # 1 se for a escolhida
    
    # Relacionamentos
    cotacao = relationship("Cotacao", back_populates="respostas")
    fornecedor = relationship("Fornecedor")
    itens_resposta = relationship("ItemRespostaFornecedor", back_populates="resposta", cascade="all, delete-orphan")


class ItemRespostaFornecedor(Base):
    __tablename__ = "itens_resposta_fornecedor"
    
    id = Column(Integer, primary_key=True, index=True)
    resposta_id = Column(Integer, ForeignKey("respostas_fornecedor.id"))
    item_cotacao_id = Column(Integer, ForeignKey("itens_cotacao.id"))
    preco_unitario = Column(Float, nullable=False)
    preco_total = Column(Float, nullable=False)
    marca = Column(String)
    observacoes = Column(Text)
    
    # Relacionamentos
    resposta = relationship("RespostaFornecedor", back_populates="itens_resposta")
    item_cotacao = relationship("ItemCotacao", back_populates="respostas")


# =============================================================================
# MÓDULO FINANCEIRO
# =============================================================================

class ContaBancaria(Base):
    __tablename__ = "contas_bancarias"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    banco = Column(String)
    agencia = Column(String)
    conta = Column(String)
    saldo_inicial = Column(Float, default=0.0)
    data_saldo_inicial = Column(Date, nullable=True)
    saldo_atual = Column(Float, default=0.0)
    ativa = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    saldos_diarios = relationship("SaldoDiario", back_populates="conta_bancaria")
    movimentacoes = relationship("MovimentacaoBancaria", back_populates="conta_bancaria")


class SaldoDiario(Base):
    __tablename__ = "saldos_diarios"
    
    id = Column(Integer, primary_key=True, index=True)
    conta_bancaria_id = Column(Integer, ForeignKey("contas_bancarias.id"), nullable=False)
    data = Column(Date, nullable=False)
    saldo_anterior = Column(Float, default=0.0)
    total_entradas = Column(Float, default=0.0)
    total_saidas = Column(Float, default=0.0)
    saldo_final = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento
    conta_bancaria = relationship("ContaBancaria", back_populates="saldos_diarios")


class MovimentacaoBancaria(Base):
    __tablename__ = "movimentacoes_bancarias"
    
    id = Column(Integer, primary_key=True, index=True)
    conta_bancaria_id = Column(Integer, ForeignKey("contas_bancarias.id"), nullable=False)
    tipo = Column(SQLEnum(TipoMovimentacaoBancaria), nullable=False)
    natureza = Column(String, nullable=False)  # ENTRADA ou SAIDA
    data_movimentacao = Column(DateTime, default=datetime.utcnow)
    data_competencia = Column(Date)
    valor = Column(Float, nullable=False)
    descricao = Column(String, nullable=False)
    conta_pagar_id = Column(Integer, ForeignKey("contas_pagar.id"), nullable=True)
    conta_receber_id = Column(Integer, ForeignKey("contas_receber.id"), nullable=True)
    transferencia_vinculada_id = Column(Integer, nullable=True)
    conciliado = Column(Boolean, default=False)
    data_conciliacao = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    conta_bancaria = relationship("ContaBancaria", back_populates="movimentacoes")


class CentroCusto(Base):
    __tablename__ = "centros_custo"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False)
    nome = Column(String, nullable=False)
    descricao = Column(Text)
    ativo = Column(Integer, default=1)


class ContaPagar(Base):
    __tablename__ = "contas_pagar"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"))
    pedido_compra_id = Column(Integer, ForeignKey("pedidos_compra.id"), nullable=True)
    centro_custo_id = Column(Integer, ForeignKey("centros_custo.id"))
    data_emissao = Column(DateTime, default=datetime.utcnow)
    data_vencimento = Column(DateTime, nullable=False)
    data_pagamento = Column(DateTime)
    valor_original = Column(Float, nullable=False)
    valor_pago = Column(Float, default=0.0)
    
    # NOVOS campos
    juros = Column(Float, default=0.0)
    desconto = Column(Float, default=0.0)
    
    status = Column(SQLEnum(StatusPagamento), default=StatusPagamento.PENDENTE)
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    fornecedor = relationship("Fornecedor")


class ContaReceber(Base):
    __tablename__ = "contas_receber"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False)
    
    # ATUALIZADO: De String para FK
    cliente_nome = Column(String, nullable=True)  # Mantido para compatibilidade com dados antigos
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)  # Novo FK
    pedido_venda_id = Column(Integer, ForeignKey("pedidos_venda.id"), nullable=True)  # Link com pedido de venda
    
    centro_custo_id = Column(Integer, ForeignKey("centros_custo.id"))
    data_emissao = Column(DateTime, default=datetime.utcnow)
    data_vencimento = Column(DateTime, nullable=False)
    data_recebimento = Column(DateTime)
    valor_original = Column(Float, nullable=False)
    valor_recebido = Column(Float, default=0.0)
    
    # NOVOS campos
    juros = Column(Float, default=0.0)
    desconto = Column(Float, default=0.0)
    
    status = Column(SQLEnum(StatusPagamento), default=StatusPagamento.PENDENTE)
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="contas_receber")
    pedido_venda = relationship("PedidoVenda", back_populates="contas_receber")


# =============================================================================
# MÓDULO DE MATERIAIS
# =============================================================================

class CategoriaMaterial(Base):
    __tablename__ = "categorias_material"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, unique=True)
    descricao = Column(Text)
    ativa = Column(Integer, default=1)


class Material(Base):
    __tablename__ = "materiais"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False, index=True)
    descricao = Column(Text)
    categoria_id = Column(Integer, ForeignKey("categorias_material.id"))
    
    # ATUALIZADO: Unidade de medida como FK
    unidade_medida = Column(String, nullable=False)  # Mantido para compatibilidade
    unidade_medida_id = Column(Integer, ForeignKey("unidades_medida.id"), nullable=True)  # Novo FK
    
    estoque_minimo = Column(Float, default=0.0)
    estoque_maximo = Column(Float, default=0.0)
    estoque_atual = Column(Float, default=0.0)
    preco_medio = Column(Float, default=0.0)
    preco_venda = Column(Float, default=0.0)  # NOVO
    localizacao = Column(String)
    ativo = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    categoria = relationship("CategoriaMaterial")
    unidade_obj = relationship("UnidadeMedida", back_populates="materiais")
    estoques_locais = relationship("EstoquePorLocal", back_populates="material")
    movimentos = relationship("MovimentoEstoque", back_populates="material")


class MovimentoEstoque(Base):
    __tablename__ = "movimentos_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materiais.id"), nullable=False)
    tipo_movimento = Column(SQLEnum(TipoMovimento), nullable=False)
    quantidade = Column(Float, nullable=False)
    data_movimento = Column(DateTime, default=datetime.utcnow)
    documento = Column(String)  # Número do documento relacionado
    observacao = Column(Text)
    usuario_id = Column(Integer)  # Quem fez o movimento
    
    # Novos campos para locais
    local_origem_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=True)
    local_destino_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=True)
    
    # Relacionamentos
    material = relationship("Material", back_populates="movimentos")
    local_origem = relationship("LocalEstoque", foreign_keys=[local_origem_id])
    local_destino = relationship("LocalEstoque", foreign_keys=[local_destino_id])


# =============================================================================
# NOVOS MODELOS - FASE 1
# =============================================================================

# -----------------------------------------------------------------------------
# CLIENTES
# -----------------------------------------------------------------------------

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True)  # CLI-0001, CLI-0002...
    
    # Dados básicos
    nome = Column(String, nullable=False, index=True)
    razao_social = Column(String)
    cpf_cnpj = Column(String, unique=True, index=True)
    tipo_pessoa = Column(String, default="PF")  # PF ou PJ
    
    # Contato
    email = Column(String)
    telefone = Column(String)
    celular = Column(String)
    
    # Endereço
    endereco = Column(String)
    numero = Column(String)
    complemento = Column(String)
    bairro = Column(String)
    cidade = Column(String)
    estado = Column(String)
    cep = Column(String)
    
    # Informações comerciais
    tipo_cliente = Column(String, default="varejo")  # varejo, atacado, distribuidor
    limite_credito = Column(Float, default=0.0)
    dias_vencimento = Column(Integer, default=30)
    
    # Vínculo opcional com fornecedor (para empresas que são ambos)
    parceiro_vinculado_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    
    # Controle
    ativo = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    contas_receber = relationship("ContaReceber", back_populates="cliente")
    pedidos_venda = relationship("PedidoVenda", back_populates="cliente")


# -----------------------------------------------------------------------------
# PEDIDOS DE VENDA
# -----------------------------------------------------------------------------

class PedidoVenda(Base):
    __tablename__ = "pedidos_venda"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True)  # PV-0001, PV-0002...
    
    # Relacionamentos
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    vendedor_id = Column(Integer, nullable=True)  # ID do usuário vendedor
    
    # Datas
    data_pedido = Column(DateTime, default=datetime.utcnow)
    data_entrega_prevista = Column(DateTime, nullable=True)
    data_faturamento = Column(DateTime, nullable=True)
    
    # Status e valores
    status = Column(String, default="orcamento")  # orcamento, aprovado, faturado, cancelado
    condicao_pagamento = Column(String, nullable=True)  # à vista, 30 dias, etc.
    
    # Valores (calculados)
    valor_produtos = Column(Float, default=0.0)
    valor_desconto = Column(Float, default=0.0)
    valor_frete = Column(Float, default=0.0)
    valor_total = Column(Float, default=0.0)
    
    observacoes = Column(Text, nullable=True)
    
    # Controle
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="pedidos_venda")
    itens = relationship("ItemPedidoVenda", back_populates="pedido", cascade="all, delete-orphan")
    contas_receber = relationship("ContaReceber", back_populates="pedido_venda")


class ItemPedidoVenda(Base):
    __tablename__ = "itens_pedido_venda"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos_venda.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materiais.id"), nullable=False)
    
    quantidade = Column(Float, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    percentual_desconto = Column(Float, default=0.0)
    valor_desconto = Column(Float, default=0.0)
    subtotal = Column(Float, nullable=False)  # (quantidade * preco_unitario) - desconto
    
    observacao = Column(String, nullable=True)
    
    # Relacionamentos
    pedido = relationship("PedidoVenda", back_populates="itens")
    material = relationship("Material")


# -----------------------------------------------------------------------------
# UNIDADES DE MEDIDA
# -----------------------------------------------------------------------------

class UnidadeMedida(Base):
    __tablename__ = "unidades_medida"
    
    id = Column(Integer, primary_key=True, index=True)
    sigla = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String)  # peso, volume, comprimento, area, unidade
    permite_decimal = Column(Integer, default=1)  # 1=sim, 0=não
    
    # Conversões (opcional para futuro)
    unidade_base_id = Column(Integer, ForeignKey("unidades_medida.id"), nullable=True)
    fator_conversao = Column(Float, default=1.0)
    
    # Controle
    ativa = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    materiais = relationship("Material", back_populates="unidade_obj")


# -----------------------------------------------------------------------------
# LOCAIS DE ESTOQUE
# -----------------------------------------------------------------------------

class LocalEstoque(Base):
    __tablename__ = "locais_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, default="almoxarifado")  # almoxarifado, loja, deposito, producao
    
    # Localização
    endereco = Column(String)
    cidade = Column(String)
    estado = Column(String)
    responsavel = Column(String)
    telefone = Column(String)
    
    # Controle
    ativo = Column(Integer, default=1)
    padrao = Column(Integer, default=0)  # Local padrão para movimentações
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    estoques = relationship("EstoquePorLocal", back_populates="local")


# -----------------------------------------------------------------------------
# ESTOQUE POR LOCAL
# -----------------------------------------------------------------------------

class EstoquePorLocal(Base):
    __tablename__ = "estoque_por_local"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materiais.id"), nullable=False)
    local_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=False)
    
    quantidade = Column(Float, default=0.0)
    estoque_minimo = Column(Float, default=0.0)
    estoque_maximo = Column(Float, default=0.0)
    localizacao_fisica = Column(String)  # Prateleira, corredor, etc
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    material = relationship("Material", back_populates="estoques_locais")
    local = relationship("LocalEstoque", back_populates="estoques")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('material_id', 'local_id', name='uk_material_local'),
    )


# =============================================================================
# MÓDULO DE FATURAMENTO / NOTAS FISCAIS
# =============================================================================

class NotaFiscal(Base):
    __tablename__ = "notas_fiscais"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True)  # Número da NF
    serie = Column(String, default="1")
    tipo = Column(SQLEnum(TipoNotaFiscal), default=TipoNotaFiscal.SAIDA)
    
    # Datas
    data_emissao = Column(DateTime, default=datetime.utcnow)
    data_saida = Column(DateTime)
    
    # Relacionamentos
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    pedido_venda_id = Column(Integer, nullable=True)  # Relacionamento opcional com pedido
    pedido_compra_id = Column(Integer, nullable=True)
    
    # Valores
    valor_produtos = Column(Float, default=0.0)
    valor_frete = Column(Float, default=0.0)
    valor_seguro = Column(Float, default=0.0)
    valor_desconto = Column(Float, default=0.0)
    valor_outras_despesas = Column(Float, default=0.0)
    
    # Impostos (simplificado para MVP)
    valor_icms = Column(Float, default=0.0)
    valor_ipi = Column(Float, default=0.0)
    valor_pis = Column(Float, default=0.0)
    valor_cofins = Column(Float, default=0.0)
    
    # Total
    valor_total = Column(Float, default=0.0)
    
    # Fiscal
    chave_acesso = Column(String)  # Chave de 44 dígitos (NFe)
    protocolo_autorizacao = Column(String)
    
    # Natureza da operação
    natureza_operacao = Column(String, default="Venda de mercadoria")
    cfop = Column(String)  # Código Fiscal de Operações
    
    # Observações
    observacao = Column(Text)
    informacoes_adicionais = Column(Text)
    
    # Controle
    status = Column(SQLEnum(StatusNotaFiscal), default=StatusNotaFiscal.RASCUNHO)
    usuario_emissao_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    cliente = relationship("Cliente")
    fornecedor = relationship("Fornecedor")
    itens = relationship("ItemNotaFiscal", back_populates="nota_fiscal", cascade="all, delete-orphan")


class ItemNotaFiscal(Base):
    __tablename__ = "itens_nota_fiscal"
    
    id = Column(Integer, primary_key=True, index=True)
    nota_fiscal_id = Column(Integer, ForeignKey("notas_fiscais.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materiais.id"), nullable=True)
    
    # Dados do produto
    codigo_produto = Column(String)
    descricao = Column(String, nullable=False)
    ncm = Column(String)  # Nomenclatura Comum do Mercosul
    unidade = Column(String)
    
    # Quantidades e valores
    quantidade = Column(Float, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    valor_desconto = Column(Float, default=0.0)
    valor_frete = Column(Float, default=0.0)
    valor_seguro = Column(Float, default=0.0)
    valor_outras_despesas = Column(Float, default=0.0)
    
    # Impostos (simplificado)
    aliquota_icms = Column(Float, default=0.0)
    valor_icms = Column(Float, default=0.0)
    aliquota_ipi = Column(Float, default=0.0)
    valor_ipi = Column(Float, default=0.0)
    
    # Total
    valor_total = Column(Float, nullable=False)
    
    # CFOP por item (pode ser diferente)
    cfop = Column(String)
    
    # Relacionamentos
    nota_fiscal = relationship("NotaFiscal", back_populates="itens")
    material = relationship("Material")
