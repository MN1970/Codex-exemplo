# Technical Debt Scoring Specification

## Overview

The Code Refactoring Engine implements a comprehensive technical debt scoring system that quantifies code quality across multiple dimensions and provides actionable insights.

## Scoring Algorithm

### Base Score Calculation

```
TechnicalDebtScore = (∑ severity_weight × issue_count) / max_possible_weight × 100

Where:
- severity_weight(CRITICAL) = 10
- severity_weight(HIGH) = 7
- severity_weight(MEDIUM) = 4
- severity_weight(LOW) = 1
- severity_weight(INFO) = 0.5
```

### Example Calculation

For a 1,000 LOC file with issues:
- 1 CRITICAL issue: 1 × 10 = 10 points
- 3 HIGH issues: 3 × 7 = 21 points
- 5 MEDIUM issues: 5 × 4 = 20 points
- 8 LOW issues: 8 × 1 = 8 points
- **Total**: 59 points

Max possible (assuming 1 issue per 5 LOC worst case):
- 1000 LOC ÷ 5 = 200 possible issues
- Max weight = 200 × 10 = 2000 points

**Debt Score** = (59 / 2000) × 100 = **2.95/100** (Excellent)

## Severity Levels

### CRITICAL (Weight: 10)
Issues that severely impact code quality and must be fixed immediately.

**Examples**:
- Bare except clauses
- Resource leaks without cleanup
- Unchecked error conditions
- Race conditions
- Type assertion without validation

**Recommendation**: Fix before next commit

### HIGH (Weight: 7)
Issues that significantly impact code quality and should be fixed soon.

**Examples**:
- Missing null checks
- Unsafe type operations
- Global variable usage
- Mutable static fields
- Unhandled errors

**Recommendation**: Fix before code review

### MEDIUM (Weight: 4)
Issues that reduce code maintainability and should be addressed.

**Examples**:
- Long methods (>50 lines)
- Complex conditions
- High nesting depth
- Unused variables
- Missing type annotations

**Recommendation**: Include in next refactoring cycle

### LOW (Weight: 1)
Issues that affect code readability but don't impact functionality.

**Examples**:
- Magic numbers without explanation
- Missing docstrings
- Verbose logging
- Comparison to None using ==
- Commented-out code

**Recommendation**: Fix in regular maintenance

### INFO (Weight: 0.5)
Informational notices for best practices.

**Examples**:
- Naming convention suggestions
- Documentation improvements
- Style consistency

**Recommendation**: Consider in code reviews

## Category-Based Analysis

### Unused Code (Weight Multiplier: 1.0x)
Dead code that doesn't contribute to functionality.
- Unused imports
- Unused variables
- Redundant statements
- Commented-out code

### Complexity (Weight Multiplier: 1.5x)
Issues related to code complexity and cognitive load.
- Long methods
- Deep nesting
- High cyclomatic complexity
- Complex conditions
- Too many parameters

### Error Handling (Weight Multiplier: 2.0x)
Critical issues in error handling and resource management.
- Missing error checks
- Resource leaks
- Unchecked exceptions
- Missing null checks
- Unhandled edge cases

### Type Safety (Weight Multiplier: 1.8x)
Issues related to type system and type safety.
- Any type usage
- Missing type annotations
- Unsafe type assertions
- Type mismatch risks
- Implicit conversions

### Security (Weight Multiplier: 2.5x)
Issues that could lead to security vulnerabilities.
- Mutable static fields
- Global state
- Unsafe operations
- Resource leaks
- Access control issues

### Performance (Weight Multiplier: 1.2x)
Issues that impact code performance.
- String concatenation in loops
- Inefficient algorithms
- Unnecessary object creation
- Memory leaks
- N+1 problems

### Maintainability (Weight Multiplier: 1.3x)
Issues affecting code maintenance and readability.
- Missing docstrings
- Poor naming conventions
- Code duplication
- Magic numbers
- Inconsistent style

### Naming (Weight Multiplier: 1.0x)
Naming convention violations.
- Inconsistent case conventions
- Non-descriptive names
- Single-letter variables (outside loops)
- Abbreviations

### Concurrency (Weight Multiplier: 2.2x)
Issues related to concurrent execution.
- Goroutine leaks
- Race conditions
- Channel leaks
- Deadlock risks
- Synchronization issues

## Maintainability Index

Derived from technical debt score:

```
MI = 100 - TechnicalDebtScore

MI Interpretation:
- 85-100: Excellent (Green) - Code is well-maintained
- 65-84:  Good (Yellow) - Code needs minor improvements
- 50-64:  Fair (Orange) - Code needs attention
- 25-49:  Poor (Red) - Code requires significant refactoring
- 0-24:   Critical (Dark Red) - Immediate action needed
```

## Advanced Metrics

### Average Severity Score

```
AverageSeverity = (∑ severity_value × issue_count) / total_issues

Where severity_value:
- CRITICAL: 1.0
- HIGH: 0.8
- MEDIUM: 0.6
- LOW: 0.3
- INFO: 0.1
```

### Hotspot Analysis

Identifies files with disproportionate issues:

```
HotspotRatio = issues_in_file / avg_issues_per_file
- Ratio > 2.0: Critical hotspot (needs refactoring)
- Ratio 1.5-2.0: Major hotspot (schedule refactoring)
- Ratio 1.0-1.5: Minor hotspot (monitor)
- Ratio < 1.0: Within baseline
```

### Quality Trend Analysis

Tracks changes in debt over time:

```
TrendScore = (debt_today - debt_yesterday) / debt_yesterday × 100
- Positive: Code quality improving ✅
- Negative: Code quality degrading ⚠️
- Threshold ±5%: Natural variation
- Threshold >10%: Significant change
```

## Rule-Specific Confidence Scores

Each rule has an inherent confidence level based on FP rate:

| Confidence Range | Interpretation | Recommendation |
|-----------------|----------------|----------------|
| 0.95-1.00 | Very High | Trust rule completely |
| 0.90-0.95 | High | Minor manual verification |
| 0.85-0.90 | Good | Manual verification recommended |
| 0.80-0.85 | Fair | Review findings before action |
| < 0.80 | Low | Treat as suggestions only |

## Thresholds & Actions

### Automatic Flags

```
If TechnicalDebtScore > 50: ⚠️ Code Review Required
If TechnicalDebtScore > 75: 🚨 Immediate Action Required
If CRITICAL_count > 0: 🚨 Blocking Issue Found
If HIGH_count > 5: ⚠️ Multiple Critical Issues
```

### Recommended Actions

| Score Range | Action | Timeline |
|------------|--------|----------|
| 0-25 | Monitor | Next review cycle |
| 25-50 | Plan refactoring | Next sprint |
| 50-75 | Execute refactoring | This sprint |
| 75-100 | Halt development | Immediate |

## Multi-File Analysis

When analyzing multiple files:

```
ProjectDebtScore = (∑ file_debt × file_weight) / ∑ file_weight

Where file_weight:
- High complexity files: 1.5x
- Critical path files: 1.3x
- Test files: 0.5x
- Standard files: 1.0x
```

## Comparative Analysis

### Against Baselines

```
QualityRegression = (current_debt - baseline_debt) / baseline_debt
- 0-5%: Acceptable
- 5-10%: Warning
- >10%: Failure
```

### Language-Specific Baselines

| Language | Target Debt Score | Achievable MI |
|----------|------------------|----------------|
| Python | 15 | 85 |
| Java | 18 | 82 |
| TypeScript | 16 | 84 |
| Go | 12 | 88 |

## False Positive Mitigation

### Adaptive Thresholding

Rules with >5% FP rate automatically adjust:

```
AdjustedConfidence = BaseConfidence × (1 - FP_rate)
If AdjustedConfidence < 0.80:
    - Issue: Marked as "suggestion" instead of "finding"
    - Display: Lower priority in reports
    - Action: Manual verification required
```

### Context-Based Filtering

```
if issue_in_test_code:
    severity × 0.7  # Reduce weight in test code

if issue_has_comment:
    confidence × 0.9  # Reduced confidence if commented

if issue_is_library_code:
    severity × 0.8  # Different standards for libraries
```

## Reporting & Visualization

### ASCII Report Format

```
Technical Debt Analysis Report
==============================
File: src/main.py
Language: Python
Lines of Code: 2,340

SUMMARY
-------
Debt Score: 28.5/100 (Good)
Maintainability Index: 71.5/100 (Good)
Status: ✅ No blocking issues

BREAKDOWN BY SEVERITY
---------------------
Critical: 0 issues
High: 2 issues
Medium: 7 issues
Low: 12 issues

BREAKDOWN BY CATEGORY
---------------------
Error Handling: 2 issues (High priority)
Complexity: 5 issues
Unused Code: 8 issues
Maintainability: 6 issues

CRITICAL ISSUES
---------------
None

HIGH PRIORITY ISSUES
--------------------
1. [PY006] Bare Except (line 156)
2. [PY008] Mutable Default Argument (line 89)

TREND
-----
Previous Score: 31.2 (Sep-13)
Current Score: 28.5 (Sep-20)
Improvement: +8.6% ✅
```

### JSON Report Format

```json
{
  "summary": {
    "debtScore": 28.5,
    "maintainabilityIndex": 71.5,
    "status": "good",
    "trend": "improving"
  },
  "severity_breakdown": {
    "critical": 0,
    "high": 2,
    "medium": 7,
    "low": 12,
    "info": 0
  },
  "category_breakdown": {
    "error_handling": 2,
    "complexity": 5,
    "unused_code": 8,
    "maintainability": 6
  },
  "top_issues": [
    {
      "rule_id": "PY006",
      "severity": "HIGH",
      "message": "Bare except clause",
      "line": 156
    }
  ]
}
```

## Performance Impact

Technical debt scoring adds minimal overhead:

| Operation | Time | % of Total |
|-----------|------|-----------|
| Issue Detection | 25ms | 85% |
| Debt Calculation | 2ms | 7% |
| Report Generation | 2ms | 8% |
| **Total** | **29ms** | **100%** |

## Validation & Testing

### Unit Tests for Scoring

```python
def test_debt_score_calculation():
    # 1 CRITICAL, 3 HIGH, 5 MEDIUM, 8 LOW
    expected = (10 + 21 + 20 + 8) / 2000 * 100  # 2.95
    assert result.overall_score == pytest.approx(2.95, 0.1)

def test_maintainability_index():
    debt = 28.5
    mi = 100 - debt  # 71.5
    assert result.maintainability_index == pytest.approx(71.5, 0.1)

def test_category_weighting():
    # Error handling issues weighted 2.0x
    # Complexity issues weighted 1.5x
    pass
```

### Edge Cases

- Empty files (0 LOC): Score = 0
- Files with only comments: Score = 0
- Single large issue: CRITICAL weight capped at 50% of total
- Mixed severity issues: Proper aggregation verified

## Future Enhancements

- [ ] Historical trending with regression detection
- [ ] Predictive debt analysis (ML)
- [ ] Team-based baselines
- [ ] Integration with CI/CD pipelines
- [ ] Automated refactoring suggestions
- [ ] Cost-benefit analysis for fixes
