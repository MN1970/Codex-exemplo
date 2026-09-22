# Revisão Manta Maestro — CLAUDE.md + agentes S6–S10 (branch `claude/clever-brown-3vs2lr`)

**Data**: 2026-09-22
**Escopo**: `CLAUDE.md` deste repositório e `.claude/agents/*.md` (agentes verticais S6–S10)
**Método**: leitura direta dos arquivos no branch, comparação com `origin/main`, e reprodução
executável das regras de routing descritas no `CLAUDE.md` contra prompts reais de
`tests/routing/prompts.md`. Nenhum achado abaixo é baseado em memória ou inferência — cada um
tem o comando ou diff que o reproduz.

---

## Resumo executivo

| # | Achado | Severidade | Evidência |
|---|--------|------------|-----------|
| 1 | Branch está **muito atrasado em relação a `main`** — `CLAUDE.md` diverge em 1.180 linhas | 🔴 Crítico | `git diff --stat HEAD origin/main -- CLAUDE.md` |
| 2 | Routing por substring simples produz **falsos positivos reproduzíveis** (misroteamento) | 🟠 Alto | regex do próprio `CLAUDE.md` rodado contra prompts de `tests/routing/prompts.md` |
| 3 | Checklist de deploy cita tabela errada (`rag_chunks`) — a migração real usa `rag_collections` | 🟡 Médio | `CLAUDE.md` §DEPLOY CHECKLIST vs `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql` |
| 4 | Palavras-chave de energia incompletas (sem `ampacidade`/`ACSR`) — falso negativo | 🟡 Médio | mesma reprodução do achado 2 |
| 5 | Rastreabilidade da variante "M6 / Tipo A" está **internamente consistente** | 🟢 Positivo | `CLAUDE.md`, `docs/MODELO-MESTRE-PROPOSTA.md`, `docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md` concordam |

---

## Achado 1 — Branch severamente desatualizado (Crítico)

Este branch (`claude/clever-brown-3vs2lr`) parte de um ponto do histórico equivalente à PR #113
(mesclada em `claude/manta-agents-s6-s10-7qklcw`), enquanto `origin/main` já avançou muito além:

```
$ git diff --stat HEAD origin/main -- CLAUDE.md
 CLAUDE.md | 1180 ++++++++++++++++++++++++++++++++++++++++++++++++++++++-------
 1 file changed, 1049 insertions(+), 131 deletions(-)
```

O `CLAUDE.md` deste branch se autodeclara **v4.2.3** (2026-09-13), com 20 agentes e eixo S
indo até **S10**. O `CLAUDE.md` de `main` já está em **v5.4.7** (2026-09-11, e com PRs abertas
subindo até v5.4.8) e documenta:

- Eixo S indo até **S14** (incluindo Túneis, Mineração, Óleo e Gás — não mencionados aqui)
- Eixo A até **A11**, eixo D (disciplinas) até **D22-23**, eixo F (funcionais) até F10 — nenhum
  desses eixos existe neste `CLAUDE.md`
- Um motor de orquestração Python real (`src/maestro/`), serviço Node.js, testes, Docker,
  observabilidade — nada disso é mencionado aqui
- Achados de segurança reais já registrados (RLS desabilitado em tabelas Supabase públicas)

**Risco prático**: qualquer pessoa ou agente que use este branch como referência (routing,
numeração de segmento, checklist de deploy) está trabalhando com um mapa que não bate mais com
o SharePoint/Supabase reais — o próprio padrão que as PRs #115–#121 deste repositório
documentam ter causado retrabalho repetido (ex.: PR #116, agente Manta 08 recriado do zero por
não ter achado o F4-Extração real já operacional).

**Recomendação**: fazer rebase/merge de `origin/main` neste branch antes de qualquer novo
trabalho, ou — se o branch tem um propósito isolado — deixar isso explícito no `CLAUDE.md` para
não ser lido como estado atual do sistema.

---

## Achado 2 — Routing por substring produz misroteamento reproduzível (Alto)

A seção ROUTING do `CLAUDE.md` define regras como:

```
IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS
   → agente-saneamento (S8)
IF menção a transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE
   → agente-energia (S9)
IF menção a porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel
   → agente-portos (S6)
IF menção a aeroporto|pista pouso|ANAC|ICAO|TPS|TECA|balizamento
   → agente-aeroportos (S7)
```

Se essas regras forem implementadas literalmente (regex `re.search` case-insensitive, sem
`\b` de fronteira de palavra — que é exatamente o que o texto descreve), qualquer keyword curto
casa como **substring dentro de outras palavras**. Reproduzi isso rodando o regex literal contra
prompts do próprio `tests/routing/prompts.md` deste branch:

```python
>>> re.search(r"saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS",
...           "Preciso projetar uma ETA de ciclo completo para 200 mil hab.", re.I).group(0)
'eta'   # casou dentro de "proj-ETA-r", antes mesmo de chegar no "ETA" de verdade

>>> re.search(r"transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE",
...           "Os dados filtrados mostraram queda de produtividade no canteiro.", re.I).group(0)
'lt'    # casou dentro de "fi-LT-rados" — prompt sem NENHUMA relação com energia

>>> texto = "Quero dimensionar a pista de pouso do aeroporto regional (código 3C)."
>>> [n for n,p in regras if re.search(p, texto, re.I)]
['agente-portos (S6)', 'agente-aeroportos (S7)']   # "porto" casa dentro de "aeroPORTO"
```

Três casos reais, reproduzíveis, com o texto exatamente como está no `CLAUDE.md` e nos prompts
de teste deste branch:

1. **Qualquer prompt com a palavra "projetar"** dispara `agente-saneamento` mesmo sem relação
   com saneamento (via `ETA` casando em "proj**eta**r").
2. **Qualquer prompt com "filtrados", "resultados", "exaltado"** etc. dispara `agente-energia`
   (via `LT` casando como substring).
3. **Prompts sobre aeroportos** também casam a regra de `agente-portos` (via `porto` dentro de
   `aeroporto`), tornando o resultado dependente da ordem de avaliação das regras — que não está
   especificada no documento.

Isso é o mesmo padrão de bug que a PR #120 (`main`) já encontrou e documentou ao rodar
`scripts/test_routing.py` (a mesma classe: `ETA`בproj**eta**r, `LT`בfi**lt**rados,
`porto`בaero**porto**) — mas esse script e a correção das keywords não existem neste branch.

**Recomendação**: (a) portar `scripts/test_routing.py` de `main` para este branch antes de
declarar o routing "operacional"; (b) usar `\b` (fronteira de palavra) nas regras, ou
correspondência por token em vez de substring; (c) definir explicitamente a ordem/prioridade de
avaliação para os casos ambíguos já listados na própria seção "Casos ambíguos" de
`tests/routing/prompts.md`.

---

## Achado 3 — Checklist cita tabela errada (Médio)

`CLAUDE.md`, seção "DEPLOY CHECKLIST v4.2":

```
- [ ] Criar 5 coleções RAG em Supabase (`rag_chunks`)
```

Mas a migração candidata real (`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`) insere
nas tabelas `rag_collections` e `sp_agent_routing`, não em `rag_chunks`:

```sql
INSERT INTO rag_collections (slug, name, storage_prefix, initial_sources) VALUES (...)
INSERT INTO sp_agent_routing (agent_slug, sp_folder, file_patterns, priority) VALUES (...)
```

`rag_chunks` não aparece em nenhum lugar do arquivo `.sql`. Quem seguir o checklist ao pé da
letra vai procurar/criar a tabela errada.

**Recomendação**: corrigir o texto do checklist para `rag_collections` (e citar também
`sp_agent_routing`, hoje omitida do item).

---

## Achado 4 — Keywords de energia incompletas (Médio)

Na mesma reprodução do Achado 2, um prompt de energia real do próprio `tests/routing/prompts.md`
não casa com nenhuma regra:

```
"Como faço o estudo de ampacidade para condutor ACSR 636 MCM?" → nenhuma regra do CLAUDE.md casa
```

`ampacidade` e `ACSR` não estão na lista de keywords de `agente-energia`
(`transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE`), apesar de o próprio
`tests/routing/prompts.md` deste branch listar esse prompt como caso de teste esperado para
`agente-energia`. `main` já identificou e corrigiu esse mesmo gap (PR #120).

---

## Achado 5 — Rastreabilidade da variante "M6 / Tipo A" (positivo)

Ao contrário dos achados acima, a cadeia de documentos sobre a variante de proposta
técnico-comercial está **consistente**:

- `CLAUDE.md` (§"MODELO MESTRE DE PROPOSTA") afirma que a variante já está implementada na
  skill de produção sob o nome "Tipo A / Concessão de Infraestrutura de Grande Porte", e que a
  citação original a `MNT-2026-COM-1183_D` era fabricada (só existe `_C_3`)
- `docs/MODELO-MESTRE-PROPOSTA.md` tem uma nota de status no topo confirmando o mesmo, sem
  reescrever a análise original — preserva o racional como registro histórico
- `docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md` também está marcado "SUPERSEDIDO", com checklist
  refletindo o estado real
- `origin/main` (v5.4.5) confirma, por investigação independente via SharePoint real, a mesma
  fabricação e a mesma correção — os dois branches convergem na mesma conclusão por caminhos
  diferentes

Esse é o padrão correto a replicar nos outros documentos do repositório: quando uma citação é
corrigida, deixar o texto original como histórico e apontar claramente para o estado atual, em
vez de reescrever silenciosamente.

---

## Recomendações priorizadas

1. **Crítico** — sincronizar este branch com `main` (ou documentar explicitamente que ele é uma
   base histórica isolada) antes de usar seu `CLAUDE.md` como referência operacional.
2. **Alto** — portar/criar `scripts/test_routing.py` neste branch e corrigir as regras de
   routing para usar fronteira de palavra, não substring cru.
3. **Médio** — corrigir `rag_chunks` → `rag_collections` no checklist de deploy.
4. **Médio** — adicionar `ampacidade`, `ACSR` (e revisar demais segmentos por gaps similares)
   às keywords de `agente-energia`.
5. **Manter** — o padrão de correção com nota de status + preservação do histórico usado na
   variante "M6 / Tipo A".

---

*Revisão gerada por sessão Claude Code neste repositório, a pedido do usuário ("rodar revisão de
conteúdo do projeto, arquitetura e outras, via Manta Maestro"). Todos os achados acima foram
verificados por leitura direta de arquivo ou execução de código nesta sessão — nenhum dado de
SharePoint/Supabase reais foi consultado (conector indisponível nesta verificação).*
