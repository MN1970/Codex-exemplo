export interface AgentDetails {
  code: string;
  name: string;
  description: string;
  tier: string;
  status: string;
  aliases: string[];
  markdown: string;
  segment?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export class AgentDetailsError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = 'AgentDetailsError';
  }
}

interface GetAgentDetailsOptions {
  includeHistory?: boolean;
  format?: 'json' | 'markdown';
}

/**
 * Retrieves agent details from the Manta Associados agent registry
 * @param agentCode - Agent code (e.g., 'manta-00', 'agente-saneamento')
 * @param options - Optional configuration
 * @returns Promise<AgentDetails>
 * @throws AgentDetailsError with statusCode 404 if agent not found
 */
export async function getAgentDetails(
  agentCode: string | null | undefined,
  options?: GetAgentDetailsOptions
): Promise<AgentDetails> {
  if (!agentCode || typeof agentCode !== 'string' || agentCode.trim() === '') {
    throw new AgentDetailsError(400, 'Invalid agent code');
  }

  const normalizedCode = agentCode.toLowerCase().trim();

  const agentRegistry = getAgentRegistry();
  const agent = findAgentByCodeOrAlias(agentRegistry, normalizedCode);

  if (!agent) {
    throw new AgentDetailsError(
      404,
      `Agent "${agentCode}" not found in registry`
    );
  }

  const markdown = generateAgentMarkdown(agent);

  return {
    code: agent.code,
    name: agent.name,
    description: agent.description,
    tier: agent.tier,
    status: agent.status,
    aliases: agent.aliases,
    markdown,
    segment: agent.segment,
  };
}

interface Agent {
  code: string;
  name: string;
  description: string;
  tier: string;
  status: string;
  aliases: string[];
  segment?: string;
}

function getAgentRegistry(): Agent[] {
  return [
    {
      code: 'Manta 00',
      name: 'maestro',
      description: 'Router principal de agentes IA',
      tier: 'Haiku→Sonnet',
      status: '✅ Operacional',
      aliases: ['maestro', 'manta-00', 'manta-router'],
    },
    {
      code: 'Manta 01',
      name: 'claims',
      description: 'Agente especializado em análise de claims e sinistros',
      tier: 'Opus',
      status: '✅ Operacional',
      aliases: ['claims', '02-C', 'manta-01', 'manta-claims'],
    },
    {
      code: 'Manta 02',
      name: 'contratual',
      description: 'Análise e revisão de contratos e documentação legal',
      tier: 'Sonnet',
      status: '✅ Operacional',
      aliases: ['contratual', 'manta-02'],
    },
    {
      code: 'Manta 04',
      name: 'imobiliario',
      description: 'Gestão e análise de questões imobiliárias',
      tier: 'Sonnet',
      status: '✅ Operacional',
      aliases: ['imobiliario', 'manta-04'],
    },
    {
      code: 'Manta 05',
      name: 'orcamento',
      description: 'Orçamentação e análise de custos de projetos',
      tier: 'Sonnet',
      status: '✅ Operacional',
      aliases: ['orcamento', 'manta-05'],
    },
    {
      code: 'Manta 06',
      name: 'modelagem',
      description: 'Modelagem financeira e de cenários',
      tier: 'Sonnet/Opus',
      status: '✅ Operacional',
      aliases: ['modelagem', 'manta-06'],
    },
    {
      code: 'Manta 07',
      name: 'cronograma',
      description: 'Gestão de cronogramas e planejamento de projetos',
      tier: 'Sonnet',
      status: '✅ Operacional',
      aliases: ['cronograma', 'manta-07'],
    },
    {
      code: 'Manta 13',
      name: 'bd',
      description: 'Business Development e oportunidades',
      tier: 'Sonnet',
      status: '✅ Operacional',
      aliases: ['bd', 'manta-13', 'business-dev'],
    },
    {
      code: 'Manta 14',
      name: 'apresentacoes',
      description: 'Criação e edição de apresentações',
      tier: 'Sonnet',
      status: '✅ Operacional',
      aliases: ['apresentacoes', 'manta-14-pptx'],
    },
    {
      code: 'Manta 15',
      name: 'advisory',
      description: 'Consultoria estratégica e advisory',
      tier: 'Sonnet/Opus',
      status: '✅ Operacional',
      aliases: ['advisory', 'manta-15'],
    },
    {
      code: 'Manta 16',
      name: 'arquiteto-ia',
      description: 'Arquitetura e design de soluções IA',
      tier: 'Opus',
      status: '✅ Operacional',
      aliases: ['arquiteto-ia', 'manta-15-arq'],
    },
    {
      code: 'Manta 03-S8',
      name: 'agente-saneamento',
      description: 'Especialista em projetos de saneamento e água',
      tier: 'Sonnet',
      status: '✅ Operacional — PRIORIDADE AySA',
      aliases: ['agente-saneamento', 'saneamento', 's8'],
      segment: 'Saneamento',
    },
    {
      code: 'Manta 03-S9',
      name: 'agente-energia',
      description: 'Especialista em projetos de energia elétrica',
      tier: 'Sonnet',
      status: '✅ Operacional — ANEEL/State Grid',
      aliases: ['agente-energia', 'energia', 's9'],
      segment: 'Energia',
    },
    {
      code: 'Manta 03-S6',
      name: 'agente-portos',
      description: 'Especialista em projetos portuários',
      tier: 'Sonnet',
      status: '✅ Operacional',
      aliases: ['agente-portos', 'portos', 's6'],
      segment: 'Portos',
    },
    {
      code: 'Manta 03-S7',
      name: 'agente-aeroportos',
      description: 'Especialista em projetos aeroportuários',
      tier: 'Sonnet',
      status: '✅ Operacional',
      aliases: ['agente-aeroportos', 'aeroportos', 's7'],
      segment: 'Aeroportos',
    },
    {
      code: 'Manta 03-S10',
      name: 'agente-barragens',
      description: 'Especialista em projetos de barragens e recursos hídricos',
      tier: 'Sonnet',
      status: '✅ Operacional',
      aliases: ['agente-barragens', 'barragens', 's10'],
      segment: 'Barragens',
    },
  ];
}

function findAgentByCodeOrAlias(agents: Agent[], query: string): Agent | null {
  const lowerQuery = query.toLowerCase();

  return (
    agents.find(
      agent =>
        agent.code.toLowerCase() === lowerQuery ||
        agent.name.toLowerCase() === lowerQuery ||
        agent.aliases.some(alias => alias.toLowerCase() === lowerQuery)
    ) || null
  );
}

function generateAgentMarkdown(agent: Agent): string {
  const lines: string[] = [
    `## ${agent.code} — ${agent.name}`,
    '',
    agent.description,
    '',
    '### Detalhes',
    '',
    `| Campo | Valor |`,
    `|-------|-------|`,
    `| Código | \`${agent.code}\` |`,
    `| Nome | \`${agent.name}\` |`,
    `| Tier | ${agent.tier} |`,
    `| Status | ${agent.status} |`,
  ];

  if (agent.segment) {
    lines.push(`| Segmento | ${agent.segment} |`);
  }

  lines.push('', '### Aliases', '');
  agent.aliases.forEach(alias => {
    lines.push(`- \`${alias}\``);
  });

  return lines.join('\n');
}
