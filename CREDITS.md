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

## Code Generation and Assistance
- **Claude Code** was used extensively for JavaScript helper utilities, repository scaffolding, and establishing portions of the project structure and development workflow.

- **OpenAI Codex** was used extensively throughout development of the Streamlit dashboard, front-end refinement, UI iteration, and rapid prototyping.

While AI-assisted tooling accelerated development significantly, all generated code was manually reviewed, tested, debugged, and iterated on throughout the project. Architectural decisions, workflow design, integration logic, and final implementation direction remained human-supervised and hands-on from start to finish.

---

## Personal Acknowledgements

**To my Dad** — For gifting me a Raspberry Pi when I was 11, for constantly reminding me that “learning to code is the future, son,” and for supporting me throughout every step of my academic and professional journey.

**To Suresh K** — My friend, mentor, and the person who showed me what it actually means to think like a technologist. The way I approach problems in this space is shaped by your influence more than you probably know.

**To the MSBA cohort and faculty at Miami** — For teaching me how to do some genuinely cool stuff, use cutting-edge tools, and for fostering an environment where curiosity gets rewarded. I'm building on what we built together.

**To my past professional colleagues** - For giving me the opportunity and platform to grow and develop my skills, both hard and soft, in a real-world setting. This project would have been ill-informed without some of the knowledge and best practices I gained from these engagements and I truly appreciate everyone I crossed paths with and got to learn from.

I built this tool a few weeks post-grad, knowing I needed to step up my game to find the right opportunity in this market. I hope it helps others do the same — at scale, with integrity, and without surrendering control to automation.

---

*ApplyChain is open source under the MIT License. See [LICENSE](./LICENSE).*
