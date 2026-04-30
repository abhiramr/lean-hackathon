#!/usr/bin/env bash
# scripts/start.sh — One-command startup for Verified EDA
#
# Usage: ./scripts/start.sh
#
# This will:
#   1. Install Python backend dependencies (if needed)
#   2. Install Node.js frontend dependencies (if needed)
#   3. Start the FastAPI backend on :8420
#   4. Start the Vite dev server on :5173
#   5. Open the browser

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "╔══════════════════════════════════════════════════╗"
echo "║      VERIFIED EDA — Starting Application         ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

cd "$ROOT"

# ── Python deps ──
echo "→ Checking Python dependencies..."
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "  Installing backend requirements..."
    pip install -r backend/requirements.txt -q
fi

# Check verified_eda is importable (it should be from the parent project)
if ! python3 -c "import verified_eda" 2>/dev/null; then
    echo "  Installing verified_eda..."
    # Try to install from parent directory if it exists
    if [ -f "../verified-eda/pyproject.toml" ]; then
        pip install -e "../verified-eda" -q
    elif [ -f "../pyproject.toml" ]; then
        pip install -e ".." -q
    else
        echo "  ⚠ verified_eda package not found."
        echo "  Please install it: pip install -e /path/to/verified-eda"
    fi
fi
echo "  ✓ Python ready"

# ── Node deps ──
echo "→ Checking Node.js dependencies..."
if [ ! -d "node_modules" ]; then
    echo "  Installing frontend packages..."
    npm install --silent
fi
echo "  ✓ Node.js ready"

# ── Lean check ──
if command -v lean &>/dev/null || [ -f "$HOME/.elan/bin/lean" ]; then
    echo "→ Lean 4: ✓ Found"
else
    echo "→ Lean 4: Not installed (optional)"
    echo "  Install: curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y"
fi

echo ""
echo "Starting servers..."
echo "  Backend:  http://localhost:8420"
echo "  Frontend: http://localhost:5173"
echo ""

# ── Launch ──
# Start backend in background
python3 backend/server.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8420/api/health > /dev/null 2>&1; then
        echo "  ✓ Backend ready"
        break
    fi
    sleep 0.5
done

# Start frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend
sleep 3

# Open browser
if command -v xdg-open &>/dev/null; then
    xdg-open http://localhost:5173
elif command -v open &>/dev/null; then
    open http://localhost:5173
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Verified EDA is running!"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8420"
echo "  Press Ctrl+C to stop"
echo "═══════════════════════════════════════════════════"

# Trap cleanup
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Wait for either process
wait
