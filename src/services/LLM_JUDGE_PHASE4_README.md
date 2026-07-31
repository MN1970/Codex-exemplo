# LLM Judge Phase 4 - Decision Engine

**Version**: 2.0.0  
**Date**: 2025-02-14  
**Status**: ✅ Operational

## Overview

LLM Judge Phase 4 implements a complete intelligent decision engine for code review and PR management. It extends the basic risk classification (Phase 1) with comprehensive code evaluation, quality scoring, and intelligent merge decisions backed by detailed audit trails.

## New Features in Phase 4

### 1. Code Evaluation (`evaluateCode`)

Perform detailed analysis of code with support for external reviews:

```typescript
const evaluation = await judge.evaluateCode(code, reviews);
```

**Returns**: `Evaluation` interface with:
- Overall score (0-100)
- Detailed issue detection (critical, major, minor)
- Security and performance risk analysis
- Testability, maintainability, and documentation scores
- Complete audit trail of the analysis

### 2. Merge Decision Engine (`decideMergeability`)

Make intelligent merge decisions based on comprehensive analysis:

```typescript
const decision = await judge.decideMergeability(prData);
```

**Returns**: `MergeDecision` with:
- Decision type: `approve`, `request-changes`, `comment`, `block`
- Confidence level: `very-high`, `high`, `moderate`, `low`, `very-low`
- Detailed reasoning with multiple reasons
- Blockers, warnings, and suggestions
- Audit trail of decision process

### 3. Quality Scoring (`scoreQuality`)

Comprehensive quality assessment across multiple dimensions:

```typescript
const qualityScore = await judge.scoreQuality(code);
```

**Returns**: `QualityScore` with:
- Overall score (0-100) with letter grade (A-F)
- Individual dimension scores:
  - Code Quality (0-100)
  - Test Coverage (0-100)
  - Documentation (0-100)
  - Security (0-100)
  - Performance (0-100)
  - Maintainability (0-100)
- Breakdown with strengths, weaknesses, recommendations
- Audit trail

### 4. Decision Explanation (`explainDecision`)

Generate natural language explanations for decisions:

```typescript
const explanation = await judge.explainDecision(evaluation);
```

**Returns**: Human-readable explanation of the evaluation and recommendations.

## Core Concepts

### Confidence Levels

Decisions include explicit confidence levels:

- **Very High (0.9-1.0)**: Analysis is very clear and certain
- **High (0.75-0.9)**: Clear analysis with high certainty
- **Moderate (0.5-0.75)**: Confident but with some uncertainty
- **Low (0.3-0.5)**: Uncertain, requires human review
- **Very Low (<0.3)**: Very uncertain, strongly recommend blocking

### Issue Severity Classification

Issues are classified by severity:

- **Critical**: Must be fixed before merge, potential security/data loss
- **Major**: Should be fixed, significant impact
- **Minor**: Nice to have, low impact
- **Info**: Informational only

### Audit Trail

Every decision includes a complete audit trail:

```typescript
interface AuditTrailEntry {
  timestamp: Date;           // When this happened
  action: string;            // What action was taken
  details: Record<string, unknown>; // Detailed information
  confidence?: number;       // Confidence in this step
  model?: string;            // Which model processed it
}
```

## Usage Examples

### Basic Code Evaluation

```typescript
import { createLLMJudge } from './services/llm-judge';

const judge = createLLMJudge();

const code = `
export function calculateTotal(items: any[]) {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    total += items[i].price * items[i].quantity;
  }
  return total;
}`;

const evaluation = await judge.evaluateCode(code);

console.log(`Score: ${evaluation.overallScore}/100`);
console.log(`Critical Issues: ${evaluation.criticalIssues.length}`);
console.log(`Security Risks: ${evaluation.securityRisks.length}`);
```

### Code Evaluation with Reviews

```typescript
import { createLLMJudge } from './services/llm-judge';

const judge = createLLMJudge();

const reviews = [
  {
    reviewer: 'alice@company.com',
    content: 'Missing null check on items',
    timestamp: new Date(),
    severity: 'major' as const,
  },
  {
    reviewer: 'bob@company.com',
    content: 'No unit tests provided',
    timestamp: new Date(),
    severity: 'minor' as const,
  },
];

const evaluation = await judge.evaluateCode(code, reviews);

// Evaluation includes feedback from previous reviews
evaluation.reviews.forEach(review => {
  console.log(`${review.reviewer}: ${review.content}`);
});
```

### Merge Decision with Confidence

```typescript
const prData = {
  prNumber: 123,
  owner: 'mycompany',
  repo: 'myapp',
  title: 'feat: add new feature',
  author: 'developer',
  branch: 'feat/new-feature',
  baseBranch: 'main',
  filesChanged: 5,
  additions: 150,
  deletions: 50,
  changedFiles: [/* ... */],
  commits: [/* ... */],
  ciPassed: true,
  testsPassed: 45,
  testsFailed: 0,
};

const decision = await judge.decideMergeability(prData);

if (decision.decision === 'approve') {
  // Safe to merge
  console.log(`✅ Can merge with ${decision.confidence * 100}% confidence`);
  
  if (decision.warnings) {
    console.log('⚠️ But note these warnings:');
    decision.warnings.forEach(warning => console.log(`  - ${warning}`));
  }
} else if (decision.decision === 'request-changes') {
  console.log('🔄 Changes requested');
  decision.reasons.forEach(reason => console.log(`  - ${reason}`));
} else if (decision.decision === 'block') {
  console.log('🛑 PR blocked');
  decision.blockers?.forEach(blocker => console.log(`  - ${blocker}`));
}
```

### Quality Scoring

```typescript
const qualityScore = await judge.scoreQuality(code);

console.log(`Grade: ${qualityScore.grade}`);
console.log(`Score: ${qualityScore.overall}/100`);

// Show detailed breakdown
console.log('\nDimensions:');
console.log(`  Code Quality:     ${qualityScore.codeQuality}/100`);
console.log(`  Test Coverage:    ${qualityScore.testCoverage}/100`);
console.log(`  Documentation:    ${qualityScore.documentation}/100`);
console.log(`  Security:         ${qualityScore.security}/100`);
console.log(`  Performance:      ${qualityScore.performance}/100`);
console.log(`  Maintainability:  ${qualityScore.maintainability}/100`);

// Show recommendations
qualityScore.breakdown.recommendations.forEach(rec => {
  console.log(`  💡 ${rec}`);
});
```

### Decision Explanation

```typescript
const evaluation = await judge.evaluateCode(code);
const explanation = await judge.explainDecision(evaluation);

console.log('Detailed Explanation:');
console.log(explanation);
```

### Complete Workflow

```typescript
// Step 1: Evaluate code
const evaluation = await judge.evaluateCode(code, reviews);
console.log(`Code Quality: ${evaluation.overallScore}/100`);

// Step 2: Score quality
const qualityScore = await judge.scoreQuality(code);
console.log(`Grade: ${qualityScore.grade}`);

// Step 3: Explain issues
const explanation = await judge.explainDecision(evaluation);
console.log('Issues:', explanation);

// Step 4: Decide merge
const decision = await judge.decideMergeability(prData);
console.log(`Can merge: ${decision.decision}`);
```

## Advanced Configuration

### Custom Model Selection

```typescript
import { createLLMJudge } from './services/llm-judge';

// Use Sonnet for deeper analysis
const judge = createLLMJudge({
  model: 'claude-3-5-sonnet-20241022', // Default: haiku
  maxTokens: 4096,
  minConfidenceThreshold: 0.75,
});
```

### Confidence Thresholds

```typescript
const judge = createLLMJudge({
  minConfidenceThreshold: 0.8, // Require 80% confidence
});

const decision = await judge.decideMergeability(prData);

// If confidence below threshold, will recommend review
if (decision.confidenceLevel === 'very-low') {
  console.log('Low confidence - human review recommended');
}
```

## Type Definitions

### Evaluation

```typescript
interface Evaluation {
  code: string;
  reviews: CodeReview[];
  overallScore: number; // 0-100
  issues: CodeIssue[];
  criticalIssues: CodeIssue[];
  minorIssues: CodeIssue[];
  improvements: string[];
  securityRisks: SecurityRisk[];
  performanceRisks: PerformanceRisk[];
  testability: TestabilityScore;
  maintainability: MaintainabilityScore;
  documentation: DocumentationScore;
  auditTrail: AuditTrailEntry[];
  evaluatedAt: Date;
  model: string;
  promptTokens?: number;
  completionTokens?: number;
}
```

### MergeDecision

```typescript
interface MergeDecision {
  decision: 'approve' | 'request-changes' | 'comment' | 'block';
  confidenceLevel: 'very-high' | 'high' | 'moderate' | 'low' | 'very-low';
  confidence: number; // 0.0-1.0
  reasoning: string;
  reasons: string[];
  blockers?: string[];
  warnings?: string[];
  suggestions?: string[];
  ciStatus?: boolean;
  reviewsApproved?: number;
  reviewsRequested?: number;
  auditTrail: AuditTrailEntry[];
  decidedAt: Date;
  model: string;
}
```

### QualityScore

```typescript
interface QualityScore {
  overall: number; // 0-100
  codeQuality: number; // 0-100
  testCoverage: number; // 0-100
  documentation: number; // 0-100
  security: number; // 0-100
  performance: number; // 0-100
  maintainability: number; // 0-100
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  breakdown: {
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
  };
  auditTrail: AuditTrailEntry[];
  scoredAt: Date;
  model: string;
}
```

## Best Practices

### 1. Always Check Confidence Levels

```typescript
const decision = await judge.decideMergeability(prData);

if (decision.confidence < 0.7) {
  // Confidence too low - require human review
  console.log('Low confidence decision - manual review needed');
  console.log(`Confidence: ${decision.confidence}`);
}
```

### 2. Review Audit Trails

```typescript
const evaluation = await judge.evaluateCode(code);

// Audit trail shows exactly what was analyzed
evaluation.auditTrail.forEach(entry => {
  console.log(`[${entry.timestamp.toISOString()}] ${entry.action}`);
  console.log(`  Details: ${JSON.stringify(entry.details)}`);
});
```

### 3. Combine Signals

```typescript
// Don't rely on a single metric
const evaluation = await judge.evaluateCode(code);
const decision = await judge.decideMergeability(prData);

const shouldMerge = 
  decision.decision === 'approve' &&
  decision.confidence > 0.8 &&
  evaluation.criticalIssues.length === 0;
```

### 4. Document Decisions

```typescript
const decision = await judge.decideMergeability(prData);

// Save decision for audit
const auditLog = {
  prNumber: prData.prNumber,
  decision: decision.decision,
  confidence: decision.confidence,
  reasoning: decision.reasoning,
  timestamp: new Date(),
  auditTrail: decision.auditTrail,
};

// Store for later review
await database.saveMergeDecision(auditLog);
```

## Integration Examples

### With GitHub Actions

```typescript
// In a GitHub Actions workflow
import { createLLMJudge } from './services/llm-judge';

const judge = createLLMJudge({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const prData = {
  prNumber: context.issue.number,
  owner: context.repo.owner,
  repo: context.repo.repo,
  // ... other PR data
};

const decision = await judge.decideMergeability(prData);

// Comment on PR with decision
core.notice(`Decision: ${decision.decision}`);
core.notice(`Confidence: ${decision.confidence}`);
```

### With Express API

```typescript
import express from 'express';
import { createLLMJudge } from './services/llm-judge';

const judge = createLLMJudge();
const app = express();

app.post('/api/review', async (req, res) => {
  const { code, reviews } = req.body;
  
  const evaluation = await judge.evaluateCode(code, reviews);
  const qualityScore = await judge.scoreQuality(code);
  
  res.json({
    evaluation,
    qualityScore,
    auditTrail: evaluation.auditTrail,
  });
});

app.post('/api/merge-decision', async (req, res) => {
  const { prData } = req.body;
  
  const decision = await judge.decideMergeability(prData);
  
  res.json(decision);
});
```

## Performance Considerations

### Token Usage

Be aware of token usage when processing large code bases:

```typescript
const evaluation = await judge.evaluateCode(code);

// Check token usage
console.log(`Tokens used:`);
console.log(`  Input: ${evaluation.promptTokens}`);
console.log(`  Output: ${evaluation.completionTokens}`);
```

### Batch Processing

For multiple PRs, process efficiently:

```typescript
const prs = [pr1, pr2, pr3, /* ... */];

// Sequential (safer for rate limits)
for (const pr of prs) {
  const decision = await judge.decideMergeability(pr);
  console.log(`PR #${pr.prNumber}: ${decision.decision}`);
}

// Or with concurrency control
const results = await Promise.all(
  prs.map(pr => judge.decideMergeability(pr))
);
```

## Monitoring and Metrics

### Decision Statistics

```typescript
const decisions = await Promise.all(
  prs.map(pr => judge.decideMergeability(pr))
);

const stats = {
  total: decisions.length,
  approved: decisions.filter(d => d.decision === 'approve').length,
  requestChanges: decisions.filter(d => d.decision === 'request-changes').length,
  blocked: decisions.filter(d => d.decision === 'block').length,
  averageConfidence: decisions.reduce((sum, d) => sum + d.confidence, 0) / decisions.length,
};

console.log('Decision Statistics:', stats);
```

### Quality Trends

```typescript
const scores = await Promise.all(
  codeFiles.map(code => judge.scoreQuality(code))
);

const trends = {
  averageGrade: scores.reduce((a, b) => a + b.overall, 0) / scores.length,
  gradeDistribution: {
    A: scores.filter(s => s.grade === 'A').length,
    B: scores.filter(s => s.grade === 'B').length,
    C: scores.filter(s => s.grade === 'C').length,
    D: scores.filter(s => s.grade === 'D').length,
    F: scores.filter(s => s.grade === 'F').length,
  },
};

console.log('Quality Trends:', trends);
```

## Troubleshooting

### Low Confidence Scores

If getting consistently low confidence:

1. Provide more context in reviews
2. Include CI/test information
3. Use a more powerful model (Sonnet instead of Haiku)
4. Check if PRs are too ambiguous

### Incorrect Decisions

If decisions seem wrong:

1. Check the audit trail for details
2. Review the reasoning provided
3. Provide external reviews for context
4. Check confidence levels

### High Token Usage

Reduce token usage by:

1. Using shorter code snippets
2. Limiting review count
3. Using Haiku model for pre-screening
4. Processing in batches

## Help & Support

- **Issues**: Report via GitHub Issues
- **Questions**: Check examples in `src/examples/llm-judge-phase4-examples.ts`
- **Documentation**: See `LLM_JUDGE_README.md` for Phase 1-3

## Version History

- **v2.0.0** (2025-02-14): Phase 4 - Complete Decision Engine
  - Added evaluateCode method
  - Added decideMergeability method
  - Added scoreQuality method
  - Added explainDecision method
  - Added comprehensive audit trails
  - Added confidence level tracking
  - Added issue severity classification

- **v1.0.0** (2024-01-XX): Phase 1 - Basic Risk Classification
  - PR risk classification
  - Confidence scoring
  - Dangerous pattern detection

---

**Maintained by**: Manta Associados - Infrastructure AI Team  
**Last Updated**: 2025-02-14
