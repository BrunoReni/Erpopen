import { useState, useEffect } from 'react';
import { MainLayout } from '../../components/layout/MainLayout';
import { Plus, Search, Edit, DollarSign, ChevronDown, ChevronUp, Layers } from 'lucide-react';
import axios from 'axios';
import { ContaPagarForm } from './ContaPagarForm';
import { BaixaContaPagarModal } from './BaixaContaPagarModal';
import { ParcelamentoForm } from './ParcelamentoForm';
import { ParcelasTable } from './ParcelasTable';

interface Parcela {
  id: number;
  numero_parcela: number;
  total_parcelas: number;
  data_vencimento: string;
  valor: number;
  valor_pago: number;
  status: string;
  juros: number;
  desconto: number;
}

interface ContaPagar {
  id: number;
  descricao: string;
  fornecedor_id: number;
  data_vencimento: string;
  valor_original: number;
  valor_pago: number;
  juros: number;
  desconto: number;
  status: string;
  observacoes: string;
  tipo_parcelamento?: string;
  quantidade_parcelas?: number;
}

export function ContasPagarList() {
  const [contas, setContas] = useState<ContaPagar[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingConta, setEditingConta] = useState<ContaPagar | null>(null);
  const [isBaixaModalOpen, setIsBaixaModalOpen] = useState(false);
  const [contaBaixar, setContaBaixar] = useState<ContaPagar | null>(null);
  const [isParcelamentoFormOpen, setIsParcelamentoFormOpen] = useState(false);
  const [expandedContaId, setExpandedContaId] = useState<number | null>(null);
  const [parcelas, setParcelas] = useState<Record<number, Parcela[]>>({});
  const [loadingParcelas, setLoadingParcelas] = useState<Record<number, boolean>>({});

  useEffect(() => {
    loadContas();
  }, []);

  const loadContas = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/financeiro/contas-pagar', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setContas(response.data);
    } catch (error) {
      console.error('Erro ao carregar contas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (conta: ContaPagar) => {
    setEditingConta(conta);
    setIsFormOpen(true);
  };

  const handleBaixar = (conta: ContaPagar) => {
    setContaBaixar(conta);
    setIsBaixaModalOpen(true);
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingConta(null);
  };

  const handleBaixaModalClose = () => {
    setIsBaixaModalOpen(false);
    setContaBaixar(null);
  };

  const handleFormSuccess = () => {
    loadContas();
  };

  const handleBaixaSuccess = () => {
    loadContas();
  };

  const toggleExpandConta = async (contaId: number) => {
    if (expandedContaId === contaId) {
      setExpandedContaId(null);
    } else {
      setExpandedContaId(contaId);
      if (!parcelas[contaId]) {
        await loadParcelas(contaId);
      }
    }
  };

  const loadParcelas = async (contaId: number) => {
    setLoadingParcelas(prev => ({ ...prev, [contaId]: true }));
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `http://localhost:8000/financeiro/contas-pagar/${contaId}/parcelas`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setParcelas(prev => ({ ...prev, [contaId]: response.data }));
    } catch (error) {
      console.error('Erro ao carregar parcelas:', error);
    } finally {
      setLoadingParcelas(prev => ({ ...prev, [contaId]: false }));
    }
  };

  const handleBaixarParcela = (parcelaId: number) => {
    // This would open a modal similar to BaixaContaPagarModal but for individual parcels
    // For now, we'll use a simple approach
    const contaId = expandedContaId;
    if (!contaId) return;
    
    const conta = contas.find(c => c.id === contaId);
    if (conta) {
      setContaBaixar({ ...conta, id: parcelaId }); // Using parcelaId to indicate it's a parcela
      setIsBaixaModalOpen(true);
    }
  };

  const handleReagendarParcela = async (parcelaId: number, novaData: string) => {
    // This is handled in ParcelasTable
    await loadParcelas(expandedContaId!);
  };

  const filteredContas = contas.filter(c =>
    c.descricao.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pago':
        return 'bg-green-100 text-green-800';
      case 'pendente':
        return 'bg-yellow-100 text-yellow-800';
      case 'parcial':
        return 'bg-blue-100 text-blue-800';
      case 'atrasado':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      'pendente': 'Pendente',
      'parcial': 'Parcial',
      'pago': 'Pago',
      'atrasado': 'Atrasado'
    };
    return labels[status] || status;
  };

  // Number of table columns for colspan calculation
  const TABLE_COLUMNS = 6;

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Contas a Pagar</h1>
            <p className="text-gray-500 mt-1">Gerencie as despesas e pagamentos</p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => setIsParcelamentoFormOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              <Layers size={20} />
              Novo Parcelamento
            </button>
            <button 
              onClick={() => setIsFormOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus size={20} />
              Nova Conta a Pagar
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Buscar por descrição..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Carregando...</div>
          ) : filteredContas.length === 0 ? (
            <div className="p-8 text-center text-gray-500">Nenhuma conta encontrada</div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vencimento</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pago</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ações</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredContas.map((conta) => (
                  <>
                    <tr key={conta.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {conta.tipo_parcelamento === 'parcelado' && conta.quantidade_parcelas && conta.quantidade_parcelas > 1 && (
                            <button
                              onClick={() => toggleExpandConta(conta.id)}
                              className="text-gray-400 hover:text-gray-600"
                            >
                              {expandedContaId === conta.id ? (
                                <ChevronUp size={16} />
                              ) : (
                                <ChevronDown size={16} />
                              )}
                            </button>
                          )}
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {conta.descricao}
                              {conta.tipo_parcelamento === 'parcelado' && conta.quantidade_parcelas && (
                                <span className="ml-2 text-xs text-purple-600">
                                  ({conta.quantidade_parcelas}x)
                                </span>
                              )}
                            </div>
                            {conta.observacoes && (
                              <div className="text-sm text-gray-500">{conta.observacoes.substring(0, 50)}...</div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(conta.data_vencimento).toLocaleDateString('pt-BR')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          R$ {conta.valor_original.toFixed(2)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          R$ {conta.valor_pago.toFixed(2)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(conta.status)}`}>
                          {getStatusLabel(conta.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          {conta.status !== 'pago' && (
                            <button 
                              onClick={() => handleBaixar(conta)}
                              className="text-red-600 hover:text-red-900"
                              title="Baixar conta"
                            >
                              <DollarSign size={18} />
                            </button>
                          )}
                          <button 
                            onClick={() => handleEdit(conta)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Editar conta"
                          >
                            <Edit size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                    {expandedContaId === conta.id && (
                      <tr>
                        <td colSpan={TABLE_COLUMNS} className="px-6 py-4 bg-gray-50">
                          {loadingParcelas[conta.id] ? (
                            <div className="text-center text-gray-500">Carregando parcelas...</div>
                          ) : parcelas[conta.id] ? (
                            <ParcelasTable
                              contaId={conta.id}
                              tipo="pagar"
                              parcelas={parcelas[conta.id]}
                              onBaixarParcela={handleBaixarParcela}
                              onReagendarParcela={handleReagendarParcela}
                              onRefresh={() => loadParcelas(conta.id)}
                            />
                          ) : (
                            <div className="text-center text-gray-500">Nenhuma parcela encontrada</div>
                          )}
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <ContaPagarForm
        isOpen={isFormOpen}
        onClose={handleFormClose}
        onSuccess={handleFormSuccess}
        conta={editingConta}
      />

      <BaixaContaPagarModal
        isOpen={isBaixaModalOpen}
        onClose={handleBaixaModalClose}
        onSuccess={handleBaixaSuccess}
        conta={contaBaixar}
      />

      <ParcelamentoForm
        isOpen={isParcelamentoFormOpen}
        onClose={() => setIsParcelamentoFormOpen(false)}
        onSuccess={handleFormSuccess}
        tipo="pagar"
      />
    </MainLayout>
  );
}
