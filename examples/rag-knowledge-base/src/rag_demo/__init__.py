"""rag_demo - offline TF-IDF retrieval-augmented generation (RAG) worked example.

Retrieval (chunk.py -> index.py -> retrieve.py) runs entirely on scikit-learn's
TfidfVectorizer, so this package needs only core deps (pandas, numpy, scikit-learn) and
works with no API key and no network access.

Generation (generate.py) is a clearly-marked STUB: it returns an extractive answer (the
top retrieved chunk) plus the exact prompt a real LLM call would receive. See
generate.py's module docstring for where a real LLM call goes.
"""

__version__ = "0.1.0"
