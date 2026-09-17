import json
from pathlib import Path


class NotebookParser:
    """
    Read-only Jupyter Notebook parser.

    Extracts:
    - notebook metadata
    - code cells
    - markdown cells
    - raw cells
    - cell source
    - cell index
    """

    SUPPORTED_CELL_TYPES = {
        "code",
        "markdown",
        "raw",
    }

    def __init__(self, notebook_path: str | Path):
        self.notebook_path = Path(notebook_path).resolve()

        if not self.notebook_path.exists():
            raise FileNotFoundError(
                f"Notebook does not exist: {self.notebook_path}"
            )

        if not self.notebook_path.is_file():
            raise ValueError(
                f"Notebook path is not a file: {self.notebook_path}"
            )

        if self.notebook_path.suffix.lower() != ".ipynb":
            raise ValueError(
                f"Expected a .ipynb file: {self.notebook_path}"
            )

    def _load_notebook(self) -> dict:
        """
        Load the notebook JSON without modifying the file.
        """

        try:
            with self.notebook_path.open(
                "r",
                encoding="utf-8",
            ) as notebook_file:
                return json.load(notebook_file)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid Jupyter Notebook JSON: "
                f"{self.notebook_path}"
            ) from exc

    @staticmethod
    def _extract_source(source) -> str:
        """
        Normalize a notebook cell's source field.

        Jupyter may store source as either:
        - a list of strings
        - a single string
        """

        if isinstance(source, list):
            return "".join(source)

        if isinstance(source, str):
            return source

        return ""

    def parse(self) -> dict:
        """
        Parse the notebook into structured cell information.
        """

        notebook_data = self._load_notebook()

        raw_cells = notebook_data.get("cells", [])

        cells = []

        for cell_index, raw_cell in enumerate(raw_cells):

            cell_type = raw_cell.get("cell_type")

            if cell_type not in self.SUPPORTED_CELL_TYPES:
                continue

            source = self._extract_source(
                raw_cell.get("source", "")
            )

            cell_data = {
                "cell_index": cell_index,
                "cell_type": cell_type,
                "source": source,
            }

            if cell_type == "code":
                cell_data["execution_count"] = raw_cell.get(
                    "execution_count"
                )

                cell_data["outputs_count"] = len(
                    raw_cell.get("outputs", [])
                )

            cells.append(cell_data)

        code_cells = [
            cell
            for cell in cells
            if cell["cell_type"] == "code"
        ]

        markdown_cells = [
            cell
            for cell in cells
            if cell["cell_type"] == "markdown"
        ]

        raw_cells_data = [
            cell
            for cell in cells
            if cell["cell_type"] == "raw"
        ]

        return {
            "notebook": self.notebook_path.name,
            "notebook_path": str(self.notebook_path),
            "total_cells": len(cells),
            "code_cells": len(code_cells),
            "markdown_cells": len(markdown_cells),
            "raw_cells": len(raw_cells_data),
            "cells": cells,
        }