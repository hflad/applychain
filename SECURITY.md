# SECURITY.md

**Project:** ApplyChain  
**Last Updated:** 2026-05-28

---

## Security Model

ApplyChain is designed to be local-first. Your personal data never leaves your machine except through LLM API calls (which use Anthropic's privacy-respecting infrastructure).

---

## Credential Handling

- All credentials (API keys, login passwords) must be stored in `.env` only
- `.env` is gitignored and must never be committed
- Use `.env.example` as a non-secret template
- Credentials must NEVER appear in:
  - Prompt text sent to Claude
  - Generated documents (resumes, cover letters)
  - Log files
  - Markdown notes or documentation
  - Screenshots
  - Chat transcripts

If you discover a credential has been accidentally committed, rotate it immediately and scrub the git history.

---

## Personal Data

- `profile_knowledge_base/` contains your resume facts — keep it local, don't commit to a public repository
- `logs/applications_log.csv` contains application history — gitignored by default
- `resumes/`, `cover_letters/`, `applications/` — gitignored by default
- Do NOT sync this project folder to public cloud storage (iCloud, Google Drive, Dropbox) without reviewing what's in it first

---

## Sensitive Form Questions

- Demographic and compliance question defaults are stored in `profile_knowledge_base/application_defaults.md`
- The AI must use only stored truthful defaults — never infer or alter protected attributes
- "Decline to answer" is preferred where the platform offers it and you haven't specified a preference
- The AI must pause and ask you before answering custom or freeform sensitive questions

---

## Browser Automation

- The AI must never click a Submit or Send button without your explicit approval in the chat interface
- The AI must never enter credentials (passwords, SSNs, bank details) into forms — these require direct human input
- If a CAPTCHA, unexpected login wall, or unfamiliar form appears, the AI must stop and notify you
- Cookie consent banners: the AI will choose the most privacy-preserving option (decline non-essential cookies) unless you instruct otherwise

---

## What the AI Is Not Allowed To Do

- Submit any application without your explicit "yes, submit" confirmation
- Fabricate any resume content, even if the job description asks for experience you don't have
- Modify sharing permissions on any document
- Create accounts on your behalf
- Enter passwords on your behalf
- Access, read, or transmit `.env` file contents

---

## Reporting Security Issues

If you discover a security issue in this template (e.g., a prompt that could leak credentials, or a script that writes to an unintended location), please open a GitHub issue marked **[SECURITY]**.
