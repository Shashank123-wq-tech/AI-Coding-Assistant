from pathlib import Path

import pytest

from app.tools.patch_tools import PatchTools


def create_repository(tmp_path: Path) -> Path:
    repository = tmp_path / "repository"

    repository.mkdir()

    (repository / "calculator.py").write_text(
        "def add(a, b):\n"
        "    return a + b\n",
        encoding="utf-8",
    )

    (repository / "test_calculator.py").write_text(
        "def test_add():\n"
        "    assert True\n",
        encoding="utf-8",
    )

    (repository / "notes.txt").write_text(
        "internal notes\n",
        encoding="utf-8",
    )

    return repository


def test_apply_patch_allows_valid_source_file(tmp_path):
    repository = create_repository(tmp_path)

    tools = PatchTools(str(repository))

    old_content = (
        "def add(a, b):\n"
        "    return a + b\n"
    )

    new_content = (
        "def add(a, b):\n"
        "    return a + b + 1\n"
    )

    result = tools.apply_patch(
        file_path="calculator.py",
        old_content=old_content,
        new_content=new_content,
    )

    assert result["applied"] is True

    assert (
        (repository / "calculator.py").read_text(
            encoding="utf-8"
        )
        == new_content
    )


def test_apply_patch_rejects_test_file(tmp_path):
    repository = create_repository(tmp_path)

    tools = PatchTools(str(repository))

    with pytest.raises(PermissionError, match="test files"):
        tools.apply_patch(
            file_path="test_calculator.py",
            old_content=(
                "def test_add():\n"
                "    assert True\n"
            ),
            new_content=(
                "def test_add():\n"
                "    assert False\n"
            ),
        )


def test_apply_patch_rejects_git_metadata(tmp_path):
    repository = create_repository(tmp_path)

    git_directory = repository / ".git"
    git_directory.mkdir()

    git_file = git_directory / "config"

    git_file.write_text(
        "[core]\n",
        encoding="utf-8",
    )

    tools = PatchTools(str(repository))

    with pytest.raises(
        PermissionError,
        match="Git metadata",
    ):
        tools.apply_patch(
            file_path=".git/config",
            old_content="[core]\n",
            new_content="[core]\nmodified=true\n",
        )


def test_apply_patch_rejects_unsupported_file_type(tmp_path):
    repository = create_repository(tmp_path)

    tools = PatchTools(str(repository))

    with pytest.raises(
        PermissionError,
        match="allowed source files",
    ):
        tools.apply_patch(
            file_path="notes.txt",
            old_content="internal notes\n",
            new_content="modified notes\n",
        )


def test_apply_patch_rejects_path_traversal(tmp_path):
    repository = create_repository(tmp_path)

    outside_file = tmp_path / "outside.py"

    outside_file.write_text(
        "original\n",
        encoding="utf-8",
    )

    tools = PatchTools(str(repository))

    with pytest.raises(
        PermissionError,
        match="outside the repository",
    ):
        tools.apply_patch(
            file_path="../outside.py",
            old_content="original\n",
            new_content="modified\n",
        )

    assert (
        outside_file.read_text(
            encoding="utf-8"
        )
        == "original\n"
    )


def test_apply_patch_rejects_stale_file_content(tmp_path):
    repository = create_repository(tmp_path)

    tools = PatchTools(str(repository))

    result = tools.apply_patch(
        file_path="calculator.py",
        old_content=(
            "def add(a, b):\n"
            "    return a - b\n"
        ),
        new_content=(
            "def add(a, b):\n"
            "    return a + b\n"
        ),
    )

    assert result["applied"] is False

    assert (
        "changed since it was read"
        in result["reason"]
    )

    assert (
        (repository / "calculator.py").read_text(
            encoding="utf-8"
        )
        == (
            "def add(a, b):\n"
            "    return a + b\n"
        )
    )


def test_validate_changed_files_detects_unexpected_file(
    tmp_path,
):
    repository = create_repository(tmp_path)

    tools = PatchTools(str(repository))

    before = tools.snapshot_files()

    (
        repository / "calculator.py"
    ).write_text(
        "def add(a, b):\n"
        "    return a + b + 1\n",
        encoding="utf-8",
    )

    (
        repository / "notes.txt"
    ).write_text(
        "unexpected modification\n",
        encoding="utf-8",
    )

    result = tools.validate_changed_files(
        expected_files=["calculator.py"],
        before_snapshot=before,
    )

    assert result["valid"] is False

    assert (
        "calculator.py"
        in result["actual_files"]
    )

    assert (
        "notes.txt"
        in result["unexpected_files"]
    )

    assert (
        result["missing_expected_files"]
        == []
    )