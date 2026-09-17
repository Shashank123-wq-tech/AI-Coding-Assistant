import pytest

from app.review.reviewer import CodeReviewer


class FakeLLMProvider:
    def __init__(self, response: str):
        self.response = response
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


def make_reviewer(response: str) -> CodeReviewer:
    reviewer = CodeReviewer.__new__(CodeReviewer)
    reviewer.llm_provider = FakeLLMProvider(response)
    return reviewer


def test_empty_diff_returns_no_issues():
    reviewer = make_reviewer("{}")

    result = reviewer.review("")

    assert result == {
        "summary": "No changes to review.",
        "issues": [],
        "diff_size": 0,
    }


def test_valid_llm_review_is_parsed():
    reviewer = make_reviewer(
        """
        {
            "summary": "The change introduces a subtraction bug.",
            "issues": [
                {
                    "severity": "high",
                    "category": "bug",
                    "file": "calculator.py",
                    "line": 2,
                    "message": "The function subtracts instead of adding the inputs.",
                    "suggestion": "Return a + b."
                }
            ]
        }
        """
    )

    diff = """diff --git a/calculator.py b/calculator.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a + b
+    return a - b
"""

    result = reviewer.review(diff)

    assert result["summary"] == (
        "The change introduces a subtraction bug."
    )
    assert result["diff_size"] == len(diff)
    assert len(result["issues"]) == 1

    issue = result["issues"][0]

    assert issue["severity"] == "high"
    assert issue["category"] == "bug"
    assert issue["file"] == "calculator.py"
    assert issue["line"] == 2
    assert issue["message"].startswith(
        "The function subtracts"
    )
    assert issue["suggestion"] == "Return a + b."


def test_invalid_issues_are_filtered():
    reviewer = make_reviewer(
        """
        {
            "summary": "Review completed.",
            "issues": [
                {
                    "severity": "critical",
                    "category": "security",
                    "file": "app.py",
                    "line": 9,
                    "message": "Unsafe operation.",
                    "suggestion": "Validate the input."
                },
                {
                    "severity": "invalid",
                    "category": "bug",
                    "file": "bad.py",
                    "line": 5,
                    "message": "Invalid severity."
                },
                {
                    "severity": "low",
                    "category": "bug",
                    "file": "",
                    "line": 5,
                    "message": "Invalid file."
                }
            ]
        }
        """
    )

    git_diff = "\n".join([
    "diff --git a/app.py b/app.py",
    "index 123..456 100644",
    "--- a/app.py",
    "+++ b/app.py",
    "@@ -9,1 +9,1 @@",
    "-old_value = 1",
    "+new_value = 2",
    ])

    result = reviewer.review(git_diff)

    assert len(result["issues"]) == 1
    assert result["issues"][0]["severity"] == "critical"
    assert result["issues"][0]["file"] == "app.py"
    assert result["issues"][0]["line"] == 9


def test_invalid_json_raises_error():
    reviewer = make_reviewer(
        "this is not json"
    )

    with pytest.raises(ValueError, match="invalid JSON"):
        reviewer.review("some diff")


def test_non_object_json_raises_error():
    reviewer = make_reviewer(
        "[]"
    )

    with pytest.raises(
        ValueError,
        match="must be a JSON object",
    ):
        reviewer.review("some diff")


def test_review_prompt_contains_diff():
    reviewer = make_reviewer(
        '{"summary": "No issues.", "issues": []}'
    )

    diff = "diff --git a/app.py b/app.py\n+print('hello')"

    reviewer.review(diff)

    provider = reviewer.llm_provider

    assert len(provider.prompts) == 1
    assert diff in provider.prompts[0]
    assert "Return ONLY valid JSON." in provider.prompts[0]

def test_extract_changed_files():
    git_diff = """diff --git a/calculator.py b/calculator.py
index 123..456 100644
--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a + b
+    return a - b
"""

    files = CodeReviewer._extract_changed_files(
        git_diff
    )

    assert files == {"calculator.py"}


def test_filter_issues_keeps_only_changed_files():
    git_diff = """diff --git a/calculator.py b/calculator.py
index 123..456 100644
--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a + b
+    return a - b
"""

    issues = [
        {
            "severity": "high",
            "category": "bug",
            "file": "calculator.py",
            "line": 2,
            "message": "Incorrect arithmetic operation.",
            "suggestion": "Use a + b.",
        },
        {
            "severity": "medium",
            "category": "bug",
            "file": "unrelated.py",
            "line": 10,
            "message": "Unrelated issue.",
            "suggestion": "Fix it.",
        },
    ]

    filtered = CodeReviewer._filter_issues_by_diff_scope(
        issues,
        git_diff,
    )

    assert len(filtered) == 1
    assert filtered[0]["file"] == "calculator.py"


def test_filter_issues_normalizes_windows_paths():
    git_diff = """diff --git a/src/calculator.py b/src/calculator.py
index 123..456 100644
--- a/src/calculator.py
+++ b/src/calculator.py
@@ -1 +1 @@
-return a + b
+return a - b
"""

    issues = [
        {
            "severity": "high",
            "category": "bug",
            "file": r"src\calculator.py",
            "line": 1,
            "message": "Incorrect arithmetic operation.",
            "suggestion": "Use addition.",
        }
    ]

    filtered = CodeReviewer._filter_issues_by_diff_scope(
        issues,
        git_diff,
    )

    assert len(filtered) == 1
    assert filtered[0]["file"] == r"src\calculator.py"

def test_extract_changed_lines():
    git_diff = """diff --git a/calculator.py b/calculator.py
index 123..456 100644
--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a + b
+    return a - b
"""

    changed_lines = CodeReviewer._extract_changed_lines(
        git_diff
    )

    assert changed_lines == {
        "calculator.py": {2}
    }


def test_filter_issues_by_changed_lines():
    git_diff = """diff --git a/calculator.py b/calculator.py
index 123..456 100644
--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a + b
+    return a - b
"""

    issues = [
        {
            "severity": "high",
            "category": "bug",
            "file": "calculator.py",
            "line": 2,
            "message": "Incorrect arithmetic operation.",
            "suggestion": "Use addition.",
        },
        {
            "severity": "medium",
            "category": "bug",
            "file": "calculator.py",
            "line": 1,
            "message": "Unrelated line.",
            "suggestion": "No change needed.",
        },
        {
            "severity": "low",
            "category": "maintainability",
            "file": "calculator.py",
            "line": None,
            "message": "General issue related to the change.",
            "suggestion": "Consider improving it.",
        },
    ]

    filtered = CodeReviewer._filter_issues_by_changed_lines(
        issues,
        git_diff,
    )

    assert len(filtered) == 2
    assert filtered[0]["line"] == 2
    assert filtered[1]["line"] is None


def test_filter_changed_lines_handles_multiple_hunks():
    git_diff = """diff --git a/app.py b/app.py
index 123..456 100644
--- a/app.py
+++ b/app.py
@@ -1,2 +1,3 @@
 first = 1
+second = 2
 third = 3
@@ -10,2 +11,2 @@
 old = 4
+new = 5
"""

    changed_lines = CodeReviewer._extract_changed_lines(
        git_diff
    )

    assert changed_lines == {
        "app.py": {2, 12}
    }
