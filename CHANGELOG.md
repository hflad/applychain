# Changelog

All notable changes to ApplyChain are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-06-03

### Added
- **CLAUDE.md** — Lean session index for on-demand file loading; replaces monolithic context loading
- **Prerequisites section** in README — explicit list of required software and subscriptions
- **STARTER.md surfaced** as Step 0 of Quick Start — the fastest path to a working workspace
- **Dashboard launch instructions** — `streamlit run dashboard.py` added to README and setup.sh
- **`docs/first_application.md`** — Complete step-by-step narrative walkthrough of a first application
- **`adapters/README.md`** — Explains adapter format, available platforms, and contribution guide
- **GitHub issue templates** — bug report and new ATS adapter templates
- **`CHANGELOG.md`** — This file

### Changed
- README Quick Start Step 4 rewritten with concrete 7-step workflow
- CHANGELOG extracted from README into standalone file
- `scripts/setup.sh` now installs `streamlit` and `pandas`; next-steps updated
- CREDITS.md closing section revised for open-source audience

### Fixed
- `.gitignore` misleading comment on `system/` line removed

---

## [0.2.0] — 2026-05-28

### Added
- **playwright_engine** — Full Human-Simulation Interaction Engine (`system/`): human-first scroll→hover→click→type→verify primitives, 7-signal weighted confidence scoring, React rerender detection, CDP connection to existing Chrome session
- **VerificationFramework** (`system/verification.py`) — 6 platform-agnostic verification primitives: `verify_input_value`, `verify_radio_selected`, `verify_dropdown_value`, `verify_text_present`, `verify_submit_enabled`, `capture_verification_snapshot`
- **Verification CLI** — `verify-input`, `verify-radio`, `verify-dropdown`, `verify-text`, `verify-submit`, `snapshot` subcommands added to `system/cli.py`
- **ATS adapters** — Taleo (tested end-to-end), Avature (observed), Workday (documented), Greenhouse (documented)
- **GOVERNANCE.md** — Agent governance contract: Claude is orchestrator, playwright_engine is execution-only helper
- **Dedicated debug browser guide** — `docs/browser_automation_guide.md` updated with dual-browser setup rationale and `--user-data-dir` isolation
- **KNOWN_ISSUES.md** — Honest tracker of open issues and workarounds

### Changed
- ATS platform notes moved from inline docs to `docs/ats_platforms/` for easier maintenance
- Repo cleanup: scratch test files removed

---

## [0.1.0] — 2026-05-01

### Added
- Full project scaffold with profile_knowledge_base templates
- `system/truth_database.json` architecture (truth-constrained generation)
- Resume pipeline with 4-evaluator scoring (ATS, Recruiter, Hiring Manager, Technical Lead)
- Cover letter generator (≤250 words, role-specific)
- `logs/applications_log.csv` tracker
- Streamlit dashboard (`dashboard.py`)
- `browser_helpers/interaction_helpers.js` — DOM-aware JS fallback helpers for Chrome automation
- Pre-commit PII guard hook
- `prompts/` — model-agnostic prompt templates for gap analysis, resume tailoring, cover letter, job scoring
- `HUMAN_CHECKPOINTS.md` — 9-checkpoint mandatory approval gate specification
- `MODEL_INSTRUCTIONS.md` — Non-negotiable agent behavior rules
