# KNOWN_ISSUES.md

**Project:** ApplyChain  
**Last Updated:** 2026-05-28

---

## Active Issues

### Issue #001 — ATS Adapters Are Stubs Only
**Status:** Open  
**Severity:** Medium  
**Description:** The adapter files in `adapters/` document known ATS quirks and provide strategy guidance, but are not executable automation scripts. Each user must adapt them to their specific platform versions and form layouts.  
**Mitigation:** Follow the tiered interaction strategy documented in `docs/browser_automation_guide.md`.  
**Resolution:** Build and test per-platform automation flows iteratively as you encounter each ATS.

---

### Issue #002 — No Automated Duplicate Detection
**Status:** Open  
**Severity:** Medium  
**Description:** No automated logic checks `logs/applications_log.csv` before beginning an application workflow. Risk of applying to the same role twice if the log isn't manually checked.  
**Mitigation:** Check the log manually before starting any application pipeline.  
**Resolution:** Implement duplicate detection script in Phase 4.

---

### Issue #003 — React ATS Interaction Failures (Avature and Similar SPAs)
**Status:** Documented / Partially Mitigated  
**Severity:** High  
**Description:** On React-based ATS platforms (e.g., Avature, some Workday versions), fields may appear to accept input but not actually update React state. Root causes include: React synthetic event mismatch, coordinate drift after scroll, custom ARIA comboboxes not responding to `form_input`.  
**Mitigation:** Use the tiered interaction strategy and DOM-aware helpers in `browser_helpers/interaction_helpers.js`. Always verify visible state after every field interaction.  
**Resolution:** Apply tiered interaction strategy; see `adapters/avature.md` for platform-specific notes.

---

### Issue #004 — Profile Knowledge Base Is Empty By Default
**Status:** Expected (setup required)  
**Severity:** High  
**Description:** All profile_knowledge_base files ship as blank templates. No application material can be generated until you fill them in.  
**Mitigation:** Complete the setup checklist in TODO.md before running any application workflow.  
**Resolution:** User action required.

---

## Resolved Issues

*(none yet — add entries as you fix things)*

---

## Notes

- Severity levels: **Critical** (blocks all work), **High** (blocks key workflow), **Medium** (workaround exists), **Low** (minor inconvenience)
- Add new issues as you discover them during application workflows
