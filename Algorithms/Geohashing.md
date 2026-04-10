# Geohashing

A technique that encodes latitude and longitude into a single compact string, where shared prefixes indicate geographic proximity.

## Why it matters

Storing lat/lon as two independent fields makes proximity queries complex and expensive. A geohash collapses both into one string, enabling proximity lookups using simple prefix comparisons — something any string-indexed database can do efficiently.

## How it works

The world is recursively divided into a grid, with each subdivision encoded as a character. Divisions follow a Z-order curve (Z-curve), which preserves two-dimensional proximity in the one-dimensional string — meaning a shared prefix indicates closeness in both latitude and longitude.

Precision scales with string length:
- 5 characters → ~5km × 5km area
- 6 characters → ~1.2km × 600m
- 9 characters → ~5m × 5m

**Example:** Duke University in Durham, NC encodes to `dnrug`. Downtown Durham is `dnruu`. Both share the prefix `dnru`, indicating they are close. The 4-character shared prefix means they are quite close (roughly city-scale proximity).

## Key tradeoffs

- **Prefix proximity is approximate** — two points near each other can have different prefixes if they fall on opposite sides of a grid boundary.
- **Edge artifacts** — neighboring cells near grid edges may share no prefix despite being physically adjacent; queries near boundaries require checking multiple cells.
- **Less precise than raw lat/lon** — precision is quantized to the cell size at a given string length, not exact coordinates.
- **Z-curve discontinuities** — the Z-order curve has jumps, so a shared prefix doesn't guarantee the two points are the closest possible pair within that prefix.

## Related concepts

- [Linear Referencing](Linear%20Referencing.md) — an alternative location encoding for positions along a fixed route, using scalar distance rather than a grid hash
