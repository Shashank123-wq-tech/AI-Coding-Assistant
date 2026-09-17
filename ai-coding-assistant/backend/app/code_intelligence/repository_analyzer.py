from pathlib import Path

from app.code_intelligence.notebook_parser import NotebookParser
from app.code_intelligence.python_ast import PythonASTParser


class RepositoryAnalyzer:
    """
    Analyze the code structure of a repository.

    Handles:
    - Python files
    - Jupyter notebooks
    - Python classes
    - Python functions
    - Syntax errors in notebook code cells
    """

    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
    }

    def __init__(self, repository_path: str | Path):
        self.repository_root = Path(repository_path).resolve()

        if not self.repository_root.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {self.repository_root}"
            )

        if not self.repository_root.is_dir():
            raise ValueError(
                f"Repository path is not a directory: "
                f"{self.repository_root}"
            )

        self.python_parser = PythonASTParser()

    def _should_ignore(self, path: Path) -> bool:
        return any(
            part in self.IGNORED_DIRECTORIES
            for part in path.relative_to(
                self.repository_root
            ).parts
        )

    def analyze_python_file(
        self,
        file_path: Path,
    ) -> dict:

        source = file_path.read_text(
            encoding="utf-8"
        )

        analysis = self.python_parser.analyze_source(
            source
        )

        return {
            "path": str(
                file_path.relative_to(
                    self.repository_root
                )
            ),
            "type": "python",
            "valid_python": analysis["valid_python"],
            "classes": analysis["classes"],
            "functions": analysis["functions"],
            "error": analysis["error"],
        }

    def analyze_notebook(
        self,
        file_path: Path,
    ) -> dict:

        parsed_notebook = NotebookParser(
            file_path
        ).parse()

        analyzed_cells = []

        for cell in parsed_notebook["cells"]:

            cell_result = {
                "cell_index": cell["cell_index"],
                "cell_type": cell["cell_type"],
                "source": cell["source"],
            }

            if cell["cell_type"] == "code":

                analysis = self.python_parser.analyze_source(
                    cell["source"]
                )

                cell_result.update(
                    {
                        "valid_python": analysis["valid_python"],
                        "classes": analysis["classes"],
                        "functions": analysis["functions"],
                        "error": analysis["error"],
                    }
                )

            analyzed_cells.append(
                cell_result
            )

        return {
            "path": str(
                file_path.relative_to(
                    self.repository_root
                )
            ),
            "type": "notebook",
            "total_cells": parsed_notebook["total_cells"],
            "code_cells": parsed_notebook["code_cells"],
            "markdown_cells": parsed_notebook["markdown_cells"],
            "raw_cells": parsed_notebook["raw_cells"],
            "cells": analyzed_cells,
        }

    def analyze(self) -> dict:

        python_files = []
        notebook_files = []

        for file_path in self.repository_root.rglob("*"):

            if not file_path.is_file():
                continue

            if self._should_ignore(file_path):
                continue

            suffix = file_path.suffix.lower()

            if suffix == ".py":
                python_files.append(
                    self.analyze_python_file(
                        file_path
                    )
                )

            elif suffix == ".ipynb":
                notebook_files.append(
                    self.analyze_notebook(
                        file_path
                    )
                )

        return {
            "repository": self.repository_root.name,
            "repository_path": str(
                self.repository_root
            ),
            "python_files": python_files,
            "notebooks": notebook_files,
            "total_python_files": len(
                python_files
            ),
            "total_notebooks": len(
                notebook_files
            ),
        }