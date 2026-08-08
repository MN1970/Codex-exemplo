# Phase 2: Maestro Router Implementation (Manta 00)

**Version:** 2.0 | **Date:** 2026-08-08  
**Scope:** Router decision tree, adaptive model selection, priority queue dispatcher

---

## 1. ROUTING DECISION TREE

### 1.1 Router.dispatch(prompt) Pseudocode

```javascript
class MaestroRouter {
  
  dispatch(userPrompt, context = {}) {
    /**
     * Main entry point for Maestro (Manta 00).
     * Routes incoming task to correct vertical agent(s) + model(s).
     * 
     * Returns: RoutingDecision {
     *   agents: [agentId, ...],
     *   models: [modelName, ...],
     *   priority: 'Q0'|'Q16'|'Q∞',
     *   pattern: 'direct'|'pipeline'|'parallel'|'fan-out',
     *   metadata: { tokenCount, complexity, phase, segment }
     * }
     */

    const tokenCount = estimateTokens(userPrompt + context);
    const keywords = extractKeywords(userPrompt);
    const complexity = detectComplexity(keywords);
    const phase = detectLifecyclePhase(userPrompt);
    
    // STEP 1: Detect priority queue
    const priority = determinePriority(keywords, context);
    
    // STEP 2: Route to segment(s)
    const segment = routeToSegment(keywords);
    
    // STEP 3: Adaptive model selection
    const { primaryModel, secondaryModel } = selectModels(
      tokenCount, 
      complexity, 
      segment
    );
    
    // STEP 4: Determine orchestration pattern
    const pattern = selectPattern(tokenCount, complexity);
    
    // STEP 5: Build agent roster
    const agents = buildAgentRoster(segment, complexity, phase, pattern);
    
    // STEP 6: Construct routing decision
    const decision = {
      agents,
      models: [primaryModel, secondaryModel],
      priority,
      pattern,
      metadata: {
        tokenCount,
        complexity,
        phase,
        segment,
        keywords: keywords.slice(0, 5)
      }
    };
    
    // STEP 7: Log to RAG learning log
    this.logToRagLearning({
      timestamp: now(),
      prompt: userPrompt.slice(0, 100),
      decision,
      status: 'ROUTING_COMPLETE'
    });
    
    return decision;
  }

  // ─────────────────────────────────────────────────────────────────
  // PRIORITY DETECTION
  // ─────────────────────────────────────────────────────────────────
  
  determinePriority(keywords, context) {
    /**
     * Q0: CRITICAL — reequilíbrio (claim), M&A, due diligence, immediate escalation
     * Q16: NORMAL — standard routing (default)
     * Q∞: BACKGROUND — learning, RAG indexing, async tasks
     */
    
    const criticalKeywords = [
      'reequilíbrio', 'claim', 'due diligence', 'M&A', 'aquisição',
      'URGENTE', 'CRÍTICO', 'escalação', 'mediação'
    ];
    
    const backgroundKeywords = [
      'indexar', 'RAG', 'aprender', 'background', 'async', 'batch'
    ];
    
    if (hasCriticalKeyword(keywords, criticalKeywords)) {
      return 'Q0';  // Critical queue
    }
    
    if (hasBackgroundKeyword(keywords, backgroundKeywords)) {
      return 'Q∞';  // Background queue
    }
    
    return 'Q16';  // Normal queue (default)
  }

  // ─────────────────────────────────────────────────────────────────
  // SEGMENT ROUTING (10 segments: 8 horizontal + 2 vertical)
  // ─────────────────────────────────────────────────────────────────
  
  routeToSegment(keywords) {
    /**
     * Returns: {
     *   primarySegment: 'S1'|'S2'|...|'S10'|'horizontal',
     *   secondarySegments: [S_i, ...],
     *   confidence: 0.0–1.0
     * }
     */

    const keywordMap = {
      'S8-saneamento': {
        regex: /saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem\s+urbana|SNIS|ABES|concessionária\s+água/i,
        agent: 'agente-saneamento',
        confidence: 0.95
      },
      'S9-energia': {
        regex: /transmissão|LT|subestação|ANEEL|RAP|leilão\s+transmissão|ONS|EPE|CCE|distribuidora/i,
        agent: 'agente-energia',
        confidence: 0.95
      },
      'S6-portos': {
        regex: /porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel|navegação/i,
        agent: 'agente-portos',
        confidence: 0.95
      },
      'S7-aeroportos': {
        regex: /aeroporto|pista\s+pouso|ANAC|ICAO|TPS|TECA|balizamento|CNT/i,
        agent: 'agente-aeroportos',
        confidence: 0.95
      },
      'S10-barragens': {
        regex: /barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF|hidrelétrica\s+barragem/i,
        agent: 'agente-barragens',
        confidence: 0.95
      },
      'S1-rodovias': {
        regex: /rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT|concessão\s+rodovia/i,
        agent: 'agente-infraestrutura-S1',
        confidence: 0.90
      },
      'S2-oae': {
        regex: /ponte|viaduto|OAE|NBR\s+7187|túnel\s+rodoviário|fundação\s+profunda/i,
        agent: 'agente-infraestrutura-S2',
        confidence: 0.90
      },
      'S3-ferrovia': {
        regex: /ferrovia|trilho|AMV|dormente|via\s+permanente|via\s+férrea/i,
        agent: 'agente-infraestrutura-S3',
        confidence: 0.90
      },
      'S4-metro': {
        regex: /metrô|estação|NATM|PSD|linha\s+[0-9]|VLT|monotrilho/i,
        agent: 'agente-infraestrutura-S4',
        confidence: 0.90
      }
    };

    const matches = [];
    
    for (const [segment, rule] of Object.entries(keywordMap)) {
      if (rule.regex.test(keywords.join(' '))) {
        matches.push({
          segment,
          agent: rule.agent,
          confidence: rule.confidence
        });
      }
    }
    
    if (matches.length === 0) {
      // Fallback to horizontal agents (Manta 01–07, 13–16)
      return {
        primarySegment: 'horizontal',
        secondarySegments: [],
        confidence: 0.3,
        agentId: 'manta-00-fallback'
      };
    }
    
    // Sort by confidence, return primary + secondary
    matches.sort((a, b) => b.confidence - a.confidence);
    
    return {
      primarySegment: matches[0].segment,
      agent: matches[0].agent,
      secondarySegments: matches.slice(1).map(m => m.segment),
      confidence: matches[0].confidence
    };
  }

  // ─────────────────────────────────────────────────────────────────
  // LIFECYCLE PHASE DETECTION
  // ─────────────────────────────────────────────────────────────────
  
  detectLifecyclePhase(prompt) {
    /**
     * Returns: 'EVTE'|'BASICO'|'EXECUTIVO'|'EXECUCAO'|'OPERACAO'|
     *          'LICITACAO'|'DUE_DILIGENCE'|'ENCERRAMENTO'
     */
    
    const phaseMap = {
      'EVTE': /estudo\s+prévio|EVTE|avaliabilidade|pré-viabilidade/i,
      'BASICO': /projeto\s+básico|PB[^A-Z]|arquitetura|conceitual/i,
      'EXECUTIVO': /projeto\s+executivo|PE[^A-Z]|detalhado|constructivo/i,
      'EXECUCAO': /obra\s+em\s+execução|em\s+execução|andamento|canteiro|frente\s+obra/i,
      'OPERACAO': /operação|manutenção|O&M|mantença|exploração/i,
      'LICITACAO': /licitação|edital|concorrência|chamada\s+pública|processo\s+competitivo/i,
      'DUE_DILIGENCE': /due\s+diligence|M&A|aquisição|diligência|acquisition/i,
      'ENCERRAMENTO': /encerramento|descomissionamento|demolição|abandono|enclosure/i
    };
    
    for (const [phase, regex] of Object.entries(phaseMap)) {
      if (regex.test(prompt)) return phase;
    }
    
    return 'GENERIC';
  }

  // ─────────────────────────────────────────────────────────────────
  // PATTERN SELECTION
  // ─────────────────────────────────────────────────────────────────
  
  selectPattern(tokenCount, complexity) {
    /**
     * Returns: 'direct'|'pipeline'|'parallel'|'fan-out'
     * 
     * direct:    1 agent, synchronous, <2 min
     * pipeline:  3–4 agents in sequence, 5–30 min
     * parallel:  8 agents in parallel, with barrier, 10–20 min
     * fan-out:   16+ agents, no barrier, 30 min–2h
     */
    
    if (tokenCount < 500) {
      return complexity < 'media' ? 'direct' : 'direct';
    }
    
    if (tokenCount < 2000) {
      return 'pipeline';
    }
    
    if (tokenCount < 5000) {
      return 'parallel';
    }
    
    return 'fan-out';
  }

  // ─────────────────────────────────────────────────────────────────
  // AGENT ROSTER BUILDER
  // ─────────────────────────────────────────────────────────────────
  
  buildAgentRoster(segment, complexity, phase, pattern) {
    /**
     * Builds the list of agents to execute based on:
     * - Primary segment (S1–S10 or horizontal)
     * - Task complexity (baixa|media|alta|critica)
     * - Lifecycle phase (EVTE|BASICO|EXECUTIVO|...)
     * - Orchestration pattern (direct|pipeline|parallel|fan-out)
     */

    const coreHorizontalAgents = {
      'baixa': ['Manta 00'], // just router
      'media': ['Manta 00', 'Manta 05', 'Manta 07'], // budget + schedule
      'alta': ['Manta 00', 'Manta 02', 'Manta 05', 'Manta 07', 'Manta 15'], // contracts + budget + schedule + advisory
      'critica': ['Manta 00', 'Manta 01', 'Manta 02', 'Manta 05', 'Manta 06', 'Manta 15', 'Manta 16'] // claims + contracts + budget + modeling + advisory + architect
    };

    const phaseAgentMap = {
      'EVTE': ['Manta 05', 'Manta 07', 'Manta 15'], // budget + schedule + advisory
      'BASICO': ['Manta 05', 'Manta 06', 'Manta 07'], // budget + modeling + schedule
      'EXECUTIVO': ['Manta 05', 'Manta 06', 'Manta 07'], // budget + modeling + schedule
      'EXECUCAO': ['Manta 07', 'Manta 01', 'Manta 02'], // schedule + claims + contracts
      'OPERACAO': ['Manta 02', 'Manta 07'], // contracts + schedule
      'LICITACAO': ['Manta 02', 'Manta 15', 'Manta 13'], // contracts + advisory + business-dev
      'DUE_DILIGENCE': ['Manta 01', 'Manta 15', 'Manta 16'], // claims + advisory + architect
      'ENCERRAMENTO': ['Manta 02', 'Manta 07'] // contracts + schedule
    };

    let roster = [];
    
    // Add vertical segment agent
    const verticalAgents = {
      'S1': 'agente-infraestrutura-S1',
      'S2': 'agente-infraestrutura-S2',
      'S3': 'agente-infraestrutura-S3',
      'S4': 'agente-infraestrutura-S4',
      'S6': 'agente-portos',
      'S7': 'agente-aeroportos',
      'S8': 'agente-saneamento',
      'S9': 'agente-energia',
      'S10': 'agente-barragens'
    };
    
    if (segment && segment !== 'horizontal') {
      roster.push(verticalAgents[segment] || 'agente-generico');
    }
    
    // Add horizontal agents by complexity
    const horizontalList = coreHorizontalAgents[complexity] || coreHorizontalAgents['media'];
    roster.push(...horizontalList);
    
    // Add phase-specific agents
    if (phase !== 'GENERIC') {
      roster.push(...(phaseAgentMap[phase] || []));
    }
    
    // Deduplicate and filter by pattern
    roster = [...new Set(roster)];
    
    if (pattern === 'direct' && roster.length > 1) {
      roster = roster.slice(0, 1);
    } else if (pattern === 'pipeline' && roster.length > 4) {
      roster = roster.slice(0, 4);
    } else if (pattern === 'parallel' && roster.length > 8) {
      roster = roster.slice(0, 8);
    }
    // fan-out: no limit
    
    return roster;
  }

  // ─────────────────────────────────────────────────────────────────
  // HELPER METHODS
  // ─────────────────────────────────────────────────────────────────
  
  estimateTokens(text) {
    // Rough rule: ~4 chars per token
    return Math.ceil(text.length / 4);
  }
  
  extractKeywords(text) {
    // Split on whitespace, remove stop words, lowercase
    const stopWords = new Set([
      'o', 'a', 'que', 'do', 'da', 'e', 'é', 'de', 'em', 'um', 'para',
      'the', 'a', 'an', 'and', 'or', 'is', 'in', 'to', 'of', 'with'
    ]);
    
    return text
      .toLowerCase()
      .split(/\s+/)
      .filter(w => w.length > 3 && !stopWords.has(w));
  }
  
  detectComplexity(keywords) {
    /**
     * Returns: 'baixa'|'media'|'alta'|'critica'
     */
    
    const complexityMap = {
      'critica': ['claim', 'reequilíbrio', 'M&A', 'due diligence', 'litigação'],
      'alta': ['edital', 'concessão', 'PPP', 'licitação', 'multicritério'],
      'media': ['projeto', 'orçamento', 'cronograma', 'análise'],
      'baixa': ['consulta', 'informação', 'verificação']
    };
    
    for (const [level, keywords_list] of Object.entries(complexityMap)) {
      if (keywords.some(k => keywords_list.some(cw => k.includes(cw)))) {
        return level;
      }
    }
    
    return 'media';
  }
  
  hasCriticalKeyword(keywords, criticalKeywords) {
    return keywords.some(k => 
      criticalKeywords.some(cw => k.includes(cw.toLowerCase()))
    );
  }
  
  hasBackgroundKeyword(keywords, backgroundKeywords) {
    return keywords.some(k =>
      backgroundKeywords.some(bw => k.includes(bw.toLowerCase()))
    );
  }
  
  logToRagLearning(data) {
    // TODO: Implement logging to Supabase RAG learning table
    console.log('[RAG_LEARNING]', JSON.stringify(data));
  }
}
```

---

## 2. ADAPTIVE MODEL SELECTION

### 2.1 Model Selection Algorithm

```javascript
class AdaptiveModelSelector {
  
  selectModels(tokenCount, complexity, segment) {
    /**
     * Returns: {
     *   primaryModel: 'haiku'|'sonnet'|'opus',
     *   secondaryModel: 'haiku'|'sonnet'|'opus'|null,
     *   reasoning: string
     * }
     * 
     * Decision matrix from CLAUDE.md § Matriz de Seleção de Modelo
     */
    
    // STEP 1: Classify volume band
    const band = this.classifyVolumeBand(tokenCount);
    
    // STEP 2: Classify complexity
    const complexityLevel = this.classifyComplexity(complexity);
    
    // STEP 3: Look up decision matrix
    const decision = this.modelSelectionMatrix[band][complexityLevel];
    
    // STEP 4: Override for critical paths
    if (complexity === 'critica') {
      return {
        primaryModel: 'opus',
        secondaryModel: 'sonnet',
        reasoning: 'Critical complexity detected (claim/M&A/due diligence) → Opus primary + Sonnet ensemble'
      };
    }
    
    // STEP 5: Override for large volume
    if (band === 'extra-grande') {
      return {
        primaryModel: 'sonnet',
        secondaryModel: 'haiku',
        reasoning: `Extra-large volume (${tokenCount} tokens) → Sonnet analysis + Haiku parallelization`
      };
    }
    
    return {
      primaryModel: decision.primary,
      secondaryModel: decision.secondary,
      reasoning: `Band: ${band}, Complexity: ${complexityLevel} → ${decision.primary}${decision.secondary ? ' + ' + decision.secondary : ''}`
    };
  }

  classifyVolumeBand(tokenCount) {
    /**
     * Pequeño: 0–500 tokens
     * Médio: 500–2000 tokens
     * Grande: 2000–5000 tokens
     * Extra-grande: 5000+ tokens
     */
    
    if (tokenCount < 500) return 'pequeno';
    if (tokenCount < 2000) return 'medio';
    if (tokenCount < 5000) return 'grande';
    return 'extra-grande';
  }

  classifyComplexity(complexity) {
    const map = {
      'baixa': 'low',
      'media': 'medium',
      'alta': 'high',
      'critica': 'critical'
    };
    return map[complexity] || 'medium';
  }

  // Decision matrix from CLAUDE.md
  modelSelectionMatrix = {
    'pequeno': {
      'low': { primary: 'haiku', secondary: null },
      'medium': { primary: 'sonnet', secondary: null },
      'high': { primary: 'sonnet', secondary: null },
      'critical': { primary: 'opus', secondary: 'sonnet' }
    },
    'medio': {
      'low': { primary: 'haiku', secondary: 'haiku' },
      'medium': { primary: 'sonnet', secondary: 'haiku' },
      'high': { primary: 'sonnet', secondary: 'sonnet' },
      'critical': { primary: 'opus', secondary: 'sonnet' }
    },
    'grande': {
      'low': { primary: 'sonnet', secondary: 'haiku' },
      'medium': { primary: 'sonnet', secondary: 'haiku' },
      'high': { primary: 'sonnet', secondary: 'haiku' },
      'critical': { primary: 'opus', secondary: 'sonnet' }
    },
    'extra-grande': {
      'low': { primary: 'sonnet', secondary: 'haiku' },
      'medium': { primary: 'sonnet', secondary: 'haiku' },
      'high': { primary: 'sonnet', secondary: 'haiku' },
      'critical': { primary: 'opus', secondary: 'sonnet' }
    }
  };
}
```

---

## 3. PRIORITY QUEUE DISPATCHER

### 3.1 QPrio Queue Implementation

```javascript
class QPrioDispatcher {
  
  constructor(agentPool) {
    /**
     * agentPool: { agentId: AgentInstance, ... }
     * 
     * Three priority queues:
     * Q0: Critical (immediate execution)
     * Q16: Normal (standard scheduling)
     * Q∞: Background (async, low priority)
     */
    this.agentPool = agentPool;
    this.queues = {
      'Q0': [],      // Critical: median wait ~5 sec
      'Q16': [],     // Normal: median wait ~30–60 sec
      'Q∞': []       // Background: median wait unbounded
    };
    this.isRunning = false;
  }

  enqueue(task, routing) {
    /**
     * task: {
     *   id: string,
     *   prompt: string,
     *   context: object,
     *   timestamp: number
     * }
     * 
     * routing: output from MaestroRouter.dispatch()
     */
    
    const queuedTask = {
      ...task,
      routing,
      priority: routing.priority,
      enqueuedAt: Date.now(),
      status: 'QUEUED'
    };
    
    this.queues[routing.priority].push(queuedTask);
    
    console.log(`[QPrio] Task ${task.id} → ${routing.priority} queue (total: ${this.queues[routing.priority].length})`);
    
    return queuedTask;
  }

  async start() {
    /**
     * Main dispatcher loop.
     * Continuously pulls tasks from queues and dispatches to agents.
     * 
     * Priority order: Q0 (stop-the-world) → Q16 (normal) → Q∞ (background)
     */
    
    this.isRunning = true;
    
    while (this.isRunning) {
      // Check Q0 first (critical)
      if (this.queues['Q0'].length > 0) {
        const task = this.queues['Q0'].shift();
        await this.dispatch(task);
        continue;
      }
      
      // Check Q16 (normal)
      if (this.queues['Q16'].length > 0) {
        const task = this.queues['Q16'].shift();
        await this.dispatch(task);
        continue;
      }
      
      // Check Q∞ (background, 1 per minute)
      if (this.queues['Q∞'].length > 0 && Math.random() < 0.016) { // ~1 in 60 cycles
        const task = this.queues['Q∞'].shift();
        await this.dispatch(task);
        continue;
      }
      
      // Sleep 100ms before next cycle
      await this.sleep(100);
    }
  }

  async dispatch(task) {
    /**
     * Main dispatcher:
     * 1. Select orchestration pattern (direct|pipeline|parallel|fan-out)
     * 2. Execute agents in correct order/concurrency
     * 3. Log results to RAG learning log
     */
    
    task.status = 'EXECUTING';
    task.dispatchedAt = Date.now();
    
    const { agents, models, pattern } = task.routing;
    
    console.log(`[Dispatcher] Executing task ${task.id} via ${pattern} (agents: ${agents.join(', ')})`);
    
    let result;
    
    try {
      if (pattern === 'direct') {
        result = await this.executeDirect(task, agents, models);
      } else if (pattern === 'pipeline') {
        result = await this.executePipeline(task, agents, models);
      } else if (pattern === 'parallel') {
        result = await this.executeParallel(task, agents, models);
      } else if (pattern === 'fan-out') {
        result = await this.executeFanOut(task, agents, models);
      }
      
      task.status = 'COMPLETE';
      task.completedAt = Date.now();
      
    } catch (error) {
      task.status = 'FAILED';
      task.error = error.message;
      console.error(`[Dispatcher] Task ${task.id} failed:`, error);
    }
    
    // Log to RAG learning
    await this.logTaskExecution(task, result);
    
    return { task, result };
  }

  async executeDirect(task, agents, models) {
    /**
     * Direct: Single agent, primary model
     * Used for small, low-complexity tasks
     * 
     * Timeline: <30 seconds
     */
    
    const agent = this.agentPool[agents[0]];
    const model = models[0];
    
    if (!agent) throw new Error(`Agent ${agents[0]} not found`);
    
    const result = await agent.execute(task.prompt, {
      model,
      context: task.context
    });
    
    return { pattern: 'direct', agents: [agents[0]], result };
  }

  async executePipeline(task, agents, models) {
    /**
     * Pipeline: 3–4 agents in sequence, with data flowing through
     * Stage 1: agents[0] (analysis)
     * Stage 2: agents[1], agents[2] (synthesis in parallel)
     * Stage 3: agents[3] (assembly)
     * 
     * Timeline: 5–10 minutes
     */
    
    const stage1Input = task.prompt;
    
    // Stage 1: Analysis (primary model)
    console.log('[Pipeline] Stage 1: Analysis');
    const stage1Result = await this.agentPool[agents[0]].execute(stage1Input, {
      model: models[0],
      context: task.context
    });
    
    // Stage 2: Synthesis (parallel, secondary model)
    console.log('[Pipeline] Stage 2: Synthesis (parallel)');
    const stage2Tasks = agents.slice(1, 3).map(agent =>
      this.agentPool[agent].execute(stage1Result, {
        model: models[1] || models[0],
        context: task.context
      })
    );
    
    const stage2Results = await Promise.all(stage2Tasks);
    
    // Stage 3: Assembly (if 4th agent present)
    let finalResult = stage1Result;
    
    if (agents.length > 3) {
      console.log('[Pipeline] Stage 3: Assembly');
      finalResult = await this.agentPool[agents[3]].execute(
        JSON.stringify(stage2Results),
        {
          model: models[0],
          context: task.context
        }
      );
    }
    
    return {
      pattern: 'pipeline',
      stages: [
        { stage: 1, agent: agents[0], result: stage1Result },
        { stage: 2, agents: agents.slice(1, 3), results: stage2Results },
        { stage: 3, agent: agents[3], result: finalResult }
      ],
      finalResult
    };
  }

  async executeParallel(task, agents, models) {
    /**
     * Parallel: 8 agents execute simultaneously on independent aspects
     * with a barrier (all must complete before assembly)
     * 
     * Timeline: 10–20 minutes
     */
    
    console.log(`[Parallel] Dispatching ${agents.length} agents in parallel`);
    
    const parallelTasks = agents.map((agent, idx) =>
      this.agentPool[agent]
        .execute(task.prompt, {
          model: models[idx % models.length],
          context: task.context
        })
        .then(result => ({ agent, result, idx }))
        .catch(error => ({ agent, error, idx }))
    );
    
    // Wait for all (barrier)
    const results = await Promise.all(parallelTasks);
    
    console.log('[Parallel] All agents completed, assembling results');
    
    // Assembly: combine results
    const assemblyInput = results
      .map(r => `[${r.agent}] ${r.result || r.error}`)
      .join('\n\n');
    
    const finalResult = await this.agentPool[agents[0]].execute(assemblyInput, {
      model: models[0],
      context: { ...task.context, phase: 'assembly' }
    });
    
    return {
      pattern: 'parallel',
      parallelResults: results,
      finalResult
    };
  }

  async executeFanOut(task, agents, models) {
    /**
     * Fan-Out: 16+ agents execute without barrier (async)
     * Results are collected asynchronously, not awaited
     * 
     * Timeline: 30 min–2h (can be left running)
     * 
     * Returns immediately with task IDs; results trickle in
     */
    
    console.log(`[FanOut] Spawning ${agents.length} agents (no barrier)`);
    
    const agentTaskIds = [];
    
    for (const agent of agents) {
      const subTaskId = `${task.id}:${agent}:${Date.now()}`;
      
      // Fire and forget
      this.agentPool[agent]
        .execute(task.prompt, {
          model: models[Math.floor(Math.random() * models.length)],
          context: task.context
        })
        .then(result => {
          this.logFanOutResult(subTaskId, agent, result);
        })
        .catch(error => {
          console.error(`[FanOut] Sub-task ${subTaskId} failed:`, error.message);
        });
      
      agentTaskIds.push(subTaskId);
    }
    
    return {
      pattern: 'fan-out',
      subTaskIds: agentTaskIds,
      message: `Spawned ${agents.length} agents; results will arrive asynchronously`
    };
  }

  async logTaskExecution(task, result) {
    /**
     * Write task execution metrics to RAG learning log (Supabase)
     * 
     * Tracked: tokenCount, wall-clock, model(s), agent(s), status, cost
     */
    
    const duration = (task.completedAt || Date.now()) - task.dispatchedAt;
    
    const logEntry = {
      task_id: task.id,
      prompt_excerpt: task.prompt.slice(0, 100),
      volume_band: task.routing.metadata.tokenCount < 500 ? 'pequeno' : 
                   task.routing.metadata.tokenCount < 2000 ? 'medio' :
                   task.routing.metadata.tokenCount < 5000 ? 'grande' : 'extra-grande',
      complexity: task.routing.metadata.complexity,
      segment: task.routing.metadata.segment,
      agents: task.routing.agents.join('|'),
      models: task.routing.models.join('|'),
      pattern: task.routing.pattern,
      priority: task.routing.priority,
      wall_clock_ms: duration,
      status: task.status,
      error: task.error || null,
      timestamp: new Date().toISOString()
    };
    
    // TODO: INSERT INTO rag_learning_log (Supabase)
    console.log('[RAG_LEARNING]', JSON.stringify(logEntry));
  }

  logFanOutResult(subTaskId, agent, result) {
    console.log(`[FanOut] ${subTaskId} completed by ${agent}`);
    // TODO: Async write to results table
  }

  stop() {
    this.isRunning = false;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  getQueueStats() {
    return {
      Q0: this.queues['Q0'].length,
      Q16: this.queues['Q16'].length,
      'Q∞': this.queues['Q∞'].length,
      total: this.queues['Q0'].length + this.queues['Q16'].length + this.queues['Q∞'].length
    };
  }
}
```

---

## 4. INTEGRATION POINTS

### 4.1 System Initialization

```javascript
// 1. Create router instance
const router = new MaestroRouter();

// 2. Create model selector
const selector = new AdaptiveModelSelector();

// 3. Create queue dispatcher
const agentPool = {
  'Manta 00': maestro,
  'Manta 01': claims,
  'Manta 02': contratual,
  'Manta 05': orcamento,
  'Manta 07': cronograma,
  'agente-infraestrutura-S1': agentS1,
  'agente-infraestrutura-S2': agentS2,
  // ... etc
};

const dispatcher = new QPrioDispatcher(agentPool);
dispatcher.start(); // Start main loop
```

### 4.2 User Request Flow

```javascript
// Endpoint: /api/maestro
app.post('/api/maestro', async (req, res) => {
  const { prompt, context } = req.body;
  
  // STEP 1: Route
  const routing = router.dispatch(prompt, context);
  
  // STEP 2: Create task
  const task = {
    id: uuid(),
    prompt,
    context,
    timestamp: Date.now()
  };
  
  // STEP 3: Enqueue
  const queuedTask = dispatcher.enqueue(task, routing);
  
  // STEP 4: Return immediately with task ID
  return res.json({
    taskId: task.id,
    status: 'QUEUED',
    priority: routing.priority,
    expectedWaitMs: estimateWait(routing.priority),
    agents: routing.agents,
    models: routing.models,
    pattern: routing.pattern
  });
});
```

### 4.3 Monitoring Dashboard

```javascript
// Endpoint: /api/maestro/stats
app.get('/api/maestro/stats', (req, res) => {
  const stats = dispatcher.getQueueStats();
  return res.json({
    queues: stats,
    activeAgents: Object.keys(agentPool).length,
    timestamp: new Date().toISOString()
  });
});
```

---

## 5. DECISION EXAMPLES

### Example 1: Small Task (Consultoria)

```
Input: "Qual a SELIC hoje?"
→ tokenCount: 12 (pequeno)
→ complexity: baixa
→ segment: horizontal
→ priority: Q16
→ Model: Haiku
→ Pattern: direct (1 agent)
→ Agent: Manta 00 (just answer)
→ Wall-clock: <10 sec
```

### Example 2: Medium Task (Edital)

```
Input: "Analise este edital de concessão rodoviária (10 pgs)"
→ tokenCount: 1800 (medio)
→ complexity: alta
→ segment: S1 (rodovia)
→ priority: Q16
→ Model: Sonnet + Haiku
→ Pattern: pipeline (3 agentes)
→ Agents: [agente-infraestrutura-S1, Manta 02, Manta 15]
  Stage 1: S1 agent (técnica)
  Stage 2: Manta 02 (legal) + Manta 15 (advisory) in parallel
→ Wall-clock: 5–10 min
```

### Example 3: Large Task (Proposta Comercial)

```
Input: "Proposta comercial completa para concessão hidrelétrica até amanhã"
→ tokenCount: 3500 (grande)
→ complexity: critica
→ segment: S10 (barragens)
→ priority: Q0 (CRITICAL)
→ Model: Opus + Sonnet
→ Pattern: parallel (8 agentes)
→ Agents: [agente-barragens, Manta 02, Manta 05, Manta 07, 
           Manta 15, Manta 06, Manta 14, Manta 01]
→ Wall-clock: 20–30 min
```

---

## 6. RAG LEARNING LOG

### 6.1 Schema

```sql
CREATE TABLE rag_learning_log (
  id BIGSERIAL PRIMARY KEY,
  task_id UUID NOT NULL,
  prompt_excerpt VARCHAR(500),
  volume_band VARCHAR(20), -- pequeno|medio|grande|extra-grande
  complexity VARCHAR(20),  -- baixa|media|alta|critica
  segment VARCHAR(10),     -- S1..S10|horizontal
  agents TEXT,             -- pipe-separated agent IDs
  models TEXT,             -- pipe-separated model names
  pattern VARCHAR(20),     -- direct|pipeline|parallel|fan-out
  priority VARCHAR(10),    -- Q0|Q16|Q∞
  wall_clock_ms INTEGER,   -- actual execution time
  status VARCHAR(20),      -- COMPLETE|FAILED
  error TEXT,              -- if FAILED
  cost_cents DECIMAL,      -- token cost
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Weekly analysis view
SELECT 
  volume_band, 
  complexity, 
  pattern,
  COUNT(*) as tasks,
  AVG(wall_clock_ms) as avg_duration_ms,
  SUM(cost_cents) as total_cost,
  100.0 * SUM(CASE WHEN status = 'COMPLETE' THEN 1 ELSE 0 END) / COUNT(*) as success_pct
FROM rag_learning_log
WHERE created_at >= now() - interval '7 days'
GROUP BY volume_band, complexity, pattern
ORDER BY total_cost DESC;
```

---

## 7. DEPLOYMENT CHECKLIST

- [ ] Implement `MaestroRouter` class with 10 routing rules
- [ ] Implement `AdaptiveModelSelector` with decision matrix
- [ ] Implement `QPrioDispatcher` with 3-queue system
- [ ] Create `/api/maestro` endpoint
- [ ] Create `/api/maestro/stats` monitoring endpoint
- [ ] Create `rag_learning_log` table in Supabase
- [ ] Integrate with existing agent pool (Manta 00–07, 13–16, S1–S10)
- [ ] Load CLAUDE.md routing rules via YAML config
- [ ] Set up weekly RAG learning analysis job
- [ ] Test with 3 decision examples (small/medium/large)
- [ ] Gate: human review before production deploy
- [ ] Monitor SLAs: Q0 <5s, Q16 <60s, Q∞ unbounded

---

**Status:** Phase 2 complete. Ready for Phase 3: Agent capability matrix and RAG indexing.
