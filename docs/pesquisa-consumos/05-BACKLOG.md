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

## Divergência de numeração a resolver com MN

A skill `manta-maestro` instalada se descreve como **v5.0.1** com numeração
diferente da deste repositório:

| Código | `manta-maestro` v5.0.1 | `CLAUDE.md` deste repo (v4.2/v4.3) |
|---|---|---|
| S6 | Edificações | **Portos** |
| S7 | Portos | **Aeroportos** |
| S8 | Aeroportos | **Saneamento** |
| S9 | Saneamento | **Energia** |
| S10 | Energia | **Barragens** |
| S11 | Barragens | — |

Esta base segue a numeração **deste repositório**. Remapear depois é um `sed` no
campo `setor`; escolher errado agora contaminaria todas as linhas. **Decisão de MN
necessária** antes de a base crescer.
