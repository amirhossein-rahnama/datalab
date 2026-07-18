---
name: document
description: Use to generate deliverables — documentation, a PDF report (academic or industrial template), a PPTX deck, and model/data cards plus a compliance checklist.
---

# Document

> **Bundled scripts live in the plugin, not the user's project.** Invoke datalab's
> Python scripts with the plugin path, e.g. `python "$CLAUDE_PLUGIN_ROOT/scripts/<name>.py"`.
> If `$CLAUDE_PLUGIN_ROOT` is unset, find the datalab plugin folder (the one containing
> `.claude-plugin/plugin.json`). The working directory is the user's own project. If a bundled script errors because a package
> is missing, run `python "$CLAUDE_PLUGIN_ROOT/scripts/setup.py"` once to install core deps.

Turns everything the project has produced into deliverables: a PDF report, a PPTX deck, and a
governance bundle (model card + data card + compliance checklist). Runs after `experiment`
(needs real results) — via `/datalab:docs`. The only skill that runs the deliverable-
generation scripts (`generate_report.py`, `generate_deck.py`).

## Step 1 — Gather sources

Don't invent content — pull from what other phases already produced:
- `README.md` (project description)
- Notebook output via `python "$CLAUDE_PLUGIN_ROOT/scripts/nb_to_md.py" --input notebooks/01_eda.ipynb` (repeat per
  notebook that has relevant output)
- `reports/results.md` (metrics, conclusions — from `experiment`)
- `reports/figures/*` (from `experiment`/`eda`)
- `reports/data_dictionary.md` (from `eda`)
- diagnostics/explain output (from `experiment`'s Step 3, or re-check `verify`'s last Gate B
  result)
- the provenance manifest (from `scripts/provenance.py`)

If any of these is missing (e.g., `document` is invoked before `experiment` ran), say so and
either delegate back to the missing phase or produce a clearly-marked partial deliverable —
never fabricate a metric or figure that doesn't exist yet.

## Step 2 — Assemble Markdown per profile

Read `state.json.profile` and follow the matching template:
- **academic** → `references/report-academic.md` (abstract → intro → data → method →
  experiments → results/tables/figures → discussion → references/BibTeX)
- **industrial** → `references/report-industrial.md` (exec summary → problem → data →
  approach → results → business impact → next steps)

Write the assembled Markdown to `reports/report.md` before rendering — it should be a
reviewable artifact on its own, not just an intermediate buffer.

## Step 3 — Render PDF and deck

```
python "$CLAUDE_PLUGIN_ROOT/scripts/generate_report.py" --input reports/report.md --output reports/report.pdf --title "<project>"
python "$CLAUDE_PLUGIN_ROOT/scripts/generate_deck.py" --input reports/deck_outline.md --output reports/deck.pptx --title "<project>"
```
The deck outline is a condensed version of the report (one `# slide title` + `- bullet` per
section per `generate_deck.py`'s outline format) — 6–12 slides, not a slide-per-paragraph
dump of the full report. Write `reports/deck_outline.md` before rendering, same reviewability
reasoning as Step 2.

## Step 4 — Governance bundle

Fill `templates/governance/{MODEL_CARD.md,DATA_CARD.md,COMPLIANCE_CHECKLIST.md}` using the
gathered metrics, diagnostics, fairness/explainability output, and provenance manifest.
Field-by-field guidance and EU AI Act framing: `references/cards.md`. Optionally render the
model/data card through `generate_report.py` as well for a PDF copy.

## Step 5 — Optional dashboard

If the interview's deliverables included "dashboard", wire `templates/dashboard/app.py` to
the trained pipeline (this is the same stub `scaffold` rendered — `document` fills in real
data/model paths rather than re-creating it).

## Step 6 — Verify artifacts

Confirm each requested deliverable file exists and is non-empty (`reports/report.pdf`,
`reports/deck.pptx`, the governance Markdown files). If a script failed because of a missing
dependency, print the exact fix (or point at `/datalab:doctor`) rather than silently skipping
the deliverable. Set `phases.docs = "done"` only once the requested deliverables are all
present and non-empty.

## Boundaries

- Don't run new experiments or regenerate figures here — if a number is missing, that's a gap
  to hand back to `experiment`/`eda`, not something to approximate.
- Don't hand-write PDF/PPTX bytes — always go through `generate_report.py`/`generate_deck.py`
  so output stays consistent and testable.
