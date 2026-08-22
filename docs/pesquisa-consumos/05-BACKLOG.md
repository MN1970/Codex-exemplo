# Backlog

## Bloqueio a resolver primeiro

**Egress.** Toda a coleta desta rodada foi limitada porque a política de rede
bloqueia os domínios das fontes. Lista exata do que foi tentado e negado em
`../../data/consumos/validacao/relatorio.md`.

Para desbloquear: rodar a coleta de um ambiente com egress liberado para, no
mínimo, `ibge.gov.br` e subdomínios (`sidra`, `biblioteca`, `concla`,
`servicodados`, `apisidra`), `snic.org.br`, `acobrasil.org.br`,
`cbicdados.com.br`, `portal.fgv.br`, `gov.br`, `worldbank.org`,
`infralatam.info`, `oecd.org`, `ec.europa.eu`.

## Fase 2 — bottom-up por serviço

O detalhamento que esta rodada deliberadamente não fez. Coeficiente físico por
unidade de serviço:

| Setor | Exemplos de coeficiente |
|---|---|
| S6 Portos | dragagem `hm/m3` e `L diesel/m3`; enrocamento `t/m` de molhe; cravação `hm/m` |
| S7 Aeroportos | pavimento de pista `kg cimento/m3` e `t CAP/m2`; balizamento `un/km` |
| S8 Saneamento | rede `m3 escavação/m` e `hh/m` por DN e profundidade; ETA/ETE `m3 concreto` e `kg aço` por m3/dia de vazão |
| S9 Energia | LT `t aço/km` por classe de torre e tensão; `kg condutor/km`; SE `m3 concreto/módulo` |
| S10 Barragens | CCR `kg cimento+pozolana/m3`; CFRD `m3 enrocamento/m3`; vertedouro `kg aço/m3 concreto` |

Fontes: SICRO 4, SINAPI, BEDEC/ITeC, USACE MII, tabelas estaduais e de
concessionárias, *bid tabulations* de DOTs americanos.

Ponto técnico crítico da Fase 2, herdado do estudo desta rodada: **SICRO separa
hora produtiva de improdutiva (FIT/FIU); RSMeans e BEDEC não.** Comparar sem
declarar a separação gera erro sistemático relevante. O schema da Fase 2 precisa
de um campo `hora_produtiva_apenas`, e material precisa de `perda_incluida`
(SINAPI e BEDEC embutem perda, SICRO não).

## Perdas de material em canteiro

Camada própria, alimentada por Poli-USP/PCC `F-086` e NORIE/UFRGS `F-089`. A
diferença entre perda de norma e perda medida em campo chega a dezenas de pontos
percentuais e nenhuma tabela oficial captura. Alto valor, baixo custo de coleta
(literatura pública).

## Dado proprietário Manta

Extrair consumo real de medições e as-builts do SharePoint `03_Projetos/*`. É a
camada de maior valor e a única que nenhum concorrente tem. Depende de acesso ao
SharePoint. Regras de tier e anonimização em `04-GOVERNANCA-LICENCAS.md`.

## Infraestrutura diferida

Registrado no `CLAUDE.md` v4.3 como planejado, não construído:

- **Supabase** — tabela `consumos_ref` e coleção RAG `consumos` (prefixo `cns:`),
  no padrão da migração v4.2. Decisão de MN foi manter o repositório como fonte
  da verdade nesta rodada.
- **Agente horizontal Manta 17** (consumos/benchmarking), alimentando o
  `manta-05 (orcamento)`.
- **Artefato React** de consulta por setor e família, com faixas P10/P50/P90 e
  rastreabilidade da fonte.

## Numeração de segmentos — RESOLVIDA

A divergência sinalizada na primeira rodada **já estava resolvida** no
`CLAUDE.md` da `main` (v5.0/v5.0.1, consolidado em v5.1). Vale registrar como
ficou, porque a decisão tem lastro melhor do que documentação:

A **Convenção A** é a canônica — `S6 = Portos … S10 = Barragens`, exatamente a
numeração que esta base adotou. Não por escolha editorial: a investigação G014
(`docs/SEGMENTOS-S12-S13-DECISION.md`) consultou a fonte de verdade real —
`manta_agent_capabilities` no Supabase de produção — e encontrou `agent_id` de
`03-S1` a `03-S13` na numeração legada. A Convenção B (S6 = Edificações …
S11 = Barragens), que a skill `manta-maestro` instalada ainda descreve, **não
tem lastro em dado de produção**.

Nenhum remapeamento foi necessário. O `setor` das linhas desta base já está
correto.

Segmentos adicionais incorporados ao schema e ao crosswalk nesta rodada:

| Código | Segmento | Estado no registro mestre |
|---|---|---|
| **S11** | Mineração (`especialista-mineracao`) | `ativo=true` em produção desde 2026-07-12; sem agente `.md`, RAG ou routing — gap **G015** |
| **S12** | Óleo & Gás | proposto, pendente gate MN |
| **S13** | Edificações | proposto, pendente gate MN |

Notas de cobertura estatística desses três:

- **S13 Edificações** é o de melhor cobertura de todos — tem divisão CNAE
  própria (41), e as linhas de `C41` desta base já servem diretamente para ele.
- **S12 Óleo & Gás** tem par limpo no trecho de dutos: CNAE 42.23-5 ↔
  NAICS 237120. Upstream (sonda, plataforma, refino) não é construção civil e
  fica fora do escopo.
- **S11 Mineração** é o pior caso: é indústria **extrativa** (CNAE seção B),
  não construção. Só a parcela de obra civil do projeto entra, e cai no
  residual 42.99-5. Intensidade via PAIC será muito imprecisa; usar fonte
  setorial.
