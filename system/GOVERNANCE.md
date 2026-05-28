# Agent Governance Rule — playwright_engine

## Core Principle

**Claude is the pilot. playwright_engine is the controls.**

Claude (via the Cowork interface and Claude Chrome extension) remains the orchestrator and decision-maker at all times. The playwright_engine is an execution tool — it performs single, narrow, deterministic browser interactions and returns a JSON result. It never decides what to do next.

---

## Separation of Responsibilities

| Layer | Role | Tools |
|-------|------|-------|
| Claude | Orchestrator — reads page state, evaluates results, decides next action | Claude Chrome extension (primary), computer-use |
| playwright_engine CLI | Execution helper — performs one interaction, returns `{success, confidence, escalate}` | Playwright CDP |

Claude calls the engine via bash:
```bash
python -m system.playwright_engine.cli fill-field \
    --tab-url "https://..." \
    --label "First Name" --value "Henry"
```

Claude reads the JSON result and decides what to do next. The engine never chains its own actions.

---

## Chrome Extension vs. CDP — NOT Interchangeable

| Tool | Purpose | When Used |
|------|---------|-----------|
| **Claude Chrome extension** | Claude's primary perception and interaction layer. Claude reads the page, navigates, observes state, fills forms via `find()` + `form_input`. | **Always** — default for all browsing and ATS interaction |
| **playwright_engine (CDP)** | Deterministic fallback for complex interactions that the Chrome extension cannot reliably execute (e.g., Select2 autocompletes, React virtual DOM fields, rerender detection). | **On demand** — only when Claude determines that direct Chrome extension interaction has failed or is likely to fail |

Launching Chrome with `--remote-debugging-port=9222` is only required when you intend to invoke playwright_engine CLI commands. It does **not** replace and does **not** conflict with the Claude Chrome extension, which connects via its own browser API.

You do NOT need to launch Chrome in debug mode for normal Claude-assisted job applications. It is an optional enhancement for complex ATS interactions.

---

## Helper Contract

Every helper command must:
1. Execute exactly **one** atomic interaction
2. Return `{success, confidence, confidence_level, escalate, ...}`
3. Never chain to the next action on its own
4. Never decide whether to proceed with an application
5. Never modify any state outside the single targeted field/button

Claude evaluates the result:
- `success: true` + `confidence_level: HIGH or MEDIUM` → proceed
- `confidence_level: LOW` → log warning, consider retry
- `escalate: true` or `confidence_level: FAILED` → stop, surface to Henry

---

## What Claude Decides

- Which field to fill next (based on visible page state)
- Whether a result looks correct (cross-reference truth_database.json)
- Whether to retry, skip, or escalate
- Whether to submit (requires Henry's explicit approval)
- Whether to use playwright_engine vs. direct Chrome extension interaction

The engine is a scalpel, not an autopilot.

---

## Security Notes

- The engine connects only to tabs already open in Henry's Chrome session (matched by URL)
- It never opens new tabs, navigates autonomously, or submits forms
- All actions are logged with before/after screenshots in `logs/playwright_traces/`
- Sensitive fields (passwords, financial data) are never passed to the engine
