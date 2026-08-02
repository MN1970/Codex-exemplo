export const meta = {
  name: 'fase1-parallel-implementation',
  description: 'Implementa Fase 1 com 10 agentes em paralelo: 5 para Supabase RAG + 5 para SharePoint',
  phases: [
    { title: 'Preparação', detail: 'Setup de credenciais e validação' },
    { title: 'RAG Loading (5 agentes)', detail: 'Carregar 5 coleções em paralelo' },
    { title: 'SharePoint Setup (5 agentes)', detail: 'Criar pastas + SKILL.md em paralelo' },
    { title: 'Validação', detail: 'Verificar integridade de tudo' }
  ]
}

// Schema definitions
const RAG_COLLECTION_SCHEMA = {
  collection_slug: { type: 'string', enum: ['saneamento', 'energia', 'portos', 'aeroportos', 'barragens'] },
  chunks_loaded: 'number',
  sources_processed: 'array',
  validation: 'object',
  status: { type: 'string', enum: ['success', 'warning', 'error'] }
}

const SHAREPOINT_SETUP_SCHEMA = {
  agent_name: 'string',
  folders_created: 'number',
  skill_md_uploaded: 'boolean',
  documents_uploaded: 'number',
  validation: 'object',
  status: { type: 'string', enum: ['success', 'warning', 'error'] }
}

const VALIDATION_SCHEMA = {
  rag_collections: 'object',
  sharepoint_folders: 'object',
  mcp_config: 'object',
  routing_tests: 'object',
  overall_status: 'string'
}

// ============================================================================
// FASE 1 PARALLEL EXECUTION
// ============================================================================

phase('Preparação')

log('🚀 Iniciando Fase 1 com 10 agentes em paralelo')
log('Objetivo: Operacionalizar 5 agentes novos (S6-S10) em 3 semanas')
log('')

// Validação de pré-requisitos
const prep = await agent(
  `Valide que tudo está pronto para Fase 1:

   CHECKLIST:
   - [ ] Supabase credenciais obtidas (API_KEY, URL)
   - [ ] SharePoint Graph API credenciais obtidas (Tenant, Client, Secret)
   - [ ] GitHub credentials prontos (PAT token)
   - [ ] Staging environments criados
   - [ ] Arquivo .mcp.json template preparado
   - [ ] Arquivo .claude/settings.json template preparado

   Se tudo está OK, retorne { status: 'ready', blockers: [] }
   Se há blockers, retorne { status: 'blocked', blockers: ['descrição'] }`,
  {
    label: 'prep-validation',
    model: 'haiku',
    schema: {
      status: { type: 'string', enum: ['ready', 'blocked'] },
      blockers: 'array'
    }
  }
)

if (prep.status === 'blocked') {
  log('❌ BLOQUEADO: Resolver antes de continuar')
  prep.blockers.forEach(b => log(`   • ${b}`))
  return { status: 'blocked', blockers: prep.blockers }
}

log('✅ Pré-requisitos validados, iniciando paralelização')
log('')

// ============================================================================
// SEMANA 1: RAG COLLECTIONS (5 agentes em paralelo)
// ============================================================================

phase('RAG Loading (5 agentes)')

log('📚 Semana 1: Carregando 5 coleções RAG em paralelo')
log('   • Cada agente carrega uma coleção completa')
log('   • Total esperado: ~2500-5000 chunks por coleção')
log('')

const rag_collections = [
  { slug: 'saneamento', label: 'S8 (Saneamento)', sources: ['SNIS', 'NBR 12211-12218', 'Lei 14.026', 'editais BNDES'] },
  { slug: 'energia', label: 'S9 (Energia)', sources: ['ANEEL editais', 'R1-R5 EPE', 'ONS', 'IEEE'] },
  { slug: 'portos', label: 'S6 (Portos)', sources: ['ANTAQ', 'PIANC', 'editais BNDES/ANTAQ'] },
  { slug: 'aeroportos', label: 'S7 (Aeroportos)', sources: ['ANAC/RBAC', 'ICAO Annex 14', 'FAA ACs'] },
  { slug: 'barragens', label: 'S10 (Barragens)', sources: ['ICOLD', 'CBDB', 'SIGBM', 'Lei 12.334'] }
]

const rag_results = await parallel(
  rag_collections.map(collection => () =>
    agent(
      `Você é o agente de carregamento de RAG para ${collection.label}.

      TAREFA: Carregar coleção RAG '${collection.slug}' com ~500-1000 chunks

      FONTES PRIMÁRIAS:
      ${collection.sources.map(s => `• ${s}`).join('\n')}

      PASSO 1: Fetch sources
      ├─ Buscar documentos das fontes oficiais
      ├─ SNIS: https://www.snis.gov.br/ (se saneamento)
      ├─ ANEEL: https://www.aneel.gov.br/resolucoes (se energia)
      ├─ ANTAQ: https://www.gov.br/antaq/ (se portos)
      ├─ ANAC: https://www.anac.gov.br/ (se aeroportos)
      └─ ICOLD: https://www.icold-cigb.org/ (se barragens)

      PASSO 2: Chunk documents
      ├─ Dividir em chunks de ~200-300 tokens
      ├─ Overlap: 50 tokens entre chunks
      └─ Metadados: source URL, tipo documento

      PASSO 3: Generate embeddings
      ├─ Usar Claude embeddings (ou similar vetorial)
      └─ Armazenar em Supabase rag_chunks

      PASSO 4: Validação
      ├─ Contar chunks: total ≥ 500
      ├─ Verificar qualidade: relevância >0.7
      └─ Testar query sample: buscar 5 chunks top-relevantes

      RETORNE:
      {
        collection_slug: '${collection.slug}',
        chunks_loaded: <número>,
        sources_processed: [<lista>],
        validation: {
          total_chunks: <número>,
          avg_similarity: <0-1>,
          sample_queries_passed: <boolean>,
          notes: '<observações>'
        },
        status: 'success | warning | error'
      }

      Se houver erro: tente retry 1x, depois retorne status 'error' com detalhes.`,
      {
        label: `rag-${collection.slug}`,
        model: 'sonnet',
        effort: 'high',
        schema: RAG_COLLECTION_SCHEMA
      }
    )
  )
)

log('📊 Resultados RAG Loading:')
rag_results.forEach((result, i) => {
  if (result && result.status === 'success') {
    log(`   ✅ ${rag_collections[i].label}: ${result.chunks_loaded} chunks carregados`)
  } else if (result && result.status === 'warning') {
    log(`   ⚠️  ${rag_collections[i].label}: ${result.chunks_loaded} chunks (com avisos)`)
  } else {
    log(`   ❌ ${rag_collections[i].label}: FALHOU`)
  }
})
log('')

// ============================================================================
// SEMANA 2: SHAREPOINT SETUP (5 agentes em paralelo)
// ============================================================================

phase('SharePoint Setup (5 agentes)')

log('📁 Semana 2: Criando estrutura SharePoint em paralelo')
log('   • Cada agente cria 2 pastas (agente + projetos)')
log('   • Carrega SKILL.md, README.md, refs e prompts')
log('')

const agents_setup = [
  {
    agent_slug: 'agente-portos',
    label: 'S6 (Portos)',
    sp_agent_path: '04_IA/Manta-Maestro/01-agentes-fundamentais/agente-portos',
    sp_project_path: '03_Projetos/Portos',
    skill_content: `# Agente Portos (S6)
Especialista em projetos portuários e hidroviários.
Cobre: estudos prévios, projetos básico/executivo, obra e operação.
Stakeholders: ANTAQ, TUP, operador portuário.
Normas: PIANC, ANTAQ, NBR 12211.`
  },
  {
    agent_slug: 'agente-aeroportos',
    label: 'S7 (Aeroportos)',
    sp_agent_path: '04_IA/Manta-Maestro/01-agentes-fundamentais/agente-aeroportos',
    sp_project_path: '03_Projetos/Aeroportos',
    skill_content: `# Agente Aeroportos (S7)
Especialista em infraestrutura aeroportuária (lado ar + terra).
Cobre: pistas RWY, taxiways, TPS, TECA, balizamento.
Stakeholders: ANAC, operador aeroporto.
Normas: RBAC 154, ICAO Annex 14, FAA AC.`
  },
  {
    agent_slug: 'agente-saneamento',
    label: 'S8 (Saneamento)',
    sp_agent_path: '04_IA/Manta-Maestro/01-agentes-fundamentais/agente-saneamento',
    sp_project_path: '03_Projetos/Saneamento',
    skill_content: `# Agente Saneamento (S8) — PRIORIDADE AySA
Especialista em saneamento básico (água, esgoto, drenagem, resíduos).
Prioridade: Projeto Argentina (AySA).
Cobre: ETA, ETE, adutoras, elevatórias, redes.
Stakeholders: ANA, ARSESP, AySA, ERAS.
Normas: Lei 14.026, NBR 12211-12218, SNIS.`
  },
  {
    agent_slug: 'agente-energia',
    label: 'S9 (Energia)',
    sp_agent_path: '04_IA/Manta-Maestro/01-agentes-fundamentais/agente-energia',
    sp_project_path: '03_Projetos/Energia',
    skill_content: `# Agente Energia (S9) — PRIORIDADE ANEEL/State Grid
Especialista em setor elétrico (geração, transmissão, distribuição).
Prioridade: Transmissão (ANEEL, State Grid).
Cobre: linhas LT, subestações, usinas, distribuição.
Stakeholders: ANEEL, ONS, EPE, concessionárias.
Normas: ANEEL resoluções, R1-R5, ONS procedimentos.`
  },
  {
    agent_slug: 'agente-barragens',
    label: 'S10 (Barragens)',
    sp_agent_path: '04_IA/Manta-Maestro/01-agentes-fundamentais/agente-barragens',
    sp_project_path: '03_Projetos/Barragens',
    skill_content: `# Agente Barragens (S10)
Especialista em barragens (concreto, terra, enrocamento, rejeitos).
Cobre: estudo prévio, projeto, obra, O&M, DD, descomissionamento.
Stakeholders: ANA, ANM, proprietário.
Normas: Lei 12.334, ICOLD, CBDB, SIGBM.`
  }
]

const sp_results = await parallel(
  agents_setup.map(agent_setup => () =>
    agent(
      `Você é o agente de setup SharePoint para ${agent_setup.label}.

      TAREFA: Criar estrutura de pastas + conteúdo para ${agent_setup.agent_slug}

      PASSO 1: Criar pastas SharePoint
      ├─ Folder: ${agent_setup.sp_agent_path}/
      │  ├─ Criar SKILL.md
      │  ├─ Criar README.md
      │  ├─ Criar refs/ (documentos de referência)
      │  └─ Criar prompts/ (exemplos de prompts)
      └─ Folder: ${agent_setup.sp_project_path}/
         └─ Subfolder vazio para projetos

      PASSO 2: Carregar SKILL.md
      Conteúdo template:
      \`\`\`markdown
      ${agent_setup.skill_content}

      ## Contexto de Domínio
      [Adicionar detalhes específicos do domínio]

      ## Ordem Canônica de Raciocínio
      1. Enquadramento
      2. Diagnóstico
      3. Concepção
      4. Detalhamento
      5. Rede / Estruturas
      6. Obras Especiais
      7. Impacto e Licenciamento
      8. Cronograma e Orçamento

      ## Ferramentas e Integrações
      - RAG: coleção '${agent_setup.agent_slug.replace('agente-', '')}' (prefixo: ${agent_setup.agent_slug.replace('agente-', '').slice(0, 3)})
      - SharePoint: ${agent_setup.sp_project_path}
      - MCP: Supabase, GitHub, Microsoft365

      ## Handoff com Outros Agentes
      - Manta 05 (orcamento)
      - Manta 06 (modelagem)
      - Manta 07 (cronograma)
      - Manta 02 (contratual)
      \`\`\`

      PASSO 3: Carregar README.md
      Conteúdo básico com links para SKILL.md, exemplos de uso, glossário.

      PASSO 4: Carregar refs/
      ├─ Buscar 3-5 documentos de referência primários
      ├─ Formatos: PDF, DOCX, XLSX
      └─ Nomeação: <FONTE>_<TITULO>.pdf

      PASSO 5: Criar prompts/
      ├─ starter-prompts.md: 5 prompts de exemplo
      ├─ Exemplos: estudo prévio, projeto básico, básico detalhado
      └─ Cada exemplo com contexto e saída esperada

      PASSO 6: Validação
      ├─ Contar folders criadas: 2 (agente + projetos)
      ├─ Contar arquivos carregados: ≥5 (SKILL, README, 3+ refs)
      └─ Testar acesso: todas as pastas visíveis no SharePoint

      RETORNE:
      {
        agent_name: '${agent_setup.agent_slug}',
        folders_created: 2,
        skill_md_uploaded: true,
        documents_uploaded: <número>,
        validation: {
          agent_folder_exists: true,
          project_folder_exists: true,
          files_count: <número>,
          notes: '<observações>'
        },
        status: 'success | warning | error'
      }

      Se houver erro: tentar fallback (criar manual, depois retry automático).`,
      {
        label: `sp-setup-${agent_setup.agent_slug}`,
        model: 'sonnet',
        effort: 'high',
        schema: SHAREPOINT_SETUP_SCHEMA
      }
    )
  )
)

log('📁 Resultados SharePoint Setup:')
sp_results.forEach((result, i) => {
  if (result && result.status === 'success') {
    log(`   ✅ ${agents_setup[i].label}: ${result.documents_uploaded} documentos carregados`)
  } else if (result && result.status === 'warning') {
    log(`   ⚠️  ${agents_setup[i].label}: parcialmente completo`)
  } else {
    log(`   ❌ ${agents_setup[i].label}: FALHOU`)
  }
})
log('')

// ============================================================================
// CONFIGURAÇÃO DE SISTEMA (paralelo com RAG + SharePoint)
// ============================================================================

log('⚙️  Configurando sistema (MCP, hooks, settings)')

const config = await agent(
  `Você é o agente de configuração do Claude Code para Manta Maestro.

  TAREFA: Criar/atualizar arquivos de configuração

  ARQUIVOS A CRIAR:

  1. .mcp.json
  Localização: Codex-exemplo/.mcp.json
  Conteúdo:
  \`\`\`json
  {
    "version": "1.0",
    "mcpServers": {
      "manta-hub": {
        "url": "https://hub.mantaassociados.com/mcp",
        "transport": "http"
      }
    }
  }
  \`\`\`

  2. .claude/settings.json
  Localização: Codex-exemplo/.claude/settings.json
  Conteúdo: Model tiering (Haiku → Sonnet → Opus)

  3. .claude/hooks/validate-claude-md.sh
  Localização: Codex-exemplo/.claude/hooks/validate-claude-md.sh
  Conteúdo: Validar schema do CLAUDE.md em pre-commit

  PASSO 1: Criar .mcp.json
  PASSO 2: Criar .claude/settings.json com tiering
  PASSO 3: Criar .claude/hooks/validate-claude-md.sh
  PASSO 4: Fazer git add + commit
  PASSO 5: Validar que todos estão no git

  RETORNE:
  {
    files_created: 3,
    commits_made: 1,
    validation: {
      mcp_json_exists: true,
      settings_json_exists: true,
      hooks_executable: true
    },
    status: 'success | error'
  }`,
  {
    label: 'system-config',
    model: 'sonnet',
    schema: {
      files_created: 'number',
      commits_made: 'number',
      validation: 'object',
      status: 'string'
    }
  }
)

log(`   ✅ Configuração: ${config.files_created} arquivos criados`)
log('')

// ============================================================================
// SEMANA 3: VALIDAÇÃO E TESTES
// ============================================================================

phase('Validação')

log('🧪 Semana 3: Validação e testes de integração')
log('')

const validation = await agent(
  `Você é o agente de QA e validação para Fase 1 do Manta Maestro.

  VALIDAÇÃO CHECKLIST:

  1. RAG Collections
  ├─ Supabase: 5 coleções existem?
  ├─ Chunks: cada uma tem ≥500 chunks?
  └─ Query test: buscar "ETA", "barragem", "Porto", "aeroporto", "energia"

  2. SharePoint
  ├─ Pastas: 10 pastas criadas (5 agentes + 5 projetos)?
  ├─ Arquivos: 5 SKILL.md carregados?
  └─ Documentos: refs/ têm documentos iniciais?

  3. MCP Configuration
  ├─ .mcp.json existe e é válido JSON?
  ├─ .claude/settings.json existe?
  └─ Hooks: .claude/hooks/validate-claude-md.sh é executável?

  4. Routing Tests
  ├─ Teste 30 prompts de routing
  ├─ Meta: ≥90% sucesso
  ├─ Ambigüidades: <5% (documentar em CLAUDDE.md)
  └─ Confiança: média ≥75%

  5. Documentação
  ├─ ARQUITETURA-AGENTES-IA.md v2.0.0 em SharePoint?
  ├─ Decisões de routing documentadas?
  └─ Runbooks básicos criados?

  RETORNE:
  {
    rag_collections: { total: 5, chunks_verified: <número> },
    sharepoint_folders: { total: 10, verified: <número> },
    mcp_config: { files_created: 3, validated: true },
    routing_tests: { total: 30, passed: <número>, confidence_avg: <0-100> },
    ambiguities: [{ prompt: '...', decision: '...' }],
    overall_status: 'success | warning | blocked',
    gate_phase2: true | false
  }`,
  {
    label: 'qa-validation',
    model: 'sonnet',
    effort: 'high',
    schema: VALIDATION_SCHEMA
  }
)

log('✅ Validação Final:')
log(`   RAG: ${validation.rag_collections.total} coleções, ${validation.rag_collections.chunks_verified} chunks`)
log(`   SharePoint: ${validation.sharepoint_folders.total} pastas criadas`)
log(`   MCP: ${validation.mcp_config.files_created} arquivos, validado`)
log(`   Routing: ${validation.routing_tests.passed}/${validation.routing_tests.total} testes passaram`)
log(`   Status: ${validation.overall_status}`)
log(`   Gate Fase 2: ${validation.gate_phase2 ? '✅ APROVADO' : '❌ BLOQUEADO'}`)
log('')

// ============================================================================
// RELATÓRIO FINAL
// ============================================================================

log('═'.repeat(60))
log('📋 RELATÓRIO FINAL FASE 1')
log('═'.repeat(60))
log('')
log('✅ RAG LOADING (Semana 1):')
rag_results.forEach((r, i) => {
  if (r && r.status === 'success') {
    log(`   ✅ ${rag_collections[i].label}: ${r.chunks_loaded} chunks`)
  }
})
log('')
log('✅ SHAREPOINT SETUP (Semana 2):')
sp_results.forEach((r, i) => {
  if (r && r.status === 'success') {
    log(`   ✅ ${agents_setup[i].label}: ${r.documents_uploaded} docs`)
  }
})
log('')
log('✅ SYSTEM CONFIG:')
log(`   ✅ ${config.files_created} arquivos criados + commitados`)
log('')
log('✅ VALIDAÇÃO & TESTES (Semana 3):')
log(`   ✅ ${validation.routing_tests.passed}/${validation.routing_tests.total} routing tests`)
log(`   ✅ Confiança média: ${validation.routing_tests.confidence_avg}%`)
log('')
log('═'.repeat(60))
log('')

if (validation.gate_phase2) {
  log('🎉 FASE 1 COMPLETA E APROVADA PARA FASE 2')
  log('')
  log('Próximos passos:')
  log('  1. MN aprova Fase 2')
  log('  2. Iniciar Semana 4: Workflows multi-agente')
  log('  3. Paralelo com Fase 2: 5 agentes para workflows + 1 para integrações MCP')
} else {
  log('⚠️  FASE 1 COM BLOQUEADORES')
  log('Antes de Fase 2, resolver:')
  validation.ambiguities.forEach(a => log(`   • ${a.prompt}: ${a.decision}`))
}

return {
  phase: 'FASE 1',
  status: validation.overall_status,
  rag_loaded: rag_results.filter(r => r?.status === 'success').length,
  sharepoint_ready: sp_results.filter(r => r?.status === 'success').length,
  config_ready: config.status === 'success',
  routing_success_rate: `${(validation.routing_tests.passed / validation.routing_tests.total * 100).toFixed(1)}%`,
  gate_phase2: validation.gate_phase2,
  duration_estimate: '14-20 dias',
  investment: '60 horas'
}
