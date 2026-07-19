"""
Adapter registry. Add a new source by creating adapters/<name>.py with a
class subclassing BaseAdapter and registering it here — no core changes.
"""
from .wikipedia import WikipediaAdapter
from .guardian import GuardianAdapter
from .aljazeera import AlJazeeraAdapter

ADAPTERS = {
    "wikipedia": WikipediaAdapter,
    "guardian": GuardianAdapter,
    "aljazeera": AlJazeeraAdapter,
}

__all__ = ["ADAPTERS"]
