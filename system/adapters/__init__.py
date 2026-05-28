"""ATS Platform Adapters — override base interaction behavior per platform."""
from .base import BaseATSAdapter
from .registry import AdapterRegistry

__all__ = ["BaseATSAdapter", "AdapterRegistry"]
