import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import api from '../../services/api';

interface MovimentacaoBancaria {
  id?: number;
  conta_bancaria_id: number;
  tipo: string;
  natureza: string;
  valor: number;
  descricao: string;
  data_movimentacao?: string;
  data_competencia?: string;
  conta_pagar_id?: number | null;
  conta_receber_id?: number | null;
}

interface ContaBancaria {
  id: number;
  nome: string;
  saldo_atual: number;
}

interface MovimentacaoBancariaFormProps {
  movimentacao: any | null;
  onClose: () => void;
  onSave: () => void;
}

const tiposMovimentacao = [
  { value: 'deposito', label: 'Depósito' },
  { value: 'saque', label: 'Saque' },
  { value: 'tarifa', label: 'Tarifa' },
  { value: 'transferencia_entrada', label: 'Transferência Entrada' },
  { value: 'transferencia_saida', label: 'Transferência Saída' },
  { value: 'juros', label: 'Juros' },
  { value: 'estorno', label: 'Estorno' },
  { value: 'outros', label: 'Outros' }
];

export function MovimentacaoBancariaForm({ movimentacao, onClose, onSave }: MovimentacaoBancariaFormProps) {
  const [formData, setFormData] = useState<MovimentacaoBancaria>({
    conta_bancaria_id: 0,
    tipo: 'deposito',
    natureza: 'ENTRADA',
    valor: 0,
    descricao: '',
    data_movimentacao: new Date().toISOString().slice(0, 16),
    data_competencia: new Date().toISOString().slice(0, 10),
    conta_pagar_id: null,
    conta_receber_id: null
  });
  const [contas, setContas] = useState<ContaBancaria[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchContas();
  }, []);

  useEffect(() => {
    if (movimentacao) {
      setFormData({
        conta_bancaria_id: movimentacao.conta_bancaria_id || 0,
        tipo: movimentacao.tipo || 'deposito',
        natureza: movimentacao.natureza || 'ENTRADA',
        valor: movimentacao.valor || 0,
        descricao: movimentacao.descricao || '',
        data_movimentacao: movimentacao.data_movimentacao 
          ? new Date(movimentacao.data_movimentacao).toISOString().slice(0, 16)
          : new Date().toISOString().slice(0, 16),
        data_competencia: movimentacao.data_competencia 
          ? new Date(movimentacao.data_competencia).toISOString().slice(0, 10)
          : new Date().toISOString().slice(0, 10),
        conta_pagar_id: movimentacao.conta_pagar_id || null,
        conta_receber_id: movimentacao.conta_receber_id || null
      });
    }
  }, [movimentacao]);

  const fetchContas = async () => {
    try {
      const response = await api.get('/financeiro/contas-bancarias');
      setContas(response.data);
    } catch (error) {
      console.error('Erro ao buscar contas bancárias:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.conta_bancaria_id) {
      alert('Selecione uma conta bancária');
      return;
    }
    
    if (formData.valor <= 0) {
      alert('O valor deve ser maior que zero');
      return;
    }
    
    if (!formData.descricao.trim()) {
      alert('Informe uma descrição');
      return;
    }
    
    setLoading(true);

    try {
      if (movimentacao?.id) {
        await api.put(`/financeiro/movimentacoes-bancarias/${movimentacao.id}`, formData);
      } else {
        await api.post('/financeiro/movimentacoes-bancarias', formData);
      }
      onSave();
    } catch (error: any) {
      console.error('Erro ao salvar movimentação:', error);
      alert(error.response?.data?.detail || 'Erro ao salvar movimentação');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">
                {movimentacao ? 'Editar Movimentação' : 'Nova Movimentação Bancária'}
              </h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Conta Bancária *
                </label>
                <select
                  value={formData.conta_bancaria_id}
                  onChange={(e) => setFormData({ ...formData, conta_bancaria_id: Number(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value={0}>Selecione uma conta</option>
                  {contas.map(conta => (
                    <option key={conta.id} value={conta.id}>
                      {conta.nome} - Saldo: R$ {conta.saldo_atual.toFixed(2)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Movimentação *
                </label>
                <select
                  value={formData.tipo}
                  onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  {tiposMovimentacao.map(tipo => (
                    <option key={tipo.value} value={tipo.value}>
                      {tipo.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Natureza *
                </label>
                <select
                  value={formData.natureza}
                  onChange={(e) => setFormData({ ...formData, natureza: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="ENTRADA">Entrada</option>
                  <option value="SAIDA">Saída</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Valor *
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.valor}
                  onChange={(e) => setFormData({ ...formData, valor: Number(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                  min="0.01"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Movimentação
                </label>
                <input
                  type="datetime-local"
                  value={formData.data_movimentacao}
                  onChange={(e) => setFormData({ ...formData, data_movimentacao: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Competência
                </label>
                <input
                  type="date"
                  value={formData.data_competencia}
                  onChange={(e) => setFormData({ ...formData, data_competencia: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Descrição *
                </label>
                <textarea
                  value={formData.descricao}
                  onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                  placeholder="Descreva a movimentação..."
                />
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                disabled={loading}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
                disabled={loading}
              >
                {loading ? 'Salvando...' : 'Salvar'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}
