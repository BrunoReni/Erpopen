import { useState, useEffect } from 'react';
import { Check, X, AlertCircle } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import api from '../../services/api';

interface Movimentacao {
  id: number;
  data: string;
  tipo: string;
  natureza: string;
  descricao: string;
  valor: number;
  conciliado: boolean;
}

interface ContaBancaria {
  id: number;
  nome: string;
  saldo_atual: number;
}

export function ConciliacaoBancaria() {
  const [contas, setContas] = useState<ContaBancaria[]>([]);
  const [contaSelecionadaId, setContaSelecionadaId] = useState<number>(0);
  const [movimentacoes, setMovimentacoes] = useState<Movimentacao[]>([]);
  const [saldoExtrato, setSaldoExtrato] = useState<number>(0);
  const [movimentacoesSelecionadas, setMovimentacoesSelecionadas] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalEntradasPendentes, setTotalEntradasPendentes] = useState(0);
  const [totalSaidasPendentes, setTotalSaidasPendentes] = useState(0);

  useEffect(() => {
    fetchContas();
  }, []);

  useEffect(() => {
    if (contaSelecionadaId > 0) {
      fetchMovimentacoesPendentes();
    }
  }, [contaSelecionadaId]);

  const fetchContas = async () => {
    try {
      const response = await api.get('/financeiro/contas-bancarias');
      setContas(response.data);
    } catch (error) {
      console.error('Erro ao buscar contas bancárias:', error);
    }
  };

  const fetchMovimentacoesPendentes = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/financeiro/conciliacao/${contaSelecionadaId}`);
      setMovimentacoes(response.data.movimentacoes || []);
      setTotalEntradasPendentes(response.data.total_entradas_pendentes || 0);
      setTotalSaidasPendentes(response.data.total_saidas_pendentes || 0);
      setMovimentacoesSelecionadas([]);
    } catch (error) {
      console.error('Erro ao buscar movimentações pendentes:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleMovimentacao = (id: number) => {
    setMovimentacoesSelecionadas(prev =>
      prev.includes(id)
        ? prev.filter(movId => movId !== id)
        : [...prev, id]
    );
  };

  const toggleAll = () => {
    if (movimentacoesSelecionadas.length === movimentacoes.length) {
      setMovimentacoesSelecionadas([]);
    } else {
      setMovimentacoesSelecionadas(movimentacoes.map(m => m.id));
    }
  };

  const handleConciliar = async () => {
    if (movimentacoesSelecionadas.length === 0) {
      alert('Selecione pelo menos uma movimentação para conciliar');
      return;
    }

    if (!confirm(`Deseja conciliar ${movimentacoesSelecionadas.length} movimentação(ões)?`)) {
      return;
    }

    setLoading(true);
    try {
      await api.post(`/financeiro/conciliacao/${contaSelecionadaId}/conciliar`, 
        movimentacoesSelecionadas
      );
      alert('Movimentações conciliadas com sucesso!');
      fetchMovimentacoesPendentes();
      fetchContas(); // Atualizar saldos
    } catch (error: any) {
      console.error('Erro ao conciliar movimentações:', error);
      alert(error.response?.data?.detail || 'Erro ao conciliar movimentações');
    } finally {
      setLoading(false);
    }
  };

  const contaSelecionada = contas.find(c => c.id === contaSelecionadaId);
  
  const totalSelecionadoEntradas = movimentacoes
    .filter(m => movimentacoesSelecionadas.includes(m.id) && m.natureza === 'ENTRADA')
    .reduce((sum, m) => sum + m.valor, 0);
    
  const totalSelecionadoSaidas = movimentacoes
    .filter(m => movimentacoesSelecionadas.includes(m.id) && m.natureza === 'SAIDA')
    .reduce((sum, m) => sum + m.valor, 0);

  const saldoERP = contaSelecionada ? contaSelecionada.saldo_atual : 0;
  const diferenca = saldoExtrato - saldoERP;

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Conciliação Bancária</h1>
          <p className="text-gray-500 mt-2">
            Compare e concilie as movimentações do sistema com o extrato bancário
          </p>
        </div>

        {/* Seleção de Conta */}
        <div className="bg-white rounded-lg shadow p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Selecione a Conta Bancária
          </label>
          <select
            value={contaSelecionadaId}
            onChange={(e) => setContaSelecionadaId(Number(e.target.value))}
            className="w-full md:w-1/2 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={0}>Selecione uma conta</option>
            {contas.map(conta => (
              <option key={conta.id} value={conta.id}>
                {conta.nome} - Saldo: R$ {conta.saldo_atual.toFixed(2)}
              </option>
            ))}
          </select>
        </div>

        {contaSelecionadaId > 0 && (
          <>
            {/* Resumo e Saldo do Extrato */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-500 mb-1">Saldo no ERP</div>
                <div className="text-2xl font-bold text-gray-900">
                  R$ {saldoERP.toFixed(2)}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <label className="text-sm text-gray-500 mb-1 block">Saldo no Extrato</label>
                <input
                  type="number"
                  step="0.01"
                  value={saldoExtrato}
                  onChange={(e) => setSaldoExtrato(Number(e.target.value))}
                  className="text-2xl font-bold text-gray-900 border-b-2 border-gray-300 focus:border-blue-500 outline-none w-full"
                  placeholder="0.00"
                />
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-500 mb-1">Diferença</div>
                <div className={`text-2xl font-bold ${
                  Math.abs(diferenca) < 0.01 
                    ? 'text-green-600' 
                    : diferenca > 0 
                    ? 'text-red-600' 
                    : 'text-orange-600'
                }`}>
                  R$ {diferenca.toFixed(2)}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-500 mb-1">Pendentes</div>
                <div className="text-2xl font-bold text-yellow-600">
                  {movimentacoes.length}
                </div>
              </div>
            </div>

            {/* Estatísticas de Seleção */}
            {movimentacoesSelecionadas.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">
                  Movimentações Selecionadas: {movimentacoesSelecionadas.length}
                </h3>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Entradas:</span>
                    <span className="ml-2 font-medium text-green-600">
                      R$ {totalSelecionadoEntradas.toFixed(2)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Saídas:</span>
                    <span className="ml-2 font-medium text-red-600">
                      R$ {totalSelecionadoSaidas.toFixed(2)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Saldo:</span>
                    <span className={`ml-2 font-medium ${
                      totalSelecionadoEntradas - totalSelecionadoSaidas >= 0 
                        ? 'text-green-600' 
                        : 'text-red-600'
                    }`}>
                      R$ {(totalSelecionadoEntradas - totalSelecionadoSaidas).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Tabela de Movimentações */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b border-gray-200 flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">
                  Movimentações Pendentes de Conciliação
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={toggleAll}
                    className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                    disabled={loading || movimentacoes.length === 0}
                  >
                    {movimentacoesSelecionadas.length === movimentacoes.length ? 'Desmarcar' : 'Marcar'} Todas
                  </button>
                  <button
                    onClick={handleConciliar}
                    className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
                    disabled={loading || movimentacoesSelecionadas.length === 0}
                  >
                    Conciliar Selecionadas
                  </button>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-center">
                        <input
                          type="checkbox"
                          checked={movimentacoes.length > 0 && movimentacoesSelecionadas.length === movimentacoes.length}
                          onChange={toggleAll}
                          className="w-4 h-4"
                        />
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Natureza</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Valor</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {loading ? (
                      <tr>
                        <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                          Carregando...
                        </td>
                      </tr>
                    ) : movimentacoes.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-6 py-8 text-center">
                          <div className="flex flex-col items-center justify-center">
                            <Check className="w-12 h-12 text-green-500 mb-2" />
                            <p className="text-gray-500">Todas as movimentações estão conciliadas!</p>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      movimentacoes.map((mov) => (
                        <tr 
                          key={mov.id} 
                          className={`hover:bg-gray-50 cursor-pointer ${
                            movimentacoesSelecionadas.includes(mov.id) ? 'bg-blue-50' : ''
                          }`}
                          onClick={() => toggleMovimentacao(mov.id)}
                        >
                          <td className="px-6 py-4 text-center">
                            <input
                              type="checkbox"
                              checked={movimentacoesSelecionadas.includes(mov.id)}
                              onChange={() => toggleMovimentacao(mov.id)}
                              className="w-4 h-4"
                            />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(mov.data).toLocaleDateString('pt-BR')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {mov.tipo.replace(/_/g, ' ')}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {mov.descricao}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                              mov.natureza === 'ENTRADA' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {mov.natureza}
                            </span>
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium text-right ${
                            mov.natureza === 'ENTRADA' ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {mov.natureza === 'ENTRADA' ? '+' : '-'} R$ {mov.valor.toFixed(2)}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Ajuda */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-yellow-800">
                  <p className="font-semibold mb-1">Como conciliar:</p>
                  <ol className="list-decimal list-inside space-y-1">
                    <li>Informe o saldo que consta no extrato bancário</li>
                    <li>Selecione as movimentações que aparecem no extrato</li>
                    <li>Verifique se a diferença entre o saldo ERP e extrato está correta</li>
                    <li>Clique em "Conciliar Selecionadas" para confirmar</li>
                  </ol>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </MainLayout>
  );
}
