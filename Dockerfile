# ---- Stage 1: build the React frontend ----
FROM node:20-alpine AS frontend
WORKDIR /build
COPY contract-risk-analyzer/package.json contract-risk-analyzer/package-lock.json ./
RUN npm ci
COPY contract-risk-analyzer/ ./
RUN npm run build

# ---- Stage 2: FastAPI backend that also serves the built UI ----
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TASK_MODE=inline \
    FRONTEND_DIST_DIR=/app/frontend-dist \
    MAX_AGENT_CONCURRENCY=1
WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir --default-timeout=120 --retries 5 -r backend/requirements.txt

COPY backend/app backend/app
COPY ["MSME BENCHMARK LIB", "MSME BENCHMARK LIB"]
COPY --from=frontend /build/dist /app/frontend-dist

WORKDIR /app/backend
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
