from app.tools.base import Tool
from app.repository.manager import RepositoryManager


class GitDiffTool(Tool):

    name = "git_diff"


    def __init__(self):

        self.manager = (
            RepositoryManager()
        )


    def run(
        self,
        repository_path: str,
    ):

        return self.manager.diff(
            repository_path
        )
