# ─── Build Stage: Frontend ──────────────────────────────────────────────────
FROM node:22-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ─── Production Stage: Backend ──────────────────────────────────────────────
FROM python:3.12-slim AS production

# System deps for OCR and PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install Python dependencies
COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --no-dev --no-editable

# Copy backend source
COPY backend/ ./

# Copy built frontend into backend static directory
COPY --from=frontend-build /app/frontend/dist/ ./app/static/

# Expose the application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Run the application
CMD ["uv", "run", "python", "-m", "app.main"]
