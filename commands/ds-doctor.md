---
description: "Health check — verify Python, required packages, and datalab plugin wiring"
---

# datalab doctor

Run the datalab environment health check and interpret the result for the user.

## Steps

1. Locate the plugin root (the directory containing `.claude-plugin/plugin.json`).
2. Run: `python scripts/doctor.py` from the plugin root.
3. Read the output. If it reports missing packages, tell the user the exact
   `pip install ...` command printed by the tool.
4. If `plugin.json` is missing/invalid, report that the install may be corrupted.
5. Summarize: healthy, or the specific fixes needed.

Arguments (optional path to a plugin root): `$ARGUMENTS`
