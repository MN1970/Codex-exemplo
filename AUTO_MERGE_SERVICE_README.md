# AutoMerge Service - Advanced PR Merge Automation

**Version:** 2.0.0  
**Phase:** 4 - Merge Automation with Distributed Locking

## Overview

The `AutoMerge` service provides intelligent, production-ready PR merge automation with distributed locking, transaction safety, and comprehensive quality criteria checking. This service complements the existing `AutoMergeController` with advanced features for complex merge scenarios.

### Key Features

- **Quality Criteria Checking** - Verifies CI, approvals, branch protection, and more
- **Intelligent Conflict Detection** - Identifies multiple types of merge conflicts
- **Custom Merge Strategies** - Supports merge, squash, rebase, cherry-pick, and fast-forward
- **Merge Scheduling** - Schedule PRs to merge at specific dates/times
- **Distributed Locking** - Prevents concurrent merge conflicts with lock manager
- **Transaction Safety** - Full audit trail and rollback capability
- **Comprehensive Metrics** - Tracks success rates, strategies, and blocking reasons
- **Audit Trail** - Complete history of all merge operations

## Installation & Setup

### 1. Import the Service

```typescript
import { createAutoMerge, AutoMerge } from '@/services';
import type { AutoMergeServiceConfig, MergeResult, Requirement } from '@/services';
```

### 2. Initialize

```typescript
const autoMerge = createAutoMerge({
  githubToken: process.env.GITHUB_TOKEN,
  owner: 'my-org',
  repo: 'my-repo',
  requireCIPassed: true,
  requiredApprovals: 1,
  allowMergingWithConflicts: false,
  defaultStrategy: 'squash',
  enableScheduling: true,
  trackMetrics: true,
  lockTtl: 60000, // 1 minute
});
```

## Configuration

### AutoMergeServiceConfig Options

```typescript
interface AutoMergeServiceConfig {
  // Required
  githubToken: string;        // GitHub API token
  owner: string;              // Repository owner
  repo: string;               // Repository name

  // Quality Requirements
  requireCIPassed?: boolean;              // Default: true
  requiredApprovals?: number;             // Default: 1
  allowConflicts?: boolean;               // Default: false
  allowMergingWithConflicts?: boolean;    // Default: false

  // Distributed Locking
  lockProvider?: 'memory' | 'redis' | 'supabase';  // Default: 'memory'
  lockTtl?: number;           // Lock timeout in ms, Default: 60000
  lockRetryAttempts?: number; // Default: 3
  lockRetryDelay?: number;    // Default: 1000

  // Merge Defaults
  defaultStrategy?: MergeStrategy;        // Default: 'squash'
  commitMessageTemplate?: string;         // Default: 'Merge PR #{prNumber}: {title}'

  // Scheduling
  enableScheduling?: boolean;             // Default: true
  schedulerIntervalMs?: number;           // Default: 60000

  // Metrics & Storage
  trackMetrics?: boolean;                 // Default: true
  metricsStorageUrl?: string;             // Optional Supabase URL

  // API
  apiBaseUrl?: string;                    // Default: 'https://api.github.com'
  requestTimeout?: number;                // Default: 30000
}
```

## Core Methods

### 1. canMerge(pr: { number: number; draft?: boolean }): Promise<boolean>

Quickly check if a PR can be merged without detailed analysis.

```typescript
const canMerge = await autoMerge.canMerge({ number: 123 });

if (canMerge) {
  console.log('PR is ready to merge');
} else {
  console.log('PR has blocking issues');
}
```

**Returns:** `true` if all requirements are met, `false` otherwise.

### 2. checkRequirements(pr: { number: number; draft?: boolean }): Promise<Requirement[]>

Perform comprehensive quality checks on a PR.

```typescript
const requirements = await autoMerge.checkRequirements({ number: 123 });

requirements.forEach((req) => {
  console.log(`${req.type}: ${req.met ? 'PASS' : 'FAIL'}`);
  console.log(`  Description: ${req.description}`);
  if (req.currentValue) {
    console.log(`  Current: ${req.currentValue}`);
  }
});
```

**Checks Performed:**
- `not_draft` - PR is not in draft mode
- `status_checks` - All required status checks passed
- `ci_passed` - CI pipeline passed
- `approvals_met` - Required review approvals met
- `no_conflicts` - No merge conflicts detected
- `branch_up_to_date` - Branch is up to date with base
- `branch_protection` - Complies with branch protection rules
- `no_wip_marker` - No WIP marker in title

**Result Structure:**

```typescript
interface Requirement {
  type: RequirementType;
  met: boolean;
  description: string;
  currentValue?: string;        // e.g., "2/1 approvals"
  requiredValue?: string;       // e.g., "1"
  lastCheckedAt: Date;
  checkDetails?: Record<string, any>;
}
```

### 3. getConflicts(pr: { number: number }): Promise<Conflict[]>

Detect merge conflicts and get resolution suggestions.

```typescript
const conflicts = await autoMerge.getConflicts({ number: 123 });

if (conflicts.length > 0) {
  conflicts.forEach((conflict) => {
    console.log(`${conflict.file} (${conflict.severity})`);
    console.log(`  Type: ${conflict.type}`);
    console.log(`  Resolvable: ${conflict.resolvable}`);
    if (conflict.suggestedResolution) {
      console.log(`  Solution: ${conflict.suggestedResolution}`);
    }
  });
}
```

**Conflict Types:**
- `content` - Text content conflict
- `delete-modify` - One side deleted, other modified
- `add-add` - Both sides added same file
- `rename-rename` - Both sides renamed file
- `structural` - Project structure conflict

**Result Structure:**

```typescript
interface Conflict {
  file: string;
  type: ConflictType;
  description: string;
  resolvable: boolean;
  suggestedResolution?: string;
  lineRange?: { start: number; end: number };
  severity: 'low' | 'medium' | 'high';
}
```

### 4. merge(prNumber: number, strategy?: MergeStrategy): Promise<MergeResult>

Execute a merge with safety checks and locking.

```typescript
const result = await autoMerge.merge(123, 'squash');

if (result.success) {
  console.log(`Merged! Commit: ${result.mergeCommitSha}`);
  console.log(`Duration: ${result.duration}ms`);
} else {
  console.log(`Merge blocked: ${result.error?.code}`);
  console.log(`Message: ${result.error?.message}`);
  console.log(`Recoverable: ${result.error?.recoverable}`);
}
```

**Merge Strategies:**
- `merge` - Create merge commit
- `squash` - Squash commits into one
- `rebase` - Rebase onto base branch
- `cherry-pick` - Cherry-pick commits
- `fast-forward` - Only allow fast-forward merge

**Merge Process:**
1. Acquire distributed lock (with retries)
2. Check all quality requirements
3. Detect merge conflicts
4. Fetch PR data
5. Perform merge operation
6. Release lock
7. Record metrics and audit trail

**Result Structure:**

```typescript
interface MergeResult {
  success: boolean;
  prNumber: number;
  strategy: MergeStrategy;
  mergeCommitSha?: string;
  message: string;
  timestamp: Date;
  duration: number;              // milliseconds
  conflictsResolved?: number;
  transactionId: string;
  auditLog: AuditLogEntry[];
  error?: {
    code: string;
    message: string;
    recoverable: boolean;
  };
}
```

### 5. scheduleMerge(prNumber: number, scheduledFor: Date, strategy?: MergeStrategy): Promise<ScheduleResult>

Schedule a PR to merge at a specific time.

```typescript
// Schedule merge for 1 hour from now
const scheduledFor = new Date(Date.now() + 3600000);
const result = await autoMerge.scheduleMerge(123, scheduledFor, 'squash');

if (result.success) {
  console.log(`Scheduled! ID: ${result.scheduleId}`);
  console.log(`Will execute at: ${result.willExecuteAt}`);
} else {
  console.log(`Schedule failed: ${result.message}`);
}
```

**Features:**
- Automatic execution at scheduled time
- Automatic retry on failure
- Can be cancelled before execution
- Full audit trail of execution

**Result Structure:**

```typescript
interface ScheduleResult {
  success: boolean;
  scheduleId: string;
  prNumber: number;
  scheduledFor: Date;
  strategy: MergeStrategy;
  status: ScheduleStatus;
  message: string;
  willExecuteAt?: Date;
}
```

### 6. getMetrics(): MergeMetrics

Get comprehensive merge operation metrics.

```typescript
const metrics = autoMerge.getMetrics();

console.log(`Total Merges: ${metrics.totalMerges}`);
console.log(`Success Rate: ${metrics.successRate.toFixed(2)}%`);
console.log(`Avg Duration: ${metrics.averageDuration.toFixed(0)}ms`);
console.log(`Conflict Rate: ${metrics.conflictRate.toFixed(2)}%`);

// Strategy usage
Object.entries(metrics.mergeStrategiesUsed).forEach(([strategy, count]) => {
  if (count > 0) {
    console.log(`  ${strategy}: ${count}`);
  }
});

// Blocking reasons
Object.entries(metrics.blockedByRequirement).forEach(([requirement, count]) => {
  if (count > 0) {
    console.log(`  Blocked by ${requirement}: ${count}`);
  }
});
```

**Metrics Structure:**

```typescript
interface MergeMetrics {
  totalMerges: number;
  successfulMerges: number;
  failedMerges: number;
  averageDuration: number;        // milliseconds
  conflictRate: number;           // percentage
  successRate: number;            // percentage
  mergeStrategiesUsed: Record<MergeStrategy, number>;
  blockedByRequirement: Record<RequirementType, number>;
  lastMergeAt?: Date;
  lockWaitTime: {
    average: number;
    max: number;
    min: number;
  };
}
```

### 7. getAuditLog(): AuditLogEntry[]

Retrieve complete audit trail.

```typescript
const auditLog = autoMerge.getAuditLog();

auditLog.forEach((entry) => {
  console.log(`[${entry.timestamp.toISOString()}] ${entry.action}`);
  console.log(`  Status: ${entry.status}`);
  console.log(`  PR: #${entry.prNumber}`);
  console.log(`  Transaction: ${entry.transactionId}`);
});
```

### 8. getTransaction(transactionId: string): Transaction | undefined

Get details of a specific merge transaction.

```typescript
const transaction = autoMerge.getTransaction('txn-123456-abc');

if (transaction) {
  console.log(`Status: ${transaction.status}`);
  console.log(`Started: ${transaction.startedAt}`);
  console.log(`Completed: ${transaction.completedAt}`);
  if (transaction.error) {
    console.log(`Error: ${transaction.error}`);
  }
}
```

### 9. getScheduledMerges(): ScheduleResult[]

List all scheduled merges.

```typescript
const scheduled = autoMerge.getScheduledMerges();

scheduled.forEach((merge) => {
  console.log(`PR #${merge.prNumber}: ${merge.status}`);
  console.log(`  Scheduled for: ${merge.scheduledFor}`);
  console.log(`  Strategy: ${merge.strategy}`);
});
```

### 10. cancelSchedule(scheduleId: string): boolean

Cancel a scheduled merge.

```typescript
const success = autoMerge.cancelSchedule('sch-123456-abc');

if (success) {
  console.log('Merge cancelled successfully');
} else {
  console.log('Schedule not found');
}
```

## Usage Examples

### Example 1: Simple Automated Merge

```typescript
import { createAutoMerge } from '@/services';

async function mergeReadyPR(prNumber: number) {
  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN!,
    owner: 'anthropics',
    repo: 'claude-code',
    requireCIPassed: true,
    requiredApprovals: 1,
    defaultStrategy: 'squash',
  });

  const canMerge = await autoMerge.canMerge({ number: prNumber });
  
  if (!canMerge) {
    console.log('PR has blocking issues');
    const requirements = await autoMerge.checkRequirements({ number: prNumber });
    requirements.filter(r => !r.met).forEach(r => {
      console.log(`  - ${r.type}: ${r.description}`);
    });
    return;
  }

  const result = await autoMerge.merge(prNumber);
  
  if (result.success) {
    console.log(`Successfully merged PR #${prNumber}`);
    console.log(`Commit: ${result.mergeCommitSha}`);
  } else {
    console.log(`Failed to merge: ${result.error?.message}`);
  }
}

await mergeReadyPR(123);
```

### Example 2: Scheduled Merge with Notifications

```typescript
async function scheduleMergeWithNotification(prNumber: number) {
  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN!,
    owner: 'anthropics',
    repo: 'claude-code',
    enableScheduling: true,
  });

  // Schedule for 30 minutes from now
  const scheduledFor = new Date(Date.now() + 30 * 60 * 1000);
  
  const result = await autoMerge.scheduleMerge(
    prNumber,
    scheduledFor,
    'squash'
  );

  if (result.success) {
    console.log(`PR #${prNumber} scheduled for merge at ${scheduledFor}`);
    console.log(`Schedule ID: ${result.scheduleId}`);
    
    // Can cancel later if needed
    // autoMerge.cancelSchedule(result.scheduleId);
  }
}
```

### Example 3: Conflict Detection and Analysis

```typescript
async function analyzeConflicts(prNumber: number) {
  const autoMerge = createAutoMerge({
    githubToken: process.env.GITHUB_TOKEN!,
    owner: 'anthropics',
    repo: 'claude-code',
    allowMergingWithConflicts: false,
  });

  const conflicts = await autoMerge.getConflicts({ number: prNumber });

  if (conflicts.length === 0) {
    console.log('No merge conflicts');
    return;
  }

  console.log(`Found ${conflicts.length} conflict(s):\n`);

  // Group by severity
  const bySeverity = conflicts.reduce((acc, c) => {
    if (!acc[c.severity]) acc[c.severity] = [];
    acc[c.severity].push(c);
    return acc;
  }, {} as Record<string, typeof conflicts>);

  Object.entries(bySeverity).forEach(([severity, conflictList]) => {
    console.log(`\n${severity.toUpperCase()} SEVERITY:`);
    conflictList.forEach(c => {
      console.log(`  - ${c.file} (${c.type})`);
      if (c.suggestedResolution) {
        console.log(`    Suggestion: ${c.suggestedResolution}`);
      }
    });
  });
}
```

### Example 4: Monitoring and Reporting

```typescript
async function generateMergeReport(autoMerge: AutoMerge) {
  const metrics = autoMerge.getMetrics();
  const auditLog = autoMerge.getAuditLog();

  console.log('=== MERGE AUTOMATION REPORT ===\n');

  console.log('METRICS:');
  console.log(`  Total Merges: ${metrics.totalMerges}`);
  console.log(`  Successful: ${metrics.successfulMerges}`);
  console.log(`  Failed: ${metrics.failedMerges}`);
  console.log(`  Success Rate: ${metrics.successRate.toFixed(2)}%`);
  console.log(`  Avg Duration: ${metrics.averageDuration.toFixed(0)}ms\n`);

  console.log('STRATEGIES USED:');
  Object.entries(metrics.mergeStrategiesUsed).forEach(([strategy, count]) => {
    if (count > 0) {
      console.log(`  ${strategy}: ${count} (${((count / metrics.totalMerges) * 100).toFixed(1)}%)`);
    }
  });

  console.log('\nBLOCKING REASONS:');
  const blockedMerges = Object.entries(metrics.blockedByRequirement)
    .filter(([, count]) => count > 0);

  if (blockedMerges.length === 0) {
    console.log('  None');
  } else {
    blockedMerges.forEach(([requirement, count]) => {
      console.log(`  ${requirement}: ${count}`);
    });
  }

  console.log('\nRECENT ACTIVITY:');
  const recent = auditLog.slice(-10);
  recent.forEach(entry => {
    console.log(`  [${entry.timestamp.toISOString().split('T')[1]}] ${entry.action} - ${entry.status}`);
  });
}
```

## Distributed Locking

The service uses a distributed lock manager to prevent concurrent merge conflicts.

### How It Works

1. **Lock Acquisition** - Before merge, acquires exclusive lock on PR
2. **Retries** - Automatically retries with configurable delays
3. **TTL** - Locks auto-expire to prevent deadlocks
4. **Providers** - Supports memory (default), Redis, and Supabase

### Configuration

```typescript
const autoMerge = createAutoMerge({
  // ... other config
  lockProvider: 'memory',        // 'memory' | 'redis' | 'supabase'
  lockTtl: 60000,               // 60 seconds
  lockRetryAttempts: 3,
  lockRetryDelay: 1000,         // 1 second between retries
});
```

## Transaction Safety

Every merge operation is tracked as a transaction with full audit trail.

### Transaction Flow

```
1. START TRANSACTION
   ├─ Generate unique txn ID
   ├─ Create audit entry
   └─ Record start time

2. ACQUIRE LOCK
   ├─ Request exclusive lock
   ├─ Retry if failed
   └─ Record lock acquisition

3. VERIFY REQUIREMENTS
   ├─ Check all quality criteria
   ├─ Detect conflicts
   └─ Abort if blocking issues

4. EXECUTE MERGE
   ├─ Call GitHub API
   ├─ Record merge commit SHA
   └─ Update transaction status

5. CLEANUP
   ├─ Release lock
   ├─ Persist metrics
   └─ Complete transaction
```

## Error Handling

The service provides detailed error information for handling failures.

```typescript
const result = await autoMerge.merge(123);

if (!result.success && result.error) {
  // Error codes
  switch (result.error.code) {
    case 'REQUIREMENTS_NOT_MET':
      console.log('PR does not meet merge criteria');
      break;
    case 'MERGE_CONFLICTS':
      console.log('Merge conflicts detected and not allowed');
      break;
    case 'MERGE_FAILED':
      console.log('GitHub API error during merge');
      break;
  }

  // Recoverable errors can be retried
  if (result.error.recoverable) {
    // Retry logic
    await new Promise(r => setTimeout(r, 5000));
    return autoMerge.merge(123);
  }
}
```

## Testing

Run the comprehensive test suite:

```bash
npm test -- src/services/__tests__/auto-merge-service.test.ts
```

Test coverage includes:
- Quality criteria checking
- Conflict detection
- Merge execution
- Scheduling
- Metrics tracking
- Audit trails
- Error handling
- Distributed locking
- Transaction management

## Integration with Manta Ecosystem

The AutoMerge service integrates with other Manta agents:

- **LLM Judge** - Uses quality decisions from LLMJudge
- **Code Reviewer** - Considers code review insights
- **CI Orchestrator** - Monitors CI/CD pipeline status
- **Rollback Orchestrator** - Coordinates rollback if needed

## Performance Considerations

- **Lock Contention** - For high-concurrency repos, consider Redis lock provider
- **API Rate Limiting** - GitHub API has 5000 requests/hour limit
- **Metrics Storage** - Consider Supabase for persistent metrics
- **Scheduler Overhead** - Adjust `schedulerIntervalMs` based on needs

## Troubleshooting

### Common Issues

**Lock Acquisition Timeout**
```typescript
// Increase lock TTL and retry attempts
const config = {
  lockTtl: 120000,          // 2 minutes instead of 1
  lockRetryAttempts: 5,     // 5 attempts instead of 3
  lockRetryDelay: 2000,     // 2 seconds between retries
};
```

**Merge Blocked by Requirements**
```typescript
// Get detailed requirement info
const requirements = await autoMerge.checkRequirements({ number: 123 });
const failed = requirements.filter(r => !r.met);
console.log(failed.map(r => ({
  type: r.type,
  description: r.description,
  current: r.currentValue,
  required: r.requiredValue,
  details: r.checkDetails,
})));
```

**Scheduled Merge Not Executing**
```typescript
// Verify scheduler is enabled
// Check if process is still running
// Review audit log for execution errors
const audit = autoMerge.getAuditLog();
const scheduled = audit.filter(a => a.action.includes('SCHEDULED'));
console.log(scheduled);
```

## Related Services

- [AutoMergeController](./AUTO_MERGE_README.md) - Basic auto-merge controller
- [LLMJudge](./LLM_JUDGE_README.md) - Quality decision engine
- [CodeReviewer](./CODE_REVIEWER_IMPLEMENTATION.md) - Code review service
- [CIOrchestratorService](./CI-ORCHESTRATOR-README.md) - CI/CD orchestration

## License

MIT - See LICENSE file for details

---

**Last Updated:** 2026-07-31
**Maintainer:** Manta Associados Team
