from typing import Any

from app.agents.context_builder import RAGContextBuilder
from app.llm.groq_provider import GroqProvider
from app.models.repository import Repository
from app.services.retrieval_service import RetrievalService
from app.tools.file_tools import FileTools
from app.tools.patch_tools import PatchTools


class PatchAgent:
    """
    Agent responsible for generating proposed code modifications.

    V1 behavior:
    - Reads the target repository file through FileTools.
    - Retrieves target-file context first.
    - Retrieves relevant repository-wide context using hybrid search.
    - Combines and deduplicates the retrieved context.
    - Sends the request and repository context to the LLM.
    - Receives proposed complete file contents.
    - Generates a unified diff using PatchTools.
    - Does NOT modify the repository.
    """

    def __init__(self, db):
        self.db = db

        self.retrieval_service = RetrievalService(
            db=db
        )

        self.context_builder = RAGContextBuilder(
            max_chunks=5,
            max_chars_per_chunk=6000,
        )

        self.llm_provider = GroqProvider()

    def _build_prompt(
        self,
        request: str,
        context: str,
        file_path: str,
        current_content: str,
    ) -> str:
        """
        Build the prompt used to ask the LLM for a proposed
        modification.
        """

        return f"""
You are an AI coding agent modifying a software repository.

Your job is to propose a modification to ONE existing file.

You must understand the existing file before proposing changes.

USER REQUEST:
{request}

TARGET FILE:
{file_path}

CURRENT FILE CONTENT:
{current_content}

REPOSITORY CONTEXT:
{context}

IMPORTANT CONTEXT PRIORITY:
1. The CURRENT FILE CONTENT is authoritative for the target file.
2. TARGET FILE CONTEXT contains indexed chunks from the target file
   and should be given higher priority than unrelated repository
   context.
3. REPOSITORY CONTEXT contains additional repository-wide information
   that may help understand dependencies or related behavior.
4. Do not use unrelated repository context to invent behavior.

TASK:
Propose the complete new content of the target file required
to satisfy the user's request.

IMPORTANT RULES:
1. Modify only the target file.
2. Preserve existing functionality unless the request requires
   changing it.
3. Do not invent repository files, functions, classes, APIs,
   variables, or behavior.
4. Use the target file and repository context as evidence.
5. Do not execute commands.
6. Do not apply changes yourself.
7. Do not describe the changes.
8. Return ONLY the complete new content of the target file.
9. Do not return Markdown code fences.
10. Do not return explanations before or after the file content.
""".strip()

    @staticmethod
    def _clean_llm_output(
        content: str,
        old_content: str,
    ) -> str:
        """
        Clean accidental Markdown code fences from the LLM output.
        """

        if not content or not content.strip():
            raise ValueError(
                "LLM returned empty file content."
            )

        content = content.strip()

        if content.startswith("```"):
            lines = content.splitlines()

            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines)

        if (
            old_content.endswith("\n")
            and not content.endswith("\n")
        ):
            content += "\n"

        return content

    @staticmethod
    def _merge_results(
        target_results: list[dict],
        repository_results: list[dict],
        limit: int,
    ) -> list[dict]:
        """
        Merge target-file results and repository-wide results.

        Target-file chunks always have higher priority.

        Duplicate chunks are removed using chunk_id.
        """

        merged = []
        seen_chunk_ids = set()

        # ---------------------------------------------------------
        # 1. Target-file chunks first
        # ---------------------------------------------------------

        for result in target_results:
            chunk_id = result.get("chunk_id")

            if chunk_id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(chunk_id)
            merged.append(result)

        # ---------------------------------------------------------
        # 2. Repository-wide results
        # ---------------------------------------------------------

        for result in repository_results:
            chunk_id = result.get("chunk_id")

            if chunk_id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(chunk_id)
            merged.append(result)

        # ---------------------------------------------------------
        # 3. Keep requested context size bounded
        # ---------------------------------------------------------

        return merged[:limit]

    def generate_patch(
        self,
        repository_id: int,
        request: str,
        file_path: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        """
        Generate a proposed patch for a repository file.

        IMPORTANT:
        This method does NOT modify the repository.
        """

        request = request.strip()
        file_path = file_path.strip()

        if not request:
            raise ValueError(
                "Coding request cannot be empty."
            )

        if not file_path:
            raise ValueError(
                "File path cannot be empty."
            )

        if limit < 1 or limit > 20:
            raise ValueError(
                "Limit must be between 1 and 20."
            )

        # ---------------------------------------------------------
        # 1. Get repository
        # ---------------------------------------------------------

        repository = (
            self.db.query(Repository)
            .filter(
                Repository.id == repository_id
            )
            .first()
        )

        if repository is None:
            raise ValueError(
                f"Repository {repository_id} not found."
            )

        # ---------------------------------------------------------
        # 2. Initialize controlled tools
        # ---------------------------------------------------------

        file_tools = FileTools(
            repository.local_path
        )

        patch_tools = PatchTools(
            repository.local_path
        )

        # ---------------------------------------------------------
        # 3. Read target file
        # ---------------------------------------------------------

        file_result = file_tools.read_file(
            file_path
        )

        old_content = file_result["content"]

        # ---------------------------------------------------------
        # 4. Retrieve target-file context
        # ---------------------------------------------------------

        target_results = (
            self.retrieval_service.search_file(
                repository_id=repository_id,
                file_path=file_path,
                limit=limit,
            )
        )

        # ---------------------------------------------------------
        # 5. Retrieve repository-wide context
        # ---------------------------------------------------------

        repository_results = (
            self.retrieval_service.search(
                repository_id=repository_id,
                query=request,
                limit=limit,
                method="hybrid",
            )
        )

        # ---------------------------------------------------------
        # 6. Merge target-file + repository context
        # ---------------------------------------------------------

        results = self._merge_results(
            target_results=target_results,
            repository_results=repository_results,
            limit=limit,
        )

        # ---------------------------------------------------------
        # 7. Build RAG context
        # ---------------------------------------------------------

        context = self.context_builder.build(
            query=request,
            results=results,
        )

        # ---------------------------------------------------------
        # 8. Build LLM prompt
        # ---------------------------------------------------------

        prompt = self._build_prompt(
            request=request,
            context=context,
            file_path=file_path,
            current_content=old_content,
        )

        # ---------------------------------------------------------
        # 9. Ask LLM for proposed new file content
        # ---------------------------------------------------------

        proposed_content = self.llm_provider.generate(
            prompt
        )

        # ---------------------------------------------------------
        # 10. Clean LLM output
        # ---------------------------------------------------------

        proposed_content = self._clean_llm_output(
            content=proposed_content,
            old_content=old_content,
        )

        # ---------------------------------------------------------
        # 11. Generate unified diff
        # ---------------------------------------------------------

        patch = patch_tools.generate_patch(
            file_path=file_path,
            old_content=old_content,
            new_content=proposed_content,
        )

        # ---------------------------------------------------------
        # 12. No modification proposed
        # ---------------------------------------------------------

        if not patch:
            return {
                "repository_id": repository_id,
                "request": request,
                "file_path": file_path,
                "changed": False,
                "message": "No changes proposed.",
                "patch": "",
                "new_content": proposed_content,
                "sources": [
                    {
                        "chunk_id": result.get(
                            "chunk_id"
                        ),
                        "file_path": result.get(
                            "file_path"
                        ),
                        "chunk_type": result.get(
                            "chunk_type"
                        ),
                        "cell_index": result.get(
                            "cell_index"
                        ),
                        "reranker_score": result.get(
                            "reranker_score"
                        ),
                    }
                    for result in results
                ],
            }

        # ---------------------------------------------------------
        # 13. Return proposed patch
        # ---------------------------------------------------------

        return {
            "repository_id": repository_id,
            "request": request,
            "file_path": file_path,
            "changed": True,
            "patch": patch,
            "new_content": proposed_content,
            "sources": [
                {
                    "chunk_id": result.get(
                        "chunk_id"
                    ),
                    "file_path": result.get(
                        "file_path"
                    ),
                    "chunk_type": result.get(
                        "chunk_type"
                    ),
                    "cell_index": result.get(
                        "cell_index"
                    ),
                    "reranker_score": result.get(
                        "reranker_score"
                    ),
                }
                for result in results
            ],
        }