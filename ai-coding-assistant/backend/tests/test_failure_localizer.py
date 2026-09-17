from pathlib import Path

from app.execution.failure_localizer import FailureLocalizer


def create_src_repository(tmp_path: Path):
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

    (tests / "test_operations.py").write_text(
        "from calculator.operations import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    return tests / "test_operations.py"


def test_localizes_src_layout_module_import(tmp_path):
    test_file = create_src_repository(tmp_path)

    localizer = FailureLocalizer(str(tmp_path))

    result = localizer.localize(
        str(test_file.relative_to(tmp_path))
    )

    assert result["localized"] is True
    assert result["source_file"] == str(
        Path("src") / "calculator" / "operations.py"
    )


def test_localizes_package_reexport(tmp_path):
    test_file = create_src_repository(tmp_path)

    test_file.write_text(
        "from calculator import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    localizer = FailureLocalizer(str(tmp_path))

    result = localizer.localize(
        str(test_file.relative_to(tmp_path))
    )

    assert result["localized"] is True
    assert result["source_file"] == str(
        Path("src") / "calculator" / "operations.py"
    )