/**
 * Workflow: Hunt Global Parallel
 *
 * Executa múltiplos agentes em paralelo para:
 * - Hugging Face (modelo + empresas)
 * - GitHub (repositórios + código)
 * - Japão (tech companies + código)
 * - Coréia (tech companies + código)
 * - China (tech companies + código)
 *
 * Total: 5 agentes rodando em paralelo
 */

export const meta = {
  name: 'hunt-global-parallel',
  description: 'Web scraping global paralelo: HF, GitHub, JP, KR, CN',
  phases: [
    { title: 'Scraping', detail: '5 sites em paralelo com Obscura' },
    { title: 'Análise', detail: 'Extrair padrões de código' },
  ]
}

// Schemas para os agentes
const SCRAPING_SCHEMA = {
  type: 'object',
  properties: {
    fonte: { type: 'string' },
    resultados: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          nome: { type: 'string' },
          url: { type: 'string' },
          tipo: { type: 'string' }
        }
      }
    },
    padroes_codigo: {
      type: 'array',
      items: { type: 'string' }
    }
  }
}

// PHASE 1: Scraping em paralelo
phase('Scraping')

const results = await parallel([
  () => agent(
    `
    Usar Obscura para fazer web scraping em Hugging Face:
    1. Fetch: https://huggingface.co/organizations
    2. Fetch: https://huggingface.co/models?sort=trending
    3. Extrair: nomes de organizações, frameworks usados, padrões de código
    4. Retornar: lista de organizações + código snippets
    `,
    {
      label: 'hunt:huggingface',
      phase: 'Scraping',
      schema: SCRAPING_SCHEMA
    }
  ),
  () => agent(
    `
    Usar Obscura para fazer web scraping em GitHub (código):
    1. Fetch: https://github.com/trending?language=python
    2. Fetch: https://github.com/search?q=transformers+pytorch
    3. Extrair: repositórios, linguagens, frameworks, exemplos de código
    4. Retornar: repos trending + padrões PyTorch/TensorFlow
    `,
    {
      label: 'hunt:github',
      phase: 'Scraping',
      schema: SCRAPING_SCHEMA
    }
  ),
  () => agent(
    `
    Usar Obscura para fazer web scraping em sites tech JAPONESES:
    1. Qiita.com (comunidade tech JP)
    2. Zenn.dev (artigos técnicos JP)
    3. GitHub awesome-japanese
    4. Extrair: empresas (Toyota, Sony, NHK, Fujitsu), padrões de código JP
    5. Retornar: tech companies + código em padrão Japanese
    `,
    {
      label: 'hunt:japan',
      phase: 'Scraping',
      schema: SCRAPING_SCHEMA
    }
  ),
  () => agent(
    `
    Usar Obscura para fazer web scraping em sites tech COREANOS:
    1. GitHub awesome-korean-nlp, awesome-korean-cv
    2. Sites: Naver Dev, Korean Tech News
    3. Extrair: Samsung, LG, Naver, Kakao, SK, KT
    4. Padrões de código coreano (NLP, CV especializado)
    5. Retornar: tech companies + código em padrão Korean
    `,
    {
      label: 'hunt:korea',
      phase: 'Scraping',
      schema: SCRAPING_SCHEMA
    }
  ),
  () => agent(
    `
    Usar Obscura para fazer web scraping em sites tech CHINESES:
    1. Alipay, Baidu, Tencent, ByteDance, Huawei (GitHub & sites)
    2. GitHub awesome-chinese, Zhihu.com (tech discussions)
    3. Gitee.com (GitHub chinês)
    4. Extrair: companies, frameworks favoritos (MindSpore, PaddlePaddle), padrões
    5. Retornar: tech companies + código em padrão Chinese
    `,
    {
      label: 'hunt:china',
      phase: 'Scraping',
      schema: SCRAPING_SCHEMA
    }
  )
])

// PHASE 2: Análise de padrões
phase('Análise')

const analysis = await parallel([
  () => agent(
    `
    Analisar resultados do scraping global de Hugging Face, GitHub, Japão, Coréia e China.

    Dados de entrada (já coletados):
    ${JSON.stringify(results.filter(Boolean).slice(0, 2), null, 2)}

    Tarefa:
    1. Identificar padrões comuns de código (PyTorch vs TensorFlow vs JAX)
    2. Comparar: qual framework é mais usado por região (JP/KR/CN)?
    3. Extrair best practices por país
    4. Recomendar frameworks para Manta por segmento
    5. Retornar: análise estruturada com insights por região
    `,
    {
      label: 'analyze:frameworks',
      phase: 'Análise'
    }
  ),
  () => agent(
    `
    Extrair padrões de código específicos encontrados no scraping global.

    Dados: ${JSON.stringify(results.filter(Boolean).slice(2, 5), null, 2)}

    Buscar e documentar:
    1. Imports mais comuns (transformers, torch, tf, jax)
    2. Padrões de função mais usados (data loaders, training loops)
    3. Convenções de naming por país (Python PT vs EN vs JP vs KR vs CN)
    4. Estrutura de projetos (setup.py vs pyproject.toml vs poetry)
    5. Retornar: snippets de código + análise de qualidade
    `,
    {
      label: 'analyze:code-patterns',
      phase: 'Análise'
    }
  )
])

// Sintetizar resultados
log(`✅ Scraping paralelo: ${results.filter(Boolean).length} fontes coletadas`)
log(`✅ Análise: ${analysis.filter(Boolean).length} análises completadas`)

return {
  scraping: results.filter(Boolean),
  analysis: analysis.filter(Boolean),
  timestamp: new Date().toISOString(),
  total_sources: 5,
  regions: ['global', 'japan', 'korea', 'china', 'huggingface']
}
