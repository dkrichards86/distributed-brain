# SQL Normalization

A set of rules (normal forms) for organizing relational database schemas to reduce redundancy and improve data integrity.

## Why it matters

Unnormalized data creates maintenance burdens — updating one fact requires finding and changing every row that stores it. Normalization eliminates these anomalies by ensuring each fact is stored once, in one place.

## How it works

Normal forms are progressive: each form requires satisfying all prior forms.

### First Normal Form (1NF)

All attributes must be **atomic** — no field may contain multiple values.

❌ Violation: `staff_email = "john@a.com, john@b.com"` (two emails in one field)

✅ Fix: Move emails to a separate `staff_email` table with one row per email address.

Rule: no repeating groups or multi-valued attributes.

---

### Second Normal Form (2NF)

Every non-key attribute must depend on the **whole** candidate key, not just part of it. Applies when the candidate key is composite.

❌ Violation: `(project_num, team) → role, team_hq` where `team_hq` depends only on `team`, not on `project_num`.

✅ Fix: Move `team_hq` to a separate `teams` table keyed by `team`.

Rule: no partial dependencies on a composite key.

---

### Third Normal Form (3NF)

All non-key attributes must depend **directly** on the candidate key, not transitively through another non-key attribute.

❌ Violation: `staff_num → manager_num → manager_name` — `manager_name` depends on `manager_num`, not on `staff_num` directly.

✅ Fix: Move `manager_name` to a separate `managers` table keyed by `manager_num`.

Rule: no transitive dependencies.

---

### Boyce-Codd Normal Form (BCNF)

Strengthens 3NF. Every determinant must be a candidate key. Eliminates reverse dependencies where a non-key attribute determines another attribute.

Example: if skills are always done in a specific language (skill → language), and a table stores `(staff_num, language, skill)`, the language is derivable from the skill. Split them.

Sometimes called "3.5NF." Required when 3NF leaves anomalies due to overlapping candidate keys.

---

### Fourth Normal Form (4NF)

No multivalued dependencies — a table shouldn't store two independent multi-valued facts about the same entity.

❌ Violation: `(project_num, staff_num, project_need)` where staff and project needs are independent facts about a project.

✅ Fix: Separate into `(project_num, staff_num)` and `(project_num, project_need)`.

Rarely encountered in practice.

---

### Fifth Normal Form (5NF)

Decomposed tables must rejoin without gaining or losing rows. Eliminates join dependencies.

Even rarer in practice. Relevant when a relation can only be decomposed into three or more tables without loss.

---

### In practice

The normal forms are guiding principles, not hard requirements. 3NF is the standard target for most OLTP schemas. BCNF is worth considering when anomalies persist after 3NF. 4NF and 5NF are academic in most production work.

Deliberate denormalization is often justified for read performance, reporting tables, or when join cost exceeds update anomaly risk.

## Key tradeoffs

- **Normalization vs. query performance** — more normal forms = fewer anomalies, but more [[SQL Joins]] needed at query time; heavily normalized schemas can be slow for read-heavy workloads
- **Update simplicity vs. read simplicity** — normalization makes writes clean (one fact in one place) but reads complex (joins everywhere)
- **Intentional denormalization** — analytics tables, materialized views, and read replicas often store denormalized data for performance; the key is knowing when you're denormalizing on purpose vs. by accident
- **Maintenance burden** — violating 2NF or 3NF means updating one fact in multiple rows; in large tables this is error-prone and slow

