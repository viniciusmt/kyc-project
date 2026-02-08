'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { dossiersService } from '@/services/dossiers';

interface DossierFormProps {
  onSuccess: () => void;
}

export default function DossierForm({ onSuccess }: DossierFormProps) {
  const router = useRouter();
  const [document, setDocument] = useState('');
  const [enableAi, setEnableAi] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [checkingDuplicate, setCheckingDuplicate] = useState(false);
  const [duplicate, setDuplicate] = useState<{ exists: boolean; dossier_id: string | null } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCheckingDuplicate(true);

    try {
      const digits = document.replace(/\D/g, '');
      if (digits.length !== 11 && digits.length !== 14) {
        setError('Documento deve ter 11 (CPF) ou 14 (CNPJ) dígitos');
        setCheckingDuplicate(false);
        return;
      }
      // Verifica duplicata
      const duplicateCheck = await dossiersService.checkDuplicate(document);

      if (duplicateCheck.exists && duplicateCheck.dossier_id) {
        setDuplicate(duplicateCheck);
        setCheckingDuplicate(false);
        return;
      }

      // Gera dossiê
      await generateDossier();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao verificar documento');
      setCheckingDuplicate(false);
    }
  };

  const generateDossier = async () => {
    setLoading(true);
    setError('');
    setCheckingDuplicate(false);

    try {
      const result = await dossiersService.create({
        document,
        enable_ai: enableAi,
      });

      // Redireciona para o dossiê criado
      const dossierId = (result as any).dossier_id ?? (result as any).id;
      if (dossierId) {
        router.push(`/dossier/${dossierId}`);
        onSuccess();
      } else {
        setError('Erro ao gerar dossiÃª (ID nÃ£o retornado)');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao gerar dossiê');
    } finally {
      setLoading(false);
    }
  };

  const handleForceGenerate = () => {
    setDuplicate(null);
    generateDossier();
  };

  const handleOpenExisting = () => {
    if (duplicate?.dossier_id) {
      router.push(`/dossier/${duplicate.dossier_id}`);
    }
  };

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Gerar dossiê para um único documento
      </h3>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {duplicate && (
        <div className="mb-4 bg-yellow-50 border border-yellow-200 p-4 rounded">
          <p className="text-yellow-800 font-medium mb-3">
            ⚠️ Já existe um dossiê para este documento
          </p>
          <div className="flex gap-3">
            <button
              onClick={handleOpenExisting}
              className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark"
            >
              📂 Abrir Dossiê Existente
            </button>
            <button
              onClick={handleForceGenerate}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              🔄 Gerar Novo Mesmo Assim
            </button>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            CPF ou CNPJ
          </label>
          <input
            type="text"
            value={document}
            onChange={(e) => {
              setDocument(e.target.value);
              if (duplicate) setDuplicate(null);
            }}
            placeholder="Digite apenas números ou com máscara (ex: 12345678901 ou 12.345.678/0001-90)"
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>

        <div className="flex items-center">
          <input
            id="enable-ai"
            type="checkbox"
            checked={enableAi}
            onChange={(e) => setEnableAi(e.target.checked)}
            className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
          />
          <label htmlFor="enable-ai" className="ml-2 text-sm text-gray-700">
            🤖 Ativar Análise com IA (Gemini) - Investigação de mídia negativa e análise de risco
          </label>
        </div>

        <button
          type="submit"
          disabled={loading || checkingDuplicate}
          className="w-full md:w-auto px-6 py-3 bg-primary text-white font-semibold rounded-lg hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading || checkingDuplicate ? '🔄 Gerando...' : '🔍 Gerar Dossiê'}
        </button>
      </form>
    </div>
  );
}
