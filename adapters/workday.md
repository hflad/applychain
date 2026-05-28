# Workday ATS — Interaction Notes

**Last Updated:** 2026-05-28  
**Reliability Rating:** Unknown (not yet tested)  
**Platform Type:** React SPA with Workday-specific component library

---

## Known Characteristics

- Heavy use of custom React components — native `form_input` may not trigger state updates
- Multi-step wizard navigation; "Next" buttons are typically visible and standard
- File upload often uses a standard file input (`<input type="file">`) — Claude for Chrome `file_upload` tool should work
- Resume upload: look for a labeled "Resume" or "CV" upload section
- "How did you hear" dropdown: typically a native `<select>` — `form_input` usually works

---

## Interaction Strategy

### Text Inputs
1. Try `form_input` first
2. If state doesn't update visually, escalate to `focusAndType()` from `browser_helpers/interaction_helpers.js`
3. Verify: visible text in the field should match what you typed

### Radio Buttons / Checkboxes
1. Try `left_click` on the label text (larger target than the input itself)
2. If click doesn't register visually, use `clickRadioByLabel()` from `browser_helpers/interaction_helpers.js`
3. Verify: the radio/checkbox should appear checked/filled after interaction

### Dropdowns (Custom Workday Components)
1. Click the trigger element
2. Wait 1–2 seconds for the dropdown to open
3. Type a search term if the dropdown has a search field
4. Click the matching option from the list
5. Verify: the displayed value should update

### File Upload
1. Use `mcp__Claude_in_Chrome__file_upload` tool with the absolute file path
2. Verify the filename appears in the upload confirmation area

---

## Common Pitfalls

- *(Add findings as you encounter this platform)*
- Workday sessions can expire during long applications — check for login prompts between sections
- Some Workday installs have custom "Additional Questions" sections that vary by employer

---

## Reliability Log

| Date | Company | Issues Encountered | Resolution |
|------|---------|-------------------|------------|
| *(add entries)* | | | |

---

## Notes

*Add platform-specific observations here as you use this adapter.*
