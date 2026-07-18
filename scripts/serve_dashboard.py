#!/usr/bin/env python3
"""CIVID dashboard static server.

Serves exports/ so the generated civid_dashboard.html is viewable in a browser
with correct relative paths, and supports auto-refresh workflows.

Run:  python scripts/serve_dashboard.py [port]
Then open the printed URL. The dashboard reads exports/ files; re-run
scripts/refresh.py to push the latest data, then reload the browser.
"""
from __future__ import annotations
import http.server, socketserver, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS = os.path.join(REPO, "exports")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=EXPORTS, **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    os.makedirs(EXPORTS, exist_ok=True)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"[ok] CIVID dashboard serving at http://localhost:{PORT}/civid_dashboard.html")
        print("     Press Ctrl+C to stop. Re-run scripts/refresh.py then reload to see new data.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[stopped]")
