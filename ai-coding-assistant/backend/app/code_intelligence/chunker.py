from dataclasses import dataclass


@dataclass
class CodeChunk:

    file_path: str

    content: str

    start_line: int

    end_line: int

    symbol: str | None = None

    language: str = "python"


class CodeChunker:


    def chunk_file(
        self,
        file_path: str,
        content: str,
        chunk_size: int = 80,
    ):

        lines = content.splitlines()

        chunks = []

        for start in range(
            0,
            len(lines),
            chunk_size,
        ):

            end = min(
                start + chunk_size,
                len(lines),
            )

            chunks.append(
                CodeChunk(
                    file_path=file_path,
                    content="\n".join(
                        lines[start:end]
                    ),
                    start_line=start + 1,
                    end_line=end,
                )
            )

        return chunks
