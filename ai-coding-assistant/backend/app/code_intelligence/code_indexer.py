from pathlib import Path

from app.code_intelligence.notebook_parser import NotebookParser
from app.code_intelligence.python_ast import PythonASTParser


class CodeIndexer:
    """
    Convert repository source files into searchable code chunks.

    V1 supports:
    - Python files
    - Jupyter notebooks

    Features:
    - Repository validation
    - Ignored directory handling
    - Python source indexing
    - Notebook cell indexing
    - Python syntax validation
    - Syntax error metadata
    - Stable chunk IDs
    """

    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        ".idea",
        ".vscode",
    }

    SUPPORTED_EXTENSIONS = {
        ".py",
        ".ipynb",
    }

    def __init__(self, repository_path: str | Path):
        self.repository_root = Path(
            repository_path
        ).resolve()

        if not self.repository_root.exists():
            raise FileNotFoundError(
                f"Repository does not exist: "
                f"{self.repository_root}"
            )

        if not self.repository_root.is_dir():
            raise ValueError(
                f"Repository path is not a directory: "
                f"{self.repository_root}"
            )

        self.python_parser = PythonASTParser()

    def _should_ignore(self, path: Path) -> bool:
        relative_path = path.relative_to(
            self.repository_root
        )

        return any(
            part in self.IGNORED_DIRECTORIES
            for part in relative_path.parts
        )

    def _relative_path(self, path: Path) -> str:
        return str(
            path.relative_to(
                self.repository_root
            )
        )

    def _index_python_file(
        self,
        file_path: Path,
    ) -> list[dict]:

        try:
            content = file_path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:
            return []

        except OSError:
            return []

        relative_path = self._relative_path(
            file_path
        )

        analysis = self.python_parser.analyze_source(
            content
        )

        metadata = {
            "file_size": file_path.stat().st_size,
            "valid_python": analysis["valid_python"],
            "classes": analysis["classes"],
            "functions": analysis["functions"],
        }

        if analysis["error"] is not None:
            metadata["syntax_error"] = analysis["error"]

        return [
            {
                "chunk_id": f"python::{relative_path}",
                "file_path": relative_path,
                "chunk_type": "python_file",
                "language": "python",
                "content": content,
                "metadata": metadata,
            }
        ]

    def _index_notebook(
        self,
        file_path: Path,
    ) -> list[dict]:

        try:
            notebook = NotebookParser(
                file_path
            ).parse()

        except (
            FileNotFoundError,
            ValueError,
        ):
            return []

        chunks = []

        relative_path = self._relative_path(
            file_path
        )

        for cell in notebook["cells"]:

            content = cell["source"].strip()

            if not content:
                continue

            cell_type = cell["cell_type"]

            metadata = {
                "valid_python": None,
            }

            if cell_type == "code":

                analysis = self.python_parser.analyze_source(
                    content
                )

                metadata["valid_python"] = (
                    analysis["valid_python"]
                )

                metadata["classes"] = (
                    analysis["classes"]
                )

                metadata["functions"] = (
                    analysis["functions"]
                )

                if analysis["error"] is not None:
                    metadata["syntax_error"] = (
                        analysis["error"]
                    )

                language = "python"

            else:
                language = "markdown"

            chunk = {
                "chunk_id": (
                    f"notebook::{relative_path}"
                    f"::cell::{cell['cell_index']}"
                ),
                "file_path": relative_path,
                "chunk_type": "notebook_cell",
                "cell_index": cell["cell_index"],
                "cell_type": cell_type,
                "language": language,
                "content": content,
                "metadata": metadata,
            }

            if cell_type == "code":

                chunk["metadata"]["execution_count"] = (
                    cell.get("execution_count")
                )

                chunk["metadata"]["outputs_count"] = (
                    cell.get("outputs_count", 0)
                )

            chunks.append(chunk)

        return chunks

    def _index_file(
        self,
        file_path: Path,
    ) -> list[dict]:

        suffix = file_path.suffix.lower()

        if suffix == ".py":
            return self._index_python_file(
                file_path
            )

        if suffix == ".ipynb":
            return self._index_notebook(
                file_path
            )

        return []

    def index(self) -> dict:

        chunks = []

        for file_path in self.repository_root.rglob("*"):

            if not file_path.is_file():
                continue

            if self._should_ignore(file_path):
                continue

            if (
                file_path.suffix.lower()
                not in self.SUPPORTED_EXTENSIONS
            ):
                continue

            file_chunks = self._index_file(
                file_path
            )

            chunks.extend(file_chunks)

        return {
            "repository": self.repository_root.name,
            "repository_path": str(
                self.repository_root
            ),
            "total_chunks": len(chunks),
            "chunks": chunks,
        }