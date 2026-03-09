# ---- Stage 1: Build frontend ----
FROM node:22-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npx vite build

# ---- Stage 2: Runtime ----
FROM python:3.12-slim
LABEL maintainer="RPAclaw" description="RPAclaw — Nanobot + RPA Management Platform"

# System deps for Playwright + RPA
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl gnupg ca-certificates fonts-liberation \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2 libxshmfence1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt pyproject.toml ./
COPY rpaclaw/ rpaclaw/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e . \
    && python -m playwright install chromium \
    && python -m playwright install-deps chromium

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy remaining files
COPY launchers/ launchers/
COPY README.md LICENSE ./

# Config volume (persist nanobot config)
VOLUME ["/root/.nanobot"]

EXPOSE 18790

ENV RPACLAW_HOST=0.0.0.0
ENV RPACLAW_PORT=18790

CMD ["python", "-m", "rpaclaw.main", "start", "--host", "0.0.0.0", "--port", "18790"]
