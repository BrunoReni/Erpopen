import { useState, useEffect } from 'react';
import { Plus, Trash2, CheckCircle, AlertCircle, DollarSign } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import api from '../../services/api';

interface Parcela {
  descricao: string;
  vencimento: string;
  valor: number;
}

interface ContaOriginal {
  id: number;
  descricao: string;
  valor_original: number;
  fornecedor_id?: number;
  cliente_id?: number;
  fornecedor?: { nome: string };
  cliente?: { nome: string };
  data_vencimento: string;
  status: string;
}

interface ContaBancaria {
  id: number;
  nome: string;
  banco: string;
  saldo_atual: number;
}

export function LiquidacaoForm() {
  const [tipoConta, setTipoConta] = useState<'RECEBER' | 'PAGAR'>('RECEBER');
  const [contas, setContas] = useState<ContaOriginal[]>([]);
  const [contaSelecionadaId, setContaSelecionadaId] = useState<number>(0);
  const [contaBancariaId, setContaBancariaId] = useState<number>(0);
  const [contasBancarias, setContasBancarias] = useState<ContaBancaria[]>([]);
  const [parcelas, setParcelas] = useState<Parcela[]>([
    { descricao: '', vencimento: '', valor: 0 }
  ]);
  const [observacao, setObservacao] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingContas, setLoadingContas] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchContasBancarias();
  }, []);

  useEffect(() => {
    if (searchTerm.length >= 2) {
      fetchContas();
    } else {
      setContas([]);
    }
  }, [searchTerm, tipoConta]);

  const fetchContasBancarias = async () => {
    try {
      const response = await api.get('/financeiro/contas-bancarias');
      setContasBancarias(response.data);
    } catch (error) {
      console.error('Erro ao buscar contas bancárias:', error);
    }
  };

  const fetchContas = async () => {
    setLoadingContas(true);
    try {
      const endpoint = tipoConta === 'RECEBER' 
        ? '/financeiro/contas-receber' 
        : '/financeiro/contas-pagar';
      const response = await api.get(endpoint);
      
      // Filter only pending accounts and by search term
      const filtered = response.data.filter((conta: ContaOriginal) => 
        conta.status.toLowerCase() === 'pendente' &&
        (conta.descricao.toLowerCase().includes(searchTerm.toLowerCase()) ||
         conta.id.toString().includes(searchTerm))
      );
      setContas(filtered);
    } catch (error) {
      console.error('Erro ao buscar contas:', error);
    } finally {
      setLoadingContas(false);
    }
  };

  const contaSelecionada = contas.find(c => c.id === contaSelecionadaId);
  const totalParcelas = parcelas.reduce((sum, p) => sum + (Number(p.valor) || 0), 0);
  const valorOriginal = contaSelecionada?.valor_original || 0;
  const diferenca = totalParcelas - valorOriginal;
  const valoresCorrespondentes = Math.abs(diferenca) < 0.01;

  const addParcela = () => {
    const valorRestante = valorOriginal - totalParcelas;
    const proximaData = new Date();
    proximaData.setMonth(proximaData.getMonth() + parcelas.length);
    
    setParcelas([
      ...parcelas,
      {
        descricao: `Parcela ${parcelas.length + 1} - ${contaSelecionada?.descricao || ''}`,
        vencimento: proximaData.toISOString().slice(0, 10),
        valor: Math.max(0, valorRestante)
      }
    ]);
  };

  const removeParcela = (index: number) => {
    if (parcelas.length > 1) {
      setParcelas(parcelas.filter((_, i) => i !== index));
    }
  };

  const updateParcela = (index: number, field: keyof Parcela, value: string | number) => {
    const newParcelas = [...parcelas];
    newParcelas[index] = { ...newParcelas[index], [field]: value };
    setParcelas(newParcelas);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validações
    if (!contaSelecionadaId) {
      alert('Selecione uma conta original');
      return;
    }

    if (!contaBancariaId) {
      alert('Selecione uma conta bancária');
      return;
    }

    if (parcelas.length === 0) {
      alert('Adicione pelo menos uma parcela');
      return;
    }

    if (!valoresCorrespondentes) {
      alert('A soma das parcelas deve ser igual ao valor original da conta');
      return;
    }

    // Validar se todas as parcelas têm data e valor
    const parcelaInvalida = parcelas.find(p => !p.vencimento || p.valor <= 0 || !p.descricao);
    if (parcelaInvalida) {
      alert('Preencha todos os campos de todas as parcelas');
      return;
    }

    if (!confirm(`Deseja realizar a baixa múltipla gerando ${parcelas.length} parcela(s)?`)) {
      return;
    }

    setLoading(true);

    try {
      const response = await api.post('/financeiro/baixa-multipla', {
        conta_id: contaSelecionadaId,
        tipo_conta: tipoConta,
        conta_bancaria_destino_id: contaBancariaId,
        parcelas_geradas: parcelas,
        observacao: observacao
      });

      alert(`Baixa múltipla realizada com sucesso!\n${response.data.contas_geradas} conta(s) gerada(s).`);

      // Limpar formulário
      setContaSelecionadaId(0);
      setContaBancariaId(0);
      setParcelas([{ descricao: '', vencimento: '', valor: 0 }]);
      setObservacao('');
      setSearchTerm('');
      setContas([]);
    } catch (error: any) {
      console.error('Erro ao realizar baixa múltipla:', error);
      alert(error.response?.data?.detail || 'Erro ao realizar baixa múltipla');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Baixa Múltipla</h1>
            <p className="text-gray-500 mt-1">Baixar título gerando múltiplas parcelas</p>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* Tipo de Conta */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Conta
              </label>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="RECEBER"
                    checked={tipoConta === 'RECEBER'}
                    onChange={(e) => {
                      setTipoConta(e.target.value as 'RECEBER');
                      setContaSelecionadaId(0);
                      setContas([]);
                    }}
                    className="mr-2"
                  />
                  <span className="text-green-600 font-medium">A Receber</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="PAGAR"
                    checked={tipoConta === 'PAGAR'}
                    onChange={(e) => {
                      setTipoConta(e.target.value as 'PAGAR');
                      setContaSelecionadaId(0);
                      setContas([]);
                    }}
                    className="mr-2"
                  />
                  <span className="text-red-600 font-medium">A Pagar</span>
                </label>
              </div>
            </div>

            {/* Busca e Seleção da Conta Original */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Buscar Conta Original *
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Digite ID ou descrição (mínimo 2 caracteres)"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              
              {loadingContas && (
                <p className="text-sm text-gray-500 mt-2">Buscando contas...</p>
              )}

              {contas.length > 0 && (
                <div className="mt-2 border border-gray-300 rounded-lg max-h-48 overflow-y-auto">
                  {contas.map((conta) => (
                    <div
                      key={conta.id}
                      onClick={() => setContaSelecionadaId(conta.id)}
                      className={`p-3 cursor-pointer hover:bg-gray-50 border-b last:border-b-0 ${
                        contaSelecionadaId === conta.id ? 'bg-purple-50 border-purple-200' : ''
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium text-gray-900">
                            #{conta.id} - {conta.descricao}
                          </div>
                          <div className="text-sm text-gray-600">
                            {tipoConta === 'RECEBER' ? conta.cliente?.nome : conta.fornecedor?.nome}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-gray-900">
                            {formatCurrency(conta.valor_original)}
                          </div>
                          <div className="text-xs text-gray-500">
                            Venc: {new Date(conta.data_vencimento).toLocaleDateString('pt-BR')}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Exibição dos Dados da Conta Selecionada */}
            {contaSelecionada && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h3 className="font-semibold text-purple-900 mb-3">Conta Selecionada</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">ID:</span>
                    <span className="ml-2 font-medium">#{contaSelecionada.id}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Valor:</span>
                    <span className="ml-2 font-medium">{formatCurrency(contaSelecionada.valor_original)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Descrição:</span>
                    <span className="ml-2 font-medium">{contaSelecionada.descricao}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Vencimento:</span>
                    <span className="ml-2 font-medium">
                      {new Date(contaSelecionada.data_vencimento).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">
                      {tipoConta === 'RECEBER' ? 'Cliente:' : 'Fornecedor:'}
                    </span>
                    <span className="ml-2 font-medium">
                      {tipoConta === 'RECEBER' ? contaSelecionada.cliente?.nome : contaSelecionada.fornecedor?.nome}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Status:</span>
                    <span className="ml-2 font-medium uppercase">{contaSelecionada.status}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Conta Bancária de Destino */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Conta Bancária de Destino *
              </label>
              <select
                value={contaBancariaId}
                onChange={(e) => setContaBancariaId(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              >
                <option value={0}>Selecione uma conta bancária</option>
                {contasBancarias.map((conta) => (
                  <option key={conta.id} value={conta.id}>
                    {conta.nome} - {conta.banco} (Saldo: {formatCurrency(conta.saldo_atual)})
                  </option>
                ))}
              </select>
            </div>

            {/* Geração de Parcelas */}
            {contaSelecionada && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-900">Parcelas a Gerar</h3>
                  <button
                    type="button"
                    onClick={addParcela}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <Plus size={20} />
                    Adicionar Parcela
                  </button>
                </div>

                <div className="space-y-3">
                  {parcelas.map((parcela, index) => (
                    <div key={index} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                      <div className="flex justify-between items-center mb-3">
                        <h4 className="font-medium text-gray-900">Parcela {index + 1}</h4>
                        {parcelas.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeParcela(index)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 size={18} />
                          </button>
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Descrição *
                          </label>
                          <input
                            type="text"
                            value={parcela.descricao}
                            onChange={(e) => updateParcela(index, 'descricao', e.target.value)}
                            placeholder="Descrição da parcela"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Data de Vencimento *
                          </label>
                          <input
                            type="date"
                            value={parcela.vencimento}
                            onChange={(e) => updateParcela(index, 'vencimento', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Valor (R$) *
                          </label>
                          <input
                            type="number"
                            step="0.01"
                            value={parcela.valor || ''}
                            onChange={(e) => updateParcela(index, 'valor', parseFloat(e.target.value) || 0)}
                            placeholder="0,00"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                            required
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Totalizador */}
                <div className="bg-white border-2 rounded-lg p-4">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Valor Original</div>
                      <div className="text-lg font-bold text-gray-900">
                        {formatCurrency(valorOriginal)}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Total das Parcelas</div>
                      <div className="text-lg font-bold text-gray-900">
                        {formatCurrency(totalParcelas)}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Diferença</div>
                      <div className={`text-lg font-bold ${valoresCorrespondentes ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(diferenca)}
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center justify-center gap-2">
                    {valoresCorrespondentes ? (
                      <>
                        <CheckCircle className="text-green-600" size={20} />
                        <span className="text-green-600 font-medium">Valores correspondem</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="text-red-600" size={20} />
                        <span className="text-red-600 font-medium">
                          Ajuste os valores das parcelas
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Observação */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Observação
              </label>
              <textarea
                value={observacao}
                onChange={(e) => setObservacao(e.target.value)}
                rows={3}
                placeholder="Observações adicionais sobre esta operação..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Botões de Ação */}
            <div className="flex gap-4 pt-4 border-t border-gray-200">
              <button
                type="submit"
                disabled={loading || !valoresCorrespondentes || !contaSelecionadaId || !contaBancariaId}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Processando...
                  </>
                ) : (
                  <>
                    <DollarSign size={20} />
                    Realizar Baixa Múltipla
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={() => window.location.href = '/financeiro'}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}
