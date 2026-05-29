# iCIMS ATS — Interaction Notes

**Last Updated:** 2026-05-28  
**Reliability Rating:** Unknown (not yet tested)  
**Platform Type:** Multi-step form, mix of legacy and modern components

---

## Known Characteristics

- Multi-step wizard with explicit "Next" navigation
- Requires account creation on first application
- Mix of standard HTML inputs and some custom components
- Resume upload is typically early in the flow
- EEO/OFCCP compliance section common at the end

---

## Interaction Strategy

### Text Inputs
1. `form_input` — try first
2. Escalate to `focusAndType()` if field doesn't update

### File Upload
- Standard file input — use `file_upload` tool

### Account Creation
- iCIMS almost always requires creating an account before you can apply
- Stop immediately and ask user to create their own account — do not attempt to create accounts on their behalf

---

## Common Pitfalls

- *(Add findings as you encounter this platform)*
- Account wall is common — plan for it and ask user to handle authentication

---

## Reliability Log

| Date | Company | Issues Encountered | Resolution |
|------|---------|-------------------|------------|
| *(add entries)* | | | |
