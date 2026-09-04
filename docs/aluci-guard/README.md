# Extensão do registry `aluci-guard` — agentes S6-S10

Consolidação das 5 extrações paralelas (uma por agente vertical novo da
v4.2) das referências normativas/legais/técnicas citadas em cada
`sharepoint/01-agentes-fundamentais/agente-<segmento>/SKILL.md`, feitas
para alimentar o registry local da skill `aluci-guard`
(validador anti-alucinação — Cap 16.3, Pacote A: AL-01 norma ABNT/lei
fabricada, AL-02 URL/DOI inventado, AL-03 código SICRO inexistente).

Arquivos individuais:

- `registry-extension-portos.md` (Manta 03-S6)
- `registry-extension-aeroportos.md` (Manta 03-S7)
- `registry-extension-saneamento.md` (Manta 03-S8)
- `registry-extension-energia.md` (Manta 03-S9)
- `registry-extension-barragens.md` (Manta 03-S10)

## Achado principal

O registry atual do `aluci-guard` só tem 3 categorias:
`registry/normas_abnt.py`, `registry/leis_federais.py`,
`registry/sicro.py`. Das ~57 referências extraídas nos 5 SKILL.md, a
maioria **não cabe em nenhuma das 3** — são resoluções de agência
reguladora setorial (ANEEL, ANTAQ, ANAC, ANM, ONS, EPE, CONAMA) ou
normas/bulletins internacionais (ICOLD, CBDB, PIANC, ROM, IEEE, IEC,
ICAO, FAA, DECEA, USACE/FEMA, IWA, e as argentinas ERAS/PIRHA/AySA).

| Segmento | Compatível (ABNT/lei federal) | Fora do schema (setorial/intl) |
|---|---|---|
| Portos (S6) | 2 (NBR 9782, NBR 6122) | 9 (ANTAQ, PIANC, ROM 0.2/2.0, NORMAM, IBAMA, DHN, EIA/RIMA...) |
| Aeroportos (S7) | 1 (NBR 10151) | 9 (RBAC 154, ICAO Annex 14 Vol I/II, ICAO Doc 9157, FAA ACs, DECEA...) |
| Saneamento (S8) | 3 (NBR 12211-12218, NBR 9648-9651, Lei 14.026/2020) | 7 (SNIS, PRC 05/2017, CONAMA 357/430, IWA, AySA, ERAS, PIRHA) |
| Energia (S9) | 4 (NBR 5422, 6118, 6122, 6123) | 9 (IEEE 738/80, IEC 60826/61850, ANEEL, EPE, ONS, CCEE, CIGRÉ) |
| Barragens (S10) | 5 (Lei 12.334/2010, Lei 14.066/2020, NBR 13028, 8681, 6122) | 8 (ICOLD 194/164/72, CBDB, ANM Res. 95/2022, SNISB, SIGBM, USACE/FEMA) |
| **Total** | **15** | **42** |

Duas ressalvas que os agentes sinalizaram e que valem revisão humana:
- As faixas `NBR 12211-12218` e `NBR 9648-9651` (saneamento) estão
  citadas como intervalo no SKILL.md, não número a número — para
  popular `normas_abnt.py` linha a linha é preciso decompor contra o
  catálogo oficial ABNT.
- `ICOLD Bulletin 194` aparece com duas descrições de assunto
  diferentes em pontos distintos do SKILL.md de barragens (possível
  inconsistência interna do próprio documento) — conferir antes de
  cadastrar.

## Decisão pendente (gate MN)

Nenhuma entrada foi verificada quanto à existência/vigência real — os
5 agentes só extraíram o que já estava escrito nos SKILL.md, por
desenho (não têm acesso à base oficial ABNT/Planalto/ICOLD). Antes de
popular o registry de produção, decidir:

1. **Nome e formato da(s) categoria(s) nova(s)** — proposta dos
   agentes: `registry/normas_setoriais.py` (resoluções de agência
   reguladora: ANEEL, ANTAQ, ANAC, ANM, ONS, EPE, CONAMA) separado de
   `registry/normas_internacionais.py` (ICOLD, CBDB, PIANC, ROM, IEEE,
   IEC, ICAO, FAA, DECEA, USACE/FEMA, IWA). Saneamento ainda sugere uma
   fatia própria para o marco argentino (ERAS/PIRHA/AySA), já que o
   agente tem prioridade AySA.
2. **Quem confirma vigência** — este repo não tem acesso online às
   bases oficiais; alguém precisa validar as 57 entradas antes de
   marcá-las `vigente` no registry real (hoje todas estão como "status
   a confirmar").
3. **Onde o registry de produção vive** — a skill `aluci-guard`
   instalada hoje (`/root/.claude/skills/synced/.../aluci-guard/`) só
   tem o `SKILL.md`; `auditor.py` e `registry/*.py` descritos na
   própria documentação não estão presentes nesse ambiente. Definir se
   o código-fonte da skill mora em outro repo (para abrir PR lá) antes
   de tentar aplicar estas 57 entradas em algum lugar.

## Próximo passo

Depois da decisão MN acima, transformar estas 5 listas markdown em
`registry/normas_abnt.py` (15 entradas), `registry/leis_federais.py`
(3 entradas: Lei 14.026/2020, Lei 12.334/2010, Lei 14.066/2020) e os
novos `registry/normas_setoriais.py` / `registry/normas_internacionais.py`
(42 entradas), no repositório onde o código do `aluci-guard` de fato
vive.
