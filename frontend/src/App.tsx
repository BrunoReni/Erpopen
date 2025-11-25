import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { LoginForm } from './components/auth/LoginForm';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Dashboard } from './components/Dashboard';
import { MainLayout } from './components/layout/MainLayout';
import { ComprasIndex } from './modules/compras/ComprasIndex';
import { FornecedoresList } from './modules/compras/FornecedoresList';
import { PedidosCompraList } from './modules/compras/PedidosCompraList';
import { CotacoesList } from './modules/compras/CotacoesList';
import { FinanceiroIndex } from './modules/financeiro/FinanceiroIndex';
import { ContasPagarList } from './modules/financeiro/ContasPagarList';
import { ContasReceberList } from './modules/financeiro/ContasReceberList';
import { ContasBancariasList } from './modules/financeiro/ContasBancariasList';
import { CentrosCustoList } from './modules/financeiro/CentrosCustoList';
import { MateriaisIndex } from './modules/materiais/MateriaisIndex';
import { VendasIndex } from './modules/vendas/VendasIndex';
import { ClientesList } from './modules/vendas/ClientesList';
import { MateriaisList } from './modules/materiais/MateriaisList';
import { MovimentosEstoqueList } from './modules/materiais/MovimentosEstoqueList';
import { UsersList } from './modules/users/UsersList';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginForm />} />
          
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute requiredPermissions={['dashboard:read']}>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          
          {/* Módulo de Compras */}
          <Route
            path="/compras"
            element={
              <ProtectedRoute requiredPermissions={['compras:read']}>
                <ComprasIndex />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/compras/fornecedores"
            element={
              <ProtectedRoute requiredPermissions={['compras:read']}>
                <FornecedoresList />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/compras/pedidos"
            element={
              <ProtectedRoute requiredPermissions={['compras:read']}>
                <PedidosCompraList />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/compras/cotacoes"
            element={
              <ProtectedRoute requiredPermissions={['compras:read']}>
                <CotacoesList />
              </ProtectedRoute>
            }
          />
          
          {/* Módulo Financeiro */}
          <Route
            path="/financeiro"
            element={
              <ProtectedRoute requiredPermissions={['financeiro:read']}>
                <FinanceiroIndex />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/financeiro/contas-pagar"
            element={
              <ProtectedRoute requiredPermissions={['financeiro:read']}>
                <ContasPagarList />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/financeiro/contas-receber"
            element={
              <ProtectedRoute requiredPermissions={['financeiro:read']}>
                <ContasReceberList />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/financeiro/bancos"
            element={
              <ProtectedRoute requiredPermissions={['financeiro:read']}>
                <ContasBancariasList />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/financeiro/centros-custo"
            element={
              <ProtectedRoute requiredPermissions={['financeiro:read']}>
                <CentrosCustoList />
              </ProtectedRoute>
            }
          />
          
          {/* Módulo de Materiais */}
          <Route
            path="/materiais"
            element={
              <ProtectedRoute requiredPermissions={['materiais:read']}>
                <MateriaisIndex />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/materiais/produtos"
            element={
              <ProtectedRoute requiredPermissions={['materiais:read']}>
                <MateriaisList />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/materiais/estoque"
            element={
              <ProtectedRoute requiredPermissions={['materiais:read']}>
                <MovimentosEstoqueList />
              </ProtectedRoute>
            }
          />
          
          {/* Vendas/Comercial */}
          <Route
            path="/vendas"
            element={
              <ProtectedRoute requiredPermissions={['vendas:read']}>
                <VendasIndex />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/vendas/clientes"
            element={
              <ProtectedRoute requiredPermissions={['vendas:read']}>
                <ClientesList />
              </ProtectedRoute>
            }
          />
          
          {/* Rotas antigas (manter por compatibilidade) */}
          <Route
            path="/users"
            element={
              <ProtectedRoute requiredPermissions={['users:read']}>
                <UsersList />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/reports"
            element={
              <ProtectedRoute requiredPermissions={['reports:read']}>
                <MainLayout>
                  <div>
                    <h1 className="text-2xl font-bold mb-4">Relatórios</h1>
                    <p className="text-gray-600">Em desenvolvimento...</p>
                  </div>
                </MainLayout>
              </ProtectedRoute>
            }
          />
          
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
