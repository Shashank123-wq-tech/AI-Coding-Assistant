from enum import Enum

from pydantic import BaseModel, Field


class ReviewSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewCategory(str, Enum):
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    CORRECTNESS = "correctness"


class ReviewIssue(BaseModel):
    severity: ReviewSeverity
    category: ReviewCategory
    file: str
    line: int | None = Field(
        default=None,
        ge=1,
    )
    message: str
    suggestion: str | None = None


class CodeReviewResponse(BaseModel):
    repository_id: int
    repository_path: str
    summary: str
    issues: list[ReviewIssue] = Field(
        default_factory=list
    )
    diff_size: int = Field(
        ge=0,
    )