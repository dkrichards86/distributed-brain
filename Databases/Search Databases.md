# Search Databases

Store data with inverted indices that map terms to the documents containing them, enabling fast full-text retrieval with relevance ranking.

## Why it matters

SQL `LIKE` queries and exact-match indexes don't handle the messy reality of text search — typos, synonyms, partial words, and ranking by relevance. Search databases are built specifically for this: they analyze text at write time and return ranked results with sub-second latency at scale.

## How it works

At index time, text fields are analyzed — tokenized into terms, lowercased, stemmed (e.g. "running" → "run"), and stored in an inverted index mapping term → list of document IDs. At query time, the query is similarly analyzed, matched against the inverted index, and documents are scored by relevance (TF-IDF or BM25). [[Text Similarity Measures|Fuzzy matching]], boosting, and faceted filters are layered on top.

## Key tradeoffs

- Higher storage overhead from indexing — the inverted index can be as large as or larger than the raw data
- Consistency during updates is complex — index updates are near-real-time, not immediately consistent
- Not suited for simple transactional workloads or as a system of record
- **Examples:** Elasticsearch

