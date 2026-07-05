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

Exceções de formato: `00-maestro.md` substitui §2-3 por *routing rules +
escalation matrix* (é router, não consumidor). `S5-tuneis.md` é cross-reference
(coberto por S2 + S4).

## Cobertura v1 (2026-07-05)

**20/20 agentes contemplados** — 11 horizontais + 10 verticais (S5 como cross-ref).

### Horizontais (11 arquivos)

| Agente             | Arquivo                     | KEs próprios | Templates |
|--------------------|-----------------------------|--------------|-----------|
| 00 Maestro         | [00-maestro.md](./00-maestro.md)         | N/A (router) | 4 skills |
| 01 Claims          | [01-claims.md](./01-claims.md)           | 10  | 5 templates |
| 02 Contratual      | [02-contratual.md](./02-contratual.md)   | 0*  | 5 templates |
| 04 Imobiliário     | [04-imobiliario.md](./04-imobiliario.md) | 0** | 4 templates |
| 05 Orçamento       | [05-orcamento.md](./05-orcamento.md)     | 12  | 5 templates |
| 06 Modelagem       | [06-modelagem.md](./06-modelagem.md)     | 2   | 4 templates |
| 07 Cronograma      | [07-cronograma.md](./07-cronograma.md)   | 18  | 6 templates |
| 13 BD              | [13-bd.md](./13-bd.md)                   | 0** | 4 templates |
| 14 Apresentações   | [14-apresentacoes.md](./14-apresentacoes.md) | 0*** | 5 templates |
| 15 Advisory        | [15-advisory.md](./15-advisory.md)       | 12  | 5 templates |
| 16 Arquiteto-IA    | [16-arquiteto-ia.md](./16-arquiteto-ia.md) | 1 + acesso irrestrito | 4 templates |

_\* Contratual opera sobre KEs de 01 + 15 (adjacência jurídica)._
_\*\* Backlog para WF-AKP-002._
_\*\*\* Não faz sentido — este agente formata, não gera conhecimento._

### Verticais (10 arquivos)

| Agente                | Arquivo                     | KEs próprios | Bloco primário |
|-----------------------|-----------------------------|--------------|----------------|
| S1 Rodovias           | [S1-rodovias.md](./S1-rodovias.md)       | 9  | B1 + B3        |
| S2 OAE                | [S2-oae.md](./S2-oae.md)                 | 5  | B8             |
| S3 Ferrovia           | [S3-ferrovia.md](./S3-ferrovia.md)       | 0  | (backlog)      |
| S4 Metrô              | [S4-metro.md](./S4-metro.md)             | 5  | B6             |
| S5 Túneis             | [S5-tuneis.md](./S5-tuneis.md)           | via S2+S4 | cross-ref |
| S6 Portos             | [S6-portos.md](./S6-portos.md)           | 0  | (backlog)      |
| S7 Aeroportos         | [S7-aeroportos.md](./S7-aeroportos.md)   | 0  | (backlog)      |
| S8 Saneamento (AySA)  | [S8-saneamento.md](./S8-saneamento.md)   | 7  | B7             |
| S9 Energia            | [S9-energia.md](./S9-energia.md)         | 0  | (backlog)      |
| S10 Barragens         | [S10-barragens.md](./S10-barragens.md)   | 0  | (backlog)      |

### Cobertura KEs total

- **KEs alocados a horizontais:** 55 assignments (contagem por agente, com
  overlap — mesmo KE aparece em múltiplos agentes).
- **KEs alocados a verticais:** 26 assignments.
- **KEs únicos no MASTER-CATALOG:** 52.
- **KEs sem consumidor natural (backlog):** os que estão só em blocos ainda
  não cobertos por verticais com backlog vazio.

## Princípio de execução (do Maestro)

**Sempre despachar agentes/sub-agentes em paralelo quando independentes.**
Ver §Princípio de Execução em [`../CLAUDE.md`](../CLAUDE.md) e cláusula 1 de
[`../sharepoint/01-agentes-fundamentais/agente-maestro/SKILL.md`](../sharepoint/01-agentes-fundamentais/agente-maestro/SKILL.md).

## Auditoria SharePoint

Os templates (`{AGENT}-M-NNN`) são hoje declarações — nem todos existem no SP.
Rode `academic-ingestor/src/sp_audit.py` (Graph API) para relatório de
declarados × existentes × órfãos assim que as credenciais SP estiverem
disponíveis:

```bash
export SP_TENANT_ID=... SP_CLIENT_ID=... SP_CLIENT_SECRET=... SP_SITE_ID=...
python academic-ingestor/src/sp_audit.py \
  --libraries agent-libraries/ --report sp-audit.json
```

## Roadmap v2

- **WF-AKP-002** — ingerir blocos que hoje têm 0 KEs: direito imobiliário/registral (04),
  editais e histórico BD (13), regulação ANTAQ/ANAC/ANEEL/ANM (S6, S7, S9, S10),
  norma ferroviária (S3).
- **Sync automático** — job que roda `select ... from knowledge_extractions`
  e re-gera a §3 de cada library.
- **Métricas de uso** — quantas vezes o agente foi acionado, feedback do cliente
  por template (v2 tem coluna adicional).

## Manutenção

- Revisão semestral por Maurício. Item marcado como *deprecated* na coluna
  origem sai do índice.
- KEs sincronizados com o Supabase — se aparecer novo KE, adicionar à §3 do
  agente cujo `agentes_destino` contém.
- Templates versionados no SharePoint em `04_IA/Manta-Maestro/Modelos/<Agente>/`.
