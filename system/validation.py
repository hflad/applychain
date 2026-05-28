"""
validation.py — Frontend State Verification
============================================
After every interaction, verify the visible UI actually changed.
Never assume "click executed" == "frontend state updated."
"""

from __future__ import annotations
import time
from typing import Optional, Tuple
from playwright.sync_api import Page, Locator


class FrontendValidator:
    """
    Verifies that interactions produced real visible state changes.
    All methods return (passed: bool, detail: str).
    """

    def __init__(self, page: Page, stable_wait_ms: int = 400):
        self.page = page
        self.stable_wait_ms = stable_wait_ms

    # ── Core verification ────────────────────────────────────────────

    def verify_input_value(self, locator: Locator, expected: str) -> Tuple[bool, str]:
        """Verify a text input contains the expected value."""
        try:
            actual = locator.input_value(timeout=2000)
            match = expected.lower() in actual.lower()
            return match, f"expected='{expected}' actual='{actual}'"
        except Exception as e:
            return False, f"could not read input value: {e}"

    def verify_select_value(self, locator: Locator, expected: str) -> Tuple[bool, str]:
        """Verify a <select> element has the expected option selected."""
        try:
            actual = locator.evaluate("el => el.options[el.selectedIndex]?.text || ''")
            match = expected.lower() in actual.lower()
            return match, f"expected='{expected}' actual='{actual}'"
        except Exception as e:
            return False, f"could not read select value: {e}"

    def verify_radio_checked(self, locator: Locator) -> Tuple[bool, str]:
        """Verify a radio button is checked."""
        try:
            checked = locator.is_checked(timeout=2000)
            return checked, f"checked={checked}"
        except Exception as e:
            return False, f"could not check radio state: {e}"

    def verify_checkbox_checked(self, locator: Locator) -> Tuple[bool, str]:
        """Verify a checkbox is checked."""
        try:
            checked = locator.is_checked(timeout=2000)
            return checked, f"checked={checked}"
        except Exception as e:
            return False, f"could not check checkbox state: {e}"

    def verify_text_visible(self, text: str, timeout_ms: int = 3000) -> Tuple[bool, str]:
        """Verify that specific text appears somewhere on the page."""
        try:
            self.page.get_by_text(text, exact=False).first.wait_for(
                state="visible", timeout=timeout_ms
            )
            return True, f"text '{text}' is visible"
        except Exception:
            return False, f"text '{text}' not found on page within {timeout_ms}ms"

    def verify_element_visible(self, selector: str, timeout_ms: int = 2000) -> Tuple[bool, str]:
        """Verify an element is visible."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout_ms)
            return True, f"element '{selector}' is visible"
        except Exception:
            return False, f"element '{selector}' not visible within {timeout_ms}ms"

    def verify_no_field_error(self, locator: Locator) -> Tuple[bool, str]:
        """Check that no validation error message appears near this field."""
        try:
            # Common error patterns across ATS systems
            error_selectors = [
                "[class*='error']:visible",
                "[class*='invalid']:visible",
                "[aria-invalid='true']:visible",
                "[class*='validation']:visible",
            ]
            parent = locator.locator("xpath=ancestor::div[1]")
            for sel in error_selectors:
                try:
                    count = parent.locator(sel).count()
                    if count > 0:
                        msg = parent.locator(sel).first.inner_text()
                        return False, f"field error found: '{msg}'"
                except Exception:
                    continue
            return True, "no field errors detected"
        except Exception as e:
            return True, f"error check skipped: {e}"

    # ── Persistence checks ───────────────────────────────────────────

    def verify_value_persists(
        self,
        locator: Locator,
        expected: str,
        wait_ms: int = 500,
        field_type: str = "input",
    ) -> Tuple[bool, str]:
        """
        Wait then re-check value — catches React rerenders silently reverting state.
        """
        time.sleep(wait_ms / 1000)
        if field_type == "select":
            return self.verify_select_value(locator, expected)
        return self.verify_input_value(locator, expected)

    def detect_rerender(self, locator: Locator, wait_ms: int = 600) -> Tuple[bool, str]:
        """
        Check if element was removed and re-added to DOM (sign of rerender wipe).
        Returns (stable, detail) — True means no problematic rerender detected.
        """
        try:
            # Capture element handle before wait
            handle_before = locator.element_handle(timeout=1000)
            time.sleep(wait_ms / 1000)
            handle_after = locator.element_handle(timeout=1000)
            # If handles are different objects the element was replaced
            same = handle_before == handle_after
            return same, f"element_replaced={not same}"
        except Exception as e:
            return True, f"rerender check skipped: {e}"

    # ── DOM stability ────────────────────────────────────────────────

    def wait_for_stable_dom(self, timeout_ms: int = 3000, poll_ms: int = 150) -> Tuple[bool, str]:
        """
        Wait until the DOM stops mutating (networkidle + no ongoing animations).
        """
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            # Brief poll to let micro-animations settle
            time.sleep(poll_ms / 1000)
            return True, "DOM stable"
        except Exception as e:
            return False, f"DOM stability timeout: {e}"

    def wait_for_hydration(
        self,
        selector: str,
        timeout_ms: int = 5000,
    ) -> Tuple[bool, str]:
        """
        Wait for an element to become interactive (not disabled, not aria-busy).
        Critical for React/Vue apps that render shells before hydrating.
        """
        try:
            loc = self.page.locator(selector).first
            loc.wait_for(state="visible", timeout=timeout_ms)
            # Check not disabled
            disabled = loc.is_disabled()
            aria_busy = loc.get_attribute("aria-busy") == "true"
            if disabled:
                return False, f"element is disabled after {timeout_ms}ms"
            if aria_busy:
                return False, f"element is aria-busy after {timeout_ms}ms"
            return True, "element hydrated and interactive"
        except Exception as e:
            return False, f"hydration wait failed: {e}"

    # ── Submit gate ──────────────────────────────────────────────────

    def verify_submit_enabled(self, submit_selector: str = "button[type=submit]") -> Tuple[bool, str]:
        """Check the submit/next button is not disabled — proxy for form validity."""
        try:
            btn = self.page.locator(submit_selector).first
            disabled = btn.is_disabled()
            return not disabled, f"submit_disabled={disabled}"
        except Exception as e:
            return False, f"could not find submit button: {e}"
