"""
Shared HTTP + config helpers for the external source extractor.
Stdlib-only: urllib, configparser, logging.
"""
import os
import configparser
from pathlib import Path
from urllib import request, error, parse

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = ROOT / "config"
SCHEMA_DIR = ROOT / "schema"

USER_AGENT = (
    "CIVID-research/1.0 "
    "(non-commercial humanitarian research; +https://github.com/civid-dataset) "
    "contact: research@civid.example"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, application/xml;q=0.9, text/html;q=0.8",
}


def load_dotenv():
    """Load KEY=VALUE pairs from .env (gitignored) into os.environ if unset."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip()
        if key and key not in os.environ:
            os.environ[key] = val


def load_cfg(source: str) -> dict:
    """Load a source config file as plain KEY=VALUE lines (no sections),
    so the project stays stdlib-only (no PyYAML dependency)."""
    cfg_path = CONFIG_DIR / f"{source}.yaml"
    out: dict = {}
    if not cfg_path.exists():
        return out
    # Support both `key: value` scalars and block lists:
    #   key:
    #     - item1
    #     - item2
    current_list_key = None
    for raw in cfg_path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # list item under an active block list
        if current_list_key is not None and stripped.startswith("- "):
            item = stripped[2:].strip().strip('"').strip("'")
            if " #" in item:
                item = item.split(" #", 1)[0].strip()
            out.setdefault(current_list_key, []).append(item)
            continue
        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        key, val = key.strip(), val.strip()
        if " #" in val:
            val = val.split(" #", 1)[0].strip()
        if val == "":
            # open a block list (unless it already exists as scalar)
            if key not in out:
                out[key] = []
            current_list_key = key
        else:
            out[key] = _coerce(val)
            current_list_key = None
    return out


def _coerce(v: str):
    """Coerce common scalar/list/boolean types from config text."""
    v = v.strip()
    low = v.lower()
    if low in ("null", "none", "nil"):
        return None
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    # strip surrounding quotes from scalars like "Gaza OR ..."
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        v = v[1:-1].strip()
        low = v.lower()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def http_get_json(url: str, timeout: int = 20) -> dict:
    req = request.Request(url, headers=HEADERS)
    with request.urlopen(req, timeout=timeout) as resp:
        return json_loads(resp.read().decode("utf-8", "replace"))


def http_get_text(url: str, timeout: int = 20) -> str:
    req = request.Request(url, headers=HEADERS)
    with request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def json_loads(s: str) -> dict:
    import json
    return json.loads(s)
