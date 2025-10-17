#!/bin/bash
# Seed runner convenience script for CWMT Flask Application
# This script activates the virtual environment and runs the seed runner

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Activate virtual environment if it exists
if [ -f "$PROJECT_ROOT/.venv/Scripts/activate" ]; then
    source "$PROJECT_ROOT/.venv/Scripts/activate"
elif [ -f "$PROJECT_ROOT/venv/Scripts/activate" ]; then
    source "$PROJECT_ROOT/venv/Scripts/activate"
fi

# Run the seed script with all arguments passed through
python "$SCRIPT_DIR/run_seeds.py" "$@"
