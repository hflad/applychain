# Prompt: Gap Analysis

Use this prompt after saving a job description. Paste it into Claude along with the JD text and your profile_knowledge_base contents.

---

## Prompt Template

```
You are performing a gap analysis for a job application. 

PROFILE KNOWLEDGE BASE:
[paste the contents of profile_knowledge_base/ here, or reference the files]

JOB DESCRIPTION:
[paste the full JD text here]

Instructions:
1. Parse the JD and extract:
   - Required skills and technologies
   - Preferred/bonus skills
   - Seniority level and years of experience required
   - Key responsibilities
   - Industry domain knowledge required

2. For each requirement, assess:
   - STRONG MATCH — directly covered by profile with evidence
   - PARTIAL MATCH — related experience but not exact; note the gap
   - GAP — not present in profile at all; flag clearly
   - TRANSFERABLE — different domain but relevant skill

3. Produce:
   a. A numbered list of requirements with their match status and evidence
   b. An overall fit score (0–100) with brief rationale
   c. A "recommended tailoring" section listing which profile bullets to emphasize
   d. A "honest gaps" section listing requirements not met — do NOT paper over these

4. Rules:
   - Never suggest claiming experience you don't have
   - Never mark a gap as "transferable" just to inflate the score
   - [FILL IN] placeholders are acceptable for metrics not yet confirmed
   - If fit score is below 50, recommend reconsidering the application
```

---

## Example Output Format

```
## Gap Analysis: [Company] — [Role]
**Fit Score: 72/100**
Rationale: Strong SQL and Python alignment; data visualization is partial match (Power BI not in profile, Tableau is); no financial modeling experience.

### Requirements Analysis
1. SQL (Advanced) — ✅ STRONG MATCH — 3+ years experience across [roles]
2. Python for data analysis — ✅ STRONG MATCH — used pandas, numpy in [role]
3. Tableau or Power BI — ⚠️ PARTIAL MATCH — Tableau in profile; Power BI not
4. Financial modeling — ❌ GAP — not present in profile
5. Cross-functional communication — ✅ STRONG MATCH — [evidence]

### Recommended Tailoring
- Lead with SQL and Python bullets
- Mention Tableau; note Power BI as adjacent skill
- Omit financial modeling from resume; do not claim it

### Honest Gaps
- Financial modeling (required): not in profile — flag to user
- Power BI specifically (preferred): Tableau is close; acknowledge in cover letter
```
