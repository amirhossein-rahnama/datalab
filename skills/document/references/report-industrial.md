# Industrial report template

Section order for `reports/report.md` when `profile == industrial`. Each section is a `##`
heading in the Markdown that `generate_report.py` renders to PDF.

## Executive summary
3-5 sentences a stakeholder reads first and possibly *only*: the business problem, what was
built, the headline result framed as business impact (not just a raw metric), and the
recommendation. Write this **last**.

## Problem
The business problem/decision this project supports, who the stakeholder is, what decision
the model's output feeds into, and the cost of getting it wrong (false positive vs false
negative cost, if applicable -- ties to the metric-choice discussion later).

## Data
Where the data comes from, size, refresh cadence if it's a production feed, and any data
quality caveats from `eda` that matter for trust (missingness, known biases).

## Approach
The modeling approach in plain language -- what was tried, why the final approach was chosen,
without requiring ML background to follow. Save pipeline internals for an appendix or the
repo itself; this section is for a decision-maker.

## Results
The leaderboard framed around the decision metric, with the baseline shown for contrast
("current process" or Dummy baseline vs the model). Include the business-impact framing here,
not just the raw number (e.g., "reduces false declines by X%" rather than only "F1 = 0.87").

## Business impact
Quantify, where possible: cost/time saved, error reduction, what changes operationally if
this ships. State assumptions explicitly (e.g., "assumes current volume of ~10k requests/mo").
If quantification isn't possible yet, say what would be needed to quantify it (a pilot, a
cost model from the stakeholder).

## Next steps
Concrete, prioritized: what's needed to deploy (does `+mlops` exist / is it wired?), what
monitoring should watch for, what would improve the model further, and any open risk
(fairness findings, data-quality debt) that should be tracked, not buried.

## Style notes
- Lead with the conclusion in every section (inverted pyramid) -- a stakeholder skimming
  should get the point from the first sentence of each section.
- Minimize jargon; when a technical term is necessary, define it in one clause inline.
- The PPTX deck (`generate_deck.py`) is a condensed version of this report, not a separate
  narrative -- keep them consistent.
