import { useEffect, useState } from 'react';
import { MainLayout } from '../../components/layout/MainLayout';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Code, 
  Layout, 
  FileText, 
  TestTube,
  Filter,
  TrendingUp
} from 'lucide-react';
import api from '../../services/api';

interface Feature {
  id: string;
  name: string;
  module: string;
  description: string;
  status: 'complete' | 'backend_only' | 'frontend_only' | 'partial' | 'disabled';
  has_backend: boolean;
  has_frontend: boolean;
  has_tests: boolean;
  has_docs: boolean;
  completeness_percentage: number;
  backend_endpoints: string[];
  frontend_components: string[];
  test_files: string[];
  doc_files: string[];
  issue_number?: number;
  pr_number?: number;
}

interface FeatureStats {
  total: number;
  complete: number;
  backend_only: number;
  frontend_only: number;
  partial: number;
  disabled: number;
  incomplete: number;
  average_completeness: number;
  completion_rate: number;
  modules: Record<string, {
    total: number;
    complete: number;
    incomplete: number;
  }>;
}

type FilterType = 'all' | 'incomplete' | 'backend_only' | 'complete';

export function IntegrationDashboard() {
  const [features, setFeatures] = useState<Feature[]>([]);
  const [stats, setStats] = useState<FeatureStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterType>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load features and stats in parallel
      const [featuresRes, statsRes] = await Promise.all([
        api.get('/dev/features'),
        api.get('/dev/features/stats')
      ]);
      
      setFeatures(featuresRes.data.features);
      setStats(statsRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar dados');
      console.error('Error loading dev tools data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      complete: { color: 'bg-green-100 text-green-800', label: 'Completo', icon: CheckCircle },
      backend_only: { color: 'bg-red-100 text-red-800', label: 'Só Backend', icon: XCircle },
      frontend_only: { color: 'bg-yellow-100 text-yellow-800', label: 'Só Frontend', icon: AlertTriangle },
      partial: { color: 'bg-blue-100 text-blue-800', label: 'Parcial', icon: AlertTriangle },
      disabled: { color: 'bg-gray-100 text-gray-800', label: 'Desabilitado', icon: XCircle }
    };
    
    const badge = badges[status as keyof typeof badges] || badges.disabled;
    const Icon = badge.icon;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className="w-3 h-3" />
        {badge.label}
      </span>
    );
  };

  const getModuleBadge = (module: string) => {
    const colors: Record<string, string> = {
      financeiro: 'bg-blue-100 text-blue-800',
      vendas: 'bg-green-100 text-green-800',
      compras: 'bg-purple-100 text-purple-800',
      materiais: 'bg-orange-100 text-orange-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${colors[module] || 'bg-gray-100 text-gray-800'}`}>
        {module.charAt(0).toUpperCase() + module.slice(1)}
      </span>
    );
  };

  const filteredFeatures = features.filter(feature => {
    if (filter === 'all') return true;
    if (filter === 'complete') return feature.status === 'complete';
    if (filter === 'backend_only') return feature.status === 'backend_only';
    if (filter === 'incomplete') return ['backend_only', 'frontend_only', 'partial'].includes(feature.status);
    return true;
  });

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Carregando dados...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <XCircle className="w-5 h-5" />
            <p className="font-medium">Erro ao carregar dashboard</p>
          </div>
          <p className="text-red-600 mt-2">{error}</p>
          <button 
            onClick={loadData}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🔧 Dev Tools - Quality Gates</h1>
          <p className="text-gray-600 mt-2">
            Monitoramento de completude de features e integração backend/frontend
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Features</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Code className="w-8 h-8 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Completas</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">{stats.complete}</p>
                </div>
                <div className="p-3 bg-green-100 rounded-lg">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
              </div>
              <div className="mt-4">
                <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                  <span>Completude</span>
                  <span>{stats.completion_rate.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full transition-all"
                    style={{ width: `${stats.completion_rate}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Incompletas</p>
                  <p className="text-3xl font-bold text-orange-600 mt-2">{stats.incomplete}</p>
                </div>
                <div className="p-3 bg-orange-100 rounded-lg">
                  <AlertTriangle className="w-8 h-8 text-orange-600" />
                </div>
              </div>
              <div className="mt-2 text-xs text-gray-600">
                <div className="flex justify-between">
                  <span>Só Backend:</span>
                  <span className="font-medium">{stats.backend_only}</span>
                </div>
                <div className="flex justify-between">
                  <span>Parciais:</span>
                  <span className="font-medium">{stats.partial}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Média Completude</p>
                  <p className="text-3xl font-bold text-blue-600 mt-2">
                    {stats.average_completeness.toFixed(0)}%
                  </p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <TrendingUp className="w-8 h-8 text-blue-600" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center gap-2 flex-wrap">
            <Filter className="w-5 h-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Filtros:</span>
            {[
              { id: 'all', label: 'Todas' },
              { id: 'complete', label: 'Completas' },
              { id: 'incomplete', label: 'Incompletas' },
              { id: 'backend_only', label: 'Só Backend' }
            ].map(f => (
              <button
                key={f.id}
                onClick={() => setFilter(f.id as FilterType)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  filter === f.id 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {f.label}
              </button>
            ))}
            <span className="ml-auto text-sm text-gray-600">
              {filteredFeatures.length} feature(s)
            </span>
          </div>
        </div>

        {/* Features Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Feature
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Módulo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Backend
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Frontend
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Testes
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Docs
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Completude
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredFeatures.map((feature) => (
                  <tr key={feature.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{feature.name}</div>
                        <div className="text-xs text-gray-500 mt-1">{feature.description}</div>
                        {feature.issue_number && (
                          <div className="text-xs text-blue-600 mt-1">
                            Issue #{feature.issue_number}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getModuleBadge(feature.module)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(feature.status)}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {feature.has_backend ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
                      ) : (
                        <XCircle className="w-5 h-5 text-gray-300 mx-auto" />
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {feature.has_frontend ? (
                        <Layout className="w-5 h-5 text-green-600 mx-auto" />
                      ) : (
                        <XCircle className="w-5 h-5 text-gray-300 mx-auto" />
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {feature.has_tests ? (
                        <TestTube className="w-5 h-5 text-green-600 mx-auto" />
                      ) : (
                        <XCircle className="w-5 h-5 text-gray-300 mx-auto" />
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {feature.has_docs ? (
                        <FileText className="w-5 h-5 text-green-600 mx-auto" />
                      ) : (
                        <XCircle className="w-5 h-5 text-gray-300 mx-auto" />
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all ${
                              feature.completeness_percentage === 100 
                                ? 'bg-green-600' 
                                : feature.completeness_percentage >= 50
                                ? 'bg-blue-600'
                                : 'bg-orange-600'
                            }`}
                            style={{ width: `${feature.completeness_percentage}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-gray-600 w-10 text-right">
                          {feature.completeness_percentage.toFixed(0)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {filteredFeatures.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Nenhuma feature encontrada com os filtros selecionados</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
