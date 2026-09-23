-- Rodada de testes T1 (docs/PLANO-TESTES-MAESTRO-v1.md), 2026-09-23.
-- Acrescenta rotas que faltavam em maestro_routing_keywords (antes: 61 linhas,
-- só 6 agentes). Somente INSERT, idempotente (PK agent_slug+keyword).
-- Verticais: prioridade 90–100 (mesma escala das linhas existentes).
-- Horizontais e ESG: prioridade 50 — só vencem quando nenhum vertical pontua
-- (o segmento decide o dispatch primário, CLAUDE.md "Modelo de composição").
-- Reverter: DELETE ... WHERE created_at >= '2026-09-23' AND keyword IN (...).

insert into public.maestro_routing_keywords (agent_slug, keyword, priority) values
  -- S6 Edificações
  ('agente-edificacoes', 'edificação', 100), ('agente-edificacoes', 'edifício', 90),
  ('agente-edificacoes', 'torre residencial', 100), ('agente-edificacoes', 'galpão', 100),
  ('agente-edificacoes', 'data center', 100), ('agente-edificacoes', 'NBR 15575', 100),
  ('agente-edificacoes', 'LEED', 90), ('agente-edificacoes', 'MCMV', 90),
  -- S12 Túneis
  ('agente-tuneis', 'túnel', 100), ('agente-tuneis', 'TBM', 100),
  ('agente-tuneis', 'EPB', 90), ('agente-tuneis', 'dovela', 90),
  ('agente-tuneis', 'emboque', 90), ('agente-tuneis', 'cut and cover', 90),
  -- S13 Mineração
  ('agente-mineracao', 'mineração', 100), ('agente-mineracao', 'lavra', 100),
  ('agente-mineracao', 'JORC', 100), ('agente-mineracao', 'mina', 90),
  ('agente-mineracao', 'minério', 90), ('agente-mineracao', 'NR 22', 90),
  -- S14 Óleo e Gás
  ('agente-oleo-gas', 'óleo e gás', 100), ('agente-oleo-gas', 'petróleo', 100),
  ('agente-oleo-gas', 'gasoduto', 100), ('agente-oleo-gas', 'oleoduto', 100),
  ('agente-oleo-gas', 'dutovia', 100), ('agente-oleo-gas', 'refinaria', 100),
  ('agente-oleo-gas', 'ANP', 100), ('agente-oleo-gas', 'API 650', 100),
  ('agente-oleo-gas', 'tancagem', 100), ('agente-oleo-gas', 'HAZOP', 90),
  ('agente-oleo-gas', 'duto', 90),  -- acrescentado após o teste E5 (T5)
  -- Termos que faltavam nos verticais existentes (falhas do T1)
  ('agente-portos', 'PIANC', 90), ('agente-portos', 'TUP', 90), ('agente-portos', 'cais', 90),
  ('agente-aeroportos', 'RBAC', 100), ('agente-aeroportos', 'PCN', 90),
  ('agente-aeroportos', 'RWY', 90), ('agente-aeroportos', 'taxiway', 90),
  ('agente-saneamento', 'PMSB', 100), ('agente-saneamento', 'Lei 14.026', 90),
  ('agente-energia', 'ampacidade', 90), ('agente-energia', 'ACSR', 90),
  ('agente-barragens', 'SIGBM', 100), ('agente-barragens', 'Lei 12.334', 100),
  ('agente-barragens', 'dam break', 100), ('agente-barragens', 'dam breach', 100),
  ('agente-barragens', 'PAEBM', 100),
  -- Horizontais (prioridade 50)
  ('agente-orcamento', 'orçamento', 50), ('agente-orcamento', 'SINAPI', 50),
  ('agente-orcamento', 'BDI', 50), ('agente-orcamento', 'composição de custo', 50),
  ('agente-cronograma', 'cronograma', 50), ('agente-cronograma', 'caminho crítico', 50),
  ('agente-cronograma', 'Gantt', 50),
  ('agente-claims', 'pleito', 50), ('agente-claims', 'reequilíbrio', 50),
  ('agente-claims', 'claim', 50), ('agente-claims', 'sinistro', 50),
  ('agente-contratual', 'contrato', 50), ('agente-contratual', 'aditivo', 50),
  ('agente-contratual', 'cláusula', 50), ('agente-contratual', 'força maior', 50),
  ('agente-contratual', 'rescisão', 50),
  ('agente-bd', 'proposta comercial', 50), ('agente-bd', 'oportunidade', 50),
  ('agente-bd', 'pipeline', 50),
  ('agente-advisory', 'parecer', 50), ('agente-advisory', 'segunda opinião', 50),
  ('agente-advisory', 'go/no-go', 50),
  ('agente-apresentacoes', 'apresentação', 50), ('agente-apresentacoes', 'deck', 50),
  ('agente-apresentacoes', 'PPTX', 50),
  ('agente-modelagem', 'modelagem financeira', 50), ('agente-modelagem', 'VPL', 50),
  ('agente-modelagem', 'TIR', 50),
  ('agente-imobiliario', 'zoneamento', 50), ('agente-imobiliario', 'desapropriação', 50),
  -- ESG (co-agente)
  ('manta-20-esg', 'ESG', 50), ('manta-20-esg', 'GHG', 50), ('manta-20-esg', 'carbono', 50),
  ('manta-20-esg', 'Escopo 1', 50), ('manta-20-esg', 'Escopo 2', 50),
  ('manta-20-esg', 'Escopo 3', 50), ('manta-20-esg', 'GRI', 50),
  ('manta-20-esg', 'TCFD', 50), ('manta-20-esg', 'net zero', 50),
  ('manta-20-esg', 'inventário de emissões', 50)
on conflict (agent_slug, keyword) do nothing;
