"""
engine.py — HumanSimulationEngine
==================================
Top-level orchestrator. Connects to Chrome via CDP, dispatches
interactions through helpers, scores confidence, captures traces,
and escalates when confidence falls below threshold.

Usage:
    with HumanSimulationEngine().connect(tab_url="https://...") as eng:
        result = eng.fill_field(label="School", value="Miami University")
        print(result)  # JSON-serializable dict
"""

from __future__ import annotations
import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from .confidence import InteractionConfidence, ConfidenceLevel
from .helpers import InteractionHelpers
from .observability import ObservabilityManager
from .validation import FrontendValidator

# Default Chrome CDP endpoint — Chrome must be launched with:
#   --remote-debugging-port=9222
DEFAULT_CDP_URL = "http://localhost:9222"


class HumanSimulationEngine:
    """
    Primary interface for all ATS form interactions.
    Wraps Playwright with confidence scoring, state verification,
    retry logic, and trace capture.
    """

    def __init__(
        self,
        cdp_url: str = DEFAULT_CDP_URL,
        workspace_root: Optional[Path] = None,
        typing_profile: str = "human",
        debug: bool = False,
        max_retries: int = 2,
    ):
        self.cdp_url = cdp_url
        self.workspace_root = workspace_root or Path(__file__).resolve().parents[2]
        self.typing_profile = typing_profile
        self.debug = debug
        self.max_retries = max_retries

        self._playwright = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._helpers: Optional[InteractionHelpers] = None
        self._obs: Optional[ObservabilityManager] = None
        self._adapter = None  # Set by adapter registry after connect

    # ── Connection ────────────────────────────────────────────────────

    def connect(self, tab_url: Optional[str] = None) -> "HumanSimulationEngine":
        """
        Connect to Chrome via CDP. Falls back to launching a new browser
        if CDP endpoint not available.
        tab_url: if provided, finds the matching open tab.
        """
        self._playwright = sync_playwright().start()
        self._obs = ObservabilityManager(self.workspace_root)

        try:
            self._browser = self._playwright.chromium.connect_over_cdp(self.cdp_url)
            contexts = self._browser.contexts
            if not contexts:
                raise RuntimeError("No browser contexts found via CDP")

            self._page = self._find_tab(contexts[0].pages, tab_url)
            if self._debug_log(f"Connected via CDP to: {self._page.url}"):
                pass

        except Exception as e:
            if self.debug:
                print(f"[engine] CDP connect failed ({e}), launching new browser")
            # Fallback: launch a fresh Chromium
            self._browser = self._playwright.chromium.launch(headless=False)
            context = self._browser.new_context()
            self._page = context.new_page()
            if tab_url:
                self._page.goto(tab_url, wait_until="domcontentloaded")

        self._helpers = InteractionHelpers(
            self._page, typing_profile=self.typing_profile, debug=self.debug
        )

        # Auto-detect ATS adapter
        from .adapters.registry import AdapterRegistry
        self._adapter = AdapterRegistry.detect(self._page.url, self)

        return self

    def _find_tab(self, pages, tab_url: Optional[str]):
        """Return the page matching tab_url, or the most recent page."""
        if tab_url:
            for p in pages:
                if tab_url in p.url:
                    return p
            # Try partial URL match
            for p in pages:
                parts = [seg for seg in tab_url.split("/") if len(seg) > 4]
                if any(part in p.url for part in parts):
                    return p
        return pages[-1] if pages else None

    def disconnect(self) -> None:
        """Clean up Playwright resources."""
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.disconnect()

    @property
    def page(self) -> Page:
        if not self._page:
            raise RuntimeError("Engine not connected. Call .connect() first.")
        return self._page

    # ── High-level interaction API ────────────────────────────────────

    def fill_field(self, label: str, value: str, selector: Optional[str] = None) -> dict:
        """
        Fill a text input found by label text or CSS selector.
        Returns interaction result dict.
        """
        trace = self._obs.new_trace(self.page, "fill_field", label, value)
        self._obs.screenshot_before(self.page, trace)

        loc = self._resolve_locator(label, selector, field_type="input")
        if loc is None:
            trace.error = f"Could not find field: label='{label}' selector='{selector}'"
            self._obs.screenshot_after(self.page, trace)
            return self._result(False, None, trace)

        def _action():
            return self._helpers.type_human_like(loc, value, label=label)

        success, conf = self._helpers.safe_retry_interaction(
            _action, max_retries=self.max_retries
        )

        self._obs.screenshot_after(self.page, trace)
        trace.final_confidence = conf.raw_score
        trace.final_level = conf.level.value
        trace_path = self._obs.save_trace(trace)

        result = self._result(success, conf, trace)
        result["trace_path"] = trace_path
        return result

    def select_option(self, label: str, value: str, selector: Optional[str] = None) -> dict:
        """Select an option in a native <select> dropdown."""
        trace = self._obs.new_trace(self.page, "select_option", label, value)
        self._obs.screenshot_before(self.page, trace)

        loc = self._resolve_locator(label, selector, field_type="select")
        if loc is None:
            trace.error = f"Could not find select: label='{label}'"
            return self._result(False, None, trace)

        def _action():
            return self._helpers.select_dropdown_option(loc, value, label=label)

        success, conf = self._helpers.safe_retry_interaction(_action, max_retries=self.max_retries)
        self._obs.screenshot_after(self.page, trace)
        trace.final_confidence = conf.raw_score
        trace.final_level = conf.level.value
        self._obs.save_trace(trace)
        return self._result(success, conf, trace)

    def click_radio(self, label_text: str, container_selector: str = "body") -> dict:
        """Click a radio button by its visible label text."""
        trace = self._obs.new_trace(self.page, "click_radio", label_text)
        self._obs.screenshot_before(self.page, trace)

        def _action():
            return self._helpers.click_radio_by_label(label_text, container_selector)

        success, conf = self._helpers.safe_retry_interaction(_action, max_retries=self.max_retries)
        self._obs.screenshot_after(self.page, trace)
        trace.final_confidence = conf.raw_score
        trace.final_level = conf.level.value
        self._obs.save_trace(trace)
        return self._result(success, conf, trace)

    def click_button(self, text: str, verify_selector: Optional[str] = None) -> dict:
        """Click a button or link by its visible text."""
        trace = self._obs.new_trace(self.page, "click_button", text)
        self._obs.screenshot_before(self.page, trace)

        loc = self.page.get_by_role("button", name=text, exact=False).first
        if loc.count() == 0:
            loc = self.page.get_by_text(text, exact=False).first

        def _action():
            return self._helpers.click_visible_element(
                loc, label=text, verify_selector=verify_selector
            )

        success, conf = self._helpers.safe_retry_interaction(_action, max_retries=self.max_retries)
        self._obs.screenshot_after(self.page, trace)
        trace.final_confidence = conf.raw_score
        trace.final_level = conf.level.value
        self._obs.save_trace(trace)
        return self._result(success, conf, trace)

    def click_add_another(self, section_hint: str = "") -> dict:
        """
        Find and click an 'Add Another / Add More' button.
        section_hint: partial text like 'education' or 'experience'.
        """
        keywords = ["add another", "add more", "+ add", "add a"]
        if section_hint:
            keywords = [f"add another {section_hint}", f"add {section_hint}"] + keywords

        for keyword in keywords:
            try:
                btn = self.page.get_by_role("button", name=keyword, exact=False).first
                if btn.count() > 0:
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    time.sleep(0.5)  # wait for new row to render
                    return {"success": True, "button_text": keyword, "confidence": 0.9}
            except Exception:
                continue

        # Fallback: text search across all clickables
        try:
            loc = self.page.get_by_text("Add Another", exact=False).first
            if loc.count() > 0:
                loc.scroll_into_view_if_needed()
                loc.click()
                time.sleep(0.5)
                return {"success": True, "button_text": "Add Another (text)", "confidence": 0.8}
        except Exception:
            pass

        return {"success": False, "button_text": None, "confidence": 0.0,
                "error": f"No 'Add Another' button found for section '{section_hint}'"}

    def audit_add_another_buttons(self) -> dict:
        """Scan page for all 'Add Another' buttons — call before filling repeating sections."""
        keywords = ["add another", "add more", "+ add", "add education", "add experience",
                    "add work", "add entry"]
        found = []
        try:
            buttons = self.page.get_by_role("button").all()
            for btn in buttons:
                txt = (btn.inner_text() or "").strip().lower()
                if any(kw in txt for kw in keywords):
                    found.append(btn.inner_text().strip())
        except Exception:
            pass
        return {"found": found, "count": len(found)}

    def validate_state(self, expected_fields: dict) -> dict:
        """Validate multiple visible fields. {selector: expected_value}"""
        return self._helpers.validate_frontend_state(expected_fields)

    def screenshot(self, label: str = "manual") -> str:
        """Take a screenshot and return the path."""
        trace = self._obs.new_trace(self.page, label, "page")
        return self._obs.screenshot_before(self.page, trace) or ""

    def wait_stable(self, ms: int = 400) -> None:
        """Wait for DOM to settle."""
        self._helpers.wait_for_stable_dom(ms)

    # ── ATS adapter passthrough ───────────────────────────────────────

    def run_adapter_action(self, action: str, **kwargs) -> dict:
        """Delegate to the detected ATS adapter if available."""
        if self._adapter and hasattr(self._adapter, action):
            return getattr(self._adapter, action)(**kwargs)
        return {"success": False, "error": f"No adapter action '{action}' available for this ATS"}

    # ── Internals ─────────────────────────────────────────────────────

    def _resolve_locator(self, label: str, selector: Optional[str], field_type: str = "input"):
        """Find a locator by label text or CSS selector."""
        try:
            if selector:
                return self.page.locator(selector).first
            if field_type == "select":
                loc = self.page.locator(f"select").filter(
                    has=self.page.locator(f"[aria-label*='{label}']")
                ).first
                if loc.count() == 0:
                    loc = self.page.get_by_label(label, exact=False).first
                return loc
            return self.page.get_by_label(label, exact=False).first
        except Exception:
            return None

    def _result(self, success: bool, conf: Optional[InteractionConfidence], trace) -> dict:
        return {
            "success": success,
            "confidence": conf.raw_score if conf else 0.0,
            "confidence_level": conf.level.value if conf else "FAILED",
            "escalate": conf.should_escalate if conf else True,
            "url": self.page.url if self._page else "",
            "screenshot_before": trace.screenshot_before,
            "screenshot_after": trace.screenshot_after,
            "confidence_detail": conf.to_dict() if conf else {},
        }

    def _debug_log(self, msg: str) -> bool:
        if self.debug:
            print(f"[engine] {msg}")
        return True
