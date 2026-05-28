# Lever ATS — Interaction Notes

**Last Updated:** 2026-05-28  
**Reliability Rating:** Unknown (not yet tested)  
**Platform Type:** React-based

---

## Known Characteristics

- Single-page form (not multi-step wizard) in most deployments
- Standard fields: name, email, phone, LinkedIn, resume upload, cover letter
- Custom questions added by employer (free text, dropdowns, or checkboxes)
- File upload typically uses a standard `<input type="file">`
- No EEOC section by default (some employers add it via custom questions)

---

## Interaction Strategy

### Text Inputs
1. Try `form_input` first
2. If React state doesn't update, use `focusAndType()` from `browser_helpers/interaction_helpers.js`

### File Upload
1. Use `mcp__Claude_in_Chrome__file_upload` with absolute file path
2. Lever typically shows "1 file selected" or the filename after upload

### Custom Questions
- These vary by employer — read each question carefully
- For dropdown questions, try `form_input` first; escalate to click + verify
- For free text, use `focusAndType()` for React safety

---

## Common Pitfalls

- *(Add findings as you encounter this platform)*

---

## Reliability Log

| Date | Company | Issues Encountered | Resolution |
|------|---------|-------------------|------------|
| *(add entries)* | | | |
