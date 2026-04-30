# Verified EDA

**Formally Verified Exploratory Data Analysis — Python × Lean 4 × Agentic AI**

A complete system that performs EDA in Python, mirrors every operation in Lean 4 with machine-checked proofs, and orchestrates the verification pipeline with agentic AI — plus a mission-control dashboard UI.

---

## Quick Start (one command)

**Windows (PowerShell or CMD):**
```
.\start.bat
```

**macOS / Linux:**
```bash
chmod +x start.sh && ./start.sh
```

This creates a venv, installs everything, runs tests, starts both servers, and opens the dashboard at http://localhost:5173.

### Manual Setup

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pip install -r ui\backend\requirements.txt

# Tests
pytest

# CLI example
python examples\example_usage.py

# UI — run each in a separate terminal
cd ui; npm install; cd ..
python ui\backend\server.py          # Terminal 1
cd ui; npx vite --host               # Terminal 2
# Open http://localhost:5173
```

**macOS / Linux:**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pip install -r ui/backend/requirements.txt
pytest
python ui/backend/server.py    # Terminal 1
cd ui && npm install && npm run dev   # Terminal 2
```

### Lean 4 (optional)

```bash
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
cd lean && lake build
```

---

## What's Inside

**Core Library** (`verified_eda/`) — mean, variance, std, median, Pearson correlation, histograms, all returning `VerifiedResult` with Lean theorem references.

**Agentic Agents** (`verified_eda/agents/`) — Translator (Python→Lean), Prover (tactic search + LLM), Certifier (SHA-256), Orchestrator (coordinates all).

**Lean 4 Proofs** (`lean/VerifiedEDA/`) — `variance_nonneg`, `sqDiff_nonneg`, `listSum_nonneg`, `innerProd_self_nonneg`, plus open goals for Cauchy-Schwarz and histogram conservation.

**Dashboard UI** (`ui/`) — React + Vite frontend, FastAPI backend. Analysis/Proofs/Agents/Lean tabs with real-time WebSocket streaming, one-click `lake build`, CSV upload, correlation heatmaps.

**CI** (`.github/workflows/ci.yml`) — Python tests on 3 versions × 2 OS, 2500 random property checks, Lean type-checking.

---

## Project Structure

```
├── verified_eda/          # Python library
├── lean/                  # Lean 4 proofs
├── ui/                    # Dashboard (React + FastAPI)
│   ├── backend/server.py
│   ├── src/App.jsx
│   └── package.json
├── tests/                 # 49 tests
├── examples/              # CLI demo
├── .github/workflows/     # CI
├── start.sh               # One-command start (macOS/Linux)
├── start.bat              # One-command start (Windows)
└── pyproject.toml
```

MIT License.
