"""
Sistema de Feature Flags para rastreamento de completude de implementações.
Garante que toda funcionalidade backend tenha frontend correspondente.
"""
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class FeatureStatus(str, Enum):
    """Status de implementação de uma feature"""
    COMPLETE = "complete"  # Backend + Frontend + Testes + Docs completos
    BACKEND_ONLY = "backend_only"  # Apenas backend implementado
    FRONTEND_ONLY = "frontend_only"  # Apenas frontend implementado
    PARTIAL = "partial"  # Implementação parcial em ambos
    DISABLED = "disabled"  # Feature desabilitada/planejada
    DEPRECATED = "deprecated"  # Feature obsoleta


@dataclass
class Feature:
    """Representa uma feature do ERP com seu status de implementação"""
    id: str
    name: str
    module: str
    description: str
    
    # Status de implementação
    has_backend: bool = False
    has_frontend: bool = False
    has_tests: bool = False
    has_docs: bool = False
    
    # Metadados
    backend_endpoints: List[str] = field(default_factory=list)
    frontend_components: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    doc_files: List[str] = field(default_factory=list)
    
    # Tracking
    issue_number: Optional[int] = None
    pr_number: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @property
    def status(self) -> FeatureStatus:
        """Calcula o status atual da feature"""
        if not self.has_backend and not self.has_frontend:
            return FeatureStatus.DISABLED
        
        if self.has_backend and self.has_frontend and self.has_tests and self.has_docs:
            return FeatureStatus.COMPLETE
        
        if self.has_backend and not self.has_frontend:
            return FeatureStatus.BACKEND_ONLY
        
        if self.has_frontend and not self.has_backend:
            return FeatureStatus.FRONTEND_ONLY
        
        return FeatureStatus.PARTIAL
    
    @property
    def completeness_percentage(self) -> float:
        """Calcula a porcentagem de completude (0-100)"""
        total_items = 4  # backend, frontend, tests, docs
        completed_items = sum([
            self.has_backend,
            self.has_frontend,
            self.has_tests,
            self.has_docs
        ])
        return (completed_items / total_items) * 100
    
    def to_dict(self) -> dict:
        """Converte para dicionário para serialização"""
        return {
            "id": self.id,
            "name": self.name,
            "module": self.module,
            "description": self.description,
            "status": self.status.value,
            "has_backend": self.has_backend,
            "has_frontend": self.has_frontend,
            "has_tests": self.has_tests,
            "has_docs": self.has_docs,
            "backend_endpoints": self.backend_endpoints,
            "frontend_components": self.frontend_components,
            "test_files": self.test_files,
            "doc_files": self.doc_files,
            "completeness_percentage": self.completeness_percentage,
            "issue_number": self.issue_number,
            "pr_number": self.pr_number,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# =============================================================================
# REGISTRY DE FEATURES DO ERP
# =============================================================================

FEATURES_REGISTRY: List[Feature] = [
    # FINANCEIRO - Features Completas
    Feature(
        id="fin_contas_pagar",
        name="Contas a Pagar",
        module="financeiro",
        description="Gestão completa de contas a pagar com parcelamento",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /financeiro/contas-pagar",
            "POST /financeiro/contas-pagar",
            "PUT /financeiro/contas-pagar/{id}",
            "DELETE /financeiro/contas-pagar/{id}",
            "POST /financeiro/contas-pagar/{id}/baixar"
        ],
        frontend_components=["ContasPagarList"],
        test_files=["test_financeiro.py"],
        doc_files=["API_ENDPOINTS_FINANCEIRO.md"]
    ),
    
    Feature(
        id="fin_contas_receber",
        name="Contas a Receber",
        module="financeiro",
        description="Gestão completa de contas a receber com parcelamento",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /financeiro/contas-receber",
            "POST /financeiro/contas-receber",
            "PUT /financeiro/contas-receber/{id}",
            "DELETE /financeiro/contas-receber/{id}",
            "POST /financeiro/contas-receber/{id}/baixar"
        ],
        frontend_components=["ContasReceberList"],
        test_files=["test_financeiro.py"],
        doc_files=["API_ENDPOINTS_FINANCEIRO.md"]
    ),
    
    Feature(
        id="fin_parcelamento",
        name="Parcelamento de Contas",
        module="financeiro",
        description="Sistema de parcelamento para contas a pagar e receber",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "POST /financeiro/contas-pagar/parcelada",
            "POST /financeiro/contas-receber/parcelada",
            "GET /financeiro/parcelas-pagar",
            "GET /financeiro/parcelas-receber"
        ],
        frontend_components=["ContasPagarList", "ContasReceberList"],
        test_files=["test_financeiro.py"],
        doc_files=["MODULO_FINANCEIRO_AVANCADO.md"]
    ),
    
    Feature(
        id="fin_conciliacao_bancaria",
        name="Conciliação Bancária",
        module="financeiro",
        description="Conciliação automática de movimentações bancárias",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /financeiro/conciliacao",
            "POST /financeiro/conciliacao/auto",
            "POST /financeiro/conciliacao/manual"
        ],
        frontend_components=["ConciliacaoBancaria"],
        test_files=["test_financeiro.py"],
        doc_files=["MODULO_FINANCEIRO_AVANCADO.md"]
    ),
    
    Feature(
        id="fin_contas_bancarias",
        name="Contas Bancárias",
        module="financeiro",
        description="Cadastro e gestão de contas bancárias",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /financeiro/contas-bancarias",
            "POST /financeiro/contas-bancarias",
            "PUT /financeiro/contas-bancarias/{id}",
            "DELETE /financeiro/contas-bancarias/{id}"
        ],
        frontend_components=["ContasBancariasList"],
        test_files=["test_financeiro.py"],
        doc_files=["API_ENDPOINTS_FINANCEIRO.md"]
    ),
    
    Feature(
        id="fin_centros_custo",
        name="Centros de Custo",
        module="financeiro",
        description="Gestão de centros de custo",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /financeiro/centros-custo",
            "POST /financeiro/centros-custo",
            "PUT /financeiro/centros-custo/{id}",
            "DELETE /financeiro/centros-custo/{id}"
        ],
        frontend_components=["CentrosCustoList"],
        test_files=["test_financeiro.py"],
        doc_files=["API_ENDPOINTS_FINANCEIRO.md"]
    ),
    
    Feature(
        id="fin_movimentacoes_bancarias",
        name="Movimentações Bancárias",
        module="financeiro",
        description="Registro de movimentações bancárias",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /financeiro/movimentacoes",
            "POST /financeiro/movimentacoes",
            "PUT /financeiro/movimentacoes/{id}",
            "DELETE /financeiro/movimentacoes/{id}"
        ],
        frontend_components=["MovimentacoesBancariasList"],
        test_files=["test_financeiro.py"],
        doc_files=["API_ENDPOINTS_FINANCEIRO.md"]
    ),
    
    Feature(
        id="fin_transferencias",
        name="Transferências entre Contas",
        module="financeiro",
        description="Transferências entre contas bancárias",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "POST /financeiro/transferencias"
        ],
        frontend_components=["TransferenciaForm"],
        test_files=["test_financeiro.py"],
        doc_files=["MODULO_FINANCEIRO_AVANCADO.md"]
    ),
    
    # FINANCEIRO - Feature with GAP (Issue #16)
    Feature(
        id="fin_compensacao_liquidacao",
        name="Compensação/Liquidação de Contas",
        module="financeiro",
        description="Sistema de compensação e liquidação de contas a pagar/receber",
        has_backend=True,
        has_frontend=True,  # ✅ FRONTEND IMPLEMENTED
        has_tests=False,
        has_docs=True,
        backend_endpoints=[
            "POST /financeiro/compensacao",
            "GET /financeiro/compensacao",
            "POST /financeiro/baixa-multipla",
            "GET /financeiro/historico-liquidacao"
        ],
        frontend_components=[
            "LiquidacaoForm.tsx",
            "HistoricoLiquidacao.tsx"
        ],
        test_files=[],
        doc_files=["MODULO_FINANCEIRO_AVANCADO.md"],
        issue_number=16,
        created_at="2024-12-01"
    ),
    
    # VENDAS - Features Completas
    Feature(
        id="vnd_pedidos_venda",
        name="Pedidos de Venda",
        module="vendas",
        description="Gestão completa de pedidos de venda",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /vendas/pedidos",
            "POST /vendas/pedidos",
            "GET /vendas/pedidos/{id}",
            "PUT /vendas/pedidos/{id}",
            "DELETE /vendas/pedidos/{id}"
        ],
        frontend_components=["PedidosVendaList", "PedidoVendaForm"],
        test_files=["test_vendas.py"],
        doc_files=["SALES_ORDERS_IMPLEMENTATION.md"]
    ),
    
    Feature(
        id="vnd_clientes",
        name="Cadastro de Clientes",
        module="vendas",
        description="Gestão de cadastro de clientes",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /vendas/clientes",
            "POST /vendas/clientes",
            "PUT /vendas/clientes/{id}",
            "DELETE /vendas/clientes/{id}"
        ],
        frontend_components=["ClientesList"],
        test_files=["test_vendas.py"],
        doc_files=["CADASTROS_IMPLEMENTADOS_FINAL.md"]
    ),
    
    Feature(
        id="vnd_notas_fiscais",
        name="Notas Fiscais",
        module="vendas",
        description="Gestão de notas fiscais de saída",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /faturamento/notas-fiscais",
            "POST /faturamento/notas-fiscais",
            "GET /faturamento/notas-fiscais/{id}"
        ],
        frontend_components=["NotasFiscaisList"],
        test_files=["test_vendas.py"],
        doc_files=["SALES_ORDERS_IMPLEMENTATION.md"]
    ),
    
    # COMPRAS - Features Completas
    Feature(
        id="cmp_fornecedores",
        name="Cadastro de Fornecedores",
        module="compras",
        description="Gestão de cadastro de fornecedores",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /compras/fornecedores",
            "POST /compras/fornecedores",
            "PUT /compras/fornecedores/{id}",
            "DELETE /compras/fornecedores/{id}"
        ],
        frontend_components=["FornecedoresList"],
        test_files=["test_compras.py"],
        doc_files=["CADASTROS_IMPLEMENTADOS_FINAL.md"]
    ),
    
    Feature(
        id="cmp_pedidos_compra",
        name="Pedidos de Compra",
        module="compras",
        description="Gestão de pedidos de compra",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /compras/pedidos",
            "POST /compras/pedidos",
            "PUT /compras/pedidos/{id}",
            "DELETE /compras/pedidos/{id}"
        ],
        frontend_components=["PedidosCompraList"],
        test_files=["test_compras.py"],
        doc_files=["FUNCIONALIDADES_POR_MODULO.md"]
    ),
    
    Feature(
        id="cmp_cotacoes",
        name="Cotações de Compra",
        module="compras",
        description="Sistema de cotações de compra",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /cotacoes",
            "POST /cotacoes",
            "PUT /cotacoes/{id}",
            "DELETE /cotacoes/{id}"
        ],
        frontend_components=["CotacoesList"],
        test_files=["test_compras.py"],
        doc_files=["FUNCIONALIDADES_POR_MODULO.md"]
    ),
    
    # MATERIAIS - Features Completas
    Feature(
        id="mat_produtos",
        name="Cadastro de Produtos/Materiais",
        module="materiais",
        description="Gestão de cadastro de produtos e materiais",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /materiais",
            "POST /materiais",
            "PUT /materiais/{id}",
            "DELETE /materiais/{id}"
        ],
        frontend_components=["MateriaisList"],
        test_files=["test_materiais.py"],
        doc_files=["CADASTROS_IMPLEMENTADOS_FINAL.md"]
    ),
    
    Feature(
        id="mat_movimentos_estoque",
        name="Movimentos de Estoque",
        module="materiais",
        description="Gestão de movimentações de estoque",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /materiais/movimentos",
            "POST /materiais/movimentos"
        ],
        frontend_components=["MovimentosEstoqueList"],
        test_files=["test_materiais.py"],
        doc_files=["FUNCIONALIDADES_POR_MODULO.md"]
    ),
    
    Feature(
        id="mat_locais_estoque",
        name="Locais de Estoque",
        module="materiais",
        description="Gestão de locais de armazenamento",
        has_backend=True,
        has_frontend=True,
        has_tests=True,
        has_docs=True,
        backend_endpoints=[
            "GET /locais",
            "POST /locais",
            "PUT /locais/{id}",
            "DELETE /locais/{id}"
        ],
        frontend_components=["LocaisEstoqueList"],
        test_files=["test_materiais.py"],
        doc_files=["CADASTROS_IMPLEMENTADOS_FINAL.md"]
    ),
    
    # FEATURES PLANEJADAS (Issue #18)
    Feature(
        id="fin_ra_pa_antecipados",
        name="RA/PA Antecipados",
        module="financeiro",
        description="Gestão de recebimentos e pagamentos antecipados",
        has_backend=False,
        has_frontend=False,
        has_tests=False,
        has_docs=False,
        backend_endpoints=[],
        frontend_components=[],
        test_files=[],
        doc_files=[],
        issue_number=18,
        created_at="2024-12-05"
    ),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_features() -> List[Feature]:
    """Retorna todas as features registradas"""
    return FEATURES_REGISTRY


def get_feature_by_id(feature_id: str) -> Optional[Feature]:
    """Busca uma feature por ID"""
    for feature in FEATURES_REGISTRY:
        if feature.id == feature_id:
            return feature
    return None


def get_features_by_module(module: str) -> List[Feature]:
    """Retorna features de um módulo específico"""
    return [f for f in FEATURES_REGISTRY if f.module == module]


def get_features_by_status(status: FeatureStatus) -> List[Feature]:
    """Retorna features com status específico"""
    return [f for f in FEATURES_REGISTRY if f.status == status]


def get_incomplete_features() -> List[Feature]:
    """Retorna features incompletas (sem backend ou frontend)"""
    return [
        f for f in FEATURES_REGISTRY 
        if f.status in [FeatureStatus.BACKEND_ONLY, FeatureStatus.FRONTEND_ONLY, FeatureStatus.PARTIAL]
    ]


def get_backend_only_features() -> List[Feature]:
    """Retorna features com apenas backend implementado (GAP crítico)"""
    return get_features_by_status(FeatureStatus.BACKEND_ONLY)


def get_features_statistics() -> dict:
    """Retorna estatísticas gerais das features"""
    total = len(FEATURES_REGISTRY)
    complete = len(get_features_by_status(FeatureStatus.COMPLETE))
    backend_only = len(get_backend_only_features())
    frontend_only = len(get_features_by_status(FeatureStatus.FRONTEND_ONLY))
    partial = len(get_features_by_status(FeatureStatus.PARTIAL))
    disabled = len(get_features_by_status(FeatureStatus.DISABLED))
    
    avg_completeness = sum(f.completeness_percentage for f in FEATURES_REGISTRY) / total if total > 0 else 0
    
    return {
        "total": total,
        "complete": complete,
        "backend_only": backend_only,
        "frontend_only": frontend_only,
        "partial": partial,
        "disabled": disabled,
        "incomplete": backend_only + frontend_only + partial,
        "average_completeness": round(avg_completeness, 2),
        "completion_rate": round((complete / total * 100), 2) if total > 0 else 0
    }
