#!/usr/bin/env python3
"""CIVID dashboard launcher.

Starts the dashboard server and opens the browser automatically.

Run:
  python scripts/open_dashboard.py
  python scripts/open_dashboard.py --port 8080
"""
from __future__ import annotations
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PORT = 8000
for i, arg in enumerate(sys.argv[1:], 1):
    if arg == "--port" and i < len(sys.argv):
        PORT = int(sys.argv[i + 1])
        break
    elif arg.isdigit():
        PORT = int(arg)
        break

# Start dashboard server
server_cmd = [sys.executable, str(REPO / "scripts" / "dashboard_server.py"), str(PORT)]
print(f"[starting] Dashboard server on port {PORT}...")
server = subprocess.Popen(server_cmd, cwd=REPO)

# Wait for server to start
time.sleep(2)

# Open browser
url = f"http://localhost:{PORT}/"
print(f"[opening] {url}")
webbrowser.open(url)

try:
    server.wait()
except KeyboardInterrupt:
    print("\n[stopping] Dashboard server...")
    server.terminate()
    server.wait()
    print("[stopped]")
