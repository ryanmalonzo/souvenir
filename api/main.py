from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlmodel import SQLModel

from dependencies import engine
from routers import auth


@asynccontextmanager
async def lifespan(_):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
