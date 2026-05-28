# Avature ATS — Interaction Notes

**Last Updated:** 2026-05-28  
**Reliability Rating:** 3/5 — usable with careful interaction strategy  
**Platform Type:** React SPA with custom ARIA component library

---

## Known Characteristics

- Custom ARIA comboboxes that don't respond to native `form_input` (React synthetic event mismatch)
- Coordinate drift after page scroll — pixel-coordinate clicks become unreliable once the page has scrolled
- Multi-section forms (typically segmented into sections: Personal Info, Work Authorization, Education, Work History, EEO)
- File upload accepts `.docx` and `.pdf` via standard file input
- Radio buttons: use label ref IDs from `read_page`, not coordinate clicks
- Session persistence: once authenticated, sessions typically hold for the full application

---

## Interaction Strategy

### Text Inputs
1. Try `form_input` first — works for simple non-React text fields
2. If the field doesn't update visually (React state mismatch), use `focusAndType()` from `browser_helpers/interaction_helpers.js`
3. Verify: visible text in the field should match the typed value

### Custom ARIA Combobox / Autocomplete Fields (University, Degree, Country, etc.)
Avature uses custom comboboxes that DO NOT respond to `form_input` or native `left_click + type` sequences:

**Working pattern:**
```
1. Click the combobox trigger to focus it
2. Type the search term directly (the field acts as a search input)
3. Wait 2 seconds for the dropdown to populate
4. Find the matching option in the dropdown list
5. Click the option by its ref ID (from read_page) — NOT by coordinates
6. Verify: the field should display the selected value
```

### Radio Buttons
**Critical:** Coordinates drift after scroll. Always use ref-based targeting:
```
1. Call read_page to get current ref IDs for the radio buttons
2. Use left_click with the ref ID of the LABEL (not the input)
3. Verify immediately: the radio should appear selected
4. If not selected, try clicking the ref ID of the input[type="radio"] directly
```

### Native `<select>` Dropdowns
Standard selects (e.g., country dropdowns, year dropdowns) work reliably:
```
1. form_input with the select element's ref ID and the option value
2. Verify the displayed option updated
```

### File Upload
```
1. Use mcp__Claude_in_Chrome__file_upload with the absolute path to the .docx file
2. Look for a "Resume" or "Upload" button to trigger the file input
3. Verify the filename appears after upload
```

---

## Form Section Order (Typical Avature Layout)

1. Personal Information (name, phone, email, address)
2. Work Authorization (radio buttons — use ref IDs)
3. Education (custom comboboxes for university and degree)
4. Work History (employer, title, dates, description)
5. Additional Questions (varies by employer)
6. EEO / Demographic Questions (voluntary — use application_defaults.md)
7. Review & Submit

---

## Critical Rules for Avature

1. **Verify after every interaction** — a click executing ≠ state changed
2. **Never use pixel coordinates for radio buttons** — always get fresh ref IDs from `read_page`
3. **Custom comboboxes require the type-and-wait pattern** — do not use `form_input`
4. **EEO fields are voluntary** — use `application_defaults.md` values and stop/ask if a field isn't covered
5. **After page scroll, re-fetch ref IDs** — don't reuse refs from before a scroll

---

## Reliability Log

| Date | Company | Issues Encountered | Resolution |
|------|---------|-------------------|------------|
| YYYY-MM-DD | *(your company)* | *(issues encountered)* | *(resolution)* |

---

## Notes

- Avature is used by Avature employer, major consulting firms, and several Fortune 500 companies
- Some Avature deployments have custom fields added by the employer — not documented here
- If you encounter a field type not covered above, stop and document the fix in this file
