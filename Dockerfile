FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md .env ./
COPY src ./src

RUN uv sync --locked --no-dev

COPY alembic.ini ./

FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/alembic.ini /app/
COPY --from=builder /app/.env /app/

CMD ["sh", "-c", "/app/.venv/bin/alembic upgrade head && /app/.venv/bin/python -m felixbot"]