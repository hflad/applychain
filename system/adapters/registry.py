"""
registry.py — ATS Adapter Auto-Detection
=========================================
Inspects the current page URL and returns the appropriate adapter.
Add new platforms here as they're encountered.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine import HumanSimulationEngine

from .base import BaseATSAdapter


class AdapterRegistry:
    """
    Maps URL patterns → adapter classes.
    Call AdapterRegistry.detect(url, engine) to get the right adapter.
    """

    _registry: list[tuple[list[str], type]] = []

    @classmethod
    def register(cls, patterns: list[str], adapter_cls: type) -> None:
        cls._registry.append((patterns, adapter_cls))

    @classmethod
    def detect(cls, url: str, engine: "HumanSimulationEngine") -> BaseATSAdapter:
        """Return the best matching adapter for the given URL."""
        url_lower = url.lower()
        for patterns, adapter_cls in cls._registry:
            if any(p in url_lower for p in patterns):
                return adapter_cls(engine)
        return BaseATSAdapter(engine)

    @classmethod
    def list_platforms(cls) -> list[str]:
        return [
            getattr(adapter_cls, "platform_name", "unknown")
            for _, adapter_cls in cls._registry
        ]


# ── Register all known adapters ───────────────────────────────────────
# Import here to trigger registration (avoid circular imports)

def _register_all():
    from .taleo import TaleoAdapter
    from .avature import AvatureAdapter
    from .workday import WorkdayAdapter
    from .greenhouse import GreenhouseAdapter

    AdapterRegistry.register(TaleoAdapter.url_patterns, TaleoAdapter)
    AdapterRegistry.register(AvatureAdapter.url_patterns, AvatureAdapter)
    AdapterRegistry.register(WorkdayAdapter.url_patterns, WorkdayAdapter)
    AdapterRegistry.register(GreenhouseAdapter.url_patterns, GreenhouseAdapter)


_register_all()
