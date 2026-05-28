"""
helpers.py — Human-Like Interaction Primitives
===============================================
All interactions simulate real user behavior:
  - scroll into view before acting
  - hover, focus, then click
  - type with per-character delays
  - verify state after every action

NEVER call element.value = "..." directly.
ALWAYS use these helpers so events propagate correctly.
"""

from __future__ import annotations
import random
import time
from typing import Optional, Tuple
from playwright.sync_api import Page, Locator, TimeoutError as PWTimeout

from .confidence import InteractionConfidence
from .validation import FrontendValidator


# ── Typing speed profile (seconds per character) ────────────────────
_TYPING_PROFILES = {
    "human":  (0.04, 0.12),   # ~60–90 WPM with natural variation
    "fast":   (0.01, 0.03),   # fast but not robotic
    "instant": (0.0, 0.0),    # no delay — use only when speed matters more than realism
}


class InteractionHelpers:
    """
    Reusable human-simulation interaction primitives.
    Each method returns (success: bool, confidence: InteractionConfidence).
    """

    def __init__(self, page: Page, typing_profile: str = "human", debug: bool = False):
        self.page = page
        self.validator = FrontendValidator(page)
        self._profile = _TYPING_PROFILES.get(typing_profile, _TYPING_PROFILES["human"])
        self.debug = debug

    # ─────────────────────────────────────────────────────────────────
    # waitForHydration — ensure element is interactive before touching
    # ─────────────────────────────────────────────────────────────────

    def wait_for_hydration(self, locator: Locator, timeout_ms: int = 5000) -> Tuple[bool, str]:
        """Wait until element is visible, enabled, and not aria-busy."""
        try:
            locator.wait_for(state="visible", timeout=timeout_ms)
            locator.wait_for(state="enabled", timeout=timeout_ms)
            aria_busy = locator.get_attribute("aria-busy")
            if aria_busy == "true":
                time.sleep(0.5)
            return True, "hydrated"
        except Exception as e:
            return False, f"hydration timeout: {e}"

    def wait_for_stable_dom(self, wait_ms: int = 300) -> None:
        """Short pause to let micro-animations and React batched updates settle."""
        self.page.wait_for_load_state("domcontentloaded")
        time.sleep(wait_ms / 1000)

    # ─────────────────────────────────────────────────────────────────
    # clickVisibleElement — scroll, hover, click, verify
    # ─────────────────────────────────────────────────────────────────

    def click_visible_element(
        self,
        locator: Locator,
        label: str = "",
        verify_selector: Optional[str] = None,
        timeout_ms: int = 5000,
    ) -> Tuple[bool, InteractionConfidence]:
        """
        Scroll element into view → hover → click → verify visibility changed.
        """
        conf = InteractionConfidence(action="click", target=label or str(locator))

        # Hydration check
        hydrated, detail = self.wait_for_hydration(locator, timeout_ms)
        conf.add_signal("hydration_ready", hydrated, detail)
        if not hydrated:
            return False, conf.compute()

        try:
            # Scroll into view
            locator.scroll_into_view_if_needed(timeout=timeout_ms)
            time.sleep(0.1)

            # Hover first (human-like)
            locator.hover(timeout=timeout_ms)
            time.sleep(random.uniform(0.05, 0.15))

            # Click
            locator.click(timeout=timeout_ms)
            time.sleep(0.15)

            conf.add_signal("selector_stable", True, "click succeeded")

            # Verify something changed if a post-click selector given
            if verify_selector:
                visible, vdetail = self.validator.verify_element_visible(verify_selector, timeout_ms=2000)
                conf.add_signal("visual_state_changed", visible, vdetail)
                conf.add_signal("value_persisted", visible, vdetail)
                conf.add_signal("no_rerender_wipe", True, "no rerender check on click")
                conf.add_signal("validation_passed", True, "n/a")
            else:
                # No post-verify — assume success but score conservatively
                conf.add_signal("visual_state_changed", True, "assumed — no verify_selector given")
                conf.add_signal("value_persisted", True, "assumed")
                conf.add_signal("no_rerender_wipe", True, "assumed")
                conf.add_signal("validation_passed", True, "n/a")

            return True, conf.compute()

        except PWTimeout as e:
            conf.add_signal("selector_stable", False, f"timeout: {e}")
            conf.add_signal("visual_state_changed", False, "timeout before click")
            conf.add_signal("value_persisted", False, "")
            conf.add_signal("no_rerender_wipe", False, "")
            conf.add_signal("validation_passed", False, "")
            return False, conf.compute()
        except Exception as e:
            conf.add_signal("selector_stable", False, str(e))
            conf.add_signal("visual_state_changed", False, "")
            conf.add_signal("value_persisted", False, "")
            conf.add_signal("no_rerender_wipe", False, "")
            conf.add_signal("validation_passed", False, "")
            return False, conf.compute()

    # ─────────────────────────────────────────────────────────────────
    # typeHumanLike — focus, clear, type character-by-character
    # ─────────────────────────────────────────────────────────────────

    def type_human_like(
        self,
        locator: Locator,
        value: str,
        label: str = "",
        clear_first: bool = True,
        verify_after: bool = True,
    ) -> Tuple[bool, InteractionConfidence]:
        """
        Focus element → optional clear → type with human-like delays → verify value.
        """
        conf = InteractionConfidence(action="type", target=label or str(locator))

        hydrated, hdetail = self.wait_for_hydration(locator)
        conf.add_signal("hydration_ready", hydrated, hdetail)
        if not hydrated:
            return False, conf.compute()

        try:
            locator.scroll_into_view_if_needed()
            locator.click()  # focus
            time.sleep(0.1)

            if clear_first:
                locator.select_all()
                locator.press("Backspace")
                time.sleep(0.05)

            # Type character by character with natural timing
            min_delay, max_delay = self._profile
            for char in value:
                locator.type(char, delay=random.randint(
                    int(min_delay * 1000), max(int(max_delay * 1000), int(min_delay * 1000) + 1)
                ))

            # Tab away to trigger blur/change events
            locator.press("Tab")
            time.sleep(0.15)

            conf.add_signal("selector_stable", True, "typed successfully")

            if verify_after:
                # Focus back to read value
                locator.click()
                match, vdetail = self.validator.verify_input_value(locator, value)
                conf.add_signal("visual_state_changed", match, vdetail)

                persist, pdetail = self.validator.verify_value_persists(locator, value, wait_ms=400)
                conf.add_signal("value_persisted", persist, pdetail)

                stable, sdetail = self.validator.detect_rerender(locator)
                conf.add_signal("no_rerender_wipe", stable, sdetail)

                no_err, edetail = self.validator.verify_no_field_error(locator)
                conf.add_signal("validation_passed", no_err, edetail)
            else:
                conf.add_signal("visual_state_changed", True, "verify skipped")
                conf.add_signal("value_persisted", True, "verify skipped")
                conf.add_signal("no_rerender_wipe", True, "verify skipped")
                conf.add_signal("validation_passed", True, "verify skipped")

            return True, conf.compute()

        except Exception as e:
            for sig in ["selector_stable", "visual_state_changed", "value_persisted",
                        "no_rerender_wipe", "validation_passed"]:
                conf.add_signal(sig, False, str(e))
            return False, conf.compute()

    # ─────────────────────────────────────────────────────────────────
    # selectDropdownOption — native <select> with visible verification
    # ─────────────────────────────────────────────────────────────────

    def select_dropdown_option(
        self,
        locator: Locator,
        option_text: str,
        label: str = "",
    ) -> Tuple[bool, InteractionConfidence]:
        """Select an option in a native <select> and verify visible state."""
        conf = InteractionConfidence(action="select", target=label or str(locator))

        hydrated, hdetail = self.wait_for_hydration(locator)
        conf.add_signal("hydration_ready", hydrated, hdetail)
        if not hydrated:
            return False, conf.compute()

        try:
            locator.scroll_into_view_if_needed()
            locator.select_option(label=option_text)
            time.sleep(0.2)

            conf.add_signal("selector_stable", True, "select_option succeeded")

            match, vdetail = self.validator.verify_select_value(locator, option_text)
            conf.add_signal("visual_state_changed", match, vdetail)

            persist, pdetail = self.validator.verify_value_persists(locator, option_text,
                                                                     wait_ms=400, field_type="select")
            conf.add_signal("value_persisted", persist, pdetail)
            conf.add_signal("no_rerender_wipe", True, "native select — rerender rare")

            no_err, edetail = self.validator.verify_no_field_error(locator)
            conf.add_signal("validation_passed", no_err, edetail)

            return match, conf.compute()

        except Exception as e:
            for sig in ["selector_stable", "visual_state_changed", "value_persisted",
                        "no_rerender_wipe", "validation_passed"]:
                conf.add_signal(sig, False, str(e))
            return False, conf.compute()

    # ─────────────────────────────────────────────────────────────────
    # clickRadioByLabel — find radio by label text, click, verify
    # ─────────────────────────────────────────────────────────────────

    def click_radio_by_label(
        self,
        label_text: str,
        container_selector: str = "body",
    ) -> Tuple[bool, InteractionConfidence]:
        """
        Find a radio button by its adjacent label text, scroll to it, click it,
        then verify it is actually checked.
        """
        conf = InteractionConfidence(action="radio", target=label_text)

        try:
            # Strategy 1: label element containing text
            radio = (
                self.page.locator(container_selector)
                .get_by_label(label_text, exact=False)
                .first
            )
            if radio.count() == 0:
                # Strategy 2: label > input[type=radio]
                radio = (
                    self.page.locator(f"label:has-text('{label_text}') input[type=radio]")
                    .first
                )

            hydrated, hdetail = self.wait_for_hydration(radio)
            conf.add_signal("hydration_ready", hydrated, hdetail)
            if not hydrated:
                return False, conf.compute()

            radio.scroll_into_view_if_needed()
            radio.hover()
            time.sleep(0.08)
            radio.click()
            time.sleep(0.2)

            conf.add_signal("selector_stable", True, "radio found and clicked")

            checked, cdetail = self.validator.verify_radio_checked(radio)
            conf.add_signal("visual_state_changed", checked, cdetail)

            # Brief pause then re-check
            time.sleep(0.35)
            still_checked, pdetail = self.validator.verify_radio_checked(radio)
            conf.add_signal("value_persisted", still_checked, pdetail)
            conf.add_signal("no_rerender_wipe", still_checked, "recheck after 350ms")
            conf.add_signal("validation_passed", True, "n/a")

            return still_checked, conf.compute()

        except Exception as e:
            for sig in ["selector_stable", "visual_state_changed", "value_persisted",
                        "no_rerender_wipe", "validation_passed"]:
                conf.add_signal(sig, False, str(e))
            return False, conf.compute()

    # ─────────────────────────────────────────────────────────────────
    # safeRetryInteraction — wraps any helper with retry + escalation
    # ─────────────────────────────────────────────────────────────────

    def safe_retry_interaction(
        self,
        action_fn,
        max_retries: int = 2,
        wait_between_ms: int = 800,
    ) -> Tuple[bool, InteractionConfidence]:
        """
        Call action_fn() up to max_retries times.
        Stops early if confidence level is HIGH or MEDIUM on first success.
        Returns (success, final_confidence).
        """
        last_success = False
        last_conf = None
        for attempt in range(max_retries + 1):
            success, conf = action_fn()
            conf.retry_count = attempt
            conf.compute()
            last_success, last_conf = success, conf
            if success and not conf.should_escalate:
                return True, conf
            if conf.level.value == "FAILED" and attempt >= 1:
                break
            if attempt < max_retries:
                time.sleep(wait_between_ms / 1000)
        return last_success, last_conf

    # ─────────────────────────────────────────────────────────────────
    # validateFrontendState — full-page sanity check
    # ─────────────────────────────────────────────────────────────────

    def validate_frontend_state(self, expected_fields: dict) -> dict:
        """
        Validate multiple fields at once.
        expected_fields: {selector: expected_value, ...}
        Returns {selector: {passed, actual, expected}, ...}
        """
        results = {}
        for selector, expected in expected_fields.items():
            try:
                loc = self.page.locator(selector).first
                tag = loc.evaluate("el => el.tagName.toLowerCase()")
                if tag == "select":
                    passed, detail = self.validator.verify_select_value(loc, expected)
                elif tag == "input":
                    inp_type = loc.get_attribute("type") or "text"
                    if inp_type in ("radio", "checkbox"):
                        passed, detail = self.validator.verify_radio_checked(loc)
                    else:
                        passed, detail = self.validator.verify_input_value(loc, expected)
                else:
                    passed = expected.lower() in (loc.inner_text() or "").lower()
                    detail = f"text check: '{loc.inner_text()[:60]}'"
                results[selector] = {"passed": passed, "detail": detail, "expected": expected}
            except Exception as e:
                results[selector] = {"passed": False, "detail": str(e), "expected": expected}
        return results

    # ─────────────────────────────────────────────────────────────────
    # detectRerender — watch for DOM replacement
    # ─────────────────────────────────────────────────────────────────

    def detect_rerender(self, selector: str, wait_ms: int = 600) -> Tuple[bool, str]:
        """
        Check if element was replaced in the DOM (sign of React rerender wipe).
        Returns (stable, detail).
        """
        return self.validator.detect_rerender(
            self.page.locator(selector).first, wait_ms
        )
