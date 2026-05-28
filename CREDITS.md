# Credits & Acknowledgements

---

## Inspirations & Prior Art

### MaverickAI — Claude Resume Guide
**Source:** [mavgpt.ai/pdfs/Claude_Resume_Guide.pdf](https://mavgpt.ai/pdfs/Claude_Resume_Guide.pdf)  
**By:** MaverickAI / [@MavGPT](https://mavgpt.ai)

Two specific ideas in ApplyChain trace directly to this guide:

- **The multi-perspective ATS evaluator structure** — the framing of running a resume through an ATS filter and a hiring manager simultaneously, producing a match score and identifying missing keywords, originates from MavGPT's Prompt 3. ApplyChain expanded this into a four-perspective evaluation loop (ATS, recruiter skim, hiring manager, technical lead) and wired it into an iterative improvement workflow.

- **The `[FILL IN]` metric placeholder convention** — the practice of marking unconfirmed metrics with an explicit placeholder rather than inventing numbers comes from MavGPT's experience rewrite prompt. ApplyChain adopted and formalized this as a hard constraint: the AI may never substitute an estimate for a `[FILL IN]`.

Everything else in ApplyChain — the Profile Knowledge Base architecture, the truth-constrained generation model, the human checkpoint system, the browser automation layer, the ATS adapter framework, and the local-first operational design — was built independently on top of these foundations.

If you haven't read the MaverickAI guide, it's worth your time. It covers the core resume prompting workflow clearly and concisely.

---

## Personal Acknowledgements

**To my Dad** — for getting me a Raspberry Pi when I was 11. That one gift set a lot in motion. Thank you.

**To Suresh** — friend, mentor, and the person who showed me what it actually means to think like a technologist. The way I approach problems is shaped by your influence more than you probably know.

**To the MSBA faculty and my classmates at Miami** — for teaching me how to do some genuinely cool stuff, and for making the kind of environment where curiosity gets rewarded. I'm building on what we built together.

---

*ApplyChain is open source under the MIT License. See [LICENSE](./LICENSE).*
