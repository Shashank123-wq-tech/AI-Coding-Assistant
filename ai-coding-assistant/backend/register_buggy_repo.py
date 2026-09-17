from app.database.session import SessionLocal
from app.models.repository import Repository

db = SessionLocal()

try:
    repository = Repository(
        name="python-buggy",
        url="local://python-buggy",
        local_path=r"C:\AI Coding Assistant\AI-Coding-Assistant\ai-coding-assistant\test-repositories\python-buggy",
        status="cloned",
    )

    db.add(repository)
    db.commit()
    db.refresh(repository)

    print("REPOSITORY ID:", repository.id)
    print("NAME:", repository.name)
    print("PATH:", repository.local_path)

finally:
    db.close()
