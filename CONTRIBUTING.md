# Contributing to ApplyChain

Thank you for contributing! This project welcomes improvements to ATS adapters, prompt templates, browser helpers, and documentation.

## What Makes a Good Contribution

- **New ATS adapter** — Document a platform's form quirks, reliable interaction methods, known failure modes, and fallback strategies. See existing files in `adapters/` for the format.
- **Improved prompts** — Better gap analysis, resume tailoring, or evaluation prompts. Please include example inputs/outputs in your PR description.
- **Browser helper functions** — New DOM-aware utilities for `browser_helpers/interaction_helpers.js`. Must be fallback-only (native Chrome MCP interactions preferred), well-documented, and non-destructive.
- **Documentation** — Clarifications, better examples, troubleshooting entries.

## Ground Rules

1. **No personal data** — Never commit real names, emails, résumé content, credentials, application history, or any PII. All examples must use clearly fictional placeholder data.
2. **No auto-submit** — Do not modify the human checkpoint flow to reduce or eliminate approval gates. The approval gates are non-negotiable.
3. **Truth-constrained** — Prompt changes must not enable or encourage the AI to fabricate, invent, or embellish facts about a user's background.
4. **Test your changes** — For scripts, include at least a basic test or sample run. For prompts, include a sample output in the PR description.

## How to Submit

1. Fork the repository
2. Create a branch: `git checkout -b feature/workday-adapter`
3. Make your changes
4. Open a pull request with a clear description of what changed and why

## Code Style

- JavaScript: standard ES6+, JSDoc comments on all exported functions
- Python: PEP 8, type hints preferred
- Markdown: use ATX headers (`##`), keep lines under 120 characters

## Questions

Open an issue or start a discussion. We're happy to help scope contributions before you write code.
