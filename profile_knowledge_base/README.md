# Profile Knowledge Base

This folder contains templates for your personal career profile. The AI uses these files — and only these files — as the source of truth for all generated resumes, cover letters, and form answers.

---

## ⚠️ Privacy Warning

**Once you fill in these templates with your real information, this folder contains sensitive personal data** — your work history, education, contact details, salary expectations, and demographic defaults.

**Before filling anything in**, uncomment the following line in `.gitignore`:

```
# profile_knowledge_base/
```

Change it to:

```
profile_knowledge_base/
```

This ensures your personal data is never accidentally committed or pushed to any remote, even if you fork this repo or use it with version control.

---

## Files

| File | Contents |
|------|----------|
| `experience.md` | Work history, roles, responsibilities, achievements |
| `education.md` | Degrees, institutions, GPA |
| `skills.md` | Technical skills, tools, languages |
| `projects.md` | Personal and side projects |
| `certifications.md` | Completed or in-progress certifications |
| `metrics.md` | Approved quantified achievements |
| `preferences.md` | Role types, company types, salary floor, work style |
| `desired_locations.txt` | Preferred cities/regions, ranked |
| `desired_roles.txt` | Target job titles, ranked |
| `application_defaults.md` | Demographic/compliance question defaults |

---

## Rules

- Only put **true, verifiable** information here
- The AI will never add to what you provide — it selects, reorders, and rephrases only
- Use `[FILL IN]` for any metric or detail you plan to confirm later
- Delete the example placeholder text and replace it with your own content
