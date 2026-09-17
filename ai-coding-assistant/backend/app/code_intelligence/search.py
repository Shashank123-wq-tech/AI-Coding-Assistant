from pathlib import Path

import subprocess


class CodeSearch:

    def __init__(
        self,
        repository_root: str,
    ):

        self.repository_root = Path(
            repository_root
        )


    def search(
        self,
        query: str,
    ):

        result = subprocess.run(
            [
                "rg",
                "--line-number",
                "--hidden",
                "--glob",
                "!.git",
                query,
                str(self.repository_root),
            ],
            capture_output=True,
            text=True,
        )

        return result.stdout
