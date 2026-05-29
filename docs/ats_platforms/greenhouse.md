# Greenhouse ATS — Interaction Notes

**Last Updated:** 2026-05-28  
**Reliability Rating:** Unknown (not yet tested)  
**Platform Type:** Primarily server-rendered with some React components

---

## Known Characteristics

- Generally more reliable than React-heavy platforms — many forms are server-rendered HTML
- Standard `<input>`, `<select>`, and `<textarea>` elements respond well to native interactions
- File upload via standard file input — `file_upload` tool should work
- EEOC section appears at the end of most applications (voluntary)
- "How did you hear" is typically a `<select>` dropdown
- Cover letter can often be typed into a textarea OR uploaded as a file

---

## Interaction Strategy

### Text Inputs
1. `form_input` usually works — try it first
2. If field doesn't register, try `left_click` then `type`
3. Escalate to `focusAndType()` only if both fail

### Dropdowns
1. `form_input` on native `<select>` elements works reliably
2. For custom dropdowns: click trigger → wait → click option → verify

### File Upload
1. Use `mcp__Claude_in_Chrome__file_upload` with absolute file path
2. Greenhouse typically shows the uploaded filename in a confirmation area

### Cover Letter
- If a textarea is provided, paste the cover letter text directly
- If only a file upload is provided, upload the `.docx` file
- Some Greenhouse forms offer both — prefer the text field for ATS parsing

---

## Common Pitfalls

- *(Add findings as you encounter this platform)*
- Some Greenhouse deployments load the EEOC section asynchronously — scroll down to confirm it's fully loaded before filling

---

## Reliability Log

| Date | Company | Issues Encountered | Resolution |
|------|---------|-------------------|------------|
| *(add entries)* | | | |
