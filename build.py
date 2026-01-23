#!/usr/bin/env python3
"""
Build script for packaging the Fogo skill.

Usage:
    python build.py
"""

import zipfile
import os
from pathlib import Path

SKILL_DIR = "fogo"
OUTPUT_FILE = "fogo.skill"

def build():
    # Validate SKILL.md exists
    skill_md = Path(SKILL_DIR) / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: {skill_md} not found")
        return False
    
    # Remove old build
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    # Create .skill file (zip archive)
    with zipfile.ZipFile(OUTPUT_FILE, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_DIR):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path  # Preserve fogo/ prefix
                zf.write(file_path, arc_name)
                print(f"  Added: {arc_name}")
    
    print(f"\n✅ Built {OUTPUT_FILE}")
    return True

if __name__ == "__main__":
    print(f"📦 Building skill from {SKILL_DIR}/\n")
    build()
