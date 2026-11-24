"""Launch AETHERVEXA without a console window (also the PyInstaller entry point)."""

from aethervexa.app import main

if __name__ == "__main__":
    raise SystemExit(main())
