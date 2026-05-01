# Verified EDA

**Verified EDA: Formally Verified Exploratory Data Analysis (Python × Lean 4 × Agentic AI)**

### Abstract: 
Verified EDA is a critical software system designed to eliminate the fundamental "Trust Gap" in Exploratory Data Analysis (EDA) by introducing formal mathematical verification. Traditional EDA workflows using Python libraries like Pandas and NumPy offer no mathematical guarantee of correctness, which poses a risk in regulated industries.1

This project bridges that gap by mirroring every Python EDA operation in Lean 4, a dependently-typed proof assistant, to formally prove theorems that certify the correctness of each analytical step. It presents a complete system that performs EDA in Python, mirrors every operation in Lean 4 with machine-checked proofs, and orchestrates the verification pipeline with agentic AI — plus a mission-control dashboard UI.


## Origin
This project was built during the **LeanLang for Verified
Autonomy Hackathon** (April 17–18 + online through May 1,
2026) at the **Indian Institute of Science (IISc),
Bangalore**.
Sponsored by **[Emergence AI](https://www.emergence.ai)**
Organized by **[Emergence India Labs]
(https://east.emergence.ai)** in collaboration with
**IISc Bangalore**.

---

## Accompanying design doc 
- [https://docs.google.com/document/d/1MVSsc2X11gWjFLgrFlAk7GfpBBxjhypHZMajD1NogtM/edit?usp=sharing](https://docs.google.com/document/d/1MVSsc2X11gWjFLgrFlAk7GfpBBxjhypHZMajD1NogtM/edit?usp=sharing)

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

# Terminal 1 — Backend (FastAPI on port 8420)
cd ui\backend
uvicorn server:app --reload --port 8420

# Terminal 2 — Frontend (React + Vite)
cd ui; npx vite --host
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

[MIT License](https://github.com/abhiramr/lean-hackathon/blob/main/LeanMowers/LICENSE)

---

## Acknowledgments
This project was made possible by:
- **Emergence AI** — Hackathon sponsor
- **Emergence India Labs** — Event organizer and
research direction
- **Indian Institute of Science (IISc), Bangalore** —
Academic partner, hackathon co-design, tutorials,
and mentorship

## Links
- [Hackathon Page](https://east.emergence.ai/
hackathon-april2026.html)
- [Emergence India Labs](https://east.emergence.ai)
- [Emergence AI](https://www.emergence.ai)
