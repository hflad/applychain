# Taleo ATS — Interaction Notes

**Last Updated:** 2026-05-28  
**Reliability Rating:** Unknown (not yet tested)  
**Platform Type:** Java-based legacy platform (Oracle Taleo)

---

## Known Characteristics

- One of the oldest enterprise ATS platforms — heavy form-based, multi-step
- Mostly standard HTML forms — generally more reliable than React SPAs
- Very long, multi-section applications common (sometimes 10+ pages)
- Session timeout is aggressive — may time out during longer sessions
- File upload often requires specific file types (.docx or .pdf)
- Some Taleo deployments require creating an account before applying

---

## Interaction Strategy

### Text Inputs
- Standard HTML inputs — `form_input` and `type` typically work reliably
- `focusAndType()` rarely needed

### Dropdowns
- Usually native `<select>` elements — `form_input` works

### Session Management
- If a login wall appears: stop, notify user, wait for authentication
- Watch for session timeout warnings — if seen, stop and ask user to re-authenticate

### File Upload
- Standard file input — use `file_upload` tool
- Some Taleo deployments parse the uploaded resume and pre-fill fields — verify all auto-filled fields after upload

---

## Common Pitfalls

- *(Add findings as you encounter this platform)*
- Auto-parse after resume upload can populate fields incorrectly — always verify auto-filled data
- Account creation required on first visit to most Taleo deployments — stop and ask user to create account themselves

---

## Reliability Log

| Date | Company | Issues Encountered | Resolution |
|------|---------|-------------------|------------|
| *(add entries)* | | | |
