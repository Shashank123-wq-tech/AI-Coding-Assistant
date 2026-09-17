import ast
from pathlib import Path


class PythonASTParser:
    """
    Production-safe Python AST parser.

    Handles:
    - valid Python files
    - syntax errors
    - incomplete notebook cells
    """

    def parse_file(self, file_path: str):
        path = Path(file_path)

        source = path.read_text(
            encoding="utf-8"
        )

        return ast.parse(source)

    def parse_source(self, source: str):
        """
        Parse Python source code directly.

        Returns:
            {
                "success": True,
                "tree": ast.AST,
                "error": None
            }

        or:

            {
                "success": False,
                "tree": None,
                "error": {...}
            }
        """

        try:
            tree = ast.parse(source)

            return {
                "success": True,
                "tree": tree,
                "error": None,
            }

        except SyntaxError as exc:
            return {
                "success": False,
                "tree": None,
                "error": {
                    "type": "SyntaxError",
                    "message": exc.msg,
                    "line": exc.lineno,
                    "column": exc.offset,
                    "text": exc.text.strip() if exc.text else None,
                },
            }

    def extract_functions(self, file_path: str):
        tree = self.parse_file(file_path)

        functions = []

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": getattr(
                            node,
                            "end_lineno",
                            node.lineno,
                        ),
                    }
                )

        return functions

    def extract_classes(self, file_path: str):
        tree = self.parse_file(file_path)

        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": getattr(
                            node,
                            "end_lineno",
                            node.lineno,
                        ),
                    }
                )

        return classes

    def analyze_source(self, source: str):
        """
        Analyze arbitrary Python source safely.
        """

        result = self.parse_source(source)

        if not result["success"]:
            return {
                "valid_python": False,
                "classes": [],
                "functions": [],
                "error": result["error"],
            }

        tree = result["tree"]

        classes = []
        functions = []

        for node in ast.walk(tree):

            if isinstance(node, ast.ClassDef):
                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": getattr(
                            node,
                            "end_lineno",
                            node.lineno,
                        ),
                    }
                )

            elif isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": getattr(
                            node,
                            "end_lineno",
                            node.lineno,
                        ),
                    }
                )

        return {
            "valid_python": True,
            "classes": classes,
            "functions": functions,
            "error": None,
        }
