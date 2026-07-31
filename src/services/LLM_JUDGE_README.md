# LLM Judge - Sistema de Classificação de Riscos de PR

O LLM Judge é um sistema inteligente que usa Claude Haiku para classificar Pull Requests quanto ao nível de risco e recomendar ações de automação (auto-merge, merge condicional, ou requer revisão).

## 📋 Visão Geral

O LLM Judge analisa PRs sob diversos aspectos e classifica-as em três níveis:

- **LOW-RISK**: Auto-merge imediato (refatorações simples, documentação, etc)
- **MEDIUM-RISK**: Merge condicional se CI passou (features bem testadas, mudanças moderadas)
- **HIGH-RISK**: Requer revisão humana (breaking changes, segurança, grandes mudanças)

## 🎯 Recursos Principais

- **Haiku Classifier**: Usa Claude 3.5 Haiku para classificação rápida e eficiente
- **Confidence Scores**: Retorna score de 0.0-1.0 para cada análise
- **Risk Categories**: Identifica categorias específicas de risco:
  - Security (vulnerabilidades)
  - Breaking changes
  - Performance risks
  - Untested code
  - Large changesets
  - External dependencies
  - Database migrations
  - Infrastructure changes
  - Documentation
  - Low-risk refactors

- **Detailed Analysis**: Fornece análise detalhada com:
  - Security concerns
  - Performance risks
  - Test coverage
  - Change size
  - Code patterns

- **Action Recommendations**: 
  - `auto_merge`: Merge imediato
  - `conditional_merge`: Merge se CI passou
  - `requires_review`: Requer revisão humana
  - `blocking`: Bloqueada, não pode fazer merge

## 🚀 Instalação e Setup

### Pré-requisitos

```bash
npm install @anthropic-ai/sdk
```

### Variáveis de Ambiente

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 💻 Uso Básico

### Exemplo Simples

```typescript
import { createLLMJudge, type PRData } from './services/llm-judge';

const judge = createLLMJudge();

const prData: PRData = {
  prNumber: 123,
  owner: 'mycompany',
  repo: 'myapp',
  title: 'feat: add user authentication',
  description: 'Implements OAuth2 integration',
  author: 'jane.doe',
  branch: 'feat/auth',
  baseBranch: 'main',
  filesChanged: 8,
  additions: 250,
  deletions: 10,
  changedFiles: [
    {
      filename: 'src/auth/oauth.ts',
      additions: 150,
      deletions: 0,
    },
    {
      filename: 'src/auth/oauth.test.ts',
      additions: 100,
      deletions: 0,
    },
  ],
  commits: [
    {
      message: 'feat: add OAuth2 provider',
      author: 'jane.doe',
    },
  ],
  ciPassed: true,
  testsPassed: 50,
  testsFailed: 0,
  coverage: 88,
};

const judgment = await judge.judge(prData);

console.log(`Risk Level: ${judgment.riskLevel}`);
console.log(`Action: ${judgment.action}`);
console.log(`Confidence: ${judgment.confidence * 100}%`);
console.log(`Reason: ${judgment.reason}`);
```

### Usando a Função Auxiliar

```typescript
import { judgePR } from './services/llm-judge';

const judgment = await judgePR(prData);
console.log(judgment);
```

### Com Configuração Personalizada

```typescript
import { createLLMJudge } from './services/llm-judge';

const judge = createLLMJudge({
  model: 'claude-3-5-haiku-20241022',
  maxTokens: 1024,
  minConfidenceThreshold: 0.65,
});

const judgment = await judge.judge(prData);
```

## 📊 Estrutura de Resposta

```typescript
interface PRJudgment {
  // Identificação
  prNumber: number;
  owner: string;
  repo: string;
  title: string;
  author: string;

  // Classificação
  riskLevel: 'high' | 'medium' | 'low';
  riskCategories: RiskCategory[];
  confidence: number; // 0.0-1.0
  reason: string;

  // Ação recomendada
  action: JudgeAction; // auto_merge | conditional_merge | requires_review | blocking
  actionReason: string;

  // Análise detalhada
  detailedAnalysis: {
    securityConcerns: string[];
    performanceRisks: string[];
    testCoverage: {
      hasTests: boolean;
      confidence: number;
    };
    changeSize: {
      filesChanged: number;
      additionsCount: number;
      deletionsCount: number;
      severity: 'large' | 'medium' | 'small';
    };
    codePatterns: {
      hasBreakingChanges: boolean;
      hasExternalDeps: boolean;
      hasMigrations: boolean;
      hasDocumentation: boolean;
    };
  };

  // Metadados
  analyzedAt: Date;
  model: string;
  promptTokens?: number;
  completionTokens?: number;
}
```

## 🔍 Exemplos de Uso Avançado

### Integração com GitHub API

```typescript
import { GitHubPRAutoMerger } from './examples/llm-judge-integration';

const merger = new GitHubPRAutoMerger(process.env.GITHUB_TOKEN!);

// Processar PR e obter decisão
const { judgment, action, comment } = await merger.processPR(prData);

// Agir baseado na decisão
if (action === 'merge') {
  // Fazer merge automático
  await github.rest.pulls.merge({
    owner: prData.owner,
    repo: prData.repo,
    pull_number: prData.prNumber,
  });
} else if (action === 'comment') {
  // Postar comentário na PR
  await github.rest.issues.createComment({
    owner: prData.owner,
    repo: prData.repo,
    issue_number: prData.prNumber,
    body: comment!,
  });
}
```

### Integração com Webhook do GitHub

```typescript
import { Router } from 'express';
import { judgePR, type PRData } from './services/llm-judge';

const router = Router();

router.post('/webhook/pull_request', async (req, res) => {
  const { action, pull_request } = req.body;

  if (action !== 'opened' && action !== 'synchronize') {
    return res.json({ status: 'ignored' });
  }

  // Construir PRData a partir do webhook
  const prData: PRData = {
    prNumber: pull_request.number,
    owner: pull_request.base.repo.owner.login,
    repo: pull_request.base.repo.name,
    title: pull_request.title,
    description: pull_request.body,
    author: pull_request.user.login,
    branch: pull_request.head.ref,
    baseBranch: pull_request.base.ref,
    filesChanged: pull_request.changed_files,
    additions: pull_request.additions,
    deletions: pull_request.deletions,
    changedFiles: [], // Buscar via API se necessário
    commits: [], // Buscar via API se necessário
  };

  // Fazer julgamento
  const judgment = await judgePR(prData);

  // Postar comentário com resultado
  await github.rest.issues.createComment({
    owner: prData.owner,
    repo: prData.repo,
    issue_number: prData.prNumber,
    body: formatJudgmentComment(judgment),
  });

  res.json({ judgment });
});
```

### Análise em Lote

```typescript
import { judgePR } from './services/llm-judge';

async function analyzeMultiplePRs(prs: PRData[]) {
  const results = await Promise.all(
    prs.map(pr => judgePR(pr))
  );

  const summary = {
    total: results.length,
    high: results.filter(r => r.riskLevel === 'high').length,
    medium: results.filter(r => r.riskLevel === 'medium').length,
    low: results.filter(r => r.riskLevel === 'low').length,
  };

  console.log('📊 Resumo:', summary);

  return results;
}
```

## 🎓 Guia de Decisão

### Quando Auto-Merge é Seguro (LOW-RISK)

- ✅ Documentação ou comentários
- ✅ Refatorações simples e seguras
- ✅ Bump de versão ou metadata
- ✅ Pequenas correções (<50 linhas)
- ✅ CI passou com sucesso
- ✅ Sem mudanças em código sensível

### Quando Usar Merge Condicional (MEDIUM-RISK)

- ⚠️ Novas features com testes
- ⚠️ Mudanças em lógica não crítica
- ⚠️ Adição de dependências baixo-risco
- ⚠️ Mudanças cosméticas/UI
- ✅ CI passou
- ✅ Coverage adequada (70%+)

### Quando Requer Revisão (HIGH-RISK)

- 🛑 Breaking changes
- 🛑 Mudanças de segurança
- 🛑 Grandes changesets (100+ arquivos)
- 🛑 Database migrations
- 🛑 Infrastructure changes
- 🛑 Código sem testes
- 🛑 Padrões perigosos detectados

## 🔒 Padrões de Segurança Detectados

O judge detecta automaticamente:

- `eval()` ou `new Function()` - Execução dinâmica
- `innerHTML` assignment - XSS risk
- Operações DDL sem validação - SQL injection risk
- String interpolation em queries - SQL injection
- Mudanças em API pública
- Dependências externas novas
- Código sensível sem documentação

## 📈 Confiança do Classificador

O score de confiança indica:

- **0.95+**: Análise muito clara
- **0.80-0.95**: Análise clara com alta certeza
- **0.60-0.80**: Confiança moderada
- **0.40-0.60**: Incerteza, recomenda high-risk
- **<0.40**: Muito incerto, recomenda blocking

## 🔧 Configuração Avançada

### Personalizar Limiares

```typescript
const judge = createLLMJudge({
  minConfidenceThreshold: 0.7, // Require 70% confidence minimum
  model: 'claude-3-5-haiku-20241022',
});
```

### Usar Modelo Diferente

```typescript
const judge = createLLMJudge({
  model: 'claude-3-5-sonnet-20241022', // Para análises mais profundas
  maxTokens: 2048,
});
```

## 📝 Testes

Executar testes:

```bash
npm test -- src/services/__tests__/llm-judge.test.ts
```

Executar demo com exemplos:

```bash
npm ts-node src/examples/llm-judge-integration.ts
```

## 🚦 Fluxo de Decisão

```
PR Enviada
    ↓
LLM Judge analisa
    ↓
├─ LOW-RISK (Confidence > 0.8)
│  └─ auto_merge ✅
│
├─ MEDIUM-RISK
│  └─ conditional_merge (se CI passou) ✓
│  └─ requires_review (se CI falhou) ⚠️
│
└─ HIGH-RISK
   └─ requires_review ou blocking 🛑
```

## 🔐 Segurança

- Não armazena PRs em cache
- Usa apenas análise stateless
- Confiança em segurança do Anthropic API
- Sem dados sensíveis em logs

## 📊 Métricas e Monitoramento

Rastreie métricas importantes:

```typescript
interface JudgeMetrics {
  totalAnalyzed: number;
  highRiskCount: number;
  mediumRiskCount: number;
  lowRiskCount: number;
  averageConfidence: number;
  autoMergeRate: number;
  reviewRequiredRate: number;
}
```

## 🤝 Integração com CI/CD

Exemplo com GitHub Actions:

```yaml
name: LLM PR Review
on: [pull_request]

jobs:
  judge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run judge-pr
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## 💡 Best Practices

1. **Sempre revisar PRs HIGH-RISK manualmente**
2. **Testar bem as changes antes de contar com auto-merge**
3. **Monitorar a taxa de acertos do judge**
4. **Ajustar thresholds conforme necessário**
5. **Manter CI pipeline rápido e confiável**
6. **Documentar breaking changes claramente**

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY não configurada"

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Taxa de Confiança Baixa

Possíveis causas:
- PR muito ambígua ou complexa
- Falta de informações (CI status, testes)
- Padrões incomuns ou novos

**Solução**: Adicionar mais contexto à PR ou revisar manualmente

### Muito Conservador (Muitos HIGH-RISK)

Ajustar thresholds:

```typescript
const judge = createLLMJudge({
  minConfidenceThreshold: 0.5,
});
```

## 📚 Referências

- [Anthropic Claude API](https://docs.anthropic.com/)
- [GitHub REST API](https://docs.github.com/en/rest)
- [PR Automation Best Practices](https://github.blog/engineering/)

## 📄 Licença

Código fornecido sob licença do projeto.

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-02-14  
**Mantido por**: Equipe de Infraestrutura IA
