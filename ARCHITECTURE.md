# ARCHITECTURE.md

**Project:** ApplyChain  
**Last Updated:** 2026-05-28  
**Version:** 1.0.0

---

## Overview

ApplyChain is a local-first, AI-assisted job application pipeline. It helps you identify strong-fit roles, generate truth-constrained application materials, and automate browser form-fill workflows — with mandatory human approval gates before any submission.

All processing runs locally. No data is sent to external services beyond LLM API calls. Credentials are stored in environment variables only.

---

## Folder Structure

```
ApplyChain/
├── profile_knowledge_base/    # Single source of truth: your approved facts
├── prompts/                   # Reusable Claude prompt templates
├── adapters/                  # Per-ATS platform interaction guides
├── browser_helpers/           # DOM-aware JS fallback helpers
├── scripts/                   # Document generation + utility scripts
├── scheduler/                 # Scheduled task configs
├── notifications/             # Notification templates
├── templates/                 # Blank document templates
├── examples/                  # Sanitized sample application bundle
├── docs/                      # Guides and troubleshooting
├── resumes/                   # Generated tailored resumes (gitignored)
├── cover_letters/             # Generated cover letters (gitignored)
├── job_descriptions/          # Saved JDs (gitignored)
├── applications/              # Per-application bundles (gitignored)
├── logs/                      # applications_log.csv + error logs (gitignored)
└── exports/                   # Final PDFs and packages (gitignored)
```

---

## Core Modules

### 1. Profile Knowledge Base
- Source of truth for all generated content
- Structured markdown files covering experience, education, skills, projects, certifications, metrics, and preferences
- The AI may rephrase and prioritize — it may never add, invent, or fabricate

### 2. Job Intake & Scoring
- Accepts JD text or URL
- Scores fit against profile (skill overlap, seniority, keyword match)
- Deduplicates against `logs/applications_log.csv`
- Rejects weak-fit roles rather than mass-applying

### 3. Gap Analysis
- Compares JD requirements to profile facts
- Surfaces alignment, partial matches, and honest gaps
- Never invents a gap-filler — flags it as `[FILL IN]`

### 4. Resume Intelligence Pipeline
- Parses JD keywords, required skills, preferred qualifications
- Generates tailored resume using ONLY approved profile content
- Evaluates through four simulated reviewer lenses:
  - **ATS Parser** — keyword density, formatting compliance
  - **Recruiter Skim (6-second)** — headline clarity, impact visibility
  - **Hiring Manager** — role relevance, narrative coherence
  - **Technical Lead** — tech depth, project specificity

### 5. Cover Letter Generator
- ≤250 words unless instructed otherwise
- Role and company specific
- Factually grounded in profile_knowledge_base
- Avoids generic AI phrasing

### 6. Human Approval Gates
Required before:
- Resume export to .docx
- Cover letter finalization
- Any application submission
- Answering freeform/custom questions

### 7. Browser Automation (Claude for Chrome) — Hybrid Interaction Architecture
- Detects ATS provider (Workday, Greenhouse, Lever, Taleo, iCIMS, Avature, etc.)
- Autofills forms from profile data using tiered interaction strategy
- Uploads resume and cover letter files
- Stops at CAPTCHA, unexpected flows, or missing required data
- Mandatory approval pause before Submit

#### Interaction Tier Priority
1. **Native Chrome MCP** — `left_click`, `type`, `form_input` (always try first)
2. **Label-aware** — target by ref IDs from `read_page`; match label text
3. **Focus-and-retry** — click → wait → verify state → retry once
4. **DOM-aware helpers** — `browser_helpers/interaction_helpers.js` via `javascript_tool` (fallback only)

**Critical rule:** A click executing does NOT mean UI state changed. Always verify the visible frontend state after every important interaction before proceeding.

#### Layered Architecture
```
Claude reasoning / orchestration
          ↓
Chrome MCP (native interactions)
          ↓
Label-aware + ref-based targeting
          ↓
DOM-aware helpers (interaction_helpers.js)
          ↓
ATS websites
```

### 8. Sensitive Question Handling
- Source of truth: `profile_knowledge_base/application_defaults.md`
- Never infers protected attributes
- Uses "decline to answer" where appropriate and available
- Human override allowed before any submission

### 9. Tracking & Logging
- `logs/applications_log.csv` — canonical tracker
- Columns: date, company, role, jd_url, ats_platform, status, resume_file, cover_letter_file, match_score, notes

---

## Data Flow

```
JD Input
  └─► Job Scorer (fit score + dedup)
        └─► [APPROVED] Gap Analysis
              └─► Resume Engine (profile_knowledge_base)
                    └─► Evaluator Agents (ATS / Recruiter / HM / Tech)
                          └─► [HUMAN REVIEW]
                                └─► Cover Letter Generator
                                      └─► [HUMAN REVIEW]
                                            └─► Browser Automation
                                                  └─► [HUMAN APPROVAL]
                                                        └─► Submit + Log
```

---

## Security Model

- Local-first: all data stays on disk
- Credentials in `.env` only — never in prompts, logs, or documents
- LLM reasoning is isolated from credential access
- See [SECURITY.md](./SECURITY.md) for full details

---

## Technology Stack

| Layer | Technology |
|---|---|
| Orchestration | Claude (Cowork / Claude Desktop) |
| Browser automation | Claude for Chrome extension |
| Document generation | python-docx, openpyxl |
| Data storage | JSON/Markdown + CSV logs |
| Version control | Git |
| Secrets | `.env` / OS keychain |
