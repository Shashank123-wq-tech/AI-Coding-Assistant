import ast
from pathlib import Path


class FailureLocalizer:
    """
    Resolve a failing test into the source file that should
    potentially be modified.

    The localizer uses Python imports and the failing test file.
    It never guesses when multiple candidates are possible.
    """

    def __init__(self, repository_path: str):
        self.repository_root = Path(
            repository_path
        ).resolve()

    def _safe_path(self, file_path: str) -> Path:
        path = (
            self.repository_root / file_path
        ).resolve()

        try:
            path.relative_to(
                self.repository_root
            )
        except ValueError:
            raise PermissionError(
                "File is outside the repository."
            )

        return path

    def _module_to_file(
        self,
        module_name: str,
    ) -> list[str]:
        """
        Resolve a Python module name to repository source files.

        Supports both:
            repository-root layouts
            src/ layouts

        Examples:
            calculator
            -> calculator.py

            calculator.operations
            -> calculator/operations.py

            calculator.operations
            -> src/calculator/operations.py
        """

        module_parts = module_name.split(".")

        candidates = []

        # Search locations where Python source code commonly lives.
        search_roots = [
            self.repository_root,
            self.repository_root / "src",
        ]

        for search_root in search_roots:

            # module.py
            module_file = (
                search_root
                / Path(*module_parts)
            ).with_suffix(".py")

            if module_file.is_file():
                relative_path = str(
                    module_file.relative_to(
                        self.repository_root
                    )
                )

                if relative_path not in candidates:
                    candidates.append(relative_path)

            # package/__init__.py
            package_init = (
                search_root
                / Path(*module_parts)
                / "__init__.py"
            )

            if package_init.is_file():
                relative_path = str(
                    package_init.relative_to(
                        self.repository_root
                    )
                )

                if relative_path not in candidates:
                    candidates.append(relative_path)

        return candidates
    
    def _resolve_symbol_from_package(
        self,
        package_file: str,
        symbol: str,
    ) -> list[str]:
        """
        Resolve a symbol re-exported by a package __init__.py.

        Example:

            calculator/__init__.py:
                from .operations import add

        Resolves:

            add -> calculator/operations.py
        """

        path = self._safe_path(package_file)

        try:
            source = path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            return []

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        results = []

        for node in tree.body:

            if not isinstance(node, ast.ImportFrom):
                continue

            if node.level < 1:
                continue

            for alias in node.names:

                if alias.name != symbol:
                    continue

                if not node.module:
                    continue

                package_directory = path.parent

                module_parts = node.module.split(".")

                target = (
                    package_directory
                    / Path(*module_parts)
                ).with_suffix(".py")

                if target.is_file():
                    relative_path = str(
                        target.relative_to(
                            self.repository_root
                        )
                    )

                    if relative_path not in results:
                        results.append(
                            relative_path
                        )

                package_target = (
                    package_directory
                    / Path(*module_parts)
                    / "__init__.py"
                )

                if package_target.is_file():
                    relative_path = str(
                        package_target.relative_to(
                            self.repository_root
                        )
                    )

                    if relative_path not in results:
                        results.append(
                            relative_path
                        )

        return results

    def _imports_from_test(
        self,
        test_file: str,
    ) -> list[dict[str, str | None]]:
        """
        Extract Python imports from a test file.

        Returns structured import information so the localizer
        can reason about imported symbols as well as modules.

        Examples:

            from calculator import add

        becomes:

            {
                "module": "calculator",
                "symbol": "add",
            }

            import calculator.operations

        becomes:

            {
                "module": "calculator.operations",
                "symbol": None,
            }
        """

        path = self._safe_path(test_file)

        try:
            source = path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            return []

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for alias in node.names:
                    imports.append(
                        {
                            "module": alias.name,
                            "symbol": None,
                        }
                    )

            elif isinstance(node, ast.ImportFrom):

                if node.module:

                    for alias in node.names:

                        if alias.name == "*":
                            symbol = None
                        else:
                            symbol = alias.name

                        imports.append(
                            {
                                "module": node.module,
                                "symbol": symbol,
                            }
                        )

        return imports

    def localize(
        self,
        test_file: str | None,
    ) -> dict:
        """
        Determine a source file from a failing test file.
        """

        if not test_file:
            return {
                "localized": False,
                "reason": (
                    "No failing test file was identified."
                ),
                "source_files": [],
            }

        imports = self._imports_from_test(
            test_file
        )

        source_files = []

        for import_info in imports:

            module = import_info["module"]
            symbol = import_info["symbol"]

            if not module:
                continue

            candidates = self._module_to_file(
                module
            )

            # If a symbol was imported from a package,
            # inspect __init__.py for a re-export.
            if symbol:
                expanded_candidates = []

                for candidate in candidates:

                    if not candidate.endswith(
                        "__init__.py"
                    ):
                        continue

                    resolved = (
                        self._resolve_symbol_from_package(
                            candidate,
                            symbol,
                        )
                    )

                    for resolved_file in resolved:

                        if resolved_file not in expanded_candidates:
                            expanded_candidates.append(
                                resolved_file
                            )

                if expanded_candidates:
                    candidates = expanded_candidates

            for candidate in candidates:

                if candidate not in source_files:
                    source_files.append(
                        candidate
                    )
        
        # Remove the test file itself.
        source_files = [
            path
            for path in source_files
            if Path(path).as_posix()
            != Path(test_file).as_posix()
        ]

        if len(source_files) == 1:
            return {
                "localized": True,
                "source_file": source_files[0],
                "source_files": source_files,
                "reason": (
                    "Unique source file resolved "
                    "from failing test imports."
                ),
            }

        if len(source_files) == 0:
            return {
                "localized": False,
                "source_file": None,
                "source_files": [],
                "reason": (
                    "No source file could be resolved "
                    "from the failing test imports."
                ),
            }

        return {
            "localized": False,
            "source_file": None,
            "source_files": source_files,
            "reason": (
                "Multiple possible source files were "
                "found; automatic repair will not guess."
            ),
        }