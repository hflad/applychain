# Browser Automation Guide

A practical guide to using Claude for Chrome to fill and submit job applications.

---

## Prerequisites

1. Claude Desktop installed with Cowork mode
2. Claude for Chrome extension installed and connected
3. The extension is visible in the Chrome toolbar and shows "Connected"

---

## Recommended Browser Setup — Dedicated Debug Browser

Running a separate Chrome instance for ApplyChain work (distinct from your everyday browsing) is strongly recommended. Here's why and how.

### Why a Separate Browser?

- **Stability** — the `--remote-debugging-port=9222` flag required for playwright_engine CDP mode can only be set at launch. You can't add it to a running Chrome. Keeping a dedicated instance means it's always ready.
- **No interference** — your daily tabs, extensions, and sessions stay untouched. If something goes wrong during automation testing, your main browser is unaffected.
- **Persistent logins** — you sign into LinkedIn, job portals, and the Claude extension once in the debug browser and they stay synced via your Google profile. No re-authentication every session.
- **Clean testing environment** — you can observe exactly what Claude is doing in the debug browser without other tabs causing noise.

### Setup

**1. Launch the debug browser** (quit regular Chrome first if it's open, or use a different Chrome channel like Chrome Canary):
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.chrome-applychain" &
```

The `--user-data-dir` flag gives this instance its own profile directory — completely separate from your main Chrome profile.

**2. Add a shell alias** so you can launch it easily in future:
```bash
# Add to ~/.zshrc or ~/.bash_profile
alias chrome-debug="/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.chrome-applychain"
```
Then `source ~/.zshrc` and just run `chrome-debug` to launch.

**3. First-time setup in the debug browser:**
- Sign into your Google account (syncs bookmarks, passwords if desired)
- Install the Claude for Chrome extension and connect it
- Sign into LinkedIn
- Sign into any job portals you use frequently

These sessions will persist across restarts because the profile is stored at `~/.chrome-applychain`.

### Daily Workflow

```
1. Run: chrome-debug          ← launches debug browser with CDP ready
2. Open Claude Desktop (Cowork)
3. Tell Claude what to work on — it uses the Claude Chrome extension to see and interact with the debug browser
4. If a complex ATS interaction fails, Claude calls playwright_engine via bash (CDP connects to the already-running debug browser on port 9222)
```

Your main Chrome browser continues running your personal tabs and is never touched.

---

## Core Philosophy

The browser automation layer is a **form-filling assistant**, not an autonomous agent. Claude navigates, reads, and fills — but you review and approve before anything is submitted.

**The golden rule:** A click executing does NOT mean the UI state changed. Always verify that the visible page state reflects what was intended before moving to the next field.

---

## Interaction Tier Priority

When filling a form field, try these approaches in order:

| Tier | Method | When to Use |
|------|--------|-------------|
| 1 | Native Chrome MCP (`form_input`, `left_click`, `type`) | Always try first |
| 2 | Label-aware targeting (click label text or use ref IDs from `read_page`) | When Tier 1 click misses or doesn't register |
| 3 | Focus-and-retry (`focusAndType()` from interaction_helpers.js) | When React state doesn't update from `form_input` |
| 4 | DOM-aware helpers (`setReactInputValue()`, `selectDropdownOption()`) | Last resort for React SPAs |

Only escalate to a higher tier when you've confirmed the lower tier failed (visible state didn't update).

---

## React SPA Forms (Avature, some Workday)

Many modern ATS platforms are React single-page apps. These have a known failure pattern:

**Problem:** `form_input` sets the DOM input's `.value` property, but React's internal state tracker doesn't see the change. The field appears filled but React won't submit the value.

**Solution:** Use the `setReactInputValue()` helper, which uses the native property setter and dispatches the events React listens for:
```javascript
// Paste into javascript_tool when native form_input fails on a React field
const input = document.querySelector('input[placeholder="First Name"]');
setReactInputValue(input, "Jane");
```

See `browser_helpers/interaction_helpers.js` for the full set of helpers.

---

## Radio Buttons

**Problem:** Pixel-coordinate clicks become inaccurate after the page has scrolled.

**Solution:** Always use ref-based targeting for radio buttons:
1. Call `read_page` to get current ref IDs
2. Click the label ref (larger target) rather than the input ref
3. Verify: `input.checked` should be `true`

If the label click doesn't work, try clicking the input ref directly.

---

## Custom Combobox / Autocomplete Fields

Many ATS platforms use custom ARIA comboboxes (not native `<select>`) for fields like university name, degree, country, etc.

**Working pattern:**
1. Click the combobox to focus it
2. Type a search term (treat it like a search input)
3. Wait 2 seconds for results to populate
4. Click the matching option from the dropdown list (by ref ID)
5. Verify: the field should display the selected value

Do NOT use `form_input` on custom comboboxes — it sets the DOM value but doesn't fire the events the component needs.

---

## File Upload

Use `mcp__Claude_in_Chrome__file_upload` with the absolute path to your resume or cover letter:
```
file path: /Users/yourname/Desktop/your-project/resumes/Company_Role_Resume_2026-01-01.docx
```

After upload, verify the filename appears in the page's confirmation area.

---

## When to Stop and Ask

Stop automation and notify the user when:
- A CAPTCHA or bot-detection challenge appears
- A login wall is encountered (never enter passwords)
- A required field can't be filled after two attempts
- An unexpected page or error message appears
- A field is asking for information not in `profile_knowledge_base/application_defaults.md`
- Any sensitive question appears that isn't covered by defaults

---

## Pre-Submission Checklist

Before the final submit, always show the user:
1. Resume file uploaded ✓
2. Cover letter file uploaded ✓
3. Detected ATS platform
4. Overall match score
5. Any `[FILL IN]` placeholders that weren't resolved
6. Any fields the user should double-check

Then wait for explicit "yes, submit" before clicking anything.

---

## Post-Submission

After successful submission:
1. Confirm the submission confirmation page loaded
2. Note the application ID or confirmation number if displayed
3. Update `logs/applications_log.csv`
4. Save the application bundle to `applications/`

---

## Troubleshooting

**Field appears filled but form won't proceed to next step:** React state mismatch. Use `focusAndType()` or `setReactInputValue()`.

**Radio button click registers but selection doesn't persist:** Coordinate drift after scroll. Re-run `read_page` to get fresh ref IDs and retry.

**Dropdown shows "no results" when typing:** Try a shorter search term (e.g., "Stanford" instead of "Stanford University").

**Page scrolls unexpectedly during form fill:** Normal behavior on long forms. After any scroll, re-fetch ref IDs before clicking radio buttons.

**Session expired mid-application:** Stop, notify user, wait for re-authentication. Most ATS platforms save partial progress.
