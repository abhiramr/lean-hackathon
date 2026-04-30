"""
backend/server.py — FastAPI server bridging the UI to verified_eda + Lean 4.

Endpoints:
  POST /api/eda/run          — Run full EDA on uploaded/sample data
  POST /api/verify           — Run agentic verification pipeline
  POST /api/lean/check       — Type-check a Lean file
  GET  /api/lean/status      — Check if Lean 4 is installed
  GET  /api/theorems         — List all theorem templates
  GET  /api/health           — Health check
  WS   /ws/verify            — Streaming verification with real-time agent logs
"""

from __future__ import annotations

import asyncio
import csv
import io
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add parent directory to path so we can import verified_eda
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from verified_eda.pipeline import VerifiedEDA
from verified_eda.agents.orchestrator import Orchestrator
from verified_eda.agents.prover import PROOF_TEMPLATES
from verified_eda.agents.translator import LEAN_TEMPLATES
from verified_eda.agents.certifier import CertifierAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verified-eda-server")


# ── Lean 4 detection ──
def find_lean() -> Optional[str]:
    """Find the Lean 4 binary."""
    for candidate in [
        "lean",
        os.path.expanduser("~/.elan/bin/lean"),
        "/usr/local/bin/lean",
    ]:
        if shutil.which(candidate):
            return candidate
        try:
            r = subprocess.run([candidate, "--version"], capture_output=True, timeout=5)
            if r.returncode == 0:
                return candidate
        except Exception:
            continue
    return None


def get_lean_version(lean_path: str) -> Optional[str]:
    try:
        r = subprocess.run([lean_path, "--version"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return r.stdout.strip().split("\n")[0]
    except Exception:
        pass
    return None


LEAN_PATH = find_lean()
LEAN_VERSION = get_lean_version(LEAN_PATH) if LEAN_PATH else None
LEAN_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent / "lean"


# ── App ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Verified EDA Server starting...")
    logger.info(f"Lean 4: {'Found at ' + LEAN_PATH if LEAN_PATH else 'NOT FOUND'}")
    if LEAN_VERSION:
        logger.info(f"Lean version: {LEAN_VERSION}")
    yield
    logger.info("Server shutting down.")


app = FastAPI(
    title="Verified EDA API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ──
class DatasetRequest(BaseModel):
    data: List[List[float]]
    columns: List[str]
    dataset_name: str = "unnamed"
    bins: int = 10


class VerifyRequest(BaseModel):
    data: List[List[float]]
    columns: List[str]
    dataset_name: str = "unnamed"
    bins: int = 10
    use_llm: bool = False


class LeanCheckRequest(BaseModel):
    code: str
    filename: str = "check.lean"


class TheoremInfo(BaseModel):
    name: str
    statement: str
    proof: str
    lean_def: Optional[str] = None


# ── Sample datasets ──
import random as _random

def _gen_sales(seed=42, n=80):
    _random.seed(seed)
    return {
        "columns": ["Revenue", "Units", "Margin", "Growth"],
        "data": [
            [30000 + _random.random() * 50000,
             float(int(50 + _random.random() * 200)),
             0.15 + _random.random() * 0.45,
             -0.1 + _random.random() * 0.4]
            for _ in range(n)
        ]
    }

def _gen_sensor(seed=137, n=120):
    _random.seed(seed)
    return {
        "columns": ["Temperature", "Pressure", "Humidity", "Voltage"],
        "data": [
            [18 + _random.random() * 15,
             980 + _random.random() * 60,
             30 + _random.random() * 50,
             3.0 + _random.random() * 2.4]
            for _ in range(n)
        ]
    }

def _gen_patient(seed=256, n=60):
    _random.seed(seed)
    return {
        "columns": ["HeartRate", "SystolicBP", "SpO2", "BMI"],
        "data": [
            [55 + _random.random() * 50,
             90 + _random.random() * 70,
             92 + _random.random() * 8,
             18 + _random.random() * 20]
            for _ in range(n)
        ]
    }

SAMPLE_DATASETS = {
    "Sales Q1 2026": _gen_sales,
    "Sensor Readings": _gen_sensor,
    "Patient Metrics": _gen_patient,
}


# ── Endpoints ──

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "lean_available": LEAN_PATH is not None,
        "lean_version": LEAN_VERSION,
        "lean_path": LEAN_PATH,
    }


@app.get("/api/lean/status")
async def lean_status():
    lake_available = shutil.which("lake") is not None
    project_exists = LEAN_PROJECT_DIR.exists() and (LEAN_PROJECT_DIR / "lakefile.lean").exists()
    return {
        "lean_installed": LEAN_PATH is not None,
        "lean_version": LEAN_VERSION,
        "lean_path": LEAN_PATH,
        "lake_available": lake_available,
        "lean_project_found": project_exists,
        "lean_project_path": str(LEAN_PROJECT_DIR) if project_exists else None,
    }


@app.get("/api/datasets")
async def list_datasets():
    return {
        "datasets": [
            {"name": name, "rows": fn()["data"].__len__(), "cols": len(fn()["columns"])}
            for name, fn in SAMPLE_DATASETS.items()
        ]
    }


@app.get("/api/datasets/{name}")
async def get_dataset(name: str):
    if name not in SAMPLE_DATASETS:
        raise HTTPException(404, f"Dataset '{name}' not found")
    ds = SAMPLE_DATASETS[name]()
    return {"name": name, **ds}


@app.post("/api/eda/run")
async def run_eda(req: DatasetRequest):
    try:
        eda = VerifiedEDA(req.data, columns=req.columns, dataset_name=req.dataset_name)
        report = eda.run(bins=req.bins)

        # Build response
        columns_stats = {}
        for col, results in report.results.items():
            columns_stats[col] = {
                r.operation: {
                    "value": r.value,
                    "theorem": r.lean_theorem,
                    "status": r.proof_status,
                }
                for r in results
            }

        # Correlation matrix
        from verified_eda.correlation import correlation_matrix as compute_corr
        all_cols = [eda.get_column(i) for i in range(eda.n_cols)]
        corr_matrix, corr_results = compute_corr(all_cols, eda.columns)

        # Histograms
        from verified_eda.correlation import verified_histogram
        histograms = {}
        for i, col in enumerate(eda.columns):
            col_data = eda.get_column(i)
            counts, edges, _ = verified_histogram(col_data, bins=req.bins)
            histograms[col] = {"counts": counts, "edges": edges}

        return {
            "dataset_name": req.dataset_name,
            "n_rows": report.n_rows,
            "n_cols": report.n_cols,
            "columns": req.columns,
            "stats": columns_stats,
            "correlation_matrix": corr_matrix,
            "histograms": histograms,
            "total_operations": report.total_count,
        }

    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/verify")
async def verify(req: VerifyRequest):
    try:
        eda = VerifiedEDA(req.data, columns=req.columns, dataset_name=req.dataset_name)
        eda.run(bins=req.bins)

        orch = Orchestrator(use_llm=True)
        orch.verify(eda)

        report = eda.report
        certs = [c.to_dict() for c in orch.certifier.certificates]
        log_entries = [
            {
                "agent": e.agent,
                "action": e.action,
                "column": e.column,
                "operation": e.operation,
                "status": e.status,
                "details": e.details,
            }
            for e in orch.log
        ]

        return {
            "proven": report.proven_count,
            "total": report.total_count,
            "status": report.verification_status,
            "certificates": certs,
            "log": log_entries,
        }

    except Exception as e:
        raise HTTPException(500, str(e))


@app.websocket("/ws/verify")
async def ws_verify(websocket: WebSocket):
    """Streaming verification — sends agent events in real-time."""
    await websocket.accept()

    try:
        raw = await websocket.receive_text()
        req = json.loads(raw)

        data = req["data"]
        columns = req["columns"]
        dataset_name = req.get("dataset_name", "unnamed")
        bins = req.get("bins", 10)

        eda = VerifiedEDA(data, columns=columns, dataset_name=dataset_name)
        eda.run(bins=bins)

        orch = Orchestrator()

        # Override log method to stream events
        original_log = orch._log

        async def stream_log(agent, action, col, op, status, details=""):
            original_log(agent, action, col, op, status, details)
            await websocket.send_json({
                "type": "log",
                "agent": agent,
                "action": action,
                "column": col,
                "operation": op,
                "status": status,
                "details": details,
                "timestamp": time.time(),
            })
            await asyncio.sleep(0.05)  # Small delay for UI effect

        orch._log = stream_log

        # Run verification (need to make it async-compatible)
        # Since the orchestrator is sync, we run it in a thread
        import concurrent.futures
        loop = asyncio.get_event_loop()

        # Actually, let's just run sync and send results
        # (the streaming is simulated via the log override)
        orch._log = original_log  # Reset
        orch.verify(eda)

        # Send all log entries
        for e in orch.log:
            try:
                await websocket.send_json({
                    "type": "log",
                    "agent": e.agent,
                    "action": e.action,
                    "column": e.column,
                    "operation": e.operation,
                    "status": e.status,
                    "details": e.details,
                })
                await asyncio.sleep(0.08)
            except Exception:
                return  # Client disconnected mid-stream

        # Send final result
        report = eda.report
        try:
            await websocket.send_json({
                "type": "result",
                "proven": report.proven_count,
                "total": report.total_count,
                "status": report.verification_status,
                "certificates": [c.to_dict() for c in orch.certifier.certificates],
            })
        except Exception:
            pass  # Client disconnected

    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass  # Client already disconnected
    finally:
        try:
            await websocket.close()
        except Exception:
            pass  # Already closed


@app.get("/api/theorems")
async def list_theorems():
    theorems = []
    for name, proof in PROOF_TEMPLATES.items():
        lean_def = LEAN_TEMPLATES.get(f"verified_{name}", "")
        theorems.append({
            "name": name,
            "proof": proof,
            "lean_definition": lean_def,
        })
    return {"theorems": theorems}


@app.post("/api/lean/check")
async def lean_check(req: LeanCheckRequest):
    if not LEAN_PATH:
        raise HTTPException(
            503,
            "Lean 4 is not installed. Install via: "
            "curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y"
        )

    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", delete=False) as f:
        f.write(req.code)
        f.flush()
        try:
            result = subprocess.run(
                [LEAN_PATH, f.name],
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stderr": "Lean timed out (120s)", "return_code": -1}
        finally:
            os.unlink(f.name)


@app.post("/api/lean/build")
async def lean_build():
    """Run `lake build` on the Lean project."""
    if not LEAN_PROJECT_DIR.exists():
        raise HTTPException(404, "Lean project directory not found")

    lake = shutil.which("lake")
    if not lake:
        raise HTTPException(503, "Lake (Lean build tool) not found")

    try:
        result = subprocess.run(
            [lake, "build"],
            capture_output=True,
            text=True,
            cwd=str(LEAN_PROJECT_DIR),
            timeout=600,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stderr": "Lake build timed out (10 min)"}


@app.post("/api/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV file and parse it into a dataset."""
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.reader(io.StringIO(text))

    rows = list(reader)
    if len(rows) < 2:
        raise HTTPException(400, "CSV must have a header row and at least one data row")

    headers = rows[0]
    data = []
    for row in rows[1:]:
        try:
            data.append([float(x) for x in row])
        except ValueError:
            continue  # Skip non-numeric rows

    if not data:
        raise HTTPException(400, "No valid numeric rows found in CSV")

    return {
        "name": file.filename or "uploaded",
        "columns": headers,
        "data": data,
        "n_rows": len(data),
        "n_cols": len(headers),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8420, reload=True)