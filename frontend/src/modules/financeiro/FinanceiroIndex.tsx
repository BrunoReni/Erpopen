import { MainLayout } from '../../components/layout/MainLayout';
import { Link } from 'react-router-dom';
import { DollarSign, CreditCard, Building2, Target, ArrowLeftRight, Receipt, CheckSquare } from 'lucide-react';

export function FinanceiroIndex() {
  const modules = [
    {
      title: 'Contas a Pagar',
      description: 'Gestão de contas e despesas',
      icon: DollarSign,
      path: '/financeiro/contas-pagar',
      color: 'bg-red-500'
    },
    {
      title: 'Contas a Receber',
      description: 'Controle de recebimentos',
      icon: CreditCard,
      path: '/financeiro/contas-receber',
      color: 'bg-green-500'
    },
    {
      title: 'Contas Bancárias',
      description: 'Cadastro de contas bancárias',
      icon: Building2,
      path: '/financeiro/bancos',
      color: 'bg-blue-500'
    },
    {
      title: 'Centros de Custo',
      description: 'Gestão de centros de custo',
      icon: Target,
      path: '/financeiro/centros-custo',
      color: 'bg-purple-500'
    },
    {
      title: 'Movimentações Bancárias',
      description: 'Entradas e saídas bancárias',
      icon: Receipt,
      path: '/financeiro/movimentacoes',
      color: 'bg-indigo-500'
    },
    {
      title: 'Transferências',
      description: 'Transferência entre contas',
      icon: ArrowLeftRight,
      path: '/financeiro/transferencias',
      color: 'bg-cyan-500'
    },
    {
      title: 'Conciliação Bancária',
      description: 'Conciliar com extrato',
      icon: CheckSquare,
      path: '/financeiro/conciliacao',
      color: 'bg-teal-500'
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Módulo Financeiro</h1>
          <p className="text-gray-500 mt-2">Controle financeiro completo da empresa</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <Link
                key={module.path}
                to={module.path}
                className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 cursor-pointer group"
              >
                <div className={`${module.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="text-white" size={24} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {module.title}
                </h3>
                <p className="text-sm text-gray-600">
                  {module.description}
                </p>
              </Link>
            );
          })}
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">Saldo Total</div>
            <div className="text-3xl font-bold text-gray-900">R$ 0,00</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-red-500 mb-1">A Pagar (Mês)</div>
            <div className="text-3xl font-bold text-red-600">R$ 0,00</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-green-500 mb-1">A Receber (Mês)</div>
            <div className="text-3xl font-bold text-green-600">R$ 0,00</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">Saldo Projetado</div>
            <div className="text-3xl font-bold text-gray-900">R$ 0,00</div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
