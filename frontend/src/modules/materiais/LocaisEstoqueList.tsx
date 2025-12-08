import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit, XCircle, Warehouse, Star, MapPin, BarChart3, TrendingUp } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import LocalEstoqueForm from './LocalEstoqueForm';

interface LocalEstoque {
  id: number;
  codigo: string;
  nome: string;
  tipo: string;
  endereco?: string;
  responsavel?: string;
  telefone?: string;
  padrao: number;
  ativo: number;
}

interface Estatisticas {
  total_itens: number;
  itens_com_estoque: number;
  itens_zerados: number;
  itens_criticos: number;
}

const LocaisEstoqueList: React.FC = () => {
  const [locais, setLocais] = useState<LocalEstoque[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingLocal, setEditingLocal] = useState<LocalEstoque | null>(null);
  const [loading, setLoading] = useState(false);
  const [filtroTipo, setFiltroTipo] = useState<string>('');
  const [filtroAtivo, setFiltroAtivo] = useState<string>('');
  const [estatisticas, setEstatisticas] = useState<Record<number, Estatisticas>>({});

  const API_URL = 'http://localhost:8000';
  const token = localStorage.getItem('token');

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    loadLocais();
  }, [filtroTipo, filtroAtivo]);

  const loadLocais = async () => {
    try {
      setLoading(true);
      let url = `${API_URL}/locais/locais?limit=100`;
      
      if (filtroTipo) url += `&tipo=${filtroTipo}`;
      if (filtroAtivo !== '') url += `&ativo=${filtroAtivo}`;
      
      const response = await axios.get(url, axiosConfig);
      setLocais(response.data);
      
      // Carregar estatísticas de cada local
      response.data.forEach(async (local: LocalEstoque) => {
        try {
          const statsResponse = await axios.get(
            `${API_URL}/locais/locais/${local.id}/estatisticas`,
            axiosConfig
          );
          setEstatisticas(prev => ({
            ...prev,
            [local.id]: statsResponse.data.estatisticas
          }));
        } catch (error) {
          console.error(`Erro ao carregar estatísticas do local ${local.id}:`, error);
        }
      });
    } catch (error) {
      console.error('Erro ao carregar locais:', error);
      alert('Erro ao carregar locais de estoque');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingLocal(null);
    setShowForm(true);
  };

  const handleEdit = (local: LocalEstoque) => {
    setEditingLocal(local);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Deseja realmente desativar este local de estoque?')) return;

    try {
      await axios.delete(`${API_URL}/locais/locais/${id}`, axiosConfig);
      alert('Local desativado com sucesso!');
      loadLocais();
    } catch (error: any) {
      console.error('Erro ao desativar local:', error);
      alert(error.response?.data?.detail || 'Erro ao desativar local');
    }
  };

  const handleDefinirPadrao = async (id: number) => {
    if (!window.confirm('Deseja definir este local como padrão do sistema?')) return;

    try {
      await axios.post(`${API_URL}/locais/locais/definir-padrao/${id}`, {}, axiosConfig);
      alert('Local definido como padrão!');
      loadLocais();
    } catch (error: any) {
      console.error('Erro ao definir local padrão:', error);
      alert(error.response?.data?.detail || 'Erro ao definir local padrão');
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setEditingLocal(null);
    loadLocais();
  };

  const getTipoLabel = (tipo: string) => {
    const tipos: Record<string, string> = {
      almoxarifado: 'Almoxarifado',
      loja: 'Loja',
      deposito: 'Depósito',
      fabrica: 'Fábrica',
      outro: 'Outro'
    };
    return tipos[tipo] || tipo;
  };

  const getTipoBadgeColor = (tipo: string) => {
    const colors: Record<string, string> = {
      almoxarifado: 'bg-blue-100 text-blue-800',
      loja: 'bg-green-100 text-green-800',
      deposito: 'bg-yellow-100 text-yellow-800',
      fabrica: 'bg-purple-100 text-purple-800',
      outro: 'bg-gray-100 text-gray-800'
    };
    return colors[tipo] || 'bg-gray-100 text-gray-800';
  };

  // Cards de resumo
  const totalLocais = locais.length;
  const locaisAtivos = locais.filter(l => l.ativo === 1).length;
  const locaisInativos = locais.filter(l => l.ativo === 0).length;
  const localPadrao = locais.find(l => l.padrao === 1);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Locais de Estoque</h1>
            <p className="text-gray-600 mt-1">Gerenciamento de armazéns e depósitos</p>
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Novo Local
          </button>
        </div>

        {/* Cards de Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total de Locais</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{totalLocais}</p>
              </div>
              <Warehouse className="w-12 h-12 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Locais Ativos</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{locaisAtivos}</p>
              </div>
              <TrendingUp className="w-12 h-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Locais Inativos</p>
                <p className="text-3xl font-bold text-gray-400 mt-1">{locaisInativos}</p>
              </div>
              <XCircle className="w-12 h-12 text-gray-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Local Padrão</p>
                <p className="text-lg font-bold text-yellow-600 mt-1 truncate">
                  {localPadrao?.nome || 'Não definido'}
                </p>
              </div>
              <Star className="w-12 h-12 text-yellow-500" />
            </div>
          </div>
        </div>

        {/* Filtros */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Local
              </label>
              <select
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos os tipos</option>
                <option value="almoxarifado">Almoxarifado</option>
                <option value="loja">Loja</option>
                <option value="deposito">Depósito</option>
                <option value="fabrica">Fábrica</option>
                <option value="outro">Outro</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={filtroAtivo}
                onChange={(e) => setFiltroAtivo(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos</option>
                <option value="1">Ativos</option>
                <option value="0">Inativos</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tabela */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Carregando...</div>
          ) : locais.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Warehouse className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p>Nenhum local de estoque cadastrado</p>
              <button
                onClick={handleCreate}
                className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
              >
                Cadastrar primeiro local
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Código
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nome
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tipo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Endereço
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estatísticas
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {locais.map((local) => (
                    <tr key={local.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {local.padrao === 1 && (
                            <Star className="w-4 h-4 text-yellow-500 mr-2 fill-current" />
                          )}
                          <span className="text-sm font-medium text-gray-900">
                            {local.codigo}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{local.nome}</div>
                        {local.responsavel && (
                          <div className="text-sm text-gray-500">Resp: {local.responsavel}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getTipoBadgeColor(local.tipo)}`}>
                          {getTipoLabel(local.tipo)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 flex items-start">
                          {local.endereco && (
                            <>
                              <MapPin className="w-4 h-4 mr-1 mt-0.5 text-gray-400 flex-shrink-0" />
                              <span className="line-clamp-2">{local.endereco}</span>
                            </>
                          )}
                          {!local.endereco && (
                            <span className="text-gray-400">-</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {estatisticas[local.id] ? (
                          <div className="text-xs space-y-1">
                            <div className="flex items-center">
                              <BarChart3 className="w-3 h-3 mr-1 text-blue-500" />
                              <span className="text-gray-600">
                                {estatisticas[local.id].itens_com_estoque} itens
                              </span>
                            </div>
                            {estatisticas[local.id].itens_criticos > 0 && (
                              <div className="flex items-center text-red-600">
                                <span className="font-semibold">
                                  {estatisticas[local.id].itens_criticos} críticos
                                </span>
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-xs text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col space-y-1">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full inline-block ${
                            local.ativo === 1 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {local.ativo === 1 ? 'Ativo' : 'Inativo'}
                          </span>
                          {local.padrao === 1 && (
                            <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 inline-block">
                              Padrão
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                        <button
                          onClick={() => handleEdit(local)}
                          className="text-blue-600 hover:text-blue-900"
                          title="Editar"
                        >
                          <Edit className="w-4 h-4 inline" />
                        </button>
                        
                        {local.padrao === 0 && local.ativo === 1 && (
                          <button
                            onClick={() => handleDefinirPadrao(local.id)}
                            className="text-yellow-600 hover:text-yellow-900"
                            title="Definir como padrão"
                          >
                            <Star className="w-4 h-4 inline" />
                          </button>
                        )}
                        
                        {local.padrao === 0 && (
                          <button
                            onClick={() => handleDelete(local.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Desativar"
                          >
                            <XCircle className="w-4 h-4 inline" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Formulário */}
      {showForm && (
        <LocalEstoqueForm
          local={editingLocal}
          onClose={() => {
            setShowForm(false);
            setEditingLocal(null);
          }}
          onSuccess={handleFormSuccess}
        />
      )}
    </MainLayout>
  );
};

export default LocaisEstoqueList;
