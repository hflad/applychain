"""
verification.py — Interaction Verification Framework
======================================================
Detects whether browser interactions actually caused visible frontend state changes.
Platform-agnostic. Stateless. Reports facts only — never decides what to do next.

Design contract:
    Claude decides what to verify
        ↓
    Playwright executes the interaction
        ↓
    VerificationFramework reports what it observes
        ↓
    Claude evaluates the result and decides next action

Every method returns a VerificationResult:
    {
        "success":      bool,
        "confidence":   float (0.0–1.0),
        "observations": list[str],   # human-readable evidence trail
        "details":      dict         # raw signal data for Claude to inspect
    }

Rules:
    - Never raise exceptions — always return a result
    - Never take follow-up action based on what is found
    - Never log warnings or errors beyond what is in the result
    - Confidence reflects evidence quality, not a recommendation to proceed
    - Observations are terse facts, not instructions

Usage:
    from system.playwright_engine.verification import VerificationFramework

    vf = VerificationFramework(page)

    result = vf.verify_input_value(locator=page.get_by_label("First Name"), expected="Henry")
    # {"success": true, "confidence": 0.95, "observations": [...], "details": {...}}

    snapshot = vf.capture_verification_snapshot(label="after-fill-firstname")
    # {"success": true, "confidence": 1.0, "observations": [...], "details": {"path": "..."}}
"""

from __future__ import annotations

import json
import time
import datetime
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)


# ── Result type ──────────────────────────────────────────────────────────────

@dataclass
class VerificationResult:
    """
    Structured result returned by every verification primitive.

    success:      Whether the verification found what was expected.
    confidence:   How certain we are about the result (0.0–1.0).
                  Low confidence means evidence was ambiguous, not that the
                  interaction failed — Claude should interpret carefully.
    observations: Ordered list of terse factual observations gathered.
    details:      Raw signal data (values, attributes, timing, paths, etc.)
    """
    success: bool
    confidence: float
    observations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "confidence": round(self.confidence, 4),
            "observations": self.observations,
            "details": self.details,
        }


def _safe_run(fn, fallback_observation: str) -> VerificationResult:
    """
    Wrap any verification call so an unexpected exception never crashes the caller.
    Returns a low-confidence failure result with the exception detail.
    """
    try:
        return fn()
    except Exception as exc:
        logger.debug("verification exception: %s", exc, exc_info=True)
        return VerificationResult(
            success=False,
            confidence=0.1,
            observations=[fallback_observation, f"exception: {exc}"],
            details={"exception": str(exc)},
        )


# ── Framework ────────────────────────────────────────────────────────────────

class VerificationFramework:
    """
    Platform-agnostic interaction verification primitives.

    All methods are read-only observers. They never click, type, scroll,
    or trigger side effects. They return VerificationResult.to_dict() so
    the caller (Claude) receives plain JSON-serialisable data.

    Instantiate once per page connection and reuse across verifications.
    """

    # Where snapshots are saved. Resolved relative to the workspace root.
    DEFAULT_SNAPSHOT_DIR = Path(__file__).resolve().parents[2] / "logs" / "verification_snapshots"

    def __init__(self, page: Page, snapshot_dir: Optional[Path] = None):
        """
        Args:
            page:         Connected Playwright Page object.
            snapshot_dir: Override where capture_verification_snapshot saves files.
        """
        self.page = page
        self.snapshot_dir = Path(snapshot_dir) if snapshot_dir else self.DEFAULT_SNAPSHOT_DIR
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. verify_text_present ───────────────────────────────────────────────

    def verify_text_present(
        self,
        expected_text: str,
        *,
        exact: bool = False,
        timeout_ms: int = 3000,
        search_selector: str = "body",
    ) -> dict:
        """
        Confirm that expected_text is visible somewhere on the page.

        Args:
            expected_text:    The text to look for.
            exact:            If True, requires an exact string match.
            timeout_ms:       How long to wait for the text to appear (ms).
            search_selector:  Narrow the search to a CSS selector subtree.

        Returns VerificationResult where:
            success=True  → text found and visible
            success=False → text not found within timeout, or page unreadable
        """
        def _run() -> VerificationResult:
            observations = []
            details: dict[str, Any] = {
                "expected_text": expected_text,
                "exact": exact,
                "search_selector": search_selector,
                "timeout_ms": timeout_ms,
            }

            container = self.page.locator(search_selector)

            # Check visibility
            try:
                locator = container.get_by_text(expected_text, exact=exact).first
                locator.wait_for(state="visible", timeout=timeout_ms)
                observations.append(f"text '{expected_text}' is visible on page")

                # Capture surrounding context for Claude to inspect
                try:
                    parent_text = locator.locator("xpath=ancestor::*[1]").inner_text(timeout=500)
                    details["surrounding_context"] = parent_text[:200]
                except Exception:
                    pass

                return VerificationResult(
                    success=True,
                    confidence=0.97,
                    observations=observations,
                    details=details,
                )

            except Exception:
                # Text not visible — check if it exists in DOM but hidden
                try:
                    hidden_count = container.get_by_text(expected_text, exact=exact).count()
                    if hidden_count > 0:
                        observations.append(
                            f"text '{expected_text}' exists in DOM ({hidden_count} instance(s)) but is not visible"
                        )
                        details["dom_count"] = hidden_count
                        details["visible"] = False
                        return VerificationResult(
                            success=False,
                            confidence=0.85,
                            observations=observations,
                            details=details,
                        )
                except Exception:
                    pass

                observations.append(f"text '{expected_text}' not found on page within {timeout_ms}ms")
                details["visible"] = False
                details["dom_count"] = 0
                return VerificationResult(
                    success=False,
                    confidence=0.90,
                    observations=observations,
                    details=details,
                )

        return _safe_run(_run, f"verify_text_present failed for '{expected_text}'").to_dict()

    # ── 2. verify_radio_selected ─────────────────────────────────────────────

    def verify_radio_selected(
        self,
        locator: Locator,
        *,
        label_text: Optional[str] = None,
    ) -> dict:
        """
        Confirm a radio button is visually and semantically selected.

        Inspects:
            - .is_checked() (Playwright native)
            - DOM .checked property
            - aria-checked attribute
            - Visual :checked CSS pseudo-class

        Args:
            locator:     Playwright Locator pointing to the radio <input>.
            label_text:  Optional human label — included in observations for clarity.

        Returns VerificationResult where:
            success=True  → all available signals agree the radio is selected
            success=False → radio is not selected, or signals are contradictory
        """
        def _run() -> VerificationResult:
            observations = []
            details: dict[str, Any] = {"label_text": label_text}
            signals: dict[str, Optional[bool]] = {}

            # Signal 1: Playwright is_checked
            try:
                pw_checked = locator.is_checked(timeout=2000)
                signals["playwright_is_checked"] = pw_checked
                observations.append(f"playwright is_checked={pw_checked}")
            except Exception as e:
                signals["playwright_is_checked"] = None
                observations.append(f"playwright is_checked unavailable: {e}")

            # Signal 2: DOM .checked property
            try:
                dom_checked = locator.evaluate("el => el.checked")
                signals["dom_checked_property"] = dom_checked
                observations.append(f"DOM .checked property={dom_checked}")
            except Exception as e:
                signals["dom_checked_property"] = None
                observations.append(f"DOM .checked unavailable: {e}")

            # Signal 3: aria-checked attribute
            try:
                aria = locator.get_attribute("aria-checked")
                aria_val = aria.lower() == "true" if aria else None
                signals["aria_checked"] = aria_val
                if aria is not None:
                    observations.append(f"aria-checked='{aria}'")
                else:
                    observations.append("aria-checked attribute not present")
            except Exception as e:
                signals["aria_checked"] = None
                observations.append(f"aria-checked unavailable: {e}")

            # Signal 4: :checked CSS pseudo-class
            try:
                css_checked = locator.evaluate("el => el.matches(':checked')")
                signals["css_pseudo_checked"] = css_checked
                observations.append(f"CSS :checked pseudo-class matched={css_checked}")
            except Exception as e:
                signals["css_pseudo_checked"] = None
                observations.append(f"CSS :checked unavailable: {e}")

            details["signals"] = signals

            # Evaluate: ignore None signals (unavailable), look at what we have
            available = {k: v for k, v in signals.items() if v is not None}

            if not available:
                return VerificationResult(
                    success=False,
                    confidence=0.1,
                    observations=observations + ["no signals available — cannot verify"],
                    details=details,
                )

            true_count = sum(1 for v in available.values() if v is True)
            false_count = sum(1 for v in available.values() if v is False)
            all_agree = false_count == 0 or true_count == 0
            selected = true_count > false_count

            # Confidence: higher when signals agree, lower when contradictory
            if all_agree and len(available) >= 2:
                confidence = 0.97
            elif all_agree and len(available) == 1:
                confidence = 0.80
            else:
                confidence = 0.55  # contradictory signals — Claude should inspect
                observations.append(
                    f"contradictory signals: {true_count} say selected, {false_count} say not selected"
                )

            if selected:
                observations.append(
                    f"radio {'(' + label_text + ') ' if label_text else ''}appears selected"
                )
            else:
                observations.append(
                    f"radio {'(' + label_text + ') ' if label_text else ''}does not appear selected"
                )

            return VerificationResult(
                success=selected,
                confidence=confidence,
                observations=observations,
                details=details,
            )

        return _safe_run(_run, "verify_radio_selected failed unexpectedly").to_dict()

    # ── 3. verify_dropdown_value ─────────────────────────────────────────────

    def verify_dropdown_value(
        self,
        locator: Locator,
        expected_value: str,
        *,
        rerender_wait_ms: int = 600,
        field_label: Optional[str] = None,
    ) -> dict:
        """
        Confirm the expected value persisted in a dropdown after selection.

        Handles:
            - Native <select> elements
            - Custom combobox / ARIA listbox patterns
            - React rerender reset detection (checks value again after a wait)

        Args:
            locator:          Locator pointing to the dropdown element.
            expected_value:   The value that should be selected.
            rerender_wait_ms: How long to wait before re-checking (catches rerender resets).
            field_label:      Optional human label for observation clarity.

        Returns VerificationResult where:
            success=True  → expected value present immediately AND after rerender wait
            success=False → value missing, wrong, or was reset by rerender
        """
        def _run() -> VerificationResult:
            observations = []
            details: dict[str, Any] = {
                "expected_value": expected_value,
                "field_label": field_label,
                "rerender_wait_ms": rerender_wait_ms,
            }

            def _read_value() -> tuple[str, str]:
                """Returns (method_used, actual_value)."""
                tag = locator.evaluate("el => el.tagName.toLowerCase()")

                if tag == "select":
                    val = locator.evaluate(
                        "el => el.options[el.selectedIndex]?.text || el.value || ''"
                    )
                    return "native_select", val

                # ARIA combobox / custom dropdown
                for attr in ("aria-label", "value", "textContent"):
                    try:
                        if attr == "textContent":
                            val = locator.inner_text(timeout=500).strip()
                        else:
                            val = locator.get_attribute(attr) or ""
                        if val:
                            return f"aria_{attr}", val
                    except Exception:
                        continue

                # Fallback: read visible text of the selected-item container
                for sel in (
                    "[class*='selected']",
                    "[class*='value']",
                    "[aria-selected='true']",
                ):
                    try:
                        child = locator.locator(sel).first
                        val = child.inner_text(timeout=300).strip()
                        if val:
                            return f"child_{sel}", val
                    except Exception:
                        continue

                return "unknown", ""

            # Initial read
            method, initial_value = _read_value()
            details["read_method"] = method
            details["value_initial"] = initial_value
            initial_match = expected_value.lower() in initial_value.lower()
            observations.append(
                f"initial read via {method}: '{initial_value}' "
                f"{'matches' if initial_match else 'does NOT match'} expected '{expected_value}'"
            )

            # Rerender check — wait then re-read
            time.sleep(rerender_wait_ms / 1000)
            _, post_wait_value = _read_value()
            details["value_post_rerender_wait"] = post_wait_value
            post_match = expected_value.lower() in post_wait_value.lower()

            if initial_match and not post_match:
                observations.append(
                    f"RERENDER RESET DETECTED: value changed from '{initial_value}' "
                    f"to '{post_wait_value}' after {rerender_wait_ms}ms wait"
                )
                details["rerender_reset"] = True
                return VerificationResult(
                    success=False,
                    confidence=0.93,
                    observations=observations,
                    details=details,
                )

            details["rerender_reset"] = False
            if post_match:
                observations.append(
                    f"value '{post_wait_value}' stable after {rerender_wait_ms}ms"
                )

            success = initial_match and post_match
            confidence = 0.95 if success else (0.88 if not initial_match else 0.50)
            return VerificationResult(
                success=success,
                confidence=confidence,
                observations=observations,
                details=details,
            )

        return _safe_run(_run, f"verify_dropdown_value failed for '{expected_value}'").to_dict()

    # ── 4. verify_input_value ────────────────────────────────────────────────

    def verify_input_value(
        self,
        locator: Locator,
        expected_value: str,
        *,
        hydration_wait_ms: int = 500,
        field_label: Optional[str] = None,
    ) -> dict:
        """
        Confirm typed text remains in an input after hydration / rerender.

        Checks:
            - Immediate value via input_value()
            - DOM .value property
            - aria-label or placeholder for field identity confirmation
            - Value stability after a hydration wait

        Args:
            locator:           Locator pointing to the <input> or <textarea>.
            expected_value:    The text that should be in the field.
            hydration_wait_ms: Wait before re-checking (catches post-hydration resets).
            field_label:       Optional human label for observation clarity.

        Returns VerificationResult where:
            success=True  → expected text present immediately AND after hydration wait
            success=False → text missing, truncated, or reset
        """
        def _run() -> VerificationResult:
            observations = []
            details: dict[str, Any] = {
                "expected_value": expected_value,
                "field_label": field_label,
                "hydration_wait_ms": hydration_wait_ms,
            }

            # Signal 1: Playwright input_value
            try:
                pw_value = locator.input_value(timeout=2000)
                details["value_playwright"] = pw_value
                pw_match = expected_value.lower() in pw_value.lower()
                observations.append(
                    f"playwright input_value='{pw_value}' "
                    f"({'match' if pw_match else 'NO MATCH'})"
                )
            except Exception as e:
                pw_value = None
                pw_match = False
                observations.append(f"playwright input_value unavailable: {e}")
                details["value_playwright"] = None

            # Signal 2: DOM .value property
            try:
                dom_value = locator.evaluate("el => el.value || ''")
                details["value_dom"] = dom_value
                dom_match = expected_value.lower() in dom_value.lower()
                if dom_value != pw_value:
                    observations.append(
                        f"DOM .value='{dom_value}' differs from playwright read "
                        f"({'match' if dom_match else 'NO MATCH'})"
                    )
            except Exception as e:
                dom_value = None
                dom_match = pw_match
                observations.append(f"DOM .value unavailable: {e}")
                details["value_dom"] = None

            # Signal 3: Field identity — confirm we're reading the right field
            try:
                placeholder = locator.get_attribute("placeholder") or ""
                aria_label = locator.get_attribute("aria-label") or ""
                details["field_identity"] = {
                    "placeholder": placeholder,
                    "aria_label": aria_label,
                }
            except Exception:
                pass

            initial_match = pw_match or (dom_value is not None and dom_match)

            # Hydration wait then re-check
            time.sleep(hydration_wait_ms / 1000)
            try:
                post_value = locator.input_value(timeout=1500)
                details["value_post_hydration"] = post_value
                post_match = expected_value.lower() in post_value.lower()

                if initial_match and not post_match:
                    observations.append(
                        f"POST-HYDRATION RESET: value changed from '{pw_value}' "
                        f"to '{post_value}' after {hydration_wait_ms}ms"
                    )
                    details["hydration_reset"] = True
                    return VerificationResult(
                        success=False,
                        confidence=0.92,
                        observations=observations,
                        details=details,
                    )

                details["hydration_reset"] = False
                if post_match:
                    observations.append(
                        f"value stable after {hydration_wait_ms}ms hydration wait"
                    )

            except Exception as e:
                post_match = initial_match
                observations.append(f"post-hydration recheck unavailable: {e}")
                details["value_post_hydration"] = None
                details["hydration_reset"] = None

            success = initial_match and post_match
            if success:
                confidence = 0.95
            elif initial_match:
                confidence = 0.60  # passed initial but post-hydration uncertain
            else:
                confidence = 0.90  # confidently wrong
            observations.append(
                f"field {'(' + field_label + ') ' if field_label else ''}"
                f"{'contains' if success else 'does NOT contain'} expected value"
            )

            return VerificationResult(
                success=success,
                confidence=confidence,
                observations=observations,
                details=details,
            )

        return _safe_run(_run, f"verify_input_value failed for '{expected_value}'").to_dict()

    # ── 5. verify_submit_enabled ─────────────────────────────────────────────

    def verify_submit_enabled(
        self,
        *,
        submit_selector: str = "button[type='submit']",
        also_check_text: Optional[list[str]] = None,
    ) -> dict:
        """
        Determine whether a submit / next / continue button became enabled.

        This is a proxy for overall form validity — most ATS platforms disable
        the submit button until all required fields are filled correctly.

        Inspects:
            - disabled attribute / property
            - aria-disabled
            - CSS pointer-events: none (visual-only disable pattern)
            - Button visibility

        Args:
            submit_selector:  CSS selector for the primary submit button.
                              Falls back to common text patterns if not found.
            also_check_text:  Additional button text patterns to check
                              (e.g. ["Next", "Continue", "Save and Continue"]).

        Returns VerificationResult where:
            success=True  → at least one matching submit-like button is enabled
            success=False → all found buttons are disabled, or none found
        """
        def _run() -> VerificationResult:
            observations = []
            details: dict[str, Any] = {
                "submit_selector": submit_selector,
                "also_check_text": also_check_text or [],
            }
            buttons_checked: list[dict] = []

            fallback_texts = also_check_text or ["Next", "Submit", "Submit Application", "Continue", "Save"]

            def _check_button(loc, label: str) -> Optional[dict]:
                try:
                    if not loc.is_visible(timeout=1000):
                        return None
                    disabled_attr = loc.get_attribute("disabled")
                    aria_disabled = loc.get_attribute("aria-disabled")
                    dom_disabled = loc.evaluate("el => el.disabled")
                    pointer_events = loc.evaluate(
                        "el => getComputedStyle(el).pointerEvents"
                    )
                    is_disabled = (
                        disabled_attr is not None
                        or dom_disabled is True
                        or (aria_disabled or "").lower() == "true"
                        or pointer_events == "none"
                    )
                    btn_text = loc.inner_text(timeout=500).strip()
                    return {
                        "label": label,
                        "button_text": btn_text,
                        "disabled": is_disabled,
                        "disabled_attr": disabled_attr,
                        "aria_disabled": aria_disabled,
                        "dom_disabled": dom_disabled,
                        "pointer_events": pointer_events,
                    }
                except Exception:
                    return None

            # Try primary selector
            try:
                info = _check_button(self.page.locator(submit_selector).first, submit_selector)
                if info:
                    buttons_checked.append(info)
            except Exception:
                pass

            # Try fallback text patterns
            for text in fallback_texts:
                try:
                    btn_loc = self.page.get_by_role("button", name=text, exact=False).first
                    info = _check_button(btn_loc, f"button[text~='{text}']")
                    if info:
                        buttons_checked.append(info)
                except Exception:
                    continue

            details["buttons_checked"] = buttons_checked

            if not buttons_checked:
                observations.append("no submit-like buttons found on page")
                return VerificationResult(
                    success=False,
                    confidence=0.70,
                    observations=observations,
                    details=details,
                )

            enabled_buttons = [b for b in buttons_checked if not b["disabled"]]
            disabled_buttons = [b for b in buttons_checked if b["disabled"]]

            for b in enabled_buttons:
                observations.append(f"button '{b['button_text']}' is ENABLED")
            for b in disabled_buttons:
                observations.append(
                    f"button '{b['button_text']}' is DISABLED "
                    f"(disabled_attr={b['disabled_attr']}, "
                    f"aria_disabled={b['aria_disabled']}, "
                    f"pointer_events={b['pointer_events']})"
                )

            success = len(enabled_buttons) > 0
            confidence = 0.95 if buttons_checked else 0.50
            return VerificationResult(
                success=success,
                confidence=confidence,
                observations=observations,
                details=details,
            )

        return _safe_run(_run, "verify_submit_enabled failed unexpectedly").to_dict()

    # ── 6. capture_verification_snapshot ────────────────────────────────────

    def capture_verification_snapshot(
        self,
        label: str = "snapshot",
        *,
        include_dom_excerpt: bool = True,
        dom_selector: str = "body",
    ) -> dict:
        """
        Save a point-in-time record of the page state for Claude to inspect.

        Captures:
            - Screenshot (PNG)
            - Current URL
            - Page title
            - Timestamp (ISO 8601)
            - Basic page diagnostics (form count, input count, visible errors)
            - Optional DOM excerpt of a specific selector

        All files are saved to logs/verification_snapshots/{label}_{timestamp}/

        Args:
            label:              Human-readable label for this snapshot point.
            include_dom_excerpt: Whether to save a DOM excerpt.
            dom_selector:       Which part of the DOM to excerpt.

        Returns VerificationResult where:
            success=True  → snapshot saved successfully
            details contain all saved paths and page diagnostics
        """
        def _run() -> VerificationResult:
            observations = []
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            slug = label.lower().replace(" ", "_").replace("/", "-")
            snap_dir = self.snapshot_dir / f"{slug}_{ts}"
            snap_dir.mkdir(parents=True, exist_ok=True)

            details: dict[str, Any] = {
                "label": label,
                "timestamp_iso": datetime.datetime.now().isoformat(),
                "snapshot_dir": str(snap_dir),
            }

            # URL + title
            try:
                details["url"] = self.page.url
                details["title"] = self.page.title()
                observations.append(f"URL: {details['url']}")
                observations.append(f"title: '{details['title']}'")
            except Exception as e:
                observations.append(f"could not read URL/title: {e}")

            # Screenshot
            screenshot_path = snap_dir / "screenshot.png"
            try:
                self.page.screenshot(path=str(screenshot_path), full_page=False)
                details["screenshot_path"] = str(screenshot_path)
                observations.append(f"screenshot saved: {screenshot_path.name}")
            except Exception as e:
                details["screenshot_path"] = None
                observations.append(f"screenshot failed: {e}")

            # Page diagnostics
            try:
                diagnostics = self.page.evaluate("""() => {
                    const forms = document.querySelectorAll('form');
                    const inputs = document.querySelectorAll('input:not([type=hidden]), select, textarea');
                    const visibleErrors = Array.from(
                        document.querySelectorAll(
                            '[class*="error"],[class*="invalid"],[aria-invalid="true"]'
                        )
                    ).filter(el => {
                        const style = getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    }).map(el => el.innerText?.trim()).filter(Boolean).slice(0, 5);

                    const submitBtns = Array.from(
                        document.querySelectorAll('button[type=submit], input[type=submit]')
                    ).map(el => ({
                        text: (el.innerText || el.value || '').trim(),
                        disabled: el.disabled
                    }));

                    return {
                        form_count: forms.length,
                        visible_input_count: inputs.length,
                        visible_errors: visibleErrors,
                        submit_buttons: submitBtns
                    };
                }""")
                details["page_diagnostics"] = diagnostics
                observations.append(
                    f"forms={diagnostics['form_count']}, "
                    f"visible_inputs={diagnostics['visible_input_count']}, "
                    f"visible_errors={len(diagnostics.get('visible_errors', []))}"
                )
                if diagnostics.get("visible_errors"):
                    observations.append(
                        f"visible error text on page: {diagnostics['visible_errors']}"
                    )
            except Exception as e:
                observations.append(f"page diagnostics unavailable: {e}")
                details["page_diagnostics"] = None

            # DOM excerpt
            if include_dom_excerpt:
                dom_path = snap_dir / "dom_excerpt.html"
                try:
                    dom_html = self.page.locator(dom_selector).first.inner_html(timeout=2000)
                    # Trim to 50KB to keep files manageable
                    if len(dom_html) > 50_000:
                        dom_html = dom_html[:50_000] + "\n<!-- truncated -->"
                    dom_path.write_text(dom_html, encoding="utf-8")
                    details["dom_excerpt_path"] = str(dom_path)
                    observations.append(f"DOM excerpt saved: {dom_path.name}")
                except Exception as e:
                    details["dom_excerpt_path"] = None
                    observations.append(f"DOM excerpt unavailable: {e}")

            # Save machine-readable summary
            summary_path = snap_dir / "summary.json"
            try:
                summary_path.write_text(
                    json.dumps(
                        {
                            "label": label,
                            "timestamp": details["timestamp_iso"],
                            "url": details.get("url"),
                            "title": details.get("title"),
                            "diagnostics": details.get("page_diagnostics"),
                            "observations": observations,
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                details["summary_path"] = str(summary_path)
            except Exception as e:
                observations.append(f"summary.json save failed: {e}")
                details["summary_path"] = None

            return VerificationResult(
                success=details.get("screenshot_path") is not None,
                confidence=1.0,
                observations=observations,
                details=details,
            )

        return _safe_run(_run, f"capture_verification_snapshot failed for label='{label}'").to_dict()
