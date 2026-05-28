# SECURITY.md

**Project:** ApplyChain  
**Last Updated:** 2026-05-28

---

## Security Model

ApplyChain is designed to be local-first. Your personal data never leaves your machine except through LLM API calls (which use your chosen provider's infrastructure). Credentials are read from local files only — they are never typed into chat, never sent in prompts, and never appear in any LLM context window.

---

## The One Rule That Overrides Everything Else

**Never type a password, API key, or secret into a chat message or prompt.**

The distinction that makes ApplyChain safe is this: the agent reads credentials from `.env` on disk — your local filesystem — not from you in conversation. Those are very different things. A file on your machine that the agent's execution environment reads is not the same as a secret traveling through an LLM API call. Keep them separate and you're fine.

---

## Credential Storage

All credentials live in `.env` only:

```bash
# ATS / job platform credentials
ATS_EMAIL=you@example.com
ATS_PASSWORD=your-password-here

# SSO providers (if not using saved browser session)
LINKEDIN_EMAIL=you@example.com
GOOGLE_EMAIL=you@example.com

# API keys
ANTHROPIC_API_KEY=sk-...
```

Rules:
- `.env` is gitignored and must never be committed — not even accidentally
- Use `.env.example` as a non-secret template (it ships with the repo)
- Credentials must never appear in prompts, generated documents, logs, markdown files, screenshots, or chat transcripts
- If a credential is accidentally committed, rotate it immediately and rewrite history (`git filter-branch` or BFG Repo Cleaner)

---

## ATS Account Creation & Login

Many ATS platforms (Workday, iCIMS, Taleo, and others) require you to create a per-employer account before applying. ApplyChain is designed to handle this.

**The agent can:**
- Create a new account using `ATS_EMAIL` and `ATS_PASSWORD` from `.env`
- Log into an existing account using the same credentials
- Handle SSO login flows (Google, LinkedIn) by clicking the appropriate button — especially reliable if you're already signed into that provider in Chrome for the day and 2FA isn't required

**The agent cannot:**
- Complete a 2FA/MFA challenge on your behalf — it will stop and ask you to handle it
- Recover a forgotten password
- Know which password you used for a specific employer if you used different ones

### Password Strategy

You have a few options for managing per-site passwords:

**Option A — One shared password for all ATS accounts (simplest)**  
Set `ATS_PASSWORD` in `.env` once. The agent uses it everywhere. Reasonable for low-stakes job portal accounts that don't hold financial data.

**Option B — Chrome's auto-generated strong passwords (recommended)**  
When the agent reaches the account creation form, let Chrome suggest a strong password. Chrome saves it to your password manager automatically and the agent can proceed. You don't need to know or store the password yourself.

**Option C — Custom password logic (advanced, stays local)**  
Write your own password generation or rotation logic in a local script. Keep it on your machine only. Never put it in the repo or in chat.

Whatever strategy you choose, the decision and the credentials stay on your machine. The agent just uses what `.env` provides.

---

## SSO & Chrome Password Manager

**SSO (Google / LinkedIn):**  
ApplyChain's browser automation can handle SSO flows by clicking the "Sign in with Google" or "Sign in with LinkedIn" buttons. This works reliably when you're already signed into that provider in Chrome. If a 2FA prompt appears, the agent will stop and ask you to complete it.

**Chrome Password Manager:**  
If Chrome has saved credentials for a site, the browser's autofill may populate login fields automatically before the agent needs to act. This is a convenience layer on top of `.env` — both can coexist. Chrome's password manager is a local credential store and is a reasonable place to keep ATS account passwords alongside `.env`.

Note: The agent's ability to trigger Chrome autofill programmatically is not fully tested across all platforms. If autofill doesn't fire, the agent falls back to `.env` credentials.

---

## Sensitive Form Questions

- Demographic and compliance defaults are stored in `profile_knowledge_base/application_defaults.md`
- The AI uses only stored truthful values — never infers or alters protected attributes
- "Decline to answer" is the default for any EEO field not explicitly specified
- The AI stops and asks before answering any custom or freeform sensitive question

---

## Browser Automation Limits

- The agent will never click Submit on any application without your explicit approval in chat
- The agent will never enter SSN, bank details, or financial information — it will stop and ask you
- CAPTCHAs: the agent stops immediately and notifies you
- Unexpected pages or login walls: the agent stops and describes what it sees

---

## What the AI Must Never Do

- Submit any application without explicit "yes, submit" from you in chat
- Fabricate resume content
- Type credentials into chat or include them in any prompt
- Commit `.env` or any credential file to version control
- Transmit credentials to any external service beyond what's required to authenticate with the target site
- Modify document sharing permissions
- Access financial accounts or enter financial data

---

## Reporting Security Issues

Open a GitHub issue marked **[SECURITY]** if you find a prompt, script, or workflow that could leak credentials or personal data.
