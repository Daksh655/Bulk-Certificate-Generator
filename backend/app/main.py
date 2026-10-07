from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  Registers models on Base.metadata.
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

from app.api import jobs_router
app.include_router(jobs_router)

@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }