#!/bin/bash
# setup.sh — Install dependencies for ApplyChain
# Run once after cloning: bash scripts/setup.sh

set -e

echo "=== ApplyChain setup ==="

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "ERROR: Python 3 is required. Install it from https://python.org"
  exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python $PYTHON_VERSION detected"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install python-docx openpyxl --break-system-packages 2>/dev/null || \
  pip3 install python-docx openpyxl

# Check for .env
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Created .env from .env.example — fill in your credentials"
  else
    echo "WARNING: No .env.example found. Create a .env file manually."
  fi
else
  echo ".env already exists"
fi

# Initialize log
if [ ! -f "logs/applications_log.csv" ]; then
  echo "Initializing applications log..."
  python3 scripts/init_log.py
else
  echo "applications_log.csv already exists"
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Fill in your credentials in .env"
echo "  2. Fill in profile_knowledge_base/ templates with your information"
echo "  3. Install the Claude for Chrome extension"
echo "  4. Open Claude Desktop in Cowork mode and start your first application"
