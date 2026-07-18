---
description: "Show what datalab can do and the typical workflow"
---

# datalab help

Give the user a clear, friendly overview of what datalab can do. Don't just paste this file
verbatim — use it as your source of truth and present it conversationally: short intro, a
compact list, a one-line workflow, and the two closing pointers. Keep the whole thing
concise and scannable, not a wall of text.

## Cover these points

1. **What it is** — one line: datalab is a Claude Code plugin that builds, runs, and
   completes data science projects, academic or industrial, end-to-end.

2. **The 7 commands**, one line each:
   - `/datalab:setup` — Install and verify the Python tooling datalab's scripts need.
   - `/datalab:new` — Scaffold a new data science project (interview + adaptive tiers).
   - `/datalab:work` — Continue or complete an existing project (resumes from saved state).
   - `/datalab:run` — Run the full experiment end-to-end (results, plots, conclusions).
   - `/datalab:docs` — Generate documentation, PDF report, PPTX deck, and model/data cards.
   - `/datalab:doctor` — Health check: Python version, dependencies, plugin wiring.
   - `/datalab:help` — Show this overview.

3. **The typical workflow**:
   ```
   /datalab:setup  ->  /datalab:new (or /datalab:work)  ->  /datalab:run  ->  /datalab:docs
   ```
   Run `/datalab:doctor` any time something feels off, and `/datalab:help` any time you want
   a reminder of what's available.

4. **Skills auto-activate too** — commands aren't the only way in. Natural-language requests
   ("profile this dataset", "check for data leakage", "add a FastAPI serving layer") trigger
   the matching skill directly (orchestrator, scaffold, eda, modeling, experiment, verify,
   mlops, document) without needing an explicit `/datalab:*` command.

5. **Where to go deeper** — the root `README.md` for install steps and the full command
   reference, and `docs/` (`docs/specs/` for the design spec, `docs/plans/` for build plans)
   for the complete picture.

## Keep it tight

A short paragraph plus a compact list/table beats a wall of text. If the user named a
specific command or topic, focus the overview on that instead of repeating everything:

$ARGUMENTS
