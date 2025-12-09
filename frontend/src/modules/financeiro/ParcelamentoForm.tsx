import { useState, useEffect } from 'react';
import { X, Eye, Calendar, DollarSign } from 'lucide-react';
import api from '../../services/api';

interface ParcelamentoFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  tipo: 'pagar' | 'receber';
}

interface Parcela {
  numero: number;
  vencimento: string;
  valor: number;
}

interface Fornecedor {
  id: number;
  nome: string;
}

interface Cliente {
  id: number;
  nome: string;
}

interface CentroCusto {
  id: number;
  nome: string;
}

export function ParcelamentoForm({ isOpen, onClose, onSuccess, tipo }: ParcelamentoFormProps) {
  const [descricao, setDescricao] = useState('');
  const [entidadeId, setEntidadeId] = useState<number>(0);
  const [valorTotal, setValorTotal] = useState<number>(0);
  const [quantidadeParcelas, setQuantidadeParcelas] = useState<number>(1);
  const [dataPrimeiraParcela, setDataPrimeiraParcela] = useState<string>('');
  const [intervaloDias, setIntervaloDias] = useState<number>(30);
  const [formaPagamento, setFormaPagamento] = useState<string>('');
  const [centroCustoId, setCentroCustoId] = useState<number>(0);
  const [numeroDocumento, setNumeroDocumento] = useState<string>('');
  const [observacoes, setObservacoes] = useState<string>('');
  const [showPreview, setShowPreview] = useState(false);
  const [loading, setLoading] = useState(false);

  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [centrosCusto, setCentrosCusto] = useState<CentroCusto[]>([]);

  useEffect(() => {
    if (isOpen) {
      fetchData();
    }
  }, [isOpen, tipo]);

  const fetchData = async () => {
    try {
      const [centrosResponse] = await Promise.all([
        api.get('/financeiro/centros-custo'),
      ]);
      setCentrosCusto(centrosResponse.data);

      if (tipo === 'pagar') {
        const fornecedoresResponse = await api.get('/compras/fornecedores');
        setFornecedores(fornecedoresResponse.data);
      } else {
        const clientesResponse = await api.get('/vendas/clientes');
        setClientes(clientesResponse.data);
      }
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
    }
  };

  const calcularParcelas = (): Parcela[] => {
    const parcelas: Parcela[] = [];
    const valorParcela = Math.round((valorTotal / quantidadeParcelas) * 100) / 100;
    let somaValores = 0;

    for (let i = 0; i < quantidadeParcelas; i++) {
      const data = new Date(dataPrimeiraParcela);
      data.setDate(data.getDate() + (i * intervaloDias));
      
      // Ajustar a última parcela para compensar arredondamento
      const valor = i === quantidadeParcelas - 1 
        ? Math.round((valorTotal - somaValores) * 100) / 100
        : valorParcela;
      
      somaValores += valor;

      parcelas.push({
        numero: i + 1,
        vencimento: data.toISOString().split('T')[0],
        valor: valor
      });
    }

    return parcelas;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!descricao || !entidadeId || valorTotal <= 0 || quantidadeParcelas <= 0 || !dataPrimeiraParcela) {
      alert('Preencha todos os campos obrigatórios');
      return;
    }

    setLoading(true);
    try {
      const endpoint = tipo === 'pagar' 
        ? '/financeiro/contas-pagar/parcelada' 
        : '/financeiro/contas-receber/parcelada';

      const data = {
        descricao,
        [tipo === 'pagar' ? 'fornecedor_id' : 'cliente_id']: entidadeId,
        valor_total: valorTotal,
        quantidade_parcelas: quantidadeParcelas,
        data_primeira_parcela: dataPrimeiraParcela,
        intervalo_dias: intervaloDias,
        forma_pagamento: formaPagamento || undefined,
        centro_custo_id: centroCustoId || undefined,
        numero_documento: numeroDocumento || undefined,
        observacoes: observacoes || undefined,
      };

      await api.post(endpoint, data);
      alert(`${tipo === 'pagar' ? 'Conta a pagar' : 'Conta a receber'} parcelada criada com sucesso!`);
      onSuccess();
      handleClose();
    } catch (error: any) {
      console.error('Erro ao criar parcelamento:', error);
      alert(error.response?.data?.detail || 'Erro ao criar parcelamento');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setDescricao('');
    setEntidadeId(0);
    setValorTotal(0);
    setQuantidadeParcelas(1);
    setDataPrimeiraParcela('');
    setIntervaloDias(30);
    setFormaPagamento('');
    setCentroCustoId(0);
    setNumeroDocumento('');
    setObservacoes('');
    setShowPreview(false);
    onClose();
  };

  if (!isOpen) return null;

  const parcelas = dataPrimeiraParcela && quantidadeParcelas > 0 && valorTotal > 0 
    ? calcularParcelas() 
    : [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">
            Novo Parcelamento - {tipo === 'pagar' ? 'Contas a Pagar' : 'Contas a Receber'}
          </h2>
          <button onClick={handleClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Informações Básicas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descrição *
              </label>
              <input
                type="text"
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {tipo === 'pagar' ? 'Fornecedor *' : 'Cliente *'}
              </label>
              <select
                value={entidadeId}
                onChange={(e) => setEntidadeId(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value={0}>Selecione...</option>
                {tipo === 'pagar' 
                  ? fornecedores.map(f => <option key={f.id} value={f.id}>{f.nome}</option>)
                  : clientes.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)
                }
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Centro de Custo
              </label>
              <select
                value={centroCustoId}
                onChange={(e) => setCentroCustoId(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={0}>Selecione...</option>
                {centrosCusto.map(cc => (
                  <option key={cc.id} value={cc.id}>{cc.nome}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Parcelamento */}
          <div className="border-t border-gray-200 pt-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuração do Parcelamento</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Valor Total *
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={valorTotal}
                  onChange={(e) => setValorTotal(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quantidade de Parcelas *
                </label>
                <input
                  type="number"
                  min="1"
                  max="120"
                  value={quantidadeParcelas}
                  onChange={(e) => setQuantidadeParcelas(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Primeira Parcela *
                </label>
                <input
                  type="date"
                  value={dataPrimeiraParcela}
                  onChange={(e) => setDataPrimeiraParcela(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Intervalo (dias)
                </label>
                <input
                  type="number"
                  min="1"
                  value={intervaloDias}
                  onChange={(e) => setIntervaloDias(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Informações Adicionais */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Forma de Pagamento
              </label>
              <select
                value={formaPagamento}
                onChange={(e) => setFormaPagamento(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Selecione...</option>
                <option value="dinheiro">Dinheiro</option>
                <option value="pix">PIX</option>
                <option value="boleto">Boleto</option>
                <option value="cartao_credito">Cartão de Crédito</option>
                <option value="cartao_debito">Cartão de Débito</option>
                <option value="transferencia">Transferência</option>
                <option value="cheque">Cheque</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Número do Documento
              </label>
              <input
                type="text"
                value={numeroDocumento}
                onChange={(e) => setNumeroDocumento(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Observações
              </label>
              <textarea
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Preview de Parcelas */}
          {parcelas.length > 0 && (
            <div className="border-t border-gray-200 pt-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Preview das Parcelas</h3>
                <button
                  type="button"
                  onClick={() => setShowPreview(!showPreview)}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-blue-600 hover:text-blue-800"
                >
                  <Eye className="w-4 h-4" />
                  {showPreview ? 'Ocultar' : 'Visualizar'}
                </button>
              </div>

              {showPreview && (
                <div className="bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                  <table className="min-w-full">
                    <thead className="bg-gray-100 sticky top-0">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-700">Parcela</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-700">Vencimento</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-700">Valor</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {parcelas.map((parcela) => (
                        <tr key={parcela.numero} className="hover:bg-gray-100">
                          <td className="px-4 py-2 text-sm">
                            {parcela.numero}/{quantidadeParcelas}
                          </td>
                          <td className="px-4 py-2 text-sm">
                            {new Date(parcela.vencimento + 'T00:00:00').toLocaleDateString('pt-BR')}
                          </td>
                          <td className="px-4 py-2 text-sm text-right font-medium">
                            R$ {parcela.valor.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-gray-100 font-semibold">
                      <tr>
                        <td colSpan={2} className="px-4 py-2 text-sm text-right">Total:</td>
                        <td className="px-4 py-2 text-sm text-right">
                          R$ {parcelas.reduce((sum, p) => sum + p.valor, 0).toFixed(2)}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              )}

              <div className="mt-2 text-sm text-gray-600">
                {quantidadeParcelas} parcela{quantidadeParcelas > 1 ? 's' : ''} de R$ {(valorTotal / quantidadeParcelas).toFixed(2)} (aproximado)
              </div>
            </div>
          )}

          {/* Botões */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={handleClose}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Salvando...' : 'Criar Parcelamento'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
