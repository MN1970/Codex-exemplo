# Cowork Integration Guide — Manta Maestro v5.0.1
## Microsoft 365 (Teams, SharePoint, OnNote) + Claude AI

**Versão**: v1.0  
**Data**: 1 de agosto de 2026  
**Status**: 🚀 Pronto para configuração  
**Escopo**: Sincronização bidirecional + menções automáticas

---

## Visão Geral

Manta Maestro integra-se com Cowork (Microsoft 365) para:

1. **SharePoint Sync** — Agentes `.md` + RAG sincronizados automaticamente
2. **Teams Mentions** — `@manta-maestro` ativa roteamento inteligente
3. **OneNote Notebooks** — Rastreamento de projetos com contexto
4. **Calendar Integration** — Prazos de projetos + checkpoints

---

## Pré-requisitos

### Setup Cowork (Administrador)

- [x] Cowork ativado para workspace
- [ ] SharePoint site Manta Associados criado
- [ ] Teams canal #manta-maestro criado
- [ ] Permissões: read/write para `03_Projetos/`
- [ ] OneNote notebook "Projetos" criado
- [ ] Claude AI connector autorizado em Cowork settings

### Setup Claude Code

- [ ] Claude Code MCP para SharePoint
- [ ] Claude Code MCP para Teams
- [ ] Cowork plugin ativado

---

## Estrutura SharePoint

```
Manta Associados (Site)
├── /Skills/
│   ├── Óleo & Gás/
│   │   └── agente-oleo-gas.md (synced from .claude/agents/)
│   ├── Edificações/
│   │   └── agente-edificacoes.md
│   ├── Saneamento/
│   │   └── agente-saneamento.md
│   ├── Energia/
│   │   └── agente-energia.md
│   ├── Portos/
│   │   └── agente-portos.md
│   ├── Aeroportos/
│   │   └── agente-aeroportos.md
│   └── Barragens/
│       └── agente-barragens.md
│
├── /Arquitetura/
│   ├── CLAUDEMD-MASTER-REGISTRY.md
│   ├── ARQUITETURA-AGENTES-IA.md
│   ├── ATIVIDADES-A1-A10.md
│   ├── FUNCIONAIS-F1-F8.md
│   └── DISCIPLINAS-D01-D20.md
│
├── /RAG-Collections/
│   ├── Rodovias/ (rod:*.pdf, *.docx)
│   ├── OAE/ (oae:*.pdf)
│   ├── Ferrovia/ (fer:*.pdf)
│   ├── Metrô/ (mtr:*.pdf)
│   ├── Portos/ (por:*.pdf)
│   ├── Aeroportos/ (aer:*.pdf)
│   ├── Saneamento/ (san:*.pdf, san:ar:*.pdf para AySA)
│   ├── Energia/ (ene:*.pdf, ene:t:, ene:d:, ene:g:)
│   └── Barragens/ (bar:*.pdf, bar:c:, bar:t:, bar:e:, bar:r:)
│
├── /03_Projetos/
│   ├── Rodovias/
│   │   └── [Projetos ativos, referências, documentação]
│   ├── Portos/
│   │   └── [...]
│   ├── Saneamento/
│   │   └── [...]
│   ├── Energia/
│   │   └── [...]
│   ├── Barragens/
│   │   └── [...]
│   ├── OleoGas/ (novo — S12)
│   │   └── [Projeto Ativo, Referências, Documentação]
│   ├── Edificacoes/ (novo — S13)
│   │   └── [...]
│   └── Mineracao/ (novo — S11, pós Fase 2)
│       └── [...]
│
├── /Documentação/
│   ├── DEPLOYMENT-COMPLETE-v5.0.1.md
│   ├── PLANEJAMENTO-EVOLUCAO-v5.0.1.md
│   ├── FASE-1-EXECUCAO.md
│   └── [Deploy checklists e runbooks]
│
└── /Comunicação/
    ├── Announcements/ (v5.0.1, v5.1, etc.)
    ├── Decision-Logs/
    └── Lessons-Learned/
```

---

## Sincronização Automática

### 1. SharePoint ← Git (`.claude/agents/` → `/Skills/`)

**Frequência**: A cada commit (via GitHub Actions) ou manual

**Processo**:
```yaml
trigger: 
  - push to main branch
  
steps:
  1. Detectar mudanças em .claude/agents/*.md
  2. Validar YAML frontmatter
  3. Converter para SharePoint-friendly format
  4. Upload para /Skills/[Segmento]/
  5. Notificar Teams #manta-architect
```

**Exemplo**:
```
Git commit: "Update agente-saneamiento.md v1.2"
    ↓
Trigger: GitHub Actions
    ↓
Upload: /Manta/Skills/Saneamento/agente-saneamiento.md
    ↓
Teams notification: "agente-saneamiento atualizado (v1.2)"
```

### 2. SharePoint ← RAG Collections

**Frequência**: Manual (upload) → Auto-sync 24h

**Processo**:
```
Admin upload: Novo PDF em /RAG-Collections/Portos/
    ↓
MCP indexing job (nightly)
    ↓
Detecta novo arquivo
    ↓
Ingestão via Supabase (rag_collections)
    ↓
Disponível em próximas queries agente-portos
```

**Lifecycle**:
- T0: Upload arquivo em SharePoint
- T+24h: Indexing job executa
- T+24-25h: Disponível em RAG
- T+25h: Notificação em Teams

### 3. Teams ← Maestro (Bidirecional)

**Webhook SharePoint → Teams**:

```
Mudança em /Skills/ ou /RAG-Collections/
    ↓
SharePoint webhook notifica Teams bot
    ↓
Publica em #manta-architect
    ↓
"✅ Recurso atualizado: agente-energia.md"
    ↓
Link direto para visualizar em SharePoint
```

---

## Teams Mentions — Roteamento Automático

### Comando: `@manta-maestro`

```
Formato: @manta-maestro "[pergunta aqui]" [--segment S#] [--activity A#]

Exemplos:
✅ @manta-maestro "orçamento ETA 50 ML/dia AySA"
✅ @manta-maestro "normas para OAE em SP" --segment oae
✅ @manta-maestro "matriz de risco barragem rejeitos"
✅ @manta-maestro "cronograma transmissão 500kV" --segment energia
```

### Fluxo

```
1. User posts: @manta-maestro "pergunta"
    ↓
2. Teams bot captura menção
    ↓
3. Claude AI Cowork connector processa
    ↓
4. Maestro router identifica keywords
    ↓
5. Agente vertical responde em thread
    ↓
6. Resposta linked em SharePoint (arquivo automático)
    ↓
7. Notificação: "Resposta disponível em #manta-maestro"
```

### Configuração Bot

**Manifest**.json:
```json
{
  "name": "Manta Maestro",
  "description": "Multi-agent infra engineering assistant",
  "handlers": [
    {
      "type": "mention",
      "trigger": "@manta-maestro",
      "endpoint": "https://api.anthropic.com/cowork/teams/handler",
      "auth": "oauth2"
    }
  ],
  "permissions": [
    "chat:read",
    "chat:write",
    "sharepoint:read",
    "sharepoint:write"
  ]
}
```

---

## OneNote Integration

### Notebook Structure

```
Manta Maestro Projetos
├── Seção: S1 — Rodovias
│   ├── Página: Projeto [Nome]
│   │   ├── Info: Segmento, Atividades, Disciplinas
│   │   ├── Contexto S.A.D
│   │   ├── Link agente: agente-infraestrutura S1
│   │   ├── RAG collections: rod:*, [...]
│   │   ├── Histórico consultas (rastreável)
│   │   └── Arquivos linked do SharePoint
│   └── [...mais páginas]
├── Seção: S8 — Saneamento
│   └── Subseção: AySA (Argentina)
│       └── [...projetos]
└── Seção: S12 — Óleo & Gás (novo)
    └── [...]
```

### Criar Notebook de Projeto

**Template OneNote**:
```markdown
# [NOME DO PROJETO]

## Contexto S.A.D

**Segmento**: S8 (Saneamento)
**Atividades**: A1 (Proposta), A3 (Orçamento), A5 (Cronograma), A10 (Risco)
**Disciplinas**: D01 (Hidráulica), D02 (Estrutural), D06 (Ambiental)

**Agente Principal**: agente-saneamento
**Handoffs**: Manta 05 (Orçamento), Manta 07 (Cronograma), Manta-10 (Risco)

## RAG Collections Ativas

- san:* (geral saneamento)
- san:ar:* (AySA Argentina) ← se aplicável

## Consultas ao Maestro

| Data | Pergunta | Agente | Resultado | Arquivo |
|------|----------|--------|-----------|---------|
| 2026-08-01 | "Orçamento ETA 50 ML" | agente-saneamiento | [resultado] | [link] |
| 2026-08-02 | "Cronograma obra" | Manta 07 | [resultado] | [link] |

## Documentos

- [Link SharePoint] Projeto-Básico.pdf
- [Link SharePoint] Regulações-AySA.pdf
- [Link] Orçamento-v2.xlsx
```

---

## Calendar Integration

### Sincronização de Prazos

**Fase 1 Checkpoints**:
```
2026-08-01 06:00
  Event: "FASE 1 — Início execução paralela"
  Owner: DevOps
  Linked: #manta-maestro Teams channel

2026-08-07 12:00
  Event: "CHECKPOINT 1 — Go/No-Go Fase 2"
  Owner: MN (Mauricio Neves)
  Decision required: ✅/❌
  Linked: Gate MN #2 documento

2026-08-21 12:00
  Event: "CHECKPOINT 2 — Estabilidade produção validada"
  Linked: S12/S13/S11 publicação

2026-09-02
  Event: "CHECKPOINT 3 — Fase 3 completa"
  Linked: v5.2 aprovação
```

**Automação**:
- Lembretes 24h antes
- Auto-notificação Teams
- Linked docs em evento

---

## Permissões & Segurança

### Roles

| Role | SharePoint | Teams | OneNote | Ação |
|------|-----------|-------|---------|------|
| Admin | RW | Admin | Owner | Tudo |
| Architect | RW | Post | Editor | Docs + decisões |
| Agent Owner | RW | Post | Editor | Docs próprios |
| User | R | Read | Viewer | Consultas |
| Guest | R | - | - | Docs públicos |

### RLS (Row-Level Security)

```sql
-- Supabase: agentes só veem RAG do próprio segmento
CREATE POLICY "agente_saneamento_sees_san"
  ON manta_rag_chunks
  FOR SELECT
  USING (collection_slug LIKE 'san:%'
         OR collection_slug = 'generic');

-- SharePoint: folders por agent via AD groups
-- /Skills/Saneamento → Group: Agents-Saneamento
```

---

## Notificações

### Tipos

1. **Doc Update**: Arquivo modificado em SharePoint
   ```
   ✅ agente-oleo-gas.md foi atualizado (v1.1)
   Autor: Cloud-Team
   Link: [abrir no SharePoint]
   ```

2. **RAG Indexed**: Nova coleção disponível
   ```
   ✅ Novos documentos indexados: Portos (3 PDFs)
   Agente: agente-portos
   Disponível em: 2026-08-02 14:00
   ```

3. **Maestro Query**: Resposta disponível
   ```
   ✅ Resposta a: "Orçamento ETA 50 ML"
   Agente: agente-saneamento
   Thread: #manta-maestro (conversa)
   Arquivo: Shared to OneNote
   ```

4. **Checkpoint Alert**: Gate decisions
   ```
   🎯 CHECKPOINT 1: 2026-08-07 12:00
   Status: 5/6 tarefas concluídas
   Ação requerida: MN avaliar Go/No-Go
   Documento: [link]
   ```

---

## Troubleshooting Cowork

| Problema | Causa | Solução |
|----------|-------|---------|
| "@manta-maestro não responde" | Bot não autorizado | Admin: permitir app em Teams |
| Docs não sincronizam | GitHub Actions falhando | Verificar logs; re-trigger |
| RAG não atualiza | MCP job não rodou | Rodar manual: `mcp sync` |
| Permissão negada | RLS policy incorreta | Verificar AD groups + Supabase policies |
| Embed quebrado | Link expirado | Re-upload arquivo em SharePoint |

---

## Roadmap Cowork

### Fase 1 (Agosto 2026)
- [x] SKILL.md criado
- [ ] SharePoint sync automático
- [ ] Teams @manta-maestro ativo
- [ ] OneNote notebooks criados

### Fase 2 (Setembro 2026)
- [ ] Calendar integration
- [ ] Forms para intake de projetos
- [ ] Approval workflows (Gate MN no Teams)

### Fase 3 (Outubro 2026)
- [ ] Power BI dashboards (Maestro metrics)
- [ ] Chatbot Copilot (Teams app)
- [ ] Custom connectors (SAP, Project Online)

---

## Quick Start — Setup em 5 minutos

### 1. Admin: Ativar Cowork Connector
```
Claude AI settings → Connectors
→ Microsoft 365 (Cowork)
→ Autorizar com credenciais de admin
```

### 2. Upload SharePoint Structure
```bash
# Via CLI ou manual
mkdir -p /Manta/Skills/{OleoGas,Edificacoes,Saneamento,...}
cp .claude/agents/*.md /Manta/Skills/*/
```

### 3. Create Teams Channel
```
Teams → + Nova equipe
Nome: Manta Maestro
Canais: #manta-maestro, #manta-architect
```

### 4. Add Bot
```
Teams #manta-maestro → + Adicionar apps
Pesquisa: Manta Maestro
Instalar
```

### 5. Test
```
@manta-maestro "teste: olá Maestro"
→ Resposta automática em thread
```

---

## Suporte Cowork

- **Setup**: #manta-architect (Teams)
- **Issues**: Azure DevOps ticket
- **Docs**: `/Manta/Documentação/`

---

**Integration Status**: ✅ PRONTO  
**Última atualização**: 2026-08-01  
**Próximo**: Go-live Teams + SharePoint sync (Fase 1)

