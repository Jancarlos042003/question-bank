from fastapi import FastAPI

from app.api.v1.router import api_v1_router
from app.core.exceptions.handlers import register_exception_handlers
from app.core.logging_config import setup_logging
from app.core.middleware import register_middleware
from app.core.openapi import FASTAPI_METADATA
from app.db import base_imports  # noqa: F401

app = FastAPI(**FASTAPI_METADATA)

setup_logging()
register_middleware(app)
register_exception_handlers(app)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["Welcome"])
def root():
    return {"message": "Welcome to API"}
