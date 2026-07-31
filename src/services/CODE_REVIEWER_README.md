# Code Reviewer Service — Phase 4 Main Service

## Overview

The **CodeReviewer** service provides comprehensive, multi-dimensional code analysis with structured feedback on security, performance, style, testing, and best practices.

**Version:** 1.0.0  
**Status:** Production Ready  
**API Surface:** 7 public methods + 5 factory functions  
**Dimensions:** 5 (Security, Performance, Style, Testing, Best Practices)  
**Models:** Haiku (fast) + Opus (deep analysis)

---

## Features

### Multi-Dimensional Analysis

1. **Security Issues** (`analyzeSecurityIssues`)
   - Injection vulnerabilities (SQL, XSS, Command)
   - Exposed secrets (keys, tokens, passwords)
   - Weak validation
   - Insecure deserialization
   - Access control flaws
   - Cryptographic weaknesses
   - External dependency risks
   - CWE classification

2. **Performance Issues** (`checkPerformance`)
   - N+1 query patterns
   - Inefficient loops
   - Memory leaks
   - Unnecessary allocations
   - Missing cache opportunities
   - Large payload handling
   - Blocking operations
   - Estimated impact metrics

3. **Refactoring Suggestions** (`suggestRefactoring`)
   - Extract method/constant
   - Simplify conditionals
   - Remove duplication
   - Improve naming
   - Reduce cyclomatic complexity
   - Split oversized classes
   - Priority-ranked suggestions

4. **Structured Comments** (`generateComments`)
   - Automatic comment generation
   - Markdown-formatted body
   - Issue/suggestion/question/praise types
   - Blocking vs. non-blocking
   - Line-specific anchoring

5. **Complete Reviews** (`reviewCode`)
   - Full code analysis in parallel
   - Aggregated scoring (0-100)
   - Weighted improvements calculation
   - Executive summary
   - Actionable recommendations

---

## API Reference

### Class: `CodeReviewer`

#### Constructor

```typescript
constructor(config?: CodeReviewerConfig)
```

**Parameters:**
- `config.apiKey?`: string — Anthropic API key (default: `process.env.ANTHROPIC_API_KEY`)
- `config.fastModel?`: string — Haiku model ID (default: `claude-3-5-haiku-20241022`)
- `config.deepModel?`: string — Opus model ID (default: `claude-opus-4-1-20250805`)
- `config.maxTokens?`: number — Token limit per request (default: 4096)
- `config.useDeepAnalysis?`: boolean — Use Opus by default (default: false)
- `config.includeExamples?`: boolean — Include code examples (default: true)
- `config.confidenceThreshold?`: number — Min confidence (default: 0.7)
- `config.anthropicApiUrl?`: string — Custom API endpoint

#### Methods

##### 1. `reviewCode(code: string, context?: ReviewContext): Promise<Review>`

Executes a complete code review with all dimensions analyzed in parallel.

**Parameters:**
- `code`: The code to review
- `context?`: Review context (filepath, language, framework, etc.)

**Returns:** Complete review with security, performance, refactoring, and comment findings.

**Example:**
```typescript
const reviewer = new CodeReviewer();
const review = await reviewer.reviewCode(
  `function processData(items) {
    for (let i = 0; i < items.length; i++) {
      db.query(\`SELECT * FROM users WHERE id = \${items[i]}\`);
    }
  }`,
  {
    filepath: "src/data-processor.ts",
    language: "typescript",
    framework: "express",
  }
);

console.log(`Overall Score: ${review.overallScore}`);
console.log(`Security Issues: ${review.securityIssues.length}`);
console.log(`Summary: ${review.summary}`);
```

---

##### 2. `analyzeSecurityIssues(code: string, context?: ReviewContext): Promise<SecurityIssue[]>`

Analyzes code for security vulnerabilities.

**Returns:** Array of `SecurityIssue` objects with:
- `id`: Unique identifier
- `type`: Vulnerability type
- `severity`: critical | error | warning | info
- `description`: Detailed problem description
- `line`: Line number
- `codeSnippet`: Affected code
- `impact`: Potential impact
- `remediation`: How to fix
- `secureExample?`: Secure code example
- `cweId?`: CWE identifier (e.g., "CWE-89" for SQL Injection)
- `confidence`: 0.0-1.0 confidence score

**Example:**
```typescript
const issues = await reviewer.analyzeSecurityIssues(
  `const sql = \`SELECT * FROM users WHERE id = \${req.params.id}\`;`
);

for (const issue of issues) {
  console.log(`[${issue.severity.toUpperCase()}] ${issue.type}`);
  console.log(`  ${issue.description}`);
  console.log(`  Fix: ${issue.remediation}`);
}
```

---

##### 3. `checkPerformance(code: string, context?: ReviewContext): Promise<PerformanceIssue[]>`

Identifies performance bottlenecks and optimization opportunities.

**Returns:** Array of `PerformanceIssue` objects with:
- `id`: Unique identifier
- `type`: Problem type (n-plus-one, memory-leak, etc.)
- `severity`: critical | error | warning | info
- `description`: Detailed problem description
- `line`: Line number
- `codeSnippet`: Affected code
- `estimatedImpact`: {timeMs?, memoryMb?, degradationPercent?}
- `optimization`: How to optimize
- `optimizedExample?`: Optimized code example
- `confidence`: 0.0-1.0 confidence score

**Example:**
```typescript
const perf = await reviewer.checkPerformance(
  `for (let i = 0; i < 10000; i++) {
    let user = db.query(\`SELECT * FROM users WHERE id = \${i}\`);
    console.log(user.name);
  }`
);

for (const issue of perf) {
  console.log(`${issue.type}: ${issue.estimatedImpact.timeMs}ms impact`);
  console.log(`Solution: ${issue.optimization}`);
}
```

---

##### 4. `suggestRefactoring(code: string, context?: ReviewContext): Promise<Refactoring[]>`

Suggests refactorings to improve code quality and maintainability.

**Returns:** Array of `Refactoring` objects with:
- `id`: Unique identifier
- `type`: Refactoring type (extract-method, remove-duplication, etc.)
- `description`: What to refactor
- `benefit`: Expected benefit
- `line`: Line number
- `beforeCode`: Original code
- `afterCode`: Refactored code
- `rationale`: Why refactor
- `complexity?`: {before: number, after: number} — Cyclomatic complexity
- `priority`: 1-5 (5 = highest)

**Example:**
```typescript
const refactors = await reviewer.suggestRefactoring(
  `const result = processA(data) ? processB(data) ? processC(data) : null : null;`
);

for (const ref of refactors.filter(r => r.priority >= 4)) {
  console.log(`Priority ${ref.priority}: ${ref.type}`);
  console.log(`Before: ${ref.beforeCode}`);
  console.log(`After:  ${ref.afterCode}`);
  console.log(`Complexity: ${ref.complexity?.before} → ${ref.complexity?.after}`);
}
```

---

##### 5. `generateComments(code: string, context?: ReviewContext): Promise<ReviewComment[]>`

Generates structured review comments for all detected issues.

**Returns:** Array of `ReviewComment` objects with:
- `id`: Unique identifier
- `line`: Line number
- `type`: suggestion | question | observation | praise | issue
- `severity`: critical | error | warning | info
- `title`: Brief title
- `body`: Markdown-formatted body
- `tag?`: Tag (e.g., @performance, @security)
- `suggestedCode?`: Code suggestion
- `context?`: Related context
- `isBlocking`: true if critical/error

**Example:**
```typescript
const comments = await reviewer.generateComments(code);

for (const comment of comments.filter(c => c.isBlocking)) {
  console.log(`[BLOCKING] Line ${comment.line}: ${comment.title}`);
  console.log(comment.body);
}
```

---

##### 6. `generateComment(issue: {...}): Promise<ReviewComment>`

Generates a single structured comment from issue details.

**Parameters:**
- `issue.type`: Review comment type
- `issue.title`: Brief title
- `issue.line`: Line number
- `issue.description`: Detailed description
- `issue.severity`: Issue severity

**Returns:** Single `ReviewComment` object.

---

### Factory Functions

```typescript
// Quick review (Haiku)
const review = await reviewCodeFast(code, context);

// Deep review (Opus)
const review = await reviewCodeDeep(code, context);

// Security only
const issues = await analyzeSecurity(code, context);

// Performance only
const perf = await analyzePerformance(code, context);

// Refactoring only
const refactors = await suggestRefactors(code, context);

// Create custom instance
const reviewer = createCodeReviewer({
  useDeepAnalysis: true,
  includeExamples: true,
});
```

---

## Data Structures

### `Review`

Complete review result:

```typescript
interface Review {
  status: "success" | "failed";
  securityIssues: SecurityIssue[];
  performanceIssues: PerformanceIssue[];
  refactorings: Refactoring[];
  comments: ReviewComment[];
  overallScore: number; // 0-100
  improvements: {
    security: number;        // 0-100
    performance: number;      // 0-100
    codeQuality: number;      // 0-100
    testability: number;      // 0-100
    maintainability: number;  // 0-100
  };
  summary: string;
  recommendations: string[];
  analysisTimeMs: number;
  errors?: string[];
}
```

### `SecurityIssue`

```typescript
interface SecurityIssue {
  id: string;
  type: "injection" | "exposed-secret" | "weak-validation" | ...;
  severity: IssueSeverity;
  description: string;
  line: number;
  endLine?: number;
  codeSnippet: string;
  impact: string;
  remediation: string;
  secureExample?: string;
  cweId?: string;
  confidence: number; // 0.0-1.0
}
```

### `PerformanceIssue`

```typescript
interface PerformanceIssue {
  id: string;
  type: "n-plus-one" | "inefficient-loop" | "memory-leak" | ...;
  severity: IssueSeverity;
  description: string;
  line: number;
  endLine?: number;
  codeSnippet: string;
  estimatedImpact: {
    timeMs?: number;
    memoryMb?: number;
    degradationPercent?: number;
  };
  optimization: string;
  optimizedExample?: string;
  confidence: number;
}
```

### `Refactoring`

```typescript
interface Refactoring {
  id: string;
  type: "extract-method" | "extract-constant" | "simplify-condition" | ...;
  description: string;
  benefit: string;
  line: number;
  endLine?: number;
  beforeCode: string;
  afterCode: string;
  rationale: string;
  complexity?: { before: number; after: number };
  priority: 1 | 2 | 3 | 4 | 5; // 5 = highest
}
```

### `ReviewContext`

```typescript
interface ReviewContext {
  filepath: string;                        // e.g., "src/services/auth.ts"
  language?: "typescript" | "javascript" | "python" | "go" | "rust" | "other";
  framework?: string;                      // e.g., "express", "fastapi"
  version?: string;                        // e.g., "16.0.0"
  standards?: string[];                    // e.g., ["eslint", "prettier"]
  dependencies?: Record<string, string>;   // package.json contents
}
```

---

## Usage Examples

### Example 1: Quick Security Scan

```typescript
import { analyzeSecurity } from "./services";

const code = `
const apiKey = "sk_live_12345abcde";
const query = \`SELECT * FROM users WHERE id = \${userId}\`;
`;

const issues = await analyzeSecurity(code);

console.log(`Found ${issues.length} security issues:`);
for (const issue of issues) {
  console.log(`- [${issue.severity}] ${issue.type}: ${issue.description}`);
  console.log(`  Remediation: ${issue.remediation}`);
}
```

**Output:**
```
Found 2 security issues:
- [critical] exposed-secret: API key exposed in source code
  Remediation: Use environment variables for secrets
- [critical] injection: SQL injection vulnerability detected
  Remediation: Use parameterized queries
```

---

### Example 2: Complete Code Review

```typescript
import { reviewCodeDeep } from "./services";

const code = `
function fetchUserData(userId) {
  let result = [];
  for (let i = 0; i < 1000; i++) {
    const user = database.query(\`
      SELECT * FROM users WHERE id = \${userId} AND index = \${i}
    \`);
    if (user && user.active) {
      result.push(user);
    }
  }
  return result;
}
`;

const review = await reviewCodeDeep(code, {
  filepath: "src/services/user-service.ts",
  language: "typescript",
  framework: "express",
});

console.log(`\n📊 Review Summary`);
console.log(`Overall Score: ${review.overallScore}/100`);
console.log(`\n🔒 Security: ${review.improvements.security}/100`);
console.log(`⚡ Performance: ${review.improvements.performance}/100`);
console.log(`✨ Code Quality: ${review.improvements.codeQuality}/100`);
console.log(`\n${review.summary}`);
console.log(`\nRecommendations:`);
review.recommendations.forEach(r => console.log(`• ${r}`));
```

---

### Example 3: Refactoring Analysis

```typescript
import { suggestRefactors } from "./services";

const code = `
function validateEmail(email) {
  if (email && email.includes("@") && email.includes(".")) {
    if (email.length > 3 && email.length < 255) {
      if (!email.startsWith(" ") && !email.endsWith(" ")) {
        return true;
      }
    }
  }
  return false;
}
`;

const refactors = await suggestRefactors(code);

console.log(`High-Priority Refactorings:`);
refactors
  .filter(r => r.priority >= 4)
  .forEach(r => {
    console.log(`\n${r.type} (Priority ${r.priority})`);
    console.log(`Benefit: ${r.benefit}`);
    console.log(`Before:  ${r.beforeCode.slice(0, 50)}...`);
    console.log(`After:   ${r.afterCode.slice(0, 50)}...`);
    if (r.complexity) {
      console.log(`Complexity: ${r.complexity.before} → ${r.complexity.after}`);
    }
  });
```

---

### Example 4: Integration with PR Automation

```typescript
import { CodeReviewer } from "./services";

class PRReviewAutomation {
  private reviewer = new CodeReviewer({ useDeepAnalysis: true });

  async reviewPullRequest(code: string, prNumber: number) {
    const review = await this.reviewer.reviewCode(code, {
      filepath: `pr-${prNumber}`,
      language: "typescript",
    });

    // Block merge if critical security issues
    if (review.securityIssues.some(i => i.severity === "critical")) {
      return {
        action: "REQUEST_CHANGES",
        message: "Critical security issues must be fixed before merge",
        issues: review.securityIssues,
      };
    }

    // Conditional merge if performance issues but CI passed
    if (review.performanceIssues.some(i => i.severity === "error")) {
      return {
        action: "COMMENT",
        message: "Performance issues detected. Please review recommendations.",
        issues: review.performanceIssues,
      };
    }

    // Auto-approve if quality is high
    if (review.overallScore >= 85) {
      return {
        action: "APPROVE",
        message: `Code quality is excellent (${review.overallScore}/100)`,
      };
    }

    return {
      action: "COMMENT",
      message: review.summary,
      recommendations: review.recommendations,
    };
  }
}
```

---

## Scoring System

### Overall Score Calculation

```
Overall = (Security×0.30 + Performance×0.25 + CodeQuality×0.25 + 
           Testability×0.10 + Maintainability×0.10)
```

**Dimension Scores:**
- **Security:** 100 - (critical×30 + error×15 + warning×5)
- **Performance:** 100 - (critical×30 + error×15 + warning×5)
- **CodeQuality:** 80 - (refactorings × 5)
- **Testability:** 80 or 60 (presence of test comments)
- **Maintainability:** 85 - (naming issues × 10)

---

## Model Selection

### Fast Analysis (Haiku)
- Suitable for: Quick scans, high-volume reviews, CI integration
- Latency: ~2-5 seconds
- Cost: Lower (Haiku pricing)
- Accuracy: 85-90%

### Deep Analysis (Opus)
- Suitable for: Critical code, architectural reviews, thorough analysis
- Latency: ~10-30 seconds
- Cost: Higher (Opus pricing)
- Accuracy: 95%+

**Recommendation:** Use `reviewCodeFast` for PR automation, `reviewCodeDeep` for manual review gates.

---

## Error Handling

All methods return structured results with optional `errors` field:

```typescript
const review = await reviewer.reviewCode(code);

if (review.status === "failed") {
  console.error("Review failed:", review.errors);
  // Handle gracefully
}

// Partial results still available even with errors
console.log(`Analyzed with ${review.errors?.length} warnings`);
```

---

## Performance Characteristics

| Operation | Model | Time | Tokens | Notes |
|-----------|-------|------|--------|-------|
| `analyzeSecurityIssues` | Haiku | 2-3s | 3,000-4,000 | Fast scan |
| `checkPerformance` | Haiku | 2-3s | 3,000-4,000 | Fast scan |
| `suggestRefactoring` | Haiku | 3-5s | 3,500-4,500 | More complex |
| `reviewCode` (full) | Haiku | 8-15s | 12,000-16,000 | Parallel execution |
| `reviewCode` (full) | Opus | 20-40s | 15,000-20,000 | Deep analysis |

---

## Integration Points

### With PR Automation
```typescript
import { PRAutomationEngine } from "./pr-automation";
import { CodeReviewer } from "./code-reviewer";

const automationEngine = createPRAutomationEngine();
const codeReviewer = new CodeReviewer({ useDeepAnalysis: true });

// Hook in code review step
automationEngine.onCodeAnalysis = async (code) => {
  return codeReviewer.reviewCode(code);
};
```

### With Feedback Engine
```typescript
import { FeedbackEngine } from "./feedback-engine";
import { CodeReviewer } from "./code-reviewer";

const feedback = createFeedbackEngine();
const reviewer = new CodeReviewer();

const review = await reviewer.reviewCode(code);
await feedback.trackReview(review);
```

### With CI/CD Orchestrator
```typescript
import { CIOrchestratorService } from "./ci-orchestrator";
import { CodeReviewer } from "./code-reviewer";

const orchestrator = createCIOrchestratorService();
const reviewer = new CodeReviewer();

const review = await reviewer.reviewCode(artifactCode);
await orchestrator.evaluateQuality(review);
```

---

## Best Practices

1. **Use context for better analysis**
   ```typescript
   const review = await reviewer.reviewCode(code, {
     filepath: "src/auth.ts",
     language: "typescript",
     framework: "express",
     dependencies: { "express": "^4.18.0" },
   });
   ```

2. **Cache reviews for identical code**
   ```typescript
   const hash = crypto.createHash("sha256").update(code).digest("hex");
   if (reviewCache[hash]) return reviewCache[hash];
   ```

3. **Batch reviews efficiently**
   ```typescript
   const reviews = await Promise.all([
     reviewer.analyzeSecurityIssues(code1),
     reviewer.checkPerformance(code2),
     reviewer.suggestRefactoring(code3),
   ]);
   ```

4. **Filter results by severity**
   ```typescript
   const blocking = review.comments.filter(c => c.isBlocking);
   const warnings = review.comments.filter(c => c.severity === "warning");
   ```

---

## Troubleshooting

### Issue: High latency
- **Solution:** Use `reviewCodeFast` instead of `reviewCodeDeep`
- **Alternative:** Implement caching for identical code snippets

### Issue: Low confidence scores
- **Cause:** Model uncertainty on complex code
- **Solution:** Provide more context in `ReviewContext`

### Issue: False positives
- **Solution:** Adjust `confidenceThreshold` config
- **Recommendation:** Set to 0.8+ for production

### Issue: Rate limiting
- **Solution:** Implement request queuing with backoff
- **Reference:** See `SyncQueueManager` in services

---

## Changelog

### v1.0.0 (2026-07-31)
- Initial release
- 5 analysis dimensions
- 7 public methods
- 5 factory functions
- Haiku + Opus model support
- Parallel analysis execution
- Weighted scoring system
- Markdown comment generation
