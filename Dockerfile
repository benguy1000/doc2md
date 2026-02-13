# Stage 1: Build
FROM python:3.11-slim AS build

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
COPY src/ src/

RUN uv pip install --system --no-cache .

# Stage 2: Production
FROM python:3.11-slim

WORKDIR /data

COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /app/src /app/src

ENV PYTHONPATH=/app/src
ENV TRANSPORT=stdio
ENV PORT=3000
ENV DEFAULT_OUTPUT_DIR=/data/output

ENTRYPOINT ["python", "-m", "doc2md"]
