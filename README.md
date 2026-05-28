# ApplyChain

> A local-first, human-supervised AI job application framework.  
> Bring your own agent. Runs on your machine. Never submits without your approval.

---

## Philosophy

Most "AI job application" tools optimize for volume: spray résumés, auto-submit, hope something sticks. ApplyChain takes the opposite approach.

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
4. **Resume Tailoring** — Your agent generates a tailored resume variant using only approved profile facts. Missing metrics are marked `[FILL IN]`, not invented.
5. **Cover Letter Generation** — Concise (≤250 words), role-specific, avoids generic AI phrasing.
6. **Human Review Gate** — You review resume + cover letter before anything is exported or submitted.
7. **Browser Automation** — Your agent fills ATS forms using your profile data, with a mandatory approval pause before the final submit button is ever clicked.
8. **Application Logging** — Every application is logged to `logs/applications_log.csv` with status, files, and notes.

---

## What Agent Platform Do You Need?

ApplyChain is designed to work with any capable AI agent that can read files, run prompts, and control a browser. You need three things:

| Capability | Why It's Needed |
|-----------|----------------|
| File access (read/write to local folders) | Reading your Profile KB, saving resumes and logs |
| Prompt execution | Running gap analysis, resume tailoring, cover letter generation |
| Browser automation | Filling ATS forms and navigating job portals |

### Reference Implementation (fully tested)

The reference implementation uses **Claude** and has been tested end-to-end:

- **[Claude for Desktop](https://claude.ai/download)** (Pro or Max plan) with Cowork mode — provides file access and prompt execution
- **[Claude for Chrome extension](https://claude.ai/download)** — provides browser automation

Everything in `prompts/`, `adapters/`, `browser_helpers/`, and `docs/` was written against this setup. If you're on Claude, you get the most complete, battle-tested experience.

### Other Platforms

If you're running a different agent stack — OpenAI Codex, Gemini, a custom LangChain pipeline, or anything else with file access + browser control — ApplyChain's structure is designed to be portable:

- **`profile_knowledge_base/`** is plain markdown — readable by any model
- **`prompts/`** are model-agnostic prompt templates — paste them into any system
- **`adapters/`** are human-readable ATS guides — useful regardless of automation layer
- **`browser_helpers/interaction_helpers.js`** is vanilla JavaScript — injectable by any browser automation tool (Playwright, Puppeteer, Selenium, etc.)
- **`MODEL_INSTRUCTIONS.md`** and **`HUMAN_CHECKPOINTS.md`** can be adapted as system prompts for any agent framework

The main caveat: the `docs/browser_automation_guide.md` and ATS adapter notes reference Claude for Chrome's specific tool names (`read_page`, `form_input`, `file_upload`, etc.). You'll need to translate those to your platform's equivalent actions.

**Contributions welcome** — if you get ApplyChain running on another platform, a PR with platform-specific adapter notes would benefit the whole community.

---

## Quick Start

### 1. Install Dependencies

```bash
bash scripts/setup.sh
```

This installs Python dependencies, initializes the application log, and sets up the pre-commit PII guard.

Or manually:
```bash
pip install python-docx openpyxl
cp .env.example .env
python3 scripts/init_log.py
```

### 2. Fill In Your Profile

Open each file in `profile_knowledge_base/` and replace the placeholder content with your real information. See [`profile_knowledge_base/README.md`](./profile_knowledge_base/README.md) for privacy instructions before you start.

```
profile_knowledge_base/
├── experience.md           Work history, roles, responsibilities, achievements
├── education.md            Degrees, institutions, GPA (if you want to include it)
├── skills.md               Technical skills, tools, languages, frameworks
├── projects.md             Personal/side projects with descriptions
├── certifications.md       Completed or in-progress certifications
├── metrics.md              Quantified achievements (%, $, volume, speed)
├── preferences.md          Role types, company types, salary floor, work style
├── desired_locations.txt   Preferred cities/regions, ranked
├── desired_roles.txt       Target job titles, ranked
└── application_defaults.md Demographic/compliance question defaults
```

> **Only put true, verifiable information here.** The AI will never add to what you provide — it can only select, reorder, and rephrase.

### 3. Configure Credentials

```bash
# Edit .env with your API key and any platform credentials
```

### 4. Run Your First Application

Point your agent at a job description. Walk it through the pipeline using the prompts in `prompts/` as starting points: gap analysis → resume tailoring → your review → cover letter → your review → form fill → your approval → submit.

---

## Folder Structure

```
applychain/
├── profile_knowledge_base/    # YOUR truth: experience, skills, preferences
├── prompts/                   # Reusable prompt templates (model-agnostic)
├── adapters/                  # ATS platform interaction guides
├── browser_helpers/           # DOM-aware JS helpers for browser automation
├── scripts/                   # Document generation and utility scripts
├── scheduler/                 # Scheduled task configs (optional)
├── notifications/             # Notification templates (optional)
├── templates/                 # Blank document templates
├── examples/                  # Sanitized sample application bundle
├── docs/                      # Guides, ATS notes, troubleshooting
├── hooks/                     # Git hooks (pre-commit PII guard)
├── resumes/                   # Generated tailored resumes (gitignored)
├── cover_letters/             # Generated cover letters (gitignored)
├── job_descriptions/          # Saved JDs (gitignored)
├── applications/              # Per-application bundles (gitignored)
├── logs/                      # applications_log.csv (gitignored)
└── exports/                   # Final PDFs and packages (gitignored)
```

---

## Browser Automation

The `adapters/` folder documents ATS-specific interaction strategies for Workday, Greenhouse, Lever, Taleo, iCIMS, Avature, and SuccessFactors. The `browser_helpers/interaction_helpers.js` file provides DOM-aware JavaScript utilities for React-heavy ATS platforms — compatible with any browser automation tool that can inject JavaScript.

See [`docs/browser_automation_guide.md`](./docs/browser_automation_guide.md) for the full interaction strategy and known platform quirks.

---

## Security

- Credentials live in `.env` only — never in prompts, logs, documents, or markdown
- A pre-commit hook scans staged files for email addresses, phone numbers, and `.env` files before any commit lands
- `profile_knowledge_base/` should be gitignored once you fill it in (see instructions in that folder)
- The system must pause and ask you before entering or submitting any sensitive data

See [SECURITY.md](./SECURITY.md) for the full security model.

---

## Human Checkpoints

These gates are **mandatory** — the AI must stop and wait at each one regardless of platform:

| Gate | When |
|------|------|
| Profile review | Before generating any application material |
| Resume approval | Before exporting resume to .docx |
| Cover letter approval | Before exporting cover letter |
| Pre-submission review | After form fill, before clicking Submit |
| Post-submission log | After any submission |

See [`MODEL_INSTRUCTIONS.md`](./MODEL_INSTRUCTIONS.md) and [`HUMAN_CHECKPOINTS.md`](./HUMAN_CHECKPOINTS.md) for the full checkpoint definitions and required behavior for each gate.

---

## Contributing

Pull requests welcome — especially for new ATS adapters, platform-specific setup guides, and browser helper improvements. See [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](./LICENSE).
