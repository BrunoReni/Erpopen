import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import axios from 'axios';

interface ContaPagarFormData {
  descricao: string;
  fornecedor_id?: number;
  centro_custo_id?: number;
  data_vencimento: string;
  valor_original: number;
  observacoes?: string;
}

interface ContaPagarFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  conta?: any;
}

export function ContaPagarForm({ isOpen, onClose, onSuccess, conta }: ContaPagarFormProps) {
  const [formData, setFormData] = useState<ContaPagarFormData>({
    descricao: '',
    fornecedor_id: undefined,
    centro_custo_id: undefined,
    data_vencimento: '',
    valor_original: 0,
    observacoes: ''
  });
  
  const [fornecedores, setFornecedores] = useState<any[]>([]);
  const [centrosCusto, setCentrosCusto] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadFornecedores();
      loadCentrosCusto();
      
      if (conta) {
        setFormData({
          descricao: conta.descricao || '',
          fornecedor_id: conta.fornecedor_id || undefined,
          centro_custo_id: conta.centro_custo_id || undefined,
          data_vencimento: conta.data_vencimento?.split('T')[0] || '',
          valor_original: conta.valor_original || 0,
          observacoes: conta.observacoes || ''
        });
      } else {
        setFormData({
          descricao: '',
          fornecedor_id: undefined,
          centro_custo_id: undefined,
          data_vencimento: '',
          valor_original: 0,
          observacoes: ''
        });
      }
      setError('');
    }
  }, [isOpen, conta]);

  const loadFornecedores = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/compras/fornecedores', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFornecedores(response.data);
    } catch (err) {
      console.error('Erro ao carregar fornecedores:', err);
    }
  };

  const loadCentrosCusto = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/financeiro/centros-custo', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCentrosCusto(response.data);
    } catch (err) {
      console.error('Erro ao carregar centros de custo:', err);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    let finalValue: any = value;
    
    if (type === 'number') {
      finalValue = parseFloat(value) || 0;
    } else if (name === 'fornecedor_id' || name === 'centro_custo_id') {
      finalValue = value ? parseInt(value) : undefined;
    }
    
    setFormData({
      ...formData,
      [name]: finalValue
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const url = conta 
        ? `http://localhost:8000/financeiro/contas-pagar/${conta.id}`
        : 'http://localhost:8000/financeiro/contas-pagar';
      
      const method = conta ? 'put' : 'post';

      await axios[method](url, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Erro ao salvar conta:', err);
      setError(err.response?.data?.detail || 'Erro ao salvar conta a pagar');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">
            {conta ? 'Editar Conta a Pagar' : 'Nova Conta a Pagar'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descrição *
              </label>
              <input
                type="text"
                name="descricao"
                value={formData.descricao}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Descrição da despesa"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fornecedor
              </label>
              <select
                name="fornecedor_id"
                value={formData.fornecedor_id || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Selecione...</option>
                {fornecedores.map(f => (
                  <option key={f.id} value={f.id}>{f.nome}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Centro de Custo
              </label>
              <select
                name="centro_custo_id"
                value={formData.centro_custo_id || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Selecione...</option>
                {centrosCusto.map(c => (
                  <option key={c.id} value={c.id}>{c.nome}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data de Vencimento *
              </label>
              <input
                type="date"
                name="data_vencimento"
                value={formData.data_vencimento}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Valor (R$) *
              </label>
              <input
                type="number"
                name="valor_original"
                value={formData.valor_original}
                onChange={handleChange}
                required
                step="0.01"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observações
              </label>
              <textarea
                name="observacoes"
                value={formData.observacoes}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Informações adicionais"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
              disabled={loading}
            >
              {loading ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
