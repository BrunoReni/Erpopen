import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, TrendingUp, TrendingDown, RefreshCw, ArrowRightLeft } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import { MovimentoEstoqueForm } from './MovimentoEstoqueForm';
import api from '../../services/api';

interface Material {
  id: number;
  codigo: string;
  nome: string;
}

interface MovimentoEstoque {
  id: number;
  material_id: number;
  material?: Material;
  tipo_movimento: string;
  quantidade: number;
  data_movimento: string;
  observacao?: string;
  usuario?: string;
}

export function MovimentosEstoqueList() {
  const [movimentos, setMovimentos] = useState<MovimentoEstoque[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTipo, setFilterTipo] = useState('');

  useEffect(() => {
    fetchMovimentos();
  }, []);

  const fetchMovimentos = async () => {
    try {
      const response = await api.get('/materiais/movimentos');
      setMovimentos(response.data);
    } catch (error) {
      console.error('Erro ao buscar movimentos:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'entrada':
        return <TrendingUp className="w-5 h-5 text-green-600" />;
      case 'saida':
        return <TrendingDown className="w-5 h-5 text-red-600" />;
      case 'ajuste':
        return <RefreshCw className="w-5 h-5 text-blue-600" />;
      case 'transferencia':
        return <ArrowRightLeft className="w-5 h-5 text-purple-600" />;
      default:
        return null;
    }
  };

  const getTipoBadge = (tipo: string) => {
    const config: Record<string, { label: string; className: string }> = {
      entrada: { label: 'Entrada', className: 'bg-green-100 text-green-800' },
      saida: { label: 'Saída', className: 'bg-red-100 text-red-800' },
      ajuste: { label: 'Ajuste', className: 'bg-blue-100 text-blue-800' },
      transferencia: { label: 'Transferência', className: 'bg-purple-100 text-purple-800' },
    };

    const item = config[tipo] || { label: tipo, className: 'bg-gray-100 text-gray-800' };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${item.className}`}>
        {item.label}
      </span>
    );
  };

  const filteredMovimentos = movimentos.filter(mov => {
    const matchesSearch = mov.material?.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mov.material?.codigo.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTipo = !filterTipo || mov.tipo_movimento === filterTipo;
    return matchesSearch && matchesTipo;
  });

  if (showForm) {
    return (
      <MovimentoEstoqueForm
        onClose={() => setShowForm(false)}
        onSave={() => {
          fetchMovimentos();
          setShowForm(false);
        }}
      />
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Movimentação de Estoque</h1>
            <p className="text-gray-600 mt-1">Registre entradas, saídas e ajustes de estoque</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Novo Movimento
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200 space-y-4">
            <input
              type="text"
              placeholder="Buscar por material..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />

            <div className="flex gap-2">
              <button
                onClick={() => setFilterTipo('')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filterTipo === '' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Todos
              </button>
              <button
                onClick={() => setFilterTipo('entrada')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filterTipo === 'entrada' 
                    ? 'bg-green-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Entradas
              </button>
              <button
                onClick={() => setFilterTipo('saida')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filterTipo === 'saida' 
                    ? 'bg-red-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Saídas
              </button>
              <button
                onClick={() => setFilterTipo('ajuste')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filterTipo === 'ajuste' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Ajustes
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data/Hora
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Material
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantidade
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Observação
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                      Carregando...
                    </td>
                  </tr>
                ) : filteredMovimentos.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                      Nenhum movimento encontrado
                    </td>
                  </tr>
                ) : (
                  filteredMovimentos.map((movimento) => (
                    <tr key={movimento.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(movimento.data_movimento).toLocaleString('pt-BR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {movimento.material?.codigo}
                        </div>
                        <div className="text-sm text-gray-500">
                          {movimento.material?.nome}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          {getTipoIcon(movimento.tipo_movimento)}
                          {getTipoBadge(movimento.tipo_movimento)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${
                          movimento.tipo_movimento === 'entrada' ? 'text-green-600' : 
                          movimento.tipo_movimento === 'saida' ? 'text-red-600' : 
                          'text-blue-600'
                        }`}>
                          {movimento.tipo_movimento === 'saida' ? '-' : '+'}{movimento.quantidade}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {movimento.observacao || '-'}
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
