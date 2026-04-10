# Object Storage

Stores discrete objects in flat namespaces (buckets) identified by a key, accessed via REST APIs, with no native query capability on contents.

## Why it matters

Files, images, video, backups, and raw data lake inputs don't fit neatly into databases. Object storage provides virtually unlimited, highly durable, cheap-at-rest storage for unstructured data — and serves as the foundation layer for most modern data lake architectures.

## How it works

Objects are stored in buckets under a flat key namespace (no real directory hierarchy — prefixes simulate folders). Each object contains raw bytes plus metadata. Access is via HTTP REST (PUT, GET, DELETE). Objects must be retrieved and replaced in full — no partial reads/writes at the storage layer. Durability is achieved via cross-zone or cross-region replication. Query engines (Athena, Spark) are layered on top to run SQL against structured files (Parquet, CSV) stored as objects.

## Key tradeoffs

- No native query capability on contents — you must pull data out or attach an external compute engine
- Latency is too high for transactional access patterns (milliseconds per request vs. microseconds for in-memory stores)
- No in-place updates or partial writes — the entire object must be replaced
- **Examples:** AWS S3
