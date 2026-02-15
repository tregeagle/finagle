# Stage 1: Build frontend
FROM node:22-slim AS frontend-build
WORKDIR /build

ARG VITE_API_KEY
ARG VITE_API_URL=/api/v1

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# Stage 2: Backend + serve frontend
FROM python:3.12-slim AS backend
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./
COPY alembic/ alembic/
COPY templates/ templates/
COPY app/ app/

COPY --from=frontend-build /build/dist frontend/dist

EXPOSE 8000

CMD uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
