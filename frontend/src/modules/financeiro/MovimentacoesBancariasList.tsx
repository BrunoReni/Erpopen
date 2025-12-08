import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, ArrowUpCircle, ArrowDownCircle, Filter, DollarSign } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import { MovimentacaoBancariaForm } from './MovimentacaoBancariaForm';
import api from '../../services/api';

interface MovimentacaoBancaria {
  id: number;
  conta_bancaria_id: number;
  tipo: string;
  natureza: string;
  data_movimentacao: string;
  data_competencia: string;
  valor: number;
  descricao: string;
  conciliado: boolean;
  data_conciliacao: string | null;
  created_at: string;
}

interface ContaBancaria {
  id: number;
  nome: string;
  saldo_atual: number;
}

export function MovimentacoesBancariasList() {
  const [movimentacoes, setMovimentacoes] = useState<MovimentacaoBancaria[]>([]);
  const [contas, setContas] = useState<ContaBancaria[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingMovimentacao, setEditingMovimentacao] = useState<MovimentacaoBancaria | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [contaFilter, setContaFilter] = useState<number | null>(null);
  const [conciliadoFilter, setConciliadoFilter] = useState<boolean | null>(null);

  useEffect(() => {
    fetchData();
  }, [contaFilter, conciliadoFilter]);

  const fetchData = async () => {
    try {
      const [movimentacoesResponse, contasResponse] = await Promise.all([
        api.get('/financeiro/movimentacoes-bancarias', {
          params: {
            conta_id: contaFilter,
            conciliado: conciliadoFilter
          }
        }),
        api.get('/financeiro/contas-bancarias')
      ]);
      
      setMovimentacoes(movimentacoesResponse.data);
      setContas(contasResponse.data);
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Deseja realmente excluir esta movimentação?')) return;
    
    try {
      await api.delete(`/financeiro/movimentacoes-bancarias/${id}`);
      fetchData();
    } catch (error: any) {
      console.error('Erro ao excluir movimentação:', error);
      alert(error.response?.data?.detail || 'Erro ao excluir movimentação');
    }
  };

  const filteredMovimentacoes = movimentacoes.filter(mov =>
    mov.descricao.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalEntradas = filteredMovimentacoes
    .filter(m => m.natureza === 'ENTRADA')
    .reduce((sum, m) => sum + m.valor, 0);

  const totalSaidas = filteredMovimentacoes
    .filter(m => m.natureza === 'SAIDA')
    .reduce((sum, m) => sum + m.valor, 0);

  const getContaNome = (contaId: number) => {
    const conta = contas.find(c => c.id === contaId);
    return conta ? conta.nome : 'Conta não encontrada';
  };

  if (showForm || editingMovimentacao) {
    return (
      <MovimentacaoBancariaForm
        movimentacao={editingMovimentacao}
        onClose={() => {
          setShowForm(false);
          setEditingMovimentacao(null);
        }}
        onSave={() => {
          fetchData();
          setShowForm(false);
          setEditingMovimentacao(null);
        }}
      />
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Movimentações Bancárias</h1>
            <p className="text-gray-500 mt-2">Gestão de entradas e saídas bancárias</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Nova Movimentação
          </button>
        </div>

        {/* Filtros */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Buscar
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por descrição..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Conta Bancária
              </label>
              <select
                value={contaFilter || ''}
                onChange={(e) => setContaFilter(e.target.value ? Number(e.target.value) : null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Todas as contas</option>
                {contas.map(conta => (
                  <option key={conta.id} value={conta.id}>
                    {conta.nome}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status Conciliação
              </label>
              <select
                value={conciliadoFilter === null ? '' : conciliadoFilter.toString()}
                onChange={(e) => setConciliadoFilter(e.target.value === '' ? null : e.target.value === 'true')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Todas</option>
                <option value="true">Conciliadas</option>
                <option value="false">Pendentes</option>
              </select>
            </div>
          </div>
        </div>

        {/* Cards de Resumo */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <div className="bg-green-100 p-3 rounded-lg">
                <ArrowUpCircle className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <div className="text-sm text-gray-500">Total Entradas</div>
                <div className="text-2xl font-bold text-green-600">
                  R$ {totalEntradas.toFixed(2)}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <div className="bg-red-100 p-3 rounded-lg">
                <ArrowDownCircle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <div className="text-sm text-gray-500">Total Saídas</div>
                <div className="text-2xl font-bold text-red-600">
                  R$ {totalSaidas.toFixed(2)}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <div className="bg-blue-100 p-3 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <div className="text-sm text-gray-500">Saldo Movimentações</div>
                <div className={`text-2xl font-bold ${totalEntradas - totalSaidas >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  R$ {(totalEntradas - totalSaidas).toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tabela */}
        <div className="bg-white rounded-lg shadow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conta</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Natureza</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Valor</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Conciliado</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ações</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                      Carregando...
                    </td>
                  </tr>
                ) : filteredMovimentacoes.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                      Nenhuma movimentação encontrada
                    </td>
                  </tr>
                ) : (
                  filteredMovimentacoes.map((mov) => (
                    <tr key={mov.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(mov.data_competencia || mov.data_movimentacao).toLocaleDateString('pt-BR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {getContaNome(mov.conta_bancaria_id)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {mov.tipo.replace(/_/g, ' ')}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {mov.descricao}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          mov.natureza === 'ENTRADA' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {mov.natureza}
                        </span>
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium text-right ${
                        mov.natureza === 'ENTRADA' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {mov.natureza === 'ENTRADA' ? '+' : '-'} R$ {mov.valor.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          mov.conciliado 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {mov.conciliado ? 'Sim' : 'Não'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => setEditingMovimentacao(mov)}
                            className="text-blue-600 hover:text-blue-900"
                            disabled={mov.conciliado}
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(mov.id)}
                            className="text-red-600 hover:text-red-900"
                            disabled={mov.conciliado}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
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
    </MainLayout>
  );
}
