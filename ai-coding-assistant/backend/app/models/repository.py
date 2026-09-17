from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base

class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        unique=True
    )

    local_path: Mapped[str] = mapped_column(
        String(2000),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="cloned"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )