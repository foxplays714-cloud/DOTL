#!/bin/bash
echo "Installing dependencies..."
pip install PyQt6 numpy Pillow scipy opencv-python

echo "Starting Paint+..."
python main.py
