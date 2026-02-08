/**
 * TypeScript Types
 * =================
 * Tipos para toda aplicação
 */

// User & Auth
export interface User {
  id: string;
  email: string;
  company_id: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
  company_id: string;
  company_name: string;
}

// Dossier
export interface Dossier {
  id: string;
  document?: string;
  document_value?: string;
  entity_name?: string;
  risk_level?: string | null;
  created_at: string;
  report_data?: DossierReportData;
  parecer_tecnico_compliance?: string | null;
  status_decisao?: string | null;
  aprovado_por_diretoria?: boolean | null;
  justificativa_diretoria?: string | null;
  data_decisao?: string | null;
}

export interface DossierReportData {
  technical_report: any; // JSON do KYC engine
  ai_analysis: string | null;
  media_findings: string | null;
  metadata: {
    generated_at: string;
    document_type: string;
    ai_enabled: boolean;
  };
}

export interface CreateDossierRequest {
  document: string;
  enable_ai: boolean;
  cep?: string;
}

export interface BatchDossiersRequest {
  documents: string[];
  enable_ai: boolean;
}

// Dossier Create Response (backend actual payload)
export interface CreateDossierResponse {
  success: boolean;
  dossier_id: string;
  entity_name?: string;
  document?: string;
  document_type?: string;
  error?: string;
}

// Monitoring
export interface MonitoringRecord {
  id: string;
  document: string;
  document_type: 'CPF' | 'CNPJ';
  status: string;
  restriction_count: number;
  has_restrictions: boolean;
  added_date: string;
  last_check: string;
  notes?: string;
  entity_name?: string;
}

export interface MonitoringStats {
  total_monitored?: number;
  total_records?: number;
  by_type: {
    CPF: number;
    CNPJ: number;
  };
  last_update: string | null;
}

export interface MonitoringChange {
  document: string;
  detected_at?: string;
  change_description?: string;
  change_date?: string;
  description?: string;
}
