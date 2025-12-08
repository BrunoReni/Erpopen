import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import api from '../../services/api';

interface ContaBancaria {
  id?: number;
  nome: string;
  banco: string;
  agencia: string;
  conta: string;
  saldo_inicial: number;
  data_saldo_inicial?: string;
}

interface ContaBancariaFormProps {
  conta: any | null;
  onClose: () => void;
  onSave: () => void;
}

export function ContaBancariaForm({ conta, onClose, onSave }: ContaBancariaFormProps) {
  const [formData, setFormData] = useState<ContaBancaria>({
    nome: '',
    banco: '',
    agencia: '',
    conta: '',
    saldo_inicial: 0,
    data_saldo_inicial: new Date().toISOString().slice(0, 10)
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (conta) {
      setFormData({
        nome: conta.nome || '',
        banco: conta.banco || '',
        agencia: conta.agencia || '',
        conta: conta.conta || '',
        saldo_inicial: conta.saldo_inicial || 0,
        data_saldo_inicial: conta.data_saldo_inicial 
          ? new Date(conta.data_saldo_inicial).toISOString().slice(0, 10)
          : new Date().toISOString().slice(0, 10)
      });
    }
  }, [conta]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (conta?.id) {
        await api.put(`/financeiro/contas-bancarias/${conta.id}`, formData);
      } else {
        await api.post('/financeiro/contas-bancarias', formData);
      }
      onSave();
    } catch (error) {
      console.error('Erro ao salvar conta bancária:', error);
      alert('Erro ao salvar conta bancária');
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
                {conta ? 'Editar Conta Bancária' : 'Nova Conta Bancária'}
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
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nome da Conta *
              </label>
              <input
                type="text"
                required
                value={formData.nome}
                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                placeholder="Ex: Conta Corrente Principal"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Banco *
                </label>
                <input
                  type="text"
                  required
                  value={formData.banco}
                  onChange={(e) => setFormData({ ...formData, banco: e.target.value })}
                  placeholder="Ex: Banco do Brasil"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Agência *
                </label>
                <input
                  type="text"
                  required
                  value={formData.agencia}
                  onChange={(e) => setFormData({ ...formData, agencia: e.target.value })}
                  placeholder="Ex: 1234-5"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Número da Conta *
                </label>
                <input
                  type="text"
                  required
                  value={formData.conta}
                  onChange={(e) => setFormData({ ...formData, conta: e.target.value })}
                  placeholder="Ex: 12345-6"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Saldo Inicial *
                </label>
                <input
                  type="number"
                  required
                  step="0.01"
                  min="0"
                  value={formData.saldo_inicial}
                  onChange={(e) => setFormData({ ...formData, saldo_inicial: parseFloat(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data do Saldo Inicial
              </label>
              <input
                type="date"
                value={formData.data_saldo_inicial}
                onChange={(e) => setFormData({ ...formData, data_saldo_inicial: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="flex justify-end gap-4 pt-6 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
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
