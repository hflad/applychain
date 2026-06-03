---
name: New ATS adapter
about: Document a new ATS platform or improve an existing adapter
labels: adapter, contribution
---

## ATS Platform

Name and any URL patterns that identify it (e.g., `*.wd1.myworkdayjobs.com`).

## Status

- [ ] Tested end-to-end (full application submitted successfully)
- [ ] Partially tested (some steps work, others need verification)
- [ ] Theoretical / documented from observation only

## Interaction summary

**Field targeting strategy:** (label text, ref IDs, ARIA roles, etc.)

**Fields requiring special handling:**
- [ ] Date pickers
- [ ] Select2 / custom dropdowns
- [ ] React-controlled inputs
- [ ] File upload (describe mechanism)
- [ ] Multi-step wizard

## Known failure modes

Describe any fields or flows that fail with native Chrome extension interactions and what fallback works.

## Sample form URL

A public job posting on this ATS so others can reproduce your findings. (Do not link to a specific role you're applying for.)

## Additional notes

Anything else that would help someone adapting this guide to their specific form layout.
