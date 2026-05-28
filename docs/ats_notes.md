# ATS Platform Reliability Notes
Last updated: 2026-05-28

This file tracks per-platform ATS behavior, known failure modes, and interaction reliability findings.
Updated after each application. Reference before starting automation on any new platform.

---

## Interaction Tier Priority (all platforms)
1. **Native browser interaction** — basic click/type via Chrome MCP (try first)
2. **Label-aware interaction** — target by label text, not coordinates
3. **Focus-and-retry interaction** — click, wait, verify, retry once
4. **DOM-aware helper fallback** — `system/interaction_helpers.js` functions

Only escalate tiers when lower tiers fail visibly. Do not default to complex helpers on every site.

---

## Platform: Avature (Avature employer Careers)
**Observed at:** Avature-hosted career portals
**ATS type:** React-heavy SPA, custom ARIA comboboxes

### Known Failures
| Field type | Failure mode | Notes |
|---|---|---|
| Custom combobox | Click opens dropdown but `form_input` doesn't fire React synthetic events | Must type to search, then click result |
| Radio buttons | Coordinate-based clicks miss after scroll/rerender | Use `ref` IDs, not pixel coordinates |
| Disability/veteran/name/resume upload | All 4 fields missed in automation pass | Page section not reached; completed manually |
| Text inputs | `form_input` sets DOM value but React state doesn't update | Use `type` action after focusing |
| Work history fields | React comboboxes for position, company, dates non-standard | User completed manually |
| Birthday dropdowns | Native `<select>` — `form_input` works | Confirmed |
| Relocate/hybrid dropdowns | Native `<select>` — `form_input` works | Confirmed |

### Reliable Methods
- Country/university/degree: click combobox → type search term → wait 2s → click result text
- Radio buttons: use `ref` IDs from `read_page` (not pixel coordinates after page scroll)
- Native selects: `form_input` with option text works reliably
- File upload: use `file_upload` tool with ref ID after reading page; click "From Device" tab first if needed

### Timing
- Search queries take 1–2s to return results — always `wait` before attempting to click results
- After selecting combobox option, wait 500ms before next interaction

### Reliability Rating: 3/5 — Multiple manual interventions required

---

## Platform: Paycom (Paycom employer)
**Observed at:** employer application
**ATS type:** Standard form-based

### Notes
- Applied successfully with minimal issues
- Standard form fields behaved reliably
- Reliability Rating: 5/5

---

## Platform: Workday
**Status:** Not yet observed
**Known general behavior:**
- React-controlled inputs common
- Date pickers may need special handling
- Multi-step wizard forms
- TODO: Document after first encounter

---

## Platform: Greenhouse
**Status:** Not yet observed
**Known general behavior:**
- Generally reliable form behavior
- File uploads standard
- TODO: Document after first encounter

---

## Platform: Taleo (Oracle) — apply.[company].com
**Observed at:** Taleo-hosted career portals (e.g. apply.[company].com)
**ATS type:** Multi-step wizard. Taleo-based with Select2 jQuery autocomplete fields.

### Steps
1. Resume upload
2. Personal info (name, phone, address, education, work history, immigration, CPA)
3. Job-specific questions
4. EEO / diversity questions
5. Review & Submit

### Known Behavior
| Field type | Method | Notes |
|---|---|---|
| School (Select2 autocomplete) | `mousedown` event on `.select2Container{id}` span → set `.select2-search__field` value → fire `input`+`keyup` → fire pointer+mouse events on `.select2-results__option` | Must use full pointer event chain: mouseenter, pointerdown, mousedown, pointerup, mouseup, click |
| Education Level | `form_input` with ref | Standard `<select>` — works reliably |
| Primary Major/Program | `form_input` with ref | Standard `<select>` — works reliably |
| Employer (Select2 autocomplete) | Same Select2 event chain as School | If company not found, use "Other" option and fill name manually in the text field that appears |
| "Add another" buttons | Must explicitly find and click these | The form does NOT pre-populate all entry rows — must click "Add Another Education" and "Add Another Experience" to get additional rows |
| Preferred first name | Separate field from legal name — always fill | Default to same as legal first name unless told otherwise |
| CPA license question | `form_input` with "I do not have or plan to pursue a CPA license" | All Big 4 firms ask this |
| Immigration / work auth | Two dropdowns: authorized=Yes, sponsorship=No | Standard selects |
| Prior employment at company | `form_input` No | |
| File upload (resume) | `file_upload` tool with ref ID | Step 1 only |

### Critical Lessons Learned
- **"Add Another" buttons are required.** Without clicking them, later entries never appear in the form. Always scan for "Add another education", "Add another experience" etc. after each entry is filled.
- **Select2 fields won't respond to simple `.click()`** — must dispatch `mousedown` event to open, then set value in the `.select2-search__field` input, then use the full pointer+mouse event chain on the result option.
- **"Other" for unlisted employers:** Some employers may not be in the Employer dropdown. Select "Other" — the form then shows a text input for the employer name. Fill that with the company name from the resume.
- **Page context can get lost between sessions** — if re-entering a session, always re-read the current tab context and verify form state before continuing.

### Timing
- Select2 search returns results synchronously from pre-loaded list (no AJAX wait needed)
- Page transitions between steps take 2–3s

### Reliability Rating: 3/5 — Select2 fields require custom event chain; Add Another buttons easy to miss

---

## Platform: Lever
**Status:** Not yet observed
**TODO:** Document after first encounter

---

## Platform: SuccessFactors (SAP)
**Status:** Not yet observed
**TODO:** Document after first encounter

---

## Platform: iCIMS
**Status:** Not yet observed
**TODO:** Document after first encounter

---

## Platform: LinkedIn Easy Apply
**Status:** Partially observed (navigation)
**Notes:** Login/SSO flow used. Direct job listings accessed. TODO: Document full form flow.

---

## General React/Dynamic Site Rules
- A click executing ≠ UI state changed
- Always verify visible state after interaction
- Never assume radio is selected just because `left_click` ran
- Never assume dropdown value persisted just because option was clicked
- Scroll position affects coordinate-based clicks — always use `ref` IDs when available
- Batch actions that scroll the page invalidate earlier coordinate assumptions

## Failure Classification
| Type | Description | Response |
|---|---|---|
| Silent radio failure | Radio clicked but stays unselected | Retry with ref ID; then try label-click via JS |
| Dropdown revert | Value selected then reverts to default | Wait longer; use JS `selectDropdownOption` helper |
| Text input miss | Typed text doesn't appear | Focus field explicitly, then type |
| React wipe | Value entered then cleared on rerender | Re-enter after delay; verify state |
| Hydration lag | Field not interactive yet | Add `wait` before interaction |
| Scroll miss | Coordinate click landed on wrong element | Scroll to element first, then use ref |
