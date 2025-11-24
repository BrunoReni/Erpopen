import { MainLayout } from '../../components/layout/MainLayout';
import { Link } from 'react-router-dom';
import { Package, List, TrendingDown, BarChart3 } from 'lucide-react';

export function MateriaisIndex() {
  const modules = [
    {
      title: 'Cadastro de Materiais',
      description: 'Produtos e materiais do estoque',
      icon: Package,
      path: '/materiais/produtos',
      color: 'bg-blue-500'
    },
    {
      title: 'Categorias',
      description: 'Categorização de materiais',
      icon: List,
      path: '/materiais/categorias',
      color: 'bg-purple-500'
    },
    {
      title: 'Movimentação',
      description: 'Entradas e saídas de estoque',
      icon: TrendingDown,
      path: '/materiais/estoque',
      color: 'bg-yellow-500'
    },
    {
      title: 'Relatórios',
      description: 'Análises e relatórios de estoque',
      icon: BarChart3,
      path: '/materiais/relatorios',
      color: 'bg-green-500'
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Módulo de Materiais</h1>
          <p className="text-gray-500 mt-2">Gestão completa de estoque e materiais</p>
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
            <div className="text-sm text-gray-500 mb-1">Total de Itens</div>
            <div className="text-3xl font-bold text-gray-900">0</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-yellow-500 mb-1">Estoque Baixo</div>
            <div className="text-3xl font-bold text-yellow-600">0</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">Valor em Estoque</div>
            <div className="text-3xl font-bold text-gray-900">R$ 0,00</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">Movimentos (Mês)</div>
            <div className="text-3xl font-bold text-gray-900">0</div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
