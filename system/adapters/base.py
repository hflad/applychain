"""
base.py — BaseATSAdapter
========================
All ATS adapters inherit from this. Override methods to handle
platform-specific quirks (Select2 fields, React rerenders,
hydration delays, custom dropdowns, etc.)
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..engine import HumanSimulationEngine


class BaseATSAdapter:
    """
    Base class for ATS-specific interaction overrides.
    The engine calls adapter methods first; base implementations
    fall through to the generic helpers.
    """

    platform_name: str = "generic"
    url_patterns: list[str] = []  # URL substrings that identify this ATS

    def __init__(self, engine: "HumanSimulationEngine"):
        self.engine = engine

    @property
    def page(self):
        return self.engine.page

    @property
    def helpers(self):
        return self.engine._helpers

    # ── Lifecycle hooks ──────────────────────────────────────────────

    def on_page_load(self) -> None:
        """Called once after connecting. Override to wait for hydration etc."""
        pass

    def before_section(self, section: str) -> None:
        """Called before filling each form section (education, experience, etc.)."""
        # Default: audit for Add Another buttons and log
        result = self.engine.audit_add_another_buttons()
        if result["count"] > 0:
            print(f"[{self.platform_name}] Add Another buttons found: {result['found']}")

    # ── Field interaction overrides ──────────────────────────────────

    def fill_autocomplete(self, container_id: str, value: str) -> dict:
        """
        Fill a custom autocomplete field (Select2, Chosen, etc.).
        Base implementation: type into the field and pick first result.
        ATS-specific adapters override this with platform-specific event chains.
        """
        raise NotImplementedError(
            f"{self.platform_name} does not implement fill_autocomplete. "
            "Override this in the platform adapter."
        )

    def fill_date(self, label: str, month: int, year: int, day: Optional[int] = None) -> dict:
        """Fill a date field. Override for ATS-specific date pickers."""
        # Generic: try typing MM/YYYY or MM/DD/YYYY
        value = f"{month:02d}/{year}" if day is None else f"{month:02d}/{day:02d}/{year}"
        return self.engine.fill_field(label=label, value=value)

    def handle_employer_dropdown(self, company_name: str) -> dict:
        """
        Handle employer/company field. If company not in dropdown,
        fall back to "Other" and fill the text input.
        """
        # Try to select directly
        result = self.engine.select_option(label="Employer", value=company_name)
        if result["success"] and result["confidence"] > 0.6:
            return result
        # Fall back to "Other"
        other_result = self.engine.select_option(label="Employer", value="Other")
        if other_result["success"]:
            # Fill the text input that should appear
            text_result = self.engine.fill_field(label="Employer Name", value=company_name)
            if not text_result["success"]:
                text_result = self.engine.fill_field(label="Company", value=company_name)
            return {**other_result, "used_other": True, "company_name_filled": text_result["success"]}
        return {"success": False, "error": f"Could not set employer to '{company_name}'"}

    # ── Form navigation ──────────────────────────────────────────────

    def click_next(self) -> dict:
        """Click the Next / Continue / Save & Continue button."""
        for label in ["Next", "Continue", "Save and Continue", "Save & Continue", "Next Step"]:
            result = self.engine.click_button(label)
            if result["success"]:
                self.engine.wait_stable(600)
                return result
        return {"success": False, "error": "Could not find Next button"}

    def click_submit(self) -> dict:
        """Click the final Submit button — only called after explicit human approval."""
        return self.engine.click_button("Submit")

    # ── EEO / compliance defaults ────────────────────────────────────

    def fill_eeo_defaults(self) -> dict:
        """Fill EEO/diversity questions with stored defaults. Override per ATS."""
        return {"success": True, "note": "EEO defaults not implemented for this ATS"}

    # ── Diagnostics ──────────────────────────────────────────────────

    def diagnose(self) -> dict:
        """Return diagnostic info about the current page state."""
        return {
            "platform": self.platform_name,
            "url": self.page.url,
            "title": self.page.title(),
            "add_another_buttons": self.engine.audit_add_another_buttons(),
        }
