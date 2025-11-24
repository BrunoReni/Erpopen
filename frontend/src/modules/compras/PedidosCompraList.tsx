import { useState, useEffect } from 'react';
import { Plus, Edit2, Eye, CheckCircle, XCircle, Trash2 } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import { PedidoCompraForm } from './PedidoCompraForm';
import api from '../../services/api';

interface ItemPedido {
  id?: number;
  material_id?: number;
  descricao: string;
  quantidade: number;
  unidade_medida: string;
  preco_unitario: number;
  preco_total?: number;
}

interface PedidoCompra {
  id: number;
  numero: string;
  fornecedor_id: number;
  fornecedor?: { nome: string };
  data_entrega_prevista: string;
  status: string;
  valor_total: number;
  observacoes?: string;
  itens: ItemPedido[];
  created_at: string;
}

export function PedidosCompraList() {
  const [pedidos, setPedidos] = useState<PedidoCompra[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingPedido, setEditingPedido] = useState<PedidoCompra | null>(null);
  const [viewingPedido, setViewingPedido] = useState<PedidoCompra | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchPedidos();
  }, []);

  const fetchPedidos = async () => {
    try {
      const response = await api.get('/compras/pedidos');
      setPedidos(response.data);
    } catch (error) {
      console.error('Erro ao buscar pedidos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Deseja realmente cancelar este pedido?')) return;
    
    try {
      await api.delete(`/compras/pedidos/${id}`);
      fetchPedidos();
    } catch (error) {
      console.error('Erro ao cancelar pedido:', error);
      alert('Erro ao cancelar pedido');
    }
  };

  const handleAprovar = async (id: number) => {
    if (!confirm('Deseja aprovar este pedido?')) return;
    
    try {
      await api.post(`/compras/pedidos/${id}/aprovar`);
      fetchPedidos();
    } catch (error: any) {
      console.error('Erro ao aprovar pedido:', error);
      alert(error.response?.data?.detail || 'Erro ao aprovar pedido');
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; className: string }> = {
      rascunho: { label: 'Rascunho', className: 'bg-gray-200 text-gray-800' },
      solicitado: { label: 'Solicitado', className: 'bg-blue-200 text-blue-800' },
      aprovado: { label: 'Aprovado', className: 'bg-green-200 text-green-800' },
      pedido_enviado: { label: 'Enviado', className: 'bg-purple-200 text-purple-800' },
      recebido: { label: 'Recebido', className: 'bg-teal-200 text-teal-800' },
      cancelado: { label: 'Cancelado', className: 'bg-red-200 text-red-800' },
    };

    const config = statusConfig[status] || { label: status, className: 'bg-gray-200 text-gray-800' };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${config.className}`}>
        {config.label}
      </span>
    );
  };

  const filteredPedidos = pedidos.filter(pedido =>
    pedido.numero.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pedido.fornecedor?.nome.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (showForm || editingPedido) {
    return (
      <PedidoCompraForm
        pedido={editingPedido}
        onClose={() => {
          setShowForm(false);
          setEditingPedido(null);
        }}
        onSave={() => {
          fetchPedidos();
          setShowForm(false);
          setEditingPedido(null);
        }}
      />
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Pedidos de Compra</h1>
            <p className="text-gray-600 mt-1">Gerencie os pedidos de compra</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Novo Pedido
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <input
              type="text"
              placeholder="Buscar por número ou fornecedor..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Número
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fornecedor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data Entrega
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Valor Total
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                      Carregando...
                    </td>
                  </tr>
                ) : filteredPedidos.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                      Nenhum pedido encontrado
                    </td>
                  </tr>
                ) : (
                  filteredPedidos.map((pedido) => (
                    <tr key={pedido.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {pedido.numero}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {pedido.fornecedor?.nome || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(pedido.data_entrega_prevista).toLocaleDateString('pt-BR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(pedido.valor_total)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {getStatusBadge(pedido.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setViewingPedido(pedido)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Visualizar"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          {pedido.status !== 'cancelado' && pedido.status !== 'recebido' && (
                            <>
                              <button
                                onClick={() => setEditingPedido(pedido)}
                                className="text-yellow-600 hover:text-yellow-900"
                                title="Editar"
                              >
                                <Edit2 className="w-4 h-4" />
                              </button>
                              {pedido.status === 'solicitado' && (
                                <button
                                  onClick={() => handleAprovar(pedido.id)}
                                  className="text-green-600 hover:text-green-900"
                                  title="Aprovar"
                                >
                                  <CheckCircle className="w-4 h-4" />
                                </button>
                              )}
                              <button
                                onClick={() => handleDelete(pedido.id)}
                                className="text-red-600 hover:text-red-900"
                                title="Cancelar"
                              >
                                <XCircle className="w-4 h-4" />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Modal de Visualização */}
      {viewingPedido && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Pedido {viewingPedido.numero}
                  </h2>
                  <p className="text-gray-600 mt-1">
                    Fornecedor: {viewingPedido.fornecedor?.nome}
                  </p>
                </div>
                <button
                  onClick={() => setViewingPedido(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  <div className="mt-1">{getStatusBadge(viewingPedido.status)}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Data de Entrega</label>
                  <p className="mt-1 text-gray-900">
                    {new Date(viewingPedido.data_entrega_prevista).toLocaleDateString('pt-BR')}
                  </p>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Itens do Pedido</h3>
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Descrição</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Qtd</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Un</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Preço Unit.</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Total</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {viewingPedido.itens.map((item, index) => (
                        <tr key={index}>
                          <td className="px-4 py-2 text-sm text-gray-900">{item.descricao}</td>
                          <td className="px-4 py-2 text-sm text-gray-900">{item.quantidade}</td>
                          <td className="px-4 py-2 text-sm text-gray-900">{item.unidade_medida}</td>
                          <td className="px-4 py-2 text-sm text-gray-900">
                            {new Intl.NumberFormat('pt-BR', {
                              style: 'currency',
                              currency: 'BRL'
                            }).format(item.preco_unitario)}
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-900 font-medium">
                            {new Intl.NumberFormat('pt-BR', {
                              style: 'currency',
                              currency: 'BRL'
                            }).format(item.preco_total || 0)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-gray-50">
                      <tr>
                        <td colSpan={4} className="px-4 py-2 text-sm font-medium text-gray-900 text-right">
                          Total do Pedido:
                        </td>
                        <td className="px-4 py-2 text-sm font-bold text-gray-900">
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(viewingPedido.valor_total)}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>

              {viewingPedido.observacoes && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Observações</label>
                  <p className="mt-1 text-gray-900 whitespace-pre-wrap">{viewingPedido.observacoes}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </MainLayout>
  );
}
