# Sample outputs

These are **real deliverables** datalab produces, generated from the
`examples/iris-classification` project so you can see the output without running anything.

| File | What it is | Produced by |
|------|-----------|-------------|
| `iris-report.pdf` | A results report (problem → data → method → results → conclusion) | `/datalab:docs` → `scripts/generate_report.py` |
| `iris-deck.pptx` | A presentation deck of the same results | `/datalab:docs` → `scripts/generate_deck.py` |
| `figures/confusion_matrix.png` | A model-evaluation figure | `scripts/plots.py` |
| `iris-report.md`, `iris-deck.md` | The Markdown sources the PDF/PPTX were rendered from | assembled by the `document` skill |

Numbers reflect an actual run: test accuracy **0.911**, 5-fold CV **0.960 ± 0.039**,
comfortably beating a 0.333 dummy baseline. Regenerate them yourself with:

```
python scripts/generate_report.py --input examples/sample-outputs/iris-report.md --output examples/sample-outputs/iris-report.pdf --title "Iris Classification Report"
python scripts/generate_deck.py   --input examples/sample-outputs/iris-deck.md   --output examples/sample-outputs/iris-deck.pptx --title "Iris Classification"
```
