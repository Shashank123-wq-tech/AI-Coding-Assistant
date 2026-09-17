from pathlib import Path


class PatchService:

    def __init__(
        self,
        repository_root: str,
    ):

        self.root = (
            Path(repository_root)
            .resolve()
        )


    def validate_path(
        self,
        relative_path: str,
    ):

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

        return target
