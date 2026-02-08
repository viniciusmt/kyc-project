/**
 * Auth Service
 * =============
 * Serviço de autenticação
 */

import api from './api';
import { LoginRequest, LoginResponse, User } from '@/types';

export const authService = {
  /**
   * Login
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/login', credentials);

    // Salva token e user no localStorage
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    localStorage.setItem('company_id', response.data.company_id);
    localStorage.setItem('company_name', response.data.company_name);

    return response.data;
  },

  /**
   * Logout
   */
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('company_id');
    localStorage.removeItem('company_name');
  },

  /**
   * Verifica se está autenticado
   */
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    return !!localStorage.getItem('access_token');
  },

  /**
   * Obtém usuário atual
   */
  getCurrentUser(): User | null {
    if (typeof window === 'undefined') return null;
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Obtém company_id
   */
  getCompanyId(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('company_id');
  },

  /**
   * Obtém company_name
   */
  getCompanyName(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('company_name');
  },
};
