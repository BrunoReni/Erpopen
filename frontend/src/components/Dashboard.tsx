import { useAuth } from '../contexts/AuthContext';
import { MainLayout } from './layout/MainLayout';
import { BarChart3, Users, Package, TrendingUp } from 'lucide-react';

export function Dashboard() {
  const { user } = useAuth();

  const stats = [
    { 
      label: 'Total de Usuários', 
      value: '1,234', 
      icon: Users, 
      color: 'bg-blue-500',
      permission: 'users:read'
    },
    { 
      label: 'Produtos', 
      value: '567', 
      icon: Package, 
      color: 'bg-green-500',
      permission: 'products:read'
    },
    { 
      label: 'Vendas (Mês)', 
      value: 'R$ 45.2K', 
      icon: TrendingUp, 
      color: 'bg-yellow-500',
      permission: 'sales:read'
    },
    { 
      label: 'Relatórios', 
      value: '89', 
      icon: BarChart3, 
      color: 'bg-purple-500',
      permission: 'reports:read'
    },
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
            Bem-vindo, {user?.full_name || user?.email}!
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.label}
                className="bg-white rounded-lg shadow p-6 flex items-center gap-4"
              >
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Permissions Info */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Suas Permissões</h2>
          <div className="flex flex-wrap gap-2">
            {user?.permissions.map((perm) => (
              <span
                key={perm}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {perm}
              </span>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Ações Rápidas</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
              <Users className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm font-medium">Novo Usuário</p>
            </button>
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors">
              <Package className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm font-medium">Novo Produto</p>
            </button>
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors">
              <BarChart3 className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm font-medium">Ver Relatórios</p>
            </button>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
