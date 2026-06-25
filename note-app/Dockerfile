FROM ghcr.io/astral-sh/uv:0.11.24-python3.14-trixie-slim AS builder

WORKDIR /app
COPY pyproject.toml .
RUN uv pip install --system --no-cache .

FROM docker.io/library/python:3.14-trixie

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
