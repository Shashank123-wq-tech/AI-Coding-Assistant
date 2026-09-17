from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    repository_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    chunk_id: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        unique=True,
        index=True,
    )

    file_path: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
        index=True,
    )

    chunk_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    cell_index: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # "metadata" is reserved by SQLAlchemy,
    # so the Python attribute is named chunk_metadata.
    # The actual database column remains "metadata".
    chunk_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )