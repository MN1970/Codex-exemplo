# Extensão do registry aluci-guard — Aeroportos (Manta 03-S7)

Fonte: `sharepoint/01-agentes-fundamentais/agente-aeroportos/SKILL.md` (v1.0.0, 2026-07-05).

## Compatível com schema atual (normas_abnt.py / leis_federais.py)

- **normas_abnt.py**
  - `codigo`: "NBR 10151"
    `titulo`: "Norma citada no SKILL.md do agente-aeroportos como referência de avaliação de ruído (disciplina D10-ambiental: 'ruído NBR 10151, GEE, resíduos')"
    `status`: "a confirmar" (sem acesso à base oficial ABNT nesta etapa)
    `ano`: "a confirmar" (não informado no SKILL.md)

Nenhuma lei federal brasileira com número específico foi encontrada no SKILL.md (não há menção a "Lei nº .../AAAA" ou similar).

## Fora do schema atual (requer nova categoria de registry, ex.: normas_setoriais.py ou normas_internacionais.py)

- **ANAC RBAC 154** (+ apostilas) — Regulamento Brasileiro da Aviação Civil citado como base de projeto de aeródromos; referenciado em V2 (`axes/01-normas.md`), V4 (`aer-doc-rbac.md`), aba 4 do artefato ("Inteligência Setorial (RBAC, ICAO, FAA)"), regra 6 ("RBAC/ICAO/FAA existe e está vigente?") e regra 11 ("não inventar RBAC, ICAO Annex ou FAA AC").
- **ICAO Annex 14 Vol I** — "aerodrome design", citada em V2/`axes/01-normas.md` e Knowledge Engine (seção 4).
- **ICAO Annex 14 Vol II** — "heliports", citada nos mesmos pontos que o Vol I.
- **ICAO Doc 9157** — "Aerodrome Design Manual", citada na seção 4 (Knowledge Engine — Fontes iniciais).
- **FAA AC 150/5300-13** — "design", citada em V2/`axes/01-normas.md` e seção 4.
- **FAA AC 150/5320-6** — "pavimentos" (grafada no SKILL.md como "5320-6"), citada na seção 4.
- **FAA AC 150/5340** — "balizamento" (grafada no SKILL.md como "5340"), citada na seção 4.
- **DECEA ICA 100-12** — citada em V2 (`axes/02-regulatorio.md`) e seção 4 (Knowledge Engine).
- **DECEA MCA 4-14** — citada na seção 4 (Knowledge Engine — Fontes iniciais), junto com ICA 100-12.

## Observações

- Total extraído: 1 referência compatível com o schema atual (NBR 10151) e 9 referências fora do schema atual (ANAC RBAC 154, ICAO Annex 14 Vol I, ICAO Annex 14 Vol II, ICAO Doc 9157, FAA AC 150/5300-13, FAA AC 150/5320-6, FAA AC 150/5340, DECEA ICA 100-12, DECEA MCA 4-14).
- Nenhum status de vigência foi confirmado nesta etapa — todas as entradas exigem verificação posterior contra fonte oficial (ABNT para NBR 10151; ANAC, ICAO e FAA para as demais).
- Agências/órgãos citados sem número de instrumento normativo específico (ex.: ANAC como órgão, IBAMA em `axes/02-regulatorio.md`) não foram listados como entradas individuais de norma — apenas os códigos/instrumentos explícitos acima foram extraídos.
- Nenhuma norma foi inventada ou inferida além do que está escrito no SKILL.md; nenhuma verificação online de existência/vigência foi realizada.
