export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  roles: string[];
  permissions: string[];
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Module {
  id: string;
  name: string;
  description: string;
  icon: string;
  path: string;
  requiredPermissions: string[];
}

export interface MenuItem {
  id: string;
  label: string;
  icon: string;
  path?: string;
  children?: MenuItem[];
  requiredPermissions?: string[];
}
