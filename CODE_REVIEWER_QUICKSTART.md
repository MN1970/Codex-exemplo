# Code Reviewer Service — Quick Start Guide

## Installation & Import

```typescript
import {
  CodeReviewer,
  createCodeReviewer,
  reviewCodeFast,
  reviewCodeDeep,
  analyzeSecurity,
  analyzePerformance,
  suggestRefactors,
} from "./services"
```

## 5-Minute Usage

### 1. Quick Review (Haiku - 8-15s)

```typescript
const review = await reviewCodeFast(`
  const sql = \`SELECT * FROM users WHERE id = \${userId}\`;
  db.query(sql);
`)

console.log(`Score: ${review.overallScore}/100`)
console.log(`Issues: ${review.securityIssues.length}`)
console.log(`Summary: ${review.summary}`)
```

### 2. Deep Review (Opus - 20-40s)

```typescript
const review = await reviewCodeDeep(code, {
  filepath: "src/auth.ts",
  language: "typescript",
})

// Access all findings
console.log(`Security: ${review.improvements.security}/100`)
console.log(`Performance: ${review.improvements.performance}/100`)
console.log(`Recommendations: ${review.recommendations}`)
```

### 3. Security Only

```typescript
const issues = await analyzeSecurity(code)

for (const issue of issues) {
  if (issue.severity === "critical") {
    console.log(`[CRITICAL] ${issue.type}`)
    console.log(`CWE: ${issue.cweId}`)
    console.log(`Fix: ${issue.remediation}`)
  }
}
```

### 4. Performance Only

```typescript
const issues = await analyzePerformance(code)

for (const issue of issues) {
  console.log(`${issue.type}: ${issue.optimization}`)
  if (issue.estimatedImpact.timeMs) {
    console.log(`  Impact: ~${issue.estimatedImpact.timeMs}ms`)
  }
}
```

### 5. Refactoring Suggestions

```typescript
const refactors = await suggestRefactors(code)

for (const ref of refactors.filter(r => r.priority >= 4)) {
  console.log(`[Priority ${ref.priority}] ${ref.type}`)
  console.log(`Benefit: ${ref.benefit}`)
  console.log(`Before: ${ref.beforeCode.slice(0, 50)}...`)
  console.log(`After:  ${ref.afterCode.slice(0, 50)}...`)
}
```

### 6. Custom Reviewer Instance

```typescript
const reviewer = createCodeReviewer({
  useDeepAnalysis: true,
  maxTokens: 8000,
  confidenceThreshold: 0.8,
})

const review = await reviewer.reviewCode(code, {
  filepath: "src/services/payment.ts",
  language: "typescript",
  framework: "express",
  dependencies: { "express": "^4.18.0" },
})
```

## Review Output Structure

```typescript
{
  status: "success",
  
  // Findings by dimension
  securityIssues: [
    {
      id: "sec-0",
      type: "injection",
      severity: "critical",
      line: 42,
      description: "SQL injection vulnerability",
      impact: "Database compromise",
      remediation: "Use parameterized queries",
      cweId: "CWE-89",
      confidence: 0.95
    }
  ],
  
  performanceIssues: [...],
  refactorings: [...],
  comments: [...],
  
  // Scores
  overallScore: 65,
  improvements: {
    security: 40,
    performance: 75,
    codeQuality: 70,
    testability: 60,
    maintainability: 65,
  },
  
  // Summaries
  summary: "Critical security issues found",
  recommendations: ["Fix SQL injection", "Add input validation"],
  analysisTimeMs: 12500,
}
```

## Common Patterns

### Pattern 1: PR Approval Automation

```typescript
async function approvePR(prCode) {
  const review = await reviewCodeFast(prCode)
  
  if (review.securityIssues.some(i => i.severity === "critical")) {
    return "REQUEST_CHANGES"  // Block
  }
  
  if (review.overallScore >= 85) {
    return "APPROVE"  // Auto-merge
  }
  
  return "COMMENT"  // Need review
}
```

### Pattern 2: Security Gate

```typescript
async function securityGate(code) {
  const issues = await analyzeSecurity(code)
  
  const critical = issues.filter(i => i.severity === "critical")
  if (critical.length > 0) {
    throw new Error(`${critical.length} critical security issues`)
  }
  
  return true
}
```

### Pattern 3: Quality Tracking

```typescript
async function trackQuality(code, filepath) {
  const review = await reviewCodeFast(code)
  
  // Store in database
  await db.insert("code_reviews", {
    filepath,
    score: review.overallScore,
    timestamp: new Date(),
    security: review.improvements.security,
    issues: review.securityIssues.length,
  })
  
  // Alert if degradation
  const previous = await db.query(
    "SELECT score FROM code_reviews WHERE filepath = ? ORDER BY timestamp DESC LIMIT 1",
    [filepath]
  )
  
  if (previous && review.overallScore < previous[0].score - 10) {
    console.warn(`Quality degradation in ${filepath}`)
  }
}
```

### Pattern 4: Batch Analysis

```typescript
async function analyzeCodebase(files) {
  const reviews = await Promise.all(
    files.map(file => 
      reviewCodeFast(file.content, {
        filepath: file.path,
        language: "typescript",
      })
    )
  )
  
  return {
    averageScore: reviews.reduce((s, r) => s + r.overallScore, 0) / reviews.length,
    totalIssues: reviews.reduce((s, r) => s + r.securityIssues.length, 0),
    criticalCount: reviews.reduce(
      (s, r) => s + r.securityIssues.filter(i => i.severity === "critical").length,
      0
    ),
  }
}
```

### Pattern 5: Issue Categorization

```typescript
async function categorizeIssues(code) {
  const review = await reviewCodeFast(code)
  
  return {
    blocking: review.comments.filter(c => c.isBlocking),
    warnings: review.comments.filter(c => c.severity === "warning"),
    suggestions: review.comments.filter(c => c.severity === "info"),
    byType: {
      security: review.securityIssues.length,
      performance: review.performanceIssues.length,
      quality: review.refactorings.length,
    },
  }
}
```

## Configuration Options

```typescript
interface CodeReviewerConfig {
  apiKey?: string              // Default: process.env.ANTHROPIC_API_KEY
  fastModel?: string           // Default: claude-3-5-haiku-20241022
  deepModel?: string           // Default: claude-opus-4-1-20250805
  maxTokens?: number           // Default: 4096
  useDeepAnalysis?: boolean    // Default: false
  includeExamples?: boolean    // Default: true
  confidenceThreshold?: number // Default: 0.7
  anthropicApiUrl?: string     // Default: undefined (use official API)
}
```

## Context Options

```typescript
interface ReviewContext {
  filepath: string                    // e.g., "src/auth.ts"
  language?: "typescript" | "javascript" | "python" | "go" | "rust" | "other"
  framework?: string                  // e.g., "express", "fastapi"
  version?: string                    // e.g., "16.0.0"
  standards?: string[]                // e.g., ["eslint", "prettier"]
  dependencies?: Record<string, string>  // package.json contents
}
```

## Severity Levels

```
critical  - Must fix before merge
error     - Should fix before merge
warning   - Should consider fixing
info      - Nice to have improvement
```

## Issue Types

### Security
- `injection` - SQL/XSS/Command injection
- `exposed-secret` - Hardcoded keys, tokens, passwords
- `weak-validation` - Missing input validation
- `insecure-deserialization` - Unsafe deserialization
- `access-control` - Authorization flaws
- `cryptography` - Weak crypto
- `external-dependency` - Risky dependencies

### Performance
- `n-plus-one` - N+1 query patterns
- `inefficient-loop` - Inefficient loops/algorithms
- `memory-leak` - Potential memory leaks
- `unnecessary-allocation` - Wasteful allocations
- `missing-cache` - Cache optimization opportunity
- `large-payload` - Oversized data transfers
- `blocking-operation` - Blocking I/O operations

### Refactoring
- `extract-method` - Extract complex method
- `extract-constant` - Extract magic number/string
- `simplify-condition` - Simplify complex conditions
- `remove-duplication` - Remove code duplication
- `improve-naming` - Improve variable/function names
- `reduce-complexity` - Reduce cyclomatic complexity
- `split-class` - Split oversized class

## Scoring

```
0-20    - Critical issues
20-40   - Major issues
40-60   - Moderate issues
60-80   - Minor issues
80-100  - Excellent code
```

## Performance Tips

### 1. Use Fast Model by Default
```typescript
const review = await reviewCodeFast(code)  // 8-15s
// Only use deep for critical review gates
const deepReview = await reviewCodeDeep(code)  // 20-40s
```

### 2. Cache Results
```typescript
const hash = crypto.createHash("sha256").update(code).digest("hex")
if (cache[hash]) return cache[hash]
const review = await reviewer.reviewCode(code)
cache[hash] = review
```

### 3. Parallel Analysis
```typescript
// All dimensions run in parallel
const review = await reviewer.reviewCode(code)
// ~3x faster than sequential calls
```

### 4. Batch Operations
```typescript
const reviews = await Promise.all(
  files.map(f => reviewCodeFast(f.code))
)
```

## Integration Examples

**PR Automation:**
```typescript
import { PRAutomationEngine } from "./pr-automation"

automationEngine.reviewCode = (code) => 
  new CodeReviewer().reviewCode(code)
```

**Feedback System:**
```typescript
import { FeedbackEngine } from "./feedback-engine"

const feedback = createFeedbackEngine()
const review = await reviewer.reviewCode(code)
await feedback.trackReview(review)
```

**CI/CD Integration:**
```typescript
import { CIOrchestratorService } from "./ci-orchestrator"

const orchestrator = createCIOrchestratorService()
const review = await reviewer.reviewCode(code)
if (!review.securityIssues.some(i => i.severity === "critical")) {
  await orchestrator.approveAndDeploy(code)
}
```

## Troubleshooting

### ❌ "API key not set"
```bash
export ANTHROPIC_API_KEY=sk_...
```

### ❌ Slow reviews
Use `reviewCodeFast` instead of `reviewCodeDeep`

### ❌ Too many false positives
Set `confidenceThreshold: 0.85` in config

### ❌ Missing context in analysis
Add `ReviewContext` with filepath, language, framework

### ❌ Rate limiting
Implement queue with backoff or cache results

## Files Reference

| File | Purpose |
|------|---------|
| `src/services/code-reviewer.ts` | Main implementation |
| `CODE_REVIEWER_README.md` | Full documentation |
| `src/services/__tests__/code-reviewer.test.ts` | 46 test cases |
| `src/services/examples/code-reviewer-examples.ts` | 6 usage examples |
| `src/services/examples/code-reviewer-integration.ts` | Integration patterns |

## Next Steps

1. **Read:** `CODE_REVIEWER_README.md` for complete reference
2. **Explore:** Examples in `src/services/examples/`
3. **Integrate:** Connect with your PR automation
4. **Monitor:** Track code quality over time
5. **Optimize:** Adjust thresholds based on team needs

---

**Version:** 1.0.0  
**Status:** Production Ready  
**Updated:** 2026-07-31
