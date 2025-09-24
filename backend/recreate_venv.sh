#!/bin/bash

# Script to recreate virtual environment with Python 3.10

echo "=== Recreating virtual environment with Python 3.10 ==="

# Step 1: Backup requirements
echo "1. Backing up current requirements..."
if [ -f "venv/bin/pip" ]; then
    ./venv/bin/pip freeze > requirements_backup.txt
    echo "   Requirements saved to requirements_backup.txt"
else
    echo "   No existing venv found, skipping backup"
fi

# Step 2: Remove old venv
echo "2. Removing old virtual environment..."
rm -rf venv

# Step 3: Create new venv with Python 3.10
echo "3. Creating new virtual environment with Python 3.10..."
python3.10 -m venv venv

# Step 4: Activate and upgrade pip
echo "4. Upgrading pip..."
./venv/bin/pip install --upgrade pip

# Step 5: Install requirements
echo "5. Installing requirements..."
./venv/bin/pip install -r requirements.txt

# Step 6: Install additional ML libraries if needed
echo "6. Installing ML libraries..."
./venv/bin/pip install ultralytics opencv-python-headless pillow numpy

# Optional: Install face recognition libraries
echo "7. Optional: Install face recognition libraries? (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    ./venv/bin/pip install onnxruntime insightface
fi

echo "=== Virtual environment recreation complete ==="
echo "Python version in new venv:"
./venv/bin/python --version

echo ""
echo "To activate the new environment, run:"
echo "source venv/bin/activate"