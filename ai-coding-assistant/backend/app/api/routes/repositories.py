from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.agents.rag_service import RepositoryQAService
from app.repository.scanner import RepositoryScanner
from app.database.session import get_db
from app.models.repository import Repository
from app.repository.manager import RepositoryManager
from app.schemas.repository import (
    PatchApplyRequest,
    RepositoryCreate,
    RepositoryResponse,
    
)
from app.code_intelligence.repository_analyzer import RepositoryAnalyzer
from app.services.indexing_service import IndexingService
from app.services.search_service import SearchService
from app.services.retrieval_service import RetrievalService
from app.agents.coding_agent import CodingAgent
from app.agents.patch_agent import PatchAgent
from app.tools.patch_tools import PatchTools
from app.tools.git_diff import GitDiffTool
from app.schemas.repository import FixErrorsRequest, FixErrorsResponse
from app.services.fix_errors_service import FixErrorsService
from app.services.review_service import ReviewService
from app.schemas.review import CodeReviewResponse
from app.tools.file_tools import FileTools

router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repository(
    repository_data: RepositoryCreate,
    db: Session = Depends(get_db),
):
    url = repository_data.url.strip()

    manager = RepositoryManager()

    if not manager.validate_github_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL.",
        )

    existing_repository = (
        db.query(Repository)
        .filter(Repository.url == url)
        .first()
    )

    if existing_repository:
        raise HTTPException(
            status_code=409,
            detail="Repository is already connected.",
        )

    try:
        name, local_path = manager.clone_repository(url)

    except FileExistsError as exc:
        raise HTTPException(
            status_code=409,
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

    repository = Repository(
        name=name,
        url=url,
        local_path=local_path,
        status="cloned",
    )

    db.add(repository)
    db.commit()
    db.refresh(repository)

    return repository

@router.get("/{repository_id}/search")
def search_repository(
    repository_id: int,
    q: str,
    limit: int = 10,
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

    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 50.",
        )

    try:
        search_service = SearchService(db)

        results = search_service.search(
            repository_id=repository_id,
            query=q,
            limit=limit,
        )

        return {
            "repository_id": repository_id,
            "query": q,
            "total_results": len(results),
            "results": results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Repository search failed: {exc}",
        )

@router.post("/{repository_id}/scan")
def scan_repository(
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
        # --------------------------------------------------
        # 1. Scan repository
        # --------------------------------------------------

        scanner = RepositoryScanner(
            repository.local_path
        )

        scan_result = scanner.scan()

        # --------------------------------------------------
        # 2. Analyze repository code structure
        # --------------------------------------------------

        analyzer = RepositoryAnalyzer(
            repository.local_path
        )

        analysis_result = analyzer.analyze()

        # --------------------------------------------------
        # 3. Update repository status
        # --------------------------------------------------

        repository.status = "scanned"

        db.commit()
        db.refresh(repository)

        # --------------------------------------------------
        # 4. Return complete result
        # --------------------------------------------------

        return {
            "repository_id": repository.id,
            "status": "scanned",
            "scan": scan_result,
            "analysis": analysis_result,
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

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Repository scanning failed: {exc}",
        )


@router.post("/{repository_id}/index")
def index_repository(
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
        indexing_service = IndexingService(db)

        result = indexing_service.index_repository(
            repository
        )

        return result

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

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Repository indexing failed: {exc}",
        )

@router.get("/{repository_id}/retrieve")
def retrieve_repository(
    repository_id: int,
    q: str,
    limit: int = 10,
    method: str = "hybrid",
    db: Session = Depends(get_db),
):
    if method not in {"exact", "bm25", "hybrid"}:
        raise HTTPException(
            status_code=400,
            detail="Method must be one of: exact, bm25, hybrid.",
        )

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be greater than 0.",
        )

    retrieval_service = RetrievalService(db)

    try:
        results = retrieval_service.search(
            repository_id=repository_id,
            query=q,
            limit=limit,
            method=method,
        )

        return {
            "repository_id": repository_id,
            "query": q,
            "retrieval_method": method,
            "total_results": len(results),
            "results": results,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Repository retrieval failed: {exc}",
        )

@router.get("/{repository_id}/qa")
def repository_question_answer(
    repository_id: int,
    q: str,
    limit: int = 5,
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

    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 20.",
        )

    try:
        qa_service = RepositoryQAService(db)

        result = qa_service.answer(
            repository_id=repository_id,
            query=q,
            limit=limit,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Repository Q&A failed: {exc}",
        )
        
@router.get("/{repository_id}/agent")
def coding_agent_analysis(
    repository_id: int,
    request: str,
    limit: int = 8,
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

    if not request.strip():
        raise HTTPException(
            status_code=400,
            detail="Coding request cannot be empty.",
        )

    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 20.",
        )

    try:
        coding_agent = CodingAgent(db)

        result = coding_agent.analyze(
            repository_id=repository_id,
            request=request,
            limit=limit,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Coding agent analysis failed: {exc}",
        ) 
        
@router.get("/{repository_id}/file")
def read_repository_file(
    repository_id: int,
    file_path: str,
    db: Session = Depends(get_db),
):
    """
    Read a source file from the selected repository.

    The file path is validated by FileTools so files outside
    the repository cannot be accessed.
    """

    repository = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id
        )
        .first()
    )

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found.",
        )

    if not file_path.strip():
        raise HTTPException(
            status_code=400,
            detail="File path cannot be empty.",
        )

    try:
        file_tools = FileTools(
            repository.local_path
        )

        return {
            "repository_id": repository_id,
            **file_tools.read_file(file_path),
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"File read failed: {str(exc)}",
        )        
        

@router.post("/{repository_id}/agent/patch")
def generate_repository_patch(
    repository_id: int,
    request: str,
    file_path: str,
    limit: int = 5,
    db: Session = Depends(get_db),
):
    """
    Generate a proposed patch for a repository file.

    This endpoint is generate-only:
    it does NOT modify the repository.
    """

    repository = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id
        )
        .first()
    )

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found.",
        )

    if not request.strip():
        raise HTTPException(
            status_code=400,
            detail="Coding request cannot be empty.",
        )

    if not file_path.strip():
        raise HTTPException(
            status_code=400,
            detail="File path cannot be empty.",
        )

    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 20.",
        )

    try:
        patch_agent = PatchAgent(db)

        result = patch_agent.generate_patch(
            repository_id=repository_id,
            request=request,
            file_path=file_path,
            limit=limit,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Patch generation failed: {str(exc)}",
        )
               
@router.post("/{repository_id}/agent/patch/apply")
def apply_repository_patch(
    repository_id: int,
    file_path: str,
    patch_request: PatchApplyRequest,
    db: Session = Depends(get_db),
):
    """
    Apply a previously generated patch to a repository file.

    The patch is applied only when the file's current content
    exactly matches old_content.

    This prevents overwriting changes made after patch generation.
    """

    repository = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id
        )
        .first()
    )

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found.",
        )

    if not file_path.strip():
        raise HTTPException(
            status_code=400,
            detail="File path cannot be empty.",
        )

    try:
        patch_tools = PatchTools(
            repository.local_path
        )

        result = patch_tools.apply_patch(
            file_path=file_path,
            old_content=patch_request.old_content,
            new_content=patch_request.new_content,
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

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Patch application failed: {str(exc)}",
        )  
        
@router.get("/{repository_id}/git-diff")
def repository_git_diff(
    repository_id: int,
    db: Session = Depends(get_db),
):
    """
    Return the current Git working-tree diff for a repository.

    This endpoint is read-only and does not modify the repository.
    """

    repository = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id
        )
        .first()
    )

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found.",
        )

    try:
        git_diff_tool = GitDiffTool()

        result = git_diff_tool.run(
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
            detail=f"Git diff generation failed: {str(exc)}",
        )          

@router.get(
    "",
    response_model=list[RepositoryResponse],
)
def list_repositories(
    db: Session = Depends(get_db),
):
    return (
        db.query(Repository)
        .order_by(Repository.created_at.desc())
        .all()
    )


@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
)
def get_repository(
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

    return repository

@router.post(
    "/{repository_id}/review",
    response_model=CodeReviewResponse,
)
def review_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):
    try:
        service = ReviewService(db)

        return service.review(
            repository_id=repository_id
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error reviewing repository: {exc}",
        ) from exc

@router.delete(
    "/{repository_id}",
)
def delete_repository(
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

    local_path = repository.local_path

    db.delete(repository)
    db.commit()

    return {
        "message": "Repository removed successfully.",
        "repository_id": repository_id,
        "local_path": local_path,
    }

@router.post(
    "/{repository_id}/fix",
    response_model=FixErrorsResponse,
)
def fix_repository_errors(
    repository_id: int,
    payload: FixErrorsRequest,
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
        service = FixErrorsService(db)

        result = service.fix(
            repository_id=repository_id,
            repository_path=repository.local_path,
            request=payload.request,
            file_path=payload.file_path,
        )

        return result

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
            detail=f"Error fixing repository: {str(exc)}",
        )    

