"""
cli.py — Command-Line Interface for HumanSimulationEngine
==========================================================
Claude calls this via bash to execute deterministic interactions and verify results.
All output is JSON — Claude parses success, confidence, escalate fields.

INTERACTION COMMANDS (execute actions):

  # Fill a text field
  python3 -m system.playwright_engine.cli fill-field \\
      --tab-url "https://apply.[company].com/..." \\
      --label "First Name" --value "Henry"

  # Select a dropdown option
  python3 -m system.playwright_engine.cli select-option \\
      --tab-url "https://..." \\
      --label "Education Level" --value "Master's Degree"

  # Click a radio button
  python3 -m system.playwright_engine.cli click-radio \\
      --tab-url "https://..." \\
      --label "Yes"

  # Click a button (Next, Submit, etc.)
  python3 -m system.playwright_engine.cli click-button \\
      --tab-url "https://..." \\
      --text "Next"

  # Click "Add Another" for a repeating section
  python3 -m system.playwright_engine.cli add-another \\
      --tab-url "https://..." \\
      --section "education"

  # Audit page for Add Another buttons (run before any repeating section)
  python3 -m system.playwright_engine.cli audit \\
      --tab-url "https://..."

  # Fill a Taleo Select2 autocomplete field
  python3 -m system.playwright_engine.cli taleo-autocomplete \\
      --tab-url "https://apply.[company].com/..." \\
      --container-id "6074-1-sample" --value "Miami University"

  # Take a screenshot
  python3 -m system.playwright_engine.cli screenshot \\
      --tab-url "https://..." --label "before-submit"

  # Validate multiple fields at once (selector-based)
  python3 -m system.playwright_engine.cli validate \\
      --tab-url "https://..." \\
      --fields '{"#school": "Miami University", "#degree": "Master"}'

  # Diagnose current page state
  python3 -m system.playwright_engine.cli diagnose \\
      --tab-url "https://..."

VERIFICATION COMMANDS (observe state — no side effects):

  # Verify a text input contains expected value (with hydration recheck)
  python3 -m system.playwright_engine.cli verify-input \\
      --tab-url "https://..." \\
      --label "First Name" --expected "Henry"

  # Verify a radio button is selected (4-signal check)
  python3 -m system.playwright_engine.cli verify-radio \\
      --tab-url "https://..." \\
      --label "Yes"

  # Verify a dropdown holds expected value (with rerender recheck)
  python3 -m system.playwright_engine.cli verify-dropdown \\
      --tab-url "https://..." \\
      --label "Education Level" --expected "Master's Degree"

  # Verify expected text is visible on the page
  python3 -m system.playwright_engine.cli verify-text \\
      --tab-url "https://..." \\
      --expected "Application submitted"

  # Check whether the submit/next button is enabled
  python3 -m system.playwright_engine.cli verify-submit \\
      --tab-url "https://..."

  # Capture full verification snapshot (screenshot + DOM + diagnostics)
  python3 -m system.playwright_engine.cli snapshot \\
      --tab-url "https://..." --label "after-education-section"
"""

import argparse
import json
import sys
from pathlib import Path


def _get_engine(tab_url: str, debug: bool = False):
    """Connect HumanSimulationEngine to the given tab URL."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from system.playwright_engine.engine import HumanSimulationEngine
    engine = HumanSimulationEngine(debug=debug)
    engine.connect(tab_url=tab_url)
    return engine


def _get_verification(tab_url: str, debug: bool = False):
    """
    Connect VerificationFramework to the given tab URL.
    Returns (framework, engine) — engine must be kept alive as context manager.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from system.playwright_engine.engine import HumanSimulationEngine
    from system.playwright_engine.verification import VerificationFramework
    engine = HumanSimulationEngine(debug=debug)
    engine.connect(tab_url=tab_url)
    vf = VerificationFramework(engine.page)
    return vf, engine


# ── Interaction commands ─────────────────────────────────────────────────────

def cmd_fill_field(args):
    with _get_engine(args.tab_url, args.debug) as eng:
        result = eng.fill_field(label=args.label, value=args.value, selector=args.selector)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


def cmd_select_option(args):
    with _get_engine(args.tab_url, args.debug) as eng:
        result = eng.select_option(label=args.label, value=args.value, selector=args.selector)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


def cmd_click_radio(args):
    with _get_engine(args.tab_url, args.debug) as eng:
        result = eng.click_radio(
            label_text=args.label,
            container_selector=args.container or "body",
        )
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


def cmd_click_button(args):
    with _get_engine(args.tab_url, args.debug) as eng:
        result = eng.click_button(text=args.text, verify_selector=args.verify_selector)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


def cmd_add_another(args):
    with _get_engine(args.tab_url, args.debug) as eng:
        result = eng.click_add_another(section_hint=args.section or "")
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


def cmd_audit(args):
    with _get_engine(args.tab_url, args.debug) as eng:
        result = eng.audit_add_another_buttons()
        result["url"] = eng.page.url
    print(json.dumps(result, indent=2))
    sys.exit(0)


def cmd_taleo_autocomplete(args):
    with _get_engine(args.tab_url, args.debug) as eng:
        result = eng.run_adapter_action(
            "fill_autocomplete",
            container_id=args.container_id,
            value=args.value,
        )
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


def cmd_screenshot(args):
    with _get_engine(args.tab_url, args.debug) as eng:
        path = eng.screenshot(label=args.label or "screenshot")
    print(json.dumps({"success": True, "path": path}, indent=2))
    sys.exit(0)


def cmd_validate(args):
    fields = json.loads(args.fields)
    with _get_engine(args.tab_url, args.debug) as eng:
        result = eng.validate_state(fields)
    all_passed = all(v["passed"] for v in result.values())
    print(json.dumps({"success": all_passed, "fields": result}, indent=2))
    sys.exit(0 if all_passed else 1)


def cmd_diagnose(args):
    with _get_engine(args.tab_url, args.debug) as eng:
        result = eng.run_adapter_action("diagnose")
        if not result.get("success") is False:
            result = {
                "url": eng.page.url,
                "title": eng.page.title(),
                "add_another_buttons": eng.audit_add_another_buttons(),
            }
    print(json.dumps(result, indent=2))
    sys.exit(0)


# ── Verification commands ────────────────────────────────────────────────────

def cmd_verify_input(args):
    """
    Verify a text input contains the expected value.
    Locates the field by label text, then calls VerificationFramework.verify_input_value().
    """
    vf, engine = _get_verification(args.tab_url, args.debug)
    with engine:
        # Resolve locator by label, falling back to CSS selector if provided
        if args.selector:
            locator = engine.page.locator(args.selector).first
        else:
            locator = engine.page.get_by_label(args.label, exact=False).first

        result = vf.verify_input_value(
            locator=locator,
            expected_value=args.expected,
            hydration_wait_ms=args.hydration_wait,
            field_label=args.label,
        )
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


def cmd_verify_radio(args):
    """
    Verify a radio button is selected.
    Locates by label text, then calls VerificationFramework.verify_radio_selected().
    """
    vf, engine = _get_verification(args.tab_url, args.debug)
    with engine:
        if args.selector:
            locator = engine.page.locator(args.selector).first
        else:
            # Try label → associated input, then aria role
            try:
                locator = engine.page.get_by_label(args.label, exact=False).first
            except Exception:
                locator = engine.page.get_by_role("radio", name=args.label, exact=False).first

        result = vf.verify_radio_selected(locator=locator, label_text=args.label)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


def cmd_verify_dropdown(args):
    """
    Verify a dropdown holds the expected value (with rerender recheck).
    Locates by label text, then calls VerificationFramework.verify_dropdown_value().
    """
    vf, engine = _get_verification(args.tab_url, args.debug)
    with engine:
        if args.selector:
            locator = engine.page.locator(args.selector).first
        else:
            locator = engine.page.get_by_label(args.label, exact=False).first

        result = vf.verify_dropdown_value(
            locator=locator,
            expected_value=args.expected,
            rerender_wait_ms=args.rerender_wait,
            field_label=args.label,
        )
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


def cmd_verify_text(args):
    """
    Verify expected text is visible on the page.
    Calls VerificationFramework.verify_text_present().
    """
    vf, engine = _get_verification(args.tab_url, args.debug)
    with engine:
        result = vf.verify_text_present(
            expected_text=args.expected,
            exact=args.exact,
            timeout_ms=args.timeout,
            search_selector=args.within or "body",
        )
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


def cmd_verify_submit(args):
    """
    Check whether the submit/next button is enabled.
    Calls VerificationFramework.verify_submit_enabled().
    """
    vf, engine = _get_verification(args.tab_url, args.debug)
    with engine:
        also_check = json.loads(args.also_check) if args.also_check else None
        result = vf.verify_submit_enabled(
            submit_selector=args.selector or "button[type='submit']",
            also_check_text=also_check,
        )
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


def cmd_snapshot(args):
    """
    Capture a full verification snapshot: screenshot + DOM excerpt + page diagnostics.
    Saved to logs/verification_snapshots/{label}_{timestamp}/
    Calls VerificationFramework.capture_verification_snapshot().
    """
    vf, engine = _get_verification(args.tab_url, args.debug)
    with engine:
        result = vf.capture_verification_snapshot(
            label=args.label or "snapshot",
            include_dom_excerpt=not args.no_dom,
            dom_selector=args.dom_selector or "body",
        )
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


# ── Argument parser ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="playwright_engine",
        description="ApplyChain Human-Simulation Interaction Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    sub = parser.add_subparsers(dest="command", required=True)

    # ── Interaction commands ─────────────────────────────────────────────────

    # fill-field
    p = sub.add_parser("fill-field", help="Fill a text input by label")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--label", required=True, help="Visible label text")
    p.add_argument("--value", required=True, help="Value to type")
    p.add_argument("--selector", default=None, help="CSS selector override")
    p.set_defaults(func=cmd_fill_field)

    # select-option
    p = sub.add_parser("select-option", help="Select a native <select> dropdown option")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--value", required=True)
    p.add_argument("--selector", default=None)
    p.set_defaults(func=cmd_select_option)

    # click-radio
    p = sub.add_parser("click-radio", help="Click a radio button by label text")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--container", default=None, help="Containing element selector")
    p.set_defaults(func=cmd_click_radio)

    # click-button
    p = sub.add_parser("click-button", help="Click a button by visible text")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--text", required=True, help="Button text")
    p.add_argument("--verify-selector", default=None, help="Selector to wait for after click")
    p.set_defaults(func=cmd_click_button)

    # add-another
    p = sub.add_parser("add-another", help="Click Add Another for a repeating section")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--section", default="", help="Section keyword hint (e.g. 'education')")
    p.set_defaults(func=cmd_add_another)

    # audit
    p = sub.add_parser("audit", help="List all Add Another buttons on the page")
    p.add_argument("--tab-url", required=True)
    p.set_defaults(func=cmd_audit)

    # taleo-autocomplete
    p = sub.add_parser("taleo-autocomplete", help="Fill a Taleo Select2 autocomplete")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--container-id", required=True, help="Select2 container ID")
    p.add_argument("--value", required=True)
    p.set_defaults(func=cmd_taleo_autocomplete)

    # screenshot
    p = sub.add_parser("screenshot", help="Take a screenshot (saves to logs/playwright_traces/)")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--label", default="screenshot")
    p.set_defaults(func=cmd_screenshot)

    # validate
    p = sub.add_parser("validate", help="Validate multiple fields by CSS selector")
    p.add_argument("--tab-url", required=True)
    p.add_argument(
        "--fields",
        required=True,
        help='JSON object: {"#css-selector": "expected_value", ...}',
    )
    p.set_defaults(func=cmd_validate)

    # diagnose
    p = sub.add_parser("diagnose", help="Diagnose current page state and ATS platform")
    p.add_argument("--tab-url", required=True)
    p.set_defaults(func=cmd_diagnose)

    # ── Verification commands ────────────────────────────────────────────────

    # verify-input
    p = sub.add_parser(
        "verify-input",
        help="Verify a text input contains the expected value (with hydration recheck)",
    )
    p.add_argument("--tab-url", required=True)
    p.add_argument("--label", required=True, help="Visible label text to locate the field")
    p.add_argument("--expected", required=True, help="Expected value in the field")
    p.add_argument("--selector", default=None, help="CSS selector override")
    p.add_argument(
        "--hydration-wait",
        type=int,
        default=500,
        help="ms to wait before rechecking for hydration resets (default: 500)",
    )
    p.set_defaults(func=cmd_verify_input)

    # verify-radio
    p = sub.add_parser(
        "verify-radio",
        help="Verify a radio button is selected (4-signal: is_checked, DOM, aria, CSS)",
    )
    p.add_argument("--tab-url", required=True)
    p.add_argument("--label", required=True, help="Label text associated with the radio")
    p.add_argument("--selector", default=None, help="CSS selector override")
    p.set_defaults(func=cmd_verify_radio)

    # verify-dropdown
    p = sub.add_parser(
        "verify-dropdown",
        help="Verify a dropdown holds the expected value (with rerender recheck)",
    )
    p.add_argument("--tab-url", required=True)
    p.add_argument("--label", required=True, help="Visible label text to locate the dropdown")
    p.add_argument("--expected", required=True, help="Expected selected value")
    p.add_argument("--selector", default=None, help="CSS selector override")
    p.add_argument(
        "--rerender-wait",
        type=int,
        default=600,
        help="ms to wait before rechecking for rerender resets (default: 600)",
    )
    p.set_defaults(func=cmd_verify_dropdown)

    # verify-text
    p = sub.add_parser(
        "verify-text",
        help="Verify expected text is visible on the page",
    )
    p.add_argument("--tab-url", required=True)
    p.add_argument("--expected", required=True, help="Text to look for on the page")
    p.add_argument("--exact", action="store_true", help="Require exact text match")
    p.add_argument(
        "--timeout",
        type=int,
        default=3000,
        help="ms to wait for text to appear (default: 3000)",
    )
    p.add_argument(
        "--within",
        default=None,
        help="CSS selector to narrow search scope (default: body)",
    )
    p.set_defaults(func=cmd_verify_text)

    # verify-submit
    p = sub.add_parser(
        "verify-submit",
        help="Check whether the submit/next button is enabled",
    )
    p.add_argument("--tab-url", required=True)
    p.add_argument(
        "--selector",
        default=None,
        help="CSS selector for submit button (default: button[type='submit'])",
    )
    p.add_argument(
        "--also-check",
        default=None,
        help='JSON array of button text patterns to also check, e.g. \'["Next","Continue"]\'',
    )
    p.set_defaults(func=cmd_verify_submit)

    # snapshot
    p = sub.add_parser(
        "snapshot",
        help="Capture verification snapshot: screenshot + DOM excerpt + page diagnostics",
    )
    p.add_argument("--tab-url", required=True)
    p.add_argument("--label", default="snapshot", help="Human-readable label for this snapshot")
    p.add_argument(
        "--no-dom",
        action="store_true",
        help="Skip DOM excerpt (faster, screenshot + diagnostics only)",
    )
    p.add_argument(
        "--dom-selector",
        default=None,
        help="CSS selector for DOM excerpt scope (default: body)",
    )
    p.set_defaults(func=cmd_snapshot)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
