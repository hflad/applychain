"""
taleo.py — Taleo ATS Adapter (apply.[company].com and similar)
=============================================================
Taleo uses Select2 jQuery autocomplete components that don't respond
to standard click+type. Requires a specific mousedown→search→pointer
event chain to open dropdowns and select values.

Observed at: Taleo-hosted career portals (e.g. apply.[company].com)
"""

from __future__ import annotations
import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..engine import HumanSimulationEngine

from .base import BaseATSAdapter


class TaleoAdapter(BaseATSAdapter):
    platform_name = "taleo"
    url_patterns = [
        "apply.[company].com",
        "taleo.net",
        "tbe.taleo.net",
        "career.deloitte",
        "/careers/Register",
        "/careers/ApplicationFlow",
    ]

    # ── Select2 autocomplete ─────────────────────────────────────────

    def fill_autocomplete(self, container_id: str, value: str) -> dict:
        """
        Fill a Taleo Select2 autocomplete field.
        container_id: e.g. '6074-1-sample' (from class 'select2Container6074-1-sample')
        value: text to search for, e.g. 'Miami University'
        """
        page = self.page
        try:
            # 1. Open the dropdown via mousedown event
            page.evaluate(f"""
                const span = document.querySelector('.select2Container{container_id}');
                if (span) span.dispatchEvent(
                    new MouseEvent('mousedown', {{bubbles: true, cancelable: true, view: window}})
                );
            """)
            time.sleep(0.3)

            # 2. Wait for the search input to appear
            search_input = page.locator(".select2-search__field").first
            search_input.wait_for(state="visible", timeout=3000)

            # 3. Type the search term
            search_input.fill(value)
            page.evaluate("""
                const inp = document.querySelector('.select2-search__field');
                if (inp) {
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                    inp.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true, key: 'a'}));
                }
            """)
            time.sleep(0.4)

            # 4. Wait for results
            option = page.locator(".select2-results__option").first
            option.wait_for(state="visible", timeout=3000)

            # 5. Select via full pointer event chain
            page.evaluate("""
                const opt = document.querySelector('.select2-results__option');
                if (opt) {
                    ['mouseenter','pointerdown','mousedown','pointerup','mouseup','click'].forEach(evt => {
                        const cls = evt.startsWith('pointer')
                            ? PointerEvent : MouseEvent;
                        opt.dispatchEvent(new cls(evt, {
                            bubbles: true, cancelable: true,
                            view: window, isPrimary: true,
                            button: 0, buttons: evt === 'mousedown' ? 1 : 0
                        }));
                    });
                }
            """)
            time.sleep(0.3)

            # 6. Verify selection
            rendered_text = page.evaluate(f"""
                const el = document.querySelector('#select2-{container_id}-container');
                el ? el.textContent.replace('×','').trim() : '';
            """)
            success = value.lower() in (rendered_text or "").lower()

            return {
                "success": success,
                "container_id": container_id,
                "expected": value,
                "actual": rendered_text,
                "confidence": 0.90 if success else 0.20,
            }

        except Exception as e:
            return {"success": False, "container_id": container_id, "error": str(e), "confidence": 0.0}

    def fill_school(self, entry_index: str, school_name: str) -> dict:
        """
        Fill a school field. entry_index: 'sample', '0', '1', etc.
        """
        container_id = f"6074-1-{entry_index}"
        return self.fill_autocomplete(container_id, school_name)

    def fill_employer(self, entry_index: str, company_name: str) -> dict:
        """
        Fill employer field. If company not found, selects 'Other'
        and fills the text box that appears.
        """
        container_id = f"6076-11-{entry_index}"
        result = self.fill_autocomplete(container_id, company_name)
        if not result["success"]:
            # Try 'Other' fallback
            other_result = self.fill_autocomplete(container_id, "Other")
            if other_result["success"]:
                # Fill the employer name text field
                time.sleep(0.3)
                try:
                    name_field = self.page.get_by_label("Employer Name", exact=False).first
                    if name_field.count() == 0:
                        name_field = self.page.get_by_label("Other Employer", exact=False).first
                    name_field.fill(company_name)
                    return {**other_result, "used_other": True, "company_filled": company_name}
                except Exception as e:
                    return {**other_result, "used_other": True, "name_fill_error": str(e)}
        return result

    # ── Multi-entry form handling ────────────────────────────────────

    def add_education_entry(self) -> dict:
        """Click 'Add Another Education' button and wait for new row."""
        return self.engine.click_add_another("education")

    def add_experience_entry(self) -> dict:
        """Click 'Add Another Experience/Work' button and wait for new row."""
        for hint in ["experience", "work history", "work", "job"]:
            result = self.engine.click_add_another(hint)
            if result["success"]:
                return result
        return {"success": False, "error": "Could not find Add Another for work experience"}

    # ── CPA / compliance ────────────────────────────────────────────

    def set_cpa_license(self, value: str = "I do not have or plan to pursue a CPA license") -> dict:
        return self.engine.select_option(label="CPA", value=value)

    def set_work_authorization(self, authorized: bool = True, sponsorship: bool = False) -> dict:
        auth_val = "Yes" if authorized else "No"
        sponsor_val = "No" if not sponsorship else "Yes"
        r1 = self.engine.select_option(label="legally authorized", value=auth_val)
        r2 = self.engine.select_option(label="sponsorship", value=sponsor_val)
        return {"success": r1["success"] and r2["success"], "authorized": r1, "sponsorship": r2}

    def set_deloitte_alumni(self, is_alumni: bool = False) -> dict:
        return self.engine.select_option(label="Taleo employer", value="No" if not is_alumni else "Yes")

    # ── Page navigation ──────────────────────────────────────────────

    def click_next(self) -> dict:
        for label in ["Next", "Next Step", "Save and Continue", "Continue"]:
            result = self.engine.click_button(label)
            if result["success"]:
                time.sleep(1.0)  # Taleo page transitions are slow
                return result
        return {"success": False, "error": "Could not find Next button"}
