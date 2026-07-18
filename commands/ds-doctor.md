---
description: "Health check — verify Python, required packages, and datalab plugin wiring"
---

# datalab doctor

> **Bundled scripts live in the plugin, not the user's project.** Invoke datalab's
> Python scripts with the plugin path, e.g. `python "$CLAUDE_PLUGIN_ROOT/scripts/<name>.py"`.
> If `$CLAUDE_PLUGIN_ROOT` is unset, find the datalab plugin folder (the one containing
> `.claude-plugin/plugin.json`). The working directory is the user's own project.

Run the datalab environment health check and interpret the result for the user.

## Steps

1. Locate the plugin root (the directory containing `.claude-plugin/plugin.json`).
2. Run: `python "$CLAUDE_PLUGIN_ROOT/scripts/doctor.py"`.
3. Read the output. If it reports missing packages, tell the user the exact
   `pip install ...` command printed by the tool.
4. If `plugin.json` is missing/invalid, report that the install may be corrupted.
5. Summarize: healthy, or the specific fixes needed.

Arguments (optional path to a plugin root): `$ARGUMENTS`
