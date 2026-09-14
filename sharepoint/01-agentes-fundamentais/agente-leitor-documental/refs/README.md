# refs/ — agente-leitor-documental

Este agente não tem bibliografia de norma técnica própria (não é um
vertical de segmento). As referências aqui são sobre **as skills de
formato que ele orquestra** e o schema de normalização.

## Skills de leitura por formato (já existentes no catálogo Manta)

- `pdf` — leitura de texto/tabela em PDF.
- `xlsx` — leitura/escrita de planilhas Excel.
- `docx` — leitura/escrita de documentos Word.
- `pptx` — leitura/escrita de apresentações PowerPoint.
- `autodesk-toolkit` — DWG, DXF, IFC, RVT, NWD, NWC, LandXML.
- `cronograma-toolkit` — XER (Primavera P6), MPP/XML MSPDI (MS Project).

## Extratores especializados (acionados quando o subtipo é reconhecido)

- `evtea-extractor` — PDFs de EVTEA rodoviário (DNIT EB-101).
- `ler-edital` — editais de licitação de obras públicas.
- `ler-edital-aneel` — editais ANEEL de transmissão.
- `leitura-diagrama-engenharia` — plantas/diagramas técnicos escaneados.
- `cad-quantifier` / `cqp-cad-bridge` — quantitativos a partir de CAD.

## Schema de normalização

Ver seção 4 do `SKILL.md` (`doc_id`, `hash`, `formato_origem`,
`doc_type`, `agente_dono`, `fase_ciclo_vida`, `origem`,
`campos_extraidos`, `fonte`, `processado_em`). Qualquer skill nova
adicionada ao catálogo que produza dados de documento deve mapear sua
saída para este schema antes do handoff a um agente vertical.

## Tabelas de apoio (Supabase)

- `sp_agent_routing` — pasta SharePoint → agente dono (já existe desde
  v4.2, reaproveitada aqui).
- `rag_collections` — coleção RAG por segmento (destino final dos
  chunks extraídos).
- Índice de controle próprio deste agente (proposto na migração
  v4.3): tabela `doc_processing_index` (hash, formato, agente_dono,
  status, processado_em).
