# ATS Adapters

This folder contains platform-specific strategy guides for Applicant Tracking Systems (ATS). Each file documents known interaction quirks, reliable form-fill approaches, and fallback strategies for a specific platform.

**These are human-readable strategy documents, not executable scripts.** Your AI agent reads them to understand how to interact with each platform. They are not code you run directly.

---

## Available Adapters

| File | Platform | Status |
|------|----------|--------|
| `workday.md` | Workday | Documented |
| `greenhouse.md` | Greenhouse | Documented |
| `taleo.md` | Taleo | Tested end-to-end |
| `avature.md` | Avature | Observed — partial |
| `icims.md` | iCIMS | Documented |
| `lever.md` | Lever | Documented |
| `successfactors.md` | SAP SuccessFactors | Documented |

See `docs/ats_notes.md` for a running log of real-world observations across platforms.

---

## How Adapters Are Used

When your agent detects or is told which ATS platform a job application uses, it reads the relevant adapter file before beginning form fill. The adapter tells it:

- How to identify form fields reliably (ref IDs, label text, ARIA attributes)
- Which interaction tier to use for each field type (native click vs. DOM helpers)
- Known failure modes and how to recover from them
- Platform-specific quirks (React state management, custom dropdowns, file upload behavior)

---

## Contributing a New Adapter

If you successfully complete an application on a platform not listed here, a PR with an adapter doc would benefit the whole community. See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

A good adapter doc includes:
- ATS name and any URL patterns that identify it
- Reliable field targeting strategy (label text, ref IDs, or ARIA roles)
- Any fields that require special handling (Select2, React-controlled inputs, date pickers)
- File upload behavior (hidden input vs. button-triggered dialog)
- Known failure modes and workarounds
- Whether the platform has been tested end-to-end or is theoretical
