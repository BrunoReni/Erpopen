import { useState, useEffect } from 'react';
import { MainLayout } from '../../components/layout/MainLayout';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Trash2, Save } from 'lucide-react';
import axios from 'axios';

interface Material {
  id: number;
  codigo: string;
  nome: string;
  preco_venda: number;
  estoque_atual: number;
  unidade_medida: string;
}

interface Cliente {
  id: number;
  codigo: string;
  nome: string;
}

interface ItemForm {
  material_id: number;
  quantidade: number;
  preco_unitario: number;
  percentual_desconto: number;
  observacao: string;
}

interface PedidoForm {
  cliente_id: number;
  vendedor_id?: number;
  data_entrega_prevista: string;
  condicao_pagamento: string;
  valor_frete: number;
  observacoes: string;
  itens: ItemForm[];
}

export function PedidoVendaForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;
  
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [materiais, setMateriais] = useState<Material[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState<PedidoForm>({
    cliente_id: 0,
    data_entrega_prevista: '',
    condicao_pagamento: 'a_vista',
    valor_frete: 0,
    observacoes: '',
    itens: []
  });

  const [novoItem, setNovoItem] = useState<ItemForm>({
    material_id: 0,
    quantidade: 1,
    preco_unitario: 0,
    percentual_desconto: 0,
    observacao: ''
  });

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      // Carregar clientes
      const clientesResponse = await axios.get(
        'http://localhost:8000/vendas/clientes?ativo=1',
        { headers }
      );
      setClientes(clientesResponse.data);

      // Carregar materiais
      const materiaisResponse = await axios.get(
        'http://localhost:8000/materiais?ativo=1',
        { headers }
      );
      setMateriais(materiaisResponse.data);

      // Se for edição, carregar pedido
      if (id) {
        const pedidoResponse = await axios.get(
          `http://localhost:8000/vendas/pedidos/${id}`,
          { headers }
        );
        const pedido = pedidoResponse.data;
        
        setFormData({
          cliente_id: pedido.cliente_id,
          vendedor_id: pedido.vendedor_id,
          data_entrega_prevista: pedido.data_entrega_prevista ? 
            new Date(pedido.data_entrega_prevista).toISOString().split('T')[0] : '',
          condicao_pagamento: pedido.condicao_pagamento || 'a_vista',
          valor_frete: pedido.valor_frete,
          observacoes: pedido.observacoes || '',
          itens: pedido.itens.map((item: any) => ({
            material_id: item.material_id,
            quantidade: item.quantidade,
            preco_unitario: item.preco_unitario,
            percentual_desconto: item.percentual_desconto,
            observacao: item.observacao || ''
          }))
        });
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      alert('Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const handleMaterialChange = (materialId: number) => {
    const material = materiais.find(m => m.id === materialId);
    if (material) {
      setNovoItem({
        ...novoItem,
        material_id: materialId,
        preco_unitario: material.preco_venda || 0
      });
    }
  };

  const adicionarItem = () => {
    if (novoItem.material_id === 0) {
      alert('Selecione um material');
      return;
    }
    if (novoItem.quantidade <= 0) {
      alert('Quantidade deve ser maior que zero');
      return;
    }
    if (novoItem.preco_unitario <= 0) {
      alert('Preço unitário deve ser maior que zero');
      return;
    }

    setFormData({
      ...formData,
      itens: [...formData.itens, { ...novoItem }]
    });

    // Resetar formulário de item
    setNovoItem({
      material_id: 0,
      quantidade: 1,
      preco_unitario: 0,
      percentual_desconto: 0,
      observacao: ''
    });
  };

  const removerItem = (index: number) => {
    setFormData({
      ...formData,
      itens: formData.itens.filter((_, i) => i !== index)
    });
  };

  const calcularSubtotal = (item: ItemForm) => {
    const valorBruto = item.quantidade * item.preco_unitario;
    const valorDesconto = valorBruto * (item.percentual_desconto / 100);
    return valorBruto - valorDesconto;
  };

  const calcularTotais = () => {
    const valorProdutos = formData.itens.reduce((sum, item) => {
      return sum + (item.quantidade * item.preco_unitario);
    }, 0);

    const valorDesconto = formData.itens.reduce((sum, item) => {
      const valorBruto = item.quantidade * item.preco_unitario;
      return sum + (valorBruto * (item.percentual_desconto / 100));
    }, 0);

    const valorTotal = valorProdutos - valorDesconto + formData.valor_frete;

    return { valorProdutos, valorDesconto, valorTotal };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.cliente_id === 0) {
      alert('Selecione um cliente');
      return;
    }

    if (formData.itens.length === 0) {
      alert('Adicione pelo menos um item ao pedido');
      return;
    }

    try {
      setSaving(true);
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      const payload = {
        ...formData,
        data_entrega_prevista: formData.data_entrega_prevista || null
      };

      if (isEdit) {
        await axios.put(
          `http://localhost:8000/vendas/pedidos/${id}`,
          payload,
          { headers }
        );
        alert('Pedido atualizado com sucesso!');
      } else {
        await axios.post(
          'http://localhost:8000/vendas/pedidos',
          payload,
          { headers }
        );
        alert('Pedido criado com sucesso!');
      }

      navigate('/vendas/pedidos');
    } catch (error: any) {
      console.error('Erro ao salvar pedido:', error);
      alert(error.response?.data?.detail || 'Erro ao salvar pedido');
    } finally {
      setSaving(false);
    }
  };

  const getMaterialNome = (materialId: number) => {
    const material = materiais.find(m => m.id === materialId);
    return material ? `${material.codigo} - ${material.nome}` : 'N/A';
  };

  const getMaterialEstoque = (materialId: number) => {
    const material = materiais.find(m => m.id === materialId);
    return material ? material.estoque_atual : 0;
  };

  const totais = calcularTotais();

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
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/vendas/pedidos')}
              className="text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft size={24} />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {isEdit ? 'Editar Pedido de Venda' : 'Novo Pedido de Venda'}
              </h1>
              <p className="text-gray-600 mt-1">
                Preencha os dados do pedido e adicione os itens
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dados do Pedido */}
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Dados do Pedido</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cliente *
                </label>
                <select
                  value={formData.cliente_id}
                  onChange={(e) => setFormData({ ...formData, cliente_id: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border rounded-lg"
                  required
                >
                  <option value={0}>Selecione um cliente</option>
                  {clientes.map(cliente => (
                    <option key={cliente.id} value={cliente.id}>
                      {cliente.codigo} - {cliente.nome}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data de Entrega Prevista
                </label>
                <input
                  type="date"
                  value={formData.data_entrega_prevista}
                  onChange={(e) => setFormData({ ...formData, data_entrega_prevista: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Condição de Pagamento *
                </label>
                <select
                  value={formData.condicao_pagamento}
                  onChange={(e) => setFormData({ ...formData, condicao_pagamento: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  required
                >
                  <option value="a_vista">À Vista</option>
                  <option value="30_dias">30 dias</option>
                  <option value="30_60_dias">30/60 dias</option>
                  <option value="30_60_90_dias">30/60/90 dias</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Valor do Frete (R$)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.valor_frete}
                  onChange={(e) => setFormData({ ...formData, valor_frete: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Observações
              </label>
              <textarea
                value={formData.observacoes}
                onChange={(e) => setFormData({ ...formData, observacoes: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="Observações gerais do pedido..."
              />
            </div>
          </div>

          {/* Adicionar Itens */}
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Adicionar Item</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Material *
                </label>
                <select
                  value={novoItem.material_id}
                  onChange={(e) => handleMaterialChange(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value={0}>Selecione...</option>
                  {materiais.map(material => (
                    <option key={material.id} value={material.id}>
                      {material.codigo} - {material.nome} (Est: {material.estoque_atual})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantidade *
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={novoItem.quantidade}
                  onChange={(e) => setNovoItem({ ...novoItem, quantidade: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Preço Unit. (R$) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={novoItem.preco_unitario}
                  onChange={(e) => setNovoItem({ ...novoItem, preco_unitario: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Desconto (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={novoItem.percentual_desconto}
                  onChange={(e) => setNovoItem({ ...novoItem, percentual_desconto: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div className="flex items-end">
                <button
                  type="button"
                  onClick={adicionarItem}
                  className="w-full flex items-center justify-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                >
                  <Plus size={20} />
                  Adicionar
                </button>
              </div>
            </div>
          </div>

          {/* Lista de Itens */}
          {formData.itens.length > 0 && (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">Itens do Pedido</h2>
              </div>
              
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Material
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Quantidade
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Preço Unit.
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Desconto
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Subtotal
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {formData.itens.map((item, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {getMaterialNome(item.material_id)}
                        </div>
                        <div className="text-xs text-gray-500">
                          Estoque: {getMaterialEstoque(item.material_id)}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right text-sm text-gray-900">
                        {item.quantidade}
                      </td>
                      <td className="px-6 py-4 text-right text-sm text-gray-900">
                        R$ {item.preco_unitario.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-right text-sm text-gray-900">
                        {item.percentual_desconto}%
                      </td>
                      <td className="px-6 py-4 text-right text-sm font-medium text-gray-900">
                        R$ {calcularSubtotal(item).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          type="button"
                          onClick={() => removerItem(index)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 size={18} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Resumo */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Resumo do Pedido</h2>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Subtotal Produtos:</span>
                <span className="font-medium">R$ {totais.valorProdutos.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">(-) Descontos:</span>
                <span className="font-medium text-red-600">R$ {totais.valorDesconto.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">(+) Frete:</span>
                <span className="font-medium">R$ {formData.valor_frete.toFixed(2)}</span>
              </div>
              <div className="border-t pt-2 flex justify-between text-lg font-bold">
                <span>Total:</span>
                <span className="text-green-600">R$ {totais.valorTotal.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Ações */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => navigate('/vendas/pedidos')}
              className="px-6 py-2 border rounded-lg hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              <Save size={20} />
              {saving ? 'Salvando...' : 'Salvar Pedido'}
            </button>
          </div>
        </form>
      </div>
    </MainLayout>
  );
}
