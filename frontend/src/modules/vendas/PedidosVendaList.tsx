import { useState, useEffect } from 'react';
import { MainLayout } from '../../components/layout/MainLayout';
import { Plus, Search, Eye, Edit, CheckCircle, FileText, XCircle, Filter } from 'lucide-react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface ItemPedidoVenda {
  id: number;
  material_id: number;
  quantidade: number;
  preco_unitario: number;
  percentual_desconto: number;
  valor_desconto: number;
  subtotal: number;
  observacao?: string;
}

interface PedidoVenda {
  id: number;
  codigo: string;
  cliente_id: number;
  vendedor_id?: number;
  data_pedido: string;
  data_entrega_prevista?: string;
  data_faturamento?: string;
  status: string;
  condicao_pagamento?: string;
  valor_produtos: number;
  valor_desconto: number;
  valor_frete: number;
  valor_total: number;
  observacoes?: string;
  itens: ItemPedidoVenda[];
}

interface Cliente {
  id: number;
  codigo: string;
  nome: string;
}

const statusColors: { [key: string]: string } = {
  orcamento: 'bg-yellow-100 text-yellow-800',
  aprovado: 'bg-blue-100 text-blue-800',
  faturado: 'bg-green-100 text-green-800',
  cancelado: 'bg-red-100 text-red-800'
};

const statusLabels: { [key: string]: string } = {
  orcamento: 'Orçamento',
  aprovado: 'Aprovado',
  faturado: 'Faturado',
  cancelado: 'Cancelado'
};

export function PedidosVendaList() {
  const navigate = useNavigate();
  const [pedidos, setPedidos] = useState<PedidoVenda[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [clienteFilter, setClienteFilter] = useState<string>('');

  useEffect(() => {
    loadData();
  }, [statusFilter, clienteFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      // Carregar pedidos
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);
      if (clienteFilter) params.append('cliente_id', clienteFilter);

      const pedidosResponse = await axios.get(
        `http://localhost:8000/vendas/pedidos?${params.toString()}`,
        { headers }
      );
      setPedidos(pedidosResponse.data);

      // Carregar clientes para filtro
      const clientesResponse = await axios.get(
        'http://localhost:8000/vendas/clientes',
        { headers }
      );
      setClientes(clientesResponse.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAprovar = async (id: number) => {
    if (!confirm('Deseja aprovar este pedido? Esta ação validará o estoque disponível.')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `http://localhost:8000/vendas/pedidos/${id}/aprovar`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Pedido aprovado com sucesso!');
      loadData();
    } catch (error: any) {
      console.error('Erro ao aprovar pedido:', error);
      alert(error.response?.data?.detail || 'Erro ao aprovar pedido');
    }
  };

  const handleFaturar = async (id: number) => {
    if (!confirm('Deseja faturar este pedido? Esta ação irá:\n- Baixar o estoque\n- Gerar conta a receber\n- Marcar o pedido como faturado')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `http://localhost:8000/vendas/pedidos/${id}/faturar`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Pedido faturado com sucesso!');
      loadData();
    } catch (error: any) {
      console.error('Erro ao faturar pedido:', error);
      alert(error.response?.data?.detail || 'Erro ao faturar pedido');
    }
  };

  const handleCancelar = async (id: number) => {
    if (!confirm('Tem certeza que deseja cancelar este pedido?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `http://localhost:8000/vendas/pedidos/${id}/cancelar`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Pedido cancelado com sucesso!');
      loadData();
    } catch (error: any) {
      console.error('Erro ao cancelar pedido:', error);
      alert(error.response?.data?.detail || 'Erro ao cancelar pedido');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir este pedido?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(
        `http://localhost:8000/vendas/pedidos/${id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Pedido excluído com sucesso!');
      loadData();
    } catch (error: any) {
      console.error('Erro ao excluir pedido:', error);
      alert(error.response?.data?.detail || 'Erro ao excluir pedido');
    }
  };

  const getClienteNome = (clienteId: number) => {
    const cliente = clientes.find(c => c.id === clienteId);
    return cliente ? cliente.nome : 'N/A';
  };

  const filteredPedidos = pedidos.filter(pedido =>
    pedido.codigo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    getClienteNome(pedido.cliente_id).toLowerCase().includes(searchTerm.toLowerCase())
  );

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
            <h1 className="text-2xl font-bold text-gray-900">Pedidos de Venda</h1>
            <p className="text-gray-600 mt-1">Gerencie os pedidos de venda</p>
          </div>
          <button
            onClick={() => navigate('/vendas/pedidos/novo')}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Plus size={20} />
            Novo Pedido
          </button>
        </div>

        {/* Filtros */}
        <div className="bg-white p-4 rounded-lg shadow space-y-4">
          <div className="flex items-center gap-2 text-gray-700 font-semibold">
            <Filter size={20} />
            <span>Filtros</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Busca */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Buscar por código ou cliente..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg"
              />
            </div>

            {/* Filtro de Status */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              <option value="">Todos os status</option>
              <option value="orcamento">Orçamento</option>
              <option value="aprovado">Aprovado</option>
              <option value="faturado">Faturado</option>
              <option value="cancelado">Cancelado</option>
            </select>

            {/* Filtro de Cliente */}
            <select
              value={clienteFilter}
              onChange={(e) => setClienteFilter(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              <option value="">Todos os clientes</option>
              {clientes.map(cliente => (
                <option key={cliente.id} value={cliente.id}>
                  {cliente.codigo} - {cliente.nome}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Tabela */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Código
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Data
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Valor Total
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPedidos.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    Nenhum pedido encontrado
                  </td>
                </tr>
              ) : (
                filteredPedidos.map((pedido) => (
                  <tr key={pedido.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {pedido.codigo}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {getClienteNome(pedido.cliente_id)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {new Date(pedido.data_pedido).toLocaleDateString('pt-BR')}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[pedido.status]}`}>
                        {statusLabels[pedido.status]}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm font-medium text-gray-900">
                        R$ {pedido.valor_total.toFixed(2)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => navigate(`/vendas/pedidos/${pedido.id}`)}
                          className="text-blue-600 hover:text-blue-900"
                          title="Ver detalhes"
                        >
                          <Eye size={18} />
                        </button>

                        {pedido.status === 'orcamento' && (
                          <>
                            <button
                              onClick={() => navigate(`/vendas/pedidos/${pedido.id}/editar`)}
                              className="text-green-600 hover:text-green-900"
                              title="Editar"
                            >
                              <Edit size={18} />
                            </button>
                            <button
                              onClick={() => handleAprovar(pedido.id)}
                              className="text-blue-600 hover:text-blue-900"
                              title="Aprovar"
                            >
                              <CheckCircle size={18} />
                            </button>
                            <button
                              onClick={() => handleDelete(pedido.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Excluir"
                            >
                              <XCircle size={18} />
                            </button>
                          </>
                        )}

                        {pedido.status === 'aprovado' && (
                          <button
                            onClick={() => handleFaturar(pedido.id)}
                            className="text-green-600 hover:text-green-900"
                            title="Faturar"
                          >
                            <FileText size={18} />
                          </button>
                        )}

                        {(pedido.status === 'orcamento' || pedido.status === 'aprovado') && (
                          <button
                            onClick={() => handleCancelar(pedido.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Cancelar"
                          >
                            <XCircle size={18} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">ℹ️ Informações</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• <strong>Orçamento:</strong> Pode ser editado, aprovado ou excluído</li>
            <li>• <strong>Aprovado:</strong> Estoque validado, pronto para faturamento</li>
            <li>• <strong>Faturado:</strong> Estoque baixado e conta a receber gerada</li>
            <li>• <strong>Cancelado:</strong> Pedido cancelado, sem movimentações</li>
          </ul>
        </div>
      </div>
    </MainLayout>
  );
}
