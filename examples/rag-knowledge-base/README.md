# RAG Knowledge Base - datalab Worked Example

A small, real, end-to-end **retrieval-augmented generation (RAG)** project used both as a
demo of the `datalab` plugin's GenAI/RAG tier and as a smoke-test fixture for the
plugin's own test suite. It mirrors [`examples/iris-classification`](../iris-classification)
in spirit: real content, a verified run, and an `EXPECTED.md` you can check your own run
against.

## This is an OFFLINE RETRIEVAL demo - read this before anything else

**Retrieval is real. Generation is a stub.** The two halves of RAG behave very
differently here on purpose:

- **Retrieval** (`chunk.py` -> `index.py` -> `retrieve.py`) is a fully working,
  fully offline implementation using scikit-learn's `TfidfVectorizer` and
  `cosine_similarity` - classic lexical (bag-of-words) search, not neural embeddings.
  It needs **no API key, no network access, and no heavy dependencies**: just the
  `datalab` core stack (pandas, numpy, scikit-learn - see
  `scripts/requirements.txt`), which is installed automatically.
- **Generation** (`generate.py`) is a **clearly-marked stub**. Turning retrieved
  passages into a fluent, synthesized answer needs an LLM call, which needs an LLM
  client library (e.g. `pip install openai`) and an API key
  (e.g. `OPENAI_API_KEY`) - neither of which this example installs or requires. Instead,
  `answer()` returns:
  1. the exact **grounded prompt** a real LLM call would receive (system instructions +
     retrieved context + the question), so you can see what "grounded" means, and
  2. an honest **extractive** stand-in answer, literally the verbatim text of the
     single highest-scoring retrieved chunk, never invented or paraphrased text.

  Open `src/rag_demo/generate.py` and look for the `# TODO: real generation` block;
  it shows exactly where a real `client.messages.create(...)` call goes and what it
  needs. Wiring that up for real needs the `genai` tier's ideas (grounding, prompt
  construction) but, notably, **not** the heavy embeddings/vector-store libraries in
  `scripts/requirements-genai.txt` (LangChain, ChromaDB, sentence-transformers) - those
  are for a *neural* retrieval path; this example's retrieval is TF-IDF and already
  works without them. All you'd add is an LLM client and a key.

Why build it this way? So this example runs **everywhere, immediately, for free**:
in CI, offline, on a laptop with no credentials configured, while still being a real,
inspectable RAG pipeline rather than a hand-wave.

## What's here

```
rag-knowledge-base/
├── README.md               # this file
├── EXPECTED.md              # expected top-1 retrieval result, for smoke-checking
├── config.yaml               # seed, task type, corpus path
├── corpus/                   # 6 small markdown docs - one fictional SaaS product's docs
│   ├── authentication.md     # API keys, bearer tokens, key rotation
│   ├── api-rate-limits.md    # per-plan limits, headers, 429s
│   ├── billing.md            # plans, invoicing, failed-payment handling
│   ├── data-export.md        # CSV/JSON/PDF export, async export jobs
│   ├── sso.md                 # SAML/SCIM single sign-on
│   └── webhooks.md            # event subscriptions, signatures, retries
└── src/rag_demo/
    ├── __init__.py
    ├── chunk.py               # load corpus/*.md, split into paragraph-sized chunks
    ├── index.py                # fit a TfidfVectorizer over the chunks
    ├── retrieve.py              # top-k retrieval by cosine similarity, with scores
    ├── generate.py               # STUB generation - extractive answer + assembled prompt
    └── run.py                    # end-to-end demo: index the corpus, run 2 sample queries
```

## The corpus

Six short markdown documents form a coherent mini knowledge base: the docs for a
fictional project-tracking SaaS product called **NimbusBoard**. Each doc is a few real,
readable paragraphs covering one topic (billing, authentication, rate limits, data
export, SSO, webhooks) - realistic enough that lexical retrieval has to actually
discriminate between topics, not just match on the product name.

## The pipeline

1. **`chunk.py`** - loads every `.md` file in `corpus/` and splits it into
   paragraph-sized chunks (further splitting any paragraph longer than ~500 characters
   on word boundaries). Returns a flat list of `{"doc": ..., "text": ...}` dicts.
2. **`index.py`** - fits a single `sklearn.feature_extraction.text.TfidfVectorizer`
   (English stop words removed) over all chunk texts and wraps the fitted vectorizer,
   matrix, and chunk list in a `RagIndex`.
3. **`retrieve.py`** - `retrieve(index, query, k=3)` transforms the query into the same
   TF-IDF space, scores every chunk with `sklearn.metrics.pairwise.cosine_similarity`,
   and returns the top-k chunks sorted by score.
4. **`generate.py`** - `answer(index, query, k=3)` calls `retrieve()`, assembles a
   grounded prompt (system instructions + numbered retrieved context + the question),
   and returns that prompt alongside the extractive stub answer described above.
5. **`run.py`** - wires the above together end-to-end: builds the index once over
   `corpus/`, then runs two sample queries, printing the top retrieved doc, its score,
   the full assembled prompt, and the stub answer for each.

## Reproduce it

Run the demo script directly, no setup beyond datalab's core dependencies
(pandas, numpy, scikit-learn), which install automatically the first time you use the
plugin:

```
python examples/rag-knowledge-base/src/rag_demo/run.py
```

`run.py` inserts `src/` onto `sys.path` itself, so it works from any working directory.

Or treat this folder as an existing `datalab` project:

```
cd examples/rag-knowledge-base
/datalab:work
```

`/datalab:work` will detect the existing `config.yaml` and `corpus/` layout (there's no
`.datalab/state.json` yet, so it reconstructs state from what's on disk) and propose next
steps, including, if you want it, wiring up real generation via Context7-checked
current LLM SDK docs (see `skills/modeling/SKILL.md` and the `genai` template tier in
`templates/genai/`).

See `EXPECTED.md` for the expected top-1 retrieval result on the sample query
"How do I export my data?" - treat a different top-1 doc as a smoke-check failure worth
investigating (a broken chunker, a corrupted corpus file, or a scikit-learn version
change in TF-IDF's default tokenization) rather than as normal variance; unlike a
statistical model, this pipeline is deterministic - the same corpus and query always
score the same way.

## Notes

- `corpus/*.md` is plain ASCII on purpose (no em dashes, no curly quotes): printing
  retrieved chunk text to stdout is otherwise sensitive to the terminal/OS's default
  text encoding, and this example is meant to run anywhere without surprises.
- `retrieve()` and `answer()` both take an already-built `RagIndex` rather than
  building one internally on every call, so `run.py` fits the `TfidfVectorizer` exactly
  once and reuses it for both sample queries; fitting is the relatively expensive step,
  scoring a query against an already-fitted index is cheap.
- Cosine similarity scores here are a **lexical overlap signal**, not a probability or a
  confidence percentage; they're useful for ranking chunks against each other for the
  same query, not for comparing scores across different queries.
