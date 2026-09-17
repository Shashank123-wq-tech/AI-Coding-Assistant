from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any


class RepositoryCreate(BaseModel):
    url: str = Field(..., min_length=1)

class PatchApplyRequest(BaseModel):
    old_content: str
    new_content: str

class FixErrorsRequest(BaseModel):
    file_path: str | None = Field(
        default=None,
        min_length=1,
    )
    request: str = Field(
        ...,
        min_length=1,
    )
    
class RepositoryResponse(BaseModel):
    id: int
    name: str
    url: str
    local_path: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

        
class TestErrorResponse(BaseModel):
    has_error: bool
    error_type: str | None = None
    message: str | None = None
    file: str | None = None
    line: int | None = None
    function: str | None = None
    pytest_failures: list[dict[str, str]] = Field(
        default_factory=list
    )
    stderr: str = ""
    stdout: str = ""


class TestResultResponse(BaseModel):
    returncode: int
    stdout: str
    stderr: str
    status: str
    error: TestErrorResponse


class PatchResponse(BaseModel):
    changed: bool
    file_path: str
    patch: str
    message: str


class ApplyPatchResponse(BaseModel):
    applied: bool
    file_path: str
    patch: str
    message: str


class FixIterationResponse(BaseModel):
    iteration: int
    test_before_fix: TestResultResponse
    patch: PatchResponse | None = None
    apply: ApplyPatchResponse | None = None
    action: str | None = None


class GitDiffResponse(BaseModel):
    repository_path: str
    changed: bool
    diff: str


class FixErrorsResponse(BaseModel):
    repository_id: int
    status: str
    iterations: list[FixIterationResponse]
    final_test: TestResultResponse | None = None
    diff: GitDiffResponse