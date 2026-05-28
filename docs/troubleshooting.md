# Troubleshooting Guide

Common issues and solutions when using ApplyChain.

---

## Setup Issues

**`python-docx` not found**  
Run: `pip3 install python-docx openpyxl --break-system-packages`  
Or use a virtual environment: `python3 -m venv venv && source venv/bin/activate && pip install python-docx openpyxl`

**`logs/applications_log.csv` missing**  
Run: `python3 scripts/init_log.py`

**Claude for Chrome not connecting**  
- Ensure the extension is installed and enabled in Chrome
- Click the extension icon and verify it shows "Connected"
- Reload the extension if needed from `chrome://extensions/`

---

## Resume Generation Issues

**Resume contains information I didn't provide**  
Check your `profile_knowledge_base/` files — the AI should only use what's there. If content was invented, this is a critical bug — do not use the generated resume. Report the exact prompt and output.

**`[FILL IN]` placeholders in the resume**  
These are intentional — the AI is flagging metrics or details that are missing from your profile. Either add the real value to your profile and regenerate, or fill in the placeholder manually before submitting.

**Resume is too long / too short**  
Adjust by telling Claude: "Keep it to 1 page" or "This can be 2 pages." The AI will trim or expand accordingly.

---

## Browser Automation Issues

**Field appears filled but form won't advance**  
This is a React state mismatch. Use the `focusAndType()` helper from `browser_helpers/interaction_helpers.js`. See `docs/browser_automation_guide.md`.

**Radio button click doesn't stick**  
Coordinate drift after scroll. Ask Claude to re-read the page and get fresh ref IDs, then retry the click.

**Custom dropdown shows "No results"**  
Try a shorter or different search term. Some dropdowns require exact partial matches (e.g., search "Stanford" not "Stanford University").

**Claude stopped mid-application**  
This is expected behavior — Claude stops when it encounters something uncertain. Read Claude's message, resolve the issue (login, CAPTCHA, missing data), and say "continue from where you left off."

**File upload fails**  
- Verify the file path is correct and the file exists
- Check the file format — some ATS platforms only accept `.pdf` or `.docx`
- Try uploading manually if the automated upload fails

---

## Log Issues

**Duplicate entry in applications_log.csv**  
Delete the duplicate row manually. Consider adding duplicate detection to your workflow (see ROADMAP.md Phase 4).

**Log not updating after submission**  
Claude should update the log automatically. If it didn't, add the entry manually using the column schema in `WORKFLOW_RULES.md`.

---

## Getting Help

1. Check `KNOWN_ISSUES.md` for documented bugs
2. Check `docs/browser_automation_guide.md` for ATS-specific guidance
3. Check the relevant adapter file in `adapters/`
4. Open an issue on GitHub if you've found a reproducible bug
