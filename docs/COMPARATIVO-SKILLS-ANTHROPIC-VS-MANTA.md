# Comparativo — Skills Oficiais Anthropic (`anthropics/skills`) vs. Ecossistema Manta Maestro

**Versão do Documento**: 1.0
**Data**: 2026-09-02
**Autores**: Claude AI + Manta Associados
**Ticket**: MNT-2026-SKILLS-BENCHMARK-ANTHROPIC

---

## Sumário

1. [Contexto e método](#1-contexto-e-método)
2. [TL;DR](#2-tldr)
3. [Achado crítico — divergência entre o auto-relato da skill `manta-maestro` e o registro real](#3-achado-crítico--divergência-entre-o-auto-relato-da-skill-manta-maestro-e-o-registro-real)
4. [Inventário: skills oficiais anthropics/skills](#4-inventário-skills-oficiais-anthropicsskills)
5. [Skills com valor novo — avaliação e agente-alvo](#5-skills-com-valor-novo--avaliação-e-agente-alvo)
6. [Skills redundantes ou irrelevantes](#6-skills-redundantes-ou-irrelevantes)
7. [Recomendação de registro formal](#7-recomendação-de-registro-formal)
8. [Caveats — licenciamento](#8-caveats--licenciamento)
9. [Referências](#9-referências)

---

## 1. Contexto e método

Este documento parte de uma análise comparativa entre as ~19 skills do
repositório público `anthropics/skills` e a suíte custom da Manta
Associados, avaliada em seguida sob a ótica operacional do **Manta
Maestro**. Foi escrito neste repositório (`MN1970/codex-exemplo`, branch
`main`) — que é a fonte de dados versionada real do ecossistema
(`CLAUDE.md`, `skill-registry.json`, `sharepoint/00-arquitetura/`,
`docs/`) — em vez de um repositório não relacionado ao domínio da Manta.

## 2. TL;DR

- Das ~19 skills oficiais, **5 têm valor potencial não coberto** pela
  suíte Manta: `skill-creator`, `mcp-builder`, `doc-coauthoring`,
  `frontend-design` e `theme-factory`.
- As quatro skills de documentos (`docx`, `pdf`, `pptx`, `xlsx`) são
  **source-available, não open source** — já operam automaticamente no
  Claude.ai/API, sem necessidade (nem permissão) de redistribuição.
- **Nenhuma das 5 skills candidatas está formalmente registrada** em
  `skill-registry.json` ou em `CLAUDE.md` neste repositório — ao
  contrário do que uma consulta à skill `manta-maestro` (via Skill tool)
  relata (ver Seção 3). Qualquer decisão de adoção precisa passar pelo
  mesmo processo de registro usado para os agentes S6–S10
  (`skill-registry.json` + PR + gate humano MN).

## 3. Achado crítico — divergência entre o auto-relato da skill `manta-maestro` e o registro real

Uma consulta à skill `manta-maestro` (Resource Scout, §9.3 do seu
`SKILL.md`) informa que `skill-creator`, `mcp-builder`,
`doc-coauthoring` e `theme-factory` já estariam "mapeadas" desde
2026-06-27/28, atribuídas a agentes como F-projeto-claude e
A8-apresentacoes.

Essa informação **não se confirma nos artefatos versionados deste
repositório**:

```bash
grep -in -E "skill-creator|mcp-builder|doc-coauthoring|frontend-design|theme-factory" \
  skill-registry.json CLAUDE.md docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md
# → nenhuma ocorrência
```

`skill-registry.json` (v1.0.0, 2026-07-27) registra formalmente **apenas
5 skills**, todas do Eixo 2 (agentes verticais S6–S10: saneamento,
energia, portos, aeroportos, barragens) — nenhuma skill horizontal ou
meta-skill do catálogo Anthropic consta ali.

Isso não é coincidência isolada. O próprio
`sharepoint/00-arquitetura/INDICE-CANONICAL-v5.0.md` (fonte de verdade
única da arquitetura, 2026-07-31) já documenta, na sua nota de
proveniência, um caso concreto de renumeração de segmentos (S6–S11)
que foi feita **"com base na descrição da skill `manta-maestro`
(v5.0.1), um texto de catálogo, não uma fonte de schema/dados"** — e
trata essa divergência como pendência de auditoria, não como fato
consumado.

**Conclusão prática**: o auto-relato da skill `manta-maestro` é útil
como *hipótese de trabalho* (ela pode estar descrevendo um estado
mantido fora deste repositório git — SharePoint, Supabase, ou uma
branch ainda não mesclada), mas não deve ser tratado como confirmação
de que uma skill já está adotada. A única fonte confiável de "o que
está registrado" é `skill-registry.json` neste repositório, e por ele,
**as 5 skills candidatas ainda não foram adotadas**.

## 4. Inventário: skills oficiais anthropics/skills

| Categoria | Skills | Observação |
|---|---|---|
| Criativas & Design | `algorithmic-art`, `canvas-design`, `slack-gif-creator`, `theme-factory` | Só `theme-factory` tem aderência ao domínio Manta |
| Design de UI | `brand-guidelines`, `frontend-design`, `web-artifacts-builder` | `brand-guidelines` aplica a marca da Anthropic, não da Manta |
| Documentos (source-available) | `docx`, `pdf`, `pptx`, `xlsx` | Licença proprietária — ver Seção 8 |
| Técnicas & Desenvolvimento | `claude-api`, `mcp-builder`, `skill-creator`, `webapp-testing` | `mcp-builder` e `skill-creator` são as de maior valor |
| Corporativas / Meta | `doc-coauthoring`, `internal-comms`, `academy-guide`, `discernment-nudge` | Só `doc-coauthoring` tem valor não coberto |

Licenciamento: a maioria (Apache 2.0) é livremente reutilizável e
modificável; as 4 skills de documentos são source-available (ver
Seção 8).

## 5. Skills com valor novo — avaliação e agente-alvo

| Skill | Valor | Agente Manta prioritário | Justificativa |
|---|---|---|---|
| `skill-creator` | **Crítico** (não apenas alto) | **Manta 16 — arquiteto-ia** | O catálogo real do ecossistema já passa de dezenas de skills/plugins (ver `CLAUDE.md`, `skill-registry.json` e os múltiplos documentos em `sharepoint/00-arquitetura/`). Nesse volume, colisão e imprecisão de trigger deixam de ser risco teórico. A metodologia de eval (20 queries trigger/não-trigger, análise de variância) deveria ser absorvida como rotina do agente `arquiteto-ia`, não instalada como skill solta. |
| `mcp-builder` | **Alto** | **Manta 16 — arquiteto-ia** | O ecossistema já opera integrações MCP (Microsoft 365/SharePoint, Supabase — ver `.mcp.json` na raiz deste repo). `mcp-builder` fornece a metodologia para padronizar novos conectores (SICRO, P6, Autodesk), mas deve ser consolidada dentro da doutrina do `arquiteto-ia`, evitando duas fontes de verdade sobre "como construir MCP" no ecossistema. |
| `doc-coauthoring` | **Médio-alto** | **Manta 01 — claims** e **Manta 15 — advisory** | Nenhum guard hoje documentado (`aluci-guard`, `consist-guard`) cobre "teste com leitor cego" antes do fechamento de um documento. Deveria entrar como **estágio no pipeline**, antes dos guards de consistência/alucinação — não como skill isolada. |
| `frontend-design` | **Médio**, condicionado a produto com UI | **Portal IA** (módulos React descritos em `docs/`) | Único ponto do ecossistema com entrega de UI a cliente final; eleva qualidade acima do "AI slop" genérico. |
| `theme-factory` | **Médio/baixo** | **Manta 14 — apresentacoes** | Sobreposição parcial com o padrão visual próprio da Manta (`padrao-manta`). Só deve ser usada quando a marca Manta não se aplica (contexto não-cliente ou tema ad hoc). |

## 6. Skills redundantes ou irrelevantes

- **`brand-guidelines`**: aplica a marca **da Anthropic**, não a da
  Manta — risco real de contaminação visual se disparada no lugar do
  padrão próprio. Uso permitido apenas como referência de estrutura de
  skill, nunca em produção de artefato cliente.
- **`docx`/`pdf`/`pptx`/`xlsx`**: já embutidas no Claude.ai/API; não
  precisam ser "adotadas" como skill custom (ver Seção 8).
- **`internal-comms`**: formatos genéricos de comunicação interna de
  empresa de tecnologia, pouco alinhados ao fluxo de consultoria de
  engenharia.
- **`web-artifacts-builder`/`webapp-testing`**: relevantes apenas se a
  Manta desenvolver software web como produto — hoje restrito ao
  escopo do Portal IA.
- **`claude-api`**: nicho — útil só para quem desenvolve as próprias
  integrações/skills.
- **`algorithmic-art`, `canvas-design`, `slack-gif-creator`,
  `academy-guide`, `discernment-nudge`**: sem aderência a owner's
  engineer, concessões, claims ou qualquer fluxo técnico da Manta.

## 7. Recomendação de registro formal

Adoção só deve ser considerada "feita" quando refletida em
`skill-registry.json`, seguindo o mesmo schema usado pelos agentes
S6–S10 (id, `manta_code`, `tier_default`, `status`, `aliases`,
handoffs) — e passando pelo mesmo processo: PR neste repositório +
gate humano MN antes de merge (ver `docs/DEPLOY-CHECKLIST-v5.0.md` para
o runbook de referência).

**Fase 1 — registrar primeiro:**
1. `skill-creator` e `mcp-builder` — como capacidades do agente
   **Manta 16 (arquiteto-ia)**, não como entradas horizontais soltas.

**Fase 2 — piloto controlado:**

2. `doc-coauthoring` — piloto em um pleito de reequilíbrio real
   (Manta 01) ou parecer (Manta 15), medindo redução de retrabalho.
3. `frontend-design` — só se houver entrega de UI programada no
   roadmap do Portal IA.
4. `theme-factory` — registrar com restrição explícita de uso (nunca
   sobrepor `padrao-manta` em artefato de cliente).

**Não registrar:** `brand-guidelines` (marca errada), skills criativas
(art/GIF), e não tratar as skills de documentos como algo a
"instalar" — elas já operam via Serviços Anthropic.

**Antes de qualquer registro**: reconciliar esta lista com o estado
real do SharePoint/Supabase (fora deste repositório git), já que a
Seção 3 mostrou que o auto-relato da skill `manta-maestro` pode estar
descrevendo um estado não commitado aqui.

## 8. Caveats — licenciamento

As quatro skills de documentos (`docx`, `pdf`, `pptx`, `xlsx`) são
regidas por licença proprietária (© Anthropic, PBC), não Apache 2.0. A
licença proíbe extrair esses materiais dos Serviços, copiá-los fora de
uso temporário autorizado, criar obras derivadas, e distribuí-los ou
sublicenciá-los a terceiros. Para uma consultoria comercial como a
Manta, isso significa: **uso legítimo apenas através do Claude.ai/API/
Claude Code**, nunca redeploy ou redistribuição a clientes como ativo
próprio. As demais skills mencionadas neste documento (Apache 2.0)
podem ser copiadas, modificadas e redistribuídas com atribuição.

## 9. Referências

- Repositório fonte da análise original: `anthropics/skills` (GitHub,
  README consultado em setembro de 2026).
- Registro real de skills deste ecossistema: `skill-registry.json`
  (raiz deste repositório).
- Arquitetura canônica: `sharepoint/00-arquitetura/INDICE-CANONICAL-v5.0.md`.
- Runbook de deploy de referência: `docs/DEPLOY-CHECKLIST-v5.0.md`.
- Skill `manta-maestro` (via Skill tool) — usada como hipótese de
  trabalho nesta análise, não como fonte de verdade (ver Seção 3).
