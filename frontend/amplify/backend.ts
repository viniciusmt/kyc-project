import { defineBackend } from '@aws-amplify/backend';

/**
 * AWS Amplify Gen 2 Backend Configuration
 * ========================================
 * Configuração mínima para Next.js SSR
 */

const backend = defineBackend({
  // Backend vazio - só precisamos do hosting SSR
  // Auth, Database, etc. já estão no App Runner
});

export default backend;
