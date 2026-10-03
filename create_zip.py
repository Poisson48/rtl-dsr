#!/usr/bin/env python3
"""Create a zip archive with forward slashes for HACS."""
import zipfile
import os
from pathlib import Path

def create_zip_with_forward_slashes():
    """Create rtl-dsr.zip with forward slashes in paths."""
    zip_name = "rtl-dsr.zip"
    
    # Remove old zip if exists
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    # Create new zip
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add custom_components/rtl_dsr/ files
        base_path = Path("custom_components/rtl_dsr")
        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                # Use forward slashes in the archive
                arcname = str(file_path).replace("\\", "/")
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")
    
    print(f"\nCreated {zip_name} with forward slashes")
    print(f"   Size: {os.path.getsize(zip_name)} bytes")

if __name__ == "__main__":
    create_zip_with_forward_slashes()
