#!/bin/bash
# RPAclaw Launcher — macOS / Linux
set -e

echo "🤖 RPAclaw — Starting..."

# Detect Python
if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null; then
    PY=python
else
    echo "❌ Python 3.11+ not found. Install from https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PY_VER=$($PY -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "   Python: $PY ($PY_VER)"

# Get project directory
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "   Project: $SCRIPT_DIR"

# Install / upgrade RPAclaw
echo "📦 Installing dependencies..."
$PY -m pip install -e "$SCRIPT_DIR" --quiet 2>/dev/null || $PY -m pip install -e "$SCRIPT_DIR"

# Install Playwright browser (for RPA)
echo "🌐 Checking Playwright browser..."
$PY -m playwright install chromium 2>/dev/null || echo "   (skip: playwright not needed or already installed)"

# Build frontend if needed
if [ ! -d "$SCRIPT_DIR/frontend/dist" ]; then
    echo "🔨 Building frontend..."
    if command -v npm &>/dev/null; then
        (cd "$SCRIPT_DIR/frontend" && npm install && npx vite build)
    else
        echo "   ⚠️  npm not found — frontend build skipped. Install Node.js >= 18"
    fi
fi

# Start server
HOST=${RPACLAW_HOST:-127.0.0.1}
PORT=${RPACLAW_PORT:-18790}

echo ""
echo "🚀 RPAclaw running at http://$HOST:$PORT"
echo "   Press Ctrl+C to stop"
echo ""

# Auto-open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://$HOST:$PORT" &
elif command -v xdg-open &>/dev/null; then
    xdg-open "http://$HOST:$PORT" &
fi

$PY -m rpaclaw.main start --host "$HOST" --port "$PORT"
