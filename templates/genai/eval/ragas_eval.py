"""RAG evaluation for {{project}} via ragas (faithfulness, answer relevance,
context precision).

ragas is imported lazily so this module doesn't hard-fail until the +genai
tier's dependencies are installed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _ragas():
    try:
        from ragas import evaluate
        from ragas.metrics import answer_relevancy, context_precision, faithfulness
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError("ragas is required for RAG evaluation. Install it with: pip install ragas") from exc
    return evaluate, [faithfulness, answer_relevancy, context_precision]


def evaluate_dataset(records: list[dict]):
    """`records` need question/answer/contexts/ground_truth keys - see ragas docs via Context7."""
    from datasets import Dataset

    evaluate, metrics = _ragas()
    dataset = Dataset.from_list(records)
    return evaluate(dataset, metrics=metrics)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run ragas evaluation for {{project}}")
    ap.add_argument("--input", required=True, help="JSON file: list of {question, answer, contexts, ground_truth}")
    ap.add_argument("--output", default="reports/ragas_eval.json")
    args = ap.parse_args(argv)

    records = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = evaluate_dataset(records)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(dict(result), indent=2, default=str), encoding="utf-8")
    print(f"[ragas] wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
