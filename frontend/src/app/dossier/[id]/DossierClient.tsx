'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { authService } from '@/services/auth';
import { dossiersService } from '@/services/dossiers';
import { Dossier } from '@/types';
import Header from '@/components/Header';

export default function DossierPage() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;

  const [dossier, setDossier] = useState<Dossier | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [parecerTecnico, setParecerTecnico] = useState('');
  const [justificativa, setJustificativa] = useState('');
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/');
      return;
    }

    loadDossier();
  }, [id, router]);

  const loadDossier = async () => {
    try {
      const data = await dossiersService.getById(id);
      setDossier(data);
      // Carrega dados existentes de decisão
      if (data.parecer_tecnico_compliance) {
        setParecerTecnico(data.parecer_tecnico_compliance);
      }
      if (data.justificativa_diretoria) {
        setJustificativa(data.justificativa_diretoria);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar dossiê');
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (aprovado: boolean) => {
    if (!parecerTecnico.trim()) {
      alert('Por favor, preencha o Parecer Técnico antes de decidir.');
      return;
    }

    if (!confirm(`Tem certeza que deseja ${aprovado ? 'APROVAR' : 'REPROVAR'} este cliente?`)) {
      return;
    }

    setSaving(true);
    setSuccessMessage('');
    setError('');

    try {
      const result = await dossiersService.updateDossierDecision(id, {
        parecer_tecnico: parecerTecnico,
        aprovado,
        justificativa,
      });

      setSuccessMessage(`Cliente ${result.status_decisao} com sucesso!`);

      // Recarrega o dossiê para mostrar os dados atualizados
      setTimeout(() => {
        loadDossier();
        setSuccessMessage('');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao registrar decisão');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="mt-4 text-gray-600">Carregando dossiê...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error || !dossier) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <p className="text-red-800">❌ {error || 'Dossiê não encontrado'}</p>
          </div>
        </main>
      </div>
    );
  }

  const rawReportData = dossier.report_data ?? (dossier as any).data;
  const reportData =
    typeof rawReportData === 'string' ? JSON.parse(rawReportData) : rawReportData;
  const technicalReport = reportData?.technical_report;
  const derived = technicalReport?.derived;
  const sources = technicalReport?.sources;
  const brasilApi = sources?.brasilapi_cnpj?.data;
  const companySummary = derived?.company_summary || {};
  const rawDocument =
    dossier.document_value ||
    dossier.document ||
    technicalReport?.input?.document ||
    '';
  const documentDigits = rawDocument.replace(/\D/g, '');
  const inferredType = documentDigits.length === 11
    ? 'CPF'
    : documentDigits.length === 14
    ? 'CNPJ'
    : 'UNKNOWN';
  const docType =
    reportData?.metadata?.document_type ||
    technicalReport?.input?.type ||
    (dossier as any).doc_type ||
    inferredType;
  const isCPF = docType === 'CPF';
  const documentValue = rawDocument || '-';
  const displayName =
    dossier.entity_name ||
    companySummary.razao_social ||
    brasilApi?.razao_social ||
    'Nome nÃ£o disponÃ­vel';
  const cpfStatus =
    derived?.cpf_validation?.valid === true
      ? 'VÃ¡lido'
      : derived?.cpf_validation?.valid === false
      ? 'InvÃ¡lido'
      : '-';
  const endereco =
    brasilApi?.logradouro || brasilApi?.bairro || brasilApi?.municipio || brasilApi?.uf || brasilApi?.cep
      ? {
          logradouro: brasilApi?.logradouro,
          numero: brasilApi?.numero,
          complemento: brasilApi?.complemento,
          bairro: brasilApi?.bairro,
          municipio: brasilApi?.municipio,
          uf: brasilApi?.uf,
          cep: brasilApi?.cep,
        }
      : null;
  const qsaList = derived?.qsa_enriched || brasilApi?.qsa || [];
  const pepData = (reportData as any)?.pep_data || (dossier as any)?.data?.pep_data;
  const sanctions = (reportData as any)?.sanctions || (dossier as any)?.data?.sanctions;
  const aiAnalysis = reportData?.ai_analysis;
  const aiAnalysisText =
    typeof aiAnalysis === 'string'
      ? aiAnalysis
      : aiAnalysis
      ? JSON.stringify(aiAnalysis, null, 2)
      : null;
  const mediaFindings = reportData?.media_findings;
  const ceis = sources?.transparencia_ceis;
  const cnep = sources?.transparencia_cnep;
  const cepim = sources?.transparencia_cepim;
  const filterSanctions = (items: any[]) => {
    if (!documentDigits) return [];
    return items.filter((item) => {
      const candidates = [
        item?.sancionado?.codigoFormatado,
        item?.pessoa?.cnpjFormatado,
        item?.pessoa?.cpfFormatado,
        item?.cnpjSancionado,
        item?.cpfSancionado,
        item?.cnpj,
        item?.cpf,
        item?.codigoFormatado,
      ]
        .filter(Boolean)
        .map((value) => String(value).replace(/\D/g, ''));
      return candidates.includes(documentDigits);
    });
  };
  const ceisListRaw = ceis?.ok && Array.isArray(ceis.data) ? ceis.data : [];
  const cnepListRaw = cnep?.ok && Array.isArray(cnep.data) ? cnep.data : [];
  const cepimListRaw = cepim?.ok && Array.isArray(cepim.data) ? cepim.data : [];
  const ceisList = filterSanctions(ceisListRaw);
  const cnepList = filterSanctions(cnepListRaw);
  const cepimList = filterSanctions(cepimListRaw);

  const getRiskColor = (level?: string) => {
    const colors = {
      BAIXO: 'bg-green-100 text-green-800 border-green-200',
      MÉDIO: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      ALTO: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const formatDateShort = (value?: string) => {
    if (!value) return '-';
    const d = new Date(value);
    if (isNaN(d.getTime())) return value;
    return d.toLocaleDateString('pt-BR');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header do Dossiê */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {isCPF ? '👤' : '🏢'} {displayName}
              </h1>
              <p className="text-gray-600">
                <span className="font-medium">{isCPF ? 'CPF' : 'CNPJ'}:</span> {documentValue}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Gerado em {new Date(dossier.created_at).toLocaleString('pt-BR')}
              </p>
            </div>
            {dossier.risk_level && (
              <div className={`px-4 py-2 rounded-lg border-2 ${getRiskColor(dossier.risk_level)}`}>
                <p className="text-xs font-medium uppercase">Nível de Risco</p>
                <p className="text-2xl font-bold">{dossier.risk_level}</p>
              </div>
            )}
          </div>
        </div>

        {/* Dados Básicos */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800">📋 Dados Básicos</h2>
          </div>
          <div className="p-6 text-gray-900">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {isCPF ? (
                <>
                  <div>
                    <p className="text-sm text-gray-600">Nome</p>
                    <p className="font-medium">{displayName || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Data de Nascimento</p>
                    <p className="font-medium">-</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Situação Cadastral</p>
                    <p className="font-medium">{cpfStatus}</p>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <p className="text-sm text-gray-600">Razão Social</p>
                    <p className="font-medium">{companySummary.razao_social || brasilApi?.razao_social || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Nome Fantasia</p>
                    <p className="font-medium">
                      {companySummary.nome_fantasia || brasilApi?.nome_fantasia || brasilApi?.fantasia || '-'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Situação Cadastral</p>
                    <p className="font-medium">{companySummary.situacao_cadastral || brasilApi?.descricao_situacao_cadastral || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Data de Abertura</p>
                    <p className="font-medium">
                      {companySummary.data_abertura ||
                        (companySummary as any).data_inicio_atividade ||
                        (companySummary as any).abertura ||
                        brasilApi?.data_inicio_atividade ||
                        brasilApi?.data_abertura ||
                        brasilApi?.abertura ||
                        '-'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Capital Social</p>
                    <p className="font-medium">{brasilApi?.capital_social || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Porte</p>
                    <p className="font-medium">{brasilApi?.porte || '-'}</p>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Endereço */}
        {endereco && (
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">📍 Endereço</h2>
            </div>
            <div className="p-6">
              <p className="text-gray-700">
                {endereco.logradouro}, {endereco.numero}
                {endereco.complemento && ` - ${endereco.complemento}`}
              </p>
              <p className="text-gray-700">
                {endereco.bairro} - {endereco.municipio}/{endereco.uf}
              </p>
              <p className="text-gray-700">CEP: {endereco.cep}</p>
            </div>
          </div>
        )}

        {/* Sócios/QSA (CNPJ) */}
        {!isCPF && qsaList && qsaList.length > 0 && (
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">👥 Quadro Societário</h2>
            </div>
            <div className="p-6 text-gray-900">
              <details className="group">
                <summary className="cursor-pointer list-none flex items-center justify-between">
                  <span className="font-medium text-gray-800">
                    {qsaList.length} participante(s)
                  </span>
                  <span className="text-sm text-gray-500 group-open:rotate-180 transition-transform">▾</span>
                </summary>
                <div className="mt-4 space-y-4">
                  {qsaList.map((socio: any, index: number) => (
                    <div key={index} className="border-l-4 border-primary pl-4">
                      <p className="font-medium text-gray-900">
                        {socio.nome || socio.nome_socio || socio.razao_social || 'Sócio'}
                      </p>
                      <p className="text-sm text-gray-600">
                        {socio.qualificacao || socio.qualificacao_socio || '-'}
                      </p>
                      {(socio.cpf_cnpj || socio.cnpj_cpf_do_socio) && (
                        <p className="text-sm text-gray-500">
                          CPF/CNPJ: {socio.cpf_cnpj || socio.cnpj_cpf_do_socio}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </details>
            </div>
          </div>
        )}

        {/* PEP */}
        {pepData && (
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">
                🎖️ Pessoa Politicamente Exposta (PEP)
              </h2>
            </div>
            <div className="p-6">
              {pepData.is_pep ? (
                <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
                  <p className="font-medium text-yellow-800">⚠️ Identificado como PEP</p>
                  {pepData.details && (
                    <div className="mt-2 text-sm text-yellow-700">
                      <pre className="whitespace-pre-wrap">{JSON.stringify(pepData.details, null, 2)}</pre>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-green-600">✓ Não identificado como PEP</p>
              )}
            </div>
          </div>
        )}

        {/* Sanções */}
        {(sanctions || ceis || cnep || cepim) && (
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">⚖️ Sanções e Restrições</h2>
            </div>
            <div className="p-6 space-y-4 text-gray-900">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-600">CEIS</p>
                  <p className="text-2xl font-bold text-gray-900">{ceisList.length}</p>
                  {!ceis?.ok && ceis && (
                    <p className="text-xs text-red-600 mt-1">Falha: {ceis.error || 'erro'}</p>
                  )}
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-600">CNEP</p>
                  <p className="text-2xl font-bold text-gray-900">{cnepList.length}</p>
                  {!cnep?.ok && cnep && (
                    <p className="text-xs text-red-600 mt-1">Falha: {cnep.error || 'erro'}</p>
                  )}
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-600">CEPIM</p>
                  <p className="text-2xl font-bold text-gray-900">{cepimList.length}</p>
                  {!cepim?.ok && cepim && (
                    <p className="text-xs text-red-600 mt-1">Falha: {cepim.error || 'erro'}</p>
                  )}
                </div>
              </div>

              {(ceisList.length + cnepList.length + cepimList.length) === 0 && (
                <p className="text-green-600">✓ Nenhuma sanção encontrada</p>
              )}

              {(ceisList.length > 0 || cnepList.length > 0 || cepimList.length > 0) && (
                <details className="group">
                  <summary className="cursor-pointer list-none flex items-center justify-between">
                    <span className="font-medium text-gray-800">Detalhes</span>
                    <span className="text-sm text-gray-500 group-open:rotate-180 transition-transform">▾</span>
                  </summary>
                  <div className="mt-4 space-y-6 text-sm text-gray-700">
                    {[{ label: 'CEIS', list: ceisList }, { label: 'CNEP', list: cnepList }, { label: 'CEPIM', list: cepimList }]
                      .filter((group) => group.list.length > 0)
                      .map((group) => (
                        <div key={group.label}>
                          <p className="font-semibold text-gray-800 mb-2">{group.label} ({group.list.length})</p>
                          <div className="space-y-3">
                            {group.list.slice(0, 5).map((item: any, index: number) => {
                              const name =
                                item?.sancionado?.nome ||
                                item?.pessoa?.nome ||
                                item?.pessoa?.razaoSocialReceita ||
                                'Sancionado';
                              const code =
                                item?.sancionado?.codigoFormatado ||
                                item?.pessoa?.cnpjFormatado ||
                                item?.pessoa?.cpfFormatado ||
                                '-';
                              const tipo = item?.tipoSancao?.descricaoResumida || item?.tipoSancao?.descricaoPortal || '-';
                              const orgao = item?.orgaoSancionador?.nome || item?.fonteSancao?.nomeExibicao || '-';
                              const inicio = formatDateShort(item?.dataInicioSancao);
                              const fim = formatDateShort(item?.dataFimSancao);
                              return (
                                <div key={index} className="border border-gray-200 rounded-lg p-3">
                                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-2">
                                    <div>
                                      <p className="font-medium text-gray-900">{name}</p>
                                      <p className="text-xs text-gray-500">{code}</p>
                                    </div>
                                    <div className="text-xs text-gray-600 md:text-right">
                                      <p>{orgao}</p>
                                      <p>{inicio} → {fim}</p>
                                    </div>
                                  </div>
                                  <p className="text-sm text-gray-700 mt-2">{tipo}</p>
                                </div>
                              );
                            })}
                          </div>
                          {group.list.length > 5 && (
                            <p className="text-xs text-gray-500 mt-2">Mostrando 5 de {group.list.length}.</p>
                          )}
                        </div>
                      ))}
                  </div>
                </details>
              )}
            </div>
          </div>
        )}

        {/* Análise de Risco com IA */}
        {aiAnalysisText && (
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">🤖 Análise de Risco com IA</h2>
            </div>
            <div className="p-6 text-gray-900">
              <div className={`p-4 rounded-lg border-2 mb-4 ${getRiskColor(dossier.risk_level || undefined)}`}>
                <p className="font-bold text-lg mb-2">
                  Nível de Risco: {dossier.risk_level || '-'}
                </p>
                <p className="text-sm whitespace-pre-wrap">{aiAnalysisText}</p>
              </div>

              {mediaFindings && (
                <div className="mt-4">
                  <h3 className="font-semibold text-gray-800 mb-2">📰 Mídia Negativa</h3>
                  <div className="space-y-2">
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">{mediaFindings}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Governança e Decisão */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800">⚖️ Governança e Decisão</h2>
          </div>
          <div className="p-6">
            {/* Mensagens de feedback */}
            {successMessage && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <p className="text-green-800 font-medium">✓ {successMessage}</p>
              </div>
            )}

            {/* Status da decisão existente */}
            {dossier.status_decisao && dossier.status_decisao !== 'PENDENTE' && (
              <div className={`rounded-lg p-4 mb-4 border-2 ${
                dossier.status_decisao === 'APROVADO'
                  ? 'bg-green-50 border-green-200'
                  : 'bg-red-50 border-red-200'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <p className={`text-lg font-bold ${
                    dossier.status_decisao === 'APROVADO' ? 'text-green-800' : 'text-red-800'
                  }`}>
                    {dossier.status_decisao === 'APROVADO' ? '✓ Cliente Aprovado' : '✗ Cliente Reprovado'}
                  </p>
                  {dossier.data_decisao && (
                    <p className="text-sm text-gray-600">
                      {new Date(dossier.data_decisao).toLocaleString('pt-BR')}
                    </p>
                  )}
                </div>
              </div>
            )}

            <div className="space-y-4">
              {/* Parecer Técnico */}
              <div>
                <label htmlFor="parecer" className="block text-sm font-medium text-gray-700 mb-2">
                  Parecer Técnico do Compliance
                </label>
                <textarea
                  id="parecer"
                  rows={4}
                  value={parecerTecnico}
                  onChange={(e) => setParecerTecnico(e.target.value)}
                  disabled={!!dossier.status_decisao && dossier.status_decisao !== 'PENDENTE'}
                  className={`w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    dossier.status_decisao && dossier.status_decisao !== 'PENDENTE'
                      ? 'bg-gray-50 text-gray-700 cursor-not-allowed'
                      : 'bg-white text-gray-900'
                  }`}
                  placeholder="Digite o parecer técnico detalhado do compliance sobre o dossiê..."
                />
              </div>

              {/* Justificativa da Diretoria */}
              <div>
                <label htmlFor="justificativa" className="block text-sm font-medium text-gray-700 mb-2">
                  Justificativa da Diretoria <span className="text-gray-400 text-xs">(opcional)</span>
                </label>
                <textarea
                  id="justificativa"
                  rows={4}
                  value={justificativa}
                  onChange={(e) => setJustificativa(e.target.value)}
                  disabled={!!dossier.status_decisao && dossier.status_decisao !== 'PENDENTE'}
                  className={`w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    dossier.status_decisao && dossier.status_decisao !== 'PENDENTE'
                      ? 'bg-gray-50 text-gray-700 cursor-not-allowed'
                      : 'bg-white text-gray-900'
                  }`}
                  placeholder="Digite a justificativa da diretoria para a decisão final (opcional)..."
                />
              </div>

              {/* Botões de Decisão */}
              {(!dossier.status_decisao || dossier.status_decisao === 'PENDENTE') && (
                <div className="flex gap-4 mt-6">
                  <button
                    onClick={() => handleDecision(true)}
                    disabled={saving}
                    className={`flex-1 px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors ${
                      saving ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    {saving ? 'Salvando...' : '✓ Aprovar Cliente'}
                  </button>
                  <button
                    onClick={() => handleDecision(false)}
                    disabled={saving}
                    className={`flex-1 px-6 py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors ${
                      saving ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    {saving ? 'Salvando...' : '✗ Reprovar Cliente'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Botão Voltar */}
        <div className="text-center">
          <button
            onClick={() => {
              // Força recarregamento do dashboard ao voltar
              router.push('/dashboard');
              router.refresh();
            }}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            ← Voltar ao Dashboard
          </button>
        </div>
      </main>
    </div>
  );
}
