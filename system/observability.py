"""
observability.py — Debugging Artifacts & Interaction Timelines
==============================================================
Captures before/after screenshots, DOM snapshots, and interaction
timelines so failures can be diagnosed rather than blindly retried.
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from playwright.sync_api import Page


@dataclass
class InteractionEvent:
    timestamp: str
    action: str
    target: str
    value: str = ""
    success: bool = True
    detail: str = ""
    confidence: float = 0.0


@dataclass
class InteractionTrace:
    """Full record of a single interaction attempt."""
    session_id: str
    url: str
    action: str
    target: str
    expected_value: str = ""
    events: List[InteractionEvent] = field(default_factory=list)
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None
    dom_snapshot: Optional[str] = None
    final_confidence: float = 0.0
    final_level: str = ""
    elapsed_ms: float = 0.0
    error: Optional[str] = None

    def add_event(self, action: str, target: str, value: str = "",
                  success: bool = True, detail: str = "", confidence: float = 0.0):
        self.events.append(InteractionEvent(
            timestamp=datetime.utcnow().isoformat(),
            action=action,
            target=target,
            value=value,
            success=success,
            detail=detail,
            confidence=confidence,
        ))

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "url": self.url,
            "action": self.action,
            "target": self.target,
            "expected_value": self.expected_value,
            "final_confidence": self.final_confidence,
            "final_level": self.final_level,
            "elapsed_ms": self.elapsed_ms,
            "error": self.error,
            "screenshot_before": self.screenshot_before,
            "screenshot_after": self.screenshot_after,
            "events": [
                {
                    "timestamp": e.timestamp,
                    "action": e.action,
                    "target": e.target,
                    "value": e.value,
                    "success": e.success,
                    "detail": e.detail,
                    "confidence": e.confidence,
                }
                for e in self.events
            ],
        }


class ObservabilityManager:
    """
    Captures debugging artifacts for every interaction attempt.
    Artifacts land in: applychain-workspace/logs/playwright_traces/
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        if workspace_root is None:
            workspace_root = Path(__file__).resolve().parents[2]
        self.trace_dir = workspace_root / "logs" / "playwright_traces"
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self._session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")

    def new_trace(self, page: Page, action: str, target: str, expected_value: str = "") -> InteractionTrace:
        return InteractionTrace(
            session_id=self._session_id,
            url=page.url,
            action=action,
            target=target,
            expected_value=expected_value,
        )

    def screenshot_before(self, page: Page, trace: InteractionTrace) -> Optional[str]:
        """Capture state before interaction."""
        try:
            path = self.trace_dir / f"{self._session_id}_{trace.action}_before.png"
            page.screenshot(path=str(path), full_page=False)
            trace.screenshot_before = str(path)
            return str(path)
        except Exception as e:
            trace.add_event("screenshot_before", "page", detail=f"failed: {e}", success=False)
            return None

    def screenshot_after(self, page: Page, trace: InteractionTrace) -> Optional[str]:
        """Capture state after interaction."""
        try:
            path = self.trace_dir / f"{self._session_id}_{trace.action}_after.png"
            page.screenshot(path=str(path), full_page=False)
            trace.screenshot_after = str(path)
            return str(path)
        except Exception as e:
            trace.add_event("screenshot_after", "page", detail=f"failed: {e}", success=False)
            return None

    def capture_dom_snapshot(self, page: Page, trace: InteractionTrace, selector: str = "body") -> Optional[str]:
        """Capture inner HTML of a region for diff analysis."""
        try:
            html = page.locator(selector).first.inner_html()
            path = self.trace_dir / f"{self._session_id}_{trace.action}_dom.html"
            path.write_text(html, encoding="utf-8")
            trace.dom_snapshot = str(path)
            return str(path)
        except Exception as e:
            trace.add_event("dom_snapshot", selector, detail=f"failed: {e}", success=False)
            return None

    def save_trace(self, trace: InteractionTrace) -> str:
        """Write the full trace JSON to disk and return path."""
        path = self.trace_dir / f"{self._session_id}_{trace.action}_trace.json"
        path.write_text(json.dumps(trace.to_dict(), indent=2), encoding="utf-8")
        return str(path)

    def log_selector_diagnostics(self, page: Page, selector: str) -> dict:
        """Debug why a selector might not be matching."""
        try:
            count = page.locator(selector).count()
            visible_count = page.locator(selector).filter(has=page.locator(":visible")).count()
            return {
                "selector": selector,
                "total_matches": count,
                "visible_matches": visible_count,
                "page_url": page.url,
            }
        except Exception as e:
            return {"selector": selector, "error": str(e)}

    def detect_rerender_wipe(self, page: Page, selector: str, value: str, wait_ms: int = 600) -> dict:
        """
        Check if value was reverted after a pause — catches React rerender wipes.
        """
        time.sleep(wait_ms / 1000)
        try:
            loc = page.locator(selector).first
            actual = loc.input_value(timeout=1000)
            wiped = value.lower() not in actual.lower()
            return {
                "selector": selector,
                "expected": value,
                "actual_after_wait": actual,
                "wiped": wiped,
                "wait_ms": wait_ms,
            }
        except Exception as e:
            return {"selector": selector, "error": str(e), "wiped": False}
