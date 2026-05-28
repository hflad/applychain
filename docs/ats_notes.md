# ATS Platform Notes

Running reliability tracker for each ATS platform encountered.

---

## Reliability Scale

| Rating | Meaning |
|--------|---------|
| 5/5 | All standard interactions work reliably with native Chrome MCP |
| 4/5 | Minor quirks; one or two fields need fallback helpers |
| 3/5 | Significant quirks; fallback helpers required for several field types |
| 2/5 | Unreliable; most interactions need DOM helpers or manual steps |
| 1/5 | Not automatable in current state; manual application recommended |

---

## Platform Summaries

### Avature
**Rating:** 3/5  
**Used by:** Avature employer, major consulting firms  
**Key quirks:**
- Custom ARIA comboboxes don't respond to `form_input` — use type-and-wait pattern
- Radio button coordinates drift after scroll — use ref IDs from `read_page`
- Native `<select>` elements work fine with `form_input`
- File upload works via `file_upload` tool

See `adapters/avature.md` for full strategy guide.

---

### Greenhouse
**Rating:** Not yet tested  
See `adapters/greenhouse.md`

---

### Workday
**Rating:** Not yet tested  
See `adapters/workday.md`

---

### Lever
**Rating:** Not yet tested  
See `adapters/lever.md`

---

### Taleo (Oracle)
**Rating:** Not yet tested  
See `adapters/taleo.md`

---

### iCIMS
**Rating:** Not yet tested  
See `adapters/icims.md`

---

### SAP SuccessFactors
**Rating:** Not yet tested  
See `adapters/successfactors.md`

---

### Paycom
**Rating:** 5/5  
**Used by:** Various employers  
**Key notes:** Standard HTML forms; all native interactions work. Smooth multi-step wizard.

---

## Adding New Platforms

When you encounter a new ATS:
1. Note the platform name (check page title, URL, or "Powered by X" footer)
2. Document any interaction failures and their fixes
3. Add a row to this file and create an adapter stub in `adapters/`
