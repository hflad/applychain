"""
greenhouse.py — Greenhouse ATS Adapter
========================================
Greenhouse uses standard HTML forms with some custom JS validation.
Generally the most reliable ATS to automate.
Status: DOCUMENTED — not yet observed in production. Update after first use.
"""

from __future__ import annotations
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine import HumanSimulationEngine

from .base import BaseATSAdapter


class GreenhouseAdapter(BaseATSAdapter):
    platform_name = "greenhouse"
    url_patterns = [
        "greenhouse.io",
        "boards.greenhouse.io",
        "app.greenhouse.io",
        "grnh.se",
    ]

    def fill_field(self, label: str, value: str) -> dict:
        """Greenhouse standard inputs respond well to fill() + Tab."""
        try:
            loc = self.page.get_by_label(label, exact=False).first
            loc.scroll_into_view_if_needed()
            loc.fill(value)
            loc.press("Tab")
            time.sleep(0.2)
            actual = loc.input_value(timeout=1500)
            success = value.lower() in actual.lower()
            return {"success": success, "actual": actual, "confidence": 0.90 if success else 0.30}
        except Exception as e:
            return {"success": False, "error": str(e), "confidence": 0.0}

    def fill_autocomplete(self, container_id: str, value: str) -> dict:
        """Greenhouse location/school fields: type + select from dropdown."""
        try:
            loc = self.page.get_by_label(container_id, exact=False).first
            loc.click()
            loc.fill(value)
            time.sleep(0.8)
            option = self.page.get_by_role("option", name=value, exact=False).first
            option.wait_for(state="visible", timeout=3000)
            option.click()
            return {"success": True, "value": value, "confidence": 0.88}
        except Exception as e:
            return {"success": False, "error": str(e), "confidence": 0.0}

    def click_next(self) -> dict:
        for label in ["Next", "Submit Application", "Continue"]:
            result = self.engine.click_button(label)
            if result["success"]:
                time.sleep(0.8)
                return result
        return {"success": False, "error": "Could not find Next button"}

    # TODO: After first observed Greenhouse application, document:
    # - resume upload flow (drag-and-drop vs file input)
    # - custom question types (multi-select, file upload)
    # - EEO section format
    # - confirmation page selector
