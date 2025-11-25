import { useState, useEffect } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import axios from 'axios';

interface ItemCotacao {
  material_id?: number;
  descricao: string;
  quantidade: number;
  unidade: string;
  observacoes?: string;
}

interface CotacaoFormData {
  descricao: string;
  data_limite_resposta?: string;
  observacoes?: string;
  itens: ItemCotacao[];
}

interface CotacaoFormProps {
  cotacao?: any;
  onClose: () => void;
}

export function CotacaoForm({ cotacao, onClose }: CotacaoFormProps) {
  const [formData, setFormData] = useState<CotacaoFormData>({
    descricao: '',
    data_limite_resposta: '',
    observacoes: '',
    itens: [
      { descricao: '', quantidade: 1, unidade: 'UN', observacoes: '' }
    ]
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [materiais, setMateriais] = useState<any[]>([]);

  useEffect(() => {
    loadMateriais();
    if (cotacao) {
      setFormData({
        descricao: cotacao.descricao || '',
        data_limite_resposta: cotacao.data_limite_resposta 
          ? new Date(cotacao.data_limite_resposta).toISOString().split('T')[0]
          : '',
        observacoes: cotacao.observacoes || '',
        itens: cotacao.itens?.length > 0 ? cotacao.itens : [
          { descricao: '', quantidade: 1, unidade: 'UN', observacoes: '' }
        ]
      });
    }
  }, [cotacao]);

  const loadMateriais = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/materiais/materiais', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMateriais(response.data);
    } catch (error) {
      console.error('Erro ao carregar materiais:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleItemChange = (index: number, field: string, value: any) => {
    const newItens = [...formData.itens];
    newItens[index] = {
      ...newItens[index],
      [field]: value
    };
    setFormData(prev => ({
      ...prev,
      itens: newItens
    }));
  };

  const handleMaterialSelect = (index: number, materialId: string) => {
    const material = materiais.find(m => m.id === parseInt(materialId));
    if (material) {
      handleItemChange(index, 'material_id', material.id);
      handleItemChange(index, 'descricao', material.nome);
      handleItemChange(index, 'unidade', material.unidade_medida);
    }
  };

  const addItem = () => {
    setFormData(prev => ({
      ...prev,
      itens: [...prev.itens, { descricao: '', quantidade: 1, unidade: 'UN', observacoes: '' }]
    }));
  };

  const removeItem = (index: number) => {
    if (formData.itens.length > 1) {
      setFormData(prev => ({
        ...prev,
        itens: prev.itens.filter((_, i) => i !== index)
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validações
    if (!formData.descricao) {
      setError('Descrição é obrigatória');
      setLoading(false);
      return;
    }

    if (formData.itens.length === 0) {
      setError('Adicione pelo menos um item');
      setLoading(false);
      return;
    }

    for (let item of formData.itens) {
      if (!item.descricao || item.quantidade <= 0) {
        setError('Todos os itens devem ter descrição e quantidade válida');
        setLoading(false);
        return;
      }
    }

    try {
      const token = localStorage.getItem('access_token');
      const payload = {
        ...formData,
        data_limite_resposta: formData.data_limite_resposta || null
      };

      if (cotacao) {
        await axios.put(
          `http://localhost:8000/cotacoes/cotacoes/${cotacao.id}`,
          payload,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        await axios.post(
          'http://localhost:8000/cotacoes/cotacoes',
          payload,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }

      onClose();
    } catch (err: any) {
      console.error('Erro ao salvar cotação:', err);
      setError(err.response?.data?.detail || 'Erro ao salvar cotação');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {cotacao ? 'Editar Cotação' : 'Nova Cotação'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Dados Principais */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Dados da Cotação</h3>
            
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data Limite para Resposta
                </label>
                <input
                  type="date"
                  name="data_limite_resposta"
                  value={formData.data_limite_resposta}
                  onChange={handleChange}
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
                />
              </div>
            </div>
          </div>

          {/* Itens da Cotação */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">Itens da Cotação</h3>
              <button
                type="button"
                onClick={addItem}
                className="flex items-center px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 mr-1" />
                Adicionar Item
              </button>
            </div>

            <div className="space-y-3">
              {formData.itens.map((item, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-sm font-medium text-gray-700">Item {index + 1}</span>
                    {formData.itens.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeItem(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
                    <div className="md:col-span-4">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Material (opcional)
                      </label>
                      <select
                        value={item.material_id || ''}
                        onChange={(e) => handleMaterialSelect(index, e.target.value)}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Selecione ou digite abaixo</option>
                        {materiais.map(m => (
                          <option key={m.id} value={m.id}>
                            {m.codigo} - {m.nome}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="md:col-span-4">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Descrição *
                      </label>
                      <input
                        type="text"
                        value={item.descricao}
                        onChange={(e) => handleItemChange(index, 'descricao', e.target.value)}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Quantidade *
                      </label>
                      <input
                        type="number"
                        value={item.quantidade}
                        onChange={(e) => handleItemChange(index, 'quantidade', parseFloat(e.target.value) || 0)}
                        step="0.01"
                        min="0.01"
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Unidade
                      </label>
                      <input
                        type="text"
                        value={item.unidade}
                        onChange={(e) => handleItemChange(index, 'unidade', e.target.value)}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div className="md:col-span-12">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Observações do Item
                      </label>
                      <input
                        type="text"
                        value={item.observacoes || ''}
                        onChange={(e) => handleItemChange(index, 'observacoes', e.target.value)}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        placeholder="Ex: Preferência por marca específica..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Salvando...' : cotacao ? 'Atualizar' : 'Criar Cotação'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
