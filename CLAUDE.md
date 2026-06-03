# ApplyChain — Session Index

This file is the only doc Claude loads at session start. Everything else is loaded on demand.

## Identity
- Project: ApplyChain
- Architecture reference: ARCHITECTURE.md (load only if asked about system design)

## Load on demand — by task type

| Task | Load these files |
|---|---|
| Generate resume or cover letter | `profile_knowledge_base/` (relevant files only), the specific JD from `job_descriptions/` |
| Score / gap-analyze a JD | `profile_knowledge_base/experience.md`, `profile_knowledge_base/skills.md`, the specific JD file |
| Fill application form | `profile_knowledge_base/application_defaults.md`, `system/ats_notes.md` (if present) |
| Check for duplicate application | `logs/applications_log.csv` (last 50 rows only) |
| Review a past application | The specific folder under `applications/` |
| Browser automation | `docs/ats_notes.md`, the relevant file under `docs/ats_platforms/` |

Do NOT load all JDs, all application bundles, or all docs at session start.

## Key file locations

- Profile facts: `profile_knowledge_base/` (experience, skills, education, projects, metrics, certifications, preferences)
- Sensitive question defaults: `profile_knowledge_base/application_defaults.md`
- Application log: `logs/applications_log.csv`
- Job descriptions: `job_descriptions/[Company]_[Role]_JD_YYYY-MM-DD.txt`
- Resumes: `resumes/[Company]_[Role]_Resume_YYYY-MM-DD.docx`
- Cover letters: `cover_letters/[Company]_[Role]_CoverLetter_YYYY-MM-DD.docx`
- Application bundles: `applications/[Company]_[Role]_YYYY-MM-DD/`
- Prompt templates: `prompts/` (load only the relevant prompt)
- Checkpoint rules: `HUMAN_CHECKPOINTS.md` (load only when a checkpoint situation arises)

## Core constraints (always enforced, no file load needed)

1. Generate content ONLY from `profile_knowledge_base/` — never invent facts
2. Use `[FILL IN]` for any gap between JD requirements and profile facts
3. Require explicit user approval before: exporting any document, clicking Submit
4. Never enter passwords, SSNs, or credentials into any form
5. Never read or surface `.env` file contents
6. Stop and notify user on: CAPTCHA, unexpected page, login prompt, low automation confidence
7. Log every completed or attempted application to `logs/applications_log.csv`
