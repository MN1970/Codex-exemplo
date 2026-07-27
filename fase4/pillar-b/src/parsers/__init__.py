"""
AST Parser Module - Multi-language support
Supports: Python, Java, TypeScript, Go
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import ast
import json


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVA = "java"
    TYPESCRIPT = "typescript"
    GO = "go"


@dataclass
class Position:
    """Source code position"""
    line: int
    column: int
    offset: int


@dataclass
class Token:
    """AST Token"""
    type: str
    value: str
    position: Position
    length: int


@dataclass
class ASTNode:
    """Generic AST Node representation"""
    node_type: str
    name: Optional[str] = None
    line: int = 0
    column: int = 0
    length: int = 0
    children: List['ASTNode'] = None
    metadata: Dict[str, Any] = None
    parent: Optional['ASTNode'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}


class Parser(ABC):
    """Abstract Parser base class"""

    @abstractmethod
    def parse(self, source: str, filename: str = None) -> ASTNode:
        """Parse source code and return AST"""
        pass

    @abstractmethod
    def tokenize(self, source: str) -> List[Token]:
        """Tokenize source code"""
        pass

    @abstractmethod
    def get_node_at_position(self, ast: ASTNode, line: int, column: int) -> Optional[ASTNode]:
        """Find node at specific position"""
        pass


class PythonParser(Parser):
    """Python source code parser using ast module"""

    def parse(self, source: str, filename: str = "unknown.py") -> ASTNode:
        """Parse Python source code"""
        try:
            tree = ast.parse(source, filename=filename)
            root = self._convert_node(tree, source)
            return root
        except SyntaxError as e:
            raise ValueError(f"Python syntax error at line {e.lineno}: {e.msg}")

    def tokenize(self, source: str) -> List[Token]:
        """Tokenize Python source"""
        import tokenize
        import io

        tokens = []
        try:
            readline = io.StringIO(source).readline
            for tok in tokenize.generate_tokens(readline):
                tokens.append(Token(
                    type=tokenize.tok_name[tok.type],
                    value=tok.string,
                    position=Position(line=tok.start[0], column=tok.start[1], offset=0),
                    length=len(tok.string)
                ))
        except tokenize.TokenError:
            pass

        return tokens

    def _convert_node(self, node: ast.AST, source: str, parent: Optional[ASTNode] = None) -> ASTNode:
        """Convert ast.AST node to ASTNode"""
        node_type = node.__class__.__name__

        # Extract name for named nodes
        name = getattr(node, 'name', None)

        # Get line and column info
        line = getattr(node, 'lineno', 0)
        col = getattr(node, 'col_offset', 0)

        ast_node = ASTNode(
            node_type=node_type,
            name=name,
            line=line,
            column=col,
            parent=parent
        )

        # Store metadata
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            ast_node.metadata['args'] = [arg.arg for arg in node.args.args]
            ast_node.metadata['decorators'] = [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in node.decorator_list]
            ast_node.metadata['returns'] = node.returns is not None

        elif isinstance(node, ast.ClassDef):
            ast_node.metadata['bases'] = [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
            ast_node.metadata['decorators'] = [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in node.decorator_list]

        elif isinstance(node, ast.Import):
            ast_node.metadata['names'] = [alias.name for alias in node.names]

        elif isinstance(node, ast.ImportFrom):
            ast_node.metadata['module'] = node.module
            ast_node.metadata['names'] = [alias.name for alias in node.names]

        # Process children
        for child in ast.iter_child_nodes(node):
            child_node = self._convert_node(child, source, ast_node)
            ast_node.children.append(child_node)

        return ast_node

    def get_node_at_position(self, ast_node: ASTNode, line: int, column: int) -> Optional[ASTNode]:
        """Find node at specific line and column"""
        if ast_node.line == line and ast_node.column == column:
            return ast_node

        for child in ast_node.children:
            result = self.get_node_at_position(child, line, column)
            if result:
                return result

        return None


class TypeScriptParser(Parser):
    """TypeScript parser using regex-based parsing"""

    def parse(self, source: str, filename: str = "unknown.ts") -> ASTNode:
        """Parse TypeScript source code"""
        root = ASTNode(node_type="Program", name="root")
        root.metadata['language'] = 'typescript'

        # Simple tokenization and parsing
        lines = source.split('\n')
        current_line = 0

        for idx, line in enumerate(lines, 1):
            current_line = idx
            stripped = line.strip()

            # Detect functions
            if 'function ' in stripped or 'async function' in stripped or '=>' in stripped:
                self._parse_function(root, line, idx)

            # Detect classes
            elif 'class ' in stripped:
                self._parse_class(root, line, idx)

            # Detect interfaces
            elif 'interface ' in stripped:
                self._parse_interface(root, line, idx)

            # Detect imports
            elif 'import ' in stripped:
                self._parse_import(root, line, idx)

        return root

    def tokenize(self, source: str) -> List[Token]:
        """Tokenize TypeScript source"""
        import re
        tokens = []

        # Simple regex tokenization
        pattern = r'\b\w+\b|[\{\}\(\)\[\];,.]|"[^"]*"|\'[^\']*\'|//.*|/\*[\s\S]*?\*/'

        offset = 0
        for match in re.finditer(pattern, source):
            start = match.start()
            value = match.group()

            # Count lines to get line number
            line = source[:start].count('\n') + 1
            col = start - source.rfind('\n', 0, start) - 1

            tokens.append(Token(
                type=self._classify_token(value),
                value=value,
                position=Position(line=line, column=col, offset=start),
                length=len(value)
            ))

        return tokens

    def _classify_token(self, value: str) -> str:
        """Classify token type"""
        if value in {'function', 'class', 'interface', 'import', 'export', 'const', 'let', 'var'}:
            return 'keyword'
        elif value.startswith('//') or value.startswith('/*'):
            return 'comment'
        elif value.startswith('"') or value.startswith("'"):
            return 'string'
        elif value in {'{', '}', '(', ')', '[', ']', ';', ',', '.'}:
            return 'punctuation'
        else:
            return 'identifier'

    def _parse_function(self, parent: ASTNode, line: str, line_num: int):
        """Extract function information"""
        import re
        func_match = re.search(r'(async\s+)?function\s+(\w+)\s*\(([^)]*)\)', line)
        arrow_match = re.search(r'(\w+)\s*=\s*(async\s*)?\(([^)]*)\)\s*=>', line)

        if func_match:
            name = func_match.group(2)
            args = [arg.strip() for arg in func_match.group(3).split(',') if arg.strip()]
            node = ASTNode(node_type="FunctionDeclaration", name=name, line=line_num)
            node.metadata['args'] = args
            parent.children.append(node)
        elif arrow_match:
            name = arrow_match.group(1)
            args = [arg.strip() for arg in arrow_match.group(3).split(',') if arg.strip()]
            node = ASTNode(node_type="ArrowFunctionExpression", name=name, line=line_num)
            node.metadata['args'] = args
            parent.children.append(node)

    def _parse_class(self, parent: ASTNode, line: str, line_num: int):
        """Extract class information"""
        import re
        match = re.search(r'class\s+(\w+)\s*(?:extends\s+(\w+))?', line)
        if match:
            name = match.group(1)
            extends = match.group(2)
            node = ASTNode(node_type="ClassDeclaration", name=name, line=line_num)
            if extends:
                node.metadata['extends'] = extends
            parent.children.append(node)

    def _parse_interface(self, parent: ASTNode, line: str, line_num: int):
        """Extract interface information"""
        import re
        match = re.search(r'interface\s+(\w+)\s*(?:extends\s+(\w+))?', line)
        if match:
            name = match.group(1)
            extends = match.group(2)
            node = ASTNode(node_type="InterfaceDeclaration", name=name, line=line_num)
            if extends:
                node.metadata['extends'] = extends
            parent.children.append(node)

    def _parse_import(self, parent: ASTNode, line: str, line_num: int):
        """Extract import information"""
        import re
        match = re.search(r'import\s+(?:\{([^}]*)\}|(\w+))\s+from\s+[\'"]([^\'"]+)[\'"]', line)
        if match:
            items = match.group(1) if match.group(1) else match.group(2)
            module = match.group(3)
            node = ASTNode(node_type="ImportDeclaration", line=line_num)
            node.metadata['items'] = items
            node.metadata['module'] = module
            parent.children.append(node)

    def get_node_at_position(self, ast_node: ASTNode, line: int, column: int) -> Optional[ASTNode]:
        """Find node at position"""
        if ast_node.line == line and ast_node.column <= column:
            return ast_node

        for child in ast_node.children:
            result = self.get_node_at_position(child, line, column)
            if result:
                return result

        return None


class JavaParser(Parser):
    """Java parser using regex-based parsing"""

    def parse(self, source: str, filename: str = "unknown.java") -> ASTNode:
        """Parse Java source code"""
        root = ASTNode(node_type="CompilationUnit", name="root")
        lines = source.split('\n')

        for idx, line in enumerate(lines, 1):
            stripped = line.strip()

            if 'class ' in stripped:
                self._parse_class(root, line, idx)
            elif 'interface ' in stripped:
                self._parse_interface(root, line, idx)
            elif 'public ' in stripped or 'private ' in stripped or 'protected ' in stripped:
                if 'void ' in stripped or 'int ' in stripped or 'String ' in stripped:
                    self._parse_method(root, line, idx)

        return root

    def tokenize(self, source: str) -> List[Token]:
        """Tokenize Java source"""
        import re
        tokens = []

        pattern = r'\b\w+\b|[\{\}\(\)\[\];,.]|"[^"]*"|\'[^\']*\'|//.*|/\*[\s\S]*?\*/'

        for match in re.finditer(pattern, source):
            value = match.group()
            start = match.start()
            line = source[:start].count('\n') + 1
            col = start - source.rfind('\n', 0, start) - 1

            tokens.append(Token(
                type=self._classify_token(value),
                value=value,
                position=Position(line=line, column=col, offset=start),
                length=len(value)
            ))

        return tokens

    def _classify_token(self, value: str) -> str:
        """Classify token type"""
        keywords = {'class', 'interface', 'public', 'private', 'protected', 'static', 'final', 'void', 'return', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break', 'continue', 'try', 'catch', 'finally', 'throw', 'throws', 'extends', 'implements', 'new', 'this', 'super', 'null', 'true', 'false'}
        if value in keywords:
            return 'keyword'
        elif value.startswith('//') or value.startswith('/*'):
            return 'comment'
        elif value.startswith('"'):
            return 'string'
        elif value in {'{', '}', '(', ')', '[', ']', ';', ',', '.'}:
            return 'punctuation'
        else:
            return 'identifier'

    def _parse_class(self, parent: ASTNode, line: str, line_num: int):
        """Extract class information"""
        import re
        match = re.search(r'class\s+(\w+)\s*(?:extends\s+(\w+))?(?:implements\s+([^{]+))?', line)
        if match:
            name = match.group(1)
            node = ASTNode(node_type="ClassDeclaration", name=name, line=line_num)
            if match.group(2):
                node.metadata['extends'] = match.group(2)
            if match.group(3):
                node.metadata['implements'] = match.group(3)
            parent.children.append(node)

    def _parse_interface(self, parent: ASTNode, line: str, line_num: int):
        """Extract interface information"""
        import re
        match = re.search(r'interface\s+(\w+)\s*(?:extends\s+([^{]+))?', line)
        if match:
            name = match.group(1)
            node = ASTNode(node_type="InterfaceDeclaration", name=name, line=line_num)
            if match.group(2):
                node.metadata['extends'] = match.group(2)
            parent.children.append(node)

    def _parse_method(self, parent: ASTNode, line: str, line_num: int):
        """Extract method information"""
        import re
        match = re.search(r'(public|private|protected)\s+(?:static\s+)?(?:final\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)', line)
        if match:
            return_type = match.group(2)
            name = match.group(3)
            args = [arg.strip() for arg in match.group(4).split(',') if arg.strip()]
            node = ASTNode(node_type="MethodDeclaration", name=name, line=line_num)
            node.metadata['returnType'] = return_type
            node.metadata['args'] = args
            parent.children.append(node)

    def get_node_at_position(self, ast_node: ASTNode, line: int, column: int) -> Optional[ASTNode]:
        """Find node at position"""
        if ast_node.line == line and ast_node.column <= column:
            return ast_node

        for child in ast_node.children:
            result = self.get_node_at_position(child, line, column)
            if result:
                return result

        return None


class GoParser(Parser):
    """Go language parser"""

    def parse(self, source: str, filename: str = "unknown.go") -> ASTNode:
        """Parse Go source code"""
        root = ASTNode(node_type="File", name="root")
        lines = source.split('\n')

        for idx, line in enumerate(lines, 1):
            stripped = line.strip()

            if 'func ' in stripped:
                self._parse_function(root, line, idx)
            elif 'type ' in stripped and 'struct' in stripped:
                self._parse_struct(root, line, idx)
            elif 'interface ' in stripped:
                self._parse_interface(root, line, idx)
            elif 'import ' in stripped:
                self._parse_import(root, line, idx)

        return root

    def tokenize(self, source: str) -> List[Token]:
        """Tokenize Go source"""
        import re
        tokens = []

        pattern = r'\b\w+\b|[\{\}\(\)\[\];:,.]|"[^"]*"|\'[^\']*\'|//.*|/\*[\s\S]*?\*/'

        for match in re.finditer(pattern, source):
            value = match.group()
            start = match.start()
            line = source[:start].count('\n') + 1
            col = start - source.rfind('\n', 0, start) - 1

            tokens.append(Token(
                type=self._classify_token(value),
                value=value,
                position=Position(line=line, column=col, offset=start),
                length=len(value)
            ))

        return tokens

    def _classify_token(self, value: str) -> str:
        """Classify token type"""
        keywords = {'func', 'type', 'struct', 'interface', 'package', 'import', 'const', 'var', 'if', 'else', 'for', 'range', 'switch', 'case', 'default', 'return', 'defer', 'go', 'select', 'chan', 'make', 'new', 'len', 'cap', 'append', 'copy', 'close', 'delete', 'complex', 'real', 'imag', 'panic', 'recover'}
        if value in keywords:
            return 'keyword'
        elif value.startswith('//') or value.startswith('/*'):
            return 'comment'
        elif value.startswith('"'):
            return 'string'
        elif value in {'{', '}', '(', ')', '[', ']', ';', ':', ',', '.'}:
            return 'punctuation'
        else:
            return 'identifier'

    def _parse_function(self, parent: ASTNode, line: str, line_num: int):
        """Extract function information"""
        import re
        match = re.search(r'func\s+(?:\(([^)]*)\)\s+)?(\w+)\s*\(([^)]*)\)', line)
        if match:
            receiver = match.group(1)
            name = match.group(2)
            args = [arg.strip() for arg in match.group(3).split(',') if arg.strip()]

            node_type = "MethodDeclaration" if receiver else "FunctionDeclaration"
            node = ASTNode(node_type=node_type, name=name, line=line_num)
            if receiver:
                node.metadata['receiver'] = receiver
            node.metadata['args'] = args
            parent.children.append(node)

    def _parse_struct(self, parent: ASTNode, line: str, line_num: int):
        """Extract struct information"""
        import re
        match = re.search(r'type\s+(\w+)\s+struct', line)
        if match:
            name = match.group(1)
            node = ASTNode(node_type="StructDeclaration", name=name, line=line_num)
            parent.children.append(node)

    def _parse_interface(self, parent: ASTNode, line: str, line_num: int):
        """Extract interface information"""
        import re
        match = re.search(r'type\s+(\w+)\s+interface', line)
        if match:
            name = match.group(1)
            node = ASTNode(node_type="InterfaceDeclaration", name=name, line=line_num)
            parent.children.append(node)

    def _parse_import(self, parent: ASTNode, line: str, line_num: int):
        """Extract import information"""
        import re
        match = re.search(r'import\s*\(\s*"([^"]+)"\s*\)', line)
        if not match:
            match = re.search(r'import\s+"([^"]+)"', line)
        if match:
            module = match.group(1)
            node = ASTNode(node_type="ImportDeclaration", line=line_num)
            node.metadata['module'] = module
            parent.children.append(node)

    def get_node_at_position(self, ast_node: ASTNode, line: int, column: int) -> Optional[ASTNode]:
        """Find node at position"""
        if ast_node.line == line and ast_node.column <= column:
            return ast_node

        for child in ast_node.children:
            result = self.get_node_at_position(child, line, column)
            if result:
                return result

        return None


# Factory for parser selection
def get_parser(language: Language) -> Parser:
    """Get appropriate parser for language"""
    parsers = {
        Language.PYTHON: PythonParser,
        Language.JAVA: JavaParser,
        Language.TYPESCRIPT: TypeScriptParser,
        Language.GO: GoParser,
    }
    return parsers[language]()
