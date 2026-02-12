#!/bin/bash

# Stop if error
set -e

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installation complete."
echo "Run the application with:"
echo "source .venv/bin/activate && python3 app.py"