#!/usr/bin/env python3
"""
FHIR Multi-Device Setup Script
Run this to share your FHIR system with friends on the same network
"""

import socket
import subprocess
import sys
import os
from flask import Flask
import webbrowser
import threading
import time

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import pandas
        import openpyxl
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_fullstack.txt"])
        return True

def start_server():
    """Start the Flask server"""
    print("�� Starting FHIR Server...")
    print("=" * 50)
    
    # Get local IP
    local_ip = get_local_ip()
    
    print(f"�� Server will be available at:")
    print(f"   Your computer: http://localhost:5000")
    print(f"   Other devices: http://{local_ip}:5000")
    print(f"   Mobile devices: http://{local_ip}:5000")
    print("\n📱 Share these URLs with your friends!")
    print("=" * 50)
    
    # Start the server
    os.system("python app.py --host=0.0.0.0 --port=5000")

if __name__ == "__main__":
    print("🏥 FHIR Multi-Device Setup")
    print("=" * 30)
    
    if check_dependencies():
        start_server()
    else:
        print("❌ Setup failed. Please install dependencies manually.")
