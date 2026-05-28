"""
cli.py — Command-Line Interface for HumanSimulationEngine
==========================================================
Claude calls this via bash to execute deterministic interactions.
All output is JSON — Claude parses success, confidence, escalate fields.

Usage examples:

  # Fill a text field
  python -m system.playwright_engine.cli fill-field \\
      --tab-url "https://apply.[company].com/..." \\
      --label "First Name" --value "Henry"

  # Select a dropdown option
  python -m system.playwright_engine.cli select-option \\
      --tab-url "https://..." \\
      --label "Education Level" --value "Master's Degree"

  # Click a radio button
  python -m system.playwright_engine.cli click-radio \\
      --tab-url "https://..." \\
      --label "Yes"

  # Click a button (Next, Submit, etc.)
  python -m system.playwright_engine.cli click-button \\
      --tab-url "https://..." \\
      --text "Next"

  # Click "Add Another" for a repeating section
  python -m system.playwright_engine.cli add-another \\
      --tab-url "https://..." \\
      --section "education"

  # Audit page for Add Another buttons (run before any repeating section)
  python -m system.playwright_engine.cli audit \\
      --tab-url "https://..."

  # Fill a Taleo Select2 autocomplete field
  python -m system.playwright_engine.cli taleo-autocomplete \\
      --tab-url "https://apply.[company].com/..." \\
      --container-id "6074-1-sample" --value "Miami University"

  # Take a screenshot
  python -m system.playwright_engine.cli screenshot \\
      --tab-url "https://..." --label "before-submit"

  # Validate multiple fields at once
  python -m system.playwright_engine.cli validate \\
      --tab-url "https://..." \\
      --fields '{"#school": "Miami University", "#degree": "Master"}'
"""

import argparse
import json
import sys
from pathlib import Path


def _get_engine(tab_url: str, debug: bool = False):
    """Connect engine to the given tab URL."""
    # Add parent dirs to path so imports work when called via bash
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from system.playwright_engine.engine import HumanSimulationEngine
    engine = HumanSimulationEngine(debug=debug)
    engine.connect(tab_url=tab_url)
    return engine


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
        result = eng.click_radio(label_text=args.label, container_selector=args.container or "body")
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
            # Generic fallback
            result = {
                "url": eng.page.url,
                "title": eng.page.title(),
                "add_another_buttons": eng.audit_add_another_buttons(),
            }
    print(json.dumps(result, indent=2))
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        prog="playwright_engine",
        description="ApplyChain Human-Simulation Interaction Engine",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    sub = parser.add_subparsers(dest="command", required=True)

    # fill-field
    p = sub.add_parser("fill-field", help="Fill a text input")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--value", required=True)
    p.add_argument("--selector", default=None)
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
    p.add_argument("--container", default=None)
    p.set_defaults(func=cmd_click_radio)

    # click-button
    p = sub.add_parser("click-button", help="Click a button by text")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--verify-selector", default=None)
    p.set_defaults(func=cmd_click_button)

    # add-another
    p = sub.add_parser("add-another", help="Click Add Another for a repeating section")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--section", default="")
    p.set_defaults(func=cmd_add_another)

    # audit
    p = sub.add_parser("audit", help="List all Add Another buttons on the page")
    p.add_argument("--tab-url", required=True)
    p.set_defaults(func=cmd_audit)

    # taleo-autocomplete
    p = sub.add_parser("taleo-autocomplete", help="Fill a Taleo Select2 autocomplete")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--container-id", required=True)
    p.add_argument("--value", required=True)
    p.set_defaults(func=cmd_taleo_autocomplete)

    # screenshot
    p = sub.add_parser("screenshot", help="Take a screenshot")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--label", default="screenshot")
    p.set_defaults(func=cmd_screenshot)

    # validate
    p = sub.add_parser("validate", help="Validate multiple field values")
    p.add_argument("--tab-url", required=True)
    p.add_argument("--fields", required=True, help='JSON: {"selector": "expected_value"}')
    p.set_defaults(func=cmd_validate)

    # diagnose
    p = sub.add_parser("diagnose", help="Diagnose current page state")
    p.add_argument("--tab-url", required=True)
    p.set_defaults(func=cmd_diagnose)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
