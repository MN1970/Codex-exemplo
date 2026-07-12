-- M-A — Registrar S1-S13 em manta_agent_capabilities
-- Ver: docs/AUDIT-v4.6-vs-PROD.md § Fase 2 M-A
--
-- Status: APLICADA em produção 2026-07-12 via MCP apply_migration
-- (nome interno da migração: m_a_register_verticals_s1_to_s13).
-- Este arquivo existe para rastreabilidade no repo — se aplicar de novo,
-- é idempotente via ON CONFLICT.

INSERT INTO public.manta_agent_capabilities
  (agent_id, capability, descricao, modelo_default, tags, ativo)
VALUES
  ('03-S1',  'especialista-rodovias',
   'Rodovias — pavimento CBUQ/BGS, terraplenagem, drenagem, SICRO. Ciclo completo estudo→DD.',
   'sonnet', ARRAY['rodovia','pavimento','CBUQ','BGS','terraplenagem','SICRO','DNIT','DER','vertical'], true),
  ('03-S2',  'especialista-oae',
   'OAE — pontes, viadutos, passarelas. NBR 7187, dimensionamento longarina/bloco/estaca, análise sísmica.',
   'sonnet', ARRAY['OAE','ponte','viaduto','NBR 7187','longarina','bloco','estaca','vertical'], true),
  ('03-S3',  'especialista-ferrovia',
   'Ferrovia — via permanente, dormente, AMV, trilho. FEC/Ferrogrão/EF-334, Vale, MRS.',
   'sonnet', ARRAY['ferrovia','trilho','AMV','dormente','via permanente','FEC','Ferrogrão','vertical'], true),
  ('03-S4',  'especialista-metro',
   'Metrô — estação, VLT, NATM, PSD, linha 4/5/6 SP. Sistemas metroviários.',
   'sonnet', ARRAY['metrô','metro','estação','NATM','PSD','VLT','Linha 4','Linha 5','Linha 6','vertical'], true),
  ('03-S5',  'especialista-tuneis',
   'Túneis — NATM/TBM/EPB, cut-and-cover, imersos (ITT), microtúneis. ITA/PIARC/NFPA 502.',
   'sonnet', ARRAY['túnel','tunel','NATM','TBM','EPB','cut and cover','ITT','dovela','PIARC','ITA','vertical'], true),
  ('03-S6',  'especialista-portos',
   'Portos — cais, píer, dolfins, dragagem, retroárea. ANTAQ/PIANC. Terminais marítimos+fluviais+hidroviários.',
   'sonnet', ARRAY['porto','terminal','ANTAQ','PIANC','dragagem','cais','píer','dolfin','vertical'], true),
  ('03-S7',  'especialista-aeroportos',
   'Aeroportos — pista, taxiway, pátio, RESA, TPS, TECA, balizamento. ANAC/RBAC 154/ICAO Annex 14.',
   'sonnet', ARRAY['aeroporto','pista','RBAC 154','ANAC','ICAO','TPS','TECA','balizamento','PCN','FAARFIELD','vertical'], true),
  ('03-S8',  'especialista-saneamento',
   'Saneamento — água, esgoto, drenagem, resíduos. PRIORIDADE AySA (Argentina). Lei 14.026 BR.',
   'sonnet', ARRAY['saneamento','ETA','ETE','adutora','esgoto','AySA','SNIS','Lei 14.026','vertical'], true),
  ('03-S9',  'especialista-energia',
   'Energia — transmissão (ANEEL/State Grid), SE, LT, condutor ACSR. Geração hidro/eólica/solar/térmica.',
   'sonnet', ARRAY['transmissão','LT','subestação','ANEEL','RAP','EPE','ONS','ACSR','HVDC','vertical'], true),
  ('03-S10', 'especialista-barragens',
   'Barragens — concreto (CCR/CFRD), terra, enrocamento, rejeitos (TSF). Pós-Brumadinho — Lei 14.066/2020, PNSB.',
   'sonnet', ARRAY['barragem','vertedouro','CFRD','CCR','rejeitos','TSF','PNSB','ICOLD','CBDB','Brumadinho','vertical'], true),
  ('03-S11', 'especialista-mineracao',
   'Mineração — cava/subterrânea/aluvionar. TSF encaminha para S10. NRM/NR-22 + SME/CIM/JORC/NI 43-101.',
   'sonnet', ARRAY['mineração','mina','minério','ANM','NRM','NR-22','JORC','NI 43-101','LOM','beneficiamento','vertical'], true),
  ('03-S12', 'especialista-oleo-gas',
   'Óleo & Gás — engenharia CIVIL. Downstream (refino) + midstream (dutos) + terminais. NÃO cobre reservatório/poço.',
   'sonnet', ARRAY['petróleo','óleo e gás','ANP','gasoduto','refinaria','API 650','ANSI B31','NFPA 30','HAZOP','vertical'], true),
  ('03-S13', 'especialista-edificacoes',
   'Edificações — vertical residencial/comercial + galpão + hospital/universidade. NBR 15575 (MCMV), LEED, BIM.',
   'sonnet', ARRAY['edificação','torre','galpão','warehouse','data center','MCMV','NBR 15575','LEED','BIM','vertical'], true)
ON CONFLICT (agent_id, capability) DO NOTHING;
