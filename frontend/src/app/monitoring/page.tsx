'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/auth';
import { monitoringService } from '@/services/monitoring';
import { MonitoringRecord, MonitoringStats, MonitoringChange } from '@/types';
import Header from '@/components/Header';

export default function MonitoringPage() {
  const router = useRouter();
  const [records, setRecords] = useState<MonitoringRecord[]>([]);
  const [stats, setStats] = useState<MonitoringStats | null>(null);
  const [recentChanges, setRecentChanges] = useState<MonitoringChange[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [newDocument, setNewDocument] = useState('');
  const [newNotes, setNewNotes] = useState('');
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/');
      return;
    }

    loadData();
  }, [router]);

  const loadData = async () => {
    try {
      const [recordsData, statsData] = await Promise.all([
        monitoringService.list(1, 50).catch(() => ({ records: [], total: 0 })),
        monitoringService.getStats().catch(() => ({
          total_monitored: 0,
          by_type: { CPF: 0, CNPJ: 0 },
          last_update: null
        })),
      ]);

      setRecords(recordsData.records || []);
      const totalRecords = (statsData as any).total_records ?? (statsData as any).total_monitored ?? 0;
      const byType = (statsData as any).by_type ?? {
        CPF: (statsData as any).total_cpf ?? 0,
        CNPJ: (statsData as any).total_cnpj ?? 0,
      };
      const lastUpdateFromRecords = (recordsData.records || [])
        .map((r: any) => r.last_check || r.added_date)
        .filter(Boolean)
        .sort()
        .slice(-1)[0] || null;
      setStats({
        total_monitored: totalRecords,
        by_type: byType,
        last_update: (statsData as any).last_update ?? lastUpdateFromRecords ?? null,
      });
      setError(''); // Limpa erro anterior se sucesso
    } catch (error) {
      console.error('Erro ao carregar dados de monitoramento:', error);
      setError('Erro ao carregar dados de monitoramento');
    } finally {
      setLoading(false);
    }

    // Carrega mudanças recentes em segundo plano (não bloqueia a tela)
    try {
      const changesData = await monitoringService.getRecentChanges(7).catch(() => ({ changes: [] }));
      const normalizedChanges = (changesData.changes || []).map((c: any) => ({
        document: c.document,
        change_description: c.change_description || c.description || '-',
        detected_at: c.detected_at || c.change_date || null,
      }));
      setRecentChanges(normalizedChanges);
    } catch {
      // silencioso
    }
  };

  const handleAddMonitoring = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setAdding(true);

    try {
      await monitoringService.add(newDocument, newNotes);
      setSuccess('Documento adicionado ao monitoramento!');
      setNewDocument('');
      setNewNotes('');
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao adicionar ao monitoramento');
    } finally {
      setAdding(false);
    }
  };

  const handleUpdateAll = async () => {
    setError('');
    setSuccess('');
    setUpdating(true);

    try {
      await monitoringService.updateAll();
      setSuccess('Todos os registros foram atualizados!');
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao atualizar registros');
    } finally {
      setUpdating(false);
    }
  };

  const handleUpdateSingle = async (document: string) => {
    setError('');
    setSuccess('');

    try {
      await monitoringService.update(document);
      setSuccess(`Registro ${document} atualizado!`);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao atualizar registro');
    }
  };

  const handleRemove = async (document: string) => {
    if (!confirm(`Remover ${document} do monitoramento?`)) return;

    setError('');
    setSuccess('');

    try {
      await monitoringService.remove(document);
      setSuccess(`Registro ${document} removido!`);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao remover registro');
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '-';
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '-';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="mt-4 text-gray-600">Carregando monitoramento...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary to-primary-light rounded-lg shadow-lg p-8 mb-8 text-white">
          <h1 className="text-3xl font-bold mb-2">📊 Monitoramento Contínuo</h1>
          <p className="text-blue-100">
            Acompanhamento automático de alterações cadastrais e de risco
          </p>
        </div>

        {/* Mensagens */}
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        )}

        {/* Estatísticas */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600">Total Monitorado</p>
              <p className="text-3xl font-bold text-primary">{stats.total_monitored}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600">CPFs</p>
              <p className="text-3xl font-bold text-blue-600">{stats.by_type?.CPF || 0}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600">CNPJs</p>
              <p className="text-3xl font-bold text-purple-600">{stats.by_type?.CNPJ || 0}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600">Última Atualização</p>
              <p className="text-sm font-medium text-gray-800">
                {stats.last_update ? formatDate(stats.last_update) : '-'}
              </p>
            </div>
          </div>
        )}

        {/* Adicionar ao Monitoramento */}
        <div className="bg-white rounded-lg shadow mb-8 p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">➕ Adicionar ao Monitoramento</h2>
          <form onSubmit={handleAddMonitoring} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  CPF ou CNPJ
                </label>
                <input
                  type="text"
                  value={newDocument}
                  onChange={(e) => setNewDocument(e.target.value)}
                  placeholder="Digite o documento"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Observações (opcional)
                </label>
                <input
                  type="text"
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  placeholder="Notas"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={adding}
              className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50"
            >
              {adding ? 'Adicionando...' : '➕ Adicionar'}
            </button>
          </form>
        </div>

        {/* Mudanças Recentes */}
        {recentChanges.length > 0 && (
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-800">🔔 Mudanças Recentes (7 dias)</h2>
              <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">
                {recentChanges.length} mudança(s)
              </span>
            </div>
            <div className="p-6">
              <div className="space-y-4">
            {recentChanges.map((change, index) => (
              <div key={index} className="border-l-4 border-red-500 bg-red-50 p-4 rounded">
                <p className="font-medium text-gray-900">{change.document}</p>
                <p className="text-sm text-gray-600 mt-1">{change.change_description}</p>
                <p className="text-xs text-gray-500 mt-2">
                  {formatDate(change.detected_at || '')}
                </p>
              </div>
            ))}
              </div>
            </div>
          </div>
        )}

        {/* Lista de Registros Monitorados */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-800">📋 Registros Monitorados</h2>
            <button
              onClick={handleUpdateAll}
              disabled={updating}
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50"
            >
              {updating ? '🔄 Atualizando...' : '🔄 Atualizar Todos'}
            </button>
          </div>
          <div className="p-6">
            {records.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>📭 Nenhum documento em monitoramento</p>
                <p className="text-sm mt-2">Adicione documentos acima para começar</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Entidade
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Documento
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Tipo
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Última Verificação
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Observações
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Ações
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {records.map((record) => (
                      <tr key={record.document} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {record.entity_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {record.document}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            record.document_type === 'CPF'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-purple-100 text-purple-800'
                          }`}>
                            {record.document_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              ['ATIVO', 'ATIVA', 'REGULAR'].includes((record.status || '').toUpperCase())
                                ? 'bg-green-100 text-green-800'
                                : ['INATIVO', 'INATIVA', 'IRREGULAR'].includes((record.status || '').toUpperCase())
                                ? 'bg-red-100 text-red-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {record.status || '-'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {record.last_check ? formatDate(record.last_check) : '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {record.notes || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                          <button
                            onClick={() => handleUpdateSingle(record.document)}
                            className="text-primary hover:text-primary-dark"
                          >
                            🔄 Atualizar
                          </button>
                          <button
                            onClick={() => handleRemove(record.document)}
                            className="text-red-600 hover:text-red-800"
                          >
                            🗑️ Remover
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
