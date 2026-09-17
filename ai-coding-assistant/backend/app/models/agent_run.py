from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from backend.app.database.base import Base


class AgentRun(Base):

    __tablename__ = "agent_runs"


    id: Mapped[int] = mapped_column(
        primary_key=True
    )


    repository_id: Mapped[int] = mapped_column()


    request: Mapped[str] = mapped_column(
        Text
    )


    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
