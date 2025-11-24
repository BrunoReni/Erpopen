import { useState, useEffect } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import api from '../../services/api';

interface ItemPedido {
  material_id?: number;
  descricao: string;
  quantidade: number;
  unidade_medida: string;
  preco_unitario: number;
}

interface PedidoCompra {
  id?: number;
  fornecedor_id: number;
  data_entrega_prevista: string;
  observacoes?: string;
  itens: ItemPedido[];
}

interface Fornecedor {
  id: number;
  nome: string;
}

interface Material {
  id: number;
  codigo: string;
  nome: string;
  unidade_medida: string;
}

interface PedidoCompraFormProps {
  pedido: any | null;
  onClose: () => void;
  onSave: () => void;
}

export function PedidoCompraForm({ pedido, onClose, onSave }: PedidoCompraFormProps) {
  const [formData, setFormData] = useState<PedidoCompra>({
    fornecedor_id: 0,
    data_entrega_prevista: '',
    observacoes: '',
    itens: []
  });
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
  const [materiais, setMateriais] = useState<Material[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchFornecedores();
    fetchMateriais();

    if (pedido) {
      setFormData({
        fornecedor_id: pedido.fornecedor_id,
        data_entrega_prevista: pedido.data_entrega_prevista?.split('T')[0] || '',
        observacoes: pedido.observacoes || '',
        itens: pedido.itens || []
      });
    }
  }, [pedido]);

  const fetchFornecedores = async () => {
    try {
      const response = await api.get('/compras/fornecedores');
      setFornecedores(response.data);
    } catch (error) {
      console.error('Erro ao buscar fornecedores:', error);
    }
  };

  const fetchMateriais = async () => {
    try {
      const response = await api.get('/materiais/produtos');
      setMateriais(response.data);
    } catch (error) {
      console.error('Erro ao buscar materiais:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.itens.length === 0) {
      alert('Adicione pelo menos um item ao pedido');
      return;
    }

    setLoading(true);
    try {
      if (pedido?.id) {
        await api.put(`/compras/pedidos/${pedido.id}`, formData);
      } else {
        await api.post('/compras/pedidos', formData);
      }
      onSave();
    } catch (error: any) {
      console.error('Erro ao salvar pedido:', error);
      alert(error.response?.data?.detail || 'Erro ao salvar pedido');
    } finally {
      setLoading(false);
    }
  };

  const addItem = () => {
    setFormData({
      ...formData,
      itens: [
        ...formData.itens,
        {
          descricao: '',
          quantidade: 1,
          unidade_medida: 'UN',
          preco_unitario: 0
        }
      ]
    });
  };

  const removeItem = (index: number) => {
    setFormData({
      ...formData,
      itens: formData.itens.filter((_, i) => i !== index)
    });
  };

  const updateItem = (index: number, field: keyof ItemPedido, value: any) => {
    const newItens = [...formData.itens];
    newItens[index] = { ...newItens[index], [field]: value };
    setFormData({ ...formData, itens: newItens });
  };

  const selectMaterial = (index: number, materialId: number) => {
    const material = materiais.find(m => m.id === materialId);
    if (material) {
      updateItem(index, 'material_id', material.id);
      updateItem(index, 'descricao', material.nome);
      updateItem(index, 'unidade_medida', material.unidade_medida);
    }
  };

  const calcularTotal = () => {
    return formData.itens.reduce(
      (total, item) => total + (item.quantidade * item.preco_unitario),
      0
    );
  };

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">
                {pedido ? 'Editar Pedido' : 'Novo Pedido de Compra'}
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
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fornecedor *
                </label>
                <select
                  required
                  value={formData.fornecedor_id}
                  onChange={(e) => setFormData({ ...formData, fornecedor_id: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Selecione...</option>
                  {fornecedores.map((fornecedor) => (
                    <option key={fornecedor.id} value={fornecedor.id}>
                      {fornecedor.nome}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data de Entrega Prevista *
                </label>
                <input
                  type="date"
                  required
                  value={formData.data_entrega_prevista}
                  onChange={(e) => setFormData({ ...formData, data_entrega_prevista: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Observações
              </label>
              <textarea
                value={formData.observacoes}
                onChange={(e) => setFormData({ ...formData, observacoes: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Itens do Pedido</h3>
                <button
                  type="button"
                  onClick={addItem}
                  className="flex items-center gap-2 px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  <Plus className="w-4 h-4" />
                  Adicionar Item
                </button>
              </div>

              <div className="space-y-4">
                {formData.itens.map((item, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                      <div className="md:col-span-4">
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Material (opcional)
                        </label>
                        <select
                          value={item.material_id || ''}
                          onChange={(e) => selectMaterial(index, parseInt(e.target.value))}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Selecione ou digite abaixo...</option>
                          {materiais.map((material) => (
                            <option key={material.id} value={material.id}>
                              {material.codigo} - {material.nome}
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
                          required
                          value={item.descricao}
                          onChange={(e) => updateItem(index, 'descricao', e.target.value)}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div className="md:col-span-1">
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Qtd *
                        </label>
                        <input
                          type="number"
                          required
                          min="0.01"
                          step="0.01"
                          value={item.quantidade}
                          onChange={(e) => updateItem(index, 'quantidade', parseFloat(e.target.value))}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div className="md:col-span-1">
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Un *
                        </label>
                        <input
                          type="text"
                          required
                          value={item.unidade_medida}
                          onChange={(e) => updateItem(index, 'unidade_medida', e.target.value)}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div className="md:col-span-1">
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Preço Unit. *
                        </label>
                        <input
                          type="number"
                          required
                          min="0"
                          step="0.01"
                          value={item.preco_unitario}
                          onChange={(e) => updateItem(index, 'preco_unitario', parseFloat(e.target.value))}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div className="md:col-span-1 flex items-end">
                        <button
                          type="button"
                          onClick={() => removeItem(index)}
                          className="w-full px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                          title="Remover item"
                        >
                          <Trash2 className="w-4 h-4 mx-auto" />
                        </button>
                      </div>
                    </div>

                    <div className="mt-2 text-right text-sm text-gray-600">
                      Subtotal: {new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                      }).format(item.quantidade * item.preco_unitario)}
                    </div>
                  </div>
                ))}
              </div>

              {formData.itens.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  Nenhum item adicionado. Clique em "Adicionar Item" para começar.
                </div>
              )}
            </div>

            {formData.itens.length > 0 && (
              <div className="border-t pt-4">
                <div className="flex justify-end">
                  <div className="text-right">
                    <div className="text-sm text-gray-600">Total do Pedido</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                      }).format(calcularTotal())}
                    </div>
                  </div>
                </div>
              </div>
            )}

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
                {loading ? 'Salvando...' : 'Salvar Pedido'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}
