import { useState, useEffect } from 'react';
import { History, ExternalLink, Filter, X } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import api from '../../services/api';

interface HistoricoItem {
  id: number;
  tipo_operacao: string;
  data_operacao: string;
  valor_total: number;
  conta_origem_id: number;
  tipo_conta_origem: string;
  contas_geradas_ids: number[];
  movimentacao_bancaria_id: number | null;
  observacao: string | null;
  created_by: number | null;
}

export function HistoricoLiquidacao() {
  const [historico, setHistorico] = useState<HistoricoItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroTipo, setFiltroTipo] = useState<string>('');
  const [page, setPage] = useState(0);
  const [limit] = useState(50);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    fetchHistorico();
  }, [filtroTipo, page]);

  const fetchHistorico = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('skip', (page * limit).toString());
      params.append('limit', limit.toString());
      if (filtroTipo) {
        params.append('tipo_operacao', filtroTipo);
      }

      const response = await api.get(`/financeiro/historico-liquidacao?${params.toString()}`);
      setHistorico(response.data);
      setHasMore(response.data.length === limit);
    } catch (error) {
      console.error('Erro ao buscar histórico:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTipoBadgeClass = (tipo: string) => {
    switch (tipo) {
      case 'BAIXA_MULTIPLA':
        return 'bg-green-100 text-green-800';
      case 'COMPENSACAO':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTipoLabel = (tipo: string) => {
    switch (tipo) {
      case 'BAIXA_MULTIPLA':
        return 'Baixa Múltipla';
      case 'COMPENSACAO':
        return 'Compensação';
      default:
        return tipo;
    }
  };

  const getTipoContaBadgeClass = (tipo: string) => {
    return tipo === 'RECEBER' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700';
  };

  const truncateText = (text: string | null, maxLength: number = 50) => {
    if (!text) return '-';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  const clearFilter = () => {
    setFiltroTipo('');
    setPage(0);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Histórico de Liquidações</h1>
          <p className="text-gray-500 mt-2">Consultar operações de liquidação realizadas</p>
        </div>

        {/* Filtros */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Filter size={18} className="text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Filtros:</span>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-600">Tipo de Operação:</label>
              <select
                value={filtroTipo}
                onChange={(e) => {
                  setFiltroTipo(e.target.value);
                  setPage(0);
                }}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-slate-500 focus:border-transparent"
              >
                <option value="">Todos</option>
                <option value="BAIXA_MULTIPLA">Baixa Múltipla</option>
                <option value="COMPENSACAO">Compensação</option>
              </select>
            </div>

            {filtroTipo && (
              <button
                onClick={clearFilter}
                className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <X size={16} />
                Limpar Filtros
              </button>
            )}
          </div>
        </div>

        {/* Tabela */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-slate-500"></div>
              <p className="text-gray-500 mt-4">Carregando histórico...</p>
            </div>
          ) : historico.length === 0 ? (
            <div className="p-12 text-center">
              <History size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500 text-lg mb-2">Nenhuma operação encontrada</p>
              <p className="text-gray-400 text-sm">
                {filtroTipo
                  ? 'Tente alterar os filtros aplicados'
                  : 'Realize operações de liquidação para visualizá-las aqui'}
              </p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Data/Hora
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tipo de Operação
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Conta Origem
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tipo Conta
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Valor Total
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Contas Geradas
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Observação
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Movimentação
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {historico.map((item) => (
                      <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatDateTime(item.data_operacao)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getTipoBadgeClass(
                              item.tipo_operacao
                            )}`}
                          >
                            {getTipoLabel(item.tipo_operacao)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <a
                            href={`/financeiro/contas-${item.tipo_conta_origem.toLowerCase()}`}
                            className="text-purple-600 hover:text-purple-800 font-medium text-sm flex items-center gap-1"
                            title="Ver conta origem"
                          >
                            #{item.conta_origem_id}
                            <ExternalLink size={14} />
                          </a>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded ${getTipoContaBadgeClass(
                              item.tipo_conta_origem
                            )}`}
                          >
                            {item.tipo_conta_origem === 'RECEBER' ? 'A Receber' : 'A Pagar'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-semibold text-gray-900">
                          {formatCurrency(item.valor_total)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <span className="inline-flex items-center justify-center px-3 py-1 bg-slate-100 text-slate-800 text-sm font-medium rounded-full">
                            {item.contas_geradas_ids?.length || 0}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600 max-w-xs">
                          <span title={item.observacao || ''}>
                            {truncateText(item.observacao)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          {item.movimentacao_bancaria_id ? (
                            <a
                              href="/financeiro/movimentacoes"
                              className="text-blue-600 hover:text-blue-800 font-medium text-sm flex items-center justify-center gap-1"
                              title="Ver movimentação bancária"
                            >
                              #{item.movimentacao_bancaria_id}
                              <ExternalLink size={14} />
                            </a>
                          ) : (
                            <span className="text-gray-400 text-sm">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Paginação */}
              <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
                <div className="text-sm text-gray-700">
                  Mostrando <span className="font-medium">{historico.length}</span> registro(s)
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(Math.max(0, page - 1))}
                    disabled={page === 0}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    Anterior
                  </button>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={!hasMore}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
