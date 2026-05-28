"""
workday.py — Workday ATS Adapter
==================================
Workday is a React SPA with custom ARIA components, aggressive hydration
delays, and modal-based date pickers. High rerender frequency.
Status: DOCUMENTED — not yet observed in production. Update after first use.
"""

from __future__ import annotations
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine import HumanSimulationEngine

from .base import BaseATSAdapter


class WorkdayAdapter(BaseATSAdapter):
    platform_name = "workday"
    url_patterns = [
        "myworkday.com",
        "wd1.myworkday",
        "wd3.myworkday",
        "wd5.myworkday",
        "workday.com/en-US/apply",
    ]

    # Workday hydration is slow — increase all timeouts
    HYDRATION_TIMEOUT = 8000

    def on_page_load(self) -> None:
        """Wait for Workday's Angular/React shell to fully hydrate."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=self.HYDRATION_TIMEOUT)
        except Exception:
            time.sleep(2.0)  # fallback wait

    def fill_field(self, label: str, value: str) -> dict:
        """Workday text inputs: use fill() with tab-away to trigger onChange."""
        try:
            loc = self.page.get_by_label(label, exact=False).first
            loc.scroll_into_view_if_needed()
            loc.click()
            time.sleep(0.2)
            loc.fill(value)
            time.sleep(0.1)
            loc.press("Tab")
            time.sleep(0.6)  # Workday async validation

            actual = loc.input_value(timeout=2000)
            success = value.lower() in actual.lower()
            return {"success": success, "actual": actual, "confidence": 0.80 if success else 0.25}
        except Exception as e:
            return {"success": False, "error": str(e), "confidence": 0.0}

    def fill_autocomplete(self, container_id: str, value: str) -> dict:
        """
        Workday typeahead: click field, type, wait for dropdown, click option.
        NOTE: Workday dropdowns have AJAX search — always wait >= 1.5s.
        """
        try:
            loc = self.page.get_by_label(container_id, exact=False).first
            loc.click()
            time.sleep(0.3)
            loc.type(value, delay=80)
            time.sleep(1.5)  # AJAX search delay

            # Options appear in a listbox
            option = self.page.get_by_role("option", name=value, exact=False).first
            option.wait_for(state="visible", timeout=5000)
            option.click()
            time.sleep(0.4)

            return {"success": True, "value": value, "confidence": 0.82}
        except Exception as e:
            return {"success": False, "error": str(e), "confidence": 0.0}

    def fill_date(self, label: str, month: int, year: int, day: int = 1) -> dict:
        """
        Workday date fields: type directly in MM/DD/YYYY format.
        The date picker modal is harder to automate than typing.
        """
        value = f"{month:02d}/{day:02d}/{year}"
        return self.fill_field(label, value)

    def click_next(self) -> dict:
        for label in ["Next", "Save and Continue", "Continue"]:
            result = self.engine.click_button(label)
            if result["success"]:
                time.sleep(2.0)  # Workday page transitions
                return result
        return {"success": False, "error": "Could not find Next button"}

    # TODO: After first observed Workday application, document:
    # - exact ARIA roles for dropdowns
    # - date picker modal selectors
    # - file upload flow
    # - EEO question format
    # - submit button selector
