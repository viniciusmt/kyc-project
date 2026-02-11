import DossierClient from './DossierClient';

// Necessário para exportação estática com rotas dinâmicas
export async function generateStaticParams() {
  // Retorna array vazio para permitir renderização dinâmica client-side
  return [];
}

export default function DossierPage() {
  return <DossierClient />;
}
