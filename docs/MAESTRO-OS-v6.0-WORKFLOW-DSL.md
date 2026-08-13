# Maestro OS v6.0 — Workflow DSL Specification

**Versão:** 0.1 (draft)  
**Data:** 2026-07-26  
**Objetivo:** Linguagem de scripting para orquestração de 8 agentes em paralelo com consenso 3/5

---

## 1. Conceitos Principais

### 1.1 Primitivas

```
project        → objeto raiz; contém metadados (tipo, sítio, escopo)
agents         → array de {name, tier, tools, rag_prefix}
parallel()     → fan-out: invoca N agentes simultaneamente
consensus()    → votação: requer 3/5 concordarem sobre decisão
fallback()     → escalate: se consensus falhar, envia para humano
wait()         → barrier: aguarda todos agentes; síncrone
aggregate()    → combina outputs em artefato (DOCX, JSON, Matrix)
```

### 1.2 Tipos de Dado

```typescript
Project = {
  id: string,               // UUID
  type: string,             // "porto", "barragem", "energia"
  title: string,
  location: string,
  budget_range: string,     // "0-50M" | "50-250M" | "250M+"
  created_at: timestamp,
  created_by: string        // email
}

Decision = {
  decision_id: string,
  project_id: string,
  aspect: string,           // "orçamento", "cronograma", "risco"
  candidates: [              // propostas de cada agente
    { agent: string, value: any, confidence: 0..1 }
  ],
  consensus_result: any,    // decisão final após votação
  consensus_threshold: 3,   // 3/5
  timestamp: timestamp,
  trace: string             // audit trail (qual agente votou o quê)
}
```

---

## 2. Sintaxe DSL

### 2.1 Declaração de Projeto

```yaml
project:
  id: proj-2026-07-26-001
  type: porto
  title: "Terminal Container Paranaguá"
  location: "Paraná, BR"
  budget_range: "250M+"

agents:
  - name: agente-portos
    tier: sonnet
    rag_prefix: por:
  - name: agente-energia
    tier: sonnet
    rag_prefix: ene:
  - name: agente-saneamento
    tier: sonnet
    rag_prefix: san:
```

### 2.2 Fan-out Paralelo

```yaml
# Invoca 3 agentes em paralelo
execute_parallel:
  agents: [agente-portos, agente-energia, agente-saneamento]
  context:
    shared_docs: [projeto_basico.pdf, estudo_previo.md]
    deadline: "2026-08-15"
  
  # Cada agente recebe prompts customizados
  prompts:
    agente-portos:
      template: "SKILL-S7-portos.md"
      focus: [orçamento, cronograma, riscos-dragagem]
    agente-energia:
      template: "SKILL-S10-energia.md"
      focus: [orçamento, cronograma, subestação]
    agente-saneamento:
      template: "SKILL-S9-saneamento.md"
      focus: [orçamento, cronograma, ETA/ETE]
  
  # Timeout por agente
  timeout_per_agent: "45min"
  
  # Armazenar intermediários
  store_outputs: true
```

### 2.3 Consenso 3/5

```yaml
# Após fan-out, agrega respostas e vota
consensus:
  aspect: "orçamento"
  candidates:  # outputs dos agentes
    - agent: agente-portos
      value: 500_000_000  # R$ 500M
      confidence: 0.85
    - agent: agente-energia
      value: 450_000_000  # R$ 450M
      confidence: 0.78
    - agent: agente-saneamento
      value: 200_000_000  # R$ 200M
      confidence: 0.92
  
  # Votação: qual hipótese é mais realista?
  voting_rule: "super_majority"  # requer 3/5
  voting_dimension: "cost_realism"
  
  # Se consensus falha
  fallback:
    action: "escalate"
    to: "mneves@mantaassociados.com"
    message: "Orçamento divergente; solicita humano para arbitrar"
```

### 2.4 Aggregação & Output

```yaml
aggregate:
  format: "docx"
  template: "artefato-maestro-v6.0.docx"
  sections:
    - title: "Escopo"
      source: project.description
    - title: "Orçamento Consolidado"
      source: consensus.orçamento
      format: "table"
    - title: "Cronograma Integrado"
      source: consensus.cronograma
      format: "gantt"
    - title: "Matriz de Interdependências"
      source: computed.interdependencies
      format: "json"
    - title: "Riscos Cross-Segmento"
      source: computed.risks
      format: "table"
  
  output_path: "s3://manta-maestro/projects/{project_id}/consolidated.docx"
  
  # Também gerar JSON estruturado para API
  also_output: "json"
```

---

## 3. Exemplo Completo: Porto + Energia + Saneamento

```yaml
# MAESTRO-OS-WORKFLOW-porto-energia-saneamento.yaml

project:
  id: proj-2026-07-paranagua
  type: "multi_segment"
  segments: [portos, energia, saneamento]
  title: "Terminal Container Paranaguá + Geração + ETA/ETE"
  location: "Paraná, BR"
  budget_range: "250M+"

# ===== FASE 1: FAN-OUT PARALELO (t=0–40min) =====

phase_1_parallel:
  stage: "fan_out"
  agents:
    - agente-portos
    - agente-energia
    - agente-saneamento
  
  shared_context:
    project_id: "proj-2026-07-paranagua"
    docs:
      - "estudo_previo_completo.pdf"
      - "mapa_topografico.dwg"
      - "sondagens_geotecnicas.xlsx"
    environment:
      locality: "Paranaguá"
      climate: "tropical"
      seasonal_factors: "cheias_verao"
  
  prompts:
    agente-portos: |
      Projeto: Terminal Container Paranaguá
      Foco: infraestrutura portuária (cais, dragagem, área retro)
      Prepare: orçamento, cronograma, riscos dragagem em site sensível
      Horizon: 48 meses
    
    agente-energia: |
      Projeto: SE Paranaguá 230kV (suprimento terminal)
      Foco: subestação, LT de conexão, geração backup
      Prepare: orçamento, cronograma, estudo fluxo potência
      Horizon: 48 meses
    
    agente-saneamento: |
      Projeto: ETA/ETE Paranaguá (abastecimento + esgoto terminal)
      Foco: captação, adução, ETA, ETE, reúso
      Prepare: orçamento, cronograma, licenças CETESB
      Horizon: 48 meses
  
  timeout: "45min"
  store_outputs: true

# ===== FASE 2: CONSENSO 3/5 (t=40–42min) =====

phase_2_consensus:
  stage: "voting"
  
  # Aspecto 1: Orçamento Total
  decision_1:
    aspect: "orçamento"
    dimension: "cost_realism"
    
    candidates:
      - agent: agente-portos
        estimate: 500_000_000
        confidence: 0.85
        reasoning: "Cais novo 1.2km, dragagem estrita (site sensível), equipamentos"
      
      - agent: agente-energia
        estimate: 450_000_000
        confidence: 0.78
        reasoning: "SE 230kV (equipamentos caros), LT 120km, fundações solo marinho"
      
      - agent: agente-saneamento
        estimate: 200_000_000
        confidence: 0.92
        reasoning: "ETA/ETE modular, tecnologia provada, regiões não críticas"
    
    voting_rule: "super_majority"
    threshold: 3  # requer 3/5 concordarem
    
    consensus_prompt: |
      Analise 3 estimativas de orçamento:
      - S7 (Portos): R$ 500M (confiança 0.85)
      - S10 (Energia): R$ 450M (confiança 0.78)
      - S9 (Saneamento): R$ 200M (confiança 0.92)
      
      Qual é mais realista considerando:
      1. Histórico de projetos similares em SICRO/BDI
      2. Risco geológico (solo marinho)
      3. Encargos sociais (região com movimento sindical ativo)
      4. Contingência (30% para obras portuárias)
      
      Vote: qual estimativa adota? (1=Portos, 2=Energia, 3=Saneamento)
    
    fallback:
      if_consensus_fails: "escalate"
      to: "mneves@mantaassociados.com"
      message: "3 estimativas divergem; solicita arbitragem (revisar SICRO/BDI regional)"
  
  # Aspecto 2: Cronograma Crítico
  decision_2:
    aspect: "cronograma"
    dimension: "critical_path"
    
    candidates:
      - agent: agente-portos
        estimate_months: 54
        critical_activities: [dragagem, cais, equipamentos]
      
      - agent: agente-energia
        estimate_months: 48
        critical_activities: [fundações, SE montagem, testes]
      
      - agent: agente-saneamento
        estimate_months: 42
        critical_activities: [ETA, ETE, reúso]
    
    voting_rule: "super_majority"
    consensus_prompt: |
      Qual cronograma total é realista para integração?
      - Se S7 atrasa, S10/S9 esperam (risco produção)
      - Se S10 atrasa, S7 não opera (sem energia)
      - Qual caminho crítico?
    
    fallback: "escalate"

# ===== FASE 3: AGREGAÇÃO (t=42–44min) =====

phase_3_aggregate:
  stage: "consolidation"
  
  format: "docx"
  template: "artefato-maestro-v6.0-multi.docx"
  
  sections:
    - title: "Escopo Integrado"
      content: |
        Terminal Container (S7) + Subestação (S10) + ETA/ETE (S9)
        Paranaguá, PR | 48–54 meses | R$ 1.0–1.2B
    
    - title: "Orçamento Consolidado"
      table:
        - "Segmento": "Portos (S7)"
          "Orçamento": "R$ 500M"
          "BDI": "SICRO regional"
        - "Segmento": "Energia (S10)"
          "Orçamento": "R$ 450M"
          "BDI": "ANEEL equipamentos"
        - "Segmento": "Saneamento (S9)"
          "Orçamento": "R$ 200M"
          "BDI": "Lei 14.026 markup"
        - "Total": "R$ 1.15B (± 8%)"
    
    - title: "Cronograma Integrado"
      gantt:
        - activity: "Dragagem"
          start: 0
          duration: 18
          owner: "S7"
        - activity: "Cais"
          start: 12
          duration: 24
          owner: "S7"
        - activity: "Fundações SE"
          start: 6
          duration: 12
          owner: "S10"
        - activity: "ETA/ETE"
          start: 12
          duration: 24
          owner: "S9"
        - activity: "Comissionamento"
          start: 42
          duration: 6
          owner: "All"
    
    - title: "Matriz de Interdependências"
      dependencies:
        - "S7 (dragagem) → S10 (fundações): aguarda conclusão dragagem"
        - "S10 (SE) → S7 (operação): terminal não opera sem energia"
        - "S9 (ETA) → S7 (abastecimento): dragagem deve respeitar tomada d'água"
    
    - title: "Riscos Cross-Segmento"
      risks:
        - risk: "Atraso dragagem → cascata para S10 + S9"
          probability: "medium"
          mitigation: "iniciar fundações antes dragagem conclusão"
        - risk: "Solo marinho pior que previsto → custo adicional"
          probability: "high"
          mitigation: "mais sondagens (BPT/CPT); contingência 30%"
  
  output:
    path: "s3://manta-maestro/projects/proj-2026-07-paranagua/consolidated.docx"
    also_json: true
    
  # Guardar na Supabase
  save_decision_trail: true
  project_id: "proj-2026-07-paranagua"

# ===== SAÍDAS ESPERADAS (t=44min) =====

expected_outputs:
  - filename: "consolidated.docx"
    size: "~15 pages"
    sections: 8
  
  - filename: "consolidated.json"
    schema:
      project_id: string
      budget_consolidated: number
      cronogram_critical_path: number
      risks: array
      interdependencies: array
      decision_trail: array
  
  - supabase_records:
    - table: "projects"
      updates: {status: "consensus_complete", consolidated_budget: "1.15B"}
    
    - table: "decisions"
      inserts:
        - {aspect: "orçamento", consensus_result: "R$ 1.15B", votes: [S7, S10, S9]}
        - {aspect: "cronograma", consensus_result: "54 months", votes: [S7, S10, S9]}

execution_time:
  fan_out: "40 min"
  consensus: "2 min"
  aggregate: "2 min"
  total: "44 min"
  saved: "105 - 44 = 61 min (-58%)"
```

---

## 4. Implementação: Parser + Executor

O Workflow DSL será:
1. **Parsed** em TypeScript/Python → AST
2. **Validado** contra schema (tipos, agentes válidos, etc.)
3. **Executado** por orchestrator (spawns agentes, aguarda, consenso, agrega)

### 4.1 Parser (TypeScript)

```typescript
interface WorkflowDSL {
  project: Project;
  agents: AgentDeclaration[];
  phase_1_parallel?: ParallelPhase;
  phase_2_consensus?: ConsensusPhase;
  phase_3_aggregate?: AggregatePhase;
}

class WorkflowParser {
  parse(yaml_content: string): WorkflowDSL {
    // YAML → TypeScript object
  }
  
  validate(workflow: WorkflowDSL): ValidationResult {
    // Verifica: agentes existem, prompts válidos, etc.
  }
}
```

### 4.2 Executor (Python + Claude API)

```python
class MaestroOrchestrator:
  def fan_out(self, agents: List[str], context: Dict) -> Dict[str, str]:
    """Invoca N agentes em paralelo via asyncio"""
  
  def consensus_vote(self, aspect: str, candidates: List[Candidate]) -> Decision:
    """Coleta votos (3/5) sobre decisão"""
  
  def aggregate(self, outputs: Dict, template: str) -> Artifact:
    """Gera DOCX consolidado"""
  
  def execute(self, workflow_yaml: str) -> Project:
    """Executa workflow end-to-end"""
```

---

## 5. Próximos Passos

- [ ] Finalizar sintaxe DSL (feedback)
- [ ] Implementar Parser (TypeScript)
- [ ] Implementar Executor (Python asyncio)
- [ ] Integração com Supabase (project + decisions tables)
- [ ] Teste com 10 workflows reais
- [ ] Documentação de usuário

---

*Especificação Maestro OS v6.0 Workflow DSL — v0.1 (draft)*
