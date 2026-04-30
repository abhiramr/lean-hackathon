#!/usr/bin/env bash
# start.sh — One-command start for the full Verified EDA project
#
# Installs everything, starts the FastAPI backend + Vite frontend,
# and opens the browser.
#
# Usage:
#   chmod +x start.sh && ./start.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo ""
echo "  ██╗   ██╗███████╗██████╗ ██╗███████╗██╗███████╗██████╗ "
echo "  ██║   ██║██╔════╝██╔══██╗██║██╔════╝██║██╔════╝██╔══██╗"
echo "  ██║   ██║█████╗  ██████╔╝██║█████╗  ██║█████╗  ██║  ██║"
echo "  ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║██╔══╝  ██║██╔══╝  ██║  ██║"
echo "   ╚████╔╝ ███████╗██║  ██║██║██║     ██║███████╗██████╔╝"
echo "    ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═════╝ "
echo ""
echo "  Formally Verified EDA — Python × Lean 4 × Agentic AI"
echo ""

# ── Python ──
echo "▸ Setting up Python..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

pip install -e "." -q 2>/dev/null || pip install -e "." --break-system-packages -q 2>/dev/null
pip install -r ui/backend/requirements.txt -q 2>/dev/null || pip install -r ui/backend/requirements.txt --break-system-packages -q 2>/dev/null
echo "  ✓ Python packages installed"

# ── Verify import ──
python3 -c "import verified_eda; print(f'  ✓ verified_eda v{verified_eda.__version__} loaded')"

# ── Node.js ──
echo "▸ Setting up frontend..."
cd ui
if [ ! -d "node_modules" ]; then
    npm install --silent 2>/dev/null
fi
echo "  ✓ Node.js packages installed"
cd "$ROOT"

# ── Lean (optional) ──
echo "▸ Checking Lean 4..."
if command -v lean &>/dev/null || [ -f "$HOME/.elan/bin/lean" ]; then
    LEAN_BIN="${HOME}/.elan/bin/lean"
    [ -f "$LEAN_BIN" ] || LEAN_BIN="lean"
    echo "  ✓ Lean 4 found: $($LEAN_BIN --version 2>/dev/null | head -1)"
else
    echo "  ○ Lean 4 not installed (optional)"
    echo "    Install: curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y"
fi

# ── Tests (quick) ──
echo "▸ Running quick test suite..."
cd "$ROOT"
python3 -m pytest tests/ -q --tb=line 2>/dev/null && echo "  ✓ All tests passed" || echo "  ⚠ Some tests failed (non-blocking)"

# ── Launch ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Starting servers..."
echo "  Backend:  http://localhost:8420"
echo "  Frontend: http://localhost:5173"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start backend
cd "$ROOT"
source .venv/bin/activate
python3 ui/backend/server.py &
BACKEND_PID=$!

# Wait for backend
for i in $(seq 1 30); do
    if curl -s http://localhost:8420/api/health > /dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# Start frontend
cd "$ROOT/ui"
npx vite --host &
FRONTEND_PID=$!

sleep 3

# Open browser
if command -v xdg-open &>/dev/null; then
    xdg-open http://localhost:5173 2>/dev/null
elif command -v open &>/dev/null; then
    open http://localhost:5173
fi

echo ""
echo "  ✓ Verified EDA is live at http://localhost:5173"
echo "  Press Ctrl+C to stop"
echo ""

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM
wait
