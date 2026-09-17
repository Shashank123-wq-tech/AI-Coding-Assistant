from pathlib import Path


class FileReader:

    def __init__(
        self,
        repository_root: str,
    ):

        self.root = (
            Path(repository_root)
            .resolve()
        )


    def read(
        self,
        relative_path: str,
    ) -> str:

        target = (
            self.root /
            relative_path
        ).resolve()

        if not target.is_relative_to(
            self.root
        ):

            raise ValueError(
                "Path traversal detected"
            )

        if not target.exists():

            raise FileNotFoundError(
                relative_path
            )

        if not target.is_file():

            raise ValueError(
                "Path is not a file"
            )

        return target.read_text(
            encoding="utf-8"
        )
