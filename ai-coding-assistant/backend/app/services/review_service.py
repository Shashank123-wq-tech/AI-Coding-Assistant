from typing import Any

from sqlalchemy.orm import Session

from app.models.repository import Repository
from app.review.reviewer import CodeReviewer
from app.tools.git_diff import GitDiffTool


class ReviewService:
    """
    Orchestrates repository code review.

    The service:
    - loads the repository
    - obtains its current Git diff
    - sends the diff to CodeReviewer
    - never modifies repository files
    """

    def __init__(self, db: Session):
        self.db = db
        self.git_diff_tool = GitDiffTool()
        self.reviewer = CodeReviewer()

    def review(
        self,
        repository_id: int,
    ) -> dict[str, Any]:
        repository = (
            self.db.query(Repository)
            .filter(
                Repository.id == repository_id
            )
            .first()
        )

        if repository is None:
            raise FileNotFoundError(
                "Repository not found."
            )

        diff_result = self.git_diff_tool.run(
            repository.local_path
        )

        git_diff = diff_result.get(
            "diff",
            "",
        )

        review_result = self.reviewer.review(
            git_diff
        )

        return {
            "repository_id": repository_id,
            "repository_path": repository.local_path,
            **review_result,
        }
