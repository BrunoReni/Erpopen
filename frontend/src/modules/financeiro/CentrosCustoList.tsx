import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, X } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import api from '../../services/api';

interface CentroCusto {
  id: number;
  codigo: string;
  nome: string;
  descricao?: string;
  ativo: number;
}

interface FormData {
  codigo: string;
  nome: string;
  descricao?: string;
}

export function CentrosCustoList() {
  const [centros, setCentros] = useState<CentroCusto[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCentro, setEditingCentro] = useState<CentroCusto | null>(null);
  const [formData, setFormData] = useState<FormData>({
    codigo: '',
    nome: '',
    descricao: ''
  });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchCentros();
  }, []);

  useEffect(() => {
    if (editingCentro) {
      setFormData({
        codigo: editingCentro.codigo,
        nome: editingCentro.nome,
        descricao: editingCentro.descricao || ''
      });
      setShowForm(true);
    } else {
      setFormData({
        codigo: '',
        nome: '',
        descricao: ''
      });
    }
  }, [editingCentro]);

  const fetchCentros = async () => {
    try {
      const response = await api.get('/financeiro/centros-custo');
      setCentros(response.data);
    } catch (error) {
      console.error('Erro ao buscar centros de custo:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingCentro) {
        await api.put(`/financeiro/centros-custo/${editingCentro.id}`, formData);
      } else {
        await api.post('/financeiro/centros-custo', formData);
      }
      fetchCentros();
      handleCloseForm();
    } catch (error: any) {
      console.error('Erro ao salvar centro de custo:', error);
      alert(error.response?.data?.detail || 'Erro ao salvar centro de custo');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Deseja realmente desativar este centro de custo?')) return;
    
    try {
      await api.delete(`/financeiro/centros-custo/${id}`);
      fetchCentros();
    } catch (error) {
      console.error('Erro ao desativar centro de custo:', error);
      alert('Erro ao desativar centro de custo');
    }
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingCentro(null);
    setFormData({
      codigo: '',
      nome: '',
      descricao: ''
    });
  };

  const filteredCentros = centros.filter(centro =>
    centro.codigo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    centro.nome.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Centros de Custo</h1>
            <p className="text-gray-600 mt-1">Gerencie os centros de custo da empresa</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Novo Centro de Custo
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <input
              type="text"
              placeholder="Buscar por código ou nome..."
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
                    Código
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nome
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Descrição
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-4 text-center text-gray-500">
                      Carregando...
                    </td>
                  </tr>
                ) : filteredCentros.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-4 text-center text-gray-500">
                      Nenhum centro de custo encontrado
                    </td>
                  </tr>
                ) : (
                  filteredCentros.map((centro) => (
                    <tr key={centro.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-mono font-medium text-gray-900">
                          {centro.codigo}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">
                          {centro.nome}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {centro.descricao || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setEditingCentro(centro)}
                            className="text-yellow-600 hover:text-yellow-900"
                            title="Editar"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(centro.id)}
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

      {/* Modal de Formulário */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">
                  {editingCentro ? 'Editar Centro de Custo' : 'Novo Centro de Custo'}
                </h2>
                <button
                  onClick={handleCloseForm}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Código *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.codigo}
                    onChange={(e) => setFormData({ ...formData, codigo: e.target.value })}
                    placeholder="Ex: CC001"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nome *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.nome}
                    onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                    placeholder="Ex: Administrativo"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Descrição
                </label>
                <textarea
                  value={formData.descricao}
                  onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                  rows={3}
                  placeholder="Descrição detalhada do centro de custo..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="flex justify-end gap-4 pt-6 border-t">
                <button
                  type="button"
                  onClick={handleCloseForm}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Salvar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </MainLayout>
  );
}
