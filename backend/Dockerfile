FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astra-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY backend/ ./backend/

WORKDIR /app/backend
CMD ["fastapi", "run", "app/main.py", "--host", "0,0,0,0", "--port", "8000"]