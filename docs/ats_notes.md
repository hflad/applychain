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

---

## Oracle HCM (Oracle HCM portals)
**Last Updated:** 2026-06-03
**Reliability Rating:** 4/5 — reliable with careful scrolling; some field misses
**Platform Type:** Oracle HCM Cloud Candidate Experience (JavaScript-heavy SPA)

### Known Characteristics
- 4-page application flow: Personal Info → Application Questions → Experience → More About You
- File upload: hidden `input[type=file]` elements behind drag-drop UI — use `file_upload` tool with `ref` IDs (`attachment-upload-[N]` for resume, `attachment-upload-[N]` for cover letter)
- ZIP code dropdown auto-populates City, State, and County — always select from dropdown, not type directly
- Language Skills: each language requires Language + Reading/Writing/Speaking proficiency + clicking "ADD LANGUAGE" button to save — ADD LANGUAGE must be clicked before moving on
- "Welcome Back" dialog may appear on return visits — close it to avoid stale profile data being loaded
- All application questions are on page 2 (not page 1 as read_page suggests)

### Work Authorization Sub-Questions
After selecting "Yes" to work authorization, sub-questions appear:
- Visa sponsorship needed → **N/A**
- Citizenship status → **US Citizen**

### Missed Fields (corrected manually — add to checklist)
- Race/ethnicity → [see application_defaults.md]
- Hispanic or Latino → [see application_defaults.md]
- Work authorization Yes + sub-questions (visa=N/A, citizenship=US Citizen)
- Prior employment at company → [see application_defaults.md]
- Affiliated firm disclosure → [see application_defaults.md]

### Latest Employer Dropdown
If employer not in dropdown — select **Other**. Rule: if employer not found in dropdown, always select "Other".

### EEO Defaults (GS-specific)
- Consent to self-identify → I consent
- Gender → [see application_defaults.md]
- Transgender → [see application_defaults.md]
- Sexual orientation → [see application_defaults.md]
- Pronouns → [see application_defaults.md]
- Race → [see application_defaults.md]
- Hispanic/Latino → [see application_defaults.md]

### Interaction Notes
- Scrolling while using coordinate-based clicks causes field misses — always scroll to element first using `scroll_to` with ref IDs, then click
- Page structure visible in `read_page` shows all sections but they are split across pages 1-4
- SUBMIT button is at bottom of page 4 — may require two clicks if first click doesn't register

---

## Oracle HCM (Oracle HCM employer — [company].fa.oraclecloud.com)
**Last Updated:** 2026-06-04
**Reliability Rating:** 2/5 — React-controlled fields block most automation; manual completion required for EEO and preferred locations
**Platform Type:** Oracle HCM Cloud Candidate Experience (same platform as GS but different instance)

### Flow
- Email → verification code → 4-step wizard: Personal Info → (unknown) → (unknown) → Review & Submit
- Email verification: enter email → check terms checkbox → click Next → receive OTP → enter code

### Step 1 — Personal Info
**Resume parser:** First file input (`input.apply-flow-profile-import-awli__file-upload`) parses resume and pre-fills name, email, phone, LinkedIn. Use `file_upload` with `ref` — found via `find` query "Import your profile from resume". Upload before filling any fields.

**Address:**
- Country field: type partial text → wait for gridcell dropdown → click option. Search "United States" to get the option. Country selection triggers address sub-fields to appear dynamically.
- City field: type city name → dropdown shows `City, County, State` format → select correct county. e.g. "CityName, County, State"
- Postal code: typing alone doesn't work — field opens a dropdown of zip codes. Type zip → select matching gridcell (e.g. "ZIPCODE, City, County, State"). County and State auto-fill from city selection.
- React state issue: `form_input` and React event injection both fail to trigger the location API. Only real keystrokes via `computer type` trigger the dropdown.

**Preferred Locations:**
- Field only accepts internal Oracle HCM employer location codes, NOT city names or street addresses
- Search by 5-digit location ID to get the right option (e.g. "54101" → "LOCID-Street Address" = Columbus OH)
- Known location codes for this job (job-id-example):
  - Location A: `LOCID` → "LOCID-Street Address"
  - Location B: `LOCID` → "LOCID-Location Name"
  - Location C: `LOCID` → "LOCID-Location Name"
- JS click on gridcell works once dropdown is open
- Field accepts up to 3 locations — add them sequentially

**EEO / Demographic Fields:**
- Disability: radio buttons — `ORA_PER_NO_US (No disability radio value)` = No disability. JS `.click()` works.
- Race: checkboxes — find by label text, JS `.click()` works. Use your application_defaults.md value.
- Gender, Military Status, Veteran Status: combobox inputs — did not reach these before manual takeover; likely same Oracle HCM pattern as GS instance
- Hispanic/Latino: checkbox — use your application_defaults.md value

### Sandbox / Playwright Limitation
playwright_engine cannot run from Cowork sandbox — pip install blocked by network proxy, and sandbox localhost ≠ Mac localhost for CDP. MCP server solution planned (see ROADMAP.md Phase 8). Until then: EEO fields and complex dropdowns require manual completion or Claude Code.
