from typing import TypedDict


class AgentState(TypedDict, total=False):

    repository_path: str

    user_request: str

    retrieved_context: list

    files_to_modify: list

    generated_patch: str

    test_output: str

    error_output: str

    git_diff: str

    code_review: str

    iteration: int

    success: bool
