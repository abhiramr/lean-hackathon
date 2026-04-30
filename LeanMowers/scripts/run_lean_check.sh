#!/usr/bin/env bash
# scripts/run_lean_check.sh — Build and type-check the Lean 4 proofs.
#
# Prerequisites: elan (Lean version manager) must be installed.
#   curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
#
# Usage:
#   ./scripts/run_lean_check.sh
#
# This will:
#   1. cd into the lean/ directory
#   2. Download the correct Lean toolchain (from lean-toolchain)
#   3. Fetch Mathlib4 (first run may take 10-20 minutes)
#   4. Build and type-check all .lean files
#   5. Exit 0 if all proofs pass, non-zero otherwise

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LEAN_DIR="$PROJECT_ROOT/lean"

echo "═══════════════════════════════════════════════"
echo "  Verified EDA — Lean 4 Proof Checker"
echo "═══════════════════════════════════════════════"
echo ""

# Check elan is installed
if ! command -v elan &>/dev/null && ! command -v lean &>/dev/null; then
    echo "ERROR: Neither 'elan' nor 'lean' found in PATH."
    echo ""
    echo "Install elan (Lean version manager):"
    echo "  curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y"
    echo ""
    echo "Then restart your shell or run: source ~/.profile"
    exit 1
fi

# Ensure PATH includes elan
if [ -d "$HOME/.elan/bin" ]; then
    export PATH="$HOME/.elan/bin:$PATH"
fi

cd "$LEAN_DIR"
echo "Working directory: $LEAN_DIR"
echo "Lean toolchain:    $(cat lean-toolchain)"
echo ""

# Build
echo "Building Lean project (first run downloads Mathlib, may take 10-20 min)..."
echo ""

if lake build; then
    echo ""
    echo "═══════════════════════════════════════════════"
    echo "  ✓ ALL PROOFS TYPE-CHECKED SUCCESSFULLY"
    echo "═══════════════════════════════════════════════"
    exit 0
else
    echo ""
    echo "═══════════════════════════════════════════════"
    echo "  ✗ PROOF CHECK FAILED"
    echo "═══════════════════════════════════════════════"
    exit 1
fi
