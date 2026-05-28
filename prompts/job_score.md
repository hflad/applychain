# Prompt: Job Fit Scoring

Use when a new job description is ingested. Scores the role against your profile before investing time in a full application.

---

## Prompt Template

```
Score this job opportunity against my profile.

PROFILE SUMMARY (from profile_knowledge_base/preferences.md + skills.md + experience.md):
[paste or reference relevant profile sections]

JOB DESCRIPTION:
[paste JD]

Evaluate and score the following dimensions (each 0–10):

1. Skills match — overlap between required skills and my profile
2. Seniority fit — does my experience level match the role's expectations?
3. Location fit — does the role's location match my desired_locations.txt?
4. Role title fit — is this in my target roles list?
5. Company type fit — does the company match my company type preference?
6. Salary fit — does the apparent range (if visible) meet my floor?
7. Industry fit — is this in my preferred industries list?

Overall score: weighted average (skills 30%, seniority 20%, location 15%, role 15%, rest 20%)

Output:
- Dimension scores with brief rationale for each
- Overall score (0–100)
- Recommendation: APPLY / REVIEW FURTHER / SKIP
- Deal-breakers: list any from preferences.md that this role fails
- Top 3 selling points (why this role is worth pursuing)
- Top 2 concerns (honest red flags)
```

---

## Scoring Guide

| Score | Meaning |
|-------|---------|
| 80–100 | Strong fit — prioritize |
| 60–79 | Good fit — worth applying |
| 40–59 | Partial fit — consider if pipeline is thin |
| < 40 | Weak fit — likely not worth the time |
