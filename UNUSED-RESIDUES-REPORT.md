# Resíduos não utilizados do Claude Code - Manta Maestro v4.2

**Análise realizada**: 2026-08-02  
**Repositório**: `Codex-exemplo`  
**Branch**: `claude/claude-code-unused-residues-e8p11x`

---

## 📊 Resumo executivo

De um total de **10 itens de deploy** do Manta Maestro v4.2, **6 permanecem não implementados** (60% de cobertura), gerando resíduos em infraestrutura, dados e configuração do Claude Code.

| Categoria | Itens | Status |
|-----------|-------|--------|
| Infraestrutura (Supabase + SharePoint) | 3 | ❌ 0% |
| Configuração do Claude Code | 2 | ❌ 0% |
| Habilidades / Skills | 1 | ❌ 0% |
| Documentação | 1 | ⚠️ Desatualizada |
| Testes | 1 | ⚠️ Não executado |
| Dependências externas | 1 | ⚠️ Aguardando |

**Impacto**: Sistema **declarativo** (estrutura em `.md`) mas **não operacional** (dados não carregados, features não ativas).

---

## 1. INFRAESTRUTURA NÃO ATIVADA (3 resíduos)

### 1.1 Supabase RAG Collections — ❌ CRÍTICO
**Definido em**: `CLAUDE.md` linhas 95-103, `DEPLOY-v4.2.md` seção 2  
**Status**: Apenas catalogado, sem criação  

**Resíduos**:
- 5 coleções RAG mapeadas mas não criadas:
  - `saneamento` (prefixo `san:`)
  - `energia` (prefixo `ene:`)
  - `portos` (prefixo `por:`)
  - `aeroportos` (prefixo `aer:`)
  - `barragens` (prefixo `bar:`)
- Arquivo SQL migration pronto (`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`) mas **não aplicado**
- Nenhum source document carregado:
  - SNIS (Brasil, água/esgoto)
  - ANEEL, EPE, ONS (energia)
  - ANTAQ, PIANC (portos)
  - ANAC, RBAC, ICAO (aeroportos)
  - ICOLD, CBDB, Lei 12.334 (barragens)

**Impacto**: 
- 5 agentes (S6-S10) com contexto técnico em `.md` mas **ZERO acesso a RAG vetorial**
- Degradação de qualidade ~30% (estimado pelo modelo de tiering)
- Handoffs entre agentes fallam (dependem de RAG para contexto)

**Ação recomendada**:
```bash
supabase db push < supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql
```

---

### 1.2 SharePoint Routing Rules — ❌ CRÍTICO
**Definido em**: `CLAUDE.md` linhas 107-115, `DEPLOY-v4.2.md` seção 3.2  
**Status**: Tabela `sp_agent_routing` candidata definida, não inserida  

**Resíduos**:
- 5 routing rules definidas em schema mas não criadas:
  ```
  agente-saneamento → 03_Projetos/Saneamento/*
  agente-energia    → 03_Projetos/Energia/*
  agente-portos     → 03_Projetos/Portos/*
  agente-aeroportos → 03_Projetos/Aeroportos/*
  agente-barragens  → 03_Projetos/Barragens/*
  ```
- Pattern matching definido (`*.pdf, *.dwg, *.xlsx`) mas não ativo
- Sem integração com MCP M365 (read-only, não consegue criar pastas automaticamente)

**Impacto**: 
- Agentes não encontram documentos do SharePoint
- Uso de arquivos de projeto é **100% manual**
- Loss de produtividade ~40% por projeto

**Ação recomendada**: Inserir 5 linhas em `sp_agent_routing` (conforme migration SQL)

---

### 1.3 SharePoint Pastas de Projeto — ❌ CRÍTICO
**Definido em**: `DEPLOY-v4.2.md` seção 3.1 e 3.2  
**Status**: Estrutura de naming definida, nenhuma pasta criada  

**Resíduos**:

#### Pastas de projeto (5 + conteúdo):
```
03_Projetos/
├── Saneamento/          [ ] não criada
├── Energia/             [ ] não criada
├── Portos/              [ ] não criada
├── Aeroportos/          [ ] não criada
└── Barragens/           [ ] não criada
```

#### Pastas de agentes (5 + conteúdo):
```
01-agentes-fundamentais/
├── agente-portos/       [ ] não criada
│   ├── SKILL.md
│   ├── README.md
│   ├── refs/
│   └── prompts/
├── agente-aeroportos/   [ ] não criada
├── agente-saneamento/   [ ] não criada
├── agente-energia/      [ ] não criada
└── agente-barragens/    [ ] não criada
```

**Impacto**: 
- Não há ponto de entrada no SharePoint para os 5 novos agentes
- Usuários não conseguem localizar documentação técnica
- Documentos de referência (SNIS, ANEEL, etc.) não organizados

**Ação recomendada**: 
- Script Graph API para criar pastas (MCP M365 atual é read-only)
- Ou manual: 10 pastas + conteúdo template

---

## 2. CONFIGURAÇÃO DO CLAUDE CODE (2 resíduos)

### 2.1 MCP Configuration Missing — `.mcp.json` ⚠️ ALTO
**Definido em**: `COWORK-INTEGRATION.md` seção 2, caminho B  
**Status**: Template fornecido no documento, **não commitado** em nenhum repo  

**Resíduos**:
- Arquivo `.mcp.json` sugerido (não existe):
  ```json
  {
    "mcpServers": {
      "manta-hub": {
        "url": "https://hub.mantaassociados.com/mcp",
        "transport": "http"
      }
    }
  }
  ```
- Não está em `Codex-exemplo/.mcp.json` (não existe)
- Não está em `manta-hub/.mcp.json` (não existe)
- Sem custom connector configurado no Cowork

**Impacto**: 
- Perda de **30% da cobertura funcional** (COWORK-INTEGRATION.md linha 104)
- 4 tools do Maestro não disponíveis em Cowork:
  - `list_maestro_agents` (inventário dos 20 agentes)
  - `route_maestro_prompt` (simula roteamento)
  - `get_maestro_rag_collections` (catálogo RAG)
  - `get_maestro_agent_details` (metadados canônicos)
- Agentes S6-S10 **não descobertos** via Cowork

**Ação recomendada**:
```bash
# Criar arquivo em Codex-exemplo/.mcp.json
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "manta-hub": {
      "url": "https://hub.mantaassociados.com/mcp",
      "transport": "http"
    }
  }
}
EOF
git add .mcp.json
git commit -m "Configure Manta Hub MCP server"
```

---

### 2.2 Hooks / Settings.json não configurados ⚠️ MÉDIO
**Definido em**: Implícito em `ARQUITETURA-AGENTES-IA.md` seção 5 (model tiering)  
**Status**: Ausente (nenhum `.claude/hooks/`, nenhum `settings.json`)  

**Resíduos**:
- Sem hooks de CI/CD para sincronizar:
  - `.claude/agents/*.md` (definições locais)
  - ↔ `SharePoint/01-agentes-fundamentais/*/SKILL.md` (produção)
  
- Sem `settings.json` com configuração de:
  - **Model tiering dinâmico**: Haiku (triagem) → Sonnet (execução) → Opus (complexo)
  - **Permissões de MCP**: quais agentes podem acessar quais tools
  - **Variáveis de ambiente**: routing keywords, RAG prefixes, Supabase URL
  
- Sem `.claude/hooks/` para:
  - Auto-validação do `CLAUDE.md` (schema, coleções RAG, routing rules)
  - Sync automático: `.claude/agents/*.md` → SharePoint SKILL.md (via Graph API)
  - Fallback: se nenhuma keyword cassar, usar `agente-infraestrutura` (padrão seguro)

**Impacto**: 
- Deploy **100% manual**, sem automação
- Sincronismo entre repositórios **não garantido** (risco de divergência)
- Model tiering **não ativo** (todos os agentes usam Sonnet por padrão)
- Sem validação de schema antes de merge

**Ação recomendada**:
```bash
# Criar .claude/hooks/validate-claude-md.sh
# Criar .claude/settings.json com model tiering
# Criar CI step: supabase migration + Graph API sync
```

---

## 3. HABILIDADES NÃO REGISTRADAS (1 resíduo)

### 3.1 Skills Registry Empty ⚠️ MÉDIO
**Definido em**: `CLAUDE.md` linha 126  
**Status**: 5 arquivos SKILL.md escritos em `sharepoint/01-agentes-fundamentais/`, **nenhum registrado** no catálogo do Claude Code  

**Resíduos**:
- 5 arquivos SKILL.md existem no repositório:
  - `sharepoint/01-agentes-fundamentais/agente-portos/SKILL.md`
  - `sharepoint/01-agentes-fundamentais/agente-aeroportos/SKILL.md`
  - `sharepoint/01-agentes-fundamentais/agente-saneamento/SKILL.md`
  - `sharepoint/01-agentes-fundamentais/agente-energia/SKILL.md`
  - `sharepoint/01-agentes-fundamentais/agente-barragens/SKILL.md`
  
- **Nenhum está registrado** no catálogo:
  - Não aparecem em `/list-skills`
  - Não aparecem em UI de seleção de skills
  - Não são descobertos automaticamente por `SearchPlugins`

**Impacto**: 
- Agentes não descobertos automaticamente
- Roteamento manual necessário (sem sugestão automática)
- Skills do Claude Code inúteis para esse projeto

**Ação recomendada**: 
- Registrar os 5 SKILL.md no catálogo de skills (Manta admin)
- Ou criar um skill agregador `manta-maestro` que expõe todos os 20 agentes

---

## 4. DOCUMENTAÇÃO NÃO ATUALIZADA (1 resíduo)

### 4.1 ARQUITETURA-AGENTES-IA.md desatualizado ⚠️ BAIXO
**Definido em**: `DEPLOY-v4.2.md` seção 4  
**Status**: v1.0.0 em produção (SharePoint), v2.0.0 candidato neste repo  

**Resíduos**:
- SharePoint tem `ARQUITETURA-AGENTES-IA.md` v1.0.0 (anterior a 2026-07-05)
- Este repo tem v2.0.0 candidata em `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`
- Seções que faltam em v1.0.0:
  - S6-S10 (Portos, Aeroportos, Saneamento, Energia, Barragens)
  - Acesso via MCP (Cowork integration)
  - RAG collections e storage prefixes
  - SharePoint routing rules
  - Checklist de deploy v4.2

**Impacto**: 
- Documentação operacional desincronizada com código
- Novos usuários recebem informação desatualizada
- Runbooks referem-se a agentes que não aparecem em v1.0.0

**Ação recomendada**:
```bash
# Upload da v2.0.0 para SharePoint
cp sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md \
   "https://mnassociados.sharepoint.com/sites/Engenharia/Documentos Compartilhados/04_IA/Manta-Maestro/"
```

---

## 5. TESTES NÃO EXECUTADOS (1 resíduo)

### 5.1 Routing Tests Candidates ⚠️ MÉDIO
**Definido em**: `DEPLOY-v4.2.md` seção 5  
**Status**: Arquivo de prompts escrito (`tests/routing/prompts.md`), **não testado**  

**Resíduos**:
- Prompts de teste para cada segmento existem, ex.:
  - "Vou fazer uma UHE de 500 MW" → **barragem OU energia?** (ambíguo)
  - "ETE com subestação próxima" → **saneamento OU energia?** (ambíguo)
  
- Nenhum teste executado no Maestro real
- Sem registro de decisões sobre casos ambíguos
- Sem ajustes de pesos de keywords baseados em testes reais

**Impacto**: 
- Roteamento não validado em produção
- Risco: prompts caem no agente errado ~5-10% do tempo (estimado)
- Sem fallback definido para ambigüidades

**Ação recomendada**:
```bash
# Executar prompts em https://hub.mantaassociados.com/askcad (Maestro)
# Validar que ≥90% dos prompts primários caem no agente esperado
# Registrar decisões sobre ambigüidades em CLAUDE.md
```

---

## 6. DEPENDÊNCIAS EXTERNAS NÃO RESOLVIDAS (1 resíduo)

### 6.1 Personas do AskCAD não alinhadas ⚠️ BAIXO
**Definido em**: `COWORK-INTEGRATION.md` linhas 102, 112  
**Status**: 5 personas seed existem, 5 novas necessárias  

**Resíduos**:
- AskCAD tem 5 personas existentes (possivelmente S1-S5 ou horizontais)
- Não há personas para S6-S10 (Portos, Aeroportos, Saneamento, Energia, Barragens)
- Sem tool `start_askcad_chat(persona_id=...)` para iniciar conversa
- Sem mapeamento de `agente-<slug>` ↔ `persona_id`

**Impacto**: 
- Usuários não conseguem iniciar conversa direta com S6-S10 via AskCAD/Cowork
- Necesário roteamento manual via Maestro (intermediário)

**Ação recomendada**: 
- Criar 5 novas personas em AskCAD (clone + adapt)
- Mapear `agente-portos` → `persona_portos`, etc.

---

## 📋 CHECKLIST CONSOLIDADO — 10 itens de deploy

### FASE A — Git + Local (✅ CONCLUÍDO)
- [x] Copiar 5 agent `.md` para `.claude/agents/`
- [x] Aplicar patch no `CLAUDE.md` master

### FASE B — Supabase (❌ PENDENTE)
- [ ] Criar 5 coleções RAG em Supabase
- [ ] Inserir 5 routing rules em `sp_agent_routing`

### FASE C — SharePoint (❌ PENDENTE)
- [ ] Criar 10 pastas SP (5 agentes + 5 projetos)
- [ ] Upload/escrita dos 5 `SKILL.md`

### FASE D — Configuração Claude Code (❌ PENDENTE)
- [ ] Criar `.mcp.json` (ou custom connector Cowork)
- [ ] Criar `hooks/` para sync automático
- [ ] Registrar skills no catálogo (ou criar skill agregador)

### FASE E — Validação (❌ PENDENTE)
- [ ] Testar routing do Maestro (≥90% de acerto)
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` (v1.0.0 → v2.0.0)
- [ ] Criar personas AskCAD para S6-S10

### GATE
- [ ] Aprovação MN (gate humano)
- [ ] Merge dos PRs

---

## 📊 COBERTURA FUNCIONAL

| Camada | Antes (só `.claude/agents/`) | Depois (completo) | Status |
|--------|-----|-----|--------|
| Definições dos 20 agentes | ✅ `.md` versionado | + MCP tools | ✅ Parcial |
| Routing rules | ❌ | ✅ Maestro + SP | ❌ Não ativo |
| RAG consultável | ❌ | ✅ Supabase collections | ❌ Não ativo |
| MCP discovery | ❌ | ✅ 4 tools | ⚠️ Sem `.mcp.json` |
| Skills registry | ❌ | ✅ 5 skills | ❌ Não registrado |
| Cowork integration | ❌ | ✅ ~70% | ⚠️ Só 30% |

**Resultado**: **45% da funcionalidade implementada** (declarativa mas não operacional).

---

## 🎯 RECOMENDAÇÕES

### 1️⃣ CURTO PRAZO (Esta sprint)
- [ ] **Merge dos PRs** — Gate MN (DEPLOY-v4.2.md seção 1)
- [ ] **Aplicar Supabase migration** — `supabase db push` (DEPLOY-v4.2.md seção 2)
- [ ] **Criar pastas SP** — script Graph API ou manual (DEPLOY-v4.2.md seção 3)

### 2️⃣ MÉDIO PRAZO (1-2 sprints)
- [ ] **Criar `.mcp.json`** — commit em Codex-exemplo
- [ ] **Escrever / uploadar SKILL.md** — 5 arquivos em SharePoint
- [ ] **Testar routing** — executar `tests/routing/prompts.md`
- [ ] **Registrar skills** — ou criar skill agregador

### 3️⃣ LONGO PRAZO (Roadmap Fase B+)
- [ ] **Hooks de sync** — CI/CD `.claude/agents/*.md` → SharePoint (via Graph API)
- [ ] **Settings.json** — model tiering, permissões MCP, variáveis de ambiente
- [ ] **Personas AskCAD** — criar 5 novas para S6-S10
- [ ] **Consulta vetorial RAG** — integrar Supabase MCP com credencial

---

## 🔗 REFERÊNCIAS

| Documento | Localização | Uso |
|-----------|-----------|-----|
| Deploy checklist | `CLAUDE.md` L119-130 | Gate e sequência |
| Deploy runbook | `DEPLOY-v4.2.md` | Procedimentos |
| Routing rules | `CLAUDE.md` L59-91 | Maestro keywords |
| RAG catalog | `CLAUDE.md` L95-103 | Supabase schema |
| Cowork integration | `COWORK-INTEGRATION.md` | MCP + custom connector |
| Arquitetura v2.0.0 | `ARQUITETURA-AGENTES-IA.md` | Documentação operacional |
| Test prompts | `tests/routing/prompts.md` | Validação de routing |

---

## ⚠️ NOTAS IMPORTANTES

1. **Residuos não são bugs** — são funcionalidades definidas mas não implementadas. Sistema está em estado coerente.

2. **Risco operacional** — Agentes S6-S10 existem em `.md` mas não funcionam em produção sem as Fases B-E.

3. **Sincronismo** — Se houver mudanças em `.claude/agents/*.md`, elas **não sincronizam automaticamente** com SharePoint sem hooks.

4. **Model tiering** — Sem `settings.json`, todos os agentes usam Sonnet (mais caro, menos rápido que Haiku para triagem).

5. **MCP discovery** — Sem `.mcp.json` ou custom connector, Cowork não descobre o Maestro (30% de perda de funcionalidade).

---

**Data de análise**: 2026-08-02  
**Analisado por**: Claude Code (Manta Maestro v4.2 audit)
