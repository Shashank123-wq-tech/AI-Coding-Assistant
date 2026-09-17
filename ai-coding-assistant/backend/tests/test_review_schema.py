import pytest
from pydantic import ValidationError

from app.schemas.review import (
    CodeReviewResponse,
    ReviewCategory,
    ReviewIssue,
    ReviewSeverity,
)


def test_review_issue_accepts_valid_values():
    issue = ReviewIssue(
        severity="high",
        category="bug",
        file="calculator.py",
        line=2,
        message="Incorrect arithmetic operation.",
        suggestion="Use a + b.",
    )

    assert issue.severity == ReviewSeverity.HIGH
    assert issue.category == ReviewCategory.BUG
    assert issue.line == 2


def test_review_issue_rejects_invalid_severity():
    with pytest.raises(ValidationError):
        ReviewIssue(
            severity="extreme",
            category="bug",
            file="calculator.py",
            line=2,
            message="Invalid severity.",
        )


def test_review_issue_rejects_invalid_category():
    with pytest.raises(ValidationError):
        ReviewIssue(
            severity="high",
            category="style",
            file="calculator.py",
            line=2,
            message="Invalid category.",
        )


def test_review_issue_rejects_invalid_line():
    with pytest.raises(ValidationError):
        ReviewIssue(
            severity="high",
            category="bug",
            file="calculator.py",
            line=0,
            message="Line must be positive.",
        )


def test_review_issue_allows_null_line():
    issue = ReviewIssue(
        severity="low",
        category="maintainability",
        file="calculator.py",
        line=None,
        message="Minor maintainability concern.",
    )

    assert issue.line is None


def test_review_response_rejects_negative_diff_size():
    with pytest.raises(ValidationError):
        CodeReviewResponse(
            repository_id=2,
            repository_path="/repo",
            summary="Review completed.",
            issues=[],
            diff_size=-1,
        )


def test_review_response_accepts_empty_issues():
    response = CodeReviewResponse(
        repository_id=2,
        repository_path="/repo",
        summary="No changes to review.",
        issues=[],
        diff_size=0,
    )

    assert response.issues == []
    assert response.diff_size == 0
