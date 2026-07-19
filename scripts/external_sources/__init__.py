"""
CIVID External Source Extractor — package init.
Stdlib-only (matches scripts/daily_update.py conventions). Adds no deps.
"""
from .pipeline import run_source, run_all
from .base_adapter import BaseAdapter, AdapterResult
from .adapters import ADAPTERS

__all__ = ["run_source", "run_all", "BaseAdapter", "AdapterResult", "ADAPTERS"]
