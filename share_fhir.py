#!/usr/bin/env python3
"""
FHIR Sharing Package
Easy setup for friends to use your FHIR system
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_sharing_package():
    """Create a complete sharing package"""
    print("📦 Creating FHIR Sharing Package...")
    
    # Files to include
    files_to_include = [
        'app.py',
        'worker_enhanced.py',
        'worker.py',
        'requirements_fullstack.txt',
        'requirements.txt',
        'templates/',
        'mobile_app/',
        'docker-compose.yml',
        'docker-compose.prod.yml',
        'Dockerfile',
        'README.md',
        'mapping 4.xlsx'  # Include sample data
    ]
    
    # Create sharing directory
    share_dir = f"fhir_share_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(share_dir, exist_ok=True)
    
    # Copy files
    for file_path in files_to_include:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                shutil.copytree(file_path, os.path.join(share_dir, file_path))
            else:
                shutil.copy2(file_path, share_dir)
            print(f"✅ Copied: {file_path}")
    
    # Create setup instructions
    setup_instructions = f"""
# FHIR System Setup Instructions

## Quick Start (Windows/Mac/Linux)

1. Install Python 3.8+ from https://python.org
2. Open terminal/command prompt in this folder
3. Run: pip install -r requirements_fullstack.txt
4. Run: python app.py
5. Open browser to: http://localhost:5000

## For Mobile Devices

1. Make sure your computer and mobile device are on the same WiFi
2. Find your computer's IP address (run: ipconfig on Windows, ifconfig on Mac/Linux)
3. On mobile device, go to: http://YOUR_IP_ADDRESS:5000

## For Friends on Different Networks

1. Deploy to cloud (Heroku, AWS, Google Cloud)
2. Share the cloud URL with friends
3. They can access from anywhere!

## Features Available

- Upload Excel files and convert to FHIR
- Enter patient data manually
- Download FHIR JSON and CSV files
- Works on phones, tablets, computers
- API endpoints for integration

## API Endpoints

- POST /api/upload - Upload Excel file
- POST /api/patient - Create patient
- GET /api/bundle/{{id}} - Get FHIR bundle
- GET /api/health - Health check

## Support

If you have issues, check:
1. Python is installed correctly
2. All dependencies are installed
3. Port 5000 is not blocked by firewall
4. Files are in the correct directory

Enjoy using the FHIR system! 🏥
"""
    
    with open(os.path.join(share_dir, "SETUP_INSTRUCTIONS.txt"), 'w') as f:
        f.write(setup_instructions)
    
    # Create zip file
    zip_filename = f"{share_dir}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(share_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, share_dir)
                zipf.write(file_path, arcname)
    
    print(f"\n✅ Sharing package created: {zip_filename}")
    print(f"�� Share this file with your friends!")
    print(f"📋 They can extract and follow SETUP_INSTRUCTIONS.txt")
    
    return zip_filename

if __name__ == "__main__":
    create_sharing_package()
