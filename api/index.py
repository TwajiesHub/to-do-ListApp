from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from api.db import engine
from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.include_router(router)
