# Expected Result

Running `python examples/rag-knowledge-base/src/rag_demo/run.py` builds a TF-IDF index
(`seed: 42` is recorded in `config.yaml` for consistency with other datalab projects, but
retrieval here is deterministic - a fitted `TfidfVectorizer` + cosine similarity has no
randomness to seed) over the 6 documents in `corpus/` and runs two sample queries.

For the sample query **"How do I export my data?"**, the retriever should return
**`data-export.md`** as the top-1 result.

Verified run (2026-07-19, scikit-learn 1.9.0, pandas 3.0.3, numpy 2.4.4, Python 3.14.6):

```
Loaded 25 chunks from 6 documents in .../rag-knowledge-base/corpus
Built TF-IDF index: 25 chunks x 407 vocabulary terms

Query: How do I export my data?
Top retrieved doc: data-export.md  (score=0.5354)
All top-3 sources: data-export.md(0.535), data-export.md(0.391), data-export.md(0.379)

Query: What are the API rate limits?
Top retrieved doc: api-rate-limits.md  (score=0.6788)
All top-3 sources: api-rate-limits.md(0.679), webhooks.md(0.304), api-rate-limits.md(0.170)
```

Both sample queries retrieve the obviously-correct document as their top-1 hit, each with
comfortable separation from the next-best score - treat a run that returns a different
top-1 doc for either query as a smoke-check failure worth investigating (a corrupted
corpus file, a broken chunker, or a scikit-learn version change in TF-IDF's default
tokenization/stop-word list) rather than as normal variance.

Exact score values may drift slightly across scikit-learn versions (tokenization and
stop-word-list details can change between releases), but the **ranking** - which document
comes out on top for each query - should not.
