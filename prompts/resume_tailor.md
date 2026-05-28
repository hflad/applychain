# Prompt: Resume Tailoring

Use this prompt after gap analysis is complete and approved. Generates a tailored resume draft using only approved profile content.

---

## Prompt Template

```
You are generating a tailored resume. You must use ONLY content from the Profile Knowledge Base below.

Rules:
- You may: rephrase bullets for clarity, reorder experience, select the most relevant subset, adjust emphasis
- You may NOT: invent experience, fabricate metrics, add skills not in the profile, create new accomplishments
- If a metric is missing, use [FILL IN] as a placeholder — never estimate
- If a required skill is not in the profile, do NOT add it to the resume — note the gap instead
- Maximum resume length: 1 page for < 5 years experience; 2 pages for 5+ years

PROFILE KNOWLEDGE BASE:
[reference or paste profile_knowledge_base/ files]

GAP ANALYSIS RESULTS:
[paste gap analysis output]

JOB DESCRIPTION:
[paste JD]

OUTPUT FORMAT:
Produce the resume as structured text sections:
1. Header (name, contact info, LinkedIn)
2. Summary (2–3 sentences, optional — only include if it adds value)
3. Work Experience (most recent first; 2–4 bullets per role)
4. Education
5. Skills (relevant subset only — match to JD keywords where truthful)
6. Projects (if relevant)
7. Certifications (if relevant)

After the resume, append:
- Tailoring decisions: list what you emphasized and why
- [FILL IN] placeholders: list each placeholder and what information is needed
- Gaps not addressed: list any JD requirements not covered in the resume
```

---

## Evaluator Prompts (run after draft)

After generating the resume draft, run each of these evaluations:

### ATS Evaluator
```
Evaluate this resume for ATS (Applicant Tracking System) parsing:
- Keyword match rate against the JD (list matched and missing keywords)
- Section headers: are they standard and parseable?
- Formatting risks: any tables, columns, or special characters that ATS may misparse?
- Score: 0–100
- Top 3 improvements
```

### Recruiter Skim Evaluator (6-second test)
```
Evaluate this resume for recruiter skim readability:
- In 6 seconds, what stands out? What's the candidate's strongest selling point?
- Is the most relevant experience visible above the fold?
- Are impact/outcome bullets visible, or buried in responsibilities?
- Score: 0–100
- Top 3 improvements
```

### Hiring Manager Evaluator
```
Evaluate this resume from a hiring manager's perspective for the role described in the JD:
- Does the narrative arc make sense for this role?
- Is seniority/scope appropriate for the role requirements?
- Are there unexplained gaps or concerns a manager would notice?
- Score: 0–100
- Top 3 improvements
```

### Technical Evaluator
```
Evaluate this resume from a technical lead's perspective:
- Is the technical depth sufficient for the role?
- Are technologies used with appropriate specificity, or vaguely mentioned?
- Are project descriptions credible and specific enough?
- Score: 0–100
- Top 3 improvements
```
