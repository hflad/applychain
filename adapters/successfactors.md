# SAP SuccessFactors ATS — Interaction Notes

**Last Updated:** 2026-05-28  
**Reliability Rating:** Unknown (not yet tested)  
**Platform Type:** SAP enterprise platform, Angular/React frontend

---

## Known Characteristics

- Heavy enterprise platform used primarily by large corporations and consulting firms
- Complex multi-step application flow
- Often requires SSO or corporate email login for external applicants
- Custom Angular/React components — native interactions may need verification
- EEO compliance section common for US roles

---

## Interaction Strategy

### Text Inputs
1. Try `form_input` first
2. If React/Angular state doesn't update, use `focusAndType()`
3. Always verify visible state after typing

### Dropdowns / Selects
1. Native `<select>`: use `form_input`
2. Custom component dropdowns: click trigger → wait 1–2s → find option by text → click → verify

### File Upload
- Use `file_upload` tool with absolute file path
- Some SuccessFactors deployments parse the resume and auto-fill fields — verify all auto-populated fields

---

## Common Pitfalls

- *(Add findings as you encounter this platform)*
- Login requirements vary significantly between employers
- Some deployments require completing a profile before applying

---

## Reliability Log

| Date | Company | Issues Encountered | Resolution |
|------|---------|-------------------|------------|
| *(add entries)* | | | |
