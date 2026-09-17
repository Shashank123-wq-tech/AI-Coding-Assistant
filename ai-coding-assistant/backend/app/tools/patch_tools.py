from pathlib import Path
import difflib
import subprocess

class PatchTools:
    """
    Controlled patch generation, validation, and application tools.

    All file operations are restricted to the repository root.
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
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty.")

        path = (self.repository_root / file_path).resolve()

        try:
            path.relative_to(self.repository_root)
        except ValueError:
            raise PermissionError(
                "Access denied: file is outside the repository."
            )

        return path
    @staticmethod
    def _is_test_file(file_path: str) -> bool:
        path = Path(file_path)

        filename = path.name.lower()

        if filename.startswith("test_"):
            return True

        if filename.endswith("_test.py"):
            return True

        if "tests" in {
            part.lower()
            for part in path.parts
        }:
            return True

        return False
    
    @staticmethod
    def _is_git_file(file_path: str) -> bool:
        path = Path(file_path)

        if ".git" in {
            part.lower()
            for part in path.parts
        }:
            return True

        return False
    
    @staticmethod
    def _is_allowed_source_file(file_path: str) -> bool:
        path = Path(file_path)

        allowed_extensions = {
            ".py",
            ".pyi",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".go",
            ".rs",
        }

        return path.suffix.lower() in allowed_extensions
    
    @staticmethod
    def compare_snapshots(
        before: dict[str, str],
        after: dict[str, str],
    ) -> dict:
        """
        Compare two repository filesystem snapshots.

        Detects files that were added, removed, or modified
        between the two snapshots.
        """

        before_files = set(before)
        after_files = set(after)

        added_files = sorted(
            after_files - before_files
        )

        removed_files = sorted(
            before_files - after_files
        )

        modified_files = sorted(
            file_path
            for file_path in (
                before_files & after_files
            )
            if before[file_path] != after[file_path]
        )

        changed_files = sorted(
            set(added_files)
            | set(removed_files)
            | set(modified_files)
        )

        return {
            "changed_files": changed_files,
            "added_files": added_files,
            "removed_files": removed_files,
            "modified_files": modified_files,
        }
    
    def get_changed_files(self) -> list[str]:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(self.repository_root),
                "status",
                "--short",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip()
                or "Failed to inspect Git status."
            )

        changed_files = []

        for line in result.stdout.splitlines():

            if not line:
                continue

            # Git status --short format:
            # XY filename
            file_path = line[2:].strip()

            if " -> " in file_path:
                file_path = file_path.split(" -> ")[-1]

            changed_files.append(file_path)

        return changed_files
    
    def snapshot_files(self) -> dict[str, str]:
        """
        Capture SHA-256 hashes of meaningful repository files.

        Git metadata and generated/cache files are excluded.
        """

        import hashlib

        snapshot = {}

        ignored_directories = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".tox",
            ".venv",
            "venv",
            "node_modules",
        }

        ignored_extensions = {
            ".pyc",
            ".pyo",
        }

        for path in self.repository_root.rglob("*"):
            if not path.is_file():
                continue

            try:
                relative_path = path.relative_to(
                    self.repository_root
                )
            except ValueError:
                continue

            relative_parts = {
                part.lower()
                for part in relative_path.parts
            }

            if relative_parts & {
                directory.lower()
                for directory in ignored_directories
            }:
                continue

            if path.suffix.lower() in ignored_extensions:
                continue

            try:
                content = path.read_bytes()
            except OSError:
                continue

            file_hash = hashlib.sha256(
                content
            ).hexdigest()

            snapshot[str(relative_path).replace("\\", "/")] = file_hash

        return snapshot
    
    def validate_changed_files(
        self,
        expected_files: list[str],
        before_snapshot: dict[str, str],
    ) -> dict:
        """
        Validate that only the expected files changed
        between the before and after repository states.
        """

        after_snapshot = self.snapshot_files()

        comparison = self.compare_snapshots(
            before=before_snapshot,
            after=after_snapshot,
        )

        actual_files = set(
            comparison["changed_files"]
        )

        expected_files = {
          str(Path(file_path)).replace("\\", "/")
          for file_path in expected_files
        }
        unexpected_files = sorted(
            actual_files - expected_files
        )

        missing_expected_files = sorted(
            expected_files - actual_files
        )

        return {
            "valid": (
                not unexpected_files
                and not missing_expected_files
            ),
            "expected_files": sorted(
                expected_files
            ),
            "actual_files": sorted(
                actual_files
            ),
            "unexpected_files": unexpected_files,
            "missing_expected_files": missing_expected_files,
            "added_files": comparison[
                "added_files"
            ],
            "removed_files": comparison[
                "removed_files"
            ],
            "modified_files": comparison[
                "modified_files"
            ],
        }

    def generate_patch(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
    ) -> str:
        if old_content == new_content:
            return ""

        patch = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=file_path,
            tofile=file_path,
        )

        return "".join(patch)

    def validate_patch(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
    ) -> dict:
        path = self._safe_path(file_path)
        if self._is_test_file(file_path):
                raise PermissionError(
                "Automated repair cannot modify test files."
            )
        if self._is_git_file(file_path):
            raise PermissionError(
                "Automated repair cannot modify Git metadata."
            ) 
        
        if not self._is_allowed_source_file(file_path):
                 raise PermissionError(
                "Automated repair can only modify allowed source files."
        )           
                

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {file_path}"
            )

        current_content = path.read_text(
            encoding="utf-8"
        )

        if current_content != old_content:
            return {
                "valid": False,
                "reason": (
                    "File changed since it was read. "
                    "Patch cannot be safely applied."
                ),
            }

        patch = self.generate_patch(
            file_path=file_path,
            old_content=old_content,
            new_content=new_content,
        )

        if not patch:
            return {
                "valid": False,
                "reason": "No changes detected.",
            }

        return {
            "valid": True,
            "file_path": file_path,
            "patch": patch,
        }
      

    def apply_patch(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
    ) -> dict:
        """
        Safely apply a validated content replacement.

        The file is modified only when its current contents
        exactly match old_content.
        """

        path = self._safe_path(file_path)

        validation = self.validate_patch(
            file_path=file_path,
            old_content=old_content,
            new_content=new_content,
        )

        if not validation["valid"]:
            return {
                "applied": False,
                "file_path": file_path,
                "reason": validation["reason"],
            }

        path.write_text(
            new_content,
            encoding="utf-8",
        )

        return {
            "applied": True,
            "file_path": file_path,
            "patch": validation["patch"],
            "message": "Patch applied successfully.",
        }