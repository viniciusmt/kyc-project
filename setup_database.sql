-- ============================================
-- Setup Database - Sistema KYC
-- ============================================
-- Script SQL para criar/atualizar tabelas no Supabase
--
-- Execute este script no SQL Editor do Supabase:
-- https://supabase.com/dashboard/project/hfjuotgjxchuspcfgnkv/sql
-- ============================================

-- 1. TABELA: companies (Empresas - Multi-tenant)
-- ============================================
CREATE TABLE IF NOT EXISTS public.companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    cnpj TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS para companies
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Companies são visíveis para usuários da própria empresa"
    ON public.companies FOR SELECT
    USING (id IN (
        SELECT company_id FROM public.profiles WHERE id = auth.uid()
    ));


-- 2. TABELA: profiles (Perfis de usuários)
-- ============================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES public.companies(id),
    full_name TEXT,
    role TEXT DEFAULT 'user', -- user, compliance, admin
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS para profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuários podem ver seu próprio perfil"
    ON public.profiles FOR SELECT
    USING (id = auth.uid());


-- 3. TABELA: dossiers (Dossiês de KYC)
-- ============================================
CREATE TABLE IF NOT EXISTS public.dossiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES public.companies(id),

    -- Dados do documento
    document_value TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN ('CPF', 'CNPJ')),
    entity_name TEXT NOT NULL,

    -- Análise
    risk_level TEXT CHECK (risk_level IN ('BAIXO', 'MÉDIO', 'ALTO')),
    report_data JSONB NOT NULL DEFAULT '{}',

    -- Decisão de diretoria
    status_decisao TEXT DEFAULT 'PENDENTE' CHECK (status_decisao IN ('PENDENTE', 'APROVADO', 'REPROVADO')),
    aprovado_por_diretoria BOOLEAN,
    parecer_tecnico_compliance TEXT,
    justificativa_diretoria TEXT,
    data_decisao TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_dossiers_company_id ON public.dossiers(company_id);
CREATE INDEX IF NOT EXISTS idx_dossiers_document_value ON public.dossiers(document_value);
CREATE INDEX IF NOT EXISTS idx_dossiers_created_at ON public.dossiers(created_at DESC);

-- RLS para dossiers
ALTER TABLE public.dossiers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuários veem apenas dossiês da própria empresa"
    ON public.dossiers FOR SELECT
    USING (company_id IN (
        SELECT company_id FROM public.profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Usuários podem criar dossiês para própria empresa"
    ON public.dossiers FOR INSERT
    WITH CHECK (company_id IN (
        SELECT company_id FROM public.profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Usuários podem atualizar dossiês da própria empresa"
    ON public.dossiers FOR UPDATE
    USING (company_id IN (
        SELECT company_id FROM public.profiles WHERE id = auth.uid()
    ));


-- 4. TABELA: monitoring_targets (Monitoramento Contínuo)
-- ============================================
CREATE TABLE IF NOT EXISTS public.monitoring_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES public.companies(id),

    -- Dados do documento
    document TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN ('CPF', 'CNPJ')),
    entity_name TEXT,

    -- Monitoramento
    notes TEXT,
    current_status TEXT DEFAULT 'ATIVO',
    restriction_count INTEGER DEFAULT 0,
    data_json JSONB DEFAULT '{}',
    has_changes BOOLEAN DEFAULT FALSE,

    -- Metadata
    last_check_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_monitoring_company_id ON public.monitoring_targets(company_id);
CREATE INDEX IF NOT EXISTS idx_monitoring_document ON public.monitoring_targets(document);
CREATE INDEX IF NOT EXISTS idx_monitoring_created_at ON public.monitoring_targets(created_at DESC);

-- RLS para monitoring_targets
ALTER TABLE public.monitoring_targets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuários veem apenas monitoramentos da própria empresa"
    ON public.monitoring_targets FOR SELECT
    USING (company_id IN (
        SELECT company_id FROM public.profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Usuários podem criar monitoramentos para própria empresa"
    ON public.monitoring_targets FOR INSERT
    WITH CHECK (company_id IN (
        SELECT company_id FROM public.profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Usuários podem atualizar monitoramentos da própria empresa"
    ON public.monitoring_targets FOR UPDATE
    USING (company_id IN (
        SELECT company_id FROM public.profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Usuários podem deletar monitoramentos da própria empresa"
    ON public.monitoring_targets FOR DELETE
    USING (company_id IN (
        SELECT company_id FROM public.profiles WHERE id = auth.uid()
    ));


-- 5. FUNÇÃO: Atualizar updated_at automaticamente
-- ============================================
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualizar updated_at
DROP TRIGGER IF EXISTS update_companies_updated_at ON public.companies;
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON public.companies
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_dossiers_updated_at ON public.dossiers;
CREATE TRIGGER update_dossiers_updated_at
    BEFORE UPDATE ON public.dossiers
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_monitoring_updated_at ON public.monitoring_targets;
CREATE TRIGGER update_monitoring_updated_at
    BEFORE UPDATE ON public.monitoring_targets
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


-- ============================================
-- DADOS DE EXEMPLO (OPCIONAL - para desenvolvimento)
-- ============================================

-- Cria empresa de exemplo
INSERT INTO public.companies (id, name, cnpj)
VALUES ('00000000-0000-0000-0000-000000000001', 'Empresa Demo KYC', '00000000000000')
ON CONFLICT (id) DO NOTHING;

-- Nota: Para criar usuário, use o Supabase Auth UI
-- Depois, vincule o profile manualmente:
--
-- INSERT INTO public.profiles (id, company_id, full_name, role)
-- VALUES ('<user-id-do-supabase-auth>', '00000000-0000-0000-0000-000000000001', 'Admin Demo', 'admin');


-- ============================================
-- FIM DO SCRIPT
-- ============================================
