#!/bin/bash
echo "Executando Diagnóstico do Codex..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/diagnose_codex.py"
