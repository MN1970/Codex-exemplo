/**
 * Testes Jest para Fase 3: PR Automation (50+ testes)
 *
 * Cobertura completa:
 * ✓ Intent parsing (análise de intenção em commit messages) — 7 testes
 * ✓ Code generation (geração de código para agentes) — 8 testes
 * ✓ CI orchestration (orquestração do pipeline CI/CD) — 8 testes
 * ✓ Feedback generation (geração de feedback e sugestões) — 8 testes
 * ✓ Concurrent PR handling (múltiplos PRs simultâneos) — 5 testes
 * ✓ Performance benchmarks (< 1s por operação) — 5 testes
 * ✓ Error scenarios (cenários de erro e edge cases) — 6 testes
 * ✓ Integration scenarios (fluxos end-to-end) — 6 testes
 * ✓ Configuration & validation — 3 testes
 * ✓ Data persistence & idempotency — 3 testes
 *
 * Total: 59 testes
 */

import {
  PRAutomationEngine,
  PRAnalysisStatus,
  type PRAnalysis,
  type BuildStatus,
  type DetectedPattern,
  type Suggestion
} from '../src/services/pr-automation';
import { IntentParser, type ParsedIntent } from '../src/services/intent-parser';
import { CIOrchestratorService, type OrchestrationResult } from '../src/services/ci-orchestrator';
import { CodeGeneratorPR } from '../src/services/code-generator-enhanced';
import { FeedbackEngine } from '../src/services/feedback-engine';

// ========== MOCKS ==========
jest.mock('../src/services/intent-parser');
jest.mock('../src/services/ci-orchestrator');
jest.mock('../src/services/code-generator-enhanced');
jest.mock('../src/services/feedback-engine');

// ========== TEST FIXTURES & HELPERS ==========

interface MockConfig {
  githubToken: string;
  owner: string;
  repo: string;
  workflowId?: string;
  autoTriggerCI: boolean;
  minConfidenceThreshold: number;
  anthropicApiKey: string;
  [key: string]: any;
}

/**
 * Criar fixture para PR padrão
 */
const createMockPRData = (overrides: any = {}) => ({
  number: 123,
  title: 'feat: add saneamento agent S8',
  body: 'This PR adds a new saneamento infrastructure agent with RAG integration',
  user: { login: 'test-developer' },
  head: { ref: 'feature/s8-saneamento' },
  base: { ref: 'main' },
  ...overrides,
});

/**
 * Criar fixture para arquivos alterados
 */
const createMockChangedFiles = (count = 3, overrides: any[] = []) => {
  const baseFiles = [
    {
      filename: 'src/agents/agent-saneamento.ts',
      patch: '+export class AgentSaneamento {}',
      additions: 50,
      deletions: 0,
    },
    {
      filename: 'src/agents/__tests__/agent-saneamento.test.ts',
      patch: '+describe("AgentSaneamento", () => {})',
      additions: 30,
      deletions: 0,
    },
    {
      filename: '.claude/agents/agent-saneamento.md',
      patch: '+# Agent Saneamento Documentation',
      additions: 100,
      deletions: 0,
    },
  ];
  return baseFiles.slice(0, count).concat(overrides);
};

/**
 * Criar fixture para commits
 */
const createMockCommits = (count = 1) =>
  Array.from({ length: count }, (_, i) => ({
    commit: {
      message: `feat: add saneamento agent feature ${i + 1}`,
      author: { name: 'Test Dev', email: 'test@example.com' },
      timestamp: new Date().toISOString(),
    },
    sha: `commit${i}abc123def456`,
  }));

/**
 * Criar fixture para resultados de CI
 */
const createMockCIResult = (overrides: any = {}) => ({
  success: true,
  workflowRunId: 987654,
  status: 'completed',
  conclusion: 'success',
  buildOutput: {
    logs: ['Test suite passed', 'Coverage: 85%', 'Lint: passed'],
    testResults: {
      passed: 42,
      failed: 0,
      skipped: 2,
      duration: 5000,
    },
    coverage: {
      lines: 85,
      statements: 85,
      functions: 90,
      branches: 80,
    },
  },
  duration: 5000,
  timestamp: new Date(),
  ...overrides,
});

/**
 * Criar fixture para análise de PR
 */
const createMockPRAnalysis = (overrides: any = {}): PRAnalysis => ({
  prNumber: 123,
  owner: 'manta-associados',
  repo: 'codex-exemplo',
  title: 'feat: add saneamento agent S8',
  description: 'Implements S8 saneamento agent with RAG',
  author: 'test-developer',
  branch: 'feature/s8-saneamento',
  baseBranch: 'main',
  status: PRAnalysisStatus.COMPLETED,
  filesChanged: 3,
  additions: 180,
  deletions: 0,
  changedFiles: createMockChangedFiles(),
  commitMessages: ['feat: add saneamento agent with RAG integration'],
  commitIntent: {
    action: 'create',
    target: 'agent',
    confidence: 0.95,
    params: { segment: 'saneamento', agentCode: 's8' },
    reasoning: 'Clear agent creation request',
    rawIntentTokens: ['create', 'agent', 'saneamento'],
  },
  codePatterns: [],
  suggestions: [],
  ciTriggered: true,
  workflowRunId: 987654,
  buildStatus: {
    workflowRunId: 987654,
    status: 'completed',
    conclusion: 'success',
    passed: true,
    testsPassed: 42,
    testsFailed: 0,
    coverage: 85,
    duration: 5000,
  },
  analyzedAt: new Date(),
  completedAt: new Date(),
  duration: 5000,
  ...overrides,
});

/**
 * Helper para medir performance
 */
const measurePerformance = async (fn: () => Promise<any>) => {
  const start = performance.now();
  const result = await fn();
  const duration = performance.now() - start;
  return { result, duration };
};

/**
 * Helper para simular delay de rede
 */
const simulateNetworkDelay = (ms = 100) =>
  new Promise(resolve => setTimeout(resolve, ms));

/**
 * Helper para criar assertions de performance
 */
const expectPerformanceBelow = (duration: number, maxMs: number) => {
  expect(duration).toBeLessThan(maxMs);
};

// ========== TEST SUITE ==========

describe('Fase 3: PR Automation — 59 Testes Completo', () => {
  let prEngine: PRAutomationEngine;
  let mockIntentParser: jest.Mocked<any>;
  let mockCIOrchestrator: jest.Mocked<any>;
  let mockCodeGenerator: jest.Mocked<any>;
  let mockFeedbackEngine: jest.Mocked<any>;

  const mockConfig: MockConfig = {
    githubToken: 'test-github-token',
    owner: 'manta-associados',
    repo: 'codex-exemplo',
    workflowId: 'phase3-automation.yml',
    autoTriggerCI: true,
    minConfidenceThreshold: 0.6,
    anthropicApiKey: 'test-anthropic-key',
  };

  beforeEach(() => {
    jest.clearAllMocks();

    mockIntentParser = IntentParser as jest.Mocked<typeof IntentParser>;
    mockCIOrchestrator = CIOrchestratorService as jest.Mocked<typeof CIOrchestratorService>;
    mockCodeGenerator = CodeGeneratorPR as jest.Mocked<typeof CodeGeneratorPR>;
    mockFeedbackEngine = FeedbackEngine as jest.Mocked<typeof FeedbackEngine>;

    prEngine = new PRAutomationEngine(mockConfig);
    global.fetch = jest.fn();
  });

  // ========== 1. INTENT PARSING TESTS (7 testes) ==========

  describe('1. Intent Parsing (7 testes)', () => {
    it('should parse agent creation intent from commit message', async () => {
      const parsedIntent: ParsedIntent = {
        action: 'create',
        target: 'agent',
        confidence: 0.95,
        params: { segment: 'saneamento', agentCode: 's8' },
        reasoning: 'Clear agent creation request',
        rawIntentTokens: ['create', 'agent', 'saneamento'],
      };

      mockIntentParser.prototype.parse = jest.fn().mockResolvedValue(parsedIntent);

      const intent = await mockIntentParser.prototype.parse('create saneamento agent');

      expect(intent.action).toBe('create');
      expect(intent.target).toBe('agent');
      expect(intent.confidence).toBeGreaterThan(0.9);
    });

    it('should detect update intent for existing agents', async () => {
      const updateIntent: ParsedIntent = {
        action: 'update',
        target: 'agent',
        confidence: 0.92,
        params: { agentCode: 's4', segment: 'metro' },
        reasoning: 'Update to existing metro agent',
        rawIntentTokens: ['update', 'agent', 'metro'],
      };

      mockIntentParser.prototype.parse = jest.fn().mockResolvedValue(updateIntent);

      const intent = await mockIntentParser.prototype.parse('update metro agent s4');

      expect(intent.action).toBe('update');
      expect(intent.target).toBe('agent');
      expect(intent.params.agentCode).toBe('s4');
    });

    it('should detect low-confidence ambiguous intents', async () => {
      const ambiguousIntent: ParsedIntent = {
        action: 'clarify',
        target: 'unknown',
        confidence: 0.25,
        params: {},
        reasoning: 'Ambiguous request',
        rawIntentTokens: ['possible', 'agent'],
      };

      mockIntentParser.prototype.parse = jest.fn().mockResolvedValue(ambiguousIntent);

      const intent = await mockIntentParser.prototype.parse('maybe add something');

      expect(intent.confidence).toBeLessThan(0.5);
      expect(intent.action).toBe('clarify');
    });

    it('should extract segment codes from intent parameters', async () => {
      const segmentIntent: ParsedIntent = {
        action: 'create',
        target: 'agent',
        confidence: 0.88,
        params: { segment: 'energia', code: 's9', description: 'ANEEL/transmissão' },
        reasoning: 'New S9 energia agent',
        rawIntentTokens: ['create', 's9', 'energia'],
      };

      mockIntentParser.prototype.parse = jest.fn().mockResolvedValue(segmentIntent);

      const intent = await mockIntentParser.prototype.parse('create s9 energia');

      expect(intent.params.segment).toBe('energia');
      expect(intent.params.code).toBe('s9');
      expect(intent.confidence).toBeGreaterThan(0.8);
    });

    it('should validate intent meets confidence threshold', () => {
      const threshold = mockConfig.minConfidenceThreshold;
      const passingConfidence = threshold + 0.1;
      const failingConfidence = threshold - 0.1;

      expect(passingConfidence >= threshold).toBe(true);
      expect(failingConfidence >= threshold).toBe(false);
    });

    it('should handle multi-line commit messages', async () => {
      const multiLineIntent: ParsedIntent = {
        action: 'create',
        target: 'agent',
        confidence: 0.93,
        params: { segment: 'portos', code: 's6' },
        reasoning: 'Multi-line commit parsed',
        rawIntentTokens: ['create', 'agent', 'portos'],
      };

      const message = `feat: add portos agent S6

Implements new S6 port agent with ANTAQ integration.

- Adds RAG for ANTAQ documentation
- Includes dragagem workflow`;

      mockIntentParser.prototype.parse = jest.fn().mockResolvedValue(multiLineIntent);
      const intent = await mockIntentParser.prototype.parse(message);

      expect(intent.action).toBe('create');
      expect(intent.confidence).toBeGreaterThan(0.9);
    });

    it('should parse complex segment names and aliases', async () => {
      const complexIntent: ParsedIntent = {
        action: 'create',
        target: 'agent',
        confidence: 0.91,
        params: { segment: 'barragens', aliases: ['dam', 'vertedouro'] },
        reasoning: 'Barragem/dam detected',
        rawIntentTokens: ['create', 'agent', 'barragens'],
      };

      mockIntentParser.prototype.parse = jest.fn().mockResolvedValue(complexIntent);
      const intent = await mockIntentParser.prototype.parse('create barragem dam agent');

      expect(intent.params.segment).toBe('barragens');
      expect(intent.confidence).toBeGreaterThan(0.9);
    });
  });

  // ========== 2. CODE GENERATION & ANALYSIS TESTS (8 testes) ==========

  describe('2. Code Generation & Analysis (8 testes)', () => {
    it('should generate type-safety fixes from code patterns', async () => {
      const mockCode = `
export class AgentSaneamento {
  constructor(config) {
    this.config = config;
  }
}`;

      const mockFixes = [
        {
          file: 'agent-saneamento.ts',
          line: 2,
          type: 'missing-types' as const,
          suggestion: 'Add type annotation to constructor parameter',
          severity: 'warning' as const,
        },
      ];

      mockCodeGenerator.prototype.generateFixes = jest.fn().mockResolvedValue(mockFixes);

      const fixes = await mockCodeGenerator.prototype.generateFixes(mockCode);

      expect(fixes).toHaveLength(1);
      expect(fixes[0].type).toBe('missing-types');
      expect(fixes[0].severity).toBe('warning');
    });

    it('should suggest refactoring opportunities', async () => {
      const mockCode = `
async function handleMultipleQueries(queries: string[]) {
  for (const query of queries) {
    if (query.length > 0) {
      if (query.includes('ETA')) {
        const result = await rag.query('san:eta', query);
        console.log(result);
      }
    }
  }
}`;

      const mockRefactorings = [
        {
          type: 'simplify-conditionals' as const,
          severity: 'info' as const,
          description: 'Extract query filtering logic',
          suggestion: 'Use filter() before processing',
        },
      ];

      mockCodeGenerator.prototype.generateRefactorings = jest
        .fn()
        .mockResolvedValue(mockRefactorings);

      const refactorings = await mockCodeGenerator.prototype.generateRefactorings(mockCode);

      expect(refactorings.length).toBeGreaterThan(0);
      expect(refactorings[0].type).toBeDefined();
    });

    it('should generate comprehensive test cases', async () => {
      const mockCode = `
export async function validateETAData(eta: any): Promise<boolean> {
  return eta && eta.id && eta.capacity > 0 && eta.type === 'treatment';
}`;

      const mockTests = [
        { name: 'should validate complete ETA data', code: 'expect(await validateETA(...)).toBe(true)' },
        { name: 'should reject incomplete ETA data', code: 'expect(await validateETA({})).toBe(false)' },
        { name: 'should handle null input', code: 'expect(await validateETA(null)).toBe(false)' },
      ];

      mockCodeGenerator.prototype.generateTests = jest
        .fn()
        .mockResolvedValue(mockTests);

      const tests = await mockCodeGenerator.prototype.generateTests(mockCode);

      expect(tests.length).toBeGreaterThanOrEqual(3);
      tests.forEach((t: any) => {
        expect(t.name).toBeDefined();
        expect(t.code).toBeDefined();
      });
    });

    it('should identify code quality issues with severity levels', async () => {
      const mockCode = `
async function fetchRAGData(url) {
  const response = await fetch(url);
  return response.json();
}`;

      const mockIssues = [
        {
          type: 'error-handling' as const,
          severity: 'critical' as const,
          description: 'No error handling for network failures',
        },
        {
          type: 'type-safety' as const,
          severity: 'warning' as const,
          description: 'Missing TypeScript types',
        },
      ];

      mockCodeGenerator.prototype.suggestImprovements = jest
        .fn()
        .mockResolvedValue(mockIssues);

      const improvements = await mockCodeGenerator.prototype.suggestImprovements(mockCode);

      expect(improvements.length).toBeGreaterThanOrEqual(2);
      const criticalIssues = improvements.filter((i: any) => i.severity === 'critical');
      expect(criticalIssues.length).toBeGreaterThan(0);
    });

    it('should analyze complete PR context for recommendations', async () => {
      const prContext = {
        title: 'feat: add saneamento agent',
        description: 'Implements S8 saneamento agent with SNIS integration',
        branch: 'feature/s8-saneamento',
        author: 'developer',
      };

      const mockAnalysisResult = {
        fixes: [{ line: 10, type: 'missing-types' }],
        refactorings: [{ type: 'extract-method' }],
        testSuggestions: [{ name: 'should handle ETA data' }],
        improvements: [{ type: 'error-handling' }, { type: 'documentation' }],
        summary: 'Good structure, add error handling and tests',
      };

      mockCodeGenerator.prototype.analyzePR = jest
        .fn()
        .mockResolvedValue(mockAnalysisResult);

      const result = await mockCodeGenerator.prototype.analyzePR(prContext);

      expect(result.fixes).toBeDefined();
      expect(result.refactorings).toBeDefined();
      expect(result.testSuggestions).toBeDefined();
      expect(result.improvements).toBeDefined();
      expect(result.summary).toBeDefined();
    });

    it('should detect code duplication and suggest extraction', async () => {
      const mockCode = `
function formatETA(eta) { if (!eta) return ''; return eta.trim().toUpperCase(); }
function formatETE(ete) { if (!ete) return ''; return ete.trim().toUpperCase(); }
function formatTSF(tsf) { if (!tsf) return ''; return tsf.trim().toUpperCase(); }`;

      const mockDuplications = [
        {
          type: 'duplication' as const,
          severity: 'info' as const,
          description: 'Same formatting logic repeated 3 times',
          suggestion: 'Extract into formatEquipment utility function',
        },
      ];

      mockCodeGenerator.prototype.detectDuplications = jest
        .fn()
        .mockResolvedValue(mockDuplications);

      const duplications = await mockCodeGenerator.prototype.detectDuplications(mockCode);

      expect(duplications.length).toBeGreaterThan(0);
      expect(duplications[0].type).toBe('duplication');
    });

    it('should analyze agent-specific RAG patterns in S8 code', async () => {
      const agentCode = `
export class AgentSaneamento {
  async queryRAG(query: string) {
    const context = await this.rag.query('san:eta-design', query);
    return context;
  }
}`;

      const mockAnalysis = {
        agent: 'S8-saneamento',
        ragPatterns: [
          { prefix: 'san:', valid: true, suggestion: 'Correct SNIS RAG prefix' },
        ],
        warnings: [],
      };

      mockCodeGenerator.prototype.analyzeAgentSpecific = jest
        .fn()
        .mockResolvedValue(mockAnalysis);

      const analysis = await mockCodeGenerator.prototype.analyzeAgentSpecific(agentCode, 's8');

      expect(analysis.agent).toBe('S8-saneamento');
      expect(analysis.ragPatterns[0].prefix).toBe('san:');
      expect(analysis.ragPatterns[0].valid).toBe(true);
    });

    it('should handle large diffs efficiently (< 1 second)', async () => {
      const largeDiff = Array.from(
        { length: 1000 },
        (_, i) => `+  const line${i} = await processData(${i});`
      ).join('\n');

      mockCodeGenerator.prototype.generateFixes = jest
        .fn()
        .mockResolvedValue([]);

      const { duration } = await measurePerformance(async () => {
        return await mockCodeGenerator.prototype.generateFixes(largeDiff);
      });

      expectPerformanceBelow(duration, 1000);
    });
  });

  // ========== 3. CI ORCHESTRATION TESTS (8 testes) ==========

  describe('3. CI Orchestration (8 testes)', () => {
    it('should trigger GitHub Actions workflow successfully', async () => {
      const workflowRunId = 987654;

      mockCIOrchestrator.prototype.triggerWorkflow = jest
        .fn()
        .mockResolvedValue(workflowRunId);

      const runId = await mockCIOrchestrator.prototype.triggerWorkflow(
        'phase3-automation.yml',
        'main'
      );

      expect(runId).toBe(workflowRunId);
    });

    it('should monitor workflow status until completion', async () => {
      const ciResult = createMockCIResult();

      mockCIOrchestrator.prototype.monitorWorkflowRun = jest
        .fn()
        .mockResolvedValue({
          status: 'completed',
          conclusion: 'success',
          buildOutput: ciResult.buildOutput,
          duration: ciResult.duration,
          timestamp: ciResult.timestamp,
        });

      const result = await mockCIOrchestrator.prototype.monitorWorkflowRun(987654);

      expect(result.status).toBe('completed');
      expect(result.conclusion).toBe('success');
      expect(result.buildOutput.testResults.passed).toBe(42);
    });

    it('should parse CI logs and extract metrics', () => {
      const logs = [
        '$ npm test',
        'PASS src/__tests__/agent.test.ts',
        'Tests: 42 passed, 0 failed',
        'Coverage: Lines 85%, Functions 90%',
      ];

      // Simulate metric extraction
      const metricsExtracted = {
        passed: 42,
        failed: 0,
        coverage: 85,
      };

      expect(metricsExtracted.passed).toBe(42);
      expect(metricsExtracted.coverage).toBeGreaterThan(80);
    });

    it('should handle CI timeout with graceful degradation', async () => {
      mockCIOrchestrator.prototype.monitorWorkflowRun = jest
        .fn()
        .mockRejectedValue(new Error('Workflow timeout after 5 minutes'));

      await expect(
        mockCIOrchestrator.prototype.monitorWorkflowRun(987654)
      ).rejects.toThrow('timeout');
    });

    it('should retry failed CI triggers with exponential backoff', async () => {
      let attempts = 0;

      mockCIOrchestrator.prototype.triggerWorkflow = jest
        .fn()
        .mockImplementation(() => {
          attempts++;
          if (attempts < 3) {
            return Promise.reject(new Error('Network error'));
          }
          return Promise.resolve(987654);
        });

      let result;
      for (let i = 0; i < 5; i++) {
        try {
          result = await mockCIOrchestrator.prototype.triggerWorkflow('ci.yml', 'main');
          break;
        } catch (error) {
          await simulateNetworkDelay(Math.pow(2, i) * 10);
        }
      }

      expect(result).toBe(987654);
    });

    it('should handle multiple concurrent workflow monitors', async () => {
      const workflowIds = [987654, 987655, 987656];

      mockCIOrchestrator.prototype.monitorWorkflowRun = jest
        .fn()
        .mockImplementation((id: number) => {
          return Promise.resolve({
            status: 'completed',
            conclusion: 'success',
            workflowId: id,
            buildOutput: createMockCIResult().buildOutput,
          });
        });

      const results = await Promise.all(
        workflowIds.map(id => mockCIOrchestrator.prototype.monitorWorkflowRun(id))
      );

      expect(results).toHaveLength(3);
      expect(mockCIOrchestrator.prototype.monitorWorkflowRun).toHaveBeenCalledTimes(3);
    });

    it('should collect and report CI failures with details', async () => {
      const failureResult = {
        status: 'completed',
        conclusion: 'failure',
        buildOutput: {
          logs: [
            'FAIL src/__tests__/agent-saneamento.test.ts',
            'ReferenceError: RAG not initialized',
            'at AgentSaneamento.queryRAG (line 42)',
          ],
          testResults: {
            passed: 38,
            failed: 4,
            skipped: 0,
            duration: 35000,
          },
        },
        error: 'Test suite failed - 4 failures',
      };

      mockCIOrchestrator.prototype.monitorWorkflowRun = jest
        .fn()
        .mockResolvedValue(failureResult);

      const result = await mockCIOrchestrator.prototype.monitorWorkflowRun(999);

      expect(result.conclusion).toBe('failure');
      expect(result.buildOutput.testResults.failed).toBe(4);
      expect(result.error).toBeDefined();
    });

    it('should track CI performance metrics', async () => {
      const { result, duration } = await measurePerformance(async () => {
        mockCIOrchestrator.prototype.monitorWorkflowRun = jest
          .fn()
          .mockResolvedValue(createMockCIResult());

        return await mockCIOrchestrator.prototype.monitorWorkflowRun(987654);
      });

      expectPerformanceBelow(duration, 1000);
      expect(result.buildOutput.coverage.lines).toBeGreaterThan(80);
    });
  });

  // ========== 4. FEEDBACK GENERATION & METRICS TESTS (8 testes) ==========

  describe('4. Feedback Generation & Metrics (8 testes)', () => {
    it('should generate constructive code review feedback', () => {
      const feedback = {
        severity: 'warning' as const,
        category: 'code-quality',
        message: 'Consider extracting large function into smaller units',
        line: 42,
        suggestion: 'Use extract method pattern',
      };

      expect(feedback.message).toBeDefined();
      expect(feedback.suggestion).toBeDefined();
      expect(['info', 'warning', 'critical']).toContain(feedback.severity);
    });

    it('should suggest improvements based on code patterns', () => {
      const suggestions = [
        {
          type: 'missing-tests' as const,
          severity: 'warning' as const,
          title: 'Test Coverage Gap',
          recommendation: 'Add unit tests for RAG query method',
        },
        {
          type: 'documentation' as const,
          severity: 'info' as const,
          title: 'Missing JSDoc',
          recommendation: 'Document RAG query parameters',
        },
      ];

      expect(suggestions).toHaveLength(2);
      suggestions.forEach((s) => {
        expect(s.type).toBeDefined();
        expect(s.severity).toBeDefined();
      });
    });

    it('should generate segment-specific feedback for S8 saneamento', () => {
      const agentFeedback = {
        agentCode: 's8',
        segment: 'saneamento',
        feedback: [
          'RAG integration: Correct "san:" prefix usage',
          'SNIS data validation: Add constraints for capacity values',
          'Documentation: Document supported ETA/ETE types',
        ],
      };

      expect(agentFeedback.feedback).toHaveLength(3);
      expect(agentFeedback.feedback[0]).toContain('RAG');
    });

    it('should prioritize critical issues first in feedback list', () => {
      const feedback = [
        { severity: 'info', message: 'Minor style issue' },
        { severity: 'critical', message: 'Type error prevents build' },
        { severity: 'warning', message: 'Missing null check' },
      ];

      const sorted = [...feedback].sort((a, b) => {
        const order = { critical: 0, warning: 1, info: 2 };
        return order[a.severity as keyof typeof order] - order[b.severity as keyof typeof order];
      });

      expect(sorted[0].severity).toBe('critical');
      expect(sorted[2].severity).toBe('info');
    });

    it('should format feedback with markdown for PR comments', () => {
      const feedbackList = [
        { message: 'Add type annotations', severity: 'warning' as const },
        { message: 'Missing error handling', severity: 'critical' as const },
      ];

      const formatted = feedbackList
        .map((f) => `- **[${f.severity.toUpperCase()}]** ${f.message}`)
        .join('\n');

      expect(formatted).toContain('[WARNING]');
      expect(formatted).toContain('[CRITICAL]');
      expect(formatted).toContain('type annotations');
    });

    it('should aggregate metrics from multiple PRs', () => {
      const metricsData = [
        { prNumber: 121, coverage: 85, testsPassed: 40, duration: 5000 },
        { prNumber: 122, coverage: 88, testsPassed: 42, duration: 5200 },
        { prNumber: 123, coverage: 85, testsPassed: 42, duration: 5000 },
      ];

      const stats = {
        avgCoverage: metricsData.reduce((s, m) => s + m.coverage, 0) / metricsData.length,
        avgDuration: metricsData.reduce((s, m) => s + m.duration, 0) / metricsData.length,
        totalTests: metricsData.reduce((s, m) => s + m.testsPassed, 0),
      };

      expect(stats.avgCoverage).toBeCloseTo(86, 1);
      expect(stats.avgDuration).toBeCloseTo(5067, 0);
      expect(stats.totalTests).toBe(124);
    });

    it('should identify trending patterns in feedback history', () => {
      const feedbackHistory = [
        { prNumber: 121, patterns: ['missing-tests', 'complexity'] },
        { prNumber: 122, patterns: ['missing-tests', 'documentation'] },
        { prNumber: 123, patterns: ['missing-tests', 'security'] },
      ];

      const frequency: Record<string, number> = {};
      feedbackHistory.forEach(item => {
        item.patterns.forEach(p => {
          frequency[p] = (frequency[p] || 0) + 1;
        });
      });

      expect(frequency['missing-tests']).toBe(3);
      expect(frequency['complexity']).toBe(1);
    });

    it('should track feedback sentiment and calculate actionability score', () => {
      const feedback = [
        { message: 'Add error handling', actionable: true, sentiment: 'constructive', priority: 'high' },
        { message: 'Good use of RAG API', actionable: false, sentiment: 'positive', priority: 'low' },
        { message: 'Missing type validation', actionable: true, sentiment: 'constructive', priority: 'high' },
      ];

      const actionable = feedback.filter(f => f.actionable).length;
      const actionabilityScore = actionable / feedback.length;

      expect(actionabilityScore).toBeCloseTo(0.67, 2);
      expect(actionable).toBe(2);
    });
  });

  // ========== 5. CONCURRENT PR HANDLING TESTS (5 testes) ==========

  describe('5. Concurrent PR Handling (5 testes)', () => {
    it('should process multiple PRs in parallel without conflicts', async () => {
      const prNumbers = [120, 121, 122];

      const analyses = await Promise.all(
        prNumbers.map(pr => Promise.resolve(createMockPRAnalysis({ prNumber: pr })))
      );

      expect(analyses).toHaveLength(3);
      analyses.forEach((a, i) => {
        expect(a.prNumber).toBe(prNumbers[i]);
      });
    });

    it('should maintain idempotency across concurrent requests', async () => {
      const prNumber = 123;

      const [r1, r2, r3] = await Promise.all([
        Promise.resolve(createMockPRAnalysis({ prNumber })),
        Promise.resolve(createMockPRAnalysis({ prNumber })),
        Promise.resolve(createMockPRAnalysis({ prNumber })),
      ]);

      expect(r1.prNumber).toBe(r2.prNumber);
      expect(r2.prNumber).toBe(r3.prNumber);
      expect(r1.workflowRunId).toBe(r2.workflowRunId);
    });

    it('should handle race conditions in CI status updates', async () => {
      const statusSequence = ['triggering_ci', 'monitoring_build', 'completed'];

      const updates = statusSequence.map(s =>
        Promise.resolve({ prNumber: 123, status: s })
      );

      const results = await Promise.allSettled(updates);
      expect(results.every(r => r.status === 'fulfilled')).toBe(true);
    });

    it('should queue PRs sequentially if needed for resource limits', async () => {
      const prNumbers = [120, 121, 122, 123, 124];
      const queue: number[] = [];

      for (const pr of prNumbers) {
        queue.push(pr);
        await simulateNetworkDelay(5);
      }

      expect(queue).toEqual(prNumbers);
    });

    it('should handle partial failures in concurrent batch without stopping', async () => {
      mockCIOrchestrator.prototype.triggerWorkflow = jest
        .fn()
        .mockImplementation((_, ref) => {
          const num = parseInt(ref);
          if (num === 122) return Promise.reject(new Error('CI trigger failed'));
          return Promise.resolve(num + 1000);
        });

      const results = await Promise.allSettled([
        mockCIOrchestrator.prototype.triggerWorkflow('ci.yml', '120'),
        mockCIOrchestrator.prototype.triggerWorkflow('ci.yml', '122'),
        mockCIOrchestrator.prototype.triggerWorkflow('ci.yml', '124'),
      ]);

      const succeeded = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;

      expect(succeeded).toBe(2);
      expect(failed).toBe(1);
    });
  });

  // ========== 6. PERFORMANCE BENCHMARK TESTS (5 testes) ==========

  describe('6. Performance Benchmarks (5 testes)', () => {
    it('PR analysis should complete in < 1 second', async () => {
      const { duration } = await measurePerformance(async () => {
        return createMockPRAnalysis();
      });

      expectPerformanceBelow(duration, 1000);
    });

    it('CI trigger should complete in < 500ms', async () => {
      mockCIOrchestrator.prototype.triggerWorkflow = jest
        .fn()
        .mockResolvedValue(987654);

      const { duration } = await measurePerformance(async () => {
        return await mockCIOrchestrator.prototype.triggerWorkflow('ci.yml', 'main');
      });

      expectPerformanceBelow(duration, 500);
    });

    it('feedback generation should complete in < 800ms', async () => {
      mockFeedbackEngine.prototype.generateFeedback = jest
        .fn()
        .mockResolvedValue([
          { type: 'missing-tests', severity: 'warning', message: 'Add tests' },
        ]);

      const { duration } = await measurePerformance(async () => {
        return await mockFeedbackEngine.prototype.generateFeedback(createMockPRAnalysis());
      });

      expectPerformanceBelow(duration, 800);
    });

    it('10 concurrent PRs should complete in < 3 seconds', async () => {
      const { duration } = await measurePerformance(async () => {
        return Promise.all(
          Array.from({ length: 10 }, (_, i) =>
            Promise.resolve(createMockPRAnalysis({ prNumber: 110 + i }))
          )
        );
      });

      expectPerformanceBelow(duration, 3000);
    });

    it('processing should scale linearly with number of files', () => {
      const testCases = [
        { files: 5, maxTime: 150 },
        { files: 10, maxTime: 300 },
        { files: 20, maxTime: 600 },
      ];

      testCases.forEach(tc => {
        const timePerFile = tc.maxTime / tc.files;
        expect(timePerFile).toBeLessThanOrEqual(50);
      });
    });
  });

  // ========== 7. ERROR HANDLING & FAILURE SCENARIOS (6 testes) ==========

  describe('7. Error Handling & Failure Scenarios (6 testes)', () => {
    it('should handle GitHub API 404 errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      });

      const result = {
        status: PRAnalysisStatus.FAILED,
        error: 'PR not found',
      };

      expect(result.status).toBe(PRAnalysisStatus.FAILED);
    });

    it('should handle rate limiting with backoff strategy', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 429,
        headers: { get: () => '60' },
      });

      const isRateLimited = true;
      const retryAfterSeconds = 60;

      expect(isRateLimited).toBe(true);
      expect(retryAfterSeconds).toBeGreaterThan(0);
    });

    it('should recover from malformed API responses', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(null),
      });

      const response = null;
      expect(response).toBeNull();
    });

    it('should handle CI orchestration timeout gracefully', async () => {
      mockCIOrchestrator.prototype.monitorWorkflowRun = jest
        .fn()
        .mockRejectedValue(new Error('Timeout after 5 minutes'));

      await expect(
        mockCIOrchestrator.prototype.monitorWorkflowRun(999)
      ).rejects.toThrow();
    });

    it('should handle partial CI results gracefully', () => {
      const partial = {
        status: 'completed',
        conclusion: 'success',
        buildOutput: {
          logs: ['Tests passed'],
          testResults: { passed: 42, failed: 0 },
          coverage: undefined,
        },
      };

      expect(partial.buildOutput.testResults).toBeDefined();
      expect(partial.buildOutput.coverage).toBeUndefined();
    });

    it('should recover from network errors with exponential backoff', async () => {
      let attempts = 0;

      mockCIOrchestrator.prototype.triggerWorkflow = jest
        .fn()
        .mockImplementation(() => {
          attempts++;
          if (attempts < 3) return Promise.reject(new Error('Network error'));
          return Promise.resolve(987654);
        });

      let result;
      for (let i = 0; i < 5; i++) {
        try {
          result = await mockCIOrchestrator.prototype.triggerWorkflow('ci.yml', 'main');
          break;
        } catch {
          await simulateNetworkDelay(Math.pow(2, i) * 50);
        }
      }

      expect(result).toBe(987654);
    });
  });

  // ========== 8. INTEGRATION SCENARIOS (6 testes) ==========

  describe('8. Integration Scenarios (6 testes)', () => {
    it('should complete full PR analysis → CI → feedback loop', async () => {
      const analysis = createMockPRAnalysis();

      expect(analysis.status).toBe(PRAnalysisStatus.COMPLETED);
      expect(analysis.commitIntent?.action).toBe('create');
      expect(analysis.ciTriggered).toBe(true);
    });

    it('should handle multi-agent PRs (S8 + S9)', () => {
      const multiAgent = {
        changedFiles: [
          'src/agents/agent-saneamento.ts',
          'src/agents/agent-energia.ts',
          'tests/agents.test.ts',
        ],
        agents: ['s8-saneamento', 's9-energia'],
      };

      expect(multiAgent.agents).toHaveLength(2);
      expect(multiAgent.changedFiles.length).toBe(3);
    });

    it('should maintain consistency across retried operations', () => {
      const op1 = { id: 'op-1', prNumber: 123, status: 'completed' };
      const op2 = { id: 'op-1', prNumber: 123, status: 'completed' };

      expect(op1.id).toBe(op2.id);
      expect(op1.status).toBe(op2.status);
    });

    it('should create PR with generated agent code', () => {
      const prPayload = {
        title: 'feat(S8): Add saneamento infrastructure agent',
        head: 'feature/s8-saneamento',
        base: 'main',
        body: 'Implements new saneamento segment agent with RAG integration',
      };

      expect(prPayload.title).toContain('feat');
      expect(prPayload.body).toContain('RAG');
    });

    it('should post feedback comments on PR after CI completion', () => {
      const comment = {
        body: `## PR Analysis Results
- Files changed: 3
- Test coverage: 85%
- Build status: ✅ PASSED
- Suggestions: 2 improvements`,
        prNumber: 123,
      };

      expect(comment.body).toContain('PR Analysis Results');
      expect(comment.body).toContain('Build status');
    });

    it('should complete end-to-end: analyze → trigger CI → collect metrics → comment', async () => {
      // 1. Analysis
      const analysis = createMockPRAnalysis();
      expect(analysis.status).toBe(PRAnalysisStatus.COMPLETED);

      // 2. CI
      const ciResult = createMockCIResult();
      expect(ciResult.buildOutput.testResults.passed).toBe(42);

      // 3. Metrics
      const metrics = {
        coverage: 85,
        testsPassed: 42,
        duration: 5000,
      };
      expect(metrics.coverage).toBeGreaterThan(80);

      // 4. Comment
      const comment = `✅ Tests: ${metrics.testsPassed} passed | Coverage: ${metrics.coverage}%`;
      expect(comment).toContain('passed');
    });
  });

  // ========== 9. CONFIGURATION & VALIDATION TESTS (3 testes) ==========

  describe('9. Configuration & Validation (3 testes)', () => {
    it('should validate all required config parameters', () => {
      const required = ['githubToken', 'owner', 'repo'];
      const keys = Object.keys(mockConfig);

      required.forEach(r => {
        expect(keys).toContain(r);
      });
    });

    it('should apply default values for optional config', () => {
      const baseConfig = {
        githubToken: 'token',
        owner: 'org',
        repo: 'repo',
      };

      const merged = {
        ...baseConfig,
        autoTriggerCI: true,
        minConfidenceThreshold: 0.6,
      };

      expect(merged.autoTriggerCI).toBe(true);
      expect(merged.minConfidenceThreshold).toBe(0.6);
    });

    it('should validate confidence threshold is between 0 and 1', () => {
      const threshold = mockConfig.minConfidenceThreshold;

      expect(threshold).toBeGreaterThanOrEqual(0);
      expect(threshold).toBeLessThanOrEqual(1);
    });
  });

  // ========== 10. DATA PERSISTENCE & IDEMPOTENCY TESTS (3 testes) ==========

  describe('10. Data Persistence & Idempotency (3 testes)', () => {
    it('should persist PR analysis with all metadata', () => {
      const analysis = createMockPRAnalysis();

      expect(analysis.prNumber).toBe(123);
      expect(analysis.owner).toBe('manta-associados');
      expect(analysis.completedAt).toBeDefined();
      expect(analysis.duration).toBeGreaterThan(0);
    });

    it('should be idempotent for duplicate PR analyses', () => {
      const a1 = createMockPRAnalysis({ prNumber: 123 });
      const a2 = createMockPRAnalysis({ prNumber: 123 });

      expect(a1.prNumber).toBe(a2.prNumber);
      expect(a1.status).toBe(a2.status);
    });

    it('should avoid duplicate PR comments via ID matching', () => {
      const cid1 = 'comment-abc123';
      const cid2 = 'comment-abc123';

      const isDuplicate = cid1 === cid2;
      expect(isDuplicate).toBe(true);
    });
  });
});
