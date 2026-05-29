ApplyChain — First-Time Setup Prompt

Paste this into your AI agent (Claude Cowork, Claude Desktop, Codex, etc.) immediately after cloning the repository.

This prompt initializes the local workspace, replaces template/example content, gathers user-specific information, and prepares the system for operational use.

⸻

APPLYCHAIN INITIALIZATION + USER ONBOARDING

You are initializing a fresh local ApplyChain workspace for a new user.

This repository is intentionally a sanitized template and may contain:

* placeholder/example resumes
* example cover letters
* example logs
* example prompts
* demo application records
* example workflow data

Your job is to convert this template into a clean operational workspace for the current user WITHOUT preserving prior example identity data.

────────────────────────
SECTION 1 — LOCAL-FIRST SAFETY RULES
────────────────────────

This system is:

* local-first
* privacy-oriented
* human-in-the-loop
* operationally isolated from GitHub

Requirements:

* do NOT upload personal files to GitHub
* do NOT expose secrets
* do NOT sync operational artifacts remotely
* do NOT commit resumes/logs/applications automatically
* preserve .gitignore protections
* preserve .env exclusion behavior

Never place:

* resumes
* credentials
* application logs
* exports
* personal profile data
* cover letters
* generated artifacts

into tracked Git history unless explicitly requested by the user.

────────────────────────
SECTION 2 — CLEAN TEMPLATE CONTENT
────────────────────────

Identify and remove or archive placeholder/example identity data from the template repository, including:

* example resumes
* example cover letters
* example recruiter logs
* example applications
* example personal metadata
* example company tracking

Preserve:

* architecture
* code
* helper utilities
* folder structure
* templates
* workflows
* onboarding docs
* prompts
* adapters
* dashboard code

The goal is:
clean operational initialization for a new user.

────────────────────────
SECTION 3 — USER PROFILE INITIALIZATION
────────────────────────

Create a guided onboarding flow to collect the user’s operational profile information.

Prompt the user for:

BASIC PROFILE

* full name
* email
* phone number
* LinkedIn URL
* GitHub URL
* portfolio URL (optional)
* city/state
* work authorization status
* visa sponsorship requirements
* preferred work arrangement
* salary preferences (optional)

EDUCATION

* university
* degree
* graduation date
* GPA (optional)

WORK PREFERENCES

* desired job titles
* preferred industries
* preferred locations
* remote/hybrid/on-site preferences
* seniority targets

EEO / APPLICATION DEFAULTS

* gender
* veteran status
* disability disclosure preference
* ethnicity/race disclosure preference
* LGBTQ disclosure preference

Only store what is operationally necessary for application workflows.

────────────────────────
SECTION 4 — RESUME + DOCUMENT INGESTION
────────────────────────

Prompt the user to:

* place their base resume(s) into the Resumes folder
* optionally add example cover letters
* optionally add portfolio materials
* optionally add recruiter contacts

Then:

* index these files
* summarize them
* extract reusable experience data
* identify measurable achievements
* identify technical skills
* identify ATS keywords
* identify likely weak spots

Create reusable structured profile knowledge files from this information.

Avoid hallucinating accomplishments or metrics.

────────────────────────
SECTION 5 — PROFILE KNOWLEDGE BASE
────────────────────────

Initialize a reusable structured profile knowledge system.

Suggested naming:

* Profile Knowledge Base
* Candidate Profile System
* Structured Candidate Data

Avoid ambiguous/internal names like:

* truth_db

The profile system should store:

* verified work history
* skills
* measurable accomplishments
* preferred phrasing
* ATS keywords
* application defaults
* reusable metrics
* approved resume variants

The system should support:

* deterministic resume tailoring
* ATS optimization
* cover letter generation
* workflow reuse

────────────────────────
SECTION 6 — HUMAN-IN-THE-LOOP DEFAULTS
────────────────────────

Enable human approval checkpoints by default.

The system should pause:

* before final application submission
* before account creation
* before overwriting resumes
* before generating new resume variants
* before modifying profile defaults
* before applying to low-confidence matches

Humans remain final decision-makers.

────────────────────────
SECTION 7 — BROWSER AUTOMATION SETUP
────────────────────────

ApplyChain uses a two-layer browser automation architecture.
Both layers must be set up before automation workflows are usable.

LAYER 1 — Claude for Chrome Extension (primary)

This is Claude's main way to observe and interact with web pages.

Requirements:
* Chrome browser installed
* Claude for Chrome extension installed from the Chrome Web Store
* Extension connected — visible in toolbar, status shows "Connected"
* User signed into Claude within the extension

This layer handles: reading pages, navigating, filling standard form fields,
clicking buttons, uploading files.

LAYER 2 — playwright_engine (fallback for complex interactions)

This is a Python CLI Claude calls via bash for interactions the Chrome
extension cannot reliably handle (React state management, Select2 autocompletes,
rerender detection, multi-signal verification).

Requirements:

1. Python 3.9+ installed (verify: python3 --version)

2. playwright_engine installed — run once from workspace root:
   bash system/playwright_engine/setup.sh

3. Test the installation:
   python3 -m system.playwright_engine.cli diagnose --tab-url "https://example.com"
   Expected: JSON output with url and title fields.

4. A dedicated debug Chrome browser for automation work (recommended):
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --remote-debugging-port=9222 \
     --user-data-dir="$HOME/.chrome-applychain" &

   Add as a shell alias for convenience:
   alias chrome-debug="/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --remote-debugging-port=9222 \
     --user-data-dir=$HOME/.chrome-applychain"

   Why a separate browser: keeps automation work isolated from daily browsing,
   maintains persistent logins (LinkedIn, job portals, Claude extension) across
   sessions, and ensures port 9222 is always available when needed.
   See docs/browser_automation_guide.md for full rationale.

HOW CLAUDE CALLS playwright_engine

Claude uses a bash tool built into Cowork — NOT your system Terminal.
You do not run these commands yourself. Claude calls them internally,
reads the JSON output, and decides what to do next.

For this to work, Claude requires:
* A workspace folder selected in Cowork (gives Claude bash access)
* playwright_engine installed (setup.sh run at least once)
* Chrome running with --remote-debugging-port=9222 when Playwright helpers are needed
* The target tab already open in that Chrome instance

────────────────────────
SECTION 8 — WORKSPACE VALIDATION
────────────────────────

Validate:

* folder structure
* dashboard functionality
* local file permissions
* .env protections
* .gitignore protections
* CSV/application log integrity
* playwright_engine installation (run diagnose command)
* Chrome extension connected
* Streamlit/dashboard launch capability

Confirm:

* operational workspace is functional
* no sensitive files are tracked by Git
* no placeholder identity data remains

────────────────────────
SECTION 9 — OPTIONAL DASHBOARD PERSONALIZATION
────────────────────────

Personalize the dashboard branding for the current user.

Potential additions:

* user name
* role interests
* preferred locations
* local workspace status
* operational statistics

Keep styling:

* minimal
* professional
* modern
* understated

────────────────────────
SECTION 10 — FINAL OUTPUT
────────────────────────

After onboarding:

* summarize collected information
* summarize initialized systems
* identify missing inputs
* identify recommended next steps

Then transition into:

* resume optimization
* ATS analysis
* job sourcing
* workflow orchestration
* application operations

using the established ApplyChain workflow architecture.