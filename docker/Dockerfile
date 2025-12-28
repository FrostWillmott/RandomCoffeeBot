# ==============================================================================
# Stage 1: Base image with uv
# ==============================================================================
FROM python:3.12-slim-bookworm AS base

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    # uv configuration
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12

# Install uv (pinned version for reproducible builds)
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# ==============================================================================
# Stage 2: Dependencies builder
# ==============================================================================
FROM base AS builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev dependencies for production)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ==============================================================================
# Stage 3: Development image
# ==============================================================================
FROM base AS development

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy dependency files for dev dependencies
COPY pyproject.toml uv.lock ./

# Install all dependencies including dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Default command for development
CMD ["python", "-m", "app.main"]

# ==============================================================================
# Stage 4: Production image
# ==============================================================================
FROM base AS production

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini ./
COPY --chown=appuser:appgroup docker/healthcheck.py ./

# Switch to non-root user
USER appuser

# Default command for production
CMD ["python", "-m", "app.main"]
