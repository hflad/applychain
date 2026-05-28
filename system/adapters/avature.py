"""
avature.py — Avature ATS Adapter (Avature employer Careers and similar)
===========================================================
Avature uses React-controlled inputs. Standard form_input sets DOM
value but React state doesn't update. Requires native setter + event
dispatch to fire synthetic React events.

Observed at: Avature-hosted career portals
Known issues: radio buttons, custom comboboxes, work history fields.
"""

from __future__ import annotations
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine import HumanSimulationEngine

from .base import BaseATSAdapter


class AvatureAdapter(BaseATSAdapter):
    platform_name = "avature"
    url_patterns = [
        "careers.[company].com",
        "avature.net",
        "ibm.avature.net",
        "avature.com",
    ]

    # ── React-aware field setter ─────────────────────────────────────

    def set_react_value(self, selector: str, value: str) -> dict:
        """
        Set value on a React-controlled input by bypassing React's
        synthetic event system via the native setter.
        """
        try:
            result = self.page.evaluate(f"""
                (function() {{
                    const el = document.querySelector('{selector}');
                    if (!el) return {{success: false, error: 'element not found'}};
                    const nativeSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    )?.set;
                    if (nativeSetter) nativeSetter.call(el, '{value}');
                    else el.value = '{value}';
                    el.dispatchEvent(new Event('input',  {{bubbles: true}}));
                    el.dispatchEvent(new Event('change', {{bubbles: true}}));
                    el.dispatchEvent(new KeyboardEvent('keydown', {{bubbles: true}}));
                    el.dispatchEvent(new KeyboardEvent('keyup',   {{bubbles: true}}));
                    return {{success: true, value: el.value}};
                }})()
            """)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def fill_field(self, label: str, value: str) -> dict:
        """
        Avature override: use Playwright's fill() which fires proper events,
        then verify with a brief wait to catch React rerender wipes.
        """
        try:
            loc = self.page.get_by_label(label, exact=False).first
            loc.scroll_into_view_if_needed()
            loc.click()
            time.sleep(0.1)
            loc.fill(value)
            loc.press("Tab")
            time.sleep(0.4)  # React state update delay

            # Verify value persisted
            actual = loc.input_value(timeout=2000)
            success = value.lower() in actual.lower()
            if not success:
                # React wiped it — try again with keyboard events
                loc.click()
                loc.type(value, delay=50)
                loc.press("Tab")
                time.sleep(0.4)
                actual = loc.input_value(timeout=2000)
                success = value.lower() in actual.lower()

            return {"success": success, "expected": value, "actual": actual,
                    "confidence": 0.85 if success else 0.25}
        except Exception as e:
            return {"success": False, "error": str(e), "confidence": 0.0}

    # ── Radio buttons ────────────────────────────────────────────────

    def click_radio(self, label_text: str) -> dict:
        """
        Avature radio buttons sometimes need label click, not input click.
        Try both.
        """
        try:
            # Try label click first (more reliable in Avature)
            label = self.page.locator(f"label:has-text('{label_text}')").first
            if label.count() > 0:
                label.click()
                time.sleep(0.3)
                radio = label.locator("input[type=radio]")
                if radio.count() == 0:
                    radio = self.page.locator(f"input[type=radio][aria-label*='{label_text}']").first
                checked = radio.is_checked(timeout=1000) if radio.count() > 0 else False
                return {"success": checked, "method": "label_click", "confidence": 0.85 if checked else 0.2}

            # Fallback: direct radio click
            radio = self.page.get_by_label(label_text, exact=False).first
            radio.click()
            time.sleep(0.3)
            checked = radio.is_checked(timeout=1000)
            return {"success": checked, "method": "direct_click", "confidence": 0.75 if checked else 0.2}
        except Exception as e:
            return {"success": False, "error": str(e), "confidence": 0.0}

    # ── Custom combobox ──────────────────────────────────────────────

    def fill_autocomplete(self, container_id: str, value: str) -> dict:
        """
        Avature combobox: click to open, type to search, click result.
        """
        try:
            # Find combobox by aria-label or container
            combo = self.page.locator(f"[role='combobox'][aria-label*='{container_id}']").first
            if combo.count() == 0:
                combo = self.page.locator(f"[aria-label*='{container_id}']").first
            combo.click()
            time.sleep(0.5)

            # Type search term
            combo.type(value, delay=60)
            time.sleep(1.0)  # Avature search has AJAX delay

            # Click matching option
            option = self.page.get_by_role("option", name=value, exact=False).first
            option.wait_for(state="visible", timeout=4000)
            option.click()
            time.sleep(0.3)

            return {"success": True, "value": value, "confidence": 0.85}
        except Exception as e:
            return {"success": False, "error": str(e), "confidence": 0.0}

    def click_next(self) -> dict:
        for label in ["Next", "Continue", "Save and Continue"]:
            result = self.engine.click_button(label)
            if result["success"]:
                time.sleep(1.5)  # Avature pages load slowly
                return result
        return {"success": False, "error": "Could not find Next button"}
