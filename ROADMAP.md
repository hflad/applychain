# ROADMAP.md

**Project:** ApplyChain  
**Last Updated:** 2026-05-28

---

## Phase 1 — Foundation ✅

- [x] Profile Knowledge Base templates
- [x] Folder structure
- [x] Log initialization script
- [x] Core documentation (README, ARCHITECTURE, SECURITY, etc.)
- [x] `.env.example` and `.gitignore`

---

## Phase 2 — Resume Intelligence

- [ ] JD keyword extractor prompt
- [ ] Gap analysis prompt (JD vs. Profile KB)
- [ ] Resume tailor prompt (truth-constrained bullet prioritization)
- [ ] ATS evaluator prompt (keyword density, formatting score)
- [ ] Recruiter skim evaluator (6-second readability)
- [ ] Hiring manager evaluator (relevance + narrative)
- [ ] Technical evaluator (tech depth + specificity)
- [ ] Iterative improvement loop (evaluate → improve → stop at threshold)
- [ ] Resume export via `scripts/resume_builder.py`

---

## Phase 3 — Cover Letter Engine

- [ ] Cover letter generation prompt
- [ ] Human approval gate
- [ ] Export to .docx
- [ ] Company research module (web context pull)

---

## Phase 4 — Job Discovery & Matching

- [ ] LinkedIn job discovery workflow (Claude for Chrome)
- [ ] Manual JD ingestion (URL or paste)
- [ ] Fit scoring algorithm
- [ ] Duplicate detection against log
- [ ] Job ranking view

---

## Phase 5 — Browser Automation

- [ ] ATS type detection
- [ ] SSO/Google login flow
- [ ] Form autofill (radio buttons, comboboxes, text inputs, file uploads)
- [ ] Resume + cover letter upload
- [ ] Sensitive question handler
- [ ] Multi-step workflow navigator
- [ ] Human approval gate before submit
- [ ] Post-submit log update
- [ ] CAPTCHA detection + pause
- [ ] Per-platform ATS adapters (Workday, Greenhouse, Lever, Taleo, iCIMS, Avature)
- [ ] State verification after every field fill
- [ ] Automatic retry with fallback tier on silent failures

---

## Phase 6 — Tracking & Reporting

- [ ] Application status tracker (applied, interviewing, rejected, offer)
- [ ] Recruiter contact log
- [ ] Weekly summary report
- [ ] Error/retry log
- [ ] Export to .xlsx for review

---

## Phase 7 — Advanced Features (Future)

- [ ] LinkedIn outreach drafts
- [ ] Salary range research per role
- [ ] Interview prep document generator
- [ ] Company culture fit scoring
- [ ] Follow-up email drafts
- [ ] Application analytics dashboard
- [ ] Scheduled daily job digest

---

## Phase 8 — Fully Agentic Workflows (Long-Term Vision)

ApplyChain is designed to support progressively more autonomous operation as users develop trust in the system's outputs. Phase 8 represents the long-term direction — not a replacement for human oversight, but an evolution of it.

The model: **start fully supervised → loosen gates as trust is earned → eventually schedule and run pipelines unattended, with async approval where needed.**

- [ ] **Configurable checkpoint levels** — let users dial oversight up or down per workflow stage (e.g., auto-approve gap analysis but always require resume approval)
- [ ] **Scheduled job discovery** — daily digest of new roles scored against your profile, delivered without manual triggering
- [ ] **Batch application queue** — queue multiple pre-approved roles; agent works through them sequentially with a single end-of-session review
- [ ] **Async approval gates** — agent pauses at checkpoints and notifies you (email, push, or dashboard flag) rather than blocking in chat
- [ ] **Trust scoring** — track AI accuracy over time (did approved resumes perform well? were gap analyses accurate?) to inform how much autonomy to grant
- [ ] **Fully unattended pipeline** — for users who have established trust: discover → score → generate → submit, with human review only for outliers or low-confidence cases
- [ ] **Audit log** — every autonomous action logged with reasoning, inputs, and outputs for post-hoc review

> The human approval gates in v1.0.0 are not a permanent ceiling — they are a starting point. The goal is an agent you trust enough to run overnight.
