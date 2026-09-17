from pathlib import Path
import subprocess


class DockerSandbox:
    """
    Secure Docker-based execution environment.

    The repository is mounted read/write into /workspace.
    Python src-layout repositories are automatically supported
    by setting PYTHONPATH=/workspace/src.
    """

    def __init__(
        self,
        cpu_limit: str = "1",
        memory_limit: str = "512m",
        pids_limit: str = "100",
    ):
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.pids_limit = pids_limit

    def run(
        self,
        repository_path: str,
        command: list[str],
        timeout: int = 120,
    ):
        repository = Path(repository_path).resolve()

        if not repository.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {repository}"
            )

        if not repository.is_dir():
            raise ValueError(
                f"Repository path is not a directory: {repository}"
            )

        

        docker_command = [
            "docker",
            "run",
            "--rm",

            "--cpus",
            self.cpu_limit,

            "--memory",
            self.memory_limit,

            "--pids-limit",
            self.pids_limit,

            "--network",
            "none",

            "--user",
            "1000:1000",

            "-v",
            f"{repository}:/workspace",

            "-w",
            "/workspace",
        ]

        src_directory = repository / "src"

        if src_directory.is_dir():
            docker_command.extend(
                [
                    "-e",
                    "PYTHONPATH=/workspace/src",
                ]
            )

        docker_command.append(
            "ai-coding-test-runner:latest"
        )
        

        docker_command.extend(command)

        result = subprocess.run(
            docker_command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }