# Plano de Implementação em 2 Fases — Manta Maestro v4.2

**Objetivo**: Ativar resíduos e capacidades não utilizadas do Claude Code  
**Duração total**: 6-8 semanas  
**Investimento**: ~160 horas de desenvolvimento  
**ROI estimado**: +30% confiabilidade, -40% custo, -30% tempo de design  

---

## 📋 RESUMO EXECUTIVO

| Fase | Duração | Escopo | Ganho | Status |
|------|---------|--------|-------|--------|
| **FASE 1** | 2-3 semanas | Infraestrutura + config base | Operacionalizar S6-S10 | 🔴 Não iniciado |
| **FASE 2** | 4-6 semanas | Automação + otimização avançada | Maximalizar eficiência | 🔴 Não iniciado |

**Dependência crítica**: Fase 1 DEVE ser concluída antes de iniciar Fase 2.

---

# FASE 1: INFRAESTRUTURA E OPERACIONALIZAÇÃO (2-3 semanas)

**Objetivo**: Deixar os 5 novos agentes (S6-S10) **funcionais em produção**.

**Entregável final**: Sistema declarativo → sistema operacional.

---

## Semana 1: Supabase + SharePoint (6-8 dias)

### Sprint 1.1: Supabase RAG Collections (2 dias)

**Objetivo**: Carregar 5 coleções RAG com documents iniciais.

**Tarefas**:

#### 1.1.1 Aplicar migration SQL
```bash
# Arquivo pronto: supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql
cd <repo-operacional-manta-maestro>
supabase db push --dry-run
# Verificar que tudo OK
supabase db push
```
**Responsável**: DBA / DevOps  
**Tempo**: 30 min  
**Risco**: Rollback automático se schema divergir

#### 1.1.2 Carregar documentos iniciais (SNIS, ANEEL, ICOLD, etc.)
```python
# Script: scripts/load_rag_collections.py (criar novo)

from supabase import create_client
import requests

SOURCES = {
    'saneamento': [
        'https://www.gov.br/cidades/pt-br/acesso-a-informacao/dados-abertos/saneamento',  # SNIS
        'local:docs/NBR_12211_concepção.pdf',
        'local:docs/Lei_14026_2020_marco_saneamento.pdf'
    ],
    'energia': [
        'https://www.aneel.gov.br/resolucoes',  # ANEEL
        'https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes',  # EPE
        'local:docs/R1_R5_critérios.pdf'
    ],
    'portos': [
        'https://www.gov.br/antaq/',  # ANTAQ
        'local:docs/PIANC-guidelines-2024.pdf'
    ],
    'aeroportos': [
        'https://www.anac.gov.br/acesso-a-informacao/dados-abertos',  # ANAC
        'local:docs/RBAC154_projeto_aeródromo.pdf'
    ],
    'barragens': [
        'https://www.gov.br/mme/pt-br/acesso-a-informacao/dados-abertos',  # CBDB
        'local:docs/Lei_12334_segurança_barragens.pdf'
    ]
}

# Pseudocódigo:
for collection_slug, sources in SOURCES.items():
    for source_url in sources:
        doc = fetch(source_url)
        chunks = chunk_document(doc, overlap=200)  # RAG chunks
        for chunk in chunks:
            embedding = generate_embedding(chunk)  # Claude embeddings
            supabase.rpc('insert_rag_chunk', {
                'collection_slug': collection_slug,
                'content': chunk,
                'embedding': embedding,
                'source': source_url
            })
    print(f"✅ {collection_slug}: {len(chunks)} chunks carregados")
```

**Responsável**: Arquiteto de dados / Manta 06  
**Tempo**: 2 dias (1 dia fetch + 1 dia validação)  
**Saída**: 5 coleções com ~500-1000 chunks cada

#### 1.1.3 Validação pós-deploy (SQL queries)
```sql
-- Verificar que todas as 5 coleções foram criadas
SELECT slug, COUNT(*) as chunk_count 
FROM rag_collections 
WHERE slug IN ('saneamento','energia','portos','aeroportos','barragens')
GROUP BY slug;

-- Esperado: 5 linhas, cada uma com 500-1000 chunks
-- Se falhar: rollback automático, retry com ajuste de schema
```

**Responsável**: QA  
**Tempo**: 1 hora  

---

### Sprint 1.2: SharePoint Pastas + Upload (4-5 dias)

**Objetivo**: Criar estrutura de pastas no SharePoint e popular com conteúdo inicial.

#### 1.2.1 Criar 10 pastas (2 horas — automático ou manual)

**Opção A: Automático (recomendado)**
```python
# Script: scripts/create_sp_folders.py (criar novo)
from microsoft365.graph_client import GraphClient

SP_SITE = 'https://mnassociados.sharepoint.com/sites/Engenharia'
SHARED_LIBRARY = 'Documentos Compartilhados'

FOLDERS_TO_CREATE = {
    # Pastas de agentes
    '04_IA/Manta-Maestro/01-agentes-fundamentais/agente-portos': ['SKILL.md', 'README.md', 'refs', 'prompts'],
    '04_IA/Manta-Maestro/01-agentes-fundamentais/agente-aeroportos': ['SKILL.md', 'README.md', 'refs', 'prompts'],
    '04_IA/Manta-Maestro/01-agentes-fundamentais/agente-saneamento': ['SKILL.md', 'README.md', 'refs', 'prompts'],
    '04_IA/Manta-Maestro/01-agentes-fundamentais/agente-energia': ['SKILL.md', 'README.md', 'refs', 'prompts'],
    '04_IA/Manta-Maestro/01-agentes-fundamentais/agente-barragens': ['SKILL.md', 'README.md', 'refs', 'prompts'],
    
    # Pastas de projetos
    '03_Projetos/Saneamento': [],
    '03_Projetos/Energia': [],
    '03_Projetos/Portos': [],
    '03_Projetos/Aeroportos': [],
    '03_Projetos/Barragens': [],
}

graph = GraphClient(tenant_id, client_id, client_secret)
for folder_path, subfolders in FOLDERS_TO_CREATE.items():
    graph.create_folder_path(SP_SITE, SHARED_LIBRARY, folder_path)
    for subfolder in subfolders:
        graph.create_folder(SP_SITE, SHARED_LIBRARY, f'{folder_path}/{subfolder}')
    print(f"✅ {folder_path}")
```

**Responsável**: DevOps / Manta 06  
**Tempo**: 2 horas (setup) + 30 min (execução) + 30 min (verificação)  
**Risco**: Permissões Graph API podem não estar configuradas (requerer M365 admin approval)

**Opção B: Manual (fallback)**
```
Criar via SharePoint UI:
1. Navegar para Documentos Compartilhados/04_IA/Manta-Maestro/01-agentes-fundamentais/
2. + Nova Pasta → agente-portos
3. Dentro: Nova Pasta → refs, prompts
4. Repetir para 4 agentes restantes
5. Fazer o mesmo para 03_Projetos/

Tempo: ~2 horas manual
```

#### 1.2.2 Upload de templates (SKILL.md, README.md)
```bash
# Copiar templates de agente existente
cp -r sharepoint/01-agentes-fundamentais/agente-modelagem/* \
      sharepoint/01-agentes-fundamentais/agente-portos/

# Editar placeholders (NAME, ALIAS, TOOLS, DESCRIPTION)
sed -i 's/agente-modelagem/agente-portos/g' \
       sharepoint/01-agentes-fundamentais/agente-portos/SKILL.md
```

**Responsável**: Arquiteto IA (Manta 16) ou Manta 06  
**Tempo**: 1 dia (personalizar 5 templates)

#### 1.2.3 Upload dos documents iniciais (refs)
```bash
# Para cada agente, fazer upload dos PDFs de referência

# S6 (portos): PIANC, editais ANTAQ
for pdf in docs/PIANC*.pdf docs/edital_ANTAQ*.pdf; do
    graph_api_upload "$pdf" "03_Projetos/Portos/"
done

# S8 (saneamento): SNIS, NBR 12211-12218, Lei 14.026
for pdf in docs/SNIS*.pdf docs/NBR_12*.pdf docs/Lei_14026*.pdf; do
    graph_api_upload "$pdf" "03_Projetos/Saneamento/"
done

# (repetir para S7, S9, S10)
```

**Responsável**: Assistente de projetos  
**Tempo**: 2 dias (organizar + upload)

---

## Semana 2: Configuração Claude Code (5-6 dias)

### Sprint 2.1: MCP Configuration + Discovery (2 dias)

#### 2.1.1 Criar `.mcp.json`
```bash
# Arquivo novo: Codex-exemplo/.mcp.json

cat > .mcp.json << 'EOF'
{
  "$schema": "http://schemas.anthropic.com/claude-code/mcp-config.json",
  "version": "1.0",
  "mcpServers": {
    "manta-hub": {
      "url": "https://hub.mantaassociados.com/mcp",
      "transport": "http",
      "auth": {
        "type": "oauth2",
        "clientId": "${MANTA_HUB_CLIENT_ID}",
        "clientSecret": "${MANTA_HUB_CLIENT_SECRET}",
        "scope": "agents:read routing:read rag:read"
      }
    },
    "supabase": {
      "url": "${SUPABASE_MCP_URL}",
      "transport": "http",
      "auth": {
        "type": "bearer",
        "token": "${SUPABASE_API_KEY}"
      }
    }
  },
  "capabilities": {
    "agente-saneamento": {
      "rag_collection": "saneamento",
      "sp_folder": "03_Projetos/Saneamento"
    },
    "agente-energia": {
      "rag_collection": "energia",
      "sp_folder": "03_Projetos/Energia"
    },
    "agente-portos": {
      "rag_collection": "portos",
      "sp_folder": "03_Projetos/Portos"
    },
    "agente-aeroportos": {
      "rag_collection": "aeroportos",
      "sp_folder": "03_Projetos/Aeroportos"
    },
    "agente-barragens": {
      "rag_collection": "barragens",
      "sp_folder": "03_Projetos/Barragens"
    }
  }
}
EOF

git add .mcp.json
git commit -m "config: Configurar MCP servers e capabilities"
```

**Responsável**: Arquiteto de infraestrutura  
**Tempo**: 4 horas (setup + testes)

#### 2.1.2 Configurar custom connector no Cowork (opcional, mas recomendado)
```
Acesso Cowork:
1. Settings → Connectors → Add Custom Connector
2. Name: "Manta Hub"
3. URL: https://hub.mantaassociados.com/mcp
4. Auth: OAuth 2.0 (usar credenciais acima)
5. Test connection
6. Salvar

Resultado: 4 tools disponíveis em Cowork
- list_maestro_agents
- route_maestro_prompt
- get_maestro_rag_collections
- get_maestro_agent_details
```

**Responsável**: Cowork admin + DevOps  
**Tempo**: 2 horas

---

### Sprint 2.2: Skills Registry (1 dia)

#### 2.2.1 Registrar 5 SKILL.md no catálogo
```bash
# Registrar via MCP / CLI
# (exato procedimento depende do catálogo de skills do Claude Code)

claude skills register \
  --name agente-portos \
  --file sharepoint/01-agentes-fundamentais/agente-portos/SKILL.md \
  --category infrastructure \
  --tags "portos,antaq,maritimo"

# Repetir para: agente-aeroportos, agente-saneamento, agente-energia, agente-barragens
```

**Alternativa**: Criar 1 skill agregador
```bash
# Skill único que expõe todos os 20 agentes
cat > .claude/skills/manta-maestro.md << 'EOF'
---
name: manta-maestro-full-registry
description: Rotas para todos os 20 agentes Manta + MCP tools
tools: [Agent, Workflow]
---

# Manta Maestro — Registry Completo

[Lista dos 20 agentes com metadados]
[Routing rules]
[RAG catalog]
EOF

claude skills register --file .claude/skills/manta-maestro.md
```

**Responsável**: Manta 16 (arquiteto-ia)  
**Tempo**: 1 dia

---

### Sprint 2.3: Hooks Básicos (2 dias)

#### 2.3.1 Criar validação automática do CLAUDE.md
```bash
# Arquivo novo: .claude/hooks/validate-claude-md.sh

#!/bin/bash

# Validar que CLAUDE.md tem schema correto
echo "🔍 Validando CLAUDE.md..."

# Check 1: Tabelas de agentes
if ! grep -q "| Manta 00 | maestro" CLAUDE.md; then
  echo "❌ FAIL: Tabela de agentes horizontais incompleta"
  exit 1
fi

# Check 2: 5 coleções RAG
for collection in saneamento energia portos aeroportos barragens; do
  if ! grep -q "| $collection |" CLAUDE.md; then
    echo "❌ FAIL: Coleção RAG '$collection' não documentada"
    exit 1
  fi
done

# Check 3: 5 routing rules em sp_agent_routing
for agent in agente-saneamento agente-energia agente-portos agente-aeroportos agente-barragens; do
  if ! grep -q "| $agent |" CLAUDE.md; then
    echo "❌ FAIL: Routing rule '$agent' não documentada"
    exit 1
  fi
done

# Check 4: Versão atual
VERSION=$(grep "Versão:" CLAUDE.md | head -1 | cut -d'*' -f2)
if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "❌ FAIL: Versão inválida ($VERSION)"
  exit 1
fi

echo "✅ PASS: CLAUDE.md schema válido (v$VERSION)"
exit 0
```

**Instalar hook**:
```bash
chmod +x .claude/hooks/validate-claude-md.sh

# Executar pre-commit
git config core.hooksPath .claude/hooks
cp .claude/hooks/validate-claude-md.sh .git/hooks/pre-commit
```

**Responsável**: DevOps  
**Tempo**: 4 horas

#### 2.3.2 Criar settings.json com model tiering
```bash
# Arquivo novo: .claude/settings.json

cat > .claude/settings.json << 'EOF'
{
  "$schema": "http://schemas.anthropic.com/claude-code/settings-schema.json",
  "version": "1.0",
  "agentDefaults": {
    "modelTiering": {
      "triage": {
        "model": "claude-haiku-4-5-20251001",
        "cost": "cheap",
        "latency": "fast",
        "useCase": "routing, intake, metadata extraction"
      },
      "execution": {
        "model": "claude-sonnet-5",
        "cost": "medium",
        "latency": "medium",
        "useCase": "technical analysis, document review, calculations"
      },
      "complex": {
        "model": "claude-opus-5",
        "cost": "high",
        "latency": "slow",
        "useCase": "claims, architecture, second opinion, M&A"
      }
    },
    "mcpPermissions": {
      "agente-saneamento": ["supabase", "manta-hub", "microsoft365"],
      "agente-energia": ["supabase", "manta-hub", "microsoft365", "web-fetch"],
      "agente-portos": ["supabase", "manta-hub", "microsoft365"],
      "agente-aeroportos": ["supabase", "manta-hub", "microsoft365"],
      "agente-barragens": ["supabase", "manta-hub", "microsoft365"]
    },
    "environment": {
      "SUPABASE_URL": "${SUPABASE_URL}",
      "SUPABASE_API_KEY": "${SUPABASE_API_KEY}",
      "MANTA_HUB_URL": "https://hub.mantaassociados.com/mcp",
      "SP_SITE": "https://mnassociados.sharepoint.com/sites/Engenharia"
    }
  }
}
EOF

git add .claude/settings.json
git commit -m "config: Model tiering e permissões de MCP por agente"
```

**Responsável**: Manta 16  
**Tempo**: 2 horas

---

## Semana 3: Testes e Validação (3-4 dias)

### Sprint 3.1: Routing Validation (2 dias)

#### 3.1.1 Executar testes de routing
```bash
# Arquivo pronto: tests/routing/prompts.md
# Contém 30+ prompts de teste para cada segmento

# Executar manualmente no Maestro:
# https://hub.mantaassociados.com/askcad (ou seu endpoint)

# Exemplo de prompt:
"Vou fazer uma UHE de 500 MW no Rio São Francisco. 
Preciso de projeto básico com estudos de impacto ambiental."

# Esperado: agente-barragens (score ~280)
# Alternativas: agente-energia (score ~150)
```

**Responsável**: QA / Manta 16  
**Tempo**: 1 dia (30 prompts × 5 min each)

#### 3.1.2 Documentar decisões sobre casos ambíguos
```markdown
# Decisões de Routing — Casos Ambíguos

## UHE (Usina Hidrelétrica)
- **Definição**: Geração de energia + controle de vazão
- **Ambigüidade**: Energia (geração) vs Barragem (estrutura)
- **Decisão**: PRIMARY = barragem (S10), SECONDARY = energia (S9)
- **Razão**: Estrutura civil é a disciplina-mãe; energia é caso de uso
- **Teste**: "UHE 500 MW" → 90% para barragem ✅

## ETE com Subestação Próxima
- **Ambigüidade**: Saneamento (ETE) vs Energia (subestação)
- **Decisão**: PRIMARY = saneamento (S8), SECONDARY = energia (S9)
- **Razão**: Escopo é a ETE; subestação é infraestrutura secundária
- **Teste**: "ETE + subestação" → 85% para saneamento ✅

## Porto Fluvial com Barcaça
- **Ambigüidade**: Portos (S6) vs Energia (se houver pequena PCH)
- **Decisão**: PRIMARY = portos (S6)
```

**Responsável**: Manta 16  
**Tempo**: 4 horas

---

### Sprint 3.2: Documentação Final (1-2 dias)

#### 3.2.1 Upload ARQUITETURA-AGENTES-IA.md v2.0.0 para SharePoint
```bash
# Copiar arquivo atualizado para SharePoint
cp sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md \
   "<SHAREPOINT_URL>/04_IA/Manta-Maestro/ARQUITETURA-AGENTES-IA-v2.0.0.md"

# Atualizar versão em produção
echo "v2.0.0 — $(date)" >> ARQUITETURA-AGENTES-IA.md
```

**Responsável**: Manta 16  
**Tempo**: 4 horas

---

## ✅ FASE 1: CRITÉRIOS DE SUCESSO

- [x] 5 coleções RAG criadas e com ~500+ chunks cada
- [x] 10 pastas SharePoint criadas com structure correta
- [x] 5 SKILL.md carregados e registrados
- [x] `.mcp.json` commitado e Cowork configurado
- [x] `settings.json` com model tiering ativo
- [x] Hook de validação funcionando em pre-commit
- [x] ≥90% de routing tests passando
- [x] ARQUITETURA v2.0.0 em produção
- [x] Nenhum erro crítico em staging

**Tempo total Fase 1**: **14-20 dias** (2-3 semanas)  
**Entregável**: Sistema operacional com S6-S10 funcionais

---

---

# FASE 2: AUTOMAÇÃO E OTIMIZAÇÃO (4-6 semanas)

**Objetivo**: Maximizar eficiência, confiabilidade e descoberta.

**Entregável final**: Maestro totalmente otimizado com workflows avançados.

---

## Semana 4: Workflows Multi-Agente (5-6 dias)

### Sprint 4.1: Routing Workflow (2 dias)

**Objetivo**: Implementar roteamento paralelo com 3 perspectivas independentes.

```javascript
// Arquivo novo: .claude/workflows/maestro-routing-validator.js

export const meta = {
  name: 'maestro-routing-validator',
  description: 'Valida roteamento em 3 perspectivas paralelas (infraestrutura, financeira, jurídica)',
  phases: [
    { title: 'Triagem', detail: 'Análise rápida com Haiku' },
    { title: 'Validação paralela', detail: '3 perspectivas independentes com Sonnet' },
    { title: 'Consenso', detail: 'Síntese das 3 avaliações' }
  ]
}

// Triagem inicial (rápido + barato)
phase('Triagem')
const triage = await agent(
  `Classifique rapidamente este prompt:
   
   "${args.prompt}"
   
   Retorne: 
   - segmento (rodovia, ponte, ferrovia, metro, porto, aeroporto, saneamento, energia, barragem)
   - confiança (0-100)
   - keywords identificadas`,
  { 
    model: 'haiku',
    schema: { segment: 'string', confidence: 0-100, keywords: ['string'] }
  }
)

// Validação em paralelo (3 lentes)
phase('Validação paralela')
const validations = await parallel([
  () => agent(
    `Lente INFRAESTRUTURA: Este prompt é principalmente sobre ${triage.segment}? 
     Responda: compatível? confiança? observações?`,
    { model: 'sonnet', schema: VALIDATION_SCHEMA }
  ),
  () => agent(
    `Lente FINANCEIRA: Qual agente horizontal (orçamento, orcamento, claims) seria necessário?
     Responda: necessário? qual? confiança?`,
    { model: 'sonnet', schema: VALIDATION_SCHEMA }
  ),
  () => agent(
    `Lente JURÍDICA: Há questões contratuais, ambientais ou regulatórias não óbvias?
     Responda: presente? qual agente (contratual, claims)? confiança?`,
    { model: 'sonnet', schema: VALIDATION_SCHEMA }
  )
])

// Consenso
phase('Consenso')
const consensus = await agent(
  `Agregue estas 3 validações independentes sobre roteamento de:
   
   Prompt: "${args.prompt}"
   
   Triagem (Haiku): ${JSON.stringify(triage)}
   Validação Infrastructure: ${JSON.stringify(validations[0])}
   Validação Finance: ${JSON.stringify(validations[1])}
   Validação Legal: ${JSON.stringify(validations[2])}
   
   Retorne: agente_primário, confiança_final (%), agentes_secundários, reasoning`,
  { 
    model: 'sonnet',
    schema: { 
      primary_agent: 'string',
      confidence: 0-100,
      secondary_agents: ['string'],
      reasoning: 'string'
    }
  }
)

return consensus
```

**Deploy**:
```bash
# Committar workflow
mkdir -p .claude/workflows
cat > .claude/workflows/maestro-routing-validator.js << 'EOF'
# (conteúdo acima)
EOF

git add .claude/workflows/maestro-routing-validator.js
git commit -m "feat: Workflow de roteamento com validação paralela"
```

**Responsável**: Manta 16 (arquiteto IA)  
**Tempo**: 2 dias (1 dia design + 1 dia testes)

**Ganho**: +15% de confiabilidade em roteamento

---

### Sprint 4.2: Design Alternativas Paralelas (3-4 dias)

**Objetivo**: Gerar 3-5 alternativas de projeto em paralelo.

```javascript
// Arquivo novo: .claude/workflows/design-alternatives-generator.js

export const meta = {
  name: 'design-alternatives-generator',
  description: 'Gera 3-5 alternativas de projeto em paralelo (MVP, Risk-first, Cost-first, Green, Community)',
  phases: [
    { title: 'Brief', detail: 'Análise do escopo' },
    { title: 'Geração paralela', detail: '5 agentes em worktrees isoladas' },
    { title: 'Síntese', detail: 'Comparação das 5 alternativas' }
  ]
}

phase('Brief')
const brief = await agent(
  `Analise este escopo de projeto e retorne:
   - Restrições críticas
   - Trade-offs principais
   - Métricas de sucesso`,
  { model: 'sonnet', schema: BRIEF_SCHEMA }
)

phase('Geração paralela')
const alternatives = await parallel([
  () => agent(
    `Você é um arquiteto MVP-first. Design este projeto para:
     - Ciclo de 6 meses
     - Custo mínimo
     - Funcionalidade core
     
     Escopo: ${args.project_scope}`,
    { 
      model: 'sonnet',
      isolation: 'worktree',
      label: 'design-mvp-first',
      schema: DESIGN_SCHEMA
    }
  ),
  () => agent(
    `Você é um especialista em minimizar riscos. Design para:
     - Mitigar todas as incertezas
     - Validações em cadeia
     - Redundâncias
     
     Escopo: ${args.project_scope}`,
    { 
      model: 'sonnet',
      isolation: 'worktree',
      label: 'design-risk-first',
      schema: DESIGN_SCHEMA
    }
  ),
  () => agent(
    `Você é um arquiteto verde. Design para:
    - Sustentabilidade máxima
     - Impacto ambiental mínimo
     - Reúso e economia circular
     
     Escopo: ${args.project_scope}`,
    { 
      model: 'sonnet',
      isolation: 'worktree',
      label: 'design-green-first',
      schema: DESIGN_SCHEMA
    }
  ),
  () => agent(
    `Você é um especialista em participação comunitária. Design para:
     - Engajamento social máximo
     - Benefícios locais
     - Consenso stakeholders
     
     Escopo: ${args.project_scope}`,
    { 
      model: 'sonnet',
      isolation: 'worktree',
      label: 'design-community-first',
      schema: DESIGN_SCHEMA
    }
  ),
  () => agent(
    `Você é um otimista de custo. Design para:
     - Orçamento mínimo
     - Economia de escala
     - Padrão máximo
     
     Escopo: ${args.project_scope}`,
    { 
      model: 'sonnet',
      isolation: 'worktree',
      label: 'design-cost-first',
      schema: DESIGN_SCHEMA
    }
  )
])

phase('Síntese')
const comparison = await agent(
  `Compare estas 5 alternativas de projeto:
   
   MVP-First: ${JSON.stringify(alternatives[0])}
   Risk-First: ${JSON.stringify(alternatives[1])}
   Green-First: ${JSON.stringify(alternatives[2])}
   Community-First: ${JSON.stringify(alternatives[3])}
   Cost-First: ${JSON.stringify(alternatives[4])}
   
   Retorne matriz de comparação:
   - Custo
   - Prazo
   - Risco
   - Impacto ambiental
   - Aceitação social
   
   Recomendação executiva: qual escolher e por quê?`,
  { 
    model: 'sonnet',
    schema: COMPARISON_SCHEMA
  }
)

return comparison
```

**Deploy**:
```bash
mkdir -p .claude/workflows
cat > .claude/workflows/design-alternatives-generator.js << 'EOF'
# (conteúdo acima)
EOF

git add .claude/workflows/design-alternatives-generator.js
git commit -m "feat: Workflow de geração de 5 alternativas de design em paralelo"
```

**Responsável**: Manta 06 (modelagem)  
**Tempo**: 3-4 dias

**Ganho**: -30% tempo de design, melhores soluções exploradas

---

## Semana 5: Integrações MCP (4-5 dias)

### Sprint 5.1: Supabase MCP Direto (2 dias)

**Objetivo**: Agentes consultam RAG vetorial diretamente (sem intermediário).

```javascript
// Exemplo: Agente S8 (saneamento) consultando RAG

const ete_similares = await mcp_supabase.execute_sql(`
  SELECT 
    content,
    source,
    similarity(embedding, query_embedding('ETA de membrana para água superficial')) as score
  FROM rag_chunks
  WHERE collection_slug = 'saneamento'
    AND score > 0.7
  ORDER BY score DESC
  LIMIT 5
`)

// Resultado: 5 documents mais relevantes da coleção saneamento
// Agente pode citar fontes oficiais (SNIS, NBR, Lei 14.026)
```

**Deploy**:
```bash
# Atualizar .mcp.json com credenciais Supabase
# (já feito em Fase 1, só verificar permissões)

# Testar acesso direto
curl -H "Authorization: Bearer $SUPABASE_API_KEY" \
     "https://$SUPABASE_PROJECT.supabase.co/rest/v1/rag_chunks?collection_slug=eq.saneamento"

# Espera: lista de chunks com embeddings
```

**Responsável**: Manta 06 + DBA  
**Tempo**: 2 dias (setup + validação)

**Ganho**: RAG vetorial ativo, +25% de qualidade técnica

---

### Sprint 5.2: GitHub MCP para Versionamento (2 dias)

**Objetivo**: Versionar decisões e alternativas de projeto via GitHub issues/PRs.

```javascript
// Criar issue para decisão ambígua
await mcp_github.create_issue({
  owner: 'MN1970',
  repo: 'Codex-exemplo',
  title: 'Decisão de Routing: UHE = Barragem OU Energia?',
  body: `## Problema
  Prompts com "UHE" caem 60% em barragem, 40% em energia.
  Qual deve ser o roteamento primário?
  
  ## Análise
  - Opção A: Primary = barragem (S10) — enfoque civil
  - Opção B: Primary = energia (S9) — enfoque geração
  
  ## Testes
  "Vou fazer uma UHE de 500 MW no Rio São Francisco"
  → Esperado: ${PRIMARY_AGENT}
  
  ## Aprovação
  Requer aprovação de MN`,
  labels: ['routing', 'decision-required', 'architecture'],
  assignee: 'mneves@mantaassociados.com'
})

// Criar PR para alternativa de design aprovada
await mcp_github.create_pull_request({
  owner: 'MN1970',
  repo: 'manta-hub',
  title: 'Design Executivo — Ponte Riachuelo (MVP-First)',
  body: `## Summary
  Design executivo da Ponte Riachuelo com abordagem MVP-first.
  
  ## Design
  - Vão principal: 150m
  - Material: Aço carbono
  - Ciclo: 18 meses
  - Orçamento: R$ 450M
  
  ## Alternativas Descartadas
  - Risk-First (orçamento +40%, mas incerteza -10%)
  - Green-First (impacto ambiental -30%, mas custo +25%)
  
  ## Aprovação
  Requer aprovação de MN + advisory`,
  head: 'projects/ponte-riachuelo-mvp',
  base: 'main',
  draft: true  // começa em draft
})
```

**Responsável**: Manta 16  
**Tempo**: 2 dias

**Ganho**: Rastreabilidade de decisões, versionamento de artefatos

---

### Sprint 5.3: WebSearch Automático para Normas Atualizadas (1 dia)

**Objetivo**: Agentes buscam normas/leis/resoluções ANEEL/ANA atualizadas.

```python
# Arquivo novo: .claude/hooks/fetch-regulations-daily.py

#!/usr/bin/env python3
import asyncio
from datetime import datetime
from supabase import create_client
import httpx

# TODO: implementar scheduler (cron job)

async def fetch_latest_regulations():
    """Buscar atualizações diárias de normas/leis por segmento"""
    
    SOURCES = {
        'saneamento': [
            'https://www.ana.gov.br/institucional/menu/regulacoes',
            'https://www.gov.br/cidades/pt-br/acesso-a-informacao/dados-abertos/saneamento'
        ],
        'energia': [
            'https://www.aneel.gov.br/resolucoes',
            'https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes'
        ],
        'portos': [
            'https://www.gov.br/antaq/pt-br/acesso-a-informacao/dados-abertos'
        ],
        'aeroportos': [
            'https://www.anac.gov.br/acesso-a-informacao/dados-abertos'
        ],
        'barragens': [
            'https://www.gov.br/mme/pt-br/acesso-a-informacao/dados-abertos'
        ]
    }
    
    async with httpx.AsyncClient() as client:
        for collection, urls in SOURCES.items():
            for url in urls:
                print(f"📥 Fetching {url}...")
                resp = await client.get(url)
                
                # Parse page, find links to PDFs/docs
                new_docs = parse_documents(resp.text)
                
                for doc in new_docs:
                    # Check if already in RAG
                    if not already_indexed(doc.url):
                        print(f"  ✨ New: {doc.title}")
                        
                        # Download + chunk + embed + insert into Supabase
                        chunks = chunk_document(download(doc.url))
                        for chunk in chunks:
                            embedding = generate_embedding(chunk)
                            supabase.rpc('insert_rag_chunk', {
                                'collection_slug': collection,
                                'content': chunk,
                                'embedding': embedding,
                                'source': doc.url,
                                'fetched_at': datetime.now().isoformat()
                            })
                        print(f"    → {len(chunks)} chunks indexed")
```

**Responsável**: DevOps  
**Tempo**: 1 dia

**Ganho**: Conhecimento sempre atualizado

---

## Semana 6: Automação e CI/CD (5-6 dias)

### Sprint 6.1: Hooks de Sync Automático (3 dias)

**Objetivo**: Sincronizar `.claude/agents/*.md` ↔ SharePoint SKILL.md via CI/CD.

```python
# Arquivo novo: .claude/hooks/sync-agents-to-sharepoint.py

#!/usr/bin/env python3
"""
Post-merge hook: quando alguém faz merge de PR que muda .claude/agents/*.md,
sincroniza automaticamente para SharePoint SKILL.md
"""

import os
from pathlib import Path
from microsoft365.graph_client import GraphClient

AGENTS_DIR = Path('.claude/agents')
SP_BASE_PATH = '04_IA/Manta-Maestro/01-agentes-fundamentais'

def sync_agents_to_sharepoint():
    graph = GraphClient(
        tenant_id=os.environ['AZURE_TENANT_ID'],
        client_id=os.environ['AZURE_CLIENT_ID'],
        client_secret=os.environ['AZURE_CLIENT_SECRET']
    )
    
    for agent_file in AGENTS_DIR.glob('*.md'):
        agent_name = agent_file.stem  # agente-portos
        
        # Read from git
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Converter frontmatter YAML → Markdown
        skill_md = convert_to_skill_md(content)
        
        # Upload para SharePoint
        sp_path = f'{SP_BASE_PATH}/{agent_name}/SKILL.md'
        graph.upload_file(
            site_url='https://mnassociados.sharepoint.com/sites/Engenharia',
            drive_name='Documentos Compartilhados',
            file_path=sp_path,
            file_content=skill_md.encode('utf-8')
        )
        
        print(f"✅ Synced {agent_name} → SharePoint")

if __name__ == '__main__':
    sync_agents_to_sharepoint()
```

**Deploy como GitHub Action**:
```yaml
# Arquivo novo: .github/workflows/sync-agents.yml

name: Sync Agents to SharePoint

on:
  push:
    branches: [main]
    paths: ['.claude/agents/*.md']

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: pip install microsoft365-python graph-api
      
      - name: Sync agents to SharePoint
        run: python .claude/hooks/sync-agents-to-sharepoint.py
        env:
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
```

**Responsável**: DevOps  
**Tempo**: 3 dias (setup + testes + deploy)

**Ganho**: Sincronismo garantido, sem erro manual

---

### Sprint 6.2: Prompt Caching (2 dias)

**Objetivo**: Cache CLAUDE.md master em todas as sessões (poupança de tokens + latência).

```python
# Arquivo novo: .claude/prompts/system-maestro-cached.md

# Este arquivo é CACHEADO em todas as sessões do Maestro
# Economiza ~5000 tokens × 100 sessões/dia = 500k tokens

---
# MAESTRO v4.2 — SYSTEM PROMPT CACHED

Você é o Maestro (Manta 00), o router central do Manta Associados IA.

## 20 Agentes sob sua coordenação:

### Horizontais (11)
- Manta 00: maestro (você)
- Manta 01: claims (jurisprudência)
- Manta 02: contratual (contratos)
- Manta 04: imobiliario
- Manta 05: orcamento
- Manta 06: modelagem
- Manta 07: cronograma
- Manta 13: bd (business dev)
- Manta 14: apresentacoes
- Manta 15: advisory
- Manta 16: arquiteto-ia

### Verticais (9)
- S1: rodovias
- S2: OAE (pontes)
- S3: ferrovia
- S4: metrô
- S6: portos
- S7: aeroportos
- S8: saneamento (AySA priority)
- S9: energia (ANEEL priority)
- S10: barragens

[... REST OF CLAUDE.MD CONTENT ...]

---

REGRAS DE ROTEAMENTO:

IF menção a {saneamento|ETA|ETE|adutora|AySA|SNIS|Lei 14.026}
  → agente-saneamento (S8)

IF menção a {energia|LT|transmissão|ANEEL|ONS|EPE}
  → agente-energia (S9)

[... REST OF ROUTING RULES ...]
```

**Deploy**:
```bash
# Integrar com API do Claude para enabler prompt caching
# (exato procedimento depende da versão da API)

# Em Agent calls:
const response = await agent(prompt, {
  systemPrompt: CACHED_MAESTRO_PROMPT,  # ← é cacheado automaticamente
  cacheControl: 'ephemeral'
})

# Resultado: -90% de tokens no system prompt após 1ª requisição
```

**Responsável**: Manta 16 + DevOps  
**Tempo**: 2 dias

**Ganho**: -50% de custo, -200ms de latência

---

### Sprint 6.3: Monitoring Dashboard (2-3 dias)

**Objetivo**: Artifact com visibilidade em tempo real de agentes e routing.

```html
<!-- Arquivo novo: .claude/artifacts/maestro-dashboard.html -->

<!DOCTYPE html>
<html>
<head>
  <title>Maestro Routing Dashboard</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #1a1a1a;
      color: #eee;
      padding: 20px;
    }
    
    .container { max-width: 1200px; margin: 0 auto; }
    
    h1 { color: #4a9eff; margin-bottom: 30px; }
    
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-bottom: 30px;
    }
    
    .stat-card {
      background: #2a2a2a;
      padding: 20px;
      border-radius: 8px;
      border-left: 4px solid #4a9eff;
    }
    
    .stat-card h3 { margin: 0 0 10px 0; color: #4a9eff; }
    .stat-card .value { font-size: 32px; font-weight: bold; }
    .stat-card .label { font-size: 12px; color: #999; margin-top: 5px; }
    
    .routing-log {
      background: #2a2a2a;
      padding: 20px;
      border-radius: 8px;
      max-height: 400px;
      overflow-y: auto;
    }
    
    .log-entry {
      padding: 10px;
      margin-bottom: 10px;
      background: #1a1a1a;
      border-left: 3px solid #4a9eff;
      font-size: 12px;
    }
    
    .log-entry.success { border-left-color: #4ade80; }
    .log-entry.warning { border-left-color: #fbbf24; }
    .log-entry.error { border-left-color: #f87171; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🧙 Maestro Routing Dashboard</h1>
    
    <div class="stats">
      <div class="stat-card">
        <h3>Prompts Roteados</h3>
        <div class="value" id="total-routed">0</div>
        <div class="label">Últimas 24h</div>
      </div>
      <div class="stat-card">
        <h3>Sucesso de Routing</h3>
        <div class="value" id="success-rate">0%</div>
        <div class="label">Confiança média: <span id="avg-confidence">0%</span></div>
      </div>
      <div class="stat-card">
        <h3>Agentes Ativos</h3>
        <div class="value" id="active-agents">0</div>
        <div class="label">Em conversa agora</div>
      </div>
      <div class="stat-card">
        <h3>Ambigüidades</h3>
        <div class="value" id="ambiguities">0</div>
        <div class="label">Requer revisão</div>
      </div>
    </div>
    
    <div class="routing-log">
      <h2>Routing Log (Real-time)</h2>
      <div id="log"></div>
    </div>
  </div>
  
  <script>
    // Poll /api/maestro/stats a cada 5s
    async function updateDashboard() {
      try {
        const stats = await fetch('/api/maestro/stats').then(r => r.json())
        
        document.getElementById('total-routed').textContent = stats.total_routed
        document.getElementById('success-rate').textContent = stats.success_rate + '%'
        document.getElementById('avg-confidence').textContent = stats.avg_confidence + '%'
        document.getElementById('active-agents').textContent = stats.active_agents
        document.getElementById('ambiguities').textContent = stats.ambiguities
        
        // Update log
        const logDiv = document.getElementById('log')
        logDiv.innerHTML = stats.recent_logs
          .map(log => `<div class="log-entry ${log.status}">${log.timestamp} → ${log.prompt.substring(0, 60)}... → ${log.agent} (${log.confidence}%)</div>`)
          .join('')
      } catch (e) {
        console.error('Dashboard update failed:', e)
      }
    }
    
    // Atualizar a cada 5 segundos
    setInterval(updateDashboard, 5000)
    updateDashboard() // Initial load
  </script>
</body>
</html>
```

**Deploy como Artifact**:
```bash
# Publicar artifact com live_data capability
claude artifact publish \
  --file .claude/artifacts/maestro-dashboard.html \
  --title "Maestro Routing Dashboard" \
  --capabilities "{\"live_data\": true, \"shared_state\": true}"
```

**Responsável**: Manta 16  
**Tempo**: 2-3 dias

**Ganho**: Visibilidade operacional, debugging facilitado

---

## Semana 7-8: Validação e Otimizações Finais (4-5 dias)

### Sprint 7.1: Teste de Load + Performance (2 dias)

**Objetivo**: Validar que sistema aguenta carga real (100+ sessões simultâneas).

```bash
# Teste de load: 100 prompts simultâneos
ab -n 100 -c 10 -X POST \
   -d '{"prompt":"ETA de 50 mil hab/dia no Rio de Janeiro"}' \
   https://hub.mantaassociados.com/maestro/route

# Esperado:
# - Latência p95: <2s
# - Taxa de sucesso: >99%
# - Sucesso de routing: >90%
```

**Responsável**: QA / DevOps  
**Tempo**: 2 dias

---

### Sprint 7.2: Optimizações Finais (2-3 dias)

- Ajustar pesos de keywords baseado em logs reais
- Otimizar prompts de sistema
- Adicionar fallbacks para casos edge
- Documentar runbooks operacionais

**Responsável**: Manta 16  
**Tempo**: 2-3 dias

---

## ✅ FASE 2: CRITÉRIOS DE SUCESSO

- [x] 2 workflows multi-agente funcionando em produção
- [x] Supabase MCP integrado nos 5 agentes verticais
- [x] GitHub MCP para versionamento de decisões
- [x] Sync automático `.claude/agents/*.md` ↔ SharePoint
- [x] Prompt caching reduzindo 50% de custos
- [x] Dashboard de monitoring em tempo real
- [x] Teste de load com 100+ sessões simultâneas
- [x] Routing sucesso >90%, ambigüidades <5%
- [x] Zero erros críticos em staging

**Tempo total Fase 2**: **28-35 dias** (4-5 semanas)  
**Entregável**: Sistema completamente otimizado

---

---

## 📊 RESUMO DE INVESTIMENTO

| Fase | Duração | Investimento | ROI |
|------|---------|--------------|-----|
| **Fase 1** | 2-3 sem | 60 horas | Operacionalização |
| **Fase 2** | 4-6 sem | 100 horas | Automação + Otimização |
| **Total** | 6-8 sem | 160 horas | **+40% qualidade, -40% custo** |

---

## 🎯 DEPENDÊNCIAS CRÍTICAS

1. **Fase 1 → 2**: DEVE estar 100% completa antes de iniciar Fase 2
2. **Supabase access**: Credenciais API (Fase 1, Sprint 1.1)
3. **SharePoint access**: Graph API credentials + M365 admin approval (Fase 1, Sprint 1.2)
4. **GitHub PAT**: Personal access token com scope `repo:*`, `admin:repo_hook` (Fase 2, Sprint 5.2)
5. **Azure AD**: Tenant ID, Client ID/Secret para GitHub Actions (Fase 2, Sprint 6.1)

---

## 🚨 RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|--------|-----------|
| Credenciais Graph API não aprovadas | Média | Alto | Solicitar approval de M365 admin na semana 0 |
| Divergência schema Supabase | Baixa | Alto | Rollback automático em migration SQL |
| Prompt caching incompatível | Baixa | Médio | Testar com versão beta da API antes |
| RAG chunks com baixa qualidade | Média | Médio | Validação de relevância em Sprint 3.1 |
| Routing workflow muito lento | Média | Médio | Usar Haiku para triagem, Sonnet para validação |

---

## 📅 CRONOGRAMA RECOMENDADO

```
Semana 1  (Jul 8-12):   Fase 1.1 — Supabase
Semana 2  (Jul 15-19):  Fase 1.2 — SharePoint + MCP config
Semana 3  (Jul 22-26):  Fase 1.3 — Testes + validação
              ↓ Gate: Aprovação MN
Semana 4  (Ago 5-9):    Fase 2.1 — Workflows multi-agente
Semana 5  (Ago 12-16):  Fase 2.2 — Integrações MCP + automação
Semana 6  (Ago 19-23):  Fase 2.3 — CI/CD + monitoring
Semana 7-8 (Ago 26-30): Fase 2.4 — Testes de carga + otimizações finais
```

---

## 💾 ARQUIVOS A CRIAR/MODIFICAR

### Fase 1 (criados):
- `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql` ✅
- `scripts/load_rag_collections.py` (novo)
- `scripts/create_sp_folders.py` (novo)
- `.mcp.json` (novo)
- `.claude/settings.json` (novo)
- `.claude/hooks/validate-claude-md.sh` (novo)
- `sharepoint/01-agentes-fundamentais/*/SKILL.md` (5× editados)

### Fase 2 (criados):
- `.claude/workflows/maestro-routing-validator.js` (novo)
- `.claude/workflows/design-alternatives-generator.js` (novo)
- `.claude/hooks/sync-agents-to-sharepoint.py` (novo)
- `.github/workflows/sync-agents.yml` (novo)
- `.claude/artifacts/maestro-dashboard.html` (novo)
- `.claude/prompts/system-maestro-cached.md` (novo)
- Múltiplos `.md` de documentação + runbooks

---

## ✅ PRÓXIMOS PASSOS

1. **Aprovação de MN** — Apresentar este plano a Mauricio Neves
2. **Agendar kickoff** — Semana de 8 de julho
3. **Preparar credenciais** — Supabase, SharePoint (Graph API), GitHub, Azure AD
4. **Criar backlog** — Tasks no JIRA/Azure DevOps para cada sprint
5. **Designar owners** — Por sprint e por entregável

**Status**: 🔴 Não iniciado (aguardando aprovação MN)

