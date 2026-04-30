# Verified EDA — UI Application

**Mission Control dashboard for formally verified exploratory data analysis.**

A full-stack application with a React + Vite frontend and a FastAPI backend that connects to your local Python `verified_eda` library and Lean 4 installation.

---

## One-Command Start

```bash
# macOS / Linux
chmod +x scripts/start.sh
./scripts/start.sh

# Windows
scripts\start.bat
```

This installs all dependencies, starts both servers, and opens the browser.

---

## Manual Setup

### Prerequisites

| Tool | Version | Required? |
|---|---|---|
| Python | ≥ 3.11 | ✅ Yes |
| Node.js | ≥ 18 | ✅ Yes |
| npm | ≥ 9 | ✅ Yes |
| Lean 4 | ≥ 4.8.0 | Optional (for proof type-checking) |

### Step 1: Install the `verified_eda` Python package

The backend depends on the `verified_eda` library. Install it from the main project:

```bash
# If you have the verified-eda project directory:
pip install -e /path/to/verified-eda

# Or install just the backend deps:
pip install -r backend/requirements.txt
```

### Step 2: Install frontend dependencies

```bash
npm install
```

### Step 3: Start the backend (Terminal 1)

```bash
python backend/server.py
# → Runs on http://localhost:8420
```

### Step 4: Start the frontend (Terminal 2)

```bash
npm run dev
# → Runs on http://localhost:5173
```

### Step 5: Open the browser

Go to **http://localhost:5173**

---

## Features

### Analysis Tab
- Switch between sample datasets (Sales, Sensor, Patient) or upload your own CSV
- Per-column stats: mean, std, median, variance with animated stat cards
- Interactive box-plot style range visualization
- Histogram with Recharts
- Correlation heatmap matrix
- Sortable summary table

### Proofs Tab
- Full Lean 4 definition source with syntax highlighting
- Key proof source display
- After verification: list of all certificates with SHA-256 hashes, theorem names, and proof status

### Agents Tab
- Real-time streaming agent activity log (via WebSocket)
- Agent status cards showing Translator, Prover, Certifier, Orchestrator
- Architecture diagram (SVG)

### Lean 4 Tab
- Auto-detects local Lean 4 installation
- Shows version, path, Lake availability, project status
- **Build & Type-Check button** — runs `lake build` on the Lean project directly from the UI
- Displays build output (success/failure with error messages)
- Lists all theorems with proven/sorry status

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Backend + Lean status |
| GET | `/api/lean/status` | Detailed Lean 4 environment info |
| GET | `/api/datasets` | List available sample datasets |
| GET | `/api/datasets/{name}` | Get a specific dataset |
| POST | `/api/eda/run` | Run full EDA pipeline |
| POST | `/api/verify` | Run agentic verification |
| WS | `/ws/verify` | Streaming verification with real-time logs |
| POST | `/api/lean/check` | Type-check arbitrary Lean code |
| POST | `/api/lean/build` | Run `lake build` on the Lean project |
| POST | `/api/upload/csv` | Upload and parse a CSV file |
| GET | `/api/theorems` | List all proof templates |

---

## Architecture

```
┌─────────────────────────────────┐
│         Browser (React)          │
│  Vite dev server :5173           │
│  ┌───────────────────────────┐  │
│  │ Analysis │ Proofs │ Agents │  │
│  │ Lean 4   │        │       │  │
│  └───────────┬───────────────┘  │
└──────────────┼──────────────────┘
               │ HTTP / WebSocket (proxied)
               ▼
┌──────────────────────────────────┐
│     FastAPI Backend :8420         │
│  ┌────────────┐ ┌─────────────┐ │
│  │ verified_eda│ │ Lean 4 CLI  │ │
│  │ (Python)   │ │ (subprocess)│ │
│  └────────────┘ └─────────────┘ │
└──────────────────────────────────┘
```

---

## Project Structure

```
verified-eda-app/
├── backend/
│   ├── server.py              # FastAPI server
│   └── requirements.txt       # Python dependencies
├── src/
│   ├── main.jsx               # React entry point
│   ├── App.jsx                # Main dashboard component
│   ├── lib/
│   │   └── api.js             # API client library
│   └── styles/
│       └── globals.css        # Tailwind + custom styles
├── scripts/
│   ├── start.sh               # One-command start (Unix)
│   └── start.bat              # One-command start (Windows)
├── index.html                 # HTML entry
├── package.json               # Node dependencies + scripts
├── vite.config.js             # Vite configuration (proxy)
├── tailwind.config.js         # Tailwind CSS config
├── postcss.config.js          # PostCSS config
└── README.md                  # This file
```

---

## npm Scripts

| Script | Command | Description |
|---|---|---|
| `npm run dev` | `vite` | Start frontend dev server |
| `npm run build` | `vite build` | Build for production |
| `npm run server` | `python backend/server.py` | Start backend only |
| `npm start` | concurrent backend + frontend | Start both servers |

---

## License

MIT
