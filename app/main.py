from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.base import Base
from app.db.engine import engine
import app.db.base_imports

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Welcome to API"}
