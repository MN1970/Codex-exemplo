// Hub Portal Mock Data & Constants

export interface Agent {
  id: string
  code: string
  name: string
  aliases: string[]
  category: 'horizontal' | 'vertical' | 'infrastructure'
  status: 'operational' | 'partial' | 'new'
  description: string
  tools?: number
}

export interface Tool {
  id: string
  name: string
  port: number
  description: string
  status: 'operational' | 'beta' | 'planned'
  agents: string[]
}

export interface SyncEvent {
  id: string
  timestamp: Date
  status: 'success' | 'partial' | 'failed'
  message: string
  itemsSync: number
  duration: number // seconds
}

// 20 Agents as per CLAUDE.md v4.2
export const MOCK_AGENTS: Agent[] = [
  // Horizontal agents (11)
  {
    id: 'manta-00',
    code: 'Manta 00',
    name: 'maestro (router)',
    aliases: ['maestro', 'manta-router'],
    category: 'horizontal',
    status: 'operational',
    description: 'Master routing agent for all segments',
    tools: 15,
  },
  {
    id: 'manta-01',
    code: 'Manta 01',
    name: 'claims',
    aliases: ['02-C', 'manta-claims'],
    category: 'horizontal',
    status: 'operational',
    description: 'Claims and dispute resolution',
    tools: 8,
  },
  {
    id: 'manta-02',
    code: 'Manta 02',
    name: 'contratual',
    aliases: ['manta-02', 'contratual'],
    category: 'horizontal',
    status: 'operational',
    description: 'Contract analysis and management',
    tools: 12,
  },
  {
    id: 'manta-04',
    code: 'Manta 04',
    name: 'imobiliario',
    aliases: ['manta-04'],
    category: 'horizontal',
    status: 'operational',
    description: 'Real estate and property management',
    tools: 9,
  },
  {
    id: 'manta-05',
    code: 'Manta 05',
    name: 'orcamento',
    aliases: ['manta-05'],
    category: 'horizontal',
    status: 'operational',
    description: 'Budget and cost estimation',
    tools: 11,
  },
  {
    id: 'manta-06',
    code: 'Manta 06',
    name: 'modelagem',
    aliases: ['manta-06'],
    category: 'horizontal',
    status: 'operational',
    description: 'Data modeling and analysis',
    tools: 10,
  },
  {
    id: 'manta-07',
    code: 'Manta 07',
    name: 'cronograma',
    aliases: ['manta-07'],
    category: 'horizontal',
    status: 'operational',
    description: 'Schedule and timeline management',
    tools: 8,
  },
  {
    id: 'manta-13',
    code: 'Manta 13',
    name: 'bd',
    aliases: ['manta-13', 'business-dev'],
    category: 'horizontal',
    status: 'operational',
    description: 'Business development and strategy',
    tools: 7,
  },
  {
    id: 'manta-14',
    code: 'Manta 14',
    name: 'apresentacoes',
    aliases: ['manta-14-pptx'],
    category: 'horizontal',
    status: 'operational',
    description: 'Presentation and report generation',
    tools: 6,
  },
  {
    id: 'manta-15',
    code: 'Manta 15',
    name: 'advisory',
    aliases: ['manta-15', 'advisory'],
    category: 'horizontal',
    status: 'operational',
    description: 'Advisory and consulting services',
    tools: 9,
  },
  {
    id: 'manta-16',
    code: 'Manta 16',
    name: 'arquiteto-ia',
    aliases: ['manta-15-arq'],
    category: 'horizontal',
    status: 'operational',
    description: 'AI architecture and design',
    tools: 8,
  },
  // Infrastructure agents S1-S4 (4)
  {
    id: 'manta-03-s1',
    code: 'Manta 03-S1',
    name: 'agente-infraestrutura (S1)',
    aliases: ['rodovias'],
    category: 'infrastructure',
    status: 'operational',
    description: 'Highways and road infrastructure',
    tools: 14,
  },
  {
    id: 'manta-03-s2',
    code: 'Manta 03-S2',
    name: 'agente-infraestrutura (S2)',
    aliases: ['oae', 'bridges'],
    category: 'infrastructure',
    status: 'operational',
    description: 'Special art works - bridges and viaducts',
    tools: 12,
  },
  {
    id: 'manta-03-s3',
    code: 'Manta 03-S3',
    name: 'agente-infraestrutura (S3)',
    aliases: ['ferrovia'],
    category: 'infrastructure',
    status: 'operational',
    description: 'Railway infrastructure',
    tools: 11,
  },
  {
    id: 'manta-03-s4',
    code: 'Manta 03-S4',
    name: 'agente-infraestrutura (S4)',
    aliases: ['metro'],
    category: 'infrastructure',
    status: 'operational',
    description: 'Metropolitan and urban transit',
    tools: 13,
  },
  // Vertical agents S6-S10 (5)
  {
    id: 'manta-03-s6',
    code: 'Manta 03-S6',
    name: 'agente-portos',
    aliases: ['portos', 'terminals'],
    category: 'vertical',
    status: 'new',
    description: 'Port and maritime terminal projects',
    tools: 10,
  },
  {
    id: 'manta-03-s7',
    code: 'Manta 03-S7',
    name: 'agente-aeroportos',
    aliases: ['aeroportos', 'airports'],
    category: 'vertical',
    status: 'new',
    description: 'Airport and aerial infrastructure',
    tools: 11,
  },
  {
    id: 'manta-03-s8',
    code: 'Manta 03-S8',
    name: 'agente-saneamento',
    aliases: ['saneamento', 'sanitation'],
    category: 'vertical',
    status: 'new',
    description: 'Water, wastewater and sanitation systems',
    tools: 12,
  },
  {
    id: 'manta-03-s9',
    code: 'Manta 03-S9',
    name: 'agente-energia',
    aliases: ['energia', 'power'],
    category: 'vertical',
    status: 'new',
    description: 'Electrical transmission and energy',
    tools: 13,
  },
  {
    id: 'manta-03-s10',
    code: 'Manta 03-S10',
    name: 'agente-barragens',
    aliases: ['barragens', 'dams'],
    category: 'vertical',
    status: 'new',
    description: 'Dam and reservoir infrastructure',
    tools: 11,
  },
]

// 14 Tools
export const MOCK_TOOLS: Tool[] = [
  {
    id: 'balanco',
    name: 'Balanço de Massa',
    port: 8000,
    description: 'Analyzes cut/fill volumes from longitudinal profiles',
    status: 'operational',
    agents: ['manta-03-s1', 'manta-03-s2', 'manta-03-s3', 'manta-03-s4'],
  },
  {
    id: 'paisagismo',
    name: 'Paisagismo',
    port: 8001,
    description: 'Analyzes landscape design areas',
    status: 'operational',
    agents: ['manta-03-s1', 'manta-03-s3'],
  },
  {
    id: 'sinalizacao',
    name: 'Sinalização Vertical',
    port: 8002,
    description: 'Extracts vertical signage data from road projects',
    status: 'operational',
    agents: ['manta-03-s1', 'manta-03-s3'],
  },
  {
    id: 'orcamento',
    name: 'Orçamento',
    port: 8003,
    description: 'Matches budget items to reference base services',
    status: 'operational',
    agents: [
      'manta-05',
      'manta-03-s1',
      'manta-03-s2',
      'manta-03-s6',
      'manta-03-s8',
    ],
  },
  {
    id: 'mantacad',
    name: 'MantaCAD',
    port: 8004,
    description: 'Web-based DXF/DWG viewer with Canvas 2D rendering',
    status: 'operational',
    agents: ['manta-00'],
  },
  {
    id: 'estrutural',
    name: 'Estrutural',
    port: 8005,
    description: 'Interactive 2D structural analysis editor',
    status: 'operational',
    agents: ['manta-03-s2', 'manta-03-s6'],
  },
  {
    id: 'iluminacao',
    name: 'Iluminação',
    port: 8006,
    description: 'Extracts public lighting data from highway drawings',
    status: 'operational',
    agents: ['manta-03-s1', 'manta-03-s3'],
  },
  {
    id: 'pavimentacao',
    name: 'Pavimentação',
    port: 8007,
    description: 'Extracts pavement hatches and calculates volumes',
    status: 'operational',
    agents: ['manta-03-s1', 'manta-03-s4'],
  },
  {
    id: 'askcad',
    name: 'AskCAD',
    port: 8009,
    description: 'Agentic Q&A and knowledge-management platform',
    status: 'operational',
    agents: ['manta-00'],
  },
  {
    id: 'terraplenagem',
    name: 'Terraplenagem',
    port: 8010,
    description: 'Extracts Brückner mass distribution diagrams',
    status: 'operational',
    agents: ['manta-03-s1', 'manta-03-s4'],
  },
  {
    id: 'landxml',
    name: 'LandXML',
    port: 8011,
    description: 'Streaming pipeline for Civil 3D LandXML files',
    status: 'operational',
    agents: ['manta-03-s1', 'manta-03-s4'],
  },
  {
    id: 'ifc',
    name: 'IFC',
    port: 8012,
    description: 'Reads IFC files and extracts native quantities',
    status: 'operational',
    agents: ['manta-06'],
  },
  {
    id: 'sondagem',
    name: 'Sondagem',
    port: 8013,
    description: 'Reads PDF geotechnical drilling reports',
    status: 'operational',
    agents: ['manta-03-s1', 'manta-03-s2', 'manta-03-s8'],
  },
  {
    id: 'oae',
    name: 'OAE',
    port: 8014,
    description: 'Batch quantity takeoff for bridges/viaducts',
    status: 'operational',
    agents: ['manta-03-s2'],
  },
]

// Sync events timeline
export const MOCK_SYNC_EVENTS: SyncEvent[] = [
  {
    id: 'sync-001',
    timestamp: new Date(Date.now() - 5 * 60000),
    status: 'success',
    message: 'Full registry sync completed',
    itemsSync: 234,
    duration: 45,
  },
  {
    id: 'sync-002',
    timestamp: new Date(Date.now() - 25 * 60000),
    status: 'success',
    message: 'Agents and tools synchronized',
    itemsSync: 189,
    duration: 32,
  },
  {
    id: 'sync-003',
    timestamp: new Date(Date.now() - 60 * 60000),
    status: 'partial',
    message: 'Partial sync: 2 tools skipped',
    itemsSync: 201,
    duration: 28,
  },
]

// Health metrics
export const MOCK_HEALTH_METRICS = {
  totalAgents: 20,
  totalTools: 14,
  operationalServices: 13,
  healthPercentage: 93,
  lastSyncTime: new Date(Date.now() - 5 * 60000),
  uptime: 99.8,
}

export const getAgentById = (id: string): Agent | undefined => {
  return MOCK_AGENTS.find(a => a.id === id)
}

export const getToolById = (id: string): Tool | undefined => {
  return MOCK_TOOLS.find(t => t.id === id)
}

export const searchAgents = (query: string): Agent[] => {
  const lowerQuery = query.toLowerCase()
  return MOCK_AGENTS.filter(
    agent =>
      agent.name.toLowerCase().includes(lowerQuery) ||
      agent.code.toLowerCase().includes(lowerQuery) ||
      agent.aliases.some(alias => alias.toLowerCase().includes(lowerQuery)) ||
      agent.description.toLowerCase().includes(lowerQuery)
  )
}
