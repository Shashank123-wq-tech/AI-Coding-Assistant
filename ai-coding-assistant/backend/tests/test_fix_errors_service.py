from pathlib import Path

from app.services.fix_errors_service import FixErrorsService


class FakeTestRunner:
    def __init__(self):
        self.calls = 0

    def run_tests(self, repository_path: str):
        self.calls += 1

        if self.calls == 1:
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": "",
                "status": "failed",
                "error": {
                    "file": "tests/test_calculator.py",
                    "line": 4,
                    "function": "test_add",
                    "error_type": "AssertionError",
                    "message": "-1 == 5",
                    "pytest_failures": [
                        {
                            "file": "tests/test_calculator.py",
                            "test": "test_add",
                        }
                    ],
                },
            }

        return {
            "returncode": 0,
            "stdout": "1 passed in 0.01s",
            "stderr": "",
            "status": "passed",
            "error": {},
        }


class FakePatchAgent:
    def __init__(self):
        self.calls = []

    def generate_patch(
        self,
        repository_id: int,
        request: str,
        file_path: str,
    ):
        self.calls.append(
            {
                "repository_id": repository_id,
                "request": request,
                "file_path": file_path,
            }
        )

        return {
            "changed": True,
            "file_path": file_path,
            "patch": (
                "--- src/calculator/operations.py\n"
                "+++ src/calculator/operations.py\n"
                "@@ -1,2 +1,2 @@\n"
                " def add(a, b):\n"
                "-    return a - b\n"
                "+    return a + b\n"
            ),
            "message": "Patch generated successfully.",
            "new_content": (
                "def add(a, b):\n"
                "    return a + b\n"
            ),
        }


class FakeRepositoryManager:
    def diff(self, repository_path: str):
        return ""


def create_buggy_repository(tmp_path: Path) -> Path:
    package = tmp_path / "src" / "calculator"
    tests = tmp_path / "tests"

    package.mkdir(parents=True)
    tests.mkdir()

    (package / "__init__.py").write_text(
        "from .operations import add\n\n"
        '__all__ = ["add"]\n',
        encoding="utf-8",
    )

    (package / "operations.py").write_text(
        "def add(a, b):\n"
        "    return a - b\n",
        encoding="utf-8",
    )

    (tests / "test_calculator.py").write_text(
        "from calculator import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    return tmp_path


def test_fix_service_repairs_localized_source_file(tmp_path):
    repository = create_buggy_repository(tmp_path)

    service = FixErrorsService.__new__(FixErrorsService)

    service.db = None
    service.test_runner = FakeTestRunner()
    service.patch_agent = FakePatchAgent()
    service.repository_manager = FakeRepositoryManager()

    result = service.fix(
        repository_id=123,
        repository_path=str(repository),
        request="Fix the failing test",
    )

    assert result["status"] == "passed"

    assert len(result["iterations"]) == 2

    first_iteration = result["iterations"][0]

    assert (
        Path(
            first_iteration["localization"]["source_file"]
        ).as_posix()
        == "src/calculator/operations.py"
    )

    assert (
        Path(
            first_iteration["target_file"]
        ).as_posix()
        == "src/calculator/operations.py"
    )

    assert (
        first_iteration["patch"]["changed"]
        is True
    )

    assert (
        first_iteration["action"]
        != "no_patch_generated"
    )

    second_iteration = result["iterations"][1]

    assert (
        second_iteration["action"]
        == "already_passed"
    )

    operations_file = (
        repository
        / "src"
        / "calculator"
        / "operations.py"
    )

    assert operations_file.read_text(
        encoding="utf-8"
    ) == (
        "def add(a, b):\n"
        "    return a + b\n"
    )

    assert service.test_runner.calls == 2

    assert len(service.patch_agent.calls) == 1

    assert (
        Path(
            service.patch_agent.calls[0]["file_path"]
        ).as_posix()
        == "src/calculator/operations.py"
    )

    assert (
        "Do not modify the test."
        in service.patch_agent.calls[0]["request"]
    )