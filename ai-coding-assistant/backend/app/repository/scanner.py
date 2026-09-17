from collections import Counter
from pathlib import Path


class RepositoryScanner:
    """
    Read-only repository scanner.

    Collects:
    - files
    - directories
    - file extensions
    - programming languages
    - total file size
    - Python files
    - test files
    - important project files
    """

    IGNORED_DIRECTORIES = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        ".idea",
        ".vscode",
    }

    LANGUAGE_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".h": "C/C++ Header",
        ".hpp": "C++ Header",
        ".c": "C",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
        ".cs": "C#",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".sql": "SQL",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".toml": "TOML",
        ".md": "Markdown",
        ".ipynb":"Jupyter Notebook"
    }

    IMPORTANT_FILES = {
        "README.md",
        "README",
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "Pipfile",
        "poetry.lock",
        "package.json",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".gitignore",
        ".env.example",
    }

    def __init__(self, repository_path: str | Path):
        self.repository_root = Path(repository_path).resolve()

        if not self.repository_root.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {self.repository_root}"
            )

        if not self.repository_root.is_dir():
            raise ValueError(
                f"Repository path is not a directory: {self.repository_root}"
            )

    def _should_ignore(self, path: Path) -> bool:
        """
        Return True when the file or directory belongs
        to an ignored directory.
        """

        relative_path = path.relative_to(self.repository_root)

        return any(
            part in self.IGNORED_DIRECTORIES
            for part in relative_path.parts
        )

    def scan(self) -> dict:
        """
        Scan the repository without modifying any files.
        """

        files = []
        directories = set()

        extension_counter = Counter()
        language_counter = Counter()

        total_size = 0

        python_files = []
        test_files = []
        important_files = []
        notebook_files = []

        for path in self.repository_root.rglob("*"):

            if self._should_ignore(path):
                continue

            if path.is_dir():
                directories.add(
                    str(
                        path.relative_to(
                            self.repository_root
                        )
                    )
                )
                continue

            if not path.is_file():
                continue

            relative_path = path.relative_to(
                self.repository_root
            )

            relative_path_str = str(relative_path)

            try:
                file_size = path.stat().st_size
            except OSError:
                continue

            extension = path.suffix.lower()

            files.append(
                {
                    "path": relative_path_str,
                    "extension": extension,
                    "size_bytes": file_size,
                }
            )

            total_size += file_size

            if extension:
                extension_counter[extension] += 1

            language = self.LANGUAGE_MAP.get(extension)

            if language:
                language_counter[language] += 1

            if extension == ".py":
                python_files.append(
                    relative_path_str
                )
            if extension == ".ipynb":
               notebook_files.append(
                 relative_path_str
                )    

            filename_lower = path.name.lower()

            if (
                filename_lower.startswith("test_")
                or filename_lower.endswith("_test.py")
                or "tests" in relative_path.parts
            ):
                test_files.append(
                    relative_path_str
                )

            if path.name in self.IMPORTANT_FILES:
                important_files.append(
                    relative_path_str
                )

        return {
            "repository": self.repository_root.name,
            "repository_path": str(
                self.repository_root
            ),
            "total_files": len(files),
            "total_directories": len(directories),
            "total_size_bytes": total_size,
            "languages": dict(
                language_counter.most_common()
            ),
            "file_extensions": dict(
                extension_counter.most_common()
            ),
            "python_files": python_files,
            "test_files": test_files,
            "important_files": sorted(
                important_files
            ),
            "files": files,
            "directories": sorted(
                directories
            ),
            "notebook_files": notebook_files,
        }


