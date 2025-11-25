import { useState, useEffect } from 'react';
import { MainLayout } from '../../components/layout/MainLayout';
import { Plus, Search, Edit, FileText, CheckCircle, XCircle, ArrowRight, BarChart3 } from 'lucide-react';
import axios from 'axios';
import { CotacaoForm } from './CotacaoForm';

interface ItemCotacao {
  id: number;
  material_id?: number;
  descricao: string;
  quantidade: number;
  unidade: string;
  observacoes?: string;
}

interface RespostaFornecedor {
  id: number;
  fornecedor_id: number;
  prazo_entrega_dias?: number;
  condicao_pagamento?: string;
  valor_total: number;
  selecionada: number;
}

interface Cotacao {
  id: number;
  numero: string;
  descricao: string;
  data_solicitacao: string;
  data_limite_resposta?: string;
  status: string;
  observacoes?: string;
  convertida_pedido_id?: number;
  melhor_fornecedor_id?: number;
  itens: ItemCotacao[];
  respostas: RespostaFornecedor[];
}

export function CotacoesList() {
  const [cotacoes, setCotacoes] = useState<Cotacao[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingCotacao, setEditingCotacao] = useState<Cotacao | null>(null);
  const [viewingComparativo, setViewingComparativo] = useState<number | null>(null);

  useEffect(() => {
    loadCotacoes();
  }, [statusFilter]);

  const loadCotacoes = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const params = statusFilter ? { status: statusFilter } : {};
      const response = await axios.get('http://localhost:8000/cotacoes/cotacoes', {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      setCotacoes(response.data);
    } catch (error) {
      console.error('Erro ao carregar cotações:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (cotacao: Cotacao) => {
    setEditingCotacao(cotacao);
    setIsFormOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir esta cotação?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(`http://localhost:8000/cotacoes/cotacoes/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadCotacoes();
    } catch (error) {
      console.error('Erro ao excluir cotação:', error);
      alert('Erro ao excluir cotação');
    }
  };

  const handleConvert = async (id: number) => {
    if (!confirm('Converter esta cotação em pedido de compra?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `http://localhost:8000/cotacoes/cotacoes/${id}/converter-pedido`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert(response.data.message + '\nPedido: ' + response.data.numero_pedido);
      loadCotacoes();
    } catch (error: any) {
      console.error('Erro ao converter cotação:', error);
      alert(error.response?.data?.detail || 'Erro ao converter cotação');
    }
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingCotacao(null);
    loadCotacoes();
  };

  const filteredCotacoes = cotacoes.filter(cotacao =>
    cotacao.numero.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cotacao.descricao.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (status: string) => {
    const statusConfig: any = {
      rascunho: { color: 'bg-gray-100 text-gray-800', label: 'Rascunho' },
      enviada: { color: 'bg-blue-100 text-blue-800', label: 'Enviada' },
      respondida: { color: 'bg-yellow-100 text-yellow-800', label: 'Respondida' },
      aprovada: { color: 'bg-green-100 text-green-800', label: 'Aprovada' },
      rejeitada: { color: 'bg-red-100 text-red-800', label: 'Rejeitada' },
      convertida: { color: 'bg-purple-100 text-purple-800', label: 'Convertida' },
      cancelada: { color: 'bg-gray-100 text-gray-800', label: 'Cancelada' }
    };

    const config = statusConfig[status] || { color: 'bg-gray-100 text-gray-800', label: status };
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${config.color}`}>
        {config.label}
      </span>
    );
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Carregando...</div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Cotações</h1>
            <p className="text-gray-600 mt-1">Gerencie cotações de preços com fornecedores</p>
          </div>
          <button
            onClick={() => setIsFormOpen(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Nova Cotação
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Buscar por número ou descrição..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos os Status</option>
              <option value="rascunho">Rascunho</option>
              <option value="enviada">Enviada</option>
              <option value="respondida">Respondida</option>
              <option value="aprovada">Aprovada</option>
              <option value="convertida">Convertida</option>
            </select>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Total</div>
            <div className="text-2xl font-bold text-gray-900">{cotacoes.length}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Aguardando Resposta</div>
            <div className="text-2xl font-bold text-blue-600">
              {cotacoes.filter(c => c.status === 'enviada').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Respondidas</div>
            <div className="text-2xl font-bold text-yellow-600">
              {cotacoes.filter(c => c.status === 'respondida').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Convertidas</div>
            <div className="text-2xl font-bold text-green-600">
              {cotacoes.filter(c => c.status === 'convertida').length}
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Número
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Descrição
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Itens
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Respostas
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data Limite
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredCotacoes.map((cotacao) => (
                <tr key={cotacao.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 text-gray-400 mr-2" />
                      <span className="text-sm font-medium text-gray-900">{cotacao.numero}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{cotacao.descricao}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-600">{cotacao.itens?.length || 0} itens</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-600">{cotacao.respostas?.length || 0} respostas</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-600">
                      {cotacao.data_limite_resposta 
                        ? new Date(cotacao.data_limite_resposta).toLocaleDateString('pt-BR')
                        : '-'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(cotacao.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      {cotacao.status === 'respondida' && cotacao.respostas?.length > 0 && (
                        <button
                          onClick={() => setViewingComparativo(cotacao.id)}
                          className="text-purple-600 hover:text-purple-900"
                          title="Ver Comparativo"
                        >
                          <BarChart3 className="w-5 h-5" />
                        </button>
                      )}
                      {cotacao.status === 'aprovada' && !cotacao.convertida_pedido_id && (
                        <button
                          onClick={() => handleConvert(cotacao.id)}
                          className="text-green-600 hover:text-green-900"
                          title="Converter em Pedido"
                        >
                          <ArrowRight className="w-5 h-5" />
                        </button>
                      )}
                      {cotacao.status !== 'convertida' && (
                        <>
                          <button
                            onClick={() => handleEdit(cotacao)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Editar"
                          >
                            <Edit className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleDelete(cotacao.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Excluir"
                          >
                            <XCircle className="w-5 h-5" />
                          </button>
                        </>
                      )}
                      {cotacao.convertida_pedido_id && (
                        <span className="text-xs text-gray-500">
                          Pedido #{cotacao.convertida_pedido_id}
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredCotacoes.length === 0 && (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma cotação encontrada</h3>
              <p className="mt-1 text-sm text-gray-500">
                Comece criando uma nova cotação.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setIsFormOpen(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Nova Cotação
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modal Form */}
      {isFormOpen && (
        <CotacaoForm
          cotacao={editingCotacao}
          onClose={handleFormClose}
        />
      )}

      {/* Modal Comparativo */}
      {viewingComparativo && (
        <ComparativoModal
          cotacaoId={viewingComparativo}
          onClose={() => setViewingComparativo(null)}
        />
      )}
    </MainLayout>
  );
}

// Componente do Modal de Comparativo
function ComparativoModal({ cotacaoId, onClose }: { cotacaoId: number; onClose: () => void }) {
  const [comparativo, setComparativo] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadComparativo();
  }, []);

  const loadComparativo = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `http://localhost:8000/cotacoes/cotacoes/${cotacaoId}/comparativo`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setComparativo(response.data);
    } catch (error) {
      console.error('Erro ao carregar comparativo:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelecionarFornecedor = async (respostaId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `http://localhost:8000/cotacoes/cotacoes/${cotacaoId}/selecionar-fornecedor/${respostaId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Fornecedor selecionado com sucesso!');
      onClose();
    } catch (error) {
      console.error('Erro ao selecionar fornecedor:', error);
      alert('Erro ao selecionar fornecedor');
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="text-lg">Carregando comparativo...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Comparativo de Fornecedores
              </h2>
              <p className="text-gray-600 mt-1">
                {comparativo?.cotacao?.numero} - {comparativo?.cotacao?.descricao}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XCircle className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {comparativo?.fornecedores?.map((fornecedor: any, index: number) => (
            <div
              key={index}
              className={`border rounded-lg p-4 ${
                fornecedor.selecionada ? 'border-green-500 bg-green-50' : 'border-gray-300'
              }`}
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {fornecedor.fornecedor_nome}
                    {fornecedor.selecionada && (
                      <span className="ml-2 px-2 py-1 text-xs bg-green-600 text-white rounded-full">
                        Selecionado
                      </span>
                    )}
                  </h3>
                  <div className="mt-2 space-y-1 text-sm text-gray-600">
                    <div>Prazo: {fornecedor.prazo_entrega_dias} dias</div>
                    <div>Pagamento: {fornecedor.condicao_pagamento}</div>
                    <div className="text-xl font-bold text-gray-900 mt-2">
                      Total: R$ {fornecedor.valor_total?.toFixed(2)}
                    </div>
                  </div>
                </div>
                {!fornecedor.selecionada && (
                  <button
                    onClick={() => handleSelecionarFornecedor(fornecedor.fornecedor_id)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    <CheckCircle className="w-5 h-5 inline mr-2" />
                    Selecionar
                  </button>
                )}
              </div>

              <div className="mt-4">
                <table className="min-w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Item</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Qtd</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Un</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Preço Unit.</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Total</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Marca</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {fornecedor.itens?.map((item: any, idx: number) => (
                      <tr key={idx}>
                        <td className="px-4 py-2 text-sm text-gray-900">{item.descricao}</td>
                        <td className="px-4 py-2 text-sm text-gray-900 text-right">{item.quantidade}</td>
                        <td className="px-4 py-2 text-sm text-gray-900 text-right">{item.unidade}</td>
                        <td className="px-4 py-2 text-sm text-gray-900 text-right">
                          R$ {item.preco_unitario?.toFixed(2)}
                        </td>
                        <td className="px-4 py-2 text-sm font-semibold text-gray-900 text-right">
                          R$ {item.preco_total?.toFixed(2)}
                        </td>
                        <td className="px-4 py-2 text-sm text-gray-600">{item.marca || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}

          {comparativo?.fornecedores?.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Nenhuma resposta de fornecedor cadastrada ainda.
            </div>
          )}
        </div>

        <div className="p-6 border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
