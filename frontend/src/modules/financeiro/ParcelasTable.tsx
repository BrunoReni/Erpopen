import { useState } from 'react';
import { DollarSign, Calendar, Eye, X } from 'lucide-react';
import api from '../../services/api';

interface Parcela {
  id: number;
  numero_parcela: number;
  total_parcelas: number;
  data_vencimento: string;
  valor: number;
  valor_pago?: number;
  valor_recebido?: number;
  status: string;
  juros: number;
  desconto: number;
}

interface ParcelasTableProps {
  contaId: number;
  tipo: 'pagar' | 'receber';
  parcelas: Parcela[];
  onBaixarParcela: (parcelaId: number) => void;
  onReagendarParcela: (parcelaId: number, novaData: string) => void;
  onRefresh: () => void;
}

export function ParcelasTable({ 
  contaId, 
  tipo, 
  parcelas, 
  onBaixarParcela, 
  onReagendarParcela,
  onRefresh 
}: ParcelasTableProps) {
  const [reagendandoId, setReagendandoId] = useState<number | null>(null);
  const [novaData, setNovaData] = useState<string>('');

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pago':
        return 'bg-green-100 text-green-800';
      case 'pendente':
        return 'bg-yellow-100 text-yellow-800';
      case 'parcial':
        return 'bg-blue-100 text-blue-800';
      case 'atrasado':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      'pendente': 'Pendente',
      'parcial': 'Parcial',
      'pago': 'Pago',
      'atrasado': 'Atrasado'
    };
    return labels[status.toLowerCase()] || status;
  };

  const handleReagendar = async (parcelaId: number) => {
    if (!novaData) {
      alert('Informe a nova data de vencimento');
      return;
    }

    try {
      await api.put(
        `/financeiro/contas-${tipo}/${contaId}/parcelas/${parcelaId}/reagendar?nova_data=${novaData}`
      );
      alert('Parcela reagendada com sucesso!');
      setReagendandoId(null);
      setNovaData('');
      onRefresh();
    } catch (error: any) {
      console.error('Erro ao reagendar parcela:', error);
      alert(error.response?.data?.detail || 'Erro ao reagendar parcela');
    }
  };

  const calcularValorPendente = (parcela: Parcela) => {
    const valorPagoRecebido = tipo === 'pagar' 
      ? (parcela.valor_pago || 0) 
      : (parcela.valor_recebido || 0);
    return parcela.valor + parcela.juros - parcela.desconto - valorPagoRecebido;
  };

  if (parcelas.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <p className="text-gray-500">Nenhuma parcela encontrada para esta conta.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">
          Parcelas ({parcelas.length})
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Parcela
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Vencimento
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Valor
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Valor {tipo === 'pagar' ? 'Pago' : 'Recebido'}
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Pendente
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {parcelas.map((parcela) => (
              <tr key={parcela.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {parcela.numero_parcela}/{parcela.total_parcelas}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {reagendandoId === parcela.id ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="date"
                        value={novaData}
                        onChange={(e) => setNovaData(e.target.value)}
                        className="px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                      <button
                        onClick={() => handleReagendar(parcela.id)}
                        className="text-green-600 hover:text-green-800"
                        title="Confirmar"
                      >
                        ✓
                      </button>
                      <button
                        onClick={() => {
                          setReagendandoId(null);
                          setNovaData('');
                        }}
                        className="text-red-600 hover:text-red-800"
                        title="Cancelar"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    new Date(parcela.data_vencimento).toLocaleDateString('pt-BR')
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                  R$ {parcela.valor.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                  R$ {(tipo === 'pagar' ? parcela.valor_pago : parcela.valor_recebido)?.toFixed(2) || '0.00'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-orange-600">
                  R$ {calcularValorPendente(parcela).toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(parcela.status)}`}>
                    {getStatusLabel(parcela.status)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center text-sm">
                  <div className="flex items-center justify-center gap-2">
                    {parcela.status.toLowerCase() !== 'pago' && (
                      <>
                        <button
                          onClick={() => onBaixarParcela(parcela.id)}
                          className="text-green-600 hover:text-green-800"
                          title={tipo === 'pagar' ? 'Baixar (Pagar)' : 'Baixar (Receber)'}
                        >
                          <DollarSign className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setReagendandoId(parcela.id);
                            setNovaData(parcela.data_vencimento.split('T')[0]);
                          }}
                          className="text-blue-600 hover:text-blue-800"
                          title="Reagendar"
                        >
                          <Calendar className="w-4 h-4" />
                        </button>
                      </>
                    )}
                    {parcela.status.toLowerCase() === 'pago' && (
                      <span className="text-gray-400">
                        <Eye className="w-4 h-4" />
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-gray-50">
            <tr>
              <td colSpan={2} className="px-6 py-3 text-sm font-semibold text-gray-900 text-right">
                Total:
              </td>
              <td className="px-6 py-3 text-sm font-semibold text-gray-900 text-right">
                R$ {parcelas.reduce((sum, p) => sum + p.valor, 0).toFixed(2)}
              </td>
              <td className="px-6 py-3 text-sm font-semibold text-gray-900 text-right">
                R$ {parcelas.reduce((sum, p) => sum + (tipo === 'pagar' ? (p.valor_pago || 0) : (p.valor_recebido || 0)), 0).toFixed(2)}
              </td>
              <td className="px-6 py-3 text-sm font-semibold text-orange-600 text-right">
                R$ {parcelas.reduce((sum, p) => sum + calcularValorPendente(p), 0).toFixed(2)}
              </td>
              <td colSpan={2}></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
