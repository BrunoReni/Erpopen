import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X } from 'lucide-react';

interface LocalEstoque {
  id?: number;
  nome: string;
  tipo: string;
  endereco?: string;
  responsavel?: string;
  telefone?: string;
  padrao?: number;
  ativo?: number;
}

interface Props {
  local: LocalEstoque | null;
  onClose: () => void;
  onSuccess: () => void;
}

const LocalEstoqueForm: React.FC<Props> = ({ local, onClose, onSuccess }) => {
  const [formData, setFormData] = useState<LocalEstoque>({
    nome: '',
    tipo: 'almoxarifado',
    endereco: '',
    responsavel: '',
    telefone: '',
    padrao: 0,
    ativo: 1,
  });
  const [loading, setLoading] = useState(false);

  const API_URL = 'http://localhost:8000';
  const token = localStorage.getItem('token');

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    if (local) {
      setFormData(local);
    }
  }, [local]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.nome.trim()) {
      alert('Nome é obrigatório');
      return;
    }

    try {
      setLoading(true);
      
      if (local?.id) {
        // Atualizar
        await axios.put(
          `${API_URL}/locais/locais/${local.id}`,
          formData,
          axiosConfig
        );
        alert('Local atualizado com sucesso!');
      } else {
        // Criar
        await axios.post(
          `${API_URL}/locais/locais`,
          formData,
          axiosConfig
        );
        alert('Local criado com sucesso!');
      }
      
      onSuccess();
    } catch (error: any) {
      console.error('Erro ao salvar local:', error);
      alert(error.response?.data?.detail || 'Erro ao salvar local');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({
        ...prev,
        [name]: checked ? 1 : 0
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b sticky top-0 bg-white z-10">
          <h2 className="text-2xl font-bold text-gray-900">
            {local ? 'Editar Local de Estoque' : 'Novo Local de Estoque'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Nome e Tipo */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nome do Local *
              </label>
              <input
                type="text"
                name="nome"
                value={formData.nome}
                onChange={handleChange}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: Almoxarifado Central"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Local *
              </label>
              <select
                name="tipo"
                value={formData.tipo}
                onChange={handleChange}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="almoxarifado">Almoxarifado</option>
                <option value="loja">Loja</option>
                <option value="deposito">Depósito</option>
                <option value="fabrica">Fábrica</option>
                <option value="outro">Outro</option>
              </select>
            </div>
          </div>

          {/* Endereço */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Endereço
            </label>
            <input
              type="text"
              name="endereco"
              value={formData.endereco || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: Rua das Flores, 123 - Centro"
            />
          </div>

          {/* Responsável e Telefone */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Responsável
              </label>
              <input
                type="text"
                name="responsavel"
                value={formData.responsavel || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Nome do responsável"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Telefone
              </label>
              <input
                type="text"
                name="telefone"
                value={formData.telefone || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="(00) 0000-0000"
              />
            </div>
          </div>

          {/* Checkboxes */}
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                name="padrao"
                checked={formData.padrao === 1}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-700">
                Definir como local padrão do sistema
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="ativo"
                checked={formData.ativo === 1}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-700">
                Local ativo
              </label>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>Dica:</strong> O local padrão será usado automaticamente nas movimentações de estoque 
              quando nenhum local for especificado. Apenas um local pode ser padrão por vez.
            </p>
          </div>

          {/* Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LocalEstoqueForm;
