from app.database.base import Base
from app.database.session import engine
from app.models.repository import Repository
from app.models.code_chunk import CodeChunk

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()