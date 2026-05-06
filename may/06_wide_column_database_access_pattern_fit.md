# When Your "Database" Is the Wrong Shape for Your Workload

## The scene

Your fraud detection service hits 50,000 transactions per second at peak. The relational database behind it has 14 read replicas. P99 latency is 380ms — and climbing. Every new feature means another index. Every index means slower writes. The on-call engineer wakes up to the same alert three times this week: replica lag exceeded threshold.

## Why it hurts

You're paying for vertical scale that won't bend any further. The schema migration to add one column took 6 hours of locked tables. Sub-millisecond reads are impossible because the storage engine wasn't built for them. And the analytics team copies the entire dataset to a warehouse nightly — because the OLTP system collapses under any query that touches more than a few thousand rows.

## What's actually happening underneath

You picked a database designed for **strong consistency and arbitrary joins** — and used it for a workload that needs **massive write throughput, predictable single-digit-millisecond reads, and a schema that mutates daily**. Relational engines optimize for row integrity across complex relationships. They keep B-trees balanced, hold locks, replicate write-ahead logs. None of that helps when your access pattern is *"give me the last 100 events for user X, in 5ms, while ingesting two million events per second from IoT devices."* The bottleneck isn't your hardware. It's the shape of the data model versus the shape of the workload.

## The shift

**Stop choosing a database by familiarity. Choose it by access pattern.**

Time-series, telemetry, feature stores, and live serving layers don't need joins — they need a wide-column store with row-key locality, automatic sharding, and tiered storage.

## The fix

Move the hot path to a NoSQL wide-column engine. Row keys carry the access pattern: `user#123#ts#1735689600`. Reads stay local to a tablet, served in milliseconds at any scale. Writes append; no locks, no migrations. Old data tiers automatically to cold storage. Run streaming connectors in parallel for analytics — and keep the relational system only for what actually needs joins. The architecture stops fighting itself.

## The question to sit with

Is your database slow because it's underprovisioned — or because you asked it to do a job it was never designed for?
