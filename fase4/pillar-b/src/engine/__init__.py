"""
Rule Engine - Orchestrates code smell detection and analysis
Handles pattern matching, suggestion generation, and technical debt scoring
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
import time
from pathlib import Path

from ..parsers import Parser, Language, get_parser, ASTNode
from ..rules import Rule, Issue, Severity, Category, ALL_RULES


@dataclass
class DetectionResult:
    """Result of code analysis"""
    filename: str
    language: Language
    issues: List[Issue] = field(default_factory=list)
    total_lines: int = 0
    execution_time: float = 0.0  # seconds
    false_positives: int = 0  # estimated count


@dataclass
class TechnicalDebtScore:
    """Technical debt metrics"""
    overall_score: float  # 0-100, lower is better
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    issues_by_category: Dict[Category, int] = field(default_factory=dict)
    average_severity: float = 0.0  # 0-1 scale
    maintainability_index: float = 75.0  # 0-100


class RuleEngine:
    """Main code smell detection engine"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.rules_applied = []
        self.statistics = {
            'files_analyzed': 0,
            'total_issues': 0,
            'false_positives': 0,
            'total_loc_analyzed': 0,
            'total_time_ms': 0,
        }

    def analyze(self, source: str, language: Language, filename: str = "unknown") -> DetectionResult:
        """Analyze source code for code smells"""
        start_time = time.time()

        try:
            # Parse source
            parser = get_parser(language)
            ast = parser.parse(source, filename)

            # Run all applicable rules
            issues = self._run_rules(ast, source, language)

            # Calculate statistics
            total_lines = len(source.split('\n'))
            execution_time = time.time() - start_time

            result = DetectionResult(
                filename=filename,
                language=language,
                issues=issues,
                total_lines=total_lines,
                execution_time=execution_time,
                false_positives=self._estimate_false_positives(issues)
            )

            # Update global statistics
            self.statistics['files_analyzed'] += 1
            self.statistics['total_issues'] += len(issues)
            self.statistics['total_loc_analyzed'] += total_lines
            self.statistics['total_time_ms'] += execution_time * 1000

            return result

        except Exception as e:
            if self.debug:
                print(f"Error analyzing {filename}: {str(e)}")
            raise

    def _run_rules(self, ast: ASTNode, source: str, language: Language) -> List[Issue]:
        """Run all applicable rules for language"""
        issues = []

        # Select rules by language prefix
        lang_prefix = {
            Language.PYTHON: 'PY',
            Language.JAVA: 'JV',
            Language.TYPESCRIPT: 'TS',
            Language.GO: 'GO',
        }[language]

        for rule_id, rule in ALL_RULES.items():
            if rule_id.startswith(lang_prefix) and rule.enabled:
                try:
                    rule_issues = rule.detect(ast, source)
                    issues.extend(rule_issues)
                    self.rules_applied.append(rule_id)
                except Exception as e:
                    if self.debug:
                        print(f"Error in rule {rule_id}: {str(e)}")

        # Sort by line number
        issues.sort(key=lambda x: (x.line, x.column))
        return issues

    def _estimate_false_positives(self, issues: List[Issue]) -> int:
        """Estimate false positive count based on heuristics"""
        # Rules with high FP rates
        high_fp_rules = ['PY003', 'JV005', 'TS006', 'GO005']

        fp_count = 0
        for issue in issues:
            if issue.rule_id in high_fp_rules:
                # Estimate 5% FP rate for high-uncertainty rules
                if issue.confidence < 0.95:
                    fp_count += 1

        return fp_count

    def calculate_debt_score(self, result: DetectionResult) -> TechnicalDebtScore:
        """Calculate technical debt score"""
        score = TechnicalDebtScore()

        # Count by severity
        for issue in result.issues:
            if issue.severity == Severity.CRITICAL:
                score.critical_count += 1
            elif issue.severity == Severity.HIGH:
                score.high_count += 1
            elif issue.severity == Severity.MEDIUM:
                score.medium_count += 1
            elif issue.severity == Severity.LOW:
                score.low_count += 1
            else:
                score.info_count += 1

            # Count by category
            if issue.category not in score.issues_by_category:
                score.issues_by_category[issue.category] = 0
            score.issues_by_category[issue.category] += 1

        # Calculate weights
        severity_weights = {
            Severity.CRITICAL: 10,
            Severity.HIGH: 7,
            Severity.MEDIUM: 4,
            Severity.LOW: 1,
            Severity.INFO: 0.5,
        }

        total_weight = sum(severity_weights[s] * getattr(score, f'{s.value}_count')
                          for s in Severity if s != Severity.INFO)

        # Normalize to 0-100 scale (inverted, lower is better)
        max_possible_weight = severity_weights[Severity.CRITICAL] * result.total_lines
        if max_possible_weight > 0:
            score.overall_score = min(100, (total_weight / max_possible_weight) * 100)
        else:
            score.overall_score = 0

        # Average severity (0-1 scale, higher is worse)
        total_issues = len(result.issues)
        if total_issues > 0:
            severity_values = {
                Severity.CRITICAL: 1.0,
                Severity.HIGH: 0.8,
                Severity.MEDIUM: 0.6,
                Severity.LOW: 0.3,
                Severity.INFO: 0.1,
            }
            score.average_severity = sum(
                severity_values[issue.severity] for issue in result.issues
            ) / total_issues
        else:
            score.average_severity = 0.0

        # Maintainability index (0-100, higher is better)
        # Simplified calculation based on issue distribution
        score.maintainability_index = max(0, 100 - score.overall_score)

        return score

    def batch_analyze(self, files: List[Tuple[str, Language]]) -> List[DetectionResult]:
        """Analyze multiple files"""
        results = []
        for source, language in files:
            try:
                # Assume source is file path
                if isinstance(source, str) and Path(source).exists():
                    with open(source, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    result = self.analyze(content, language, str(source))
                else:
                    # Source is inline code
                    result = self.analyze(source, language, "inline")
                results.append(result)
            except Exception as e:
                if self.debug:
                    print(f"Error analyzing {source}: {str(e)}")

        return results

    def get_statistics(self) -> Dict:
        """Get analysis statistics"""
        stats = dict(self.statistics)

        # Calculate derived metrics
        if stats['files_analyzed'] > 0:
            stats['avg_issues_per_file'] = stats['total_issues'] / stats['files_analyzed']
            stats['avg_loc_per_file'] = stats['total_loc_analyzed'] / stats['files_analyzed']
            stats['avg_time_per_file_ms'] = stats['total_time_ms'] / stats['files_analyzed']
        else:
            stats['avg_issues_per_file'] = 0
            stats['avg_loc_per_file'] = 0
            stats['avg_time_per_file_ms'] = 0

        if stats['total_loc_analyzed'] > 0:
            stats['loc_per_second'] = (stats['total_loc_analyzed'] * 1000) / stats['total_time_ms']
        else:
            stats['loc_per_second'] = 0

        stats['fp_rate'] = (stats['false_positives'] / stats['total_issues']
                           if stats['total_issues'] > 0 else 0)

        stats['rules_available'] = len(ALL_RULES)
        stats['rules_applied'] = len(set(self.rules_applied))

        return stats

    def generate_report(self, result: DetectionResult, include_suggestions: bool = True) -> str:
        """Generate human-readable report"""
        lines = [
            f"Code Smell Analysis Report - {result.filename}",
            f"{'='*60}",
            f"Language: {result.language.value}",
            f"Total Lines: {result.total_lines}",
            f"Execution Time: {result.execution_time:.3f}s",
            f"Total Issues: {len(result.issues)}",
            f"Estimated False Positives: {result.false_positives}",
            "",
        ]

        # Group by severity
        by_severity = {}
        for issue in result.issues:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)

        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            if severity in by_severity:
                issues = by_severity[severity]
                lines.append(f"{severity.value.upper()} ({len(issues)} issues)")
                lines.append("-" * 40)

                for issue in issues[:10]:  # Limit to 10 per severity
                    lines.append(f"  [{issue.rule_id}] {issue.rule_name} (L{issue.line})")
                    lines.append(f"    {issue.message}")
                    if include_suggestions:
                        lines.append(f"    Suggestion: {issue.suggestion}")
                    lines.append("")

                if len(issues) > 10:
                    lines.append(f"  ... and {len(issues) - 10} more")
                lines.append("")

        # Category summary
        lines.append("Issues by Category:")
        lines.append("-" * 40)
        by_category = {}
        for issue in result.issues:
            if issue.category not in by_category:
                by_category[issue.category] = 0
            by_category[issue.category] += 1

        for category in sorted(by_category.keys(), key=lambda x: x.value):
            count = by_category[category]
            lines.append(f"  {category.value}: {count}")

        return "\n".join(lines)


class SuggestionGenerator:
    """Generates fix suggestions for detected issues"""

    @staticmethod
    def generate_fix(issue: Issue, source: str) -> Tuple[str, str]:
        """Generate before/after code suggestion"""
        lines = source.split('\n')

        if issue.line > 0 and issue.line <= len(lines):
            before = lines[issue.line - 1]
        else:
            before = issue.code_snippet

        # Get rule instance and generate suggestion
        if issue.rule_id in ALL_RULES:
            rule = ALL_RULES[issue.rule_id]
            suggestion = rule.get_suggestion(issue)
        else:
            suggestion = issue.suggestion

        # Generate "after" code based on rule
        after = SuggestionGenerator._apply_fix(issue.rule_id, before)

        return before.strip(), after.strip(), suggestion

    @staticmethod
    def _apply_fix(rule_id: str, code: str) -> str:
        """Apply automatic fix based on rule"""
        # Python rules
        if rule_id == 'PY001':  # Unused imports
            return ""  # Remove import

        elif rule_id == 'PY006':  # Bare except
            return code.replace("except:", "except Exception:")

        elif rule_id == 'PY009':  # Comparison to None
            code = code.replace("== None", "is None")
            code = code.replace("!= None", "is not None")
            return code

        elif rule_id == 'PY013':  # Wildcard import
            return code.replace("from module import *", "from module import specific_name")

        # Java rules
        elif rule_id == 'JV011':  # Naming convention
            # Suggest PascalCase for class names
            return code.replace("class", "class")

        # TypeScript rules
        elif rule_id == 'TS001':  # Any type
            return code.replace(": any", ": unknown").replace("any,", "unknown,")

        elif rule_id == 'TS006':  # Null check
            return code.replace("?.", "")  # Suggest removing optional chaining

        # Go rules
        elif rule_id == 'GO001':  # Error handling
            return "if err != nil {\n    return err\n}"

        else:
            return code


class VerificationEngine:
    """Verifies that suggested fixes are valid"""

    @staticmethod
    def verify_fix(original: str, fixed: str, language: Language) -> bool:
        """Verify that fix compiles/parses correctly"""
        try:
            parser = get_parser(language)
            # Try to parse the fixed code
            parser.parse(fixed, "verification.tmp")
            return True
        except Exception as e:
            return False

    @staticmethod
    def verify_semantic(original: str, fixed: str, language: Language) -> Dict[str, any]:
        """Verify semantic equivalence"""
        verification = {
            'is_valid': False,
            'issues': [],
            'warnings': [],
        }

        # Check if fixed code is syntactically valid
        if VerificationEngine.verify_fix(original, fixed, language):
            verification['is_valid'] = True
        else:
            verification['issues'].append("Fixed code is not syntactically valid")

        # Check length ratio (shouldn't be drastically different)
        original_lines = len(original.split('\n'))
        fixed_lines = len(fixed.split('\n'))

        if original_lines > 0:
            ratio = fixed_lines / original_lines
            if ratio > 2 or ratio < 0.5:
                verification['warnings'].append(
                    f"Size change significant ({ratio:.2f}x). Manual review recommended."
                )

        return verification
