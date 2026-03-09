FROM docker.1ms.run/python:3.12-slim
LABEL maintainer="RPAclaw" description="RPAclaw — Nanobot + RPA Management Platform"

# Use Chinese Debian mirror (USTC)
RUN sed -i 's|deb.debian.org|mirrors.ustc.edu.cn|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null; \
    sed -i 's|deb.debian.org|mirrors.ustc.edu.cn|g' /etc/apt/sources.list 2>/dev/null; \
    true

# China pip mirror
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# System deps for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl ca-certificates fonts-liberation \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt pyproject.toml ./
COPY rpaclaw/ rpaclaw/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e . \
    && python -m playwright install chromium \
    && python -m playwright install-deps chromium 2>/dev/null; true

# Pre-built frontend
COPY frontend/dist /app/frontend/dist

# Copy remaining files
COPY launchers/ launchers/
COPY README.md LICENSE ./

VOLUME ["/root/.nanobot"]
EXPOSE 18790

ENV RPACLAW_HOST=0.0.0.0
ENV RPACLAW_PORT=18790

CMD ["python", "-m", "rpaclaw.main", "start", "--host", "0.0.0.0", "--port", "18790"]
