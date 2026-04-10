# SQL Joins

SQL operations that combine rows from two or more tables based on a related column between them.

## Why it matters

[[SQL Normalization|Normalized]] relational data is spread across multiple tables by design. Joins are the primary mechanism for reuniting related data at query time without denormalizing the schema.

## How it works

ANSI SQL defines five join types:

### INNER JOIN

Returns only rows where the join predicate is satisfied in **both** tables. Rows without a match in either table are excluded.

```sql
SELECT project_staff.project_num, staff.staff_num, staff.staff_name
FROM staff
INNER JOIN project_staff ON project_staff.staff_num = staff.staff_num;
```

Use when: you only want records that have a matching counterpart.

---

### LEFT OUTER JOIN

Returns **all rows from the left table**, plus matching rows from the right. Where there's no match in the right table, columns from the right are `NULL`.

```sql
SELECT project_staff.project_num, staff.staff_num, staff.staff_name
FROM staff
LEFT OUTER JOIN project_staff ON project_staff.staff_num = staff.staff_num;
```

Use when: you want everything from the primary entity regardless of whether it has related records.

---

### RIGHT OUTER JOIN

Mirror of LEFT OUTER JOIN. Returns **all rows from the right table**, plus matching rows from the left. Rarely used in practice — most queries rewrite as a LEFT JOIN by swapping table order.

---

### FULL OUTER JOIN

Returns **all rows from both tables**. Matched rows are combined; unmatched rows from either side appear with `NULL`s for the other table's columns. Conceptually: LEFT JOIN + RIGHT JOIN merged.

Use when: you want a complete picture of both tables including unmatched rows on either side.

---

### CROSS JOIN

Returns the **Cartesian product** — every row from the first table paired with every row from the second. No join predicate.

```sql
SELECT * FROM staff CROSS JOIN project_staff;
```

3 staff × 8 project_staff rows = 24 output rows.

Use when: intentionally generating all combinations. Rarely used in practice; accidental cross joins on large tables are expensive.

---

### Quick reference

| Join type | Returns |
|---|---|
| INNER | Only matched rows from both tables |
| LEFT OUTER | All rows from left + matched rows from right |
| RIGHT OUTER | All rows from right + matched rows from left |
| FULL OUTER | All rows from both, matched or not |
| CROSS | All combinations (Cartesian product) |

## Key tradeoffs

- **INNER vs. OUTER** — INNER is typically more efficient because it produces fewer rows; OUTER joins require materializing the full left/right table even when most rows have no match
- **Join order** — query planners generally pick optimal join order, but on complex queries with many joins, explicit ordering or hints can matter
- **Null handling** — OUTER join NULLs in WHERE clauses require `IS NULL` not `= NULL`; this trips up queries that filter on outer-join columns
- **Normalization cost** — the more [[SQL Normalization|normalized]] the schema, the more joins queries need; heavily normalized schemas trade storage efficiency for query complexity
