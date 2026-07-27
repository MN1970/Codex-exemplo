"""
Code Smell Detection Rules - 55 rules across 4 languages
Python: 15 rules
Java: 15 rules
TypeScript: 15 rules
Go: 10 rules
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import ast
import re


class Severity(Enum):
    """Rule severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Category(Enum):
    """Code smell categories"""
    UNUSED_CODE = "unused_code"
    COMPLEXITY = "complexity"
    NAMING = "naming"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    TYPE_SAFETY = "type_safety"
    MEMORY = "memory"
    CONCURRENCY = "concurrency"


@dataclass
class Issue:
    """Detected code smell issue"""
    rule_id: str
    rule_name: str
    severity: Severity
    category: Category
    line: int
    column: int
    message: str
    suggestion: str
    code_snippet: str = ""
    confidence: float = 0.95  # 0.0-1.0 confidence score


class Rule(ABC):
    """Abstract base class for detection rules"""

    rule_id: str
    name: str
    severity: Severity
    category: Category
    enabled: bool = True

    @abstractmethod
    def detect(self, ast_node, source: str) -> List[Issue]:
        """Detect issues in AST"""
        pass

    @abstractmethod
    def get_suggestion(self, issue: Issue) -> str:
        """Generate fix suggestion"""
        pass


# ============================================================================
# PYTHON RULES (15 rules)
# ============================================================================

class PythonUnusedImports(Rule):
    """PY001: Unused imports detection"""
    rule_id = "PY001"
    name = "Unused Imports"
    severity = Severity.MEDIUM
    category = Category.UNUSED_CODE

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        imports = {}  # {name: (line, used_count)}
        names_used = set()

        # Collect imports
        for node in ast.walk(ast_node):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name.split('.')[0]
                    imports[name] = (node.lineno, 0)

        # Count usage
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id in imports:
                    imports[node.id] = (imports[node.id][0], imports[node.id][1] + 1)
                    names_used.add(node.id)

        # Find unused
        for name, (line, count) in imports.items():
            if count == 0 and name != '__all__':
                issues.append(Issue(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    category=self.category,
                    line=line,
                    column=0,
                    message=f"Unused import '{name}'",
                    suggestion=f"Remove unused import '{name}'"
                ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return f"Remove this import: {issue.message}"


class PythonLongMethod(Rule):
    """PY002: Long method detection (>50 lines)"""
    rule_id = "PY002"
    name = "Long Method"
    severity = Severity.MEDIUM
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for node in ast.walk(ast_node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, 'end_lineno'):
                    length = node.end_lineno - node.lineno
                    if length > 50:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=node.lineno,
                            column=0,
                            message=f"Method '{node.name}' is too long ({length} lines)",
                            suggestion=f"Consider breaking down this method into smaller functions"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Extract method: Break this function into smaller, single-responsibility functions"


class PythonDeepNesting(Rule):
    """PY003: Deep nesting detection (>3 levels)"""
    rule_id = "PY003"
    name = "Deep Nesting"
    severity = Severity.MEDIUM
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        def check_depth(node, depth=0, parent_line=0):
            if depth > 3:
                if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=node.lineno,
                        column=0,
                        message=f"Nesting depth {depth} exceeds recommended maximum (3)",
                        suggestion="Extract nested logic into a separate function"
                    ))

            for child in ast.iter_child_nodes(node):
                new_depth = depth + 1 if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)) else depth
                check_depth(child, new_depth, getattr(node, 'lineno', 0))

        check_depth(ast_node)
        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Extract the nested block into a helper function to reduce cognitive complexity"


class PythonComplexCondition(Rule):
    """PY004: Complex conditions (>3 boolean operations)"""
    rule_id = "PY004"
    name = "Complex Condition"
    severity = Severity.LOW
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for node in ast.walk(ast_node):
            if isinstance(node, ast.If):
                bool_ops = sum(1 for _ in ast.walk(node.test) if isinstance(_, ast.BoolOp))
                if bool_ops > 3:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=node.lineno,
                        column=0,
                        message=f"Condition has {bool_ops} boolean operations (recommended max: 3)",
                        suggestion="Extract condition into a named variable or helper function"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Extract the condition into a well-named boolean variable for clarity"


class PythonMissingDocstring(Rule):
    """PY005: Missing docstring"""
    rule_id = "PY005"
    name = "Missing Docstring"
    severity = Severity.LOW
    category = Category.MAINTAINABILITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for node in ast.walk(ast_node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Check if has docstring
                docstring = ast.get_docstring(node)
                if not docstring and node.name not in ('__init__', '__str__', '__repr__'):
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=node.lineno,
                        column=0,
                        message=f"'{node.name}' is missing a docstring",
                        suggestion=f'Add docstring: """Documentation here."""'
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return 'Add a docstring describing the purpose and parameters of this function'


class PythonBareExcept(Rule):
    """PY006: Bare except clause"""
    rule_id = "PY006"
    name = "Bare Except"
    severity = Severity.HIGH
    category = Category.ERROR_HANDLING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for node in ast.walk(ast_node):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=node.lineno,
                        column=0,
                        message="Bare except clause catches all exceptions including SystemExit",
                        suggestion="Specify the exception type: except Exception: or except SpecificError:"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Replace 'except:' with 'except Exception:' to avoid catching SystemExit and KeyboardInterrupt"


class PythonGlobalVariable(Rule):
    """PY007: Global variable usage"""
    rule_id = "PY007"
    name = "Global Variable Usage"
    severity = Severity.HIGH
    category = Category.MAINTAINABILITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for node in ast.walk(ast_node):
            if isinstance(node, ast.Global):
                issues.append(Issue(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    category=self.category,
                    line=node.lineno,
                    column=0,
                    message=f"Global variable '{node.names[0]}' reduces code modularity",
                    suggestion="Use function parameters or class attributes instead"
                ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Pass values as parameters instead of using global variables"


class PythonMutableDefault(Rule):
    """PY008: Mutable default argument"""
    rule_id = "PY008"
    name = "Mutable Default Argument"
    severity = Severity.HIGH
    category = Category.MAINTAINABILITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for node in ast.walk(ast_node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict)):
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=node.lineno,
                            column=0,
                            message=f"Mutable default argument in '{node.name}'",
                            suggestion="Use None as default and create new instance inside function"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use 'def func(arg=None):' and initialize with 'arg = arg or []' inside the function"


class PythonComparisonToNone(Rule):
    """PY009: Comparison to None using =="""
    rule_id = "PY009"
    name = "Comparison to None"
    severity = Severity.LOW
    category = Category.NAMING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for node in ast.walk(ast_node):
            if isinstance(node, ast.Compare):
                for i, op in enumerate(node.ops):
                    if isinstance(op, (ast.Eq, ast.NotEq)):
                        comparator = node.comparators[i]
                        if isinstance(comparator, ast.Constant) and comparator.value is None:
                            issues.append(Issue(
                                rule_id=self.rule_id,
                                rule_name=self.name,
                                severity=self.severity,
                                category=self.category,
                                line=node.lineno,
                                column=0,
                                message="Use 'is' or 'is not' for None comparison",
                                suggestion="Replace '== None' with 'is None' and '!= None' with 'is not None'"
                            ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use 'is None' or 'is not None' instead of '== None' or '!= None'"


class PythonUnusedVariable(Rule):
    """PY010: Unused local variable"""
    rule_id = "PY010"
    name = "Unused Local Variable"
    severity = Severity.MEDIUM
    category = Category.UNUSED_CODE

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for func in ast.walk(ast_node):
            if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            # Collect assigned variables
            assigned = {}
            for node in ast.walk(func):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            assigned[target.id] = node.lineno

            # Check if used
            for var, line in assigned.items():
                used = False
                for node in ast.walk(func):
                    if isinstance(node, ast.Name) and node.id == var and isinstance(node.ctx, ast.Load):
                        used = True
                        break

                if not used and not var.startswith('_'):
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=line,
                        column=0,
                        message=f"Variable '{var}' is assigned but never used",
                        suggestion=f"Remove variable '{var}' or prefix with underscore if intentionally unused"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Remove this variable assignment or use the variable in the code"


class PythonMultipleStatements(Rule):
    """PY011: Multiple statements on one line"""
    rule_id = "PY011"
    name = "Multiple Statements Per Line"
    severity = Severity.LOW
    category = Category.NAMING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = {}

        for node in ast.walk(ast_node):
            if isinstance(node, (ast.stmt, ast.expr)):
                line = getattr(node, 'lineno', None)
                if line:
                    lines[line] = lines.get(line, 0) + 1

        for line, count in lines.items():
            if count > 2:
                issues.append(Issue(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    category=self.category,
                    line=line,
                    column=0,
                    message=f"Line {line} has {count} statements (recommend 1 per line)",
                    suggestion="Split multiple statements onto separate lines"
                ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Split statements across multiple lines for better readability"


class PythonTooManyArguments(Rule):
    """PY012: Too many function arguments"""
    rule_id = "PY012"
    name = "Too Many Arguments"
    severity = Severity.MEDIUM
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for node in ast.walk(ast_node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                arg_count = len(node.args.args)
                if arg_count > 5:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=node.lineno,
                        column=0,
                        message=f"Function '{node.name}' has {arg_count} arguments (recommended max: 5)",
                        suggestion="Consider using a configuration object or dataclass for multiple parameters"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use a dataclass, NamedTuple, or config object to group related parameters"


class PythonWildcardImport(Rule):
    """PY013: Wildcard import (*) usage"""
    rule_id = "PY013"
    name = "Wildcard Import"
    severity = Severity.MEDIUM
    category = Category.MAINTAINABILITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for node in ast.walk(ast_node):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == '*':
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=node.lineno,
                            column=0,
                            message=f"Wildcard import from '{node.module}' pollutes namespace",
                            suggestion="Use explicit imports instead"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Replace 'from module import *' with explicit imports of needed names"


class PythonReassignedBuiltin(Rule):
    """PY014: Reassignment of builtin names"""
    rule_id = "PY014"
    name = "Reassigned Builtin"
    severity = Severity.HIGH
    category = Category.MAINTAINABILITY

    BUILTINS = {'dict', 'list', 'str', 'int', 'float', 'bool', 'set', 'tuple', 'type', 'object', 'super', 'property', 'staticmethod', 'classmethod', 'len', 'range', 'enumerate', 'zip', 'map', 'filter', 'sum', 'max', 'min'}

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for node in ast.walk(ast_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in self.BUILTINS:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=node.lineno,
                            column=0,
                            message=f"Reassignment of builtin '{target.id}'",
                            suggestion=f"Use a different variable name instead of '{target.id}'"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Rename this variable to avoid shadowing builtin functions"


class PythonPassStatement(Rule):
    """PY015: Redundant pass statement"""
    rule_id = "PY015"
    name = "Redundant Pass Statement"
    severity = Severity.LOW
    category = Category.UNUSED_CODE

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        for node in ast.walk(ast_node):
            if isinstance(node, ast.Pass):
                issues.append(Issue(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    category=self.category,
                    line=node.lineno,
                    column=0,
                    message="Redundant 'pass' statement",
                    suggestion="Remove 'pass' or replace with docstring if documenting intention"
                ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Remove 'pass' or replace with a docstring explaining why the block is empty"


# ============================================================================
# JAVA RULES (15 rules)
# ============================================================================

class JavaUnusedVariable(Rule):
    """JV001: Unused variable detection"""
    rule_id = "JV001"
    name = "Unused Variable"
    severity = Severity.MEDIUM
    category = Category.UNUSED_CODE

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []

        # Regex-based detection for Java
        lines = source.split('\n')
        for idx, line in enumerate(lines, 1):
            # Detect variable declarations
            if re.search(r'(private|public|protected)?\s+\w+\s+\w+\s*[=;]', line):
                var_name = re.search(r'\s+(\w+)\s*[=;]', line)
                if var_name and '_' not in var_name.group(1):
                    # Check if variable is used elsewhere (simplified)
                    var = var_name.group(1)
                    if not any(var in l for l in lines[idx:]):
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=idx,
                            column=0,
                            message=f"Variable '{var}' might be unused",
                            suggestion=f"Remove variable or use it in the code"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Remove this variable if it's not needed"


class JavaLongMethod(Rule):
    """JV002: Long method detection"""
    rule_id = "JV002"
    name = "Long Method"
    severity = Severity.MEDIUM
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        in_method = False
        method_start = 0
        open_braces = 0

        for idx, line in enumerate(lines):
            if re.search(r'(public|private|protected)\s+(\w+|void)\s+\w+\s*\(', line):
                in_method = True
                method_start = idx
                open_braces = 0

            if in_method:
                open_braces += line.count('{')
                open_braces -= line.count('}')

                if open_braces == 0 and idx > method_start:
                    length = idx - method_start
                    if length > 50:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=method_start + 1,
                            column=0,
                            message=f"Method is too long ({length} lines)",
                            suggestion="Consider breaking method into smaller methods"
                        ))
                    in_method = False

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Extract this method into smaller, single-responsibility methods"


class JavaTooManyMethods(Rule):
    """JV003: Class with too many methods"""
    rule_id = "JV003"
    name = "Too Many Methods"
    severity = Severity.MEDIUM
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        in_class = False
        class_start = 0
        method_count = 0

        for idx, line in enumerate(lines):
            if 'class ' in line:
                in_class = True
                class_start = idx
                method_count = 0

            if in_class and re.search(r'(public|private|protected)\s+\w+\s+\w+\s*\(', line):
                method_count += 1

            if in_class and line.strip().startswith('}'):
                if method_count > 10:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=class_start + 1,
                        column=0,
                        message=f"Class has {method_count} methods (recommended max: 10)",
                        suggestion="Consider breaking into multiple classes"
                    ))
                in_class = False

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Extract related methods into separate classes following Single Responsibility Principle"


class JavaGetterSetter(Rule):
    """JV004: Detect potential getter/setter patterns"""
    rule_id = "JV004"
    name = "Getter/Setter Potential"
    severity = Severity.LOW
    category = Category.MAINTAINABILITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            # Simple getter pattern detection
            if re.search(r'public\s+\w+\s+get(\w+)\s*\(\)\s*\{\s*return\s+\w+', line):
                if 'private' not in ''.join(lines[max(0, idx-5):idx]):
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Simple getter method found",
                        suggestion="Consider using Lombok @Getter annotation or a record class"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use Lombok @Getter/@Setter annotations or convert to a record class for cleaner code"


class JavaNullCheck(Rule):
    """JV005: Missing null checks"""
    rule_id = "JV005"
    name = "Missing Null Check"
    severity = Severity.HIGH
    category = Category.ERROR_HANDLING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            # Detect method calls on objects without null checks
            if re.search(r'(\w+)\.(\w+)\(', line):
                # Check previous lines for null check
                prev_context = ''.join(lines[max(0, idx-3):idx])
                match = re.search(r'(\w+)\.(\w+)\(', line)
                if match:
                    obj = match.group(1)
                    if f'!= null' not in prev_context and f'if ({obj}' not in prev_context:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=idx + 1,
                            column=0,
                            message=f"Method call on '{obj}' without null check",
                            suggestion=f"Add null check before accessing '{obj}'"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Add null check or use Optional/Objects.requireNonNull before accessing the object"


class JavaEmptyCatchBlock(Rule):
    """JV006: Empty catch blocks"""
    rule_id = "JV006"
    name = "Empty Catch Block"
    severity = Severity.HIGH
    category = Category.ERROR_HANDLING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'catch' in line:
                # Check if next lines have actual code
                next_lines = ''.join(lines[idx:min(idx+3, len(lines))])
                if re.search(r'catch\s*\([^)]+\)\s*\{[\s}]', next_lines.replace('\n', '')):
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Empty catch block found",
                        suggestion="Log the exception or handle it appropriately"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Replace empty catch with appropriate error handling: log, rethrow, or handle exception"


class JavaComplexClass(Rule):
    """JV007: Overly complex class structure"""
    rule_id = "JV007"
    name = "Complex Class"
    severity = Severity.MEDIUM
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        in_class = False
        class_start = 0
        nested_count = 0

        for idx, line in enumerate(lines):
            if 'class ' in line:
                in_class = True
                class_start = idx
                nested_count = line.count('{') - line.count('}')

            if in_class:
                nested_count += line.count('{') - line.count('}')

                if nested_count == 0 and idx > class_start:
                    if line.count('{') == 0:
                        if idx - class_start > 100:
                            issues.append(Issue(
                                rule_id=self.rule_id,
                                rule_name=self.name,
                                severity=self.severity,
                                category=self.category,
                                line=class_start + 1,
                                column=0,
                                message=f"Class is too complex ({idx - class_start} lines)",
                                suggestion="Consider breaking into multiple smaller classes"
                            ))
                        in_class = False

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Decompose this class using composition or delegation patterns"


class JavaStringConcatenation(Rule):
    """JV008: String concatenation in loops"""
    rule_id = "JV008"
    name = "String Concatenation in Loop"
    severity = Severity.MEDIUM
    category = Category.PERFORMANCE

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'for' in line or 'while' in line:
                # Check next 5 lines for string concatenation
                context = ''.join(lines[idx:min(idx+5, len(lines))])
                if '+=' in context and ('"' in context or "'" in context):
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="String concatenation in loop (performance issue)",
                        suggestion="Use StringBuilder instead of string concatenation in loops"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use StringBuilder to accumulate strings in loops for better performance"


class JavaMagicNumber(Rule):
    """JV009: Magic numbers without explanation"""
    rule_id = "JV009"
    name = "Magic Number"
    severity = Severity.LOW
    category = Category.NAMING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            # Detect magic numbers
            if re.search(r'[^\w]([0-9]{2,})[^\w]', line):
                if 'final' not in line and '0x' not in line:
                    match = re.search(r'[^\w]([0-9]{2,})[^\w]', line)
                    if match:
                        number = match.group(1)
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=idx + 1,
                            column=0,
                            message=f"Magic number '{number}' found",
                            suggestion=f"Extract to a named constant: final int {number.upper()} = {number};"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Extract magic number into a named constant with a meaningful name"


class JavaCyclomaticComplexity(Rule):
    """JV010: High cyclomatic complexity"""
    rule_id = "JV010"
    name = "High Cyclomatic Complexity"
    severity = Severity.MEDIUM
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if re.search(r'(public|private)\s+\w+\s+\w+\s*\(', line):
                # Count decision points in method
                method_lines = []
                method_start = idx
                open_braces = 0

                for jdx in range(idx, min(idx + 50, len(lines))):
                    method_lines.append(lines[jdx])
                    open_braces += lines[jdx].count('{')
                    open_braces -= lines[jdx].count('}')

                    if open_braces == 0 and jdx > idx:
                        complexity = sum(1 for l in method_lines if any(x in l for x in ['if ', 'for ', 'while ', 'case ', '?']))
                        if complexity > 5:
                            issues.append(Issue(
                                rule_id=self.rule_id,
                                rule_name=self.name,
                                severity=self.severity,
                                category=self.category,
                                line=method_start + 1,
                                column=0,
                                message=f"Cyclomatic complexity {complexity} exceeds threshold (5)",
                                suggestion="Extract conditional logic into separate methods"
                            ))
                        break

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Reduce complexity by extracting conditional branches into separate methods"


class JavaNamingConvention(Rule):
    """JV011: Naming convention violations"""
    rule_id = "JV011"
    name = "Naming Convention Violation"
    severity = Severity.LOW
    category = Category.NAMING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            # Check for camelCase in class names
            class_match = re.search(r'class\s+([a-z_]\w*)', line)
            if class_match:
                class_name = class_match.group(1)
                if '_' in class_name or class_name[0].islower():
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message=f"Class name '{class_name}' doesn't follow PascalCase convention",
                        suggestion=f"Rename to PascalCase: {class_name.title()}"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Follow Java naming conventions: class names in PascalCase, variables in camelCase"


class JavaStaticField(Rule):
    """JV012: Mutable static fields"""
    rule_id = "JV012"
    name = "Mutable Static Field"
    severity = Severity.HIGH
    category = Category.SECURITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'static' in line and not 'final' in line:
                # Could be mutable static
                if any(dtype in line for dtype in ['List', 'Map', 'Set', 'String']):
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Mutable static field found",
                        suggestion="Make field final or provide thread-safe access methods"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Either make this field final or use thread-safe access patterns (locks, volatile)"


class JavaDuplicateCode(Rule):
    """JV013: Duplicate code detection"""
    rule_id = "JV013"
    name = "Duplicate Code"
    severity = Severity.MEDIUM
    category = Category.MAINTAINABILITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        # Simple duplicate detection
        seen_blocks = {}
        for idx, line in enumerate(lines):
            if len(line) > 20:  # Only check substantial lines
                if line in seen_blocks:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message=f"Duplicate code block (also at line {seen_blocks[line]})",
                        suggestion="Extract duplicate code into a shared method"
                    ))
                else:
                    seen_blocks[line] = idx + 1

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Extract the common logic into a shared method to reduce duplication"


class JavaVerboseLogging(Rule):
    """JV014: Overly verbose logging"""
    rule_id = "JV014"
    name = "Verbose Logging"
    severity = Severity.LOW
    category = Category.MAINTAINABILITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        log_count = {}
        method_start = 0

        for idx, line in enumerate(lines):
            if 'public' in line or 'private' in line:
                method_start = idx

            if 'log.' in line or 'System.out' in line:
                method_key = method_start
                log_count[method_key] = log_count.get(method_key, 0) + 1

                if log_count[method_key] > 5:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Excessive logging statements",
                        suggestion="Use log levels appropriately: info, debug, warn, error"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use appropriate log levels and avoid logging every line of execution"


class JavaResourceLeak(Rule):
    """JV015: Potential resource leak"""
    rule_id = "JV015"
    name = "Potential Resource Leak"
    severity = Severity.HIGH
    category = Category.ERROR_HANDLING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            # Detect resource creation without try-with-resources
            if 'new FileInputStream' in line or 'new File Reader' in line or 'new Socket' in line:
                # Check if try-with-resources is used
                context = ''.join(lines[max(0, idx-2):idx+3])
                if 'try' not in context:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Resource creation without try-with-resources",
                        suggestion="Use try-with-resources: try (Resource res = new Resource()) {...}"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use try-with-resources statement to ensure resource cleanup"


# ============================================================================
# TYPESCRIPT RULES (15 rules)
# ============================================================================

class TypeScriptAnyType(Rule):
    """TS001: Usage of 'any' type"""
    rule_id = "TS001"
    name = "Any Type Usage"
    severity = Severity.HIGH
    category = Category.TYPE_SAFETY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if ': any' in line or ': any;' in line or ': any,' in line:
                issues.append(Issue(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    category=self.category,
                    line=idx + 1,
                    column=0,
                    message="Usage of 'any' type bypasses type checking",
                    suggestion="Use specific types or generics instead of 'any'"
                ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Replace 'any' with a specific type or use generics for better type safety"


class TypeScriptUnusedVariable(Rule):
    """TS002: Unused variable or parameter"""
    rule_id = "TS002"
    name = "Unused Variable"
    severity = Severity.MEDIUM
    category = Category.UNUSED_CODE

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        # Simplified detection
        for idx, line in enumerate(lines):
            if re.search(r'(const|let|var)\s+\w+\s*[:=]', line):
                match = re.search(r'(const|let|var)\s+(\w+)\s*[:=]', line)
                if match:
                    var_name = match.group(2)
                    # Check if used in following lines
                    remaining = ''.join(lines[idx+1:])
                    if var_name not in remaining and '_' not in var_name:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=idx + 1,
                            column=0,
                            message=f"Variable '{var_name}' is declared but never used",
                            suggestion=f"Remove variable or use it in the code"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Remove this unused variable or use it"


class TypeScriptImplicitAny(Rule):
    """TS003: Implicit any types"""
    rule_id = "TS003"
    name = "Implicit Any"
    severity = Severity.MEDIUM
    category = Category.TYPE_SAFETY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            # Detect parameters without type annotation
            if 'function ' in line or '=>' in line:
                if re.search(r'\(\w+\)', line):
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Parameter has implicit 'any' type",
                        suggestion="Add explicit type annotation"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Add explicit type annotation to parameters for type safety"


class TypeScriptPromiseHandling(Rule):
    """TS004: Improper async/Promise handling"""
    rule_id = "TS004"
    name = "Promise Handling"
    severity = Severity.HIGH
    category = Category.CONCURRENCY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            # Detect Promise creation without .catch()
            if 'new Promise' in line or '.then(' in line:
                context = ''.join(lines[idx:min(idx+5, len(lines))])
                if '.catch' not in context:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Promise without error handling",
                        suggestion="Add .catch() handler or use try/catch in async function"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Add error handling with .catch() or use try/catch in async function"


class TypeScriptLongFunction(Rule):
    """TS005: Long function (>50 lines)"""
    rule_id = "TS005"
    name = "Long Function"
    severity = Severity.MEDIUM
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        in_function = False
        func_start = 0
        open_braces = 0

        for idx, line in enumerate(lines):
            if 'function ' in line or '=>' in line or 'class ' in line:
                in_function = True
                func_start = idx
                open_braces = 0

            if in_function:
                open_braces += line.count('{')
                open_braces -= line.count('}')

                if open_braces == 0 and idx > func_start:
                    length = idx - func_start
                    if length > 50:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=func_start + 1,
                            column=0,
                            message=f"Function is too long ({length} lines)",
                            suggestion="Extract into smaller functions"
                        ))
                    in_function = False

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Break this function into smaller, single-purpose functions"


class TypeScriptNullCheck(Rule):
    """TS006: Missing null/undefined checks"""
    rule_id = "TS006"
    name = "Missing Null Check"
    severity = Severity.HIGH
    category = Category.TYPE_SAFETY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            # Detect property access without null check
            if re.search(r'(\w+)\?.(\w+)\s*\)', line):
                match = re.search(r'(\w+)\?.(\w+)', line)
                if match:
                    obj = match.group(1)
                    prop = match.group(2)
                    # Check for null check in previous lines
                    prev = ''.join(lines[max(0, idx-3):idx])
                    if f'if ({obj}' not in prev:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=idx + 1,
                            column=0,
                            message=f"Property access '{prop}' without prior null check",
                            suggestion="Add null check or use optional chaining"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Add null check or use optional chaining (?.) operator"


class TypeScriptUnusedImport(Rule):
    """TS007: Unused imports"""
    rule_id = "TS007"
    name = "Unused Import"
    severity = Severity.MEDIUM
    category = Category.UNUSED_CODE

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        imports = {}
        for idx, line in enumerate(lines):
            if 'import ' in line:
                match = re.search(r'import\s+(?:\{([^}]+)\}|(\w+))\s+from', line)
                if match:
                    items = match.group(1) if match.group(1) else match.group(2)
                    for item in items.split(','):
                        item = item.strip()
                        imports[item] = idx + 1

        # Check if imports are used
        for import_name, line_num in imports.items():
            source_without_imports = '\n'.join([l for l in lines if 'import' not in l])
            if import_name not in source_without_imports:
                issues.append(Issue(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    category=self.category,
                    line=line_num,
                    column=0,
                    message=f"Unused import '{import_name}'",
                    suggestion=f"Remove unused import"
                ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Remove this unused import"


class TypeScriptComplexCondition(Rule):
    """TS008: Complex conditional expression"""
    rule_id = "TS008"
    name = "Complex Condition"
    severity = Severity.LOW
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'if ' in line:
                # Count boolean operators
                count = line.count('&&') + line.count('||') + line.count('?')
                if count > 3:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message=f"Complex condition with {count} boolean operators",
                        suggestion="Extract condition into a named variable or helper function"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Extract the condition into a well-named variable for better readability"


class TypeScriptConsoleLog(Rule):
    """TS009: console.log in production code"""
    rule_id = "TS009"
    name = "Console.log in Production"
    severity = Severity.LOW
    category = Category.MAINTAINABILITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'console.' in line and not '//' in line[:line.find('console.')]:
                issues.append(Issue(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    category=self.category,
                    line=idx + 1,
                    column=0,
                    message="console.log statement found",
                    suggestion="Remove or use proper logging framework"
                ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Replace console.log with a proper logging framework or remove for production"


class TypeScriptMissingReturn(Rule):
    """TS010: Missing return type annotation"""
    rule_id = "TS010"
    name = "Missing Return Type"
    severity = Severity.MEDIUM
    category = Category.TYPE_SAFETY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'function ' in line or '=>' in line:
                if ')' in line and ':' not in line.split(')')[0]:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Function missing return type annotation",
                        suggestion="Add return type annotation: function() -> ReturnType"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Add explicit return type annotation for better type safety"


class TypeScriptTooManyParameters(Rule):
    """TS011: Function with too many parameters"""
    rule_id = "TS011"
    name = "Too Many Parameters"
    severity = Severity.MEDIUM
    category = Category.COMPLEXITY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'function ' in line or '=>' in line:
                match = re.search(r'\(([^)]*)\)', line)
                if match:
                    params = match.group(1)
                    param_count = len([p for p in params.split(',') if p.strip()])
                    if param_count > 5:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=idx + 1,
                            column=0,
                            message=f"Function has {param_count} parameters (recommended max: 5)",
                            suggestion="Use object parameter or options pattern"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use an options object or interface to group multiple parameters"


class TypeScriptNoExplicitAny(Rule):
    """TS012: Explicit any without justification"""
    rule_id = "TS012"
    name = "Explicit Any"
    severity = Severity.HIGH
    category = Category.TYPE_SAFETY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'any' in line and '//' not in line[:line.find('any') if 'any' in line else 0]:
                if ': any' in line:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Explicit 'any' type without TSLint override comment",
                        suggestion="Either add @ts-ignore comment or use specific type"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Replace 'any' with a specific type or add '@ts-ignore' comment with explanation"


class TypeScriptAssertion(Rule):
    """TS013: Type assertion usage"""
    rule_id = "TS013"
    name = "Type Assertion"
    severity = Severity.MEDIUM
    category = Category.TYPE_SAFETY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if ' as ' in line:
                issues.append(Issue(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    category=self.category,
                    line=idx + 1,
                    column=0,
                    message="Type assertion used (bypasses type checking)",
                    suggestion="Use proper typing instead of type assertion"
                ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Avoid type assertions (as) and instead properly type your variables and functions"


class TypeScriptStaticAnalysis(Rule):
    """TS014: Potential null pointer dereference"""
    rule_id = "TS014"
    name = "Null Dereference"
    severity = Severity.HIGH
    category = Category.TYPE_SAFETY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if '!' in line and '!=' not in line and '!==' not in line:
                if '.constructor' in line or '.prototype' in line:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Non-null assertion operator used (unsound)",
                        suggestion="Add proper null checks instead of asserting non-null"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Replace '!' with proper null checks to avoid potential runtime errors"


class TypeScriptDeadCode(Rule):
    """TS015: Dead code detection"""
    rule_id = "TS015"
    name = "Dead Code"
    severity = Severity.LOW
    category = Category.UNUSED_CODE

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if line.strip().startswith('//'):
                if 'TODO' not in line and 'FIXME' not in line:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Commented out code found",
                        suggestion="Remove or replace with proper logging/debug code"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Remove commented code or replace with proper logging statements"


# ============================================================================
# GO RULES (10 rules)
# ============================================================================

class GoErrorHandling(Rule):
    """GO001: Missing error handling"""
    rule_id = "GO001"
    name = "Missing Error Handling"
    severity = Severity.HIGH
    category = Category.ERROR_HANDLING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if re.search(r'(\w+)\s*:=\s*\w+\.\w+\(', line):
                # Check if err is handled
                context = ''.join(lines[idx:min(idx+3, len(lines))])
                if 'if err != nil' not in context:
                    match = re.search(r'(\w+)\s*:=', line)
                    if match:
                        var = match.group(1)
                        if var != '_':
                            issues.append(Issue(
                                rule_id=self.rule_id,
                                rule_name=self.name,
                                severity=self.severity,
                                category=self.category,
                                line=idx + 1,
                                column=0,
                                message="Potential error not checked",
                                suggestion="Add 'if err != nil { ... }' error check"
                            ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Add proper error handling: if err != nil { return err } or handle appropriately"


class GoDeferCleanup(Rule):
    """GO002: Missing defer for resource cleanup"""
    rule_id = "GO002"
    name = "Missing Defer Cleanup"
    severity = Severity.HIGH
    category = Category.ERROR_HANDLING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'Open(' in line or 'Create(' in line or 'Dial(' in line:
                context = ''.join(lines[idx:min(idx+3, len(lines))])
                if 'defer' not in context:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Resource created without defer cleanup",
                        suggestion="Add 'defer resource.Close()' to ensure cleanup"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use defer statement to ensure resource cleanup: defer resource.Close()"


class GoInterfaceCompliance(Rule):
    """GO003: Interface compliance not verified"""
    rule_id = "GO003"
    name = "Interface Compliance"
    severity = Severity.MEDIUM
    category = Category.TYPE_SAFETY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        # Detect interface definitions without compliance checks
        for idx, line in enumerate(lines):
            if 'type ' in line and 'interface' in line:
                # Check if implementation has _ = check line
                context = ''.join(lines[idx:min(idx+20, len(lines))])
                if 'var _ ' not in context:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Interface implementation not verified at compile time",
                        suggestion="Add 'var _ Interface = (*Struct)(nil)' to verify implementation"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Add compile-time interface compliance check: var _ Interface = (*Impl)(nil)"


class GoUnusedVariable(Rule):
    """GO004: Unused variable or import"""
    rule_id = "GO004"
    name = "Unused Variable"
    severity = Severity.MEDIUM
    category = Category.UNUSED_CODE

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        # Check for imports
        for idx, line in enumerate(lines):
            if 'import ' in line and '"' in line:
                match = re.search(r'import\s+"([^"]+)"', line)
                if match:
                    import_path = match.group(1)
                    if import_path not in ''.join(lines):
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=idx + 1,
                            column=0,
                            message=f"Unused import '{import_path}'",
                            suggestion="Remove unused import"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Remove the unused import or variable"


class GoNilCheck(Rule):
    """GO005: Missing nil check"""
    rule_id = "GO005"
    name = "Missing Nil Check"
    severity = Severity.HIGH
    category = Category.ERROR_HANDLING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if re.search(r'(\w+)\.(\w+)\(', line):
                prev_context = ''.join(lines[max(0, idx-2):idx])
                match = re.search(r'(\w+)\.(\w+)\(', line)
                if match:
                    var = match.group(1)
                    if f'if {var} != nil' not in prev_context and f'if {var} == nil' not in prev_context:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=idx + 1,
                            column=0,
                            message=f"Method call on '{var}' without nil check",
                            suggestion=f"Add nil check: if {var} != nil {{ ... }}"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Add nil check before calling methods on pointers"


class GoTypeAssertion(Rule):
    """GO006: Unchecked type assertion"""
    rule_id = "GO006"
    name = "Unchecked Type Assertion"
    severity = Severity.HIGH
    category = Category.ERROR_HANDLING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if '.(Type)' in line or re.search(r'\.\([^)]+\)', line):
                # Check if assertion result is checked
                context = line
                if ', ok :=' not in context and '= .*(' not in context:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Type assertion result not checked for success",
                        suggestion="Use 'value, ok := x.(Type)' and check ok"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Always check type assertion result: value, ok := x.(Type); if !ok { ... }"


class GoChannelLeak(Rule):
    """GO007: Channel not closed or received from"""
    rule_id = "GO007"
    name = "Channel Leak"
    severity = Severity.HIGH
    category = Category.CONCURRENCY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'make(chan' in line:
                var_match = re.search(r'(\w+)\s*:=\s*make\(chan', line)
                if var_match:
                    var = var_match.group(1)
                    context = ''.join(lines[idx:])
                    if f'close({var})' not in context:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=idx + 1,
                            column=0,
                            message=f"Channel '{var}' might not be closed",
                            suggestion=f"Ensure 'close({var})' is called when done"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Close the channel when done to avoid goroutine leaks"


class GoGoroutineLeak(Rule):
    """GO008: Potential goroutine leak"""
    rule_id = "GO008"
    name = "Goroutine Leak"
    severity = Severity.HIGH
    category = Category.CONCURRENCY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'go ' in line and 'func()' in line:
                # Check if goroutine is waited on or controlled
                context = ''.join(lines[idx:min(idx+10, len(lines))])
                if 'Wait' not in context and 'select' not in context:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity=self.severity,
                        category=self.category,
                        line=idx + 1,
                        column=0,
                        message="Goroutine started without synchronization",
                        suggestion="Use WaitGroup or context.Context to manage goroutine lifecycle"
                    ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use sync.WaitGroup or context.Context to properly manage goroutine lifecycle"


class GoRaceCondition(Rule):
    """GO009: Potential race condition"""
    rule_id = "GO009"
    name = "Race Condition"
    severity = Severity.HIGH
    category = Category.CONCURRENCY

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        # Simplified detection
        for idx, line in enumerate(lines):
            if 'go ' in line:
                # Check if accessing shared state
                prev_context = ''.join(lines[max(0, idx-5):idx])
                if re.search(r'(\w+)\s*=', prev_context):
                    var_match = re.search(r'(\w+)\s*=', prev_context)
                    if var_match:
                        var = var_match.group(1)
                        # Check if mutex is used
                        if 'Lock()' not in prev_context:
                            issues.append(Issue(
                                rule_id=self.rule_id,
                                rule_name=self.name,
                                severity=self.severity,
                                category=self.category,
                                line=idx + 1,
                                column=0,
                                message="Possible race condition on shared variable",
                                suggestion="Protect shared state with sync.Mutex"
                            ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Protect shared state with sync.Mutex or use sync.atomic for safe concurrent access"


class GoPackageNaming(Rule):
    """GO010: Package naming convention violations"""
    rule_id = "GO010"
    name = "Package Naming"
    severity = Severity.LOW
    category = Category.NAMING

    def detect(self, ast_node, source: str) -> List[Issue]:
        issues = []
        lines = source.split('\n')

        for idx, line in enumerate(lines):
            if 'package ' in line:
                match = re.search(r'package\s+(\w+)', line)
                if match:
                    pkg = match.group(1)
                    # Check for invalid characters or naming
                    if any(c.isupper() for c in pkg):
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            severity=self.severity,
                            category=self.category,
                            line=idx + 1,
                            column=0,
                            message=f"Package name '{pkg}' contains uppercase letters",
                            suggestion=f"Use lowercase package names: '{pkg.lower()}'"
                        ))

        return issues

    def get_suggestion(self, issue: Issue) -> str:
        return "Use lowercase package names following Go naming conventions"


# Rule registry for easy lookup
ALL_RULES = {
    # Python rules
    'PY001': PythonUnusedImports(),
    'PY002': PythonLongMethod(),
    'PY003': PythonDeepNesting(),
    'PY004': PythonComplexCondition(),
    'PY005': PythonMissingDocstring(),
    'PY006': PythonBareExcept(),
    'PY007': PythonGlobalVariable(),
    'PY008': PythonMutableDefault(),
    'PY009': PythonComparisonToNone(),
    'PY010': PythonUnusedVariable(),
    'PY011': PythonMultipleStatements(),
    'PY012': PythonTooManyArguments(),
    'PY013': PythonWildcardImport(),
    'PY014': PythonReassignedBuiltin(),
    'PY015': PythonPassStatement(),
    # Java rules
    'JV001': JavaUnusedVariable(),
    'JV002': JavaLongMethod(),
    'JV003': JavaTooManyMethods(),
    'JV004': JavaGetterSetter(),
    'JV005': JavaNullCheck(),
    'JV006': JavaEmptyCatchBlock(),
    'JV007': JavaComplexClass(),
    'JV008': JavaStringConcatenation(),
    'JV009': JavaMagicNumber(),
    'JV010': JavaCyclomaticComplexity(),
    'JV011': JavaNamingConvention(),
    'JV012': JavaStaticField(),
    'JV013': JavaDuplicateCode(),
    'JV014': JavaVerboseLogging(),
    'JV015': JavaResourceLeak(),
    # TypeScript rules
    'TS001': TypeScriptAnyType(),
    'TS002': TypeScriptUnusedVariable(),
    'TS003': TypeScriptImplicitAny(),
    'TS004': TypeScriptPromiseHandling(),
    'TS005': TypeScriptLongFunction(),
    'TS006': TypeScriptNullCheck(),
    'TS007': TypeScriptUnusedImport(),
    'TS008': TypeScriptComplexCondition(),
    'TS009': TypeScriptConsoleLog(),
    'TS010': TypeScriptMissingReturn(),
    'TS011': TypeScriptTooManyParameters(),
    'TS012': TypeScriptNoExplicitAny(),
    'TS013': TypeScriptAssertion(),
    'TS014': TypeScriptStaticAnalysis(),
    'TS015': TypeScriptDeadCode(),
    # Go rules
    'GO001': GoErrorHandling(),
    'GO002': GoDeferCleanup(),
    'GO003': GoInterfaceCompliance(),
    'GO004': GoUnusedVariable(),
    'GO005': GoNilCheck(),
    'GO006': GoTypeAssertion(),
    'GO007': GoChannelLeak(),
    'GO008': GoGoroutineLeak(),
    'GO009': GoRaceCondition(),
    'GO010': GoPackageNaming(),
}
