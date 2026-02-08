/**
 * Monitoring Service
 * ==================
 * Serviço de monitoramento
 */

import api from './api';
import { MonitoringRecord, MonitoringStats, MonitoringChange } from '@/types';

const MONITORING_TIMEOUT_MS = 30000;

export const monitoringService = {
  /**
   * Adiciona documento ao monitoramento
   */
  async add(document: string, notes?: string): Promise<MonitoringRecord> {
    const response = await api.post<MonitoringRecord>('/api/monitoring/', {
      document,
      notes: notes || '',
    }, {
      timeout: MONITORING_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Lista documentos monitorados
   */
  async list(
    page: number = 1,
    pageSize: number = 10,
    docType?: 'CPF' | 'CNPJ'
  ): Promise<{ records: MonitoringRecord[]; total: number }> {
    const response = await api.get('/api/monitoring/', {
      params: {
        page,
        page_size: pageSize,
        doc_type: docType,
      },
      timeout: MONITORING_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Obtém estatísticas
   */
  async getStats(): Promise<MonitoringStats> {
    const response = await api.get<MonitoringStats>('/api/monitoring/stats', {
      timeout: MONITORING_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Atualiza documento
   */
  async update(document: string): Promise<any> {
    const response = await api.put(`/api/monitoring/${document}`, undefined, {
      timeout: MONITORING_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Atualiza todos os documentos
   */
  async updateAll(): Promise<any> {
    const response = await api.put('/api/monitoring/all', undefined, {
      timeout: MONITORING_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Remove documento
   */
  async remove(document: string): Promise<any> {
    const response = await api.delete(`/api/monitoring/${document}`, {
      timeout: MONITORING_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Obtém mudanças recentes
   */
  async getRecentChanges(days: number = 2): Promise<{ changes: MonitoringChange[]; total: number }> {
    const response = await api.get('/api/monitoring/changes/recent', {
      params: { days },
      timeout: MONITORING_TIMEOUT_MS,
    });
    return response.data;
  },
};
