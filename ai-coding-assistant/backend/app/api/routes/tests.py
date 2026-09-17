from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.repository import Repository
from app.execution.test_runner import TestRunner


router = APIRouter(
    prefix="/repositories",
    tags=["tests"],
)


@router.post("/{repository_id}/tests")
def run_repository_tests(
    repository_id: int,
    db: Session = Depends(get_db),
):
    repository = (
        db.query(Repository)
        .filter(Repository.id == repository_id)
        .first()
    )

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found.",
        )

    try:
        test_runner = TestRunner()

        result = test_runner.run_tests(
            repository.local_path
        )

        return {
            "repository_id": repository_id,
            **result,
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Test execution failed: {str(exc)}",
        )
