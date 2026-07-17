import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import nb_to_md  # noqa: E402

NB = {
    "cells": [
        {"cell_type": "markdown", "source": ["# Heading\n", "text"]},
        {"cell_type": "code", "source": ["print('hi')"],
         "outputs": [{"output_type": "stream", "text": ["hi\n"]}]},
    ],
    "metadata": {}, "nbformat": 4, "nbformat_minor": 5,
}

def test_markdown_cell_passthrough():
    md = nb_to_md.notebook_to_markdown(NB, include_outputs=False)
    assert "# Heading" in md and "text" in md

def test_code_cell_fenced():
    md = nb_to_md.notebook_to_markdown(NB, include_outputs=False)
    assert "```python\nprint('hi')\n```" in md

def test_outputs_included_when_requested():
    md = nb_to_md.notebook_to_markdown(NB, include_outputs=True)
    assert "hi" in md.split("```python")[1]  # output appears after the code block

def test_convert_file_roundtrip(tmp_path):
    import json
    nb_path = tmp_path / "nb.ipynb"
    nb_path.write_text(json.dumps(NB), encoding="utf-8")
    out = nb_to_md.convert_file(nb_path)
    assert out.suffix == ".md" and out.read_text(encoding="utf-8").strip()
