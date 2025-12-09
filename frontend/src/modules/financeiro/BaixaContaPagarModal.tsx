import { useState, useEffect } from 'react';
import { X, DollarSign } from 'lucide-react';
import axios from 'axios';

interface ContaBancaria {
  id: number;
  nome: string;
  banco: string;
  saldo_atual: number;
}

interface BaixaContaPagarModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  conta: any;
}

export function BaixaContaPagarModal({ isOpen, onClose, onSuccess, conta }: BaixaContaPagarModalProps) {
  const [juros, setJuros] = useState<number>(0);
  const [desconto, setDesconto] = useState<number>(0);
  const [valorPagar, setValorPagar] = useState<number>(0);
  const [dataPagamento, setDataPagamento] = useState<string>('');
  const [contaBancariaId, setContaBancariaId] = useState<number | undefined>(undefined);
  const [observacoes, setObservacoes] = useState<string>('');
  const [contasBancarias, setContasBancarias] = useState<ContaBancaria[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen && conta) {
      loadContasBancarias();
      // Calcular saldo devedor
      const saldoDevedor = conta.valor_original + (conta.juros || 0) - (conta.desconto || 0) - conta.valor_pago;
      setValorPagar(saldoDevedor);
      setJuros(0);
      setDesconto(0);
      setDataPagamento(new Date().toISOString().split('T')[0]);
      setObservacoes('');
      setContaBancariaId(undefined);
      setError('');
    }
  }, [isOpen, conta]);

  const loadContasBancarias = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/financeiro/contas-bancarias', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setContasBancarias(response.data);
    } catch (err) {
      console.error('Erro ao carregar contas bancárias:', err);
    }
  };

  const calcularValorFinal = () => {
    if (!conta) return 0;
    const saldoDevedor = conta.valor_original + (conta.juros || 0) - (conta.desconto || 0) - conta.valor_pago;
    return saldoDevedor + juros - desconto;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validações
    if (!contaBancariaId) {
      setError('Selecione uma conta bancária');
      return;
    }

    if (valorPagar <= 0) {
      setError('Valor a pagar deve ser maior que zero');
      return;
    }

    const valorFinal = calcularValorFinal();
    if (valorPagar > valorFinal) {
      setError(`Valor a pagar não pode ser maior que o saldo devedor (R$ ${valorFinal.toFixed(2)})`);
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      const baixaData = {
        valor_pago: valorPagar,
        juros: juros,
        desconto: desconto,
        conta_bancaria_id: contaBancariaId,
        data_pagamento: dataPagamento ? new Date(dataPagamento).toISOString() : null,
        observacoes: observacoes || null
      };

      await axios.post(
        `http://localhost:8000/financeiro/contas-pagar/${conta.id}/baixar`,
        baixaData,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Erro ao realizar baixa:', err);
      setError(err.response?.data?.detail || 'Erro ao realizar baixa');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !conta) return null;

  const saldoDevedor = conta.valor_original + (conta.juros || 0) - (conta.desconto || 0) - conta.valor_pago;
  const valorFinal = calcularValorFinal();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <DollarSign className="text-red-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Baixar Conta a Pagar</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Informações da Conta */}
          <div className="bg-gray-50 p-4 rounded-lg space-y-2">
            <div className="text-sm text-gray-600">
              <span className="font-semibold">Descrição:</span> {conta.descricao}
            </div>
            <div className="text-sm text-gray-600">
              <span className="font-semibold">Vencimento:</span>{' '}
              {new Date(conta.data_vencimento).toLocaleDateString('pt-BR')}
            </div>
          </div>

          {/* Valores */}
          <div className="bg-blue-50 p-4 rounded-lg space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-700">Valor Original:</span>
              <span className="font-semibold text-gray-900">
                R$ {conta.valor_original.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-700">Já Pago:</span>
              <span className="font-semibold text-gray-900">
                R$ {conta.valor_pago.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between text-sm border-t border-blue-200 pt-2">
              <span className="text-gray-700 font-semibold">Saldo Devedor:</span>
              <span className="font-bold text-red-600">
                R$ {saldoDevedor.toFixed(2)}
              </span>
            </div>
          </div>

          {/* Acréscimos e Descontos */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Acréscimos / Descontos
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Juros/Multa (R$)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  value={juros}
                  onChange={(e) => setJuros(parseFloat(e.target.value) || 0)}
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Desconto (R$)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  value={desconto}
                  onChange={(e) => setDesconto(parseFloat(e.target.value) || 0)}
                />
              </div>
            </div>
          </div>

          {/* Valor Final */}
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-gray-700 font-semibold">Valor Final:</span>
              <span className="text-2xl font-bold text-gray-900">
                R$ {valorFinal.toFixed(2)}
              </span>
            </div>
          </div>

          {/* Valor a Pagar */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Valor a Pagar *
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              max={valorFinal}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              value={valorPagar}
              onChange={(e) => setValorPagar(parseFloat(e.target.value) || 0)}
            />
            <p className="text-xs text-gray-500 mt-1">
              Pode ser menor que o total para baixa parcial
            </p>
          </div>

          {/* Data Pagamento */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data do Pagamento *
            </label>
            <input
              type="date"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              value={dataPagamento}
              onChange={(e) => setDataPagamento(e.target.value)}
            />
          </div>

          {/* Conta Bancária */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Conta Bancária *
            </label>
            <select
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              value={contaBancariaId || ''}
              onChange={(e) => setContaBancariaId(parseInt(e.target.value))}
            >
              <option value="">Selecione uma conta</option>
              {contasBancarias.map((cb) => (
                <option key={cb.id} value={cb.id}>
                  {cb.banco} - {cb.nome} (Saldo: R$ {cb.saldo_atual.toFixed(2)})
                </option>
              ))}
            </select>
          </div>

          {/* Observações */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Observações
            </label>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              rows={3}
              placeholder="Observações sobre o pagamento..."
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Botões */}
          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-400"
              disabled={loading}
            >
              {loading ? 'Processando...' : 'Confirmar Baixa'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
