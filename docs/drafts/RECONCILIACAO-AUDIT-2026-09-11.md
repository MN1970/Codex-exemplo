# Auditoria de Reconciliação — Codex-exemplo vs. SharePoint `INDICE-CANONICAL.md` v1.1

**Data da auditoria**: 2026-09-11
**Baseline "real"**: SharePoint `INDICE-CANONICAL.md` v1.1, verificado 2026-09-07 (fora deste repositório — ground truth, não um arquivo local).
**Escopo**: todos os arquivos deste repositório que mencionam códigos de segmento/disciplina, contagem de agentes, ou o modelo "Eixo S/A/D/F".
**Nota metodológica**: `CLAUDE.md` foi lido diretamente do disco nesta sessão e está em **v4.3.0-draft** (2026-09-11, draft da proposta Manta 17/geotecnia) — mais recente que a versão v4.2.1 citada nas instruções do projeto. A auditoria usa o conteúdo real em disco.

---

## Achado estrutural nº 1 (o mais importante) — modelo de eixos obsoleto em todo o repositório

**Real (ground truth)**: 4 eixos ortogonais —
- **Eixo S (Segmentos)**: 14, S1–S14 (S1 Rodovias, S2 OAE, S3 Ferrovia, S4 Metrô, **S5 Imobiliário**, **S6 Edificações**, **S7 Portos**, **S8 Aeroportos**, **S9 Saneamento**, **S10 Energia**, **S11 Barragens**, S12 Túneis "a confirmar", S13 Mineração "a confirmar", S14 Óleo e Gás "a confirmar").
- **Eixo A (Atividades)**: 11, A1–A11 (A1 Proposta, A2 Quantidades, A3 Orçamento, A4 Modelagem, A5 Cronograma, A6 Contratual, A7 Claims, A8 Advisory, A9 Regulatório, A10 Risco, A11 Fiscalização "a confirmar").
- **Eixo F (Funcionais)**: 10, F1–F10.
- **Eixo D (Disciplinas)**: 22, D01–D22.

**Repositório**: todo documento de arquitetura (`CLAUDE.md`, `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`) descreve **"3 eixos"** — Horizontais / Verticais por segmento / Ciclo de vida (8 fases) — sem qualquer menção a Atividades, Funcionais ou Disciplinas como eixos formais do sistema. Isso não é um detalhe: é o modelo inteiro de organização do Maestro, e está desatualizado em nível de arquitetura, não só de conteúdo pontual.

Consequência prática: a renumeração de segmentos abaixo (achado nº 2) é só a manifestação mais visível deste problema maior — o repositório nunca teve como saber que o eixo de Atividades ganhou A2/A9/A10/A11, que existe um eixo Funcionais inteiro (F1–F10), ou que Disciplinas (D01–D22) é um eixo formal e não uma lista informal dentro de cada SKILL.md.

---

## Achado estrutural nº 2 — renumeração dos segmentos verticais (S6–S10 → S7–S11) não refletida em lugar nenhum

**Real**: S7=Portos, S8=Aeroportos, S9=Saneamento, S10=Energia, S11=Barragens (deslocados em +1 pela inserção de **S5=Imobiliário** e **S6=Edificações**, dois segmentos que este repositório desconhece por completo).

**Repositório**: todos os arquivos usam a numeração antiga **S6=Portos, S7=Aeroportos, S8=Saneamento, S9=Energia, S10=Barragens** — a numeração da v4.2 (2026-07-05), nunca corrigida. Isso está presente, de forma idêntica, em:

- `CLAUDE.md` — tabela "Eixo 2", bloco `ROUTING`, tabela RAG, tabela SharePoint, seção "PROPOSTA — Manta 17" (linhas 34–47, 68–110, 118–136, 165–187).
- `.claude/agents/agente-portos.md` (frontmatter `Manta 03-S6` + título + corpo), `agente-aeroportos.md` (`Manta 03-S7`), `agente-saneamento.md` (`Manta 03-S8`), `agente-energia.md` (`Manta 03-S9`), `agente-barragens.md` (`Manta 03-S10`).
- `sharepoint/01-agentes-fundamentais/agente-{portos,aeroportos,saneamento,energia,barragens}/SKILL.md` — mesmo padrão em `manta_code:` do frontmatter e no corpo (ex.: `agente-portos/SKILL.md:3` `manta_code: "Manta 03-S6"`; `aliases: ["manta-03-s6", ...]`).
- `sharepoint/01-agentes-fundamentais/*/README.md` (ex.: `agente-portos/README.md:1` `# agente-portos (Manta 03-S6)`).
- `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md` — tabela do Eixo 2 (linhas 67–78) e bloco de routing (linhas 154–168).
- `docs/DEPLOY-v4.2.md` — título do runbook e checklists referenciam S6–S10.
- `docs/COWORK-INTEGRATION.md` — prefixos RAG `por:/aer:/san:/ene:/bar:` associados aos números antigos implicitamente via `CLAUDE.md`.
- `tests/routing/prompts.md` — cabeçalhos `## S6 — Portos`, `## S7 — Aeroportos`, `## S8 — Saneamento`, `## S9 — Energia`, `## S10 — Barragens`.
- `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql` — nome do arquivo e comentários (`-- Manta Maestro v4.2 — expansão de agentes S6-S10`).

Nenhum arquivo do repositório usa a numeração real (S7–S11). O conteúdo técnico de domínio de cada agente (normas, fórmulas, handoffs) não é afetado por isso — só o **código do segmento** está errado; ver seção "O que está correto" abaixo.

**Ação recomendada**: renumerar globalmente S6→S7, S7→S8, S8→S9, S9→S10, S10→S11 em todos os arquivos listados, de uma vez (é um find-and-replace mecânico, mas toca ~15 arquivos).

---

## `CLAUDE.md`

| # | Linha(s) | Trecho | Problema |
|---|---|---|---|
| 1 | 15 | `## MAPA COMPLETO DE AGENTES — 20 agentes operacionais + 1 proposto, 3 eixos` | Real: 21 agentes operacionais já confirmados (12 horizontais incl. **Manta 20-ESG** + 9 verticais operacionais). O repositório não tem nenhuma menção a um agente ESG — nem no eixo horizontal (11 linhas, não 12) nem em lugar algum. Contagem "20 + 1 proposto" não bate com "21 operacionais" real. |
| 2 | 17–32 | Tabela "Eixo 1 — Horizontais" (11 linhas + Manta 17 proposto) | Faltam o(s) agente(s) horizontal(is) 18/19/20, incl. **Manta 20-ESG**, confirmados como operacionais no real. Repositório não tem visibilidade de nenhum deles. |
| 3 | 34–47 | Tabela "Eixo 2 — Verticais" (S1–S10) | Numeração antiga (ver achado estrutural nº 2). Além disso, **S5 (Túneis, "parcial coberto por S2/S4")** não corresponde ao real: no real, Túneis é **S12**, um segmento próprio (conteúdo "a confirmar"), não fundido em S2/S4. O real **S5 é Imobiliário** (que aqui aparece só como horizontal "Manta 04"), e o real **S6 é Edificações**, ausente por completo do repositório. |
| 4 | 49–59 | "Eixo 3 — Ciclo de vida (8 fases)" | Este conceito não corresponde a nenhum dos 4 eixos reais confirmados (S/A/D/F). Pode ser um sub-modelo legítimo dentro do eixo Atividades, mas não está documentado como tal, e o repositório o trata como um "eixo" próprio — o que contradiz o modelo real de 4 eixos. |
| 5 | 63–110 | Bloco `ROUTING` | Todas as 5 regras de S6–S10 usam a numeração antiga (ver achado nº 2). Comentário na linha 83 ("Regras existentes S1-S4 mantidas sem alteração") está correto para S1-S4, mas nada no bloco cobre S5(Imobiliário)/S6(Edificações)/S12-S14 reais. |
| 6 | 114–123 | Tabela RAG — 5 coleções (+ geotecnia proposta) | Só 6 coleções (5 operacionais + geotecnia proposta) documentadas; nenhuma menção às coleções que os novos segmentos reais (S5-Imobiliário-vertical, S6-Edificações, S12-14) precisariam, nem a qualquer coleção ligada aos eixos A/F/D. |
| 7 | 140–156 | "MODELO MESTRE DE PROPOSTA" — `agente A7-bd/Manta 13-bd` | **Inconsistência interna + contradição com o real**: o próprio `CLAUDE.md` nunca usa o código "A7" em nenhuma outra tabela (lista "Manta 13" para `bd`). E no eixo Atividades real, **A7 = Claims** (já ocupado por "Manta 01 | claims" nesta mesma tabela), não Proposta. Se o autor tentou mapear `bd`/propostas para o eixo Atividades real, o código correto seria **A1 (Proposta)**, não A7. Esse mesmo erro se repete em `docs/MODELO-MESTRE-PROPOSTA.md:9-10`. |
| 8 | 160–205 | "PROPOSTA — Manta 17 (geotecnia/geologia)" — "**Gap identificado**: nenhum dos 20 agentes cobre geotecnia/geologia como disciplina própria" | **Contradiz diretamente o real**: `D03-Geotecnia` já existe como Disciplina viva no SharePoint (`SKILL.md` v2.0.0), com segmentos-clientes típicos S1, S2, S3, S4, S7(Portos), S11(Barragens). A premissa central da proposta — que "não existe hoje" cobertura de geotecnia — está desatualizada; o gap real (se houver) é outro: por exemplo, D03 real ainda não lista S12-Túneis, apesar de NATM/maciço rochoso claramente exigir a disciplina — mas isso é uma lacuna a resolver na fonte (SharePoint), não algo que valide a criação de um Manta 17 do zero. Recomenda-se reabrir a análise verificando se D03 (Eixo Disciplinas) já cobre a necessidade antes de prosseguir com o agente horizontal proposto. |
| 9 | 162 | "nenhum dos 20 agentes cobre..." | Mesmo problema de contagem do item 1 (20 vs. 21 real) reaparece aqui. |
| 10 | 211–220, 224–237 | Checklists de deploy v4.2 e v4.3 | Sem contradição de conteúdo — describem passos pendentes reais deste repo (não a produção). Não stale por si só, mas dependem dos achados acima para fazer sentido (ex.: "criar pasta SP `03_Projetos/Geotecnia/`" presume que geotecnia ainda não existe, o que o achado 8 questiona). |
| 11 | 241–259 | Bloco "Arquivos deste repositório" | Consistente com o que existe fisicamente no repo (inclui `agente-geotecnia.md`). Sem problema. |
| 12 | 265–277 | Histórico de versões | Consistente internamente (v4.1→v4.2→v4.2.1→v4.3.0-draft). Sem problema de leitura, mas herda a numeração antiga de segmentos citada em v4.2. |

---

## `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`

Este documento é o mais desatualizado do repositório: é datado 2026-07-05 (v2.0.0), **anterior** até à proposta Manta 17 e à v4.2.1. Portanto herda todos os problemas de v4.2 sem nenhuma das atualizações posteriores.

| Linha(s) | Trecho | Problema |
|---|---|---|
| 14, 38 | `## 2. 3 eixos do sistema` | Mesmo problema do achado estrutural nº 1 — modelo de 3 eixos, real são 4 (S/A/D/F). |
| 30 | "20 agentes especializados" | Real: 21 operacionais. Também não inclui Manta 17 (nem como proposto — este doc é anterior a ele). |
| 43–60 | Tabela "Eixo 1 — Horizontais (11 agentes transversais)" | Só 11; falta ao menos o agente ESG (Manta 20) confirmado no real. |
| 62–78 | Tabela "Eixo 2 — Verticais (9 agentes operacionais)" | Numeração antiga S6–S10 (achado nº 2); "9 agentes operacionais" bate certo com o número real de verticais operacionais (9), mas por acidente — a lista de quais 9 está desatualizada (deveria refletir S1-S4 + S7-S11, não S1-S4 + S6-S10; e não inclui S5/S6 reais). |
| 194–209 | Tabela "Knowledge Engine (RAG)" | Mesmas 9 coleções antigas; sem geotecnia (nem como proposta, por ser anterior). |
| 220–234 | Tabela "SharePoint routing" | Mesma numeração antiga refletida nos nomes de agente (não nos códigos numéricos diretamente, mas a tabela do item 2 acima já fixa a associação errada). |
| 271–296 | "Changelog v1.0 → v2.0" | "Total de agentes: 15 → 20" — consistente com o histórico da época (correto para v2.0.0 em 2026-07-05), mas não reflete nada pós-v4.2. Não é uma contradição do próprio documento, só está congelado no tempo — junto com o "10. Referências" que cita `viniciusmagnos/manta-hub` como mirror operacional sem qualquer atualização desde então. |

---

## `docs/PROPOSTA-AGENTE-GEOTECNIA-GEOLOGIA.md`

| Linha(s) | Trecho | Problema |
|---|---|---|
| 3–8, 17–35 | "não existe hoje um agente especialista em geotecnia/geologia" / tabela "Onde geotecnia aparece hoje" | Mesma contradição do achado `CLAUDE.md` item 8: **D03-Geotecnia já existe** como Disciplina real, com SKILL.md v2.0.0 e mapeamento explícito a S1/S2/S3/S4/S7(Portos)/S11(Barragens). A tabela do documento ("Onde geotecnia aparece hoje: Manta 03-S1, S2, S4/S5, S10, Manta 04") usa a numeração antiga de segmentos e ignora completamente a existência do Eixo D real. O gap descrito (perguntas geotécnicas "puras" sem base compartilhada) pode já estar resolvido por D03 na fonte oficial — precisa reverificação antes de prosseguir com o agente Manta 17. |
| 19 | "Revisando o CLAUDE.md master (v4.2.1, 20 agentes)..." | Contagem desatualizada (real: 21 operacionais) — e a versão citada (v4.2.1) já não é a do `CLAUDE.md` atual em disco (v4.3.0-draft), embora isso seja esperado já que este doc é anterior ao merge da própria proposta. |
| 36–49 | "Por que horizontal, não um novo vertical S11" | Nomenclatura de risco: o real já usa **S11 para Barragens**. Se este agente fosse mesmo criado como vertical (o que o documento rejeita, com razão, por motivos de domínio), o próximo número livre real não seria S11 — estaria em conflito direto com Barragens. Isso reforça (por acidente) que "horizontal" é a escolha certa, mas o texto do documento não tem como saber que S11 já está ocupado no real. |

---

## `docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`

Nenhuma contradição direta com o eixo S/A/D/F — o documento trata de estrutura de proposta comercial (seções 1-18), não de segmentos/disciplinas. Sem menção a "A7-bd" (diferente do `MODELO-MESTRE-PROPOSTA.md`), então não herda o erro de numeração de Atividades. **Sem achados de discrepância** contra o real state fornecido.

## `docs/MODELO-MESTRE-PROPOSTA.md`

| Linha(s) | Trecho | Problema |
|---|---|---|
| 9–10 | "consumida pelo agente **A7-bd**, ver CLAUDE.md" | Mesmo erro do `CLAUDE.md` item 7: A7 no eixo Atividades real é **Claims**, não Proposta/BD. O código correto seria A1 (Proposta). `CLAUDE.md` não define "A7-bd" em nenhuma tabela própria — a referência é uma alegação não sustentada pelo próprio arquivo que ela cita. |
| Resto do documento | — | Conteúdo de análise de proposta comercial (mapeamento de seções, recomendação M6) não depende de segmentos/disciplinas — sem outras discrepâncias contra o real state fornecido. |

## `docs/DEPLOY-v4.2.md`

| Linha(s) | Trecho | Problema |
|---|---|---|
| 1, 8 | Título / "Portos, Aeroportos, Saneamento, Energia, Barragens" | Runbook histórico do ticket v4.2 (2026-07-05) — descreve corretamente o que a v4.2 fez **na época**, com a numeração então vigente (S6-S10). Não é uma "mentira" no sentido de nunca ter sido verdade, mas está desatualizado frente à renumeração real e nunca foi revisado. |
| 17–19 | "Revisar `MN1970/Codex-exemplo#1`... Revisar `viniciusmagnos/manta-hub#3`" | Checklist de PRs específicos da v4.2; não verificável aqui, mas não contradiz o real state fornecido diretamente — apenas processo interno de merge. |
| 191–203 | "Estado atual (por seção)" | Consistente internamente com o próprio runbook (não afirma nada como "resolvido" que o conteúdo do arquivo desminta) — todos os itens pendentes seguem `[ ]`. Sem contradição "resolvido vs. não resolvido". |

## `docs/COWORK-INTEGRATION.md`

| Linha(s) | Trecho | Problema |
|---|---|---|
| 4, 33, 96, 111 | "20 agentes" (4 ocorrências) | Mesma contagem desatualizada (real: 21 operacionais + numeração de segmentos deslocada). |
| 35 | "9 coleções RAG (prefixos rod:/oae:/fer:/mtr:/por:/aer:/san:/ene:/bar:)" | Falta a coleção `geo:` (geotecnia, ainda que só proposta no `CLAUDE.md` atual) e qualquer coleção para os segmentos reais ausentes (S5-Imobiliário-vertical, S6-Edificações, S12-14). Não é tecnicamente "errado" para o momento em que foi escrito (antes da proposta Manta 17), mas está desatualizado frente ao próprio `CLAUDE.md` atual do repo. |
| Resto do documento | Runbook de integração Cowork/MCP | Não depende de segmentos/disciplinas para o conteúdo central (OAuth, custom connector, roadmap Fase B) — sem outras discrepâncias diretas contra o real state. |

## `.claude/agents/agente-{portos,aeroportos,saneamento,energia,barragens}.md`

Todos os 5 arquivos têm o mesmo padrão de problema, já coberto no achado estrutural nº 2:

- `agente-portos.md:1-8` — `Manta 03-S6` (real: S7).
- `agente-aeroportos.md:1-8` — `Manta 03-S7` (real: S8).
- `agente-saneamento.md:1-8` — `Manta 03-S8` (real: S9).
- `agente-energia.md:1-8` — `Manta 03-S9` (real: S10).
- `agente-barragens.md:1-8` — `Manta 03-S10` (real: S11).

**O que está correto** nesses 5 arquivos: todo o conteúdo técnico de domínio (normas, fórmulas, listas de handoff entre agentes, o que cada agente não faz) é consistente internamente e não é contradito por nada no real state fornecido — a única coisa desatualizada é o rótulo numérico do segmento.

## `sharepoint/01-agentes-fundamentais/agente-{portos,aeroportos,saneamento,energia,barragens}/{SKILL.md,README.md}`

Mesmo padrão: `manta_code` no frontmatter e o código no título/corpo usam a numeração antiga (S6–S10 em vez de S7–S11). Exemplos:
- `agente-portos/SKILL.md:3` `manta_code: "Manta 03-S6"`.
- `agente-saneamento/SKILL.md:3` `manta_code: "Manta 03-S8"`.
- `agente-portos/README.md:1` `# agente-portos (Manta 03-S6)`.

Além disso, cada `SKILL.md` define uma numeração interna própria de disciplinas (`V5 — N Disciplinas`, ex.: `disciplines/D01-mananciais.md` … `D12-reuso.md` em saneamento; `D01-batimetria.md` … `D10-ambiental-costeiro.md` em portos). **Isto não é uma discrepância factual** — são listas de módulos internos por agente, numeradas independentemente — mas é um risco de confusão de nomenclatura: um leitor pode achar que esse `D01…D12` por agente é o mesmo Eixo D (Disciplinas, D01–D22) real e transversal. Vale desambiguar (ex.: renomear para `M01…M12` ou "módulo" em vez de "disciplina D0N") para não colidir com o eixo real quando ele for adotado neste repositório.

`sharepoint/01-agentes-fundamentais/*/refs/README.md` e `*/prompts/starters.md`: conteúdo bibliográfico e de prompts de exemplo — não fazem referência a contagens de agentes/segmentos, sem discrepância própria além de herdar o `manta_code` do `SKILL.md` correspondente.

`sharepoint/README.md`: descreve apenas a estrutura de espelho de pastas; sem números de segmento ou contagem de agentes — **sem achados**.

## `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`

- Nome do arquivo e comentário de cabeçalho (`-- Manta Maestro v4.2 — expansão de agentes S6-S10`) usam a numeração antiga — mas como é uma migração já executada/candidata amarrada a um ticket histórico (`MNT-2026-UPGRADE-AGENTS-S6S10`), renomear o arquivo não é indicado (quebraria rastreabilidade); o conteúdo (slugs `agente-portos`, `agente-saneamento` etc., prefixos `por:`/`san:`/etc.) continua válido porque os **nomes** dos agentes não mudaram — só os números de segmento. **Sem ação necessária no SQL em si**, só ciência de que os comentários citam a numeração antiga.

## `tests/routing/prompts.md`

- Cabeçalhos `## S6 — Portos`, `## S7 — Aeroportos`, `## S8 — Saneamento`, `## S9 — Energia`, `## S10 — Barragens` usam a numeração antiga (real: S7/S8/S9/S10/S11). Os prompts de teste em si e os agentes-alvo (`agente-portos`, `agente-energia`, etc.) continuam válidos — só o rótulo do cabeçalho de seção está desatualizado.
- Seção final "Casos ambíguos / desafiadores" (UHE, ETE+subestação, porto+pista) — conteúdo de política de routing, não depende de numeração — **sem discrepância**.

## `README.md` (raiz)

| Linha(s) | Trecho | Problema |
|---|---|---|
| 6 | "registro mestre dos 20 agentes" | Mesma contagem desatualizada (real: 21 operacionais). |
| 8–9, 19–24 | ".claude/agents/*.md — definições canônicas... S6–S10" | Numeração antiga; também não menciona mais `agente-geotecnia.md`, que já existe fisicamente no repo (`.claude/agents/agente-geotecnia.md`) — este README não foi atualizado desde a v4.2, ficando atrás até do próprio `CLAUDE.md` em disco (v4.3.0-draft). |
| 27–29 | "Versão atual: v4.2.1" | Desatualizado frente a `CLAUDE.md` em disco, que já está em v4.3.0-draft. |

---

## Achado nº: "agente-oleo-gas" / "Mineração" mencionados no briefing da auditoria

O briefing da auditoria alertou para reverificar `agente-oleo-gas` e um agente "Mineração" que supostamente "existem em alguns arquivos locais". **Busca por `oleo-gas`, `óleo e gás` e `Mineração` neste repositório não encontrou nenhum agente com esse nome ou escopo.** As únicas ocorrências de "Mineração" são referências a **clientes** (ex.: "Mineração Rio do Norte" como cliente de EPC de barragens em `sharepoint/01-agentes-fundamentais/agente-barragens/refs/README.md:127`) e ao setor de mineração no contexto de rejeitos/ANM dentro do `agente-barragens`. **Portanto, neste repositório específico (`Codex-exemplo`), não há arquivo que precise reconciliação quanto a S13-Mineração/S14-Óleo e Gás — a omissão é total (nenhuma menção), não uma contradição de conteúdo.** Isso deve ser reverificado no repositório operacional (`manta-hub`) ou no próprio SharePoint, não aqui.

---

## Resumo do que está CORRETO / não precisa de correção

- O conteúdo técnico de domínio de cada agente vertical (normas, fórmulas, cálculos, o que cada agente não faz) em `.claude/agents/*.md` e nos `SKILL.md` espelhados — não é contradito por nada no real state fornecido.
- As relações de handoff entre agentes (ex.: saneamento ↔ energia, portos ↔ infraestrutura S1/S2) — consistentes e plausíveis, sem contradição.
- A lógica de palavras-chave de routing em si (quais termos apontam para qual agente) — funcionalmente ainda válida; só o rótulo numérico do segmento anexado está errado.
- `docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md` — sem discrepância contra o real state (não trata de segmentos/disciplinas).
- O processo de gate humano (MN) descrito em `CLAUDE.md`, `docs/DEPLOY-v4.2.md` e `docs/PROPOSTA-AGENTE-GEOTECNIA-GEOLOGIA.md` — nenhum arquivo afirma falsamente que algo já foi aprovado/mergeado; todos os itens pendentes seguem marcados `[ ]` corretamente.
- A migração SQL (`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`) é estruturalmente correta (idempotente, com bloco de rollback) — só o comentário de cabeçalho usa numeração antiga, sem necessidade de alterar o arquivo em si.
- `sharepoint/README.md` — descrição de estrutura de mirror, sem números de segmento/contagens — sem achados.
- O histórico de versões em `CLAUDE.md` (v4.1 → v4.2 → v4.2.1 → v4.3.0-draft) é internamente consistente — não afirma nada como "resolvido" que o conteúdo desminta.

---

## Prioridade de correção sugerida

1. **Resolver a contradição de premissa da proposta Manta 17** (`CLAUDE.md` seção "PROPOSTA — Manta 17", `docs/PROPOSTA-AGENTE-GEOTECNIA-GEOLOGIA.md`) — verificar se D03-Geotecnia (real, já em produção) já cobre o gap antes de prosseguir com um agente horizontal novo. Maior risco de trabalho duplicado/desperdiçado.
2. **Renumerar globalmente S6→S7 … S10→S11** em todo o repositório (achado estrutural nº 2) — mecânico, mas toca ~15 arquivos; sem isso, todo teste de routing e toda pasta SharePoint futura nascerá com o código errado.
3. **Atualizar o modelo de eixos** em `CLAUDE.md` e `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md` de "3 eixos" para os 4 eixos reais (S/A/D/F), incluindo os segmentos S5-Imobiliário e S6-Edificações ausentes, e corrigir a contagem de 20→21 agentes operacionais (incl. Manta 20-ESG, hoje totalmente invisível a este repositório).

Achados secundários (não bloqueantes, mas a corrigir na mesma leva): o erro "A7-bd" para o agente de propostas/BD (deveria ser A1), e a ambiguidade de nomenclatura entre o `D01…D12` interno de cada `SKILL.md` e o Eixo D real (D01–D22).
