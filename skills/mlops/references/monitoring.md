# Drift monitoring (Evidently)

## Structure

```
monitoring/
  reference_data.py     # or a pointer to data/processed's training snapshot
  drift_report.py         # generates the Evidently report
```

## Pattern

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset

report = Report(metrics=[DataDriftPreset(), TargetDriftPreset()])
report.run(reference_data=reference_df, current_data=current_df)
report.save_html("monitoring/drift_report.html")
```

Check Context7 for the current Evidently `Report`/preset API before writing this — the
package has renamed/reorganized presets across versions; don't assume the import path from
memory.

## Rules

- **Reference dataset** = the training data snapshot (or a deliberately-chosen held-out
  slice) that the deployed model was validated against — pin it, don't silently let
  "reference" mean "whatever's in `data/processed` right now."
- **Current dataset** = the latest batch of incoming/production data (or, if there's no live
  traffic yet, the most recent batch the user wants to check against reference).
- **Report both feature drift and target/prediction drift** — feature drift alone can be
  benign if the model is still calibrated; prediction drift is the more direct signal
  something's wrong.
- **Threshold + action**: state what drift level should trigger a retrain/investigation (a
  specific dataset-drift-share threshold from Evidently's summary, or a per-column p-value
  cutoff) — a drift report nobody acts on is not monitoring.
- **Scheduling**: this skill wires the *capability*; running it on a cron/schedule against
  live production data is deployment infrastructure outside this plugin's scope (v1) — say so
  if the user asks for it, and point at where the script would plug into their own scheduler.
