"""
playwright_engine — Human-Simulation Interaction Engine for ApplyChain
======================================================================
Provides deterministic, human-like browser interactions via Playwright
connected to an existing Chrome session via CDP.

Usage (from Claude via bash):
    python -m system.playwright_engine.cli fill-field \\
        --tab-url "https://apply.[company].com/..." \\
        --label "School" --value "Miami University"

Returns JSON with: success, confidence, action_log, screenshot_path
"""

from .engine import HumanSimulationEngine
from .confidence import InteractionConfidence, ConfidenceLevel
from .helpers import InteractionHelpers
from .validation import FrontendValidator

__version__ = "0.1.0"
__all__ = [
    "HumanSimulationEngine",
    "InteractionConfidence",
    "ConfidenceLevel",
    "InteractionHelpers",
    "FrontendValidator",
]
