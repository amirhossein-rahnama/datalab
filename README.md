# datalab

A Claude Code plugin to build, run, and complete **any** data science project —
academic or industrial. Scaffolds projects, runs full experiments, verifies model
quality (over/underfitting, leakage, fairness), and produces PDF/PPTX/dashboard deliverables.

## Install

```
/plugin marketplace add <repo-or-path>
/plugin install datalab
/datalab:doctor
```

Then install the Python tooling used by the scripts:

```
pip install -r scripts/requirements.txt
```

## Commands

| Command | Purpose |
|---------|---------|
| `/datalab:new` | Scaffold a new project (interview + adaptive tiers) |
| `/datalab:work` | Continue/complete an existing project |
| `/datalab:run` | Run the full experiment end-to-end (results, plots, conclusions) |
| `/datalab:docs` | Generate documentation, PDF report, PPTX deck, model/data cards |
| `/datalab:doctor` | Health check: Python, dependencies, plugin wiring |

## Status

Under active development. See `docs/specs/` for the design and `docs/plans/` for build plans.
