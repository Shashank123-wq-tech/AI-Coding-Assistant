from pathlib import Path


class FileTools:
    """
    Controlled repository file operations.

    All file access is restricted to the repository root.
    """

    def __init__(self, repository_path: str):
        self.repository_root = Path(repository_path).resolve()

        if not self.repository_root.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {self.repository_root}"
            )

        if not self.repository_root.is_dir():
            raise ValueError(
                f"Repository path is not a directory: {self.repository_root}"
            )

    def _safe_path(self, file_path: str) -> Path:
        """
        Resolve a repository-relative path and prevent
        path traversal outside the repository.
        """

        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty.")

        requested_path = (
            self.repository_root / file_path
        ).resolve()

        try:
            requested_path.relative_to(
                self.repository_root
            )
        except ValueError:
            raise PermissionError(
                "Access denied: file is outside the repository."
            )

        return requested_path

    def read_file(self, file_path: str) -> dict:
        """
        Read a text file inside the repository.
        """

        path = self._safe_path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {file_path}"
            )

        content = path.read_text(
            encoding="utf-8"
        )

        return {
            "file_path": file_path,
            "content": content,
            "size_bytes": len(
                content.encode("utf-8")
            ),
        }