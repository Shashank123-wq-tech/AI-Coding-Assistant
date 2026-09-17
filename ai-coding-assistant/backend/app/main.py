from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.repositories import router as repository_router
from app.api.routes.tests import router as tests_router


app = FastAPI(
    title="AI Coding Assistant",
    version="0.1.0",
    debug=True,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix="/api",
)

app.include_router(
    repository_router,
    prefix="/api",
)

app.include_router(
    tests_router,
    prefix="/api",
)


@app.get("/")
def root():
    return {
        "name": "AI Coding Assistant",
        "status": "running",
    }