# Code Generator Enhanced (Phase 3) — PR-Specific Code Generation

**Version:** 2.0.0  
**Status:** ✅ Operational  
**Tier:** Sonnet/Opus

## Overview

`CodeGeneratorPR` extends the base `CodeGenerator` with intent-based, PR-specific code generation capabilities. It analyzes Pull Requests to:

1. **Generate Fixes** — Detect and suggest corrections for common code issues
2. **Generate Refactorings** — Propose code improvement opportunities
3. **Generate Tests** — Create comprehensive test suites for new code
4. **Suggest Improvements** — Provide recommendations for performance, security, and quality

**Key Differentiators:**

- PR-aware analysis (reads diffs, titles, descriptions)
- Automatic cache management (avoid re-analyzing identical code)
- Comprehensive audit logging (track all operations)
- Performance optimization (parallel analysis when possible)
- Risk assessment (summarizes findings with severity levels)

---

## Installation & Setup

### Basic Usage

```typescript
import { createCodeGeneratorPR } from "@/services/code-generator-enhanced";

// Create instance
const generator = createCodeGeneratorPR(projectRoot);

// Analyze a PR
const result = await generator.analyzePR({
  title: "Add user authentication",
  description: "Implements JWT-based auth",
  diff: "...", // git diff format
  changedFiles: {
    "src/auth.ts": "code content...",
  },
});

console.log(result.summary);
// Output:
// {
//   totalIssuesFound: 3,
//   criticalIssues: 0,
//   highIssues: 1,
//   estimatedTestCoverage: 85,
//   estimatedRefactoringTime: "2h",
//   overallRiskLevel: "medium"
// }
```

### Environment Setup

```bash
# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Create project structure
mkdir -p .claude/{logs,cache/code-gen}
```

---

## Core Methods

### 1. `generateFixes(prDiff: string): Promise<CodeFix[]>`

Analyzes a PR diff to identify and suggest fixes for common issues.

**Supported Issue Types:**

- `null-check` — Missing null/undefined validation
- `type-error` — Type mismatches and inference issues
- `performance` — Inefficient algorithms or patterns
- `security` — Vulnerabilities and injection risks
- `memory-leak` — Resource management issues
- `error-handling` — Inadequate error handling
- `logic-error` — Logical flaws in code
- `style` — Code style and formatting issues
- `other` — Miscellaneous issues

**Example:**

```typescript
const diff = `
  --- a/src/user.ts
  +++ b/src/user.ts
  @@ -5,3 +5,4 @@
   function getUser(id) {
  +  const user = users[id];
  +  return user.profile; // Missing null check!
   }
`;

const fixes = await generator.generateFixes(diff);

// Result:
// [
//   {
//     id: "fix-abc123",
//     issueType: "null-check",
//     severity: "high",
//     description: "User object may be undefined",
//     location: "src/user.ts:8:10",
//     problematicCode: "return user.profile;",
//     suggestedCode: "if (!user) return null; return user.profile;",
//     explanation: "users[id] can return undefined",
//     confidence: 95,
//     tags: ["null-safety", "defensive-programming"],
//     validated: false
//   }
// ]
```

**Severity Levels:**

| Level | Meaning | Impact |
|-------|---------|--------|
| `low` | Minor improvement | Code cleanup |
| `medium` | Should address | Can cause minor issues |
| `high` | Must address | Can cause significant failures |
| `critical` | Urgent | Security/data loss risk |

---

### 2. `generateRefactorings(code: string): Promise<Refactoring[]>`

Suggests refactoring opportunities to improve code quality.

**Refactoring Types:**

- `extract-function` — Extract logic into separate function
- `extract-constant` — Extract magic values to named constants
- `extract-interface` — Extract interface from class
- `merge-duplicates` — Consolidate duplicate code
- `simplify-logic` — Reduce conditional complexity
- `improve-naming` — Better variable/function names
- `reduce-complexity` — Lower cyclomatic complexity
- `improve-types` — Better type annotations
- `other` — Other improvements

**Example:**

```typescript
const code = `
  function processUser(user) {
    const firstName = user.name.split(' ')[0];
    const lastName = user.name.split(' ')[1];
    const email = user.email.toLowerCase();
    if (email.includes('@')) {
      console.log(firstName + ' ' + lastName);
    }
  }
`;

const refactorings = await generator.generateRefactorings(code);

// Result:
// [
//   {
//     id: "ref-xyz789",
//     type: "extract-function",
//     description: "Extract name parsing logic",
//     impact: 6,
//     difficulty: 1,
//     currentCode: "const firstName = user.name.split(' ')[0];",
//     refactoredCode: "const { firstName, lastName } = parseName(user.name);",
//     benefits: ["reusability", "testability", "readability"],
//     risks: [],
//     priority: "medium",
//     validated: false
//   },
//   {
//     id: "ref-xyz790",
//     type: "extract-constant",
//     description: "Extract email validation pattern",
//     impact: 3,
//     difficulty: 1,
//     currentCode: "if (email.includes('@'))",
//     refactoredCode: "const EMAIL_PATTERN = /@/; if (EMAIL_PATTERN.test(email))",
//     benefits: ["clarity"],
//     risks: [],
//     priority: "low",
//     validated: false
//   }
// ]
```

**Impact vs Difficulty:**

- **Impact (1-10)**: How much code quality improves
- **Difficulty (1-10)**: How hard to implement

**Priority:**

- `high` — High impact, low difficulty (do these first)
- `medium` — Medium impact or difficulty
- `low` — Low impact or high difficulty (nice to have)

---

### 3. `generateTests(code: string, testFramework?: Framework): Promise<TestSuite>`

Generates comprehensive test suites for new code.

**Supported Frameworks:**

- `jest` (default)
- `vitest`
- `mocha`

**Example:**

```typescript
const code = `
  export function calculateTotal(items: Array<{ price: number }>) {
    return items.reduce((sum, item) => sum + item.price, 0);
  }
`;

const testSuite = await generator.generateTests(code, "jest");

// Result:
// {
//   id: "ts-abc123",
//   testFramework: "jest",
//   expectedCoverage: 95,
//   testCaseCount: 5,
//   testCode: "import { calculateTotal } from '../fn'; describe(...)",
//   testCases: [
//     {
//       name: "should sum prices of items",
//       description: "Happy path with valid items",
//       type: "unit",
//       input: { items: [{ price: 10 }, { price: 20 }] },
//       expectedOutput: 30,
//       assertions: ["result === 30"],
//       critical: true
//     },
//     {
//       name: "should handle empty array",
//       description: "Edge case: no items",
//       type: "unit",
//       input: { items: [] },
//       expectedOutput: 0,
//       assertions: ["result === 0"],
//       critical: true
//     },
//     // ... more test cases
//   ],
//   testedFunctions: ["calculateTotal"],
//   scenarios: [
//     {
//       name: "Basic calculations",
//       description: "Standard use cases",
//       testCaseNames: ["should sum prices of items", "should handle empty array"],
//       executionOrder: 1
//     }
//   ],
//   suggestedFileName: "calculateTotal.test.ts"
// }
```

**Test Types:**

- `unit` — Single function/component
- `integration` — Multiple components together
- `e2e` — Full user workflows

**Test Coverage:**

Generated tests aim for:
- 90%+ line coverage
- All critical paths
- Edge cases and error scenarios

---

### 4. `suggestImprovements(code: string): Promise<Improvement[]>`

Provides holistic suggestions for code improvements.

**Improvement Categories:**

- `performance` — Speed and efficiency optimizations
- `security` — Security vulnerabilities and hardening
- `readability` — Code clarity and understandability
- `maintainability` — Long-term code health
- `types` — TypeScript type safety
- `error-handling` — Error management
- `documentation` — Comments and docs
- `testing` — Test coverage and quality
- `other` — Miscellaneous suggestions

**Example:**

```typescript
const code = `
  function getUsers() {
    const result = fetch('/api/users');
    return result.json();
  }
`;

const improvements = await generator.suggestImprovements(code);

// Result:
// [
//   {
//     id: "imp-sec001",
//     category: "security",
//     description: "Add request timeout to prevent hanging",
//     impact: 8,
//     effort: 2,
//     suggestion: "Use AbortController with timeout",
//     codeExample: "const controller = new AbortController(); setTimeout(() => controller.abort(), 5000);",
//     references: ["https://developer.mozilla.org/en-US/docs/Web/API/AbortController"],
//     priority: "high",
//     validated: false
//   },
//   {
//     id: "imp-err001",
//     category: "error-handling",
//     description: "Add error handling for fetch failures",
//     impact: 9,
//     effort: 2,
//     suggestion: "Wrap in try/catch and handle network errors",
//     codeExample: "try { ... } catch (error) { console.error('Fetch failed:', error); }",
//     references: ["https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API"],
//     priority: "high",
//     validated: false
//   }
// ]
```

---

## Complete PR Analysis

### `analyzePR(prContext: PRContext): Promise<PRAnalysisResult>`

Performs comprehensive analysis of a PR across all dimensions.

**Input Structure:**

```typescript
interface PRContext {
  title: string;              // PR title
  description?: string;       // PR description
  branch?: string;            // Branch name
  author?: string;            // Author email
  diff?: string;              // git diff output
  changedFiles?: Record<string, string>;  // filename -> content
  deletedFiles?: string[];    // files deleted
  labels?: string[];          // PR labels
  isWIP?: boolean;            // Work in progress flag
  relatedIssueNumbers?: number[];
}
```

**Output Structure:**

```typescript
interface PRAnalysisResult {
  status: "success" | "partial" | "failed";
  fixes: CodeFix[];           // Found issues
  refactorings: Refactoring[]; // Improvement opportunities
  testSuite?: TestSuite;      // Generated tests
  improvements: Improvement[];  // General suggestions
  
  summary: {
    totalIssuesFound: number;
    criticalIssues: number;
    highIssues: number;
    estimatedTestCoverage: number;
    estimatedRefactoringTime: string;
    overallRiskLevel: "low" | "medium" | "high" | "critical";
  };
  
  processingTimeMs: number;
  generatedAt: Date;
  errors: string[];
}
```

**Example:**

```typescript
const result = await generator.analyzePR({
  title: "Add payment processing",
  description: "Implements Stripe integration",
  diff: "...",
  changedFiles: {
    "src/payment.ts": "new payment code...",
    "src/payment.test.ts": "test code...",
  },
});

console.log(result.summary);
// {
//   totalIssuesFound: 5,
//   criticalIssues: 1,
//   highIssues: 2,
//   estimatedTestCoverage: 88,
//   estimatedRefactoringTime: "3h",
//   overallRiskLevel: "high"
// }

// Check for critical issues
if (result.summary.criticalIssues > 0) {
  const critical = result.fixes.filter(f => f.severity === "critical");
  console.log("Critical issues found:", critical);
}
```

---

## Caching & Performance

### Cache Management

The service automatically caches results to avoid re-analyzing identical code:

```typescript
// First call — analyzes and caches
const fixes1 = await generator.generateFixes(diff);

// Second call with same diff — returns from cache immediately
const fixes2 = await generator.generateFixes(diff);

// Check cache stats
const stats = generator.getCacheStats();
console.log(`Cache contains ${stats.entries} entries`);

// Clear expired cache entries
generator.clearCache();
```

**Cache Configuration:**

- **TTL**: 24 hours by default
- **Storage**: In-memory map + filesystem backup
- **Key**: SHA256 hash of content

### Performance Optimization

The service includes several optimizations:

1. **Parallel Analysis** — When analyzing multiple files, processes them concurrently
2. **Lazy Evaluation** — Only runs expensive analyses if needed
3. **Content Deduplication** — Skips duplicate code analysis
4. **Early Exit** — Stops analysis when findings reach threshold

---

## Audit Logging

All operations are logged for compliance and debugging:

### Access Audit Log

```typescript
// Get audit statistics
const stats = generator.getAuditStats();
console.log(`Total operations: ${stats.totalActions}`);
console.log(`Success rate: ${(stats.successCount / stats.totalActions * 100).toFixed(2)}%`);
console.log(`Avg execution time: ${stats.averageExecutionTime.toFixed(0)}ms`);

// Save audit log to disk
generator.saveAuditLog();
```

### Audit Log Format

Stored in `.claude/logs/code-gen-audit.jsonl`:

```json
{
  "timestamp": "2026-07-31T10:30:45.123Z",
  "action": "generateFixes",
  "details": { "fixesCount": 3, "source": "api" },
  "status": "success",
  "executionTimeMs": 2345
}
```

---

## API Reference

### Types

```typescript
// PR Input
interface PRContext {
  title: string;
  description?: string;
  branch?: string;
  author?: string;
  diff?: string;
  changedFiles?: Record<string, string>;
  deletedFiles?: string[];
  labels?: string[];
  isWIP?: boolean;
  relatedIssueNumbers?: number[];
}

// Fixes
interface CodeFix {
  id: string;
  issueType: "null-check" | "type-error" | "performance" | ...;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  location?: string;
  problematicCode?: string;
  suggestedCode: string;
  explanation: string;
  confidence: number;  // 0-100
  tags: string[];
  validated: boolean;
}

// Refactorings
interface Refactoring {
  id: string;
  type: "extract-function" | "extract-constant" | ...;
  description: string;
  impact: number;      // 1-10
  difficulty: number;  // 1-10
  currentCode: string;
  refactoredCode: string;
  benefits: string[];
  risks: string[];
  priority: "high" | "medium" | "low";
  validated: boolean;
}

// Tests
interface TestSuite {
  id: string;
  testFramework: "jest" | "vitest" | "mocha";
  expectedCoverage: number;  // 0-100
  testCaseCount: number;
  testCode: string;
  testCases: TestCase[];
  testedFunctions: string[];
  scenarios: TestScenario[];
  suggestedFileName: string;
}

// Improvements
interface Improvement {
  id: string;
  category: "performance" | "security" | ...;
  description: string;
  impact: number;    // 1-10
  effort: number;    // 1-10
  suggestion: string;
  codeExample?: string;
  references?: string[];
  priority: "high" | "medium" | "low";
  validated: boolean;
}

// Analysis Result
interface PRAnalysisResult {
  status: "success" | "partial" | "failed";
  fixes: CodeFix[];
  refactorings: Refactoring[];
  testSuite?: TestSuite;
  improvements: Improvement[];
  summary: {
    totalIssuesFound: number;
    criticalIssues: number;
    highIssues: number;
    estimatedTestCoverage: number;
    estimatedRefactoringTime: string;
    overallRiskLevel: "low" | "medium" | "high" | "critical";
  };
  processingTimeMs: number;
  generatedAt: Date;
  errors: string[];
}
```

### Methods

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| `generateFixes()` | `diff: string` | `CodeFix[]` | Find bugs and suggest fixes |
| `generateRefactorings()` | `code: string` | `Refactoring[]` | Suggest code improvements |
| `generateTests()` | `code: string, framework?: string` | `TestSuite` | Generate test cases |
| `suggestImprovements()` | `code: string` | `Improvement[]` | Suggest quality improvements |
| `analyzePR()` | `prContext: PRContext` | `PRAnalysisResult` | Complete PR analysis |
| `getCacheStats()` | none | `{ size, entries }` | Cache statistics |
| `getAuditStats()` | none | `{ totalActions, ... }` | Audit statistics |
| `clearCache()` | none | void | Clear expired cache |
| `saveAuditLog()` | none | void | Save audit log to disk |

---

## Integration Patterns

### GitHub Actions

```yaml
name: Code Analysis
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Analyze PR
        run: |
          npx ts-node -O '{"module":"commonjs"}' ./scripts/analyze-pr.ts
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

npx ts-node ./scripts/pre-commit-analysis.ts
if [ $? -ne 0 ]; then
  echo "Code analysis failed. Please fix issues before committing."
  exit 1
fi
```

### Slack Notification

```typescript
import { createCodeGeneratorPR } from "@/services";

async function notifySlack(prContext: PRContext) {
  const gen = createCodeGeneratorPR();
  const result = await gen.analyzePR(prContext);

  if (result.summary.criticalIssues > 0) {
    await slack.send({
      channel: "#code-review",
      text: `🚨 Critical issues in ${prContext.title}`,
      blocks: formatResult(result),
    });
  }
}
```

---

## Configuration

### Environment Variables

```bash
ANTHROPIC_API_KEY          # Anthropic API key (required)
CODE_GEN_PROJECT_ROOT      # Project root directory (default: cwd)
CODE_GEN_CACHE_TTL         # Cache TTL in ms (default: 86400000 = 24h)
CODE_GEN_AUDIT_PATH        # Audit log path (default: .claude/logs/...)
```

### Initialization

```typescript
import { createCodeGeneratorPR } from "@/services";

const gen = createCodeGeneratorPR(
  "/path/to/project",
  "/custom/audit/path"
);
```

---

## Troubleshooting

### No Analysis Results

**Issue**: `generateFixes()` returns empty array

**Solutions**:
1. Check API key is set: `echo $ANTHROPIC_API_KEY`
2. Verify diff format is correct (should be git diff format)
3. Check API rate limits
4. Review error logs: `.claude/logs/code-gen-audit.jsonl`

### High Cache Miss Rate

**Issue**: Cache not being used effectively

**Solutions**:
1. Verify code is identical between calls
2. Check cache TTL hasn't expired (default 24h)
3. Call `getCacheStats()` to debug
4. Clear cache with `clearCache()` if needed

### Slow Analysis

**Issue**: Analysis takes too long

**Solutions**:
1. Analyze smaller code chunks separately
2. Use caching more effectively
3. Check if API is slow (monitor `processingTimeMs`)
4. Consider sampling instead of full analysis

---

## Best Practices

1. **Cache Results** — Reuse analysis results within TTL window
2. **Batch Improvements** — Group fixes by severity and category
3. **Prioritize High Impact** — Focus on high-impact, low-difficulty refactorings first
4. **Monitor Risk** — Don't merge PRs with "critical" risk level
5. **Validate Suggestions** — Review suggested fixes before auto-applying
6. **Log Everything** — Enable audit logging for compliance
7. **Test Thoroughly** — Use generated test cases as starting point

---

## Examples

### Example 1: PR Review Automation

```typescript
async function reviewPR(prNumber: number) {
  const pr = await github.getPR(prNumber);
  const diff = await github.getPRDiff(prNumber);
  
  const gen = createCodeGeneratorPR();
  const result = await gen.analyzePR({
    title: pr.title,
    description: pr.body,
    diff,
    changedFiles: await github.getPRFiles(prNumber),
  });
  
  // Post review comment
  const comment = formatReview(result);
  await github.createReview(prNumber, comment, result.summary.overallRiskLevel);
}
```

### Example 2: Test Coverage Improvement

```typescript
async function improveTestCoverage(filePath: string) {
  const code = fs.readFileSync(filePath, 'utf-8');
  
  const gen = createCodeGeneratorPR();
  const testSuite = await gen.generateTests(code, 'jest');
  
  const outputPath = filePath.replace('.ts', '.test.ts');
  fs.writeFileSync(outputPath, testSuite.testCode);
  
  console.log(`Generated ${testSuite.testCaseCount} test cases`);
  console.log(`Expected coverage: ${testSuite.expectedCoverage}%`);
}
```

### Example 3: Code Quality Dashboard

```typescript
async function generateQualityReport(repoPath: string) {
  const files = glob.sync(`${repoPath}/**/*.ts`);
  const gen = createCodeGeneratorPR();
  
  const allFixes: CodeFix[] = [];
  const allRefactorings: Refactoring[] = [];
  
  for (const file of files) {
    const code = fs.readFileSync(file, 'utf-8');
    const fixes = await gen.generateFixes(code);
    const refactorings = await gen.generateRefactorings(code);
    
    allFixes.push(...fixes.map(f => ({ ...f, file })));
    allRefactorings.push(...refactorings.map(r => ({ ...r, file })));
  }
  
  console.table({
    'Total Files': files.length,
    'Issues Found': allFixes.length,
    'Critical': allFixes.filter(f => f.severity === 'critical').length,
    'High': allFixes.filter(f => f.severity === 'high').length,
    'Refactoring Opportunities': allRefactorings.length,
  });
}
```

---

## Performance Characteristics

| Operation | Input Size | Avg Time | Notes |
|-----------|-----------|----------|-------|
| generateFixes | Small diff (<5KB) | 1-2s | Cached after first call |
| generateFixes | Large diff (>50KB) | 5-10s | May be split into chunks |
| generateRefactorings | Single function | 1-2s | Depends on complexity |
| generateTests | 100 lines | 3-5s | Full suite with all cases |
| suggestImprovements | Single function | 2-3s | Comprehensive analysis |
| analyzePR | Full PR | 15-30s | Parallel file analysis |

**Optimization Tips:**

- Use caching for repeated analysis (saves 95%+ time)
- Analyze functions independently (parallelizable)
- Batch similar requests together
- Use smaller code chunks for faster analysis

---

## Support & Debugging

### Enable Debug Logging

```typescript
const gen = createCodeGeneratorPR(projectRoot);

// Check audit log
const stats = gen.getAuditStats();
console.log(JSON.stringify(stats, null, 2));

// Review last audit entries
gen.saveAuditLog();
// Then check: .claude/logs/code-gen-audit.jsonl
```

### Report Issues

When reporting issues, include:
1. Code snippet or diff causing the issue
2. Output from `getAuditStats()`
3. Content of `.claude/logs/code-gen-audit.jsonl`
4. Environment details (Node version, OS, etc.)

---

## Changelog

### v2.0.0 (Phase 3)

- ✅ Added PR-specific analysis
- ✅ Implemented caching system
- ✅ Added audit logging
- ✅ Added risk assessment
- ✅ Performance optimizations
- ✅ Comprehensive test suite

### v1.0.0

- Base CodeGenerator implementation
- YAML frontmatter validation
- Agent creation workflow

---

## License

Proprietary — Manta Associados 2026

For questions or support, contact the Manta Maestro team.
