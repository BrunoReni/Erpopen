import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, DollarSign } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import { ContaBancariaForm } from './ContaBancariaForm';
import api from '../../services/api';

interface ContaBancaria {
  id: number;
  nome: string;
  banco: string;
  agencia: string;
  conta: string;
  saldo_inicial: number;
  saldo_atual: number;
  ativa: number;
  created_at: string;
}

export function ContasBancariasList() {
  const [contas, setContas] = useState<ContaBancaria[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingConta, setEditingConta] = useState<ContaBancaria | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchContas();
  }, []);

  const fetchContas = async () => {
    try {
      const response = await api.get('/financeiro/contas-bancarias');
      setContas(response.data);
    } catch (error) {
      console.error('Erro ao buscar contas bancárias:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Deseja realmente desativar esta conta bancária?')) return;
    
    try {
      await api.delete(`/financeiro/contas-bancarias/${id}`);
      fetchContas();
    } catch (error) {
      console.error('Erro ao desativar conta:', error);
      alert('Erro ao desativar conta bancária');
    }
  };

  const filteredContas = contas.filter(conta =>
    conta.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conta.banco.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalSaldo = contas.reduce((sum, conta) => sum + conta.saldo_atual, 0);

  if (showForm || editingConta) {
    return (
      <ContaBancariaForm
        conta={editingConta}
        onClose={() => {
          setShowForm(false);
          setEditingConta(null);
        }}
        onSave={() => {
          fetchContas();
          setShowForm(false);
          setEditingConta(null);
        }}
      />
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Contas Bancárias</h1>
            <p className="text-gray-600 mt-1">Gerencie suas contas bancárias</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Nova Conta
          </button>
        </div>

        {/* Card com Saldo Total */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-white bg-opacity-20 rounded-lg">
              <DollarSign className="w-8 h-8" />
            </div>
            <div>
              <p className="text-blue-100 text-sm">Saldo Total</p>
              <p className="text-3xl font-bold">
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: 'BRL'
                }).format(totalSaldo)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <input
              type="text"
              placeholder="Buscar por nome ou banco..."
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
                    Nome da Conta
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Banco
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Agência
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Conta
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Saldo Atual
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
                ) : filteredContas.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                      Nenhuma conta bancária encontrada
                    </td>
                  </tr>
                ) : (
                  filteredContas.map((conta) => (
                    <tr key={conta.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <DollarSign className="w-5 h-5 text-blue-600" />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{conta.nome}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {conta.banco}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {conta.agencia}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {conta.conta}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${
                          conta.saldo_atual >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(conta.saldo_atual)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setEditingConta(conta)}
                            className="text-yellow-600 hover:text-yellow-900"
                            title="Editar"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(conta.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Desativar"
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
