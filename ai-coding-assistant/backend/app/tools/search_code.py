from backend.app.tools.base import Tool
from backend.app.code_intelligence.search import CodeSearch


class SearchCodeTool(Tool):

    name = "search_code"


    def __init__(
        self,
        repository_root: str,
    ):

        self.searcher = CodeSearch(
            repository_root
        )


    def run(
        self,
        query: str,
    ):

        return self.searcher.search(
            query
        )
