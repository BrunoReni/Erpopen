import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Menu, 
  X, 
  LayoutDashboard, 
  Users, 
  Package, 
  ShoppingCart, 
  FileText,
  Settings,
  LogOut
} from 'lucide-react';
import type { MenuItem } from '../../types';

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout, hasAnyPermission } = useAuth();

  const menuItems: MenuItem[] = [
    { 
      id: 'dashboard', 
      label: 'Dashboard', 
      icon: 'dashboard', 
      path: '/dashboard',
      requiredPermissions: ['dashboard:read']
    },
    { 
      id: 'compras', 
      label: 'Compras', 
      icon: 'shopping-cart', 
      path: '/compras',
      requiredPermissions: ['compras:read']
    },
    { 
      id: 'financeiro', 
      label: 'Financeiro', 
      icon: 'dollar-sign', 
      path: '/financeiro',
      requiredPermissions: ['financeiro:read']
    },
    { 
      id: 'materiais', 
      label: 'Materiais', 
      icon: 'package', 
      path: '/materiais',
      requiredPermissions: ['materiais:read']
    },
    { 
      id: 'vendas', 
      label: 'Vendas', 
      icon: 'users', 
      path: '/vendas',
      requiredPermissions: ['users:read']
    },
    { 
      id: 'users', 
      label: 'Usuários', 
      icon: 'users', 
      path: '/users',
      requiredPermissions: ['users:read']
    },
    { 
      id: 'reports', 
      label: 'Relatórios', 
      icon: 'file-text', 
      path: '/reports',
      requiredPermissions: ['reports:read']
    },
  ];

  const getIcon = (iconName: string) => {
    const icons: Record<string, any> = {
      dashboard: LayoutDashboard,
      users: Users,
      package: Package,
      'shopping-cart': ShoppingCart,
      'file-text': FileText,
      'dollar-sign': () => <span className="text-xl">$</span>,
      settings: Settings,
    };
    const Icon = icons[iconName] || LayoutDashboard;
    return typeof Icon === 'function' ? <Icon /> : <Icon className="w-5 h-5" />;
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Filter menu items based on permissions
  const visibleMenuItems = menuItems.filter(item => 
    !item.requiredPermissions || hasAnyPermission(item.requiredPermissions)
  );

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-blue-600 text-white"
      >
        {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Sidebar */}
      <aside
        className={`${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-40 w-64 bg-gray-900 text-white transition-transform duration-300 ease-in-out flex flex-col`}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-xl font-bold">ERP Open</h1>
          <p className="text-sm text-gray-400">{user?.email}</p>
          <div className="flex flex-wrap gap-1 mt-2">
            {user?.roles.map(role => (
              <span key={role} className="text-xs px-2 py-1 bg-blue-600 rounded">
                {role}
              </span>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {visibleMenuItems.map((item) => (
            <Link
              key={item.id}
              to={item.path!}
              className={`flex items-center gap-3 px-4 py-2 rounded-md transition-colors ${
                location.pathname === item.path
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              {getIcon(item.icon)}
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-800">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-2 text-gray-300 hover:bg-gray-800 rounded-md transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>Sair</span>
          </button>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
