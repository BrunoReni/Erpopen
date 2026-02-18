from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db import get_session
from app.dependencies import require_permission
from app.models import User
from app.models_modules import (
    Fornecedor, PedidoCompra, Cliente, PedidoVenda,
    Material, ContaPagar, ContaReceber, ContaBancaria,
    StatusPagamento
)

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    session: Session = Depends(get_session),
    _: bool = Depends(require_permission("dashboard:read"))
):
    """Retorna estatísticas gerais do sistema para o dashboard"""

    # Contagens gerais
    total_clientes = session.query(func.count(Cliente.id)).scalar() or 0
    total_fornecedores = session.query(func.count(Fornecedor.id)).filter(
        Fornecedor.ativo == 1
    ).scalar() or 0
    total_materiais = session.query(func.count(Material.id)).scalar() or 0
    total_usuarios = session.query(func.count(User.id)).scalar() or 0

    # Pedidos de venda por status
    pedidos_venda_total = session.query(func.count(PedidoVenda.id)).scalar() or 0
    pedidos_venda_aprovados = session.query(func.count(PedidoVenda.id)).filter(
        PedidoVenda.status == "aprovado"
    ).scalar() or 0
    pedidos_venda_faturados = session.query(func.count(PedidoVenda.id)).filter(
        PedidoVenda.status == "faturado"
    ).scalar() or 0

    # Pedidos de compra por status
    pedidos_compra_total = session.query(func.count(PedidoCompra.id)).scalar() or 0
    pedidos_compra_aprovados = session.query(func.count(PedidoCompra.id)).filter(
        PedidoCompra.status == "aprovado"
    ).scalar() or 0

    # Financeiro - Contas a pagar
    contas_pagar_pendentes = session.query(func.count(ContaPagar.id)).filter(
        ContaPagar.status == StatusPagamento.PENDENTE
    ).scalar() or 0
    valor_pagar_pendente = session.query(
        func.coalesce(func.sum(ContaPagar.valor_original - ContaPagar.valor_pago), 0.0)
    ).filter(
        ContaPagar.status.in_([StatusPagamento.PENDENTE, StatusPagamento.PARCIAL])
    ).scalar() or 0.0

    # Financeiro - Contas a receber
    contas_receber_pendentes = session.query(func.count(ContaReceber.id)).filter(
        ContaReceber.status == StatusPagamento.PENDENTE
    ).scalar() or 0
    valor_receber_pendente = session.query(
        func.coalesce(func.sum(ContaReceber.valor_original - ContaReceber.valor_recebido), 0.0)
    ).filter(
        ContaReceber.status.in_([StatusPagamento.PENDENTE, StatusPagamento.PARCIAL])
    ).scalar() or 0.0

    # Contas vencidas
    hoje = datetime.utcnow()
    contas_pagar_vencidas = session.query(func.count(ContaPagar.id)).filter(
        ContaPagar.data_vencimento < hoje,
        ContaPagar.status.in_([StatusPagamento.PENDENTE, StatusPagamento.PARCIAL])
    ).scalar() or 0
    contas_receber_vencidas = session.query(func.count(ContaReceber.id)).filter(
        ContaReceber.data_vencimento < hoje,
        ContaReceber.status.in_([StatusPagamento.PENDENTE, StatusPagamento.PARCIAL])
    ).scalar() or 0

    # Materiais com estoque baixo (estoque_atual <= estoque_minimo)
    materiais_estoque_baixo = session.query(func.count(Material.id)).filter(
        Material.estoque_atual <= Material.estoque_minimo
    ).scalar() or 0

    # Pedidos de venda recentes (últimos 5)
    pedidos_recentes = session.query(PedidoVenda).order_by(
        PedidoVenda.created_at.desc()
    ).limit(5).all()

    pedidos_recentes_data = [
        {
            "id": p.id,
            "codigo": p.codigo,
            "cliente_id": p.cliente_id,
            "valor_total": p.valor_total,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in pedidos_recentes
    ]

    # Valor total faturado (pedidos de venda faturados)
    valor_faturado_mes = session.query(
        func.coalesce(func.sum(PedidoVenda.valor_total), 0.0)
    ).filter(
        PedidoVenda.status == "faturado",
        PedidoVenda.data_faturamento >= hoje.replace(day=1, hour=0, minute=0, second=0)
    ).scalar() or 0.0

    return {
        "resumo": {
            "total_clientes": total_clientes,
            "total_fornecedores": total_fornecedores,
            "total_materiais": total_materiais,
            "total_usuarios": total_usuarios,
        },
        "vendas": {
            "pedidos_total": pedidos_venda_total,
            "pedidos_aprovados": pedidos_venda_aprovados,
            "pedidos_faturados": pedidos_venda_faturados,
            "valor_faturado_mes": round(valor_faturado_mes, 2),
        },
        "compras": {
            "pedidos_total": pedidos_compra_total,
            "pedidos_aprovados": pedidos_compra_aprovados,
        },
        "financeiro": {
            "contas_pagar_pendentes": contas_pagar_pendentes,
            "valor_pagar_pendente": round(float(valor_pagar_pendente), 2),
            "contas_receber_pendentes": contas_receber_pendentes,
            "valor_receber_pendente": round(float(valor_receber_pendente), 2),
            "contas_pagar_vencidas": contas_pagar_vencidas,
            "contas_receber_vencidas": contas_receber_vencidas,
        },
        "estoque": {
            "materiais_estoque_baixo": materiais_estoque_baixo,
        },
        "pedidos_recentes": pedidos_recentes_data,
    }
