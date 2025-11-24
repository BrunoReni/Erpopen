import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import axios from 'axios';

interface MaterialFormData {
  codigo: string;
  nome: string;
  descricao?: string;
  unidade_medida: string;
  estoque_minimo?: number;
  estoque_maximo?: number;
  preco_medio?: number;
  localizacao?: string;
}

interface MaterialFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  material?: any;
}

export function MaterialForm({ isOpen, onClose, onSuccess, material }: MaterialFormProps) {
  const [formData, setFormData] = useState<MaterialFormData>({
    codigo: '',
    nome: '',
    descricao: '',
    unidade_medida: '',
    estoque_minimo: 0,
    estoque_maximo: 0,
    preco_medio: 0,
    localizacao: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      if (material) {
        setFormData({
          codigo: material.codigo || '',
          nome: material.nome || '',
          descricao: material.descricao || '',
          unidade_medida: material.unidade_medida || '',
          estoque_minimo: material.estoque_minimo || 0,
          estoque_maximo: material.estoque_maximo || 0,
          preco_medio: material.preco_medio || 0,
          localizacao: material.localizacao || ''
        });
      } else {
        setFormData({
          codigo: '',
          nome: '',
          descricao: '',
          unidade_medida: '',
          estoque_minimo: 0,
          estoque_maximo: 0,
          preco_medio: 0,
          localizacao: ''
        });
      }
      setError('');
    }
  }, [isOpen, material]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const value = e.target.type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const url = material 
        ? `http://localhost:8000/materiais/materiais/${material.id}`
        : 'http://localhost:8000/materiais/materiais';
      
      const method = material ? 'put' : 'post';

      await axios[method](url, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Erro ao salvar material:', err);
      setError(err.response?.data?.detail || 'Erro ao salvar material');
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
            {material ? 'Editar Material' : 'Novo Material'}
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
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Código *
              </label>
              <input
                type="text"
                name="codigo"
                value={formData.codigo}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Código único"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unidade de Medida *
              </label>
              <select
                name="unidade_medida"
                value={formData.unidade_medida}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Selecione...</option>
                <option value="UN">UN - Unidade</option>
                <option value="KG">KG - Quilograma</option>
                <option value="G">G - Grama</option>
                <option value="L">L - Litro</option>
                <option value="ML">ML - Mililitro</option>
                <option value="M">M - Metro</option>
                <option value="CM">CM - Centímetro</option>
                <option value="M2">M² - Metro Quadrado</option>
                <option value="M3">M³ - Metro Cúbico</option>
                <option value="CX">CX - Caixa</option>
                <option value="PC">PC - Peça</option>
                <option value="PAR">PAR - Par</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nome *
              </label>
              <input
                type="text"
                name="nome"
                value={formData.nome}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Nome do material"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descrição
              </label>
              <textarea
                name="descricao"
                value={formData.descricao}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Descrição detalhada"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estoque Mínimo
              </label>
              <input
                type="number"
                name="estoque_minimo"
                value={formData.estoque_minimo}
                onChange={handleChange}
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estoque Máximo
              </label>
              <input
                type="number"
                name="estoque_maximo"
                value={formData.estoque_maximo}
                onChange={handleChange}
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Preço Médio (R$)
              </label>
              <input
                type="number"
                name="preco_medio"
                value={formData.preco_medio}
                onChange={handleChange}
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Localização
              </label>
              <input
                type="text"
                name="localizacao"
                value={formData.localizacao}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: Prateleira A1"
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
