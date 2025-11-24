# 🔧 MELHORIAS IMPLEMENTADAS - Backend

## 1. MODELO CLIENTE (Novo)

```python
class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    
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
    estado = Column(String(2))
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
```

---

## 2. MELHORIAS NO MÓDULO DE MATERIAIS

### 2.1 Grupos/Categorias de Produtos

```python
class CategoriaMaterial(Base):
    __tablename__ = "categorias_material"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False, unique=True)
    descricao = Column(Text)
    categoria_pai_id = Column(Integer, ForeignKey("categorias_material.id"), nullable=True)
    
    # Controle
    ativa = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    subcategorias = relationship("CategoriaMaterial", remote_side=[id])
    materiais = relationship("Material", back_populates="categoria")
```

### 2.2 Unidades de Medida (Tabela Padronizada)

```python
class UnidadeMedida(Base):
    __tablename__ = "unidades_medida"
    
    id = Column(Integer, primary_key=True, index=True)
    sigla = Column(String(10), unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String)  # peso, volume, comprimento, area, unidade
    permite_decimal = Column(Integer, default=1)
    
    # Conversões (opcional para futuro)
    unidade_base_id = Column(Integer, ForeignKey("unidades_medida.id"), nullable=True)
    fator_conversao = Column(Float, default=1.0)
    
    # Controle
    ativa = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    materiais = relationship("Material", back_populates="unidade_medida")
```

#### Unidades Padrão (Seed):
```python
unidades_padrao = [
    ("UN", "Unidade", "unidade", 0),
    ("PC", "Peça", "unidade", 0),
    ("CX", "Caixa", "unidade", 0),
    ("KG", "Quilograma", "peso", 1),
    ("G", "Grama", "peso", 1),
    ("L", "Litro", "volume", 1),
    ("ML", "Mililitro", "volume", 1),
    ("M", "Metro", "comprimento", 1),
    ("M2", "Metro Quadrado", "area", 1),
    ("M3", "Metro Cúbico", "volume", 1),
]
```

### 2.3 Locais de Estoque / Armazéns

```python
class LocalEstoque(Base):
    __tablename__ = "locais_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, default="almoxarifado")  # almoxarifado, loja, deposito, producao
    
    # Localização
    endereco = Column(String)
    cidade = Column(String)
    estado = Column(String(2))
    responsavel = Column(String)
    telefone = Column(String)
    
    # Controle
    ativo = Column(Integer, default=1)
    padrao = Column(Integer, default=0)  # Local padrão para movimentações
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    estoques = relationship("EstoquePorLocal", back_populates="local")
```

### 2.4 Estoque por Local

```python
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
```

---

## 3. ATUALIZAÇÃO DO MODELO MATERIAL

```python
class Material(Base):
    __tablename__ = "materiais"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False, index=True)
    descricao = Column(Text)
    
    # NOVO: Relacionamento com categoria
    categoria_id = Column(Integer, ForeignKey("categorias_material.id"))
    
    # NOVO: Relacionamento com unidade de medida
    unidade_medida_id = Column(Integer, ForeignKey("unidades_medida.id"), nullable=False)
    
    # Estoque (mantido para compatibilidade, será calculado dos locais)
    estoque_minimo = Column(Float, default=0.0)
    estoque_maximo = Column(Float, default=0.0)
    estoque_atual = Column(Float, default=0.0)  # Soma de todos os locais
    
    # Financeiro
    preco_medio = Column(Float, default=0.0)
    preco_venda = Column(Float, default=0.0)  # NOVO
    
    # Controle
    localizacao = Column(String)  # Deprecated, usar EstoquePorLocal
    ativo = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    categoria = relationship("CategoriaMaterial", back_populates="materiais")
    unidade_medida = relationship("UnidadeMedida", back_populates="materiais")
    estoques_locais = relationship("EstoquePorLocal", back_populates="material")
    movimentos = relationship("MovimentoEstoque", back_populates="material")
```

---

## 4. ATUALIZAÇÃO DAS CONTAS FINANCEIRAS

### 4.1 Contas a Receber (com FK para Cliente)

```python
class ContaReceber(Base):
    __tablename__ = "contas_receber"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False)
    
    # MUDANÇA: De String para FK
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    pedido_venda_id = Column(Integer, ForeignKey("pedidos_venda.id"), nullable=True)  # NOVO
    centro_custo_id = Column(Integer, ForeignKey("centros_custo.id"))
    
    data_emissao = Column(DateTime, default=datetime.utcnow)
    data_vencimento = Column(DateTime, nullable=False)
    data_recebimento = Column(DateTime)
    
    valor_original = Column(Float, nullable=False)
    valor_recebido = Column(Float, default=0.0)
    juros = Column(Float, default=0.0)  # NOVO
    desconto = Column(Float, default=0.0)  # NOVO
    
    status = Column(SQLEnum(StatusPagamento), default=StatusPagamento.PENDENTE)
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="contas_receber")
    pedido_venda = relationship("PedidoVenda")
```

### 4.2 Contas a Pagar (melhorias)

```python
class ContaPagar(Base):
    __tablename__ = "contas_pagar"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False)
    
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    pedido_compra_id = Column(Integer, ForeignKey("pedidos_compra.id"), nullable=True)
    centro_custo_id = Column(Integer, ForeignKey("centros_custo.id"))
    
    data_emissao = Column(DateTime, default=datetime.utcnow)
    data_vencimento = Column(DateTime, nullable=False)
    data_pagamento = Column(DateTime)
    
    valor_original = Column(Float, nullable=False)
    valor_pago = Column(Float, default=0.0)
    juros = Column(Float, default=0.0)  # NOVO
    desconto = Column(Float, default=0.0)  # NOVO
    
    status = Column(SQLEnum(StatusPagamento), default=StatusPagamento.PENDENTE)
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    fornecedor = relationship("Fornecedor", back_populates="contas_pagar")
    pedido_compra = relationship("PedidoCompra")
```

---

## 5. MOVIMENTO DE ESTOQUE (Atualizado)

```python
class MovimentoEstoque(Base):
    __tablename__ = "movimentos_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materiais.id"), nullable=False)
    local_origem_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=True)  # NOVO
    local_destino_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=True)  # NOVO
    
    tipo_movimento = Column(SQLEnum(TipoMovimento), nullable=False)
    quantidade = Column(Float, nullable=False)
    
    # Referências opcionais
    pedido_compra_id = Column(Integer, ForeignKey("pedidos_compra.id"), nullable=True)
    pedido_venda_id = Column(Integer, ForeignKey("pedidos_venda.id"), nullable=True)  # NOVO
    
    data_movimento = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("users.id"))
    observacao = Column(Text)
    
    # Relacionamentos
    material = relationship("Material", back_populates="movimentos")
    local_origem = relationship("LocalEstoque", foreign_keys=[local_origem_id])
    local_destino = relationship("LocalEstoque", foreign_keys=[local_destino_id])
```

---

## 📝 RESUMO DAS MELHORIAS

### ✅ Criado:
1. **Cliente** - Tabela completa com campos específicos
2. **CategoriaMaterial** - Com suporte a hierarquia
3. **UnidadeMedida** - Padronização de unidades
4. **LocalEstoque** - Múltiplos armazéns
5. **EstoquePorLocal** - Estoque por local

### ✅ Atualizado:
1. **ContaReceber** - FK para Cliente + campos de juros/desconto
2. **ContaPagar** - Campos de juros/desconto
3. **Material** - FKs para categoria e unidade
4. **MovimentoEstoque** - Suporte a locais origem/destino

### ✅ Relacionamentos Criados:
```
Cliente → ContaReceber (1:N)
Cliente → PedidoVenda (1:N)
CategoriaMaterial → Material (1:N)
UnidadeMedida → Material (1:N)
LocalEstoque → EstoquePorLocal (1:N)
Material → EstoquePorLocal (1:N)
```

---

## 🚀 Próximos Passos:

1. ✅ Atualizar arquivo `models_modules.py`
2. ✅ Criar schemas Pydantic correspondentes
3. ✅ Criar rotas API para novos módulos
4. ✅ Criar migrations
5. ✅ Criar telas frontend
6. ✅ Seed de dados padrão (unidades de medida)

