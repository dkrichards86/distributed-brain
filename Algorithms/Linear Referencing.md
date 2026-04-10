# Linear Referencing

A way to encode locations along a fixed route as a single distance measurement from a known starting point, instead of lat/lon coordinates.

## Why it matters

Lat/lon is a general-purpose coordinate system that doesn't naturally express "position along a path." Linear referencing matches how humans intuitively describe locations on routes — trails, roads, pipelines — using distance from a known landmark rather than abstract coordinates.

## How it works

Pick a starting point on a route (the "reference point") and measure distance from there. Every location on that route gets a single scalar value: how far along it sits.

**Example:** Instead of storing a waterfall at `(35.9940, -78.8986)`, you store it as "0.7 miles from the trailhead on Riverside Trail." A hiker reading "1.2 miles on Lakeside Loop" immediately knows where to go without a GPS lookup.

The geometry of the route itself is stored separately. The linear reference value is only meaningful relative to that route definition.

## Key tradeoffs

- **Route-dependent** — references are only valid for a specific route. If the path is rerouted significantly, all measurements along it need recalculation.
- **Linear features only** — only works for things that exist on the route itself. Nearby-but-off-path landmarks don't fit naturally.
- **No cross-route queries** — finding "everything within 1 mile of this point" requires converting back to coordinates; you can't query across routes with a simple scalar comparison.
- **Intuitive for humans, awkward for GIS** — great for user-facing descriptions; requires extra translation work when integrating with coordinate-based spatial systems.

## Related concepts

- [Geohashing](Geohashing.md) — encodes lat/lon into a grid-based string for proximity queries; a general-purpose alternative to route-specific linear references
