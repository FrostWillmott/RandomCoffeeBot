"""Main module for the FastAPI application."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint that returns a greeting message."""
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    """Endpoint to greet a user by name."""
    return {"message": f"Hello {name}"}
