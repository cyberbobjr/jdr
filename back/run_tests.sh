#!/bin/bash

# This script runs all pytest tests in the tests/ directory, ensuring the correct PYTHONPATH.

# Get the directory of this script to reliably find the project root.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

# Change to the project root directory.
cd "$PROJECT_ROOT"

# Activate the virtual environment.
source back/venv/bin/activate

# Add the project root to the PYTHONPATH to resolve 'from back.app...' imports.
export PYTHONPATH="$PWD"

echo "Running all tests from back/tests/..."
pytest back/tests/

