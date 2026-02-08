/**
 * Dossiers Service
 * =================
 * Serviço de dossiês
 */

import api from './api';
import { Dossier, CreateDossierRequest, BatchDossiersRequest, CreateDossierResponse } from '@/types';

const DOSSIER_TIMEOUT_MS = 30000;

export const dossiersService = {
  /**
   * Cria um novo dossiê
   */
  async create(data: CreateDossierRequest): Promise<CreateDossierResponse> {
    const response = await api.post<CreateDossierResponse>('/api/dossiers/', data, {
      timeout: DOSSIER_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Lista dossiês
   */
  async list(page: number = 1, pageSize: number = 20): Promise<Dossier[]> {
    const response = await api.get<Dossier[]>('/api/dossiers/', {
      params: { page, page_size: pageSize },
      timeout: DOSSIER_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Obtém dossiê por ID
   */
  async getById(dossierId: string): Promise<Dossier> {
    const response = await api.get<Dossier>(`/api/dossiers/${dossierId}`, {
      timeout: DOSSIER_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Verifica duplicata
   */
  async checkDuplicate(document: string): Promise<{ exists: boolean; dossier_id: string | null }> {
    const response = await api.get(`/api/dossiers/check-duplicate`, {
      params: { document },
      timeout: DOSSIER_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Processa batch de dossiês
   */
  async processBatch(data: BatchDossiersRequest): Promise<{ message: string; total: number; status: string }> {
    const response = await api.post('/api/dossiers/batch', data, {
      timeout: DOSSIER_TIMEOUT_MS,
    });
    return response.data;
  },

  /**
   * Atualiza a decisão de diretoria sobre o dossiê
   */
  async updateDossierDecision(
    dossierId: string,
    data: {
      parecer_tecnico: string;
      aprovado: boolean;
      justificativa: string;
    }
  ): Promise<{ success: boolean; message: string; status_decisao: string }> {
    const response = await api.put(`/api/dossiers/${dossierId}/decide`, data, {
      timeout: DOSSIER_TIMEOUT_MS,
    });
    return response.data;
  },
};
