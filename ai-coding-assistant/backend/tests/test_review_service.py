import pytest

from app.services.review_service import ReviewService


class FakeQuery:
    def __init__(self, repository):
        self.repository = repository

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.repository


class FakeDB:
    def __init__(self, repository):
        self.repository = repository

    def query(self, model):
        return FakeQuery(self.repository)


class FakeGitDiffTool:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def run(self, repository_path):
        self.calls.append(repository_path)
        return self.result


class FakeReviewer:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def review(self, git_diff):
        self.calls.append(git_diff)
        return self.result


class FakeRepository:
    def __init__(self):
        self.local_path = r"C:\repositories\example"


def make_service(
    repository,
    diff_result,
    review_result,
):
    service = ReviewService.__new__(ReviewService)

    service.db = FakeDB(repository)

    service.git_diff_tool = FakeGitDiffTool(
        diff_result
    )

    service.reviewer = FakeReviewer(
        review_result
    )

    return service


def test_review_orchestrates_diff_and_reviewer():
    repository = FakeRepository()

    diff = """diff --git a/calculator.py b/calculator.py
@@ -1 +1 @@
-return a + b
+return a - b
"""

    review_result = {
        "summary": "A correctness issue was found.",
        "issues": [
            {
                "severity": "high",
                "category": "bug",
                "file": "calculator.py",
                "line": 2,
                "message": "The implementation subtracts instead of adding.",
                "suggestion": "Use a + b.",
            }
        ],
        "diff_size": len(diff),
    }

    service = make_service(
        repository=repository,
        diff_result={
            "repository_path": repository.local_path,
            "changed": True,
            "diff": diff,
        },
        review_result=review_result,
    )

    result = service.review(
        repository_id=7
    )

    assert result["repository_id"] == 7
    assert result["repository_path"] == (
        repository.local_path
    )
    assert result["summary"] == (
        "A correctness issue was found."
    )
    assert len(result["issues"]) == 1

    assert service.git_diff_tool.calls == [
        repository.local_path
    ]

    assert service.reviewer.calls == [
        diff
    ]


def test_review_with_empty_diff_does_not_fail():
    repository = FakeRepository()

    service = make_service(
        repository=repository,
        diff_result={
            "repository_path": repository.local_path,
            "changed": False,
            "diff": "",
        },
        review_result={
            "summary": "No changes to review.",
            "issues": [],
            "diff_size": 0,
        },
    )

    result = service.review(
        repository_id=3
    )

    assert result["repository_id"] == 3
    assert result["issues"] == []
    assert result["diff_size"] == 0

    assert service.reviewer.calls == [""]


def test_review_raises_when_repository_not_found():
    service = make_service(
        repository=None,
        diff_result={},
        review_result={},
    )

    with pytest.raises(
        FileNotFoundError,
        match="Repository not found",
    ):
        service.review(
            repository_id=999
        )
