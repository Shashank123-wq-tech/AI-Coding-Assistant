import subprocess

from app.repository.manager import RepositoryManager


def run_git(repository, *args):
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def test_diff_excludes_generated_python_artifacts(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()

    source_file = repository / "example.py"
    source_file.write_text(
        "def add(a, b):\n"
        "    return a + b\n",
        encoding="utf-8",
    )

    run_git(repository, "init", "-b", "main")
    run_git(repository, "config", "user.email", "test@example.com")
    run_git(repository, "config", "user.name", "Test User")

    run_git(repository, "add", ".")
    run_git(repository, "commit", "-m", "Initial commit")

    source_file.write_text(
        "def add(a, b):\n"
        "    return a - b\n",
        encoding="utf-8",
    )

    pycache = repository / "__pycache__"
    pycache.mkdir()

    pyc_file = pycache / "example.cpython-312.pyc"
    pyc_file.write_bytes(b"fake-pyc-data")

    result = RepositoryManager().diff(str(repository))

    assert result["changed"] is True
    assert "example.py" in result["diff"]
    assert "return a + b" in result["diff"]
    assert "return a - b" in result["diff"]
    assert "__pycache__" not in result["diff"]
    assert ".pyc" not in result["diff"]