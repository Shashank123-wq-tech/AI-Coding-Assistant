import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from app.core.config import settings


class RepositoryManager:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[3]

        
        self.storage_path = (
                project_root
                / settings.REPOSITORY_STORAGE_PATH
            ).resolve()

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def validate_github_url(url: str) -> bool:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return False

        if parsed.netloc.lower() != "github.com":
            return False

        path = parsed.path.strip("/")

        parts = path.split("/")

        if len(parts) != 2:
            return False

        owner, repository = parts

        if not owner or not repository:
            return False

        return True

    @staticmethod
    def repository_name_from_url(url: str) -> str:
        path = urlparse(url).path.strip("/")

        repository = path.split("/")[-1]

        if repository.endswith(".git"):
            repository = repository[:-4]

        repository = re.sub(
            r"[^a-zA-Z0-9._-]",
            "_",
            repository,
        )

        return repository

    def clone_repository(self, url: str) -> tuple[str, str]:
        if not self.validate_github_url(url):
            raise ValueError(
                "Only valid public GitHub repository URLs are supported."
            )

        repository_name = self.repository_name_from_url(url)

        destination = self.storage_path / repository_name

        if destination.exists():
            raise FileExistsError(
                f"Repository '{repository_name}' already exists."
            )

        command = [
            "git",
            "clone",
            "--depth",
            "1",
            url,
            str(destination),
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,
            )

        except subprocess.TimeoutExpired:
            if destination.exists():
                shutil.rmtree(destination, ignore_errors=True)

            raise RuntimeError(
                "Repository cloning timed out."
            )

        if result.returncode != 0:
            if destination.exists():
                shutil.rmtree(destination, ignore_errors=True)

            raise RuntimeError(
                result.stderr.strip()
                or "Git clone failed."
            )

        return repository_name, str(destination)



    def diff(self, repository_path: str) -> dict:
        """
        Return the current Git working-tree diff for a repository.

        Includes:
        - tracked modified files
        - tracked deleted files
        - untracked files

        This method is read-only and never stages or modifies files.
        """

        repository_root = Path(repository_path).resolve()

        if not repository_root.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {repository_root}"
            )

        if not repository_root.is_dir():
            raise ValueError(
                f"Repository path is not a directory: {repository_root}"
            )

        git_directory = repository_root / ".git"

        if not git_directory.exists():
            raise ValueError(
                "The specified path is not a Git repository."
            )

        try:
            tracked_result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository_root),
                    "diff",
                    "--no-ext-diff",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "Git diff operation timed out."
            )

        if tracked_result.returncode != 0:
            raise RuntimeError(
                tracked_result.stderr.strip()
                or "Git diff failed."
            )

        diff_parts = []

        if tracked_result.stdout.strip():
            diff_parts.append(
                tracked_result.stdout.rstrip()
            )

        try:
            untracked_result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository_root),
                    "ls-files",
                    "--others",
                    "--exclude-standard",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "Git untracked-file detection timed out."
            )

        if untracked_result.returncode != 0:
            raise RuntimeError(
                untracked_result.stderr.strip()
                or "Git untracked-file detection failed."
            )

        untracked_files = [
            line.strip()
            for line in untracked_result.stdout.splitlines()
            if line.strip()
        ]

        for relative_path in untracked_files:
            file_path = repository_root / relative_path

            if not file_path.is_file():
                continue

            try:
                content = file_path.read_text(
                    encoding="utf-8"
                )
            except UnicodeDecodeError:
                continue

            lines = content.splitlines()

            diff_parts.append(
                "\n".join(
                    [
                        f"diff --git a/{relative_path} b/{relative_path}",
                        "new file mode 100644",
                        "--- /dev/null",
                        f"+++ b/{relative_path}",
                        f"@@ -0,0 +1,{len(lines)} @@",
                        *[
                            f"+{line}"
                            for line in lines
                        ],
                    ]
                )
            )

        combined_diff = "\n".join(
            part for part in diff_parts if part
        )

        return {
            "repository_path": str(repository_root),
            "changed": bool(combined_diff.strip()),
            "diff": combined_diff,
        }    