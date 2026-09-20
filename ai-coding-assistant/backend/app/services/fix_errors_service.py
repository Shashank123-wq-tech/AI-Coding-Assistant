from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.agents.patch_agent import PatchAgent
from app.core.config import settings
from app.execution.failure_localizer import FailureLocalizer
from app.execution.test_runner import TestRunner
from app.repository.manager import RepositoryManager
from app.tools.patch_tools import PatchTools


class FixErrorsService:
    """
    Orchestrates automated test failure repair.

    Workflow:

        Run tests
            ↓
        Parse failure
            ↓
        Localize failing test
            ↓
        Resolve source file
            ↓
        Retrieve repository context
            ↓
        Generate patch
            ↓
        Apply patch
            ↓
        Validate changed files
            ↓
        Run tests again
            ↓
        Repeat until PASS or iteration limit

    Safety:

        - Repository path is validated.
        - Target file must remain inside repository.
        - Test files cannot be modified.
        - Git metadata cannot be modified.
        - Only allowed source files can be modified.
        - Unexpected changed files stop the repair workflow.
        - Ambiguous localization never guesses.
        - Agent iterations are limited.
        - No Git commits are performed.
    """

    def __init__(self, db: Session):
        self.db = db

        self.test_runner = TestRunner()

        self.patch_agent = PatchAgent(db)

        self.repository_manager = RepositoryManager()

    # =========================================================
    # REPOSITORY VALIDATION
    # =========================================================

    @staticmethod
    def _validate_repository(
        repository_path: str,
    ) -> Path:
        """
        Validate and resolve the repository path.
        """

        repository = Path(
            repository_path
        ).resolve()

        if not repository.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {repository}"
            )

        if not repository.is_dir():
            raise ValueError(
                f"Repository path is not a directory: {repository}"
            )

        return repository

    # =========================================================
    # TARGET FILE VALIDATION
    # =========================================================

    @staticmethod
    def _validate_target_file(
        repository: Path,
        file_path: str,
    ) -> Path:
        """
        Validate that a target file exists and is located
        inside the repository.
        """

        if not file_path or not file_path.strip():
            raise ValueError(
                "Target file path cannot be empty."
            )

        target_file = (
            repository / file_path
        ).resolve()

        try:
            target_file.relative_to(
                repository
            )
        except ValueError:
            raise PermissionError(
                "Target file must be inside the repository."
            )

        if not target_file.is_file():
            raise FileNotFoundError(
                f"Target file does not exist: {file_path}"
            )

        return target_file

    # =========================================================
    # TEST FILE PROTECTION
    # =========================================================

    @staticmethod
    def _is_test_file(
        file_path: str,
    ) -> bool:
        """
        Determine whether a path represents a test file.
        """

        path = Path(file_path)

        filename = path.name.lower()

        if filename.startswith("test_"):
            return True

        if filename.endswith("_test.py"):
            return True

        if "tests" in {
            part.lower()
            for part in path.parts
        }:
            return True

        return False

    # =========================================================
    # GIT METADATA PROTECTION
    # =========================================================

    @staticmethod
    def _is_git_file(
        file_path: str,
    ) -> bool:
        """
        Prevent modifications inside .git.
        """

        return (
            ".git"
            in {
                part.lower()
                for part in Path(file_path).parts
            }
        )

    # =========================================================
    # SOURCE FILE VALIDATION
    # =========================================================

    @staticmethod
    def _is_allowed_source_file(
        file_path: str,
    ) -> bool:
        """
        Check whether the file extension is supported
        by the coding assistant.
        """

        allowed_extensions = {
            ".py",
            ".pyi",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".go",
            ".rs",
        }

        return (
            Path(file_path)
            .suffix
            .lower()
            in allowed_extensions
        )

    # =========================================================
    # COMPLETE TARGET SAFETY VALIDATION
    # =========================================================

    def _validate_patch_target(
        self,
        repository: Path,
        file_path: str,
    ) -> Path:
        """
        Perform all safety checks before a file is given
        to PatchAgent.
        """

        target_file = (
            self._validate_target_file(
                repository,
                file_path,
            )
        )

        relative_path = (
            target_file
            .relative_to(repository)
            .as_posix()
        )

        # Never modify tests.
        if self._is_test_file(
            relative_path
        ):
            raise PermissionError(
                "Automatic repair cannot modify test files."
            )

        # Never modify Git metadata.
        if self._is_git_file(
            relative_path
        ):
            raise PermissionError(
                "Automatic repair cannot modify Git metadata."
            )

        # Only source files may be modified.
        if not self._is_allowed_source_file(
            relative_path
        ):
            raise PermissionError(
                "Automatic repair only supports allowed source files."
            )

        return target_file

    # =========================================================
    # DIFF HELPER
    # =========================================================

    def _get_diff(
        self,
        repository: Path,
    ) -> dict:
        """
        Return the current repository Git diff.
        """

        return self.repository_manager.diff(
            str(repository)
        )

    # =========================================================
    # MAIN FIX WORKFLOW
    # =========================================================

    def fix(
        self,
        repository_id: int,
        repository_path: str,
        request: str,
        file_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Automatically repair failing tests.

        Parameters
        ----------
        repository_id:
            Database repository ID.

        repository_path:
            Local repository path.

        request:
            Natural-language repair request.

        file_path:
            Optional explicit source file.

            If supplied:
                use this file directly.

            If omitted:
                automatically localize the source file from
                the failing test.

        Returns
        -------
        dict
            Structured repair result.
        """

        # =====================================================
        # 1. VALIDATE INPUT
        # =====================================================

        repository = (
            self._validate_repository(
                repository_path
            )
        )

        if not request or not request.strip():
            raise ValueError(
                "Repair request cannot be empty."
            )

        # =====================================================
        # 2. OPTIONAL EXPLICIT TARGET
        # =====================================================

        explicit_target_file = None

        if file_path:

            explicit_target_file = (
                self._validate_patch_target(
                    repository,
                    file_path,
                )
            )

        # =====================================================
        # 3. ITERATION STORAGE
        # =====================================================

        iterations = []

        # =====================================================
        # 4. AGENT ITERATION LOOP
        # =====================================================

        for iteration in range(
            1,
            settings.MAX_AGENT_ITERATIONS + 1,
        ):

            # -------------------------------------------------
            # 4.1 RUN TESTS
            # -------------------------------------------------

            test_result = (
                self.test_runner.run_tests(
                    str(repository)
                )
            )

            iteration_result = {
                "iteration": iteration,
                "test_before_fix": test_result,
            }

            # -------------------------------------------------
            # 4.2 TESTS PASSED
            # -------------------------------------------------

            if test_result["status"] == "passed":

                iteration_result[
                    "action"
                ] = "already_passed"

                iterations.append(
                    iteration_result
                )

                return {
                    "repository_id": repository_id,
                    "status": "passed",
                    "iterations": iterations,
                    "final_test": test_result,
                    "diff": self._get_diff(
                        repository
                    ),
                }

            # -------------------------------------------------
            # 4.3 NO TESTS
            # -------------------------------------------------

            if test_result["status"] == "no_tests":

                iteration_result[
                    "action"
                ] = "no_tests"

                iterations.append(
                    iteration_result
                )

                return {
                    "repository_id": repository_id,
                    "status": "no_tests",
                    "iterations": iterations,
                    "final_test": test_result,
                    "diff": self._get_diff(
                        repository
                    ),
                }

            # -------------------------------------------------
            # 4.4 EXTRACT ERROR
            # -------------------------------------------------

            error = (
                test_result.get(
                    "error",
                    {},
                )
            )

            # -------------------------------------------------
            # 4.5 DETERMINE TARGET FILE
            # -------------------------------------------------

            localized_file = None

            # =================================================
            # OPTION A:
            # USER EXPLICITLY PROVIDED FILE
            # =================================================

            if explicit_target_file is not None:

                localized_file = (
                    explicit_target_file
                    .relative_to(
                        repository
                    )
                    .as_posix()
                )

                localization = {
                    "localized": True,
                    "source_file": localized_file,
                    "source_files": [
                        localized_file
                    ],
                    "reason": (
                        "Explicit source file "
                        "provided by caller."
                    ),
                }

                iteration_result[
                    "localization"
                ] = localization

            # =================================================
            # OPTION B:
            # AUTOMATIC LOCALIZATION
            # =================================================

            else:

                failure_localizer = (
                    FailureLocalizer(
                        str(repository)
                    )
                )

                localization = (
                    failure_localizer.localize(
                        error.get("file")
                    )
                )

                iteration_result[
                    "localization"
                ] = localization

                # ---------------------------------------------
                # Localization failed / ambiguous.
                #
                # IMPORTANT:
                # Never guess.
                # ---------------------------------------------

                if not localization.get(
                    "localized",
                    False,
                ):

                    iteration_result[
                        "action"
                    ] = "unable_to_localize"

                    iterations.append(
                        iteration_result
                    )

                    return {
                        "repository_id": repository_id,
                        "status": (
                            "unable_to_localize"
                        ),
                        "iterations": iterations,
                        "diff": self._get_diff(
                            repository
                        ),
                    }

                localized_file = (
                    localization.get(
                        "source_file"
                    )
                )

            # =================================================
            # 4.6 ENSURE LOCALIZED FILE EXISTS
            # =================================================

            if not localized_file:

                iteration_result[
                    "action"
                ] = "unable_to_localize"

                iteration_result[
                    "localization_error"
                ] = (
                    "Localization did not return "
                    "a source file."
                )

                iterations.append(
                    iteration_result
                )

                return {
                    "repository_id": repository_id,
                    "status": (
                        "unable_to_localize"
                    ),
                    "iterations": iterations,
                    "diff": self._get_diff(
                        repository
                    ),
                }

            # =================================================
            # 4.7 VALIDATE LOCALIZED TARGET
            # =================================================

            try:

                target_file = (
                    self._validate_patch_target(
                        repository,
                        localized_file,
                    )
                )

            except (
                FileNotFoundError,
                ValueError,
                PermissionError,
            ) as exc:

                iteration_result[
                    "action"
                ] = "invalid_patch_target"

                iteration_result[
                    "localization_error"
                ] = str(exc)

                iterations.append(
                    iteration_result
                )

                return {
                    "repository_id": repository_id,
                    "status": "unable_to_fix",
                    "iterations": iterations,
                    "diff": self._get_diff(
                        repository
                    ),
                }

            # -------------------------------------------------
            # Store resolved target.
            # -------------------------------------------------

            iteration_result[
                "target_file"
            ] = localized_file

            # =================================================
            # 4.8 BUILD REPAIR REQUEST
            # =================================================

            repair_request = (
                f"{request}\n\n"
                "CURRENT TEST FAILURE\n"
                "====================\n"
                f"Error type: "
                f"{error.get('error_type')}\n"
                f"Message: "
                f"{error.get('message')}\n"
                f"Failure file: "
                f"{error.get('file')}\n"
                f"Failure line: "
                f"{error.get('line')}\n"
                f"Failing test function: "
                f"{error.get('function')}\n"
                f"Pytest failures: "
                f"{error.get('pytest_failures')}\n\n"
                "RESOLVED SOURCE FILE\n"
                "====================\n"
                f"{localized_file}\n\n"
                "REPAIR RULES\n"
                "============\n"
                "Fix the underlying source implementation.\n"
                "Do not modify the test.\n"
                "Do not modify unrelated files.\n"
                "Only modify the resolved source file."
            )

            # =================================================
            # 4.9 GENERATE PATCH
            # =================================================

            patch_result = (
                self.patch_agent.generate_patch(
                    repository_id=repository_id,
                    request=repair_request,
                    file_path=localized_file,
                )
            )

            iteration_result[
                "patch"
            ] = {
                "changed": patch_result.get(
                    "changed",
                    False,
                ),
                "file_path": patch_result.get(
                    "file_path",
                    localized_file,
                ),
                "patch": patch_result.get(
                    "patch",
                    "",
                ),
                "message": patch_result.get(
                    "message",
                    "Patch generated successfully.",
                ),
            }

            # =================================================
            # 4.10 PATCH NOT GENERATED
            # =================================================

            if not patch_result.get(
                "changed",
                False,
            ):

                iteration_result[
                    "action"
                ] = "no_patch_generated"

                iterations.append(
                    iteration_result
                )

                return {
                    "repository_id": repository_id,
                    "status": "unable_to_fix",
                    "iterations": iterations,
                    "diff": self._get_diff(
                        repository
                    ),
                }

            # =================================================
            # 4.11 REQUIRE NEW FILE CONTENT
            # =================================================

            new_content = (
                patch_result.get(
                    "new_content"
                )
            )

            if new_content is None:

                iteration_result[
                    "action"
                ] = (
                    "patch_missing_new_content"
                )

                iterations.append(
                    iteration_result
                )

                return {
                    "repository_id": repository_id,
                    "status": "unable_to_fix",
                    "iterations": iterations,
                    "diff": self._get_diff(
                        repository
                    ),
                }

            # =================================================
            # 4.12 PATCH TOOLS
            # =================================================

            patch_tools = PatchTools(
                str(repository)
            )

            # =================================================
            # 4.13 SNAPSHOT BEFORE PATCH
            # =================================================

            before_snapshot = (
                patch_tools.snapshot_files()
            )

            # =================================================
            # 4.14 READ TARGET FILE
            # =================================================

            try:

                old_content = (
                    target_file.read_text(
                        encoding="utf-8"
                    )
                )

            except UnicodeDecodeError:

                iteration_result[
                    "action"
                ] = "target_file_not_utf8"

                iterations.append(
                    iteration_result
                )

                return {
                    "repository_id": repository_id,
                    "status": "unable_to_fix",
                    "iterations": iterations,
                    "diff": self._get_diff(
                        repository
                    ),
                }

            except OSError as exc:

                iteration_result[
                    "action"
                ] = "target_file_read_failed"

                iteration_result[
                    "error"
                ] = str(exc)

                iterations.append(
                    iteration_result
                )

                return {
                    "repository_id": repository_id,
                    "status": "unable_to_fix",
                    "iterations": iterations,
                    "diff": self._get_diff(
                        repository
                    ),
                }

            # =================================================
            # 4.15 APPLY PATCH
            # =================================================

            apply_result = (
                patch_tools.apply_patch(
                    str(target_file),
                    old_content,
                    new_content,
                )
            )

            iteration_result[
                "apply"
            ] = apply_result

            # =================================================
            # 4.16 PATCH APPLICATION FAILED
            # =================================================

            if not apply_result.get(
                "applied",
                False,
            ):

                iteration_result[
                    "action"
                ] = "patch_apply_failed"

                iterations.append(
                    iteration_result
                )

                return {
                    "repository_id": repository_id,
                    "status": "unable_to_fix",
                    "iterations": iterations,
                    "diff": self._get_diff(
                        repository
                    ),
                }

            # =================================================
            # 4.17 VALIDATE CHANGED FILES
            # =================================================

            changed_files_validation = (
                patch_tools.validate_changed_files(
                    expected_files=[
                        localized_file
                    ],
                    before_snapshot=(
                        before_snapshot
                    ),
                )
            )

            iteration_result[
                "changed_files_validation"
            ] = changed_files_validation

            # =================================================
            # 4.18 UNEXPECTED FILE CHANGED
            # =================================================
            
            

            if not changed_files_validation.get(
                "valid",
                False,
            ):

                iteration_result[
                    "action"
                ] = (
                    "unexpected_files_changed"
                )

                iterations.append(
                    iteration_result
                )

                return {
                    "repository_id": repository_id,
                    "status": "unable_to_fix",
                    "iterations": iterations,
                    "diff": self._get_diff(
                        repository
                    ),
                }

            # =================================================
            # 4.19 PATCH SUCCESSFULLY APPLIED
            # =================================================

            iteration_result[
                "action"
            ] = "patch_applied"

            iterations.append(
                iteration_result
            )

        # =====================================================
        # 5. MAX ITERATIONS REACHED
        # =====================================================

        final_test_result = (
            self.test_runner.run_tests(
                str(repository)
            )
        )

        if (
            final_test_result["status"]
            == "passed"
        ):
            status = "passed"
        else:
            status = "max_iterations_reached"

        # =====================================================
        # 6. FINAL RESPONSE
        # =====================================================

        return {
            "repository_id": repository_id,
            "status": status,
            "iterations": iterations,
            "final_test": final_test_result,
            "diff": self._get_diff(
                repository
            ),
        }
