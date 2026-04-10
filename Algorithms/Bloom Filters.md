# Bloom Filters

A probabilistic data structure that answers "is this item in my set?" with either "definitely not" or "possibly yes."

## Why it matters

Traditional membership testing has real costs: hash tables are memory-intensive at scale, sorted arrays have slow lookups, and database queries require network round trips and disk I/O. Bloom filters provide O(k) lookups (where k is small and constant) with a minimal memory footprint — perfect for filtering out items that definitely aren't present before doing more expensive lookups.

## How it works

Create a bit array of size `n` (initially all zeros) and choose `k` independent hash functions.

**Insert:** Run the item through all `k` hash functions. Each returns an index; set those `k` bits to 1.

**Query:** Run the item through the same `k` hash functions. If any resulting bit is 0 → definitely not in the set. If all bits are 1 → possibly in the set.

**Example** (16-bit array, 3 hash functions):
- Start: `[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]`
- Insert "cat" (hashes to 2, 5, 11): `[0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0]`
- Insert "dog" (hashes to 1, 5, 7): `[0,1,1,0,0,1,0,1,0,0,0,1,0,0,0,0]`
- Query "bird" (hashes to 1, 5, 9): bit 9 is 0 → definitely not present
- Query "snake" (hashes to 1, 5, 11): all bits set → false positive (never actually inserted)

## Key tradeoffs

- **False positives are possible** — bits from different items can overlap, making unseen items look present. False negatives are impossible.
- **No deletions** — you can't unset a bit because it may be shared by multiple items (counting Bloom filters address this at higher memory cost).
- **Tunable accuracy** — larger bit array or more hash functions reduce false positive rate but increase memory or CPU usage.
- **No retrieval** — you can only test membership, not retrieve the stored item.

## Related concepts
- [ClickHouse Indexing Strategies](../Databases/ClickHouse/ClickHouse%20Indexing%20Strategies.md)

