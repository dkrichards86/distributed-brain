# Text Similarity Measures

Algorithms for quantifying how alike two strings or documents are, each optimized for different definitions of "similar."

## Why it matters

"How similar are these?" is actually several different questions depending on whether you care about character-level edits, word overlap, word order, or semantic meaning. Choosing the wrong measure gives you misleading similarity scores — or worse, wrong matches that feel plausible.

## How it works

### Character-level measures

**Edit distance (Levenshtein)**
Minimum single-character operations (insert, delete, substitute) to transform one string into another.

- Best for: catching typos and small character-level variations in short strings
- Weakness: treats all operations equally; ignores word boundaries and meaning

**Hamming distance**
Count of positions where two equal-length strings differ.

- Best for: fixed-length encodings — error-correcting codes, DNA sequences, binary data
- Weakness: requires equal-length strings; can't handle insertions or deletions at all

**Jaro-Winkler similarity**
Considers matching characters, transpositions, and gives a bonus for matching prefixes. Designed specifically for short strings like names.

- Best for: fuzzy name matching and record linkage ("Jon" vs "John", "Dwayne" vs "Duane")
- Prefix bonus reflects the pattern that people usually get the start of a name right even when they mess up the rest
- Weakness: optimized for short strings; benefits diminish on longer text

---

### Token-level measures

**Jaccard similarity**
Treats texts as sets of tokens. `|intersection| / |union|` of their word sets.

- Best for: comparing shared vocabulary without caring about order or frequency — tag sets, topic similarity
- Weakness: ignores word order and frequency; "The cat sat on the mat" and "The mat sat on the cat" are identical

**Cosine similarity**
Represents documents as term-frequency vectors; measures the angle between them. Normalized for document length, so a short paragraph and a long essay can be similar if they emphasize the same terms.

- Best for: [[Search Databases|document search]] and recommendation — the workhorse for most text retrieval systems
- Weakness: bag-of-words model ignores word order; "car" and "automobile" treated as completely different

---

### Semantic measures

**Sentence embeddings**
Neural networks map text to dense vectors where semantically similar texts cluster together, even with different words.

- Best for: paraphrase detection, semantic search, question answering — anywhere meaning matters more than words
- "The car is red" and "The automobile is crimson" score high despite sharing no words
- Weakness: requires a pre-trained model, inference compute, and careful model selection for your domain; black box — you can measure similarity but not easily explain it

---

### Choosing the right measure

| Need | Use |
|---|---|
| Typos and character edits | Edit distance or Jaro-Winkler |
| Fixed-length encodings | Hamming distance |
| Fuzzy name matching | Jaro-Winkler |
| Shared vocabulary / topic overlap | Jaccard |
| Document search with term frequency | Cosine similarity |
| Meaning across different vocabulary | Embeddings |

## Key tradeoffs

- **Precision vs. semantics** — character-level measures are precise about edits but blind to meaning; semantic embeddings capture meaning but are computationally expensive and opaque
- **Speed vs. quality** — Hamming is O(n), edit distance is O(n²), embeddings require model inference; pick the cheapest measure that's good enough for your use case
- **Short vs. long strings** — Jaro-Winkler degrades on long text; cosine similarity and Jaccard don't scale well to very short strings
- **Order sensitivity** — Jaccard and cosine similarity are bag-of-words models that ignore word order; if order matters, you need a different approach
