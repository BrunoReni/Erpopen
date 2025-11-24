import { MainLayout } from '../../components/layout/MainLayout';
import { Link } from 'react-router-dom';
import { ShoppingCart, Users, FileText, TrendingUp } from 'lucide-react';

export function ComprasIndex() {
  const modules = [
    {
      title: 'Fornecedores',
      description: 'Cadastro e gestão de fornecedores',
      icon: Users,
      path: '/compras/fornecedores',
      color: 'bg-blue-500'
    },
    {
      title: 'Pedidos de Compra',
      description: 'Solicitações e pedidos de compra',
      icon: ShoppingCart,
      path: '/compras/pedidos',
      color: 'bg-green-500'
    },
    {
      title: 'Cotações',
      description: 'Comparativo de preços e cotações',
      icon: FileText,
      path: '/compras/cotacoes',
      color: 'bg-yellow-500'
    },
    {
      title: 'Relatórios',
      description: 'Análises e relatórios de compras',
      icon: TrendingUp,
      path: '/compras/relatorios',
      color: 'bg-purple-500'
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Módulo de Compras</h1>
          <p className="text-gray-500 mt-2">Gestão completa do processo de compras</p>
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">Fornecedores Ativos</div>
            <div className="text-3xl font-bold text-gray-900">0</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">Pedidos em Andamento</div>
            <div className="text-3xl font-bold text-gray-900">0</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">Total Comprado (Mês)</div>
            <div className="text-3xl font-bold text-gray-900">R$ 0,00</div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
