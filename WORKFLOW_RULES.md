# WORKFLOW_RULES.md

Operational rules for running the ApplyChain pipeline. These govern sequencing, naming, saving, and error handling across all workflows.

---

## File Naming Conventions

| Artifact | Pattern | Example |
|----------|---------|---------|
| Resume | `[Company]_[Role]_Resume_YYYY-MM-DD.docx` | `Acme_DataAnalyst_Resume_2026-05-28.docx` |
| Cover Letter | `[Company]_[Role]_CoverLetter_YYYY-MM-DD.docx` | `Acme_DataAnalyst_CoverLetter_2026-05-28.docx` |
| Job Description | `[Company]_[Role]_JD_YYYY-MM-DD.txt` | `Acme_DataAnalyst_JD_2026-05-28.txt` |
| Application Log | `applications_log.csv` | *(fixed name)* |

Use underscores, not spaces. Use the exact company name as it appears in the job posting. Abbreviate long role titles if necessary (e.g., `SrDataEng` for "Senior Data Engineer").

---

## Pipeline Sequencing

Every application must follow this order. Do not skip steps.

```
1. Save JD to job_descriptions/
2. Score JD fit against profile
3. Run gap analysis
4. Generate tailored resume draft
5. Run 4-evaluator scoring
6. [HUMAN REVIEW] — resume
7. Export resume to resumes/
8. Generate cover letter draft
9. [HUMAN REVIEW] — cover letter
10. Export cover letter to cover_letters/
11. Open application form
12. Fill form fields from profile
13. Upload resume and cover letter
14. [HUMAN REVIEW] — full form before submit
15. [HUMAN APPROVAL] — explicit "yes, submit"
16. Submit
17. Update logs/applications_log.csv
18. Save application bundle to applications/
```

---

## Saving Rules

- Save the JD before beginning any analysis
- Save all generated drafts before showing them for review
- Save final .docx files before opening the application form
- Save the log entry before closing the browser session
- If a workflow is interrupted, save whatever has been completed and note the interruption in the log

---

## Pre-Submission Checklist

Before the user approves submission, show:
1. Tailored resume (filename + key tailoring decisions)
2. Cover letter (full text)
3. Detected ATS platform
4. Match score (0–100) with brief rationale
5. Any identified gaps or risks
6. Any `[FILL IN]` placeholders that were not resolved

Do not proceed until the user explicitly approves all five items.

---

## Duplicate Detection

Before starting a new application:
1. Check `logs/applications_log.csv` for the company + role combination
2. If a matching row exists with status `applied`, `interviewing`, or `offer` — stop and notify the user
3. If a matching row exists with status `viewed` or `archived` — flag it and ask whether to proceed

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Required form field can't be filled | Stop, notify user, wait for guidance |
| CAPTCHA appears | Stop immediately, notify user |
| Login wall encountered | Stop, invite user to authenticate, then resume |
| Unexpected page or flow | Stop, take screenshot, describe what was seen, ask how to proceed |
| Automation confidence is low (field state uncertain after 2 attempts) | Stop, describe the field state, ask user to fill manually |
| Form submit fails or shows error | Do NOT retry automatically — notify user and describe the error |

When in doubt, pause. Reliability is more important than speed.

---

## Application Log Schema

`logs/applications_log.csv` columns:

| Column | Description |
|--------|-------------|
| `date` | ISO date of submission (YYYY-MM-DD) |
| `company` | Company name |
| `role` | Job title as listed in the posting |
| `jd_url` | URL of the job posting (if available) |
| `ats_platform` | Detected ATS (Workday, Greenhouse, etc.) |
| `status` | `viewed` / `applied` / `interviewing` / `rejected` / `offer` / `archived` |
| `resume_file` | Filename of tailored resume used |
| `cover_letter_file` | Filename of cover letter used |
| `match_score` | Numeric score 0–100 |
| `notes` | Free-text notes (ATS issues, manual steps, follow-up needed) |

---

## Tone and Style Rules (Generated Content)

- Cover letters: concise, human-sounding, ≤250 words unless instructed otherwise
- Resume bullets: action verb → task/technology → outcome/impact
- Avoid: "leveraged", "utilized", "spearheaded", generic superlatives, AI-typical phrasing
- Prefer: specific verbs, concrete details, quantified results where profile data supports them
- Never start multiple bullets with the same verb
