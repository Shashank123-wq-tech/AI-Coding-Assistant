import json
import re
from typing import Any

from app.llm.groq_provider import GroqProvider


class CodeReviewer:
    """
    LLM-powered code reviewer.

    The reviewer analyzes an already-generated Git diff.
    It never modifies repository files.
    """

    def __init__(self):
        self.llm_provider = GroqProvider()

    @staticmethod
    def _build_prompt(git_diff: str) -> str:
        return f"""
You are a senior software engineer performing a code review.

Review ONLY the Git diff provided below.

Your job is to identify concrete problems introduced by the changes.

Focus on:
- correctness bugs
- security vulnerabilities
- performance problems
- maintainability problems
- incorrect or fragile behavior

Do not report issues merely because you dislike a coding style.

IMPORTANT RULES:
1. Review only the changes shown in the diff.
2. Do not invent files, functions, APIs, requirements, or behavior.
3. Do not modify the code.
4. Do not suggest unrelated improvements.
5. Every issue must have concrete evidence in the diff.
6. If there are no meaningful issues, return an empty issues list.
7. Return ONLY valid JSON.
8. Do not use Markdown code fences.

The JSON must have exactly this structure:

{{
    "summary": "Short overall summary of the changes.",
    "issues": [
        {{
            "severity": "critical|high|medium|low",
            "category": "bug|security|performance|maintainability|correctness",
            "file": "path/to/file.py",
            "line": 10,
            "message": "Concrete explanation of the issue.",
            "suggestion": "Specific suggested improvement."
        }}
    ]
}}

For issues where an exact line cannot be determined, use null for "line".

GIT DIFF:
{git_diff}
""".strip()

    @staticmethod
    def _extract_changed_files(git_diff: str) -> set[str]:
        """
        Extract changed file paths from standard Git diff headers.

        Only files explicitly represented by a `diff --git` header
        are considered part of the review scope.
        """
        changed_files: set[str] = set()

        for line in git_diff.splitlines():
            if not line.startswith("diff --git "):
                continue

            match = re.match(
                r"diff --git a/(.+?) b/(.+)$",
                line,
            )

            if not match:
                continue

            old_path, new_path = match.groups()

            if old_path != "/dev/null":
                changed_files.add(old_path)

            if new_path != "/dev/null":
                changed_files.add(new_path)

        return changed_files
    
    @staticmethod
    def _extract_changed_lines(
        git_diff: str,
    ) -> dict[str, set[int]]:
        """
        Extract added/changed line numbers for each file
        from a unified Git diff.

        Only added lines are considered reviewable locations.
        """
        changed_lines: dict[str, set[int]] = {}

        current_file: str | None = None
        current_new_line: int | None = None

        for line in git_diff.splitlines():
            if line.startswith("diff --git "):
                match = re.match(
                    r"diff --git a/(.+?) b/(.+)$",
                    line,
                )

                if match:
                    _, new_path = match.groups()
                    current_file = new_path
                    changed_lines.setdefault(
                        current_file,
                        set(),
                    )

                current_new_line = None
                continue

            if not current_file:
                continue

            if line.startswith("@@"):
                match = re.search(
                    r"\+(\d+)(?:,(\d+))?",
                    line,
                )

                if match:
                    current_new_line = int(
                        match.group(1)
                    )

                continue

            if current_new_line is None:
                continue

            if line.startswith("+") and not line.startswith("+++"):
                changed_lines[current_file].add(
                    current_new_line
                )
                current_new_line += 1

            elif line.startswith("-") and not line.startswith("---"):
                # Deleted lines do not advance the new-file line.
                continue

            else:
                # Context line.
                current_new_line += 1

        return changed_lines

    @classmethod
    def _filter_issues_by_changed_lines(
        cls,
        issues: list[dict[str, Any]],
        git_diff: str,
    ) -> list[dict[str, Any]]:
        """
        Keep issues whose reported line is either:
        - null, or
        - an actual added/changed line in the diff.
        """
        changed_lines = cls._extract_changed_lines(
            git_diff
        )

        filtered = []

        for issue in issues:
            issue_file = issue.get("file")

            if not isinstance(issue_file, str):
                continue

            normalized_file = issue_file.replace(
                "\\",
                "/",
            )

            normalized_changed_lines = {}

            for path, lines in changed_lines.items():
                normalized_changed_lines[
                    path.replace("\\", "/")
                ] = lines

            if normalized_file not in normalized_changed_lines:
                continue

            issue_line = issue.get("line")

            if issue_line is None:
                filtered.append(issue)
                continue

            if issue_line in normalized_changed_lines[
                normalized_file
            ]:
                filtered.append(issue)

        return filtered

    @classmethod
    def _filter_issues_by_diff_scope(
        cls,
        issues: list[dict[str, Any]],
        git_diff: str,
    ) -> list[dict[str, Any]]:
        """
        Keep only issues referring to files present in the Git diff.
        """
        changed_files = cls._extract_changed_files(git_diff)

        if not changed_files:
            return []

        filtered = []

        for issue in issues:
            issue_file = issue.get("file")

            if not isinstance(issue_file, str):
                continue

            normalized_file = issue_file.replace("\\", "/")

            normalized_changed_files = {
                path.replace("\\", "/")
                for path in changed_files
            }

            if normalized_file in normalized_changed_files:
                filtered.append(issue)

        return filtered

    @staticmethod
    def _validate_issue(issue: Any) -> dict[str, Any] | None:
        if not isinstance(issue, dict):
            return None

        severity = issue.get("severity")
        category = issue.get("category")
        file_path = issue.get("file")
        line = issue.get("line")
        message = issue.get("message")
        suggestion = issue.get("suggestion")

        valid_severities = {
            "critical",
            "high",
            "medium",
            "low",
        }

        valid_categories = {
            "bug",
            "security",
            "performance",
            "maintainability",
            "correctness",
        }

        if severity not in valid_severities:
            return None

        if category not in valid_categories:
            return None

        if not isinstance(file_path, str) or not file_path.strip():
            return None

        if line is not None and (
            not isinstance(line, int)
            or line < 1
        ):
            line = None

        if not isinstance(message, str) or not message.strip():
            return None

        if suggestion is not None and not isinstance(
            suggestion,
            str,
        ):
            suggestion = None

        return {
            "severity": severity,
            "category": category,
            "file": file_path.strip(),
            "line": line,
            "message": message.strip(),
            "suggestion": (
                suggestion.strip()
                if isinstance(suggestion, str)
                else None
            ),
        }

    @classmethod
    def _parse_response(
        cls,
        response: str,
    ) -> dict[str, Any]:
        if not response or not response.strip():
            raise ValueError(
                "LLM returned an empty review response."
            )

        try:
            parsed = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON."
            ) from exc

        if not isinstance(parsed, dict):
            raise ValueError(
                "LLM review response must be a JSON object."
            )

        summary = parsed.get("summary")

        if not isinstance(summary, str):
            summary = "Automated code review completed."

        raw_issues = parsed.get("issues", [])

        if not isinstance(raw_issues, list):
            raw_issues = []

        issues = []

        for raw_issue in raw_issues:
            issue = cls._validate_issue(raw_issue)

            if issue is not None:
                issues.append(issue)

        return {
            "summary": summary.strip(),
            "issues": issues,
        }

    def review(
        self,
        git_diff: str,
    ) -> dict[str, Any]:
        """
        Review a Git diff using the configured LLM.

        This method is read-only and never modifies repository files.
        """
        if not git_diff or not git_diff.strip():
            return {
                "summary": "No changes to review.",
                "issues": [],
                "diff_size": 0,
            }

        prompt = self._build_prompt(git_diff)

        response = self.llm_provider.generate(prompt)

        parsed = self._parse_response(response)

        parsed["issues"] = self._filter_issues_by_diff_scope(
            parsed["issues"],
            git_diff,
        )
        
        parsed["issues"] = self._filter_issues_by_changed_lines(
            parsed["issues"],
            git_diff,
        )

        return {
            **parsed,
            "diff_size": len(git_diff),
        }