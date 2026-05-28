# ApplyChain

> A local-first, human-supervised AI job application assistant.  
> Built on Claude. Runs on your machine. Never submits without your approval.

---

## Philosophy

Most "AI job application" tools optimize for volume: spray résumés, auto-submit, hope something sticks. This project takes the opposite approach.

**Principles:**

- **Truth-constrained** — The AI may rephrase, reorder, and emphasize, but it may never invent experience, fabricate metrics, or claim technologies you haven't used. Every generated document traces back to your [Profile Knowledge Base](./profile_knowledge_base/).
- **Human-gated** — Every resume, cover letter, and form submission requires your explicit review and approval before anything is finalized or sent. The AI is a drafter and navigator, not an autonomous agent.
- **Local-first** — Your résumé facts, credentials, and application history stay on your machine. No cloud sync, no third-party data sharing beyond LLM API calls.
- **Quality over quantity** — One well-targeted application beats ten generic ones. The system is designed to help you find strong-fit roles and present yourself accurately and compellingly.
- **Transparent** — Every decision, gap, placeholder, and assumption is surfaced to you. Nothing is hidden or auto-resolved.

---

## What This Does

1. **Profile Knowledge Base** — You fill in structured markdown templates with your real experience, projects, skills, and preferences. This is the single source of truth for all generated content.
2. **Job Intake** — Paste a job description URL or text. The system scores it against your profile and saves it.
3. **Gap Analysis** — A prompt compares the JD requirements against your profile, surfacing alignment and gaps honestly.
4. **Resume Tailoring** — Claude generates a tailored resume variant using only approved profile facts. Missing metrics are marked `[FILL IN]`, not invented.
5. **Cover Letter Generation** — Concise (≤250 words), role-specific, avoids generic AI phrasing.
6. **Human Review Gate** — You review resume + cover letter before anything is exported or submitted.
7. **Browser Automation** — Claude for Chrome fills ATS forms using your profile data, with a mandatory approval pause before the final submit button is ever clicked.
8. **Application Logging** — Every application is logged to `logs/applications_log.csv` with status, files, and notes.

---

## Quick Start

### 1. Prerequisites

- [Claude for Desktop](https://claude.ai/download) with Cowork mode enabled
- [Claude for Chrome extension](https://chrome.google.com/webstore/detail/claude-for-chrome/) installed
- Python 3.9+ (for document generation scripts)
- `pip install python-docx openpyxl` (or use the provided `scripts/setup.sh`)

### 2. Fill In Your Profile

Open each file in `profile_knowledge_base/` and replace the placeholder content with your real information:

```
profile_knowledge_base/
├── experience.md        ← Work history, roles, responsibilities, achievements
├── education.md         ← Degrees, institutions, GPA (if you want to include it)
├── skills.md            ← Technical skills, tools, languages, frameworks
├── projects.md          ← Personal/side projects with descriptions
├── certifications.md    ← Completed or in-progress certifications
├── metrics.md           ← Quantified achievements (%, $, volume, speed)
├── preferences.md       ← Role types, company types, salary floor, work style
├── desired_locations.txt← Preferred cities/regions, ranked
├── desired_roles.txt    ← Target job titles, ranked
└── application_defaults.md ← Demographic/compliance question defaults
```

> **Important:** Only put true, verifiable information here. The AI will never add to what you provide — it can only select, reorder, and rephrase.

### 3. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your Claude API key and any other needed credentials
```

### 4. Run Your First Application

Open Claude (Cowork mode) and paste a job description. Claude will walk you through the full pipeline: gap analysis → resume → cover letter → your review → form fill → your approval → submit.

---

## Folder Structure

```
ApplyChain/
├── profile_knowledge_base/    # YOUR truth: experience, skills, preferences
├── prompts/                   # Reusable Claude prompt templates
│   ├── gap_analysis.md
│   ├── resume_tailor.md
│   ├── cover_letter.md
│   ├── ats_evaluator.md
│   ├── recruiter_evaluator.md
│   ├── hiring_manager_evaluator.md
│   └── technical_evaluator.md
├── adapters/                  # ATS platform-specific automation guides
│   ├── workday.md
│   ├── greenhouse.md
│   ├── lever.md
│   ├── taleo.md
│   ├── icims.md
│   ├── avature.md
│   └── successfactors.md
├── browser_helpers/           # DOM-aware JS helpers for browser automation
│   └── interaction_helpers.js
├── scripts/                   # Document generation and utility scripts
│   ├── setup.sh
│   ├── resume_builder.py
│   └── init_log.py
├── scheduler/                 # Scheduled task configs (optional)
├── notifications/             # Notification templates (optional)
├── templates/                 # Blank .docx/.xlsx/.txt templates
├── examples/                  # Sample application bundle (sanitized)
├── docs/                      # Additional guides
│   ├── ats_notes.md
│   ├── browser_automation_guide.md
│   └── troubleshooting.md
├── resumes/                   # Generated tailored resumes (.docx)
├── cover_letters/             # Generated cover letters (.docx)
├── job_descriptions/          # Saved JDs (.txt)
├── applications/              # Per-application bundles
├── logs/                      # applications_log.csv + error logs
└── exports/                   # Final PDFs and submission-ready packages
```

---

## Browser Automation

Browser automation uses the Claude for Chrome extension. Claude navigates ATS forms, fills fields from your profile, uploads documents, and stops at every sensitive decision point. It will never click Submit without an explicit approval message from you in chat.

**ATS platforms with documented adapters:**
- Workday, Greenhouse, Lever, Taleo, iCIMS, Avature, SuccessFactors

See [`docs/browser_automation_guide.md`](./docs/browser_automation_guide.md) for interaction strategy, known quirks, and fallback tiers.

---

## Security

- Credentials live in `.env` only — never in prompts, logs, documents, or markdown
- `.env` is gitignored; use `.env.example` as a template
- Sensitive question defaults (demographics, authorization) are stored in `profile_knowledge_base/application_defaults.md` and never inferred
- The system will pause and ask you before entering or submitting any sensitive data

See [SECURITY.md](./SECURITY.md) for the full security model.

---

## Human Checkpoints

These gates are **mandatory** and cannot be bypassed by the AI:

| Gate | When |
|------|------|
| Profile review | Before generating any application material |
| Resume approval | Before exporting resume to .docx |
| Cover letter approval | Before exporting cover letter to .docx |
| Pre-submission review | After form fill, before clicking Submit |
| Post-submission log | After any submission |

See [`MODEL_INSTRUCTIONS.md`](./MODEL_INSTRUCTIONS.md) and [`HUMAN_CHECKPOINTS.md`](./HUMAN_CHECKPOINTS.md) for details.

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Pull requests welcome for new ATS adapters, prompt improvements, and browser helper functions.

---

## License

MIT — see [LICENSE](./LICENSE).

---

*Built with [Claude](https://claude.ai) and the [Claude for Chrome](https://chrome.google.com/webstore/detail/claude-for-chrome/) extension.*
