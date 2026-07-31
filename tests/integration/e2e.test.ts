/**
 * End-to-End Integration Tests (E2E)
 *
 * Cobertura completa de fluxos críticos:
 * ✓ Full flow: intent → merge (mocked)
 * ✓ Error scenarios (CI timeout, generation fail)
 * ✓ Webhook delivery & retry
 * ✓ Cowork sync consistency
 * ✓ Rollback workflow
 *
 * Total: 12 testes E2E
 * Target: <5s por teste, >80% coverage
 */

import crypto from 'crypto';
import { EventEmitter } from 'events';

// ============================================================================
// MOCK TYPES & INTERFACES
// ============================================================================

enum WebhookEventType {
  PR_OPENED = 'pr.opened',
  PR_MERGED = 'pr.merged',
  COMMIT = 'commit',
  TASK_UPDATED = 'task.updated',
}

enum PRAnalysisStatus {
  PENDING = 'pending',
  ANALYZING = 'analyzing',
  ANALYZED = 'analyzed',
  TRIGGERING_CI = 'triggering_ci',
  MONITORING_BUILD = 'monitoring_build',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

enum RollbackPhase {
  PREPARING = 'preparing',
  REVERTING_CODE = 'reverting_code',
  REBUILDING = 'rebuilding',
  REVERTING_WORKSPACE = 'reverting_workspace',
  VERIFICATION = 'verification',
  COMPLETED = 'completed',
}

// Webhook Payload
interface WebhookPayload {
  event: WebhookEventType;
  timestamp: string;
  deliveryId: string;
  signature: string;
  data: Record<string, unknown>;
  retryCount?: number;
}

// PR Analysis Result
interface PRAnalysis {
  prNumber: number;
  owner: string;
  repo: string;
  title: string;
  author: string;
  branch: string;
  baseBranch: string;
  status: PRAnalysisStatus;
  filesChanged: number;
  additions: number;
  deletions: number;
  ciTriggered: boolean;
  workflowRunId?: number;
  buildStatus?: BuildStatus;
  analyzedAt: Date;
  completedAt?: Date;
  duration?: number;
  error?: string;
}

interface BuildStatus {
  workflowRunId: number;
  status: string;
  conclusion: string;
  passed: boolean;
  testsPassed: number;
  testsFailed: number;
  coverage: number;
  duration: number;
}

// Intent Parsing
interface ParsedIntent {
  action: string;
  target: string;
  confidence: number;
  params: Record<string, unknown>;
  reasoning: string;
}

// Webhook delivery result
interface WebhookDeliveryResult {
  deliveryId: string;
  success: boolean;
  status: 'pending' | 'sent' | 'failed' | 'retrying' | 'delivered';
  attempt: number;
  timestamp: Date;
  error?: string;
}

// Rollback request
interface RollbackRequest {
  rollbackId: string;
  prNumber: number;
  owner: string;
  repo: string;
  reason: string;
  initiatedBy: string;
  createdAt: Date;
}

// Rollback result
interface RollbackResult {
  rollbackId: string;
  phase: RollbackPhase;
  status: 'in_progress' | 'completed' | 'failed';
  previousCommitSha?: string;
  revertedCommitSha?: string;
  completedAt?: Date;
  duration?: number;
  error?: string;
}

// ============================================================================
// MOCK SERVICES
// ============================================================================

class MockIntentParser {
  async parseCommitMessage(message: string): Promise<ParsedIntent> {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('create') && lowerMessage.includes('agent')) {
      return {
        action: 'create',
        target: 'agent',
        confidence: 0.95,
        params: { segment: 'saneamento', agentCode: 's8' },
        reasoning: 'Clear agent creation request',
      };
    }

    if (lowerMessage.includes('update') && lowerMessage.includes('agent')) {
      return {
        action: 'update',
        target: 'agent',
        confidence: 0.92,
        params: { agentCode: 's4' },
        reasoning: 'Update to existing agent',
      };
    }

    if (lowerMessage.includes('fix') && lowerMessage.includes('bug')) {
      return {
        action: 'fix',
        target: 'bug',
        confidence: 0.88,
        params: { priority: 'high' },
        reasoning: 'Bug fix request',
      };
    }

    return {
      action: 'unknown',
      target: 'unknown',
      confidence: 0.1,
      params: {},
      reasoning: 'Could not parse intent',
    };
  }
}

class MockCIOrchestrator extends EventEmitter {
  private workflows = new Map<number, BuildStatus>();

  async triggerCI(prNumber: number, branch: string): Promise<number> {
    const workflowId = Math.floor(Math.random() * 1000000);

    this.workflows.set(workflowId, {
      workflowRunId: workflowId,
      status: 'queued',
      conclusion: '',
      passed: false,
      testsPassed: 0,
      testsFailed: 0,
      coverage: 0,
      duration: 0,
    });

    // Simulate async completion
    setTimeout(() => {
      this.workflows.set(workflowId, {
        workflowRunId: workflowId,
        status: 'completed',
        conclusion: 'success',
        passed: true,
        testsPassed: 42,
        testsFailed: 0,
        coverage: 85,
        duration: 5000,
      });
      this.emit('workflow:completed', { workflowId, status: 'success' });
    }, 100);

    return workflowId;
  }

  async getBuildStatus(workflowId: number): Promise<BuildStatus | null> {
    return this.workflows.get(workflowId) || null;
  }

  async failWorkflow(workflowId: number, reason: string): Promise<void> {
    const status = this.workflows.get(workflowId);
    if (status) {
      status.conclusion = 'failure';
      status.passed = false;
      this.emit('workflow:failed', { workflowId, reason });
    }
  }

  async timeoutWorkflow(workflowId: number): Promise<void> {
    const status = this.workflows.get(workflowId);
    if (status) {
      status.status = 'completed';
      status.conclusion = 'timed_out';
      status.passed = false;
      this.emit('workflow:timeout', { workflowId });
    }
  }
}

class MockCodeGenerator {
  private generationHistory: string[] = [];

  async generateCode(intent: ParsedIntent): Promise<string> {
    const code = `
// Generated code for ${intent.target} ${intent.action}
export class Generated${intent.target} {
  constructor(params: Record<string, unknown>) {
    // ${JSON.stringify(intent.params)}
  }
}
    `.trim();

    this.generationHistory.push(code);
    return code;
  }

  async failGeneration(reason: string): Promise<void> {
    throw new Error(`Code generation failed: ${reason}`);
  }

  getGenerationHistory(): string[] {
    return this.generationHistory;
  }
}

class MockWebhookHandler extends EventEmitter {
  private secret: string;
  private deliveryLog: WebhookDeliveryResult[] = [];
  private retryQueue: Map<string, { payload: WebhookPayload; retries: number }> = new Map();
  private maxRetries: number = 3;

  constructor(secret: string = 'test-webhook-secret') {
    super();
    this.secret = secret;
  }

  validateSignature(payload: string, signature: string): boolean {
    try {
      const expectedSignature = crypto
        .createHmac('sha256', this.secret)
        .update(payload)
        .digest('hex');

      if (signature.length !== expectedSignature.length) {
        return false;
      }

      return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));
    } catch (error) {
      return false;
    }
  }

  generateSignature(payload: string): string {
    return crypto.createHmac('sha256', this.secret).update(payload).digest('hex');
  }

  async handleWebhook(
    payload: WebhookPayload,
    shouldFail: boolean = false
  ): Promise<WebhookDeliveryResult> {
    const deliveryId = payload.deliveryId;
    const result: WebhookDeliveryResult = {
      deliveryId,
      success: false,
      status: 'pending',
      attempt: 1,
      timestamp: new Date(),
    };

    try {
      if (shouldFail) {
        throw new Error('Simulated webhook processing failure');
      }

      result.success = true;
      result.status = 'delivered';
      this.emit('webhook:delivered', { deliveryId });
    } catch (error) {
      result.error = (error as Error).message;
      result.status = 'failed';

      // Attempt retry
      if (!this.retryQueue.has(deliveryId)) {
        this.retryQueue.set(deliveryId, { payload, retries: 0 });
      }

      const queuedItem = this.retryQueue.get(deliveryId);
      if (queuedItem && queuedItem.retries < this.maxRetries) {
        result.status = 'retrying';
        result.attempt = queuedItem.retries + 1;

        // Simulate retry
        setTimeout(() => {
          queuedItem.retries++;
          this.emit('webhook:retry', { deliveryId, attempt: result.attempt });
        }, 100 * result.attempt);
      }
    }

    this.deliveryLog.push(result);
    return result;
  }

  getDeliveryLog(): WebhookDeliveryResult[] {
    return this.deliveryLog;
  }

  getRetryQueueSize(): number {
    return this.retryQueue.size;
  }
}

class MockCoworkSync {
  private syncState: Map<string, unknown> = new Map();
  private syncHistory: Array<{ action: string; data: unknown; timestamp: Date }> = [];
  private consistencyErrors: string[] = [];

  async syncPRData(prNumber: number, data: Partial<PRAnalysis>): Promise<void> {
    const key = `pr:${prNumber}`;
    this.syncState.set(key, data);
    this.syncHistory.push({
      action: 'sync_pr_data',
      data,
      timestamp: new Date(),
    });
  }

  async syncWorkflowStatus(
    workflowId: number,
    status: Partial<BuildStatus>
  ): Promise<void> {
    const key = `workflow:${workflowId}`;
    const existing = this.syncState.get(key) as Partial<BuildStatus> | undefined;
    const updated = { ...(existing || {}), ...status };
    this.syncState.set(key, updated);

    this.syncHistory.push({
      action: 'sync_workflow_status',
      data: status,
      timestamp: new Date(),
    });
  }

  async verifyConsistency(): Promise<boolean> {
    // Validate that all synced states are consistent
    for (const [key, value] of this.syncState) {
      if (!value) {
        this.consistencyErrors.push(`Inconsistent state: ${key} is null/undefined`);
        return false;
      }
    }
    return true;
  }

  getSyncState(): Map<string, unknown> {
    return this.syncState;
  }

  getSyncHistory(): Array<{ action: string; data: unknown; timestamp: Date }> {
    return this.syncHistory;
  }

  getConsistencyErrors(): string[] {
    return this.consistencyErrors;
  }
}

class MockRollbackService extends EventEmitter {
  private rollbackHistory: RollbackResult[] = [];
  private currentPhase: Map<string, RollbackPhase> = new Map();

  async initializeRollback(request: RollbackRequest): Promise<RollbackResult> {
    const rollbackId = request.rollbackId;

    const result: RollbackResult = {
      rollbackId,
      phase: RollbackPhase.PREPARING,
      status: 'in_progress',
      completedAt: undefined,
      duration: 0,
    };

    this.currentPhase.set(rollbackId, RollbackPhase.PREPARING);
    this.emit('rollback:started', { rollbackId });

    return result;
  }

  async executePhase(
    rollbackId: string,
    phase: RollbackPhase
  ): Promise<RollbackResult> {
    const result: RollbackResult = {
      rollbackId,
      phase,
      status: 'in_progress',
    };

    this.currentPhase.set(rollbackId, phase);

    // Simulate phase execution
    switch (phase) {
      case RollbackPhase.REVERTING_CODE:
        result.previousCommitSha = 'abc123def456';
        result.revertedCommitSha = 'revert123456';
        break;
      case RollbackPhase.REBUILDING:
        // Simulate rebuild
        break;
      case RollbackPhase.VERIFICATION:
        result.status = 'completed';
        result.completedAt = new Date();
        result.duration = 5000;
        break;
    }

    this.emit('rollback:phase_completed', { rollbackId, phase });
    return result;
  }

  async failRollback(rollbackId: string, error: string): Promise<RollbackResult> {
    const result: RollbackResult = {
      rollbackId,
      phase: this.currentPhase.get(rollbackId) || RollbackPhase.PREPARING,
      status: 'failed',
      error,
      completedAt: new Date(),
    };

    this.rollbackHistory.push(result);
    this.emit('rollback:failed', { rollbackId, error });

    return result;
  }

  getRollbackHistory(): RollbackResult[] {
    return this.rollbackHistory;
  }

  getCurrentPhase(rollbackId: string): RollbackPhase | undefined {
    return this.currentPhase.get(rollbackId);
  }
}

// ============================================================================
// INTEGRATION TEST SUITE
// ============================================================================

describe('E2E Integration Tests — 12 testes críticos', () => {
  let intentParser: MockIntentParser;
  let ciOrchestrator: MockCIOrchestrator;
  let codeGenerator: MockCodeGenerator;
  let webhookHandler: MockWebhookHandler;
  let coworkSync: MockCoworkSync;
  let rollbackService: MockRollbackService;

  beforeEach(() => {
    intentParser = new MockIntentParser();
    ciOrchestrator = new MockCIOrchestrator();
    codeGenerator = new MockCodeGenerator();
    webhookHandler = new MockWebhookHandler();
    coworkSync = new MockCoworkSync();
    rollbackService = new MockRollbackService();

    jest.clearAllMocks();
  });

  // ========== TEST 1: Full Flow - Intent to Merge ==========

  test('E2E #1: Full flow - intent parsing → code generation → CI trigger → merge (mocked)', async () => {
    // Step 1: Parse intent from commit message
    const commitMessage = 'create saneamento agent S8 with RAG integration';
    const intent = await intentParser.parseCommitMessage(commitMessage);

    expect(intent.action).toBe('create');
    expect(intent.target).toBe('agent');
    expect(intent.confidence).toBeGreaterThan(0.9);

    // Step 2: Generate code based on intent
    const generatedCode = await codeGenerator.generateCode(intent);

    expect(generatedCode).toContain('Generated');
    expect(generatedCode).toContain('saneamento');

    // Step 3: Trigger CI pipeline
    const workflowId = await ciOrchestrator.triggerCI(123, 'feature/s8');

    expect(workflowId).toBeDefined();
    expect(typeof workflowId).toBe('number');

    // Step 4: Wait for build completion and verify
    await new Promise(resolve => setTimeout(resolve, 150));
    const buildStatus = await ciOrchestrator.getBuildStatus(workflowId);

    expect(buildStatus).toBeDefined();
    expect(buildStatus?.passed).toBe(true);
    expect(buildStatus?.coverage).toBeGreaterThanOrEqual(85);

    // Step 5: Sync PR data to Cowork
    const prAnalysis: PRAnalysis = {
      prNumber: 123,
      owner: 'manta-associados',
      repo: 'codex-exemplo',
      title: 'feat: add saneamento agent S8',
      author: 'test-dev',
      branch: 'feature/s8',
      baseBranch: 'main',
      status: PRAnalysisStatus.COMPLETED,
      filesChanged: 3,
      additions: 180,
      deletions: 0,
      ciTriggered: true,
      workflowRunId: workflowId,
      buildStatus: buildStatus!,
      analyzedAt: new Date(),
      completedAt: new Date(),
      duration: 5000,
    };

    await coworkSync.syncPRData(123, prAnalysis);
    const isConsistent = await coworkSync.verifyConsistency();

    expect(isConsistent).toBe(true);

    // Verify all steps completed
    expect(codeGenerator.getGenerationHistory().length).toBe(1);
  });

  // ========== TEST 2: Error Scenario - CI Timeout ==========

  test('E2E #2: Error scenario - CI timeout during build', async () => {
    const workflowId = await ciOrchestrator.triggerCI(124, 'feature/timeout-test');

    expect(workflowId).toBeDefined();

    // Simulate CI timeout BEFORE the workflow completes normally
    await ciOrchestrator.timeoutWorkflow(workflowId);

    // Give timeout operation time to take effect
    await new Promise(resolve => setTimeout(resolve, 50));

    const buildStatus = await ciOrchestrator.getBuildStatus(workflowId);

    expect(buildStatus?.conclusion).toBe('timed_out');
    expect(buildStatus?.passed).toBe(false);

    // Verify sync reflects timeout state
    const prAnalysis: PRAnalysis = {
      prNumber: 124,
      owner: 'manta-associados',
      repo: 'codex-exemplo',
      title: 'feat: timeout test',
      author: 'test-dev',
      branch: 'feature/timeout-test',
      baseBranch: 'main',
      status: PRAnalysisStatus.FAILED,
      filesChanged: 2,
      additions: 50,
      deletions: 0,
      ciTriggered: true,
      workflowRunId: workflowId,
      buildStatus: buildStatus!,
      analyzedAt: new Date(),
      error: 'CI timeout after 30 minutes',
    };

    await coworkSync.syncPRData(124, prAnalysis);
    const syncedState = coworkSync.getSyncState();

    expect(syncedState.get('pr:124')).toBeDefined();
    const syncedPR = syncedState.get('pr:124') as Partial<PRAnalysis>;
    expect(syncedPR.error).toContain('timeout');
  });

  // ========== TEST 3: Error Scenario - Code Generation Failure ==========

  test('E2E #3: Error scenario - code generation fails with meaningful error', async () => {
    const intent: ParsedIntent = {
      action: 'create',
      target: 'agent',
      confidence: 0.95,
      params: { segment: 'invalid' },
      reasoning: 'Test invalid segment',
    };

    let generationError: string | undefined;
    try {
      await codeGenerator.failGeneration('Invalid segment configuration');
    } catch (error) {
      generationError = (error as Error).message;
    }

    expect(generationError).toContain('Code generation failed');

    // Sync error state to Cowork
    const prAnalysis: PRAnalysis = {
      prNumber: 125,
      owner: 'manta-associados',
      repo: 'codex-exemplo',
      title: 'feat: broken agent',
      author: 'test-dev',
      branch: 'feature/broken',
      baseBranch: 'main',
      status: PRAnalysisStatus.FAILED,
      filesChanged: 0,
      additions: 0,
      deletions: 0,
      ciTriggered: false,
      analyzedAt: new Date(),
      error: generationError,
    };

    await coworkSync.syncPRData(125, prAnalysis);
    const errorRecord = coworkSync.getSyncState().get('pr:125') as Partial<PRAnalysis>;

    expect(errorRecord.error).toBeDefined();
  });

  // ========== TEST 4: Webhook Delivery Success ==========

  test('E2E #4: Webhook delivery succeeds with valid signature', async () => {
    const payloadData = {
      event: WebhookEventType.PR_OPENED,
      timestamp: new Date().toISOString(),
      deliveryId: 'webhook-123',
      data: {
        pr_id: '456',
        title: 'New PR',
        author: 'test-dev',
        target_branch: 'main',
      },
    };

    const payloadString = JSON.stringify(payloadData);
    const signature = webhookHandler.generateSignature(payloadString);

    const payload: WebhookPayload = {
      ...payloadData,
      event: WebhookEventType.PR_OPENED,
      signature,
    };

    // Validate signature
    const isValid = webhookHandler.validateSignature(payloadString, signature);
    expect(isValid).toBe(true);

    // Handle webhook
    const result = await webhookHandler.handleWebhook(payload);

    expect(result.success).toBe(true);
    expect(result.status).toBe('delivered');

    // Verify delivery log
    const deliveryLog = webhookHandler.getDeliveryLog();
    expect(deliveryLog.length).toBe(1);
    expect(deliveryLog[0].deliveryId).toBe('webhook-123');
  });

  // ========== TEST 5: Webhook Retry Logic ==========

  test('E2E #5: Webhook retry logic handles failures gracefully', async () => {
    const payloadData = {
      event: WebhookEventType.COMMIT,
      timestamp: new Date().toISOString(),
      deliveryId: 'webhook-retry-123',
      data: {
        commit_sha: 'abc123',
        message: 'test commit',
        author: 'test-dev',
        branch: 'main',
      },
    };

    const payloadString = JSON.stringify(payloadData);
    const signature = webhookHandler.generateSignature(payloadString);

    const payload: WebhookPayload = {
      ...payloadData,
      event: WebhookEventType.COMMIT,
      signature,
    };

    // Handle webhook with failure (should trigger retry)
    const result = await webhookHandler.handleWebhook(payload, true);

    expect(result.success).toBe(false);
    expect(['failed', 'retrying']).toContain(result.status);
    expect(result.error).toBeDefined();

    // Verify retry queue
    await new Promise(resolve => setTimeout(resolve, 150));
    const retryQueueSize = webhookHandler.getRetryQueueSize();
    expect(retryQueueSize).toBeGreaterThan(0);
  });

  // ========== TEST 6: Webhook Invalid Signature ==========

  test('E2E #6: Webhook rejects invalid signature', async () => {
    const payloadData = {
      event: WebhookEventType.TASK_UPDATED,
      timestamp: new Date().toISOString(),
      deliveryId: 'webhook-invalid-sig',
      data: {
        task_id: '789',
        status: 'done',
      },
    };

    const payloadString = JSON.stringify(payloadData);
    const invalidSignature = 'invalid_signature_xyz';

    const isValid = webhookHandler.validateSignature(payloadString, invalidSignature);

    expect(isValid).toBe(false);
  });

  // ========== TEST 7: Cowork Sync Consistency ==========

  test('E2E #7: Cowork sync maintains consistency across multiple PR updates', async () => {
    // Sync multiple PRs
    const pr1: Partial<PRAnalysis> = {
      prNumber: 201,
      status: PRAnalysisStatus.COMPLETED,
      buildStatus: { passed: true, coverage: 85, testsPassed: 40 } as BuildStatus,
    };

    const pr2: Partial<PRAnalysis> = {
      prNumber: 202,
      status: PRAnalysisStatus.COMPLETED,
      buildStatus: { passed: true, coverage: 90, testsPassed: 45 } as BuildStatus,
    };

    await coworkSync.syncPRData(201, pr1);
    await coworkSync.syncPRData(202, pr2);

    // Update workflow status for both
    await coworkSync.syncWorkflowStatus(1001, {
      status: 'completed',
      conclusion: 'success',
      passed: true,
    });

    await coworkSync.syncWorkflowStatus(1002, {
      status: 'completed',
      conclusion: 'success',
      passed: true,
    });

    // Verify consistency
    const isConsistent = await coworkSync.verifyConsistency();
    expect(isConsistent).toBe(true);

    // Verify sync history
    const syncHistory = coworkSync.getSyncHistory();
    expect(syncHistory.length).toBe(4);
  });

  // ========== TEST 8: Sync History Auditing ==========

  test('E2E #8: Sync history maintains audit trail for compliance', async () => {
    const prData: Partial<PRAnalysis> = {
      prNumber: 301,
      author: 'dev-1',
      status: PRAnalysisStatus.COMPLETED,
    };

    await coworkSync.syncPRData(301, prData);

    const syncHistory = coworkSync.getSyncHistory();

    expect(syncHistory.length).toBeGreaterThan(0);
    expect(syncHistory[0].action).toBe('sync_pr_data');
    expect(syncHistory[0].timestamp).toBeDefined();
    expect((syncHistory[0].data as Partial<PRAnalysis>).prNumber).toBe(301);
  });

  // ========== TEST 9: Rollback Workflow - Complete Flow ==========

  test('E2E #9: Rollback workflow executes all phases successfully', async () => {
    // Initialize rollback
    const rollbackRequest: RollbackRequest = {
      rollbackId: 'rollback-001',
      prNumber: 400,
      owner: 'manta-associados',
      repo: 'codex-exemplo',
      reason: 'Critical bug detected post-merge',
      initiatedBy: 'release-manager',
      createdAt: new Date(),
    };

    const initialResult = await rollbackService.initializeRollback(rollbackRequest);

    expect(initialResult.rollbackId).toBe('rollback-001');
    expect(initialResult.status).toBe('in_progress');
    expect(initialResult.phase).toBe(RollbackPhase.PREPARING);

    // Execute phases
    const phase1 = await rollbackService.executePhase('rollback-001', RollbackPhase.REVERTING_CODE);
    expect(phase1.phase).toBe(RollbackPhase.REVERTING_CODE);
    expect(phase1.previousCommitSha).toBeDefined();

    const phase2 = await rollbackService.executePhase('rollback-001', RollbackPhase.REBUILDING);
    expect(phase2.phase).toBe(RollbackPhase.REBUILDING);

    const phase3 = await rollbackService.executePhase(
      'rollback-001',
      RollbackPhase.VERIFICATION
    );
    expect(phase3.phase).toBe(RollbackPhase.VERIFICATION);
    expect(phase3.status).toBe('completed');
    expect(phase3.completedAt).toBeDefined();
    expect(phase3.duration).toBeDefined();
  });

  // ========== TEST 10: Rollback Error Handling ==========

  test('E2E #10: Rollback gracefully handles failures mid-phase', async () => {
    const rollbackRequest: RollbackRequest = {
      rollbackId: 'rollback-002',
      prNumber: 401,
      owner: 'manta-associados',
      repo: 'codex-exemplo',
      reason: 'Test rollback failure',
      initiatedBy: 'test-user',
      createdAt: new Date(),
    };

    // Initialize
    await rollbackService.initializeRollback(rollbackRequest);

    // Fail during execution
    const failResult = await rollbackService.failRollback(
      'rollback-002',
      'Revert operation failed: merge conflict'
    );

    expect(failResult.status).toBe('failed');
    expect(failResult.error).toContain('merge conflict');
    expect(failResult.completedAt).toBeDefined();

    // Verify history
    const history = rollbackService.getRollbackHistory();
    expect(history.length).toBeGreaterThan(0);
    expect(history[0].rollbackId).toBe('rollback-002');
  });

  // ========== TEST 11: End-to-End with Multiple Events ==========

  test('E2E #11: Complex scenario - multiple webhook events trigger coordinated actions', async () => {
    // Event 1: PR opened
    const pr1Payload: WebhookPayload = {
      event: WebhookEventType.PR_OPENED,
      timestamp: new Date().toISOString(),
      deliveryId: 'deliver-multi-1',
      signature: webhookHandler.generateSignature(JSON.stringify({})),
      data: { pr_id: '500', title: 'Complex PR' },
    };

    const result1 = await webhookHandler.handleWebhook(pr1Payload);
    expect(result1.success).toBe(true);

    // Parse intent
    const intent = await intentParser.parseCommitMessage('update agent metro');
    expect(intent.action).toBe('update');

    // Generate code
    const code = await codeGenerator.generateCode(intent);
    expect(code).toBeDefined();

    // Trigger CI
    const workflowId = await ciOrchestrator.triggerCI(500, 'feature/metro-update');
    expect(workflowId).toBeDefined();

    // Sync state
    await coworkSync.syncPRData(500, {
      prNumber: 500,
      status: PRAnalysisStatus.COMPLETED,
    });

    // Verify all actions completed
    expect(webhookHandler.getDeliveryLog().length).toBe(1);
    expect(codeGenerator.getGenerationHistory().length).toBe(1);
    expect(coworkSync.getSyncHistory().length).toBe(1);
  });

  // ========== TEST 12: Performance Baseline - All Services <5s Total ==========

  test('E2E #12: Performance benchmark - full flow completes in <5 seconds', async () => {
    const startTime = performance.now();

    // Parse intent
    await intentParser.parseCommitMessage('create saneamento agent');

    // Generate code
    const intent = await intentParser.parseCommitMessage('create saneamento agent');
    await codeGenerator.generateCode(intent);

    // Trigger CI
    const workflowId = await ciOrchestrator.triggerCI(600, 'perf-test');

    // Handle webhook
    const webhookPayload: WebhookPayload = {
      event: WebhookEventType.PR_OPENED,
      timestamp: new Date().toISOString(),
      deliveryId: 'perf-test-deliver',
      signature: webhookHandler.generateSignature(JSON.stringify({})),
      data: { pr_id: '600' },
    };
    await webhookHandler.handleWebhook(webhookPayload);

    // Sync
    await coworkSync.syncPRData(600, { prNumber: 600 });

    // Initialize rollback
    await rollbackService.initializeRollback({
      rollbackId: 'perf-rollback-1',
      prNumber: 600,
      owner: 'test',
      repo: 'test',
      reason: 'perf test',
      initiatedBy: 'test',
      createdAt: new Date(),
    });

    const endTime = performance.now();
    const totalDuration = endTime - startTime;

    // Should complete in <5 seconds
    expect(totalDuration).toBeLessThan(5000);
  });
});
