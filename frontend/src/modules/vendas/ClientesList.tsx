import { useState, useEffect } from 'react';
import { MainLayout } from '../../components/layout/MainLayout';
import { Plus, Search, Edit, Trash2, User } from 'lucide-react';
import axios from 'axios';
import { ClienteForm } from './ClienteForm';

interface Cliente {
  id: number;
  codigo: string;
  nome: string;
  razao_social?: string;
  cpf_cnpj: string;
  tipo_pessoa: string;
  email?: string;
  telefone?: string;
  celular?: string;
  cidade?: string;
  estado?: string;
  tipo_cliente: string;
  limite_credito: number;
  ativo: number;
}

export function ClientesList() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingCliente, setEditingCliente] = useState<Cliente | null>(null);

  useEffect(() => {
    loadClientes();
  }, []);

  const loadClientes = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/vendas/clientes', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setClientes(response.data);
    } catch (error) {
      console.error('Erro ao carregar clientes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (cliente: Cliente) => {
    setEditingCliente(cliente);
    setIsFormOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja desativar este cliente?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(`http://localhost:8000/vendas/clientes/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadClientes();
    } catch (error) {
      console.error('Erro ao desativar cliente:', error);
      alert('Erro ao desativar cliente');
    }
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingCliente(null);
    loadClientes();
  };

  const filteredClientes = clientes.filter(cliente =>
    cliente.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cliente.codigo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cliente.cpf_cnpj.includes(searchTerm) ||
    (cliente.razao_social && cliente.razao_social.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Carregando...</div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Clientes</h1>
            <p className="text-gray-600">Gerencie seus clientes</p>
          </div>
          <button
            onClick={() => setIsFormOpen(true)}
            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
          >
            <Plus size={20} />
            Novo Cliente
          </button>
        </div>

        {/* Search */}
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Buscar por código, nome, razão social ou CPF/CNPJ..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
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
                  CPF/CNPJ
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contato
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cidade/UF
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Limite Crédito
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredClientes.map((cliente) => (
                <tr key={cliente.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <User className="text-green-600 mr-2" size={16} />
                      <span className="text-sm font-mono font-bold text-gray-900">
                        {cliente.codigo}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{cliente.nome}</div>
                    {cliente.razao_social && (
                      <div className="text-sm text-gray-500">{cliente.razao_social}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{cliente.cpf_cnpj}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      cliente.tipo_pessoa === 'PF' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-purple-100 text-purple-800'
                    }`}>
                      {cliente.tipo_pessoa}
                    </span>
                    <div className="text-xs text-gray-500 mt-1">{cliente.tipo_cliente}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{cliente.telefone || cliente.celular || '-'}</div>
                    <div className="text-sm text-gray-500">{cliente.email || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {cliente.cidade && cliente.estado 
                        ? `${cliente.cidade}/${cliente.estado}` 
                        : '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-green-600">
                      R$ {cliente.limite_credito.toFixed(2)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      cliente.ativo 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {cliente.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(cliente)}
                        className="text-blue-600 hover:text-blue-900"
                        title="Editar"
                      >
                        <Edit size={18} />
                      </button>
                      {cliente.ativo === 1 && (
                        <button
                          onClick={() => handleDelete(cliente.id)}
                          className="text-red-600 hover:text-red-900"
                          title="Desativar"
                        >
                          <Trash2 size={18} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredClientes.length === 0 && (
            <div className="text-center py-12">
              <User className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhum cliente encontrado</h3>
              <p className="mt-1 text-sm text-gray-500">
                Comece criando um novo cliente.
              </p>
            </div>
          )}
        </div>

        {/* Total */}
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-600">
            Total de clientes: <span className="font-bold text-gray-900">{filteredClientes.length}</span>
            {searchTerm && ` (filtrado de ${clientes.length})`}
          </div>
        </div>
      </div>

      {/* Form Modal */}
      {isFormOpen && (
        <ClienteForm
          cliente={editingCliente}
          onClose={handleFormClose}
        />
      )}
    </MainLayout>
  );
}
