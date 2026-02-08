'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/auth';
import { dossiersService } from '@/services/dossiers';
import { Dossier } from '@/types';
import Header from '@/components/Header';
import DossierForm from '@/components/DossierForm';
import BatchProcessor from '@/components/BatchProcessor';
import DossiersList from '@/components/DossiersList';

export default function Dashboard() {
  const router = useRouter();
  const [dossiers, setDossiers] = useState<Dossier[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'individual' | 'batch'>('individual');

  useEffect(() => {
    // Verifica autenticação
    if (!authService.isAuthenticated()) {
      router.push('/');
      return;
    }

    loadDossiers();

    // Recarrega os dossiês quando a página é montada (ex: voltar do dossiê)
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('[Dashboard] Página visível, recarregando dossiês...');
        loadDossiers();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [router]);

  const loadDossiers = async () => {
    try {
      const data = await dossiersService.list(1, 20);
      setDossiers(data);
    } catch (error) {
      console.error('Erro ao carregar dossiês:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDossierCreated = () => {
    loadDossiers();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="bg-gradient-to-r from-primary to-primary-light rounded-lg shadow-lg p-8 mb-8 text-white">
          <h1 className="text-3xl font-bold mb-2">
            🔍 Dossiê de Análise de Risco - KYC
          </h1>
          <p className="text-blue-100">
            Sistema de Know Your Customer seguindo diretrizes COAF
          </p>
        </div>

        {/* Geração de Dossiês */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('individual')}
                className={`px-6 py-4 font-medium ${
                  activeTab === 'individual'
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                📄 Individual
              </button>
              <button
                onClick={() => setActiveTab('batch')}
                className={`px-6 py-4 font-medium ${
                  activeTab === 'batch'
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                📦 Lote (Batch)
              </button>
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'individual' ? (
              <DossierForm onSuccess={handleDossierCreated} />
            ) : (
              <BatchProcessor onSuccess={handleDossierCreated} />
            )}
          </div>
        </div>

        {/* Histórico de Dossiês */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800">
              📚 Histórico de Dossiês
            </h2>
          </div>
          <div className="p-6">
            {loading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p className="mt-2 text-gray-600">Carregando...</p>
              </div>
            ) : (
              <DossiersList dossiers={dossiers} />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
