# Benchmark Tests

Tests that measure code execution time and memory allocation under controlled, repeatable conditions to quantify performance trade-offs.

## Why it matters

Intuition about performance is often wrong, and premature optimization is expensive. Benchmarks replace guesses with measurements — letting you confirm a suspected bottleneck is real, quantify the improvement from a proposed fix, and make trade-off decisions (speed vs. memory) with actual numbers. They complement unit tests: tests verify correctness, benchmarks verify performance.

## How it works

### Basic mechanism

Run the target code many times, measure total elapsed time, divide by iterations to get average time per operation. The framework determines iteration count dynamically, increasing it until measurements are stable.

In Go:

```go
func BenchmarkGroupElements(b *testing.B) {
    data := generateTestData()  // setup outside the timer

    b.ResetTimer()              // exclude setup from measurement
    for i := 0; i < b.N; i++ {
        groupElements(data)     // b.N determined by the framework
    }
}
```

`b.ResetTimer()` ensures setup time doesn't contaminate results. `b.N` is chosen automatically for statistical stability.

### Memory tracking

```go
b.ReportAllocs()
```

Adds `allocs/op` and `B/op` to output — allocations per operation and bytes allocated. Essential for understanding GC pressure and evaluating speed vs. memory trade-offs.

### Running benchmarks (Go)

```bash
go test -bench=.                     # run all benchmarks
go test -bench=. -benchmem           # include memory stats
go test -bench=. -benchtime=10s      # longer run for noisy systems
```

Sample output:
```
BenchmarkGroupElements-8    10000    123456 ns/op    4096 B/op    12 allocs/op
```

`-8` = CPU cores available. Each column: iterations, time per op, bytes per op, allocations per op.

### Environment matters

Results are sensitive to:
- Background processes (close unnecessary applications)
- Thermal throttling on laptops (long runs skew results as CPU heats up)
- Time of day (scheduled tasks, system updates)
- Machine class (don't compare laptop benchmarks to CI benchmarks)

Run on a quiet system. Run multiple times to understand variance.

### Interpreting results

Numbers are only meaningful in context. A 10x speedup matters if the code is in a hot path on large datasets. The same improvement is irrelevant if the code runs once per day on tiny inputs.

**Key questions:**
1. Is this code on a hot path?
2. Does the improvement fit within resource constraints (memory, CPU)?
3. Does the benchmark reflect realistic data — distribution, size, access patterns?

For interpreting system-level performance measurements, see [Metrics and Percentiles](../Observability/Metrics%20and%20Percentiles.md).

### Common pitfalls

- **Synthetic data that doesn't match production** — uniform random data may represent a best case; skewed production data can change results significantly
- **Benchmarking the wrong thing** — micro-optimizing a function that runs once per request while ignoring a function called 10,000 times
- **Cross-machine comparisons** — absolute numbers aren't comparable across different hardware; compare relative improvements on the same machine
- **Ignoring warm-up effects** — the first few iterations may be slower due to cold caches; most frameworks handle this, but be aware of it

## Key tradeoffs

- **Benchmark accuracy vs. environment noise** — ideal benchmarks run on dedicated quiet hardware; real benchmarks run on developer laptops; understand the noise floor of your setup
- **Speed vs. memory** — faster algorithms often allocate more; `ReportAllocs` makes this trade-off visible before committing to an approach
- **Micro-benchmark vs. production profile** — micro-benchmarks measure isolated operations; production profiling (pprof, etc.) measures the real system under real load; both are necessary for different decisions
