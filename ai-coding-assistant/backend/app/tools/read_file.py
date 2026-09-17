from backend.app.tools.base import Tool
from backend.app.repository.file_reader import FileReader


class ReadFileTool(Tool):

    name = "read_file"


    def __init__(
        self,
        repository_root: str,
    ):

        self.reader = FileReader(
            repository_root
        )


    def run(
        self,
        path: str,
    ):

        return self.reader.read(
            path
        )
