import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Plus, Trash2 } from 'lucide-react';

interface NotaFiscal {
  id?: number;
  numero?: string;
  serie: string;
  tipo: string;
  cliente_id?: number;
  fornecedor_id?: number;
  natureza_operacao: string;
  cfop?: string;
  valor_frete: number;
  valor_seguro: number;
  valor_desconto: number;
  observacao?: string;
}

interface ItemNF {
  material_id?: number;
  codigo_produto?: string;
  descricao: string;
  ncm?: string;
  unidade: string;
  quantidade: number;
  valor_unitario: number;
  valor_desconto: number;
  aliquota_icms: number;
  cfop?: string;
}

interface Cliente {
  id: number;
  codigo: string;
  nome: string;
}

interface Material {
  id: number;
  codigo: string;
  nome: string;
  unidade_medida: string;
  preco_venda: number;
}

interface Props {
  nota: NotaFiscal | null;
  onClose: () => void;
  onSuccess: () => void;
}

const NotaFiscalForm: React.FC<Props> = ({ nota, onClose, onSuccess }) => {
  const [formData, setFormData] = useState<NotaFiscal>({
    serie: '1',
    tipo: 'saida',
    natureza_operacao: 'Venda de mercadoria',
    cfop: '5102',
    valor_frete: 0,
    valor_seguro: 0,
    valor_desconto: 0,
  });
  
  const [itens, setItens] = useState<ItemNF[]>([{
    descricao: '',
    unidade: 'UN',
    quantidade: 1,
    valor_unitario: 0,
    valor_desconto: 0,
    aliquota_icms: 0,
    cfop: '5102'
  }]);
  
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [materiais, setMateriais] = useState<Material[]>([]);
  const [loading, setLoading] = useState(false);

  const API_URL = 'http://localhost:8000';
  const token = localStorage.getItem('token');

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    loadClientes();
    loadMateriais();
    
    if (nota) {
      setFormData(nota);
      // Carregar itens se for edição
      loadNotaItens(nota.id!);
    }
  }, [nota]);

  const loadClientes = async () => {
    try {
      const response = await axios.get(`${API_URL}/vendas/clientes`, axiosConfig);
      setClientes(response.data);
    } catch (error) {
      console.error('Erro ao carregar clientes:', error);
    }
  };

  const loadMateriais = async () => {
    try {
      const response = await axios.get(`${API_URL}/materiais/produtos`, axiosConfig);
      setMateriais(response.data);
    } catch (error) {
      console.error('Erro ao carregar materiais:', error);
    }
  };

  const loadNotaItens = async (notaId: number) => {
    try {
      const response = await axios.get(
        `${API_URL}/faturamento/notas-fiscais/${notaId}`,
        axiosConfig
      );
      if (response.data.itens && response.data.itens.length > 0) {
        setItens(response.data.itens);
      }
    } catch (error) {
      console.error('Erro ao carregar itens da nota:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.cliente_id && formData.tipo === 'saida') {
      alert('Cliente é obrigatório para NF de saída');
      return;
    }
    
    if (itens.length === 0) {
      alert('Adicione pelo menos um item à nota fiscal');
      return;
    }

    // Validar itens
    for (const item of itens) {
      if (!item.descricao || item.quantidade <= 0 || item.valor_unitario <= 0) {
        alert('Preencha todos os campos obrigatórios dos itens');
        return;
      }
    }

    try {
      setLoading(true);
      
      const payload = {
        ...formData,
        itens: itens
      };
      
      if (nota?.id) {
        // Atualizar (apenas cabeçalho, itens não podem ser alterados em NF emitida)
        await axios.put(
          `${API_URL}/faturamento/notas-fiscais/${nota.id}`,
          formData,
          axiosConfig
        );
        alert('Nota fiscal atualizada com sucesso!');
      } else {
        // Criar
        await axios.post(
          `${API_URL}/faturamento/notas-fiscais`,
          payload,
          axiosConfig
        );
        alert('Nota fiscal criada com sucesso!');
      }
      
      onSuccess();
    } catch (error: any) {
      console.error('Erro ao salvar nota fiscal:', error);
      alert(error.response?.data?.detail || 'Erro ao salvar nota fiscal');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name.includes('valor') || name.includes('id') ? parseFloat(value) || 0 : value
    }));
  };

  const handleItemChange = (index: number, field: string, value: any) => {
    const newItens = [...itens];
    newItens[index] = {
      ...newItens[index],
      [field]: value
    };
    setItens(newItens);
  };

  const handleMaterialSelect = (index: number, materialId: number) => {
    const material = materiais.find(m => m.id === materialId);
    if (material) {
      const newItens = [...itens];
      newItens[index] = {
        ...newItens[index],
        material_id: material.id,
        codigo_produto: material.codigo,
        descricao: material.nome,
        unidade: material.unidade_medida,
        valor_unitario: material.preco_venda || 0
      };
      setItens(newItens);
    }
  };

  const addItem = () => {
    setItens([...itens, {
      descricao: '',
      unidade: 'UN',
      quantidade: 1,
      valor_unitario: 0,
      valor_desconto: 0,
      aliquota_icms: 0,
      cfop: formData.cfop || '5102'
    }]);
  };

  const removeItem = (index: number) => {
    if (itens.length > 1) {
      setItens(itens.filter((_, i) => i !== index));
    } else {
      alert('A nota fiscal deve ter pelo menos um item');
    }
  };

  const calcularTotalItem = (item: ItemNF) => {
    return (item.quantidade * item.valor_unitario) - item.valor_desconto;
  };

  const calcularTotalNota = () => {
    const totalProdutos = itens.reduce((sum, item) => sum + calcularTotalItem(item), 0);
    return totalProdutos + formData.valor_frete + formData.valor_seguro - formData.valor_desconto;
  };

  const isReadOnly = nota?.id && nota?.id > 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl my-8">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b sticky top-0 bg-white z-10 rounded-t-lg">
          <h2 className="text-2xl font-bold text-gray-900">
            {nota ? (isReadOnly ? 'Visualizar Nota Fiscal' : 'Editar Nota Fiscal') : 'Nova Nota Fiscal'}
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
          {/* Dados da Nota */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Dados da Nota Fiscal</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Série *
                </label>
                <input
                  type="text"
                  name="serie"
                  value={formData.serie}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                  disabled={isReadOnly}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo *
                </label>
                <select
                  name="tipo"
                  value={formData.tipo}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                  disabled={isReadOnly}
                >
                  <option value="saida">Saída (Venda)</option>
                  <option value="entrada">Entrada (Compra)</option>
                  <option value="devolucao">Devolução</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cliente *
                </label>
                <select
                  name="cliente_id"
                  value={formData.cliente_id || ''}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required={formData.tipo === 'saida'}
                  disabled={isReadOnly}
                >
                  <option value="">Selecione um cliente</option>
                  {clientes.map(cliente => (
                    <option key={cliente.id} value={cliente.id}>
                      {cliente.codigo} - {cliente.nome}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Natureza da Operação *
                </label>
                <input
                  type="text"
                  name="natureza_operacao"
                  value={formData.natureza_operacao}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Venda de mercadoria"
                  required
                  disabled={isReadOnly}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CFOP
                </label>
                <input
                  type="text"
                  name="cfop"
                  value={formData.cfop || ''}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: 5102"
                  disabled={isReadOnly}
                />
              </div>
            </div>
          </div>

          {/* Itens */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Itens da Nota Fiscal</h3>
              {!isReadOnly && (
                <button
                  type="button"
                  onClick={addItem}
                  className="flex items-center px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Adicionar Item
                </button>
              )}
            </div>

            <div className="space-y-4 max-h-96 overflow-y-auto">
              {itens.map((item, index) => (
                <div key={index} className="bg-white rounded-lg p-4 border">
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-sm font-semibold text-gray-700">Item {index + 1}</span>
                    {!isReadOnly && itens.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeItem(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
                    <div className="md:col-span-2">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Material
                      </label>
                      <select
                        value={item.material_id || ''}
                        onChange={(e) => handleMaterialSelect(index, parseInt(e.target.value))}
                        className="w-full px-2 py-1.5 text-sm border rounded focus:ring-2 focus:ring-blue-500"
                        disabled={isReadOnly}
                      >
                        <option value="">Selecione (opcional)</option>
                        {materiais.map(mat => (
                          <option key={mat.id} value={mat.id}>
                            {mat.codigo} - {mat.nome}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Descrição *
                      </label>
                      <input
                        type="text"
                        value={item.descricao}
                        onChange={(e) => handleItemChange(index, 'descricao', e.target.value)}
                        className="w-full px-2 py-1.5 text-sm border rounded focus:ring-2 focus:ring-blue-500"
                        required
                        disabled={isReadOnly}
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Qtd *
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={item.quantidade}
                        onChange={(e) => handleItemChange(index, 'quantidade', parseFloat(e.target.value))}
                        className="w-full px-2 py-1.5 text-sm border rounded focus:ring-2 focus:ring-blue-500"
                        required
                        disabled={isReadOnly}
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Un *
                      </label>
                      <input
                        type="text"
                        value={item.unidade}
                        onChange={(e) => handleItemChange(index, 'unidade', e.target.value)}
                        className="w-full px-2 py-1.5 text-sm border rounded focus:ring-2 focus:ring-blue-500"
                        required
                        disabled={isReadOnly}
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Valor Unit. (R$) *
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={item.valor_unitario}
                        onChange={(e) => handleItemChange(index, 'valor_unitario', parseFloat(e.target.value))}
                        className="w-full px-2 py-1.5 text-sm border rounded focus:ring-2 focus:ring-blue-500"
                        required
                        disabled={isReadOnly}
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Desconto (R$)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={item.valor_desconto}
                        onChange={(e) => handleItemChange(index, 'valor_desconto', parseFloat(e.target.value))}
                        className="w-full px-2 py-1.5 text-sm border rounded focus:ring-2 focus:ring-blue-500"
                        disabled={isReadOnly}
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        ICMS (%)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={item.aliquota_icms}
                        onChange={(e) => handleItemChange(index, 'aliquota_icms', parseFloat(e.target.value))}
                        className="w-full px-2 py-1.5 text-sm border rounded focus:ring-2 focus:ring-blue-500"
                        disabled={isReadOnly}
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Total do Item
                      </label>
                      <div className="w-full px-2 py-1.5 text-sm border rounded bg-gray-50 font-semibold">
                        R$ {calcularTotalItem(item).toFixed(2)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Totais */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Valores Adicionais e Totais</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Frete (R$)
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="valor_frete"
                  value={formData.valor_frete}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  disabled={isReadOnly}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seguro (R$)
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="valor_seguro"
                  value={formData.valor_seguro}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  disabled={isReadOnly}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Desconto (R$)
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="valor_desconto"
                  value={formData.valor_desconto}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  disabled={isReadOnly}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Total da NF
                </label>
                <div className="w-full px-3 py-2 border rounded-lg bg-green-50 font-bold text-lg text-green-700">
                  R$ {calcularTotalNota().toFixed(2)}
                </div>
              </div>
            </div>
          </div>

          {/* Observações */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Observações
            </label>
            <textarea
              name="observacao"
              value={formData.observacao || ''}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Observações adicionais..."
              disabled={isReadOnly}
            />
          </div>

          {/* Buttons */}
          {!isReadOnly && (
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
                {loading ? 'Salvando...' : 'Salvar Nota Fiscal'}
              </button>
            </div>
          )}
          
          {isReadOnly && (
            <div className="flex justify-end pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Fechar
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default NotaFiscalForm;
