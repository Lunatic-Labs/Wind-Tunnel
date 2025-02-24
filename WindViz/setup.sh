#!/bin/bash

# Check if a virtual environment directory exists, if not create one
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR
else
  echo "Virtual environment already exists."
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Install the required packages from requirements.txt
if [ -f "requirements.txt" ]; then
  echo "Installing packages from requirements.txt..."
  pip install -r requirements.txt
else
  echo "requirements.txt not found!"
fi

echo "Setup complete! To keep the virtual environment active, use: source venv/bin/activate"

