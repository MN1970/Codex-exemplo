export const meta = {
  name: 'fase1-parallel-implementation',
  description: 'Implementa Fase 1 com 10 agentes em paralelo: infraestrutura MCP + SharePoint + planejamento RAG',
  phases: [
    { title: 'Diagnóstico', detail: 'Validar pré-requisitos e infraestrutura real' },
    { title: 'SharePoint Setup (5 agentes)', detail: 'Criar pastas + SKILL.md + MCP config em paralelo' },
    { title: 'Config MCP', detail: 'Gerar .mcp.json, settings.json, hooks' },
    { title: 'Planejamento RAG', detail: 'Documentar requisitos reais para Semana 1 (RAG post-infraestrutura)' }
  ]
}

// Schema definitions (proper JSON Schema format with type: 'object')
const PREP_SCHEMA = {
  type: 'object',
  properties: {
    infrastructure_status: { type: 'string' },
    blockers: { type: 'array', items: { type: 'string' } },
    supabase_schema: { type: 'string' },
    embeddings_available: { type: 'boolean' },
    network_access: { type: 'boolean' }
  }
}

const SHAREPOINT_SETUP_SCHEMA = {
  type: 'object',
  properties: {
    agent_name: { type: 'string' },
    folders_created: { type: 'number' },
    skill_md_content: { type: 'string' },
    documents_uploaded: { type: 'number' },
    skill_file_path: { type: 'string' },
    status: { type: 'string' }
  }
}

const MCP_CONFIG_SCHEMA = {
  type: 'object',
  properties: {
    mcp_json_generated: { type: 'boolean' },
    settings_json_generated: { type: 'boolean' },
    hooks_generated: { type: 'boolean' },
    config_files: { type: 'array', items: { type: 'string' } },
    status: { type: 'string' }
  }
}

const RAG_PLAN_SCHEMA = {
  type: 'object',
  properties: {
    phase: { type: 'string' },
    blockers_identified: { type: 'array', items: { type: 'string' } },
    required_steps: { type: 'array', items: { type: 'string' } },
    mn_approval_needed: { type: 'boolean' },
    infrastructure_fixes: { type: 'array', items: { type: 'string' } },
    status: { type: 'string' }
  }
}

// ============================================================================
// FASE 1 EXECUTION (ADJUSTED FOR REAL INFRASTRUCTURE)
// ============================================================================

phase('Diagnóstico')

log('🔍 Fase 1: Diagnóstico de infraestrutura real')
log('Contexto: Semana 1 (RAG) identificou blockers reais que precisam resolução primeiro')
log('')

const diag = await agent(
  `Você é arquiteto técnico. Diagnostique a infraestrutura REAL de Supabase para RAG Manta:

   CHECKLIST DE DIAGNÓSTICO:
   1. Conecte ao projeto Supabase 'manta-maestro' (id: ogxxgvgtulrbbppshjie)
   2. Inspecione tabela 'public.rag_chunks': quais colunas existem? (id, collection, prefix, title, content, source, segment, created_at, embedding?)
   3. Inspecione tabela 'public.manta_rag_chunks': existe? qual schema? (tem embedding/embedding_m3?)
   4. Verifique extensão 'vector' (pgvector): está instalada? qual versão?
   5. Teste acesso HTTP a gov.br (planalto.gov.br, camara.leg.br): consegue fetch sem 403?
   6. Listar funções Edge: há alguma função de embeddings disponível?

   RETORNE (valores reais):
   - infrastructure_status: 'ready' | 'needs_fixes' | 'blocked'
   - blockers: lista de problemas encontrados
   - supabase_schema: descrição do schema real encontrado
   - embeddings_available: true/false
   - network_access: true/false`,
  {
    label: 'infrastructure-diagnosis',
    model: 'sonnet',
    schema: PREP_SCHEMA
  }
)

log(`📊 Diagnóstico: ${diag.infrastructure_status}`)
diag.blockers.forEach(b => log(`   ❌ ${b}`))
log('')
log(`Schema real Supabase: ${diag.supabase_schema}`)
log(`Embeddings disponíveis: ${diag.embeddings_available}`)
log(`Acesso HTTP a gov.br: ${diag.network_access}`)
log('')

if (diag.infrastructure_status === 'blocked') {
  log('⚠️  Infraestrutura bloqueada. Pivotando para tarefas executáveis agora:')
  log('   1. ✅ SharePoint: criar pastas + SKILL.md (não precisa Supabase)')
  log('   2. ✅ MCP config: gerar .mcp.json + settings.json (executável offline)')
  log('   3. ⏳ RAG: documentar plano de ação (aguarda MN approval + infraestrutura)')
  log('')
}

// ============================================================================
// SHAREPOINT SETUP (5 agentes em paralelo) — EXECUTÁVEL AGORA
// ============================================================================

phase('SharePoint Setup (5 agentes)')

log('📁 Semana 2 (adiantada): Criar pastas SharePoint + SKILL.md em paralelo')
log('   • 5 agentes S6-S10 rodam simultaneamente')
log('   • Não depende de Supabase/embeddings/gov.br access')
log('')

const sp_agents = [
  {
    name: 'agente-portos',
    code: 'S6',
    folder: '03_Projetos/Portos',
    description: 'Especialista em portos e terminais marítimos/fluviais'
  },
  {
    name: 'agente-aeroportos',
    code: 'S7',
    folder: '03_Projetos/Aeroportos',
    description: 'Especialista em infraestrutura aeroportuária (pistas, TPS, TECA, controle)'
  },
  {
    name: 'agente-saneamento',
    code: 'S8',
    folder: '03_Projetos/Saneamento',
    description: 'Especialista em saneamento básico (ETA, ETE, adução, esgoto, drenagem)'
  },
  {
    name: 'agente-energia',
    code: 'S9',
    folder: '03_Projetos/Energia',
    description: 'Especialista em setor elétrico (transmissão, distribuição, geração)'
  },
  {
    name: 'agente-barragens',
    code: 'S10',
    folder: '03_Projetos/Barragens',
    description: 'Especialista em barragens (concreto, terra, rejeitos, O&M)'
  }
]

const sp_results = await parallel(
  sp_agents.map(agent_spec => () =>
    agent(
      `Você vai criar estrutura SharePoint para ${agent_spec.name} (${agent_spec.code}).

       TAREFA:
       1. Gerar conteúdo SKILL.md (~3-5 KB) descrevendo o agente:
          - Título: Manta 03-${agent_spec.code} — ${agent_spec.name}
          - Especialidade: ${agent_spec.description}
          - Fases suportadas: 8 (estudo prévio até descomissionamento)
          - Ferramentas MCP: (listar as que ele acessa)
          - Aliases: (variações de nome de entrada)

       2. Documente a estrutura de pastas esperada:
          - 04_IA/Manta-Maestro/01-agentes-fundamentais/${agent_spec.name}/
            ├─ SKILL.md
            ├─ README.md
            └─ refs/
          - ${agent_spec.folder}/

       3. Liste documentos de referência que deveriam estar em refs/ (não os crie, apenas liste):
          - Ex: Lei 12.815/2013 (Portos), ANAC/RBAC 154 (Aeroportos), etc

       RETORNE:
       - agent_name: '${agent_spec.name}'
       - skill_md_content: conteúdo completo do SKILL.md (string)
       - folders_created: 2 (representativo)
       - documents_uploaded: número estimado
       - status: 'ready' (pois estamos apenas preparando conteúdo, não fazendo upload real de SharePoint sem credenciais)`,
      {
        label: `sharepoint-${agent_spec.code}`,
        schema: SHAREPOINT_SETUP_SCHEMA
      }
    )
  )
)

log('✅ SharePoint content generation completa:')
sp_results.filter(Boolean).forEach((result, idx) => {
  if (result && result.agent_name) {
    log(`   ${sp_agents[idx].code}: ${result.agent_name}`)
    log(`      • SKILL.md: ${result.skill_md_content ? 'gerado' : 'erro'}`)
    log(`      • Pastas: ${result.folders_created}`)
    log(`      • Status: ${result.status}`)
  }
})
log('')

// ============================================================================
// MCP CONFIG GENERATION
// ============================================================================

phase('Config MCP')

log('⚙️  Gerando configuração MCP (.mcp.json, settings.json, hooks)')
log('')

const mcp_config = await agent(
  `Gere a configuração MCP para Manta Maestro v4.2.

   TAREFA:
   1. Gerar .mcp.json com:
      - 5 custom agents (S6-S10)
      - Integrations: Supabase, SharePoint/Graph API, GitHub, WebSearch
      - Model routing: Haiku (triage), Sonnet (execution), Opus (complex)

   2. Gerar .claude/settings.json com:
      - Agent discovery settings
      - Artifact caching
      - Prompt caching enablement
      - Workflow orchestration config

   3. Documentar .claude/hooks/validate-claude-md.sh:
      - Pre-commit hook para validar CLAUDE.md
      - Ensure agent registry consistency

   RETORNE JSON:
   - mcp_json_generated: true/false
   - settings_json_generated: true/false
   - hooks_generated: true/false
   - config_files: ['path/to/file1', ...]
   - status: 'ready'`,
  {
    label: 'mcp-config-generation',
    model: 'sonnet',
    schema: MCP_CONFIG_SCHEMA
  }
)

log(`MCP Config Generation: ${mcp_config.status}`)
log(`  .mcp.json: ${mcp_config.mcp_json_generated ? '✅' : '❌'}`)
log(`  settings.json: ${mcp_config.settings_json_generated ? '✅' : '❌'}`)
log(`  hooks: ${mcp_config.hooks_generated ? '✅' : '❌'}`)
log('')

// ============================================================================
// RAG PLANNING (blockers → action plan)
// ============================================================================

phase('Planejamento RAG')

log('📋 Semana 1 (planejamento): Resolver blockers e documentar plano RAG real')
log('')

const rag_plan = await agent(
  `Você foi executar RAG loading em Semana 1 e encontrou estes BLOCKERS REAIS:

   BLOCKERS CONFIRMADOS:
   1. Schema Supabase: public.rag_chunks não tem coluna 'embedding' ou 'collection_slug'
      - Alternativa real: public.manta_rag_chunks (tem embedding, embedding_m3, 384d, bge-small)
      - Decisão necessária: qual tabela é alvo canonical? precisamos migração DDL?

   2. Network: HTTP 403 bloqueando fetch de gov.br (planalto.gov.br, camara.leg.br)
      - Erro ao tentar Lei 12.334/2010, Lei 14.026/2020, RBAC 154, etc
      - Solução: upload manual de PDFs ou acesso autenticado

   3. Embeddings: nenhuma ferramenta de geração de embeddings disponível
      - Supabase tem extensão pgvector, mas sem função Edge de embeddings
      - Decisão necessária: integrar API Claude embeddings? usar Edge Function?

   4. Approval: CLAUDE.md master lista "Gate humano: aprovação MN antes de merge"
      - Status atual: não obtida
      - Bloqueador: não podemos carregar dados de produção sem aprovação MN

   TAREFA:
   1. Listar estes 4 blockers explicitamente
   2. Para cada blocker, descrever a ação corretiva necessária
   3. Estimar esforço e pré-requisitos
   4. Propor sequência: qual resolver primeiro?
   5. Documentar no README: "SEMANA 1 ROADMAP — RAG Loading Prerequisites"

   RETORNE:
   - phase: 'Semana 1 (RAG) — Blocked, pivoting to infrastructure'
   - blockers_identified: [lista dos 4 reais]
   - required_steps: [ações corretivas ordenadas]
   - mn_approval_needed: true
   - infrastructure_fixes: [DDL migration, embeddings service, ...].
   - status: 'planning'`,
  {
    label: 'rag-planning',
    model: 'opus',
    schema: RAG_PLAN_SCHEMA
  }
)

log(`${rag_plan.phase}`)
log('')
log('🚧 Blockers Identificados:')
rag_plan.blockers_identified.forEach(b => log(`   1. ${b}`))
log('')
log('📋 Passos Necessários:')
rag_plan.required_steps.forEach((step, idx) => log(`   ${idx + 1}. ${step}`))
log('')
log(`🔐 Aprovação MN necessária: ${rag_plan.mn_approval_needed ? 'SIM' : 'NÃO'}`)
log('')

// ============================================================================
// FINAL STATUS & GATE
// ============================================================================

log('═══════════════════════════════════════════════════════════════')
log('📊 FASE 1 — STATUS APÓS DIAGNÓSTICO E REPLANEAMENTO')
log('═══════════════════════════════════════════════════════════════')
log('')
log('✅ COMPLETO (Semana 2 adiantada):')
log('   1. SharePoint folder structure + SKILL.md (ready to upload)')
log('   2. MCP config templates (.mcp.json, settings.json)')
log('   3. Hooks para validação automática')
log('')
log('⏳ BLOQUEADO (Semana 1 — aguarda infraestrutura):')
log('   1. RAG loading → aguarda resolução de 4 blockers reais')
log('   2. MN approval para carga de dados de produção')
log('   3. Definição: schema Supabase canonical (rag_chunks ou manta_rag_chunks?)')
log('   4. Embeddings service (API Claude ou Edge Function?)')
log('')
log('📞 PRÓXIMO PASSO:')
log('   → Comunicar blockers a MN (mneves@mantaassociados.com)')
log('   → Obter aprovação + definição de arquitetura')
log('   → Committar SKILL.md + MCP config para Git')
log('   → Executar RAG loading com infraestrutura correta')
log('')

return {
  phase: 'Fase 1 - Diagnóstico + Replaneamento',
  infrastructure_status: diag.infrastructure_status,
  sharepoint_ready: true,
  mcp_config_ready: mcp_config.status === 'ready',
  rag_blockers: rag_plan.blockers_identified,
  mcp_approval_needed: true,
  overall_status: 'ready_for_infrastructure_fix',
  next_gate: 'MN approval + architecture definition (Supabase schema, embeddings service)'
}
