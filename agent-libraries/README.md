# Agent Libraries — Manta Maestro

Referência canônica de trabalho de cada agente. Complementa
`.claude/agents/` (system prompts) com **starter kits** operacionais: pastas
SharePoint, documentos-modelo, KEs indexadas no pgvector, skills registradas
e padrões de acionamento.

## Formato

Todos os arquivos seguem 5 seções fixas:

1. **Pastas SharePoint canônicas** — rotas do `sp_agent_routing`
2. **Documentos-modelo** — templates curados com origem rastreada
3. **Knowledge Elements** — KEs relevantes do `MASTER-CATALOG.json`
4. **Skills** — nomes e interfaces registradas no catálogo
5. **Padrões de uso** — gatilhos → rotas → saídas esperadas

## Escopo v1 (piloto — 2026-07-05)

Os 4 horizontais que aparecem em todos os projetos e cobrem 48 dos 52 KEs:

| Agente             | Arquivo                     | KEs | Blocos primários       |
|--------------------|-----------------------------|-----|-----------------------|
| 01 Claims          | [01-claims.md](./01-claims.md)         | 10  | B2, B5                 |
| 02 Contratual      | [02-contratual.md](./02-contratual.md) | 0*  | (via 01 e 15)          |
| 05 Orçamento       | [05-orcamento.md](./05-orcamento.md)   | 12  | B1, B3, B4             |
| 07 Cronograma      | [07-cronograma.md](./07-cronograma.md) | 18  | B1, B2, B4             |

_\* Contratual não tem KEs próprios; opera sobre a base de Claims + Advisory._

## Roadmap v2

Expandir para os 7 horizontais restantes: **04 Imobiliário, 06 Modelagem,
13 BD, 14 Apresentações, 15 Advisory, 16 Arquiteto-IA**, mais o
**00 Maestro** (router).

## Manutenção

- Revisão semestral por Maurício. Item marcado como *deprecated* na coluna
  origem sai do índice.
- KEs sincronizados automaticamente com o Supabase (`select ... from
  knowledge_extractions`).
- Templates versionados no SharePoint em `04_IA/Manta-Maestro/Modelos/<Agente>/`.
