#!/usr/bin/env bash
set -euo pipefail

echo "== Photon Install =="

# must be run from repo root
if [[ ! -f "ui_app.py" ]]; then
  echo "ERROR: ui_app.py not found. Run this script from the repo root."
  exit 1
fi

echo "== Updating apt and installing system dependencies (sudo required) =="
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-tk

echo "== Creating virtual environment (.venv) if needed =="
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

echo "== Installing Python dependencies into venv =="
source .venv/bin/activate
python -m pip install --upgrade pip
pip install psycopg2-binary pillow

echo "== Verifying imports =="
python -c "import tkinter; print('tkinter: OK')"
python -c "import psycopg2; print('psycopg2: OK')"
python -c "from PIL import Image; print('pillow: OK')"

echo "== Checking assets =="
if [[ ! -f "assets/logo.png" ]]; then
  echo "WARNING: assets/logo.png not found. Splash screen will show text fallback."
else
  echo "assets/logo.png: OK"
fi

echo "== Checking PostgreSQL service==" 
if command -v systemctl >/dev/null 2>&1; then
  if systemctl is-active --quiet postgresql; then
    echo "postgresql: active"
  else
    echo "postgresql: NOT active — start it with: sudo systemctl start postgresql"
  fi
else
  echo "systemctl not available, skipping postgres check"
fi

echo ""
echo "== Install complete =="
echo "Next:"
echo "  source .venv/bin/activate"
echo "  python3 ui_app.py"