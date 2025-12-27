"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="RandomCoffeeBot",
    description="A bot for organizing random coffee meetings",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
)

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint that returns a greeting message."""
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str) -> dict[str, str]:
    """Endpoint to greet a user by name."""
    return {"message": f"Hello {name}"}
