#!/usr/bin/env python
"""
Simple launcher script for the Lucky Wheel App
This helps avoid debugger connection issues
"""

import os
import sys
import subprocess

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main application
    app_path = os.path.join(script_dir, "lucky_wheel_app.py")
    
    # Run the application directly without debugger
    print("Starting Lucky Wheel App...")
    subprocess.run([sys.executable, app_path])

if __name__ == "__main__":
    main()