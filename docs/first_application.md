# Your First Application — Step by Step

This guide walks through a complete application workflow from zero to submitted, using the fictional "Acme Analytics Corp" role in `examples/sample_application/` as a reference.

Before starting, confirm:
- [ ] `profile_knowledge_base/` is filled in with your real information
- [ ] `logs/applications_log.csv` exists (run `python3 scripts/init_log.py` if not)
- [ ] Claude Desktop is open in Cowork mode with your workspace folder selected
- [ ] Claude for Chrome extension is installed and connected

---

## Step 1 — Save the Job Description

Find a role you want to apply for. Copy the full job description text and save it:

```
job_descriptions/Acme_DataAnalyst_JD_2026-01-15.txt
```

Use the naming convention: `[Company]_[Role]_JD_YYYY-MM-DD.txt`

Tell Claude: **"I saved a new JD for Acme Analytics — Data Analyst. Can you score it against my profile?"**

---

## Step 2 — Gap Analysis

Claude reads your profile and the JD and produces:
- A numbered list of JD requirements with STRONG MATCH / PARTIAL MATCH / GAP / TRANSFERABLE ratings
- An overall fit score (0–100)
- Recommended tailoring decisions
- An honest gaps section

**Review the gap analysis.** If the fit score is below 50, consider whether to proceed. If there are gaps you can actually address (experience you have but didn't document), update `profile_knowledge_base/` now before generating materials.

Tell Claude: **"Looks good — generate a tailored resume."**

---

## Step 3 — Resume Generation

Claude generates a tailored resume using only facts from your `profile_knowledge_base/`. Any metric or detail it can't confirm is marked `[FILL IN]` — never invented.

**Review the draft carefully:**
- Verify every bullet point is accurate
- Fill in any `[FILL IN]` placeholders where you have the real number
- Check that the role emphasis matches the JD

Tell Claude: **"Looks good — export it."**

Claude exports the resume to:
```
resumes/Acme_DataAnalyst_Resume_2026-01-15.docx
```

---

## Step 4 — Cover Letter Generation

Claude generates a concise cover letter (≤250 words) specific to the role and company.

**Review it:**
- Does the opening hook land?
- Is it specific to this role, or generic?
- Does it sound like you?

Tell Claude: **"Export it."** (or give specific edits first)

Claude exports to:
```
cover_letters/Acme_DataAnalyst_CoverLetter_2026-01-15.docx
```

---

## Step 5 — Check for Duplicate Application

Before opening the ATS, ask Claude: **"Have I applied to Acme Analytics before?"**

Claude checks `logs/applications_log.csv` and confirms. If you've already applied, stop here.

---

## Step 6 — Browser Automation

Tell Claude: **"Open the application form at [URL] and begin filling it out."**

Claude will:
1. Navigate to the ATS URL
2. Identify the platform (Workday, Greenhouse, Taleo, etc.) and read the relevant adapter
3. Fill fields from your `profile_knowledge_base/` data
4. Upload your resume and cover letter files
5. Stop at any CAPTCHA, login wall, unexpected page, or low-confidence field and ask you how to proceed
6. Stop at any demographic or sensitive question and show you the proposed answer before filling

**You stay in the loop throughout.** Claude narrates what it's doing and pauses whenever it needs your input.

---

## Step 7 — Pre-Submission Review

Before clicking Submit, Claude displays a summary:

```
Ready to submit — please review:

Resume uploaded:       Acme_DataAnalyst_Resume_2026-01-15.docx
Cover letter uploaded: Acme_DataAnalyst_CoverLetter_2026-01-15.docx
ATS platform:         Greenhouse
Fit score:            78/100
Unresolved [FILL IN]: none
Fields to double-check: [any Claude flagged]

Ready to proceed?
```

**You must say "yes, submit" or equivalent.** Claude will not click Submit without this.

---

## Step 8 — Submission and Logging

Claude clicks Submit, confirms the submission (success page or confirmation email), and logs the application:

```
logs/applications_log.csv ← updated with date, company, role, ATS, status, files, score, notes
```

Claude shows you the log entry and asks you to confirm it looks correct.

---

## What to Do If Something Goes Wrong

- **Login wall:** Claude stops and asks you to log in, then continue
- **CAPTCHA:** Claude stops and asks you to solve it, then continue
- **Unexpected page:** Claude stops, describes what it sees, and asks how to proceed
- **Field it can't fill:** Claude marks it `[UNANSWERED]`, flags it to you, and asks for input
- **React state issue:** Claude retries with DOM helpers; if it still fails, it asks you to fill the field manually

All of these are expected — see `KNOWN_ISSUES.md` for platform-specific gotchas.

---

## Reference Example

The `examples/sample_application/` folder contains fictional but realistic output from this entire workflow: JD, gap analysis, resume draft, cover letter, and log entry. Use it to calibrate what good output looks like before your first real run.
