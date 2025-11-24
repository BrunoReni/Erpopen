import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import api from '../../services/api';

interface Material {
  id: number;
  codigo: string;
  nome: string;
  unidade_medida: string;
  estoque_atual: number;
}

interface MovimentoEstoque {
  material_id: number;
  tipo_movimento: string;
  quantidade: number;
  observacao?: string;
}

interface MovimentoEstoqueFormProps {
  onClose: () => void;
  onSave: () => void;
}

export function MovimentoEstoqueForm({ onClose, onSave }: MovimentoEstoqueFormProps) {
  const [formData, setFormData] = useState<MovimentoEstoque>({
    material_id: 0,
    tipo_movimento: 'entrada',
    quantidade: 0,
    observacao: ''
  });
  const [materiais, setMateriais] = useState<Material[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<Material | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMateriais();
  }, []);

  const fetchMateriais = async () => {
    try {
      const response = await api.get('/materiais/produtos');
      setMateriais(response.data);
    } catch (error) {
      console.error('Erro ao buscar materiais:', error);
    }
  };

  const handleMaterialChange = (materialId: number) => {
    const material = materiais.find(m => m.id === materialId);
    setSelectedMaterial(material || null);
    setFormData({ ...formData, material_id: materialId });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post('/materiais/movimentos', formData);
      onSave();
    } catch (error: any) {
      console.error('Erro ao salvar movimento:', error);
      alert(error.response?.data?.detail || 'Erro ao salvar movimento');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">
                Novo Movimento de Estoque
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
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Material *
              </label>
              <select
                required
                value={formData.material_id}
                onChange={(e) => handleMaterialChange(parseInt(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Selecione...</option>
                {materiais.map((material) => (
                  <option key={material.id} value={material.id}>
                    {material.codigo} - {material.nome}
                  </option>
                ))}
              </select>

              {selectedMaterial && (
                <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-900">
                    <span className="font-medium">Estoque Atual:</span>{' '}
                    {selectedMaterial.estoque_atual} {selectedMaterial.unidade_medida}
                  </p>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Movimento *
              </label>
              <select
                required
                value={formData.tipo_movimento}
                onChange={(e) => setFormData({ ...formData, tipo_movimento: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="entrada">Entrada</option>
                <option value="saida">Saída</option>
                <option value="ajuste">Ajuste</option>
                <option value="transferencia">Transferência</option>
              </select>

              <div className="mt-2 text-sm text-gray-600">
                <ul className="list-disc list-inside space-y-1">
                  <li><strong>Entrada:</strong> Compra ou devolução de material</li>
                  <li><strong>Saída:</strong> Consumo ou venda de material</li>
                  <li><strong>Ajuste:</strong> Correção de estoque (inventário)</li>
                  <li><strong>Transferência:</strong> Movimentação entre locais</li>
                </ul>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quantidade *
              </label>
              <input
                type="number"
                required
                min="0.01"
                step="0.01"
                value={formData.quantidade}
                onChange={(e) => setFormData({ ...formData, quantidade: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="mt-1 text-sm text-gray-500">
                {formData.tipo_movimento === 'saida' ? 'Será subtraído do estoque' : 'Será adicionado ao estoque'}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Observação
              </label>
              <textarea
                value={formData.observacao}
                onChange={(e) => setFormData({ ...formData, observacao: e.target.value })}
                rows={3}
                placeholder="Motivo ou detalhes do movimento..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {selectedMaterial && (
              <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Resumo</h4>
                <div className="space-y-1 text-sm text-gray-600">
                  <p>Estoque Atual: {selectedMaterial.estoque_atual} {selectedMaterial.unidade_medida}</p>
                  <p>
                    {formData.tipo_movimento === 'saida' ? 'Diminuição' : 'Aumento'}:{' '}
                    {formData.quantidade} {selectedMaterial.unidade_medida}
                  </p>
                  <p className="font-medium text-gray-900 pt-2 border-t">
                    Novo Estoque:{' '}
                    {formData.tipo_movimento === 'saida'
                      ? selectedMaterial.estoque_atual - (formData.quantidade || 0)
                      : selectedMaterial.estoque_atual + (formData.quantidade || 0)}{' '}
                    {selectedMaterial.unidade_medida}
                  </p>
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
                {loading ? 'Salvando...' : 'Salvar Movimento'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}
