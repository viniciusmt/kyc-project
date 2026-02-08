'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/auth';
import LoginForm from '@/components/LoginForm';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Se já está autenticado, redireciona para dashboard
    if (authService.isAuthenticated()) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-primary-light flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🔍 Dossiê KYC
          </h1>
          <p className="text-blue-100">
            Sistema de Análise de Risco
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-lg shadow-2xl p-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">
            Acesso ao Sistema
          </h2>

          <LoginForm />

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center">
              Sistema Multi-tenant de KYC
            </p>
            <p className="text-xs text-gray-500 text-center mt-2">
              Autenticação segura via Supabase
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-blue-100 text-sm">
          <p>Desenvolvido por Vinicius Matsumoto</p>
          <p className="text-xs mt-1">Eng. Software & Compliance</p>
        </div>
      </div>
    </div>
  );
}
