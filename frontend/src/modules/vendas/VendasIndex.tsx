import { MainLayout } from '../../components/layout/MainLayout';
import { Users, FileText, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function VendasIndex() {
  const navigate = useNavigate();

  const modules = [
    {
      title: 'Clientes',
      description: 'Cadastro e gestão de clientes',
      icon: Users,
      path: '/vendas/clientes',
      color: 'green'
    },
    {
      title: 'Notas Fiscais',
      description: 'Emissão e gestão de notas fiscais',
      icon: FileText,
      path: '/vendas/notas-fiscais',
      color: 'blue'
    },
    {
      title: 'Pedidos de Venda',
      description: 'Criar e gerenciar pedidos de venda',
      icon: TrendingUp,
      path: '/vendas/pedidos',
      color: 'purple',
      disabled: true
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Vendas / Comercial</h1>
          <p className="text-gray-600 mt-2">
            Módulo de gestão de vendas e relacionamento com clientes
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module) => {
            const Icon = module.icon;
            const colorClasses = {
              green: 'bg-green-100 text-green-600',
              blue: 'bg-blue-100 text-blue-600',
              purple: 'bg-purple-100 text-purple-600'
            };

            return (
              <button
                key={module.path}
                onClick={() => !module.disabled && navigate(module.path)}
                disabled={module.disabled}
                className={`
                  bg-white p-6 rounded-lg shadow hover:shadow-lg transition-all text-left
                  ${module.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105 cursor-pointer'}
                `}
              >
                <div className={`w-12 h-12 rounded-lg ${colorClasses[module.color as keyof typeof colorClasses]} flex items-center justify-center mb-4`}>
                  <Icon size={24} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {module.title}
                  {module.disabled && (
                    <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                      Em breve
                    </span>
                  )}
                </h3>
                <p className="text-gray-600 text-sm">{module.description}</p>
              </button>
            );
          })}
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">📋 Módulos Disponíveis</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>✅ <strong>Clientes</strong> - Cadastro completo com código automático (CLI-XXXX)</li>
            <li>✅ <strong>Notas Fiscais</strong> - Emissão de NF com baixa automática de estoque</li>
            <li>⏳ <strong>Pedidos de Venda</strong> - Em desenvolvimento</li>
          </ul>
        </div>
      </div>
    </MainLayout>
  );
}
