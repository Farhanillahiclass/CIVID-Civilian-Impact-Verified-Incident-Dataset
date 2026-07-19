#!/usr/bin/env python3
"""CIVID dashboard server with pipeline trigger, auto-refresh, and static file serving.

Serves the output/ directory and exposes:
  - GET  /              -> output/index.html
  - GET  /api/status    -> pipeline status JSON
  - POST /api/run_pipeline -> triggers full pipeline in background
  - Static serving of output/, exports/, data/leaders_photos/

Run: python scripts/dashboard_server.py [port]
Then open http://localhost:<port>/
"""
from __future__ import annotations
import http.server
import json
import os
import socketserver
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUTPUT = REPO / "output"
EXPORTS = REPO / "exports"

PIPELINE_LOCK = threading.Lock()
PIPELINE_RUNNING = False
LAST_PIPELINE = {
    "status": "idle",
    "last_run": "never",
    "records_added": 0,
    "records_reviewed": 0,
    "errors": [],
}


def find_free_port(start_port=8080, max_tries=20):
    import socket
    for port in range(start_port, start_port + max_tries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
            return port
        except OSError:
            continue
    raise RuntimeError(f"No free port in range {start_port}-{start_port + max_tries}")

PORT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else find_free_port(8000)

PIPELINE_LOCK = threading.Lock()
PIPELINE_RUNNING = False
LAST_PIPELINE = {
    "status": "idle",
    "last_run": "never",
    "records_added": 0,
    "records_reviewed": 0,
    "errors": [],
}


def log_event(step, status, duration=0, records_added=0, records_reviewed=0, errors=None):
    log_path = OUTPUT / "run_log.json"
    logs = []
    if log_path.exists():
        try:
            logs = json.load(open(log_path, encoding="utf-8"))
        except Exception:
            logs = []
    logs.append({
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "step": step,
        "status": status,
        "duration": duration,
        "records_added": records_added,
        "records_reviewed": records_reviewed,
        "errors": errors or [],
    })
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def run_pipeline():
    global PIPELINE_RUNNING, LAST_PIPELINE
    with PIPELINE_LOCK:
        if PIPELINE_RUNNING:
            return {"success": False, "message": "Pipeline already running."}
        PIPELINE_RUNNING = True

    steps = [
        ("validate", [sys.executable, str(REPO / "scripts" / "validate_dataset.py")]),
        ("renumber", [sys.executable, str(REPO / "scripts" / "renumber_records.py")]),
        ("news", [sys.executable, str(REPO / "scripts" / "generate_news_intelligence.py")]),
        ("export", [sys.executable, str(REPO / "scripts" / "build_exports.py")]),
        ("dashboard", [sys.executable, str(REPO / "scripts" / "generate_html_dashboard.py")]),
    ]

    added = 0
    reviewed = 0
    errors = []
    t0 = time.time()
    for name, cmd in steps:
        step_t0 = time.time()
        try:
            p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
            dur = round(time.time() - step_t0, 2)
            if p.returncode != 0:
                err = {"step": name, "message": p.stderr.strip() or f"exit {p.returncode}"}
                errors.append(err)
                log_event(name, "failed", dur, 0, 0, [err])
            else:
                log_event(name, "success", dur)
                if name == "export":
                    try:
                        summary = json.load(open(EXPORTS / "summary.json", encoding="utf-8"))
                        added = summary.get("totals", {}).get("events", 0)
                        reviewed = summary.get("totals", {}).get("events_verified", 0)
                    except Exception:
                        pass
        except Exception as e:
            dur = round(time.time() - step_t0, 2)
            err = {"step": name, "message": str(e)}
            errors.append(err)
            log_event(name, "failed", dur, 0, 0, [err])

    total_dur = round(time.time() - t0, 2)
    status = "failed" if errors else "success"
    LAST_PIPELINE = {
        "status": status,
        "last_run": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "records_added": added,
        "records_reviewed": reviewed,
        "errors": errors,
    }
    log_event("pipeline_complete", status, total_dur, added, reviewed, errors)
    PIPELINE_RUNNING = False
    return {"success": status == "success", "message": f"Pipeline {status}. {len(errors)} error(s).", "errors": errors}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(OUTPUT), **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/civid_dashboard.html":
            self.path = "/index.html"
        if self.path == "/api/status":
            log_path = OUTPUT / "run_log.json"
            logs = []
            if log_path.exists():
                try:
                    logs = json.load(open(log_path, encoding="utf-8"))
                except Exception:
                    logs = []
            last = logs[-1] if logs else LAST_PIPELINE
            status = {
                "status": last.get("status", "idle"),
                "last_run": last.get("timestamp", "never"),
                "records_added": last.get("records_added", 0),
                "records_reviewed": last.get("records_reviewed", 0),
                "errors": last.get("errors", []),
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
            return
        if self.path == "/" or self.path == "/index.html":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/run_pipeline":
            threading.Thread(target=lambda: self.run_and_respond(), daemon=True).start()
            return
        self.send_response(404)
        self.end_headers()

    def run_and_respond(self):
        result = run_pipeline()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())


if __name__ == "__main__":
    os.makedirs(OUTPUT, exist_ok=True)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"[ok] CIVID dashboard serving at http://localhost:{PORT}/")
        print("     API: GET /api/status  POST /api/run_pipeline")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[stopped]")
