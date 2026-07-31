-- Manta Maestro v4.2 — Seed dos 20 Agentes
-- Data: 2026-07-31
-- Ticket: MNT-2026-BOOTSTRAP-AGENTS
--
-- Este arquivo seeds os 20 agentes (11 horizontais + 10 verticais S1-S10)
-- na tabela 'agents' do Supabase.
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$DATABASE_URL" -f supabase/migrations/2026_07_31_agents_seed_v4_2.sql

BEGIN;

-- Criar tabela agents se não existir
CREATE TABLE IF NOT EXISTS agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  aliases TEXT[] DEFAULT '{}',
  segment VARCHAR(50),
  tier VARCHAR(50) DEFAULT 'Sonnet',
  status VARCHAR(50) DEFAULT 'active',
  description TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar RLS se aplicável
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;

-- Política de leitura pública
CREATE POLICY IF NOT EXISTS "Enable read access for all users" ON agents
  FOR SELECT USING (true);

-- Seed dos 20 agentes Manta v4.2
-- Agentes Horizontais (11)
INSERT INTO agents (code, name, aliases, tier, status, description, metadata)
VALUES
  ('manta-00', 'Maestro (Router)', ARRAY['maestro','manta-router'], 'Haiku→Sonnet', 'active',
   'Roteador central dos agentes IA da Manta. Direciona requisições para agentes especializados.',
   '{"group":"horizontal","version":"v4.2","mcp_protocol":true,"tier_adaptive":true}'::jsonb),

  ('manta-01', 'Claims', ARRAY['02-C','manta-claims'], 'Opus', 'active',
   'Especialista em análise e processamento de sinistros e reclamações contratuais.',
   '{"group":"horizontal","version":"v4.2","modules":["analytics","extraction","risk-assessment"]}'::jsonb),

  ('manta-02', 'Contratual', ARRAY['manta-02','contratual'], 'Sonnet', 'active',
   'Análise de riscos contratuais, revisão de cláusulas e conformidade legal.',
   '{"group":"horizontal","version":"v4.2","modules":["risk-analysis","legal-review","compliance"]}'::jsonb),

  ('manta-04', 'Imobiliário', ARRAY['manta-04'], 'Sonnet', 'active',
   'Avaliação de propriedades, análise de projetos imobiliários e due diligence.',
   '{"group":"horizontal","version":"v4.2","focus":"real-estate","specialization":"valuation"}'::jsonb),

  ('manta-05', 'Orçamento', ARRAY['manta-05'], 'Sonnet', 'active',
   'Análise, elaboração e otimização de orçamentos de projetos e empreendimentos.',
   '{"group":"horizontal","version":"v4.2","modules":["estimation","cost-control","optimization"]}'::jsonb),

  ('manta-06', 'Modelagem', ARRAY['manta-06'], 'Sonnet/Opus', 'active',
   'Modelagem financeira, BIM, simulações e análise de cenários.',
   '{"group":"horizontal","version":"v4.2","capabilities":["bim","financial-modeling","simulations","scenario-analysis"]}'::jsonb),

  ('manta-07', 'Cronograma', ARRAY['manta-07'], 'Sonnet', 'active',
   'Planejamento, controle e otimização de cronogramas de projetos.',
   '{"group":"horizontal","version":"v4.2","modules":["planning","tracking","optimization","cpm"]}'::jsonb),

  ('manta-13', 'Business Development', ARRAY['manta-13','business-dev'], 'Sonnet', 'active',
   'Inteligência de mercado, oportunidades comerciais e análise competitiva.',
   '{"group":"horizontal","version":"v4.2","focus":"market-intelligence","modules":["competitive-analysis","opportunity-assessment"]}'::jsonb),

  ('manta-14', 'Apresentações', ARRAY['manta-14-pptx'], 'Sonnet', 'active',
   'Geração de apresentações, decks executivos e materiais de comunicação.',
   '{"group":"horizontal","version":"v4.2","output_format":"pptx","capabilities":["deck-generation","visual-design","storytelling"]}'::jsonb),

  ('manta-15', 'Advisory', ARRAY['manta-15','advisory'], 'Sonnet/Opus', 'active',
   'Consultoria estratégica, governance e assessoria executiva.',
   '{"group":"horizontal","version":"v4.2","modules":["strategy","governance","executive-advisory"],"tier_adaptive":true}'::jsonb),

  ('manta-16', 'Arquiteto IA', ARRAY['manta-15-arq'], 'Opus', 'active',
   'Design de arquiteturas de IA, sistemas multiagente e workflows avançados.',
   '{"group":"horizontal","version":"v4.2","specialization":"ai-architecture","modules":["system-design","multi-agent","workflow-design"]}'::jsonb),

-- Agentes Verticais por Segmento (10)
  ('manta-03-s1', 'Infraestrutura - Rodovias', ARRAY['agente-infraestrutura','s1','rodovias'], 'Sonnet', 'active',
   'Especialista em projetos de rodovias, pavimentação e terraplenagem. Conhecimento em SICRO, DNIT, BGS, CBUQ.',
   '{"group":"vertical","segment":"rodovias","version":"v4.2","rag_prefix":"rod:","regulators":["DNIT"],"standards":["SICRO","NBR 7207","NBR 7210"]}'::jsonb),

  ('manta-03-s2', 'Infraestrutura - OAE', ARRAY['agente-infraestrutura','s2','oae','pontes'], 'Sonnet', 'active',
   'Especialista em Obras de Arte Especiais: pontes, viadutos, túneis rodoviários. NBR 7187, projeto de estruturas.',
   '{"group":"vertical","segment":"oae","version":"v4.2","rag_prefix":"oae:","standards":["NBR 7187","NBR 6122","NBR 8681"],"oae_types":["pontes","viadutos","tuneis_rodo"]}'::jsonb),

  ('manta-03-s3', 'Infraestrutura - Ferrovia', ARRAY['agente-infraestrutura','s3','ferrovia'], 'Sonnet', 'active',
   'Especialista em projetos ferroviários, via permanente, trilhos, dormente, AMV e sistemas de transporte ferroviário.',
   '{"group":"vertical","segment":"ferrovia","version":"v4.2","rag_prefix":"fer:","focus":"via-permanente","standards":["ABNT NBR","IAPF"]}'::jsonb),

  ('manta-03-s4', 'Infraestrutura - Metrô', ARRAY['agente-infraestrutura','s4','metro','vlt'], 'Sonnet', 'active',
   'Especialista em metrô, VLT, transporte rápido. Conhecimento em NATM, PSD, linhas urbanas, estações, ventilação.',
   '{"group":"vertical","segment":"metro","version":"v4.2","rag_prefix":"met:","techniques":["NATM","PSD","mined_stations"],"standards":["NBR 13594"]}'::jsonb),

  ('manta-03-s5', 'Infraestrutura - Túneis', ARRAY['agente-infraestrutura','s5','tuneis'], 'Sonnet', 'active',
   'Especialista em túneis e obras subterrâneas. Versão parcial (coberta por S2/S4). Suporte a NATM, drenagem, suporte temporário.',
   '{"group":"vertical","segment":"tuneis","version":"v4.2","rag_prefix":"tun:","status":"partial","coverage":["s2","s4"],"techniques":["NATM","shotcrete"]}'::jsonb),

  ('manta-03-s6', 'Portos', ARRAY['agente-portos','s6','portos','terminal'], 'Sonnet', 'active',
   'Especialista em terminais portuários, dragagem, berços de atracação, estruturas de cais. ANTAQ, PIANC, editais BNDES/ANTAQ.',
   '{"group":"vertical","segment":"portos","version":"v4.2","rag_prefix":"por:","new_agent":"2026-07-05","regulators":["ANTAQ"],"standards":["PIANC","ROM 2.0","NBR 9782","NBR 6122"]}'::jsonb),

  ('manta-03-s7', 'Aeroportos', ARRAY['agente-aeroportos','s7','aeroportos'], 'Sonnet', 'active',
   'Especialista em aeroportos, pistas de pouso, terminais, balizamento. ANAC, RBAC 154, ICAO Annex 14, FAA ACs.',
   '{"group":"vertical","segment":"aeroportos","version":"v4.2","rag_prefix":"aer:","new_agent":"2026-07-05","regulators":["ANAC","ICAO","FAA"],"standards":["RBAC 154","Annex 14"]}'::jsonb),

  ('manta-03-s8', 'Saneamento', ARRAY['agente-saneamento','s8','saneamento','ete','eta'], 'Sonnet', 'active',
   'Especialista em saneamento (ETA/ETE), adução, sistemas de esgoto, tratamento. AySA (Argentina), SNIS, Lei 14.026/2020.',
   '{"group":"vertical","segment":"saneamento","version":"v4.2","rag_prefix":"san:","new_agent":"2026-07-05","priority":"AySA","regulators":["ANA","ANA-Argentina"],"standards":["NBR 12211","NBR 12212","NBR 12213","Lei 14.026"]}'::jsonb),

  ('manta-03-s9', 'Energia', ARRAY['agente-energia','s9','energia','transmissao'], 'Sonnet', 'active',
   'Especialista em energia (LT, subestações, RAP, leilões). ANEEL, EPE, ONS, leilões de transmissão, regulação.',
   '{"group":"vertical","segment":"energia","version":"v4.2","rag_prefix":"ene:","new_agent":"2026-07-05","regulators":["ANEEL","EPE","ONS"],"standards":["IEEE 738","IEEE 80","NBR 5422"]}'::jsonb),

  ('manta-03-s10', 'Barragens', ARRAY['agente-barragens','s10','barragens','represas'], 'Sonnet', 'active',
   'Especialista em barragens, vertedouros, rejeitos, CFRD, CCR. ICOLD, CBDB, Lei 12.334/2010, SIGBM (ANM), Lei 14.066/2020.',
   '{"group":"vertical","segment":"barragens","version":"v4.2","rag_prefix":"bar:","new_agent":"2026-07-05","regulators":["ANM","ANA"],"standards":["Lei 12.334","Lei 14.066","NBR 13028","NBR 8681","ICOLD"]}'::jsonb)

ON CONFLICT (code) DO NOTHING;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_agents_code ON agents(code);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_segment ON agents(segment);
CREATE INDEX IF NOT EXISTS idx_agents_group ON agents((metadata->>'group'));
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at);

-- Comentários de documentação
COMMENT ON TABLE agents IS 'Registro master dos 20 agentes IA da Manta Associados v4.2 (11 horizontais + 10 verticais S1-S10)';
COMMENT ON COLUMN agents.code IS 'Código único do agente (manta-00 a manta-16, manta-03-s1 a manta-03-s10)';
COMMENT ON COLUMN agents.tier IS 'Model tier: Haiku, Sonnet, Opus, custom, Haiku→Sonnet (adaptive)';
COMMENT ON COLUMN agents.segment IS 'Segmento vertical (rodovias, oae, ferrovia, metro, tuneis, portos, aeroportos, saneamento, energia, barragens)';
COMMENT ON COLUMN agents.metadata IS 'Metadados customizados em JSONB (version, rag_prefix, modules, capabilities, regulators, standards, etc)';

COMMIT;
