'use client';

import Link from 'next/link';
import { Dossier } from '@/types';

interface DossiersListProps {
  dossiers: Dossier[];
}

export default function DossiersList({ dossiers }: DossiersListProps) {
  if (dossiers.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p className="text-lg">📋 Nenhum dossiê encontrado</p>
        <p className="text-sm mt-2">Gere seu primeiro dossiê acima</p>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getRiskBadge = (riskLevel?: string) => {
    if (!riskLevel) return null;

    const colors = {
      BAIXO: 'bg-green-100 text-green-800',
      MÉDIO: 'bg-yellow-100 text-yellow-800',
      ALTO: 'bg-red-100 text-red-800',
    };

    const emoji = {
      BAIXO: '🟢',
      MÉDIO: '🟡',
      ALTO: '🔴',
    };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${colors[riskLevel as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {emoji[riskLevel as keyof typeof emoji]} {riskLevel}
      </span>
    );
  };

  const getDecisionBadge = (statusDecisao?: string | null) => {
    const status = statusDecisao || 'PENDENTE';

    const colors = {
      APROVADO: 'bg-green-100 text-green-800',
      REPROVADO: 'bg-red-100 text-red-800',
      PENDENTE: 'bg-gray-100 text-gray-600',
    };

    const emoji = {
      APROVADO: '✓',
      REPROVADO: '✗',
      PENDENTE: '⏳',
    };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${colors[status as keyof typeof colors]}`}>
        {emoji[status as keyof typeof emoji]} {status}
      </span>
    );
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Documento
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Nome/Razão Social
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Tipo
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Risco
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Data
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Ações
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {dossiers.map((dossier) => {
            const documentValue = dossier.document || dossier.document_value || '-';
            const entityName = dossier.entity_name || '-';
            const inferredType = documentValue.replace(/\D/g, '').length === 11
              ? 'CPF'
              : documentValue.replace(/\D/g, '').length === 14
              ? 'CNPJ'
              : 'UNKNOWN';
            const docType =
              dossier.report_data?.metadata?.document_type ||
              dossier.report_data?.technical_report?.input?.type ||
              inferredType;

            return (
            <tr key={dossier.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {documentValue}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {entityName}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  docType === 'CPF'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-purple-100 text-purple-800'
                }`}>
                  {docType === 'CPF' ? '👤 CPF' : '🏢 CNPJ'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {getRiskBadge(dossier.risk_level || undefined)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {getDecisionBadge(dossier.status_decisao)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatDate(dossier.created_at)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <Link
                  href={`/dossier/${dossier.id}`}
                  className="text-primary hover:text-primary-dark"
                >
                  📄 Ver Dossiê
                </Link>
              </td>
            </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
