from app.execution.error_parser import ErrorParser
from app.execution.sandbox import DockerSandbox


class TestRunner:
    def __init__(self):
        self.sandbox = DockerSandbox()
        self.error_parser = ErrorParser()

    def run_tests(self, repository_path: str):
        result = self.sandbox.run(
            repository_path,
            ["python", "-m", "pytest", "-q"],
        )

        if result["returncode"] == 0:
            status = "passed"
        elif result["returncode"] == 5:
            status = "no_tests"
        else:
            status = "failed"

        error = self.error_parser.parse(
            stderr=result["stderr"],
            stdout=result["stdout"],
        )

        return {
            **result,
            "status": status,
            "error": error,
        }