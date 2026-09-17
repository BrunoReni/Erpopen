import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { MainLayout } from './layout/MainLayout';
import {
  Users, Package, TrendingUp, DollarSign,
  ShoppingCart, AlertTriangle, ArrowUpCircle, ArrowDownCircle
} from 'lucide-react';
import api from '../services/api';

interface DashboardStats {
  resumo: {
    total_clientes: number;
    total_fornecedores: number;
    total_materiais: number;
    total_usuarios: number;
  };
  vendas: {
    pedidos_total: number;
    pedidos_aprovados: number;
    pedidos_faturados: number;
    valor_faturado_mes: number;
  };
  compras: {
    pedidos_total: number;
    pedidos_aprovados: number;
  };
  financeiro: {
    contas_pagar_pendentes: number;
    valor_pagar_pendente: number;
    contas_receber_pendentes: number;
    valor_receber_pendente: number;
    contas_pagar_vencidas: number;
    contas_receber_vencidas: number;
  };
  estoque: {
    materiais_estoque_baixo: number;
  };
  pedidos_recentes: Array<{
    id: number;
    codigo: string;
    cliente_id: number;
    valor_total: number;
    status: string;
    created_at: string;
  }>;
}

export function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const getStatusBadge = (status: string) => {
    const config: Record<string, { label: string; className: string }> = {
      orcamento: { label: 'Orçamento', className: 'bg-gray-200 text-gray-800' },
      aprovado: { label: 'Aprovado', className: 'bg-green-200 text-green-800' },
      faturado: { label: 'Faturado', className: 'bg-blue-200 text-blue-800' },
      cancelado: { label: 'Cancelado', className: 'bg-red-200 text-red-800' },
    };
    const c = config[status] || { label: status, className: 'bg-gray-200 text-gray-800' };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${c.className}`}>{c.label}</span>
    );
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
            Bem-vindo, {user?.full_name || user?.email}!
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-500">Carregando estatísticas...</div>
        ) : stats ? (
          <>
            {/* Stats Grid - Main KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6 flex items-center gap-4">
                <div className="bg-blue-500 p-3 rounded-lg">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Clientes</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.resumo.total_clientes}</p>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6 flex items-center gap-4">
                <div className="bg-green-500 p-3 rounded-lg">
                  <Package className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Materiais</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.resumo.total_materiais}</p>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6 flex items-center gap-4">
                <div className="bg-yellow-500 p-3 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Faturado (Mês)</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(stats.vendas.valor_faturado_mes)}
                  </p>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6 flex items-center gap-4">
                <div className="bg-purple-500 p-3 rounded-lg">
                  <ShoppingCart className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Fornecedores</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.resumo.total_fornecedores}</p>
                </div>
              </div>
            </div>

            {/* Financial + Alerts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Financeiro */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-green-600" />
                  Resumo Financeiro
                </h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <ArrowUpCircle className="w-5 h-5 text-red-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-700">Contas a Pagar</p>
                        <p className="text-xs text-gray-500">
                          {stats.financeiro.contas_pagar_pendentes} pendente(s)
                        </p>
                      </div>
                    </div>
                    <p className="text-lg font-bold text-red-600">
                      {formatCurrency(stats.financeiro.valor_pagar_pendente)}
                    </p>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <ArrowDownCircle className="w-5 h-5 text-green-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-700">Contas a Receber</p>
                        <p className="text-xs text-gray-500">
                          {stats.financeiro.contas_receber_pendentes} pendente(s)
                        </p>
                      </div>
                    </div>
                    <p className="text-lg font-bold text-green-600">
                      {formatCurrency(stats.financeiro.valor_receber_pendente)}
                    </p>
                  </div>

                  {(stats.financeiro.contas_pagar_vencidas > 0 || stats.financeiro.contas_receber_vencidas > 0) && (
                    <div className="flex items-center gap-2 p-3 bg-yellow-50 rounded-lg">
                      <AlertTriangle className="w-5 h-5 text-yellow-600" />
                      <div className="text-sm">
                        {stats.financeiro.contas_pagar_vencidas > 0 && (
                          <p className="text-yellow-800">
                            {stats.financeiro.contas_pagar_vencidas} conta(s) a pagar vencida(s)
                          </p>
                        )}
                        {stats.financeiro.contas_receber_vencidas > 0 && (
                          <p className="text-yellow-800">
                            {stats.financeiro.contas_receber_vencidas} conta(s) a receber vencida(s)
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Vendas & Compras + Alertas */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  Vendas & Compras
                </h2>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-blue-50 rounded-lg text-center">
                      <p className="text-2xl font-bold text-blue-600">{stats.vendas.pedidos_total}</p>
                      <p className="text-xs text-gray-600">Pedidos de Venda</p>
                    </div>
                    <div className="p-3 bg-indigo-50 rounded-lg text-center">
                      <p className="text-2xl font-bold text-indigo-600">{stats.compras.pedidos_total}</p>
                      <p className="text-xs text-gray-600">Pedidos de Compra</p>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg text-center">
                      <p className="text-2xl font-bold text-green-600">{stats.vendas.pedidos_faturados}</p>
                      <p className="text-xs text-gray-600">Faturados</p>
                    </div>
                    <div className="p-3 bg-yellow-50 rounded-lg text-center">
                      <p className="text-2xl font-bold text-yellow-600">{stats.vendas.pedidos_aprovados}</p>
                      <p className="text-xs text-gray-600">Aguardando Faturamento</p>
                    </div>
                  </div>

                  {stats.estoque.materiais_estoque_baixo > 0 && (
                    <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-lg">
                      <AlertTriangle className="w-5 h-5 text-orange-600" />
                      <p className="text-sm text-orange-800">
                        {stats.estoque.materiais_estoque_baixo} material(is) com estoque baixo
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Recent Orders */}
            {stats.pedidos_recentes.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Pedidos de Venda Recentes</h2>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Código</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {stats.pedidos_recentes.map((pedido) => (
                        <tr key={pedido.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm font-medium text-gray-900">{pedido.codigo}</td>
                          <td className="px-4 py-3 text-sm text-gray-900">{formatCurrency(pedido.valor_total)}</td>
                          <td className="px-4 py-3 text-sm">{getStatusBadge(pedido.status)}</td>
                          <td className="px-4 py-3 text-sm text-gray-500">
                            {pedido.created_at ? new Date(pedido.created_at).toLocaleDateString('pt-BR') : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12 text-gray-500">
            Não foi possível carregar as estatísticas.
          </div>
        )}
      </div>
    </MainLayout>
  );
}
