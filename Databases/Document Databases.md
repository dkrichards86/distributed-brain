# Document Databases

Store data as flexible JSON-like documents where each document can have a different shape — no predefined schema required.

## Why it matters

When data models evolve rapidly or vary per entity, relational schemas become a bottleneck. Document databases let you ship and iterate without upfront schema design or migrations, and store nested structures naturally without joins.

## How it works

Each record is a self-contained document (typically JSON or BSON). Documents are grouped into collections but are not required to share a schema. Query languages traverse nested fields and filter on any attribute. Indexes can be built on any field, including nested ones. No joins — related data is either embedded or fetched in separate queries.

## Key tradeoffs

- No complex joins across documents — you either denormalize (embed) or handle relationships in application code
- Referential integrity is your problem — the database won't enforce foreign-key-style constraints
- ACID guarantees vary by implementation and version; multi-document transactions are often limited or expensive
- **Examples:** MongoDB
