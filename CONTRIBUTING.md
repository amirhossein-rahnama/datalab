# Contributing to datalab

Thanks for your interest in improving datalab! This is a Claude Code plugin — most of "the
code" is Markdown (commands, skills) plus a set of small, independently-testable Python
scripts. Contributions of any size are welcome: typo fixes, new checks, template
improvements, bug fixes, or whole new skills.

## Dev setup

```bash
git clone <this-repo-url>
cd data-science-claude-plugin
python -m pip install -r scripts/requirements.txt
python -m pip install pytest
```

Python 3.11 or 3.12 is recommended (matches CI); `scripts/doctor.py` will flag anything
older than 3.10.

To try the plugin itself inside Claude Code, add this checkout as a local marketplace:

```
/plugin marketplace add <path-to-your-checkout>
/plugin install datalab
/datalab:doctor
```

## Running the tests

```bash
python -m pytest tests/ -q
```

Every script in `scripts/` has a matching `tests/test_<script>.py`. Tests import the script
module directly (no packaging or install step needed) — see any existing test file for the
pattern.

## Repo layout

| Path | What lives there |
|------|-------------------|
| `commands/` | Slash-command entry points (`/datalab:*`) — thin Markdown files that tell Claude what to do and which skill to load. |
| `skills/` | The skills that do the real work (orchestrator, scaffold, eda, modeling, experiment, verify, mlops, document) — each a `SKILL.md` plus optional `references/`. |
| `scripts/` | Small, independently-testable Python helpers the skills/commands call (doctor, data profiling, stats, plots, report/deck generation, provenance, privacy scan, etc.). |
| `templates/` | The adaptive project scaffold (base / ml / mlops / dashboard / governance / genai tiers), driven by `templates/stacks.yaml`. |
| `tests/` | Pytest unit tests — one file per `scripts/` module, plus a manifest test that checks `plugin.json` / `marketplace.json` stay valid. |
| `docs/` | `docs/specs/` (design specs) and `docs/plans/` (build plans). |

(`examples/` holds a small worked project used as a test fixture; `.claude-plugin/` holds
the plugin manifest.)

## Coding conventions

- **Focused files.** Each script does one job with small, single-purpose functions and a
  thin `main(argv)` / `if __name__ == "__main__"` entry point (see `scripts/doctor.py` for
  the shape). Prefer adding a new small script over growing an existing one into a
  do-everything module.
- **Tests for scripts.** Any new or changed script in `scripts/` needs a matching test in
  `tests/`. Cover the normal case, at least one edge case, and — for anything with a
  pass/fail notion — both outcomes.
- **Lazy-import heavy deps.** Heavy or optional packages (`shap`, `evidently`, `optuna`, and
  similar) must be imported *inside* the function that needs them, not at module top-level,
  so importing the module never fails when that package isn't installed. See
  `shap_summary()` in `scripts/explain.py` for the pattern: catch `ImportError` and raise a
  clear error with the exact `pip install` command.
- Keep everything pure-Python and pip-installable — no LaTeX/pandoc/system-level
  dependencies. That's what lets `/datalab:doctor` fully diagnose the environment and lets
  the plugin run anywhere.

## Making a change

1. For anything non-trivial (new skill, new command, behavior change), open an issue first
   to discuss the approach. For small fixes (typos, obvious bugs) a PR alone is fine.
2. Keep PRs focused: one logical change per PR. Unrelated drive-by fixes are easier to review
   — and to land — as their own PR.
3. Add or update tests and run `python -m pytest tests/ -q`. Update docs (README, a skill's
   `SKILL.md`, or `docs/`) if behavior changed.
4. Update `CHANGELOG.md` for user-visible changes.
5. Open the PR — the template will walk you through the checklist.

## Reporting bugs / requesting features

Please use the issue templates ("Bug report" / "Feature request"). For bugs, include your
OS, Python version, and the output of `/datalab:doctor` — it saves a round trip.

## Code of conduct

Be respectful and constructive. Assume good faith, disagree on substance, and keep feedback
focused on the work.
