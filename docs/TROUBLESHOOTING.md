# Troubleshooting

Common problems, why they happen, and the exact fix. If you don't see your issue here, run `/datalab:doctor` first — it catches most of the "something's missing" category automatically — then check [`docs/FAQ.md`](FAQ.md) or open an issue at [github.com/amirhossein-rahnama/datalab](https://github.com/amirhossein-rahnama/datalab).

## `/datalab:*` command not found

**Symptom:** Typing `/datalab:new` (or any other command) does nothing, or Claude Code says it doesn't recognize it.

**Cause:** The plugin isn't installed, isn't enabled, or Claude Code hasn't picked up the install yet.

**Fix:**
1. Confirm the marketplace was added and the plugin installed:
   ```
   /plugin marketplace add https://github.com/amirhossein-rahnama/datalab
   /plugin install datalab
   ```
2. Make sure you're typing the full name with the colon — `/datalab:new`, not `/datalab new` or `/new`.
3. If you just installed it, restart Claude Code (or start a fresh session) so it reloads the plugin list.
4. Run `/datalab:doctor` — if `plugin.json` reports missing or invalid, the install itself is corrupted; reinstall the plugin.

## `/datalab:doctor` reports missing packages

**Symptom:** `/datalab:doctor` prints one or more `[FAIL]` lines under package checks.

**Cause:** `/datalab:setup` hasn't been run yet, or ran in a different Python environment than the one Claude Code is using.

**Fix:**
```
/datalab:setup
```
This installs exactly the packages `datalab`'s tooling needs — `/datalab:doctor` also prints the literal `pip install ...` line it would take to fix things by hand, if you'd rather run that yourself. Re-run `/datalab:doctor` afterward to confirm everything shows `[OK]`.

## A feature says it needs a package that isn't installed

**Symptom:** A skill tells you it needs SHAP, Optuna, pandera, Evidently, or a GenAI/RAG-related library, and stops rather than proceeding.

**Cause:** This is expected, not a bug. `/datalab:setup` (no flags) only installs the small **core** set — heavier, feature-specific libraries install on demand, only when a feature actually needs them, so you're never made to install things you won't use.

**Fix:**
```
/datalab:setup --full     # SHAP, Optuna, pandera, Evidently, pip-audit
/datalab:setup --genai    # embeddings / vector store / ragas, for genai-rag projects
```
Both are safe to run any time — they only install what's missing.

## An optional library fails to install on a very new Python version

**Symptom:** `/datalab:setup --full` (or `--genai`) fails on one specific package, especially right after a new Python release (e.g. Python 3.14) — everything else installs fine.

**Cause:** Some scientific-Python packages publish pre-built wheels for a new CPython version a little while after that version ships. If you're on a brand-new interpreter, one optional library's wheel might not exist yet (and building from source can fail without a compiler toolchain).

**Fix:**
- The **core** set (needed for scaffolding, doctor, EDA, baseline modeling, and report/deck/notebook generation) has no such issue and works everywhere Python 3.10+ runs — this only affects optional, feature-specific libraries.
- If a feature degrades because its optional library couldn't install, `datalab` tells you clearly which feature and which package — it doesn't fail silently or produce a broken result.
- Options: wait for the upstream package to publish a wheel for your Python version (usually weeks, not months, after release), or create a virtual environment on a slightly older, well-supported Python (3.11 or 3.12) for that one project:
  ```
  python3.11 -m venv .venv
  # Windows (PowerShell):
  .venv\Scripts\Activate.ps1
  # macOS/Linux:
  source .venv/bin/activate
  ```

## Windows-specific issues

`datalab`'s own tooling is pure Python and behaves identically on Windows, macOS, and Linux — the differences below are shell/OS conventions, not the plugin.

| Issue | Fix |
|---|---|
| A path with spaces breaks a command (common with folders like `My Projects` or a `OneDrive` path) | Quote it: `python scripts/doctor.py "C:\Users\you\My Projects\datalab"` |
| `.venv\Scripts\Activate.ps1` fails with a script-execution error in PowerShell | Run PowerShell as your user and allow local scripts once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or activate via `cmd.exe` instead: `.venv\Scripts\activate.bat` |
| A copy-pasted Unix example with a trailing `\` line continuation fails in PowerShell | PowerShell uses a backtick `` ` `` for line continuation, not `\` — or just put the whole command on one line |
| Very long scaffolded paths (deep `src/<pkg>/models/` trees under a long project name) hit Windows' historical 260-character path limit | Enable long paths once (Windows 10/11): `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force`, then restart your shell |

## A notebook fails to execute — kernel error

**Symptom:** `verify`'s notebook-execution check (or `/datalab:new`'s smoke check) fails with something like "no kernel named python3" or a `nbclient` timeout.

**Cause:** `nbclient` (the tool that runs notebooks non-interactively) needs a registered Jupyter kernel matching what the notebook asks for — that's a separate install from `nbclient`/`nbformat` themselves.

**Fix:**
```
pip install ipykernel
python -m ipykernel install --user --name python3
```
Make sure this is run in the **same** Python environment your project's dependencies are installed in (the one from `python tasks.py setup` inside your project — see [Two kinds of dependencies](ARCHITECTURE.md#two-kinds-of-dependencies)), not a different one.

## Scaffold didn't create (or update) a file you expected

**Symptom:** After `/datalab:new` or adding a tier, a file you expected to see rendered is missing or unchanged.

**Cause:** This is almost always **non-clobbering working as intended** — `scaffold` never overwrites a file that already exists on disk, even an empty placeholder. The scaffold report distinguishes **added** from **skipped**; a skipped file means something was already there.

**Fix:** If you genuinely want that file regenerated from the template, delete or rename your version first, then re-run the scaffold step (`/datalab:new` again, or `/datalab:work` if you're adding a tier to an existing project). Otherwise, no action needed — your customization was preserved on purpose.

## `verify` keeps failing / seems stuck retrying

**Symptom:** The same phase keeps getting sent back for fixes.

**Cause:** By design, `verify` gives the owning skill a bounded number of attempts (about 3) to fix a reported issue — it does not loop forever, and it does not silently downgrade a red result to "done, mostly."

**Fix:** After the bounded retries, `verify` escalates to you with the **exact** finding — file, line, and message for a code issue; the specific metric/check for a model issue. Read that finding; it's written to be actionable without you having to re-diagnose it yourself. Common ones:
- *"Model does not beat baseline"* → the feature set or model choice needs real work, not a hyperparameter tweak.
- *"Leakage suspected — preprocessing fit outside CV folds"* → check that scaling/encoding/imputation live inside a single `sklearn.Pipeline`, not fit once on the full dataset (see [`skills/modeling/references/pipelines.md`](../skills/modeling/references/pipelines.md) for the exact pattern).
- *"Class imbalance — accuracy blocked as headline metric"* → not a bug to fix in code, just report F1/PR-AUC/balanced accuracy instead, as the message suggests.

## PDF or PPTX generation fails outright

**Symptom:** `/datalab:docs` errors out before producing `reports/report.pdf` or `reports/deck.pptx`.

**Cause:** `reportlab` and `python-pptx` are both part of the **core** dependency set — if this fails, `/datalab:setup` likely hasn't been run in the environment Claude Code is using.

**Fix:** Run `/datalab:doctor` to confirm, then `/datalab:setup`. If both packages already show `[OK]`, check that `reports/results.md` and at least one figure actually exist first — `document` refuses to fabricate a report from missing sources; it'll tell you which phase to run first (usually `/datalab:run`) instead of producing an empty PDF.

## `.datalab/state.json` looks wrong or out of sync

**Symptom:** `/datalab:work` says a phase is done that you don't think is, or vice versa.

**Cause:** Either the file was hand-edited, or it was reconstructed from disk (no state file was found, but the project looked real) and the inference guessed wrong.

**Fix:** Just tell Claude what's actually true — e.g., "the model isn't actually trained yet, that was a leftover file" — and continue with `/datalab:work`; it isn't a source of ground truth Claude blindly trusts over you. If you want a clean slate, you can also delete `.datalab/state.json` and let `/datalab:work` reconstruct it from disk again.

## Dependency vulnerability findings (`pip-audit`)

**Symptom:** After `/datalab:setup --full`, a gap-analysis or compliance-checklist step surfaces `pip-audit` findings.

**Cause:** This is the intended behavior of the governance/compliance tooling (see [Compliance checklist](../skills/document/references/cards.md)) — it's flagging known vulnerabilities in your **project's** installed dependencies, not the plugin's.

**Fix:** Review each finding; most resolve with a version bump in your project's `requirements.txt`. If one can't be fixed yet (no patched version available), the compliance checklist has a line for explicitly accepting a known, documented risk rather than leaving it silently unaddressed.
