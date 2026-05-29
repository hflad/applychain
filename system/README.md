# playwright_engine — Human-Simulation Interaction Engine

Deterministic, human-like browser interactions for ApplyChain ATS automation.
Wraps Playwright with confidence scoring, state verification, retry logic,
and full trace capture.

---

## Architecture

```
Claude/Cowork (reasoning + orchestration)
         ↓
  VerificationFramework  (verification.py)  ← PUBLIC API — Claude calls this
         ↓
  HumanSimulationEngine  (engine.py)
         ↓
  InteractionHelpers     (helpers.py)       ← human-event simulation
  FrontendValidator      (validation.py)    ← INTERNAL — low-level primitives used by engine
  InteractionConfidence  (confidence.py)    ← confidence scoring
  ObservabilityManager   (observability.py) ← screenshots + traces
         ↓
  ATS Adapter            (adapters/)        ← platform-specific overrides
         ↓
  Playwright CDP         ← connects to your existing Chrome session
         ↓
  ATS Website
```

### validation.py vs verification.py

Two files handle state checking — they serve different layers:

| File | Class | Role | Who uses it |
|------|-------|------|-------------|
| `validation.py` | `FrontendValidator` | Internal low-level primitives (verify_input_value, detect_rerender, wait_for_hydration). Returns `(bool, str)` tuples. | `engine.py` and `helpers.py` internally |
| `verification.py` | `VerificationFramework` | Public API for Claude. Multi-signal checks with structured `{success, confidence, observations, details}` results. | Claude via CLI (`verify-input`, `verify-radio`, etc.) |

Do not call `FrontendValidator` directly from Claude — use `VerificationFramework` via the CLI.

---

## Setup

```bash
# From applychain-workspace root:
bash system/playwright_engine/setup.sh

# Launch Chrome with CDP enabled (quit Chrome first):
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &
```

Add as an alias for convenience:
```bash
alias chrome-debug="/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222"
```

---

## Usage (Claude calls these via bash)

```bash
# Audit the page for "Add Another" buttons before filling repeating sections
python -m system.playwright_engine.cli audit \
    --tab-url "https://apply.[company].com/..."

# Fill a text input
python -m system.playwright_engine.cli fill-field \
    --tab-url "https://apply.[company].com/..." \
    --label "First Name" --value "Henry"

# Select a native dropdown
python -m system.playwright_engine.cli select-option \
    --tab-url "https://apply.[company].com/..." \
    --label "Education Level" --value "Master's Degree"

# Click a radio button
python -m system.playwright_engine.cli click-radio \
    --tab-url "https://apply.[company].com/..." \
    --label "Yes"

# Click Next / Submit
python -m system.playwright_engine.cli click-button \
    --tab-url "https://apply.[company].com/..." \
    --text "Next"

# Add another education/work entry
python -m system.playwright_engine.cli add-another \
    --tab-url "https://apply.[company].com/..." \
    --section "education"

# Taleo Select2 autocomplete (school, employer)
python -m system.playwright_engine.cli taleo-autocomplete \
    --tab-url "https://apply.[company].com/..." \
    --container-id "6074-1-sample" --value "Miami University"

# Validate fields are showing correct values
python -m system.playwright_engine.cli validate \
    --tab-url "https://apply.[company].com/..." \
    --fields '{"#school-field": "Miami University", "#degree": "Master"}'

# Screenshot
python -m system.playwright_engine.cli screenshot \
    --tab-url "https://apply.[company].com/..." --label "step-2-complete"
```

---

## Output Format

Every command outputs JSON:

```json
{
  "success": true,
  "confidence": 0.91,
  "confidence_level": "HIGH",
  "escalate": false,
  "url": "https://apply.[company].com/...",
  "screenshot_before": "/path/to/before.png",
  "screenshot_after": "/path/to/after.png",
  "confidence_detail": {
    "signals": [
      {"name": "visual_state_changed", "passed": true, "weight": 0.30},
      {"name": "value_persisted",      "passed": true, "weight": 0.25},
      ...
    ]
  }
}
```

**Claude should check:**
- `success` — did the action complete without error?
- `confidence_level` — `HIGH`/`MEDIUM` = proceed; `LOW` = log warning; `FAILED` = escalate
- `escalate` — if `true`, stop and ask Henry before proceeding

---

## Confidence Levels

| Level  | Score  | Action                          |
|--------|--------|---------------------------------|
| HIGH   | ≥ 0.85 | Proceed                         |
| MEDIUM | 0.60–0.84 | Proceed with logged warning  |
| LOW    | 0.35–0.59 | Retry once, then escalate    |
| FAILED | < 0.35 | Stop, escalate to Henry         |

---

## ATS Platform Support

| Platform   | Status      | Adapter file     |
|------------|-------------|------------------|
| Taleo      | ✅ Tested   | adapters/taleo.py    |
| Avature    | ✅ Observed | adapters/avature.py  |
| Workday    | 📋 Documented | adapters/workday.py |
| Greenhouse | 📋 Documented | adapters/greenhouse.py |

Adapters auto-detect from URL. To add a new platform:
1. Create `adapters/yourplatform.py` extending `BaseATSAdapter`
2. Set `url_patterns` and `platform_name`
3. Register in `adapters/registry.py`

---

## Verification Framework

`verification.py` provides platform-agnostic primitives to confirm that interactions produced real visible state changes. It reports facts — it never decides what to do next.

```
Claude decides what to verify
    ↓
Playwright executes the interaction
    ↓
VerificationFramework reports what it observes
    ↓
Claude evaluates the result and decides next action
```

### Usage

```python
from system.playwright_engine.verification import VerificationFramework

vf = VerificationFramework(page)

# After typing into a field
result = vf.verify_input_value(
    locator=page.get_by_label("First Name"),
    expected_value="Henry",
    field_label="First Name",
)
# {"success": true, "confidence": 0.95, "observations": [...], "details": {...}}

# After selecting a radio button
result = vf.verify_radio_selected(
    locator=page.locator("#radio-yes"),
    label_text="Yes",
)

# After choosing a dropdown option
result = vf.verify_dropdown_value(
    locator=page.locator("#degree-select"),
    expected_value="Master's Degree",
)

# Before clicking submit — check if it's enabled
result = vf.verify_submit_enabled(
    also_check_text=["Next", "Continue"],
)

# Confirm text appeared after an action
result = vf.verify_text_present("Application submitted successfully")

# Save a full snapshot (screenshot + DOM + diagnostics)
snapshot = vf.capture_verification_snapshot(label="after-education-section")
# Files saved to: logs/verification_snapshots/after-education-section_{ts}/
```

### Result Shape

Every method returns the same structure:

```json
{
  "success": true,
  "confidence": 0.95,
  "observations": [
    "playwright input_value='Henry' (match)",
    "DOM .value='Henry'",
    "value stable after 500ms hydration wait",
    "field (First Name) contains expected value"
  ],
  "details": {
    "expected_value": "Henry",
    "value_playwright": "Henry",
    "value_dom": "Henry",
    "value_post_hydration": "Henry",
    "hydration_reset": false
  }
}
```

`confidence` reflects evidence quality, not a recommendation to proceed. A `0.55` confidence on a radio result means signals were contradictory — Claude should inspect `details.signals` before deciding.

### Snapshot Contents

`capture_verification_snapshot()` saves to `logs/verification_snapshots/{label}_{ts}/`:
- `screenshot.png` — viewport screenshot at that moment
- `dom_excerpt.html` — inner HTML of the target selector (default: body, max 50KB)
- `summary.json` — URL, title, timestamp, form/input counts, visible errors

---

## Debugging

Traces land in: `applychain-workspace/logs/playwright_traces/`

Each failed interaction writes:
- `*_before.png` — screenshot before interaction
- `*_after.png` — screenshot after
- `*_dom.html` — DOM snapshot of relevant region
- `*_trace.json` — full interaction timeline with confidence signals

---

## Design Philosophy

> A slower system with reliable visible interactions is far more valuable
> than a fast system silently failing underneath the UI.

- **Human-first**: scroll → hover → click → type → tab. Always.
- **Verify everything**: never assume "click executed" = "state changed"
- **Confidence over speed**: low confidence stops the workflow
- **Observe to debug**: traces tell you WHY it failed, not just that it did
- **Adapters for reliability**: platform quirks are first-class, not afterthoughts
