'use client';

import { useState } from 'react';
import { dossiersService } from '@/services/dossiers';

interface BatchProcessorProps {
  onSuccess: () => void;
}

export default function BatchProcessor({ onSuccess }: BatchProcessorProps) {
  const [input, setInput] = useState('');
  const [enableAi, setEnableAi] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState('');

  const parseDocuments = (text: string): string[] => {
    // Remove espaços, quebras de linha extras
    const cleaned = text.trim().replace(/\s+/g, ' ');

    // Separa por ; ou quebra de linha
    const docs = cleaned
      .split(/[;\n]/)
      .map(doc => doc.trim())
      .filter(doc => doc.length > 0);

    return docs;
  };

  const validDocuments = parseDocuments(input);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResults(null);

    if (validDocuments.length === 0) {
      setError('Nenhum documento válido encontrado');
      return;
    }

    setProcessing(true);

    try {
      const result = await dossiersService.processBatch({
        documents: validDocuments,
        enable_ai: enableAi,
      });

      setResults(result);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao processar lote');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Gerar dossiês em lote
      </h3>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {results && (
        <div className="mb-4 bg-green-50 border border-green-200 p-4 rounded">
          <p className="text-green-800 font-medium mb-2">
            ✅ Lote processado com sucesso!
          </p>
          <div className="text-sm text-green-700">
            <p>Total processados: {results.total_processed}</p>
            <p>Sucessos: {results.successful}</p>
            <p>Falhas: {results.failed}</p>
            {results.errors && results.errors.length > 0 && (
              <div className="mt-2">
                <p className="font-medium">Erros:</p>
                <ul className="list-disc list-inside">
                  {results.errors.map((error: any, index: number) => (
                    <li key={index}>
                      {error.document}: {error.error}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Documentos (CPF ou CNPJ)
          </label>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Cole os documentos aqui (separados por ; ou quebra de linha)&#10;&#10;Exemplo:&#10;47.960.950/0001-21&#10;07.526.557/0001-00&#10;12345678901"
            rows={8}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent font-mono text-sm"
          />
          <p className="mt-2 text-sm text-gray-600">
            {validDocuments.length > 0 ? (
              <span className="text-green-600 font-medium">
                ✓ {validDocuments.length} documento(s) encontrado(s)
              </span>
            ) : (
              <span className="text-gray-500">
                Aguardando documentos...
              </span>
            )}
          </p>
        </div>

        <div className="flex items-center">
          <input
            id="batch-enable-ai"
            type="checkbox"
            checked={enableAi}
            onChange={(e) => setEnableAi(e.target.checked)}
            className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
          />
          <label htmlFor="batch-enable-ai" className="ml-2 text-sm text-gray-700">
            🤖 Ativar Análise com IA (Gemini) - Investigação de mídia negativa e análise de risco
          </label>
        </div>

        <button
          type="submit"
          disabled={processing || validDocuments.length === 0}
          className="w-full md:w-auto px-6 py-3 bg-primary text-white font-semibold rounded-lg hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {processing ? (
            <span>🔄 Processando {validDocuments.length} documentos...</span>
          ) : (
            <span>📦 Processar Lote ({validDocuments.length})</span>
          )}
        </button>
      </form>
    </div>
  );
}
