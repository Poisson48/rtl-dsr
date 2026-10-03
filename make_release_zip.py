#!/usr/bin/env python3
"""
Create rtl-dsr.zip with forward slashes in ZIP entry names.

This script is Windows-safe: it uses zipfile.ZipInfo() explicitly with
forward-slash paths so the resulting archive is POSIX-compatible (which
HACS and Home Assistant require).

Verification: after writing, the script re-opens the archive and prints
every entry name. Every name MUST use '/' separators.
"""
import os
import sys
import zipfile
from pathlib import Path

# Force UTF-8 output on Windows consoles
sys.stdout.reconfigure(encoding="utf-8")

SOURCE_DIR = Path("custom_components/rtl_dsr")
OUTPUT_ZIP = Path("rtl-dsr.zip")

def collect_files(base: Path):
    """Return (absolute_path, posix_arcname) for every file under base."""
    entries = []
    for path in sorted(base.rglob("*")):
        if path.is_file():
            # Build the archive name with forward slashes explicitly
            rel = path.relative_to(base.parent.parent)  # keep custom_components/rtl_dsr/...
            arcname = rel.as_posix()  # pathlib's as_posix() always uses '/'
            entries.append((path, arcname))
    return entries

def main():
    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    files = collect_files(SOURCE_DIR)
    print(f"Found {len(files)} files to archive")

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for abs_path, arcname in files:
            # ZipInfo with the arcname guarantees forward slashes in the header
            info = zipfile.ZipInfo(filename=arcname)
            info.external_attr = 0o644 << 16
            with open(abs_path, "rb") as fh:
                data = fh.read()
            zf.writestr(info, data)
            print(f"  + {arcname}")

    size = OUTPUT_ZIP.stat().st_size
    print(f"\nWrote {OUTPUT_ZIP} ({size} bytes)")

    # Verification: reopen and print every entry name
    print("\n=== VERIFY: entry names in the ZIP ===")
    with zipfile.ZipFile(OUTPUT_ZIP, "r") as zf:
        for name in zf.namelist():
            marker = "OK " if "/" in name and "\\" not in name else "BAD"
            print(f"  [{marker}] {name}")

    print("\nDone.")

if __name__ == "__main__":
    main()
