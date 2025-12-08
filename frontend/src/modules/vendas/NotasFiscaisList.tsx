import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit, XCircle, FileText, CheckCircle, Send, Eye } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import NotaFiscalForm from './NotaFiscalForm';

interface NotaFiscal {
  id: number;
  numero: string;
  serie: string;
  tipo: string;
  data_emissao: string;
  cliente_id?: number;
  fornecedor_id?: number;
  valor_produtos: number;
  valor_total: number;
  status: string;
  natureza_operacao: string;
}

const NotasFiscaisList: React.FC = () => {
  const [notas, setNotas] = useState<NotaFiscal[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingNota, setEditingNota] = useState<NotaFiscal | null>(null);
  const [loading, setLoading] = useState(false);
  const [filtroStatus, setFiltroStatus] = useState<string>('');
  const [filtroTipo, setFiltroTipo] = useState<string>('');

  const API_URL = 'http://localhost:8000';
  const token = localStorage.getItem('token');

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    loadNotas();
  }, [filtroStatus, filtroTipo]);

  const loadNotas = async () => {
    try {
      setLoading(true);
      let url = `${API_URL}/faturamento/notas-fiscais?limit=100`;
      
      if (filtroStatus) url += `&status=${filtroStatus}`;
      if (filtroTipo) url += `&tipo=${filtroTipo}`;
      
      const response = await axios.get(url, axiosConfig);
      setNotas(response.data);
    } catch (error) {
      console.error('Erro ao carregar notas fiscais:', error);
      alert('Erro ao carregar notas fiscais');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingNota(null);
    setShowForm(true);
  };

  const handleEdit = (nota: NotaFiscal) => {
    setEditingNota(nota);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Deseja realmente cancelar/excluir esta nota fiscal?')) return;

    try {
      await axios.delete(`${API_URL}/faturamento/notas-fiscais/${id}`, axiosConfig);
      alert('Nota fiscal cancelada/excluída com sucesso!');
      loadNotas();
    } catch (error: any) {
      console.error('Erro ao cancelar nota:', error);
      alert(error.response?.data?.detail || 'Erro ao cancelar nota fiscal');
    }
  };

  const handleEmitir = async (id: number) => {
    if (!window.confirm('Deseja emitir esta nota fiscal? O estoque será baixado automaticamente.')) return;

    try {
      const response = await axios.post(
        `${API_URL}/faturamento/notas-fiscais/${id}/emitir?baixar_estoque=true`,
        {},
        axiosConfig
      );
      alert(response.data.message);
      loadNotas();
    } catch (error: any) {
      console.error('Erro ao emitir nota:', error);
      alert(error.response?.data?.detail || 'Erro ao emitir nota fiscal');
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setEditingNota(null);
    loadNotas();
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      rascunho: 'Rascunho',
      emitida: 'Emitida',
      autorizada: 'Autorizada',
      cancelada: 'Cancelada',
      denegada: 'Denegada'
    };
    return labels[status] || status;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      rascunho: 'bg-gray-100 text-gray-800',
      emitida: 'bg-blue-100 text-blue-800',
      autorizada: 'bg-green-100 text-green-800',
      cancelada: 'bg-red-100 text-red-800',
      denegada: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getTipoLabel = (tipo: string) => {
    const labels: Record<string, string> = {
      saida: 'Saída (Venda)',
      entrada: 'Entrada (Compra)',
      devolucao: 'Devolução'
    };
    return labels[tipo] || tipo;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  // Cards de resumo
  const totalNotas = notas.length;
  const notasEmitidas = notas.filter(n => n.status === 'emitida').length;
  const notasAutorizadas = notas.filter(n => n.status === 'autorizada').length;
  const valorTotal = notas
    .filter(n => n.status !== 'cancelada')
    .reduce((sum, n) => sum + n.valor_total, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Notas Fiscais</h1>
            <p className="text-gray-600 mt-1">Gestão de faturamento e documentos fiscais</p>
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Nova Nota Fiscal
          </button>
        </div>

        {/* Cards de Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total de Notas</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{totalNotas}</p>
              </div>
              <FileText className="w-12 h-12 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Emitidas</p>
                <p className="text-3xl font-bold text-blue-600 mt-1">{notasEmitidas}</p>
              </div>
              <Send className="w-12 h-12 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Autorizadas</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{notasAutorizadas}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Valor Total</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatCurrency(valorTotal)}
                </p>
              </div>
              <FileText className="w-12 h-12 text-green-500" />
            </div>
          </div>
        </div>

        {/* Filtros */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={filtroStatus}
                onChange={(e) => setFiltroStatus(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos os status</option>
                <option value="rascunho">Rascunho</option>
                <option value="emitida">Emitida</option>
                <option value="autorizada">Autorizada</option>
                <option value="cancelada">Cancelada</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo
              </label>
              <select
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos os tipos</option>
                <option value="saida">Saída (Venda)</option>
                <option value="entrada">Entrada (Compra)</option>
                <option value="devolucao">Devolução</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tabela */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Carregando...</div>
          ) : notas.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p>Nenhuma nota fiscal cadastrada</p>
              <button
                onClick={handleCreate}
                className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
              >
                Cadastrar primeira nota fiscal
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Número
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Data
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tipo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Natureza
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Valor
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
                  {notas.map((nota) => (
                    <tr key={nota.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <FileText className="w-4 h-4 mr-2 text-blue-500" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {nota.numero}
                            </div>
                            <div className="text-xs text-gray-500">Série: {nota.serie}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(nota.data_emissao)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {getTipoLabel(nota.tipo)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-gray-900">{nota.natureza_operacao}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-semibold text-gray-900">
                          {formatCurrency(nota.valor_total)}
                        </div>
                        <div className="text-xs text-gray-500">
                          Produtos: {formatCurrency(nota.valor_produtos)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(nota.status)}`}>
                          {getStatusLabel(nota.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                        {nota.status === 'rascunho' && (
                          <>
                            <button
                              onClick={() => handleEdit(nota)}
                              className="text-blue-600 hover:text-blue-900"
                              title="Editar"
                            >
                              <Edit className="w-4 h-4 inline" />
                            </button>
                            
                            <button
                              onClick={() => handleEmitir(nota.id)}
                              className="text-green-600 hover:text-green-900"
                              title="Emitir NF"
                            >
                              <Send className="w-4 h-4 inline" />
                            </button>
                            
                            <button
                              onClick={() => handleDelete(nota.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Excluir"
                            >
                              <XCircle className="w-4 h-4 inline" />
                            </button>
                          </>
                        )}
                        
                        {nota.status !== 'rascunho' && (
                          <>
                            <button
                              onClick={() => handleEdit(nota)}
                              className="text-blue-600 hover:text-blue-900"
                              title="Visualizar"
                            >
                              <Eye className="w-4 h-4 inline" />
                            </button>
                            
                            {nota.status === 'emitida' && (
                              <button
                                onClick={() => handleDelete(nota.id)}
                                className="text-red-600 hover:text-red-900"
                                title="Cancelar"
                              >
                                <XCircle className="w-4 h-4 inline" />
                              </button>
                            )}
                          </>
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
        <NotaFiscalForm
          nota={editingNota}
          onClose={() => {
            setShowForm(false);
            setEditingNota(null);
          }}
          onSuccess={handleFormSuccess}
        />
      )}
    </MainLayout>
  );
};

export default NotasFiscaisList;
