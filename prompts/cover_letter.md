# Prompt: Cover Letter Generation

Use after resume is approved. Generates a concise, human-sounding cover letter.

---

## Prompt Template

```
Generate a cover letter for the following application.

PROFILE KNOWLEDGE BASE:
[reference or paste relevant sections]

JOB DESCRIPTION:
[paste JD]

COMPANY RESEARCH (if available):
[paste any notes about the company — what they do, culture signals, recent news]

TAILORED RESUME (approved version):
[paste the approved resume text]

Rules:
- Length: ≤250 words (unless I explicitly ask for longer)
- Tone: professional but human — not stiff, not generic
- Structure: opening hook → why this role/company → what I bring → close
- Must reference: the specific role title, at least one company-specific detail
- Must NOT: use "I am writing to express my interest", "I am passionate about", "leveraged", "spearheaded", or other AI-typical phrases
- Must NOT: claim any skill or experience not in the profile
- Must NOT: repeat the resume verbatim — the cover letter adds context, not duplication

Output the cover letter as plain text, ready to be pasted into a form or exported.

After the letter, note:
- Any company-specific claims made (so I can verify accuracy)
- Any [FILL IN] placeholders in the letter
```

---

## Example Output Format

```
[Your Name]
[Date]

Hiring Manager,
[Opening: specific hook — why this company, why now]

[Body: 2–3 focused sentences connecting your strongest relevant experience to the role's core need. Be specific, not generic.]

[Close: what you're looking forward to discussing; brief, confident]

[Your Name]

---
Notes:
- Claimed: [company] recently expanded into [market] — verify accuracy before submitting
- No [FILL IN] placeholders
```
