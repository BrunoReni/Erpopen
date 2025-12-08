import { useState, useEffect } from 'react';
import { ArrowRight } from 'lucide-react';
import { MainLayout } from '../../components/layout/MainLayout';
import api from '../../services/api';

interface ContaBancaria {
  id: number;
  nome: string;
  banco: string;
  saldo_atual: number;
}

export function TransferenciaForm() {
  const [contas, setContas] = useState<ContaBancaria[]>([]);
  const [contaOrigemId, setContaOrigemId] = useState<number>(0);
  const [contaDestinoId, setContaDestinoId] = useState<number>(0);
  const [valor, setValor] = useState<number>(0);
  const [data, setData] = useState<string>(new Date().toISOString().slice(0, 16));
  const [descricao, setDescricao] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchContas();
  }, []);

  const fetchContas = async () => {
    try {
      const response = await api.get('/financeiro/contas-bancarias');
      setContas(response.data);
    } catch (error) {
      console.error('Erro ao buscar contas bancárias:', error);
    }
  };

  const contaOrigem = contas.find(c => c.id === contaOrigemId);
  const contaDestino = contas.find(c => c.id === contaDestinoId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!contaOrigemId || !contaDestinoId) {
      alert('Selecione as contas de origem e destino');
      return;
    }
    
    if (contaOrigemId === contaDestinoId) {
      alert('Conta origem e destino devem ser diferentes');
      return;
    }
    
    if (valor <= 0) {
      alert('O valor deve ser maior que zero');
      return;
    }
    
    if (contaOrigem && valor > contaOrigem.saldo_atual) {
      alert('Saldo insuficiente na conta de origem');
      return;
    }
    
    if (!descricao.trim()) {
      alert('Informe uma descrição para a transferência');
      return;
    }
    
    setLoading(true);

    try {
      const response = await api.post('/financeiro/transferencias', {
        conta_origem_id: contaOrigemId,
        conta_destino_id: contaDestinoId,
        valor: valor,
        data: data,
        descricao: descricao
      });
      
      alert('Transferência realizada com sucesso!');
      
      // Limpar formulário
      setContaOrigemId(0);
      setContaDestinoId(0);
      setValor(0);
      setDescricao('');
      setData(new Date().toISOString().slice(0, 16));
      
      // Recarregar contas para atualizar saldos
      fetchContas();
    } catch (error: any) {
      console.error('Erro ao realizar transferência:', error);
      alert(error.response?.data?.detail || 'Erro ao realizar transferência');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">
              Transferência entre Contas
            </h2>
            <p className="text-gray-500 mt-1">
              Transferir valores entre suas contas bancárias
            </p>
          </div>

          <form onSubmit={handleSubmit} className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
              {/* Conta Origem */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Conta Origem *
                </label>
                <select
                  value={contaOrigemId}
                  onChange={(e) => setContaOrigemId(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value={0}>Selecione</option>
                  {contas.map(conta => (
                    <option key={conta.id} value={conta.id}>
                      {conta.nome}
                    </option>
                  ))}
                </select>
                {contaOrigem && (
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    <div className="text-xs text-gray-500">Banco</div>
                    <div className="text-sm font-medium">{contaOrigem.banco}</div>
                    <div className="text-xs text-gray-500 mt-1">Saldo Atual</div>
                    <div className="text-lg font-bold text-green-600">
                      R$ {contaOrigem.saldo_atual.toFixed(2)}
                    </div>
                  </div>
                )}
              </div>

              {/* Seta */}
              <div className="flex justify-center pb-8">
                <div className="bg-blue-100 p-3 rounded-full">
                  <ArrowRight className="w-6 h-6 text-blue-600" />
                </div>
              </div>

              {/* Conta Destino */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Conta Destino *
                </label>
                <select
                  value={contaDestinoId}
                  onChange={(e) => setContaDestinoId(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value={0}>Selecione</option>
                  {contas
                    .filter(c => c.id !== contaOrigemId)
                    .map(conta => (
                      <option key={conta.id} value={conta.id}>
                        {conta.nome}
                      </option>
                    ))}
                </select>
                {contaDestino && (
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    <div className="text-xs text-gray-500">Banco</div>
                    <div className="text-sm font-medium">{contaDestino.banco}</div>
                    <div className="text-xs text-gray-500 mt-1">Saldo Atual</div>
                    <div className="text-lg font-bold text-green-600">
                      R$ {contaDestino.saldo_atual.toFixed(2)}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Valor e Data */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Valor da Transferência *
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={valor}
                  onChange={(e) => setValor(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                  min="0.01"
                  placeholder="0.00"
                />
                {contaOrigem && valor > 0 && (
                  <div className="mt-2 text-sm">
                    {valor > contaOrigem.saldo_atual ? (
                      <span className="text-red-600">⚠️ Saldo insuficiente</span>
                    ) : (
                      <span className="text-green-600">
                        ✓ Saldo após transferência: R$ {(contaOrigem.saldo_atual - valor).toFixed(2)}
                      </span>
                    )}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data da Transferência *
                </label>
                <input
                  type="datetime-local"
                  value={data}
                  onChange={(e) => setData(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            {/* Descrição */}
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descrição *
              </label>
              <textarea
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                placeholder="Ex: Transferência para pagamento de fornecedores..."
              />
            </div>

            {/* Preview da Transferência */}
            {contaOrigem && contaDestino && valor > 0 && (
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">
                  Resumo da Transferência
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">De:</span>
                    <span className="ml-2 font-medium">{contaOrigem.nome}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Para:</span>
                    <span className="ml-2 font-medium">{contaDestino.nome}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Valor:</span>
                    <span className="ml-2 font-medium text-blue-600">
                      R$ {valor.toFixed(2)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Data:</span>
                    <span className="ml-2 font-medium">
                      {new Date(data).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Botões */}
            <div className="flex justify-end gap-4 mt-6 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={() => window.history.back()}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                disabled={loading}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
                disabled={loading || !contaOrigemId || !contaDestinoId || valor <= 0}
              >
                {loading ? 'Processando...' : 'Realizar Transferência'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}
