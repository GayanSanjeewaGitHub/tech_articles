# CPU Time vs. Wall Clock Time: Why Your 1.5 CPU Limit Doesn't Do What You Think

## The Problem: Your Container Gets Throttled and You Don't Know Why

You set `cpu.cfs_quota_us = 150000` with `cpu.cfs_period_us = 100000` — a 1.5 CPU limit. Your Node.js app is single-threaded. It gets throttled constantly. Adding more CPU doesn't help. **You're confusing CPU time with wall clock time.**

- Your app needs 150ms of CPU work but only gets a 100ms scheduling window
- The remaining 50ms can't carry over — **CPU time is not saveable**
- It can't borrow from the next window either — **that would violate CFS fairness**
- Single-threaded apps on >1 CPU limit waste the excess entirely

## Why This Happens

- **CFS (Completely Fair Scheduler) works in fixed windows** — quota resets every period, no rollover
- **CPU time ≠ wall clock time** — 1.5 CPUs means 150ms of CPU time per 100ms wall clock, not 150ms on one core
- **Single-threaded apps can only consume 1 CPU-core-worth per window** — the extra 0.5 CPUs are unreachable

## The Mental Model Shift

> **Stop thinking in "how much CPU." Start thinking in "how many threads can burn quota in parallel within one window."**

| Scenario | Threads | What Happens in 100ms Window |
|---|---|---|
| 1 CPU, 1 thread | 1 | Max 100ms CPU time used. Remaining 50ms quota wasted |
| 1 CPU, multiple threads | N | Threads share the core. Total CPU time still ≤ 100ms per window |
| Multiple CPUs, multiple threads | N | 5 threads on separate cores can exhaust 150ms quota in 30ms wall clock → **throttled for remaining 70ms** |

## Real Consequences

- **Node.js with 1.5 CPU limit:** Main thread can only use 1.0 of the 1.5. The extra 0.5 only helps GC, libuv, and worker threads — marginal benefit
- **Java with 1.5 CPU limit:** Multiple threads burn through 150ms quota in <100ms wall clock → process sleeps until next window → latency spike users can feel
- **Over-provisioning single-threaded apps:** You're paying for CPU your app physically cannot use

## The Solution: Match Limits to Thread Model

- **Single-threaded apps (Node.js main thread):** Set CPU limit to ~1.0. Anything above 1.0 is wasted on the main thread
- **Multi-threaded apps (Java, Go):** Higher limits work — threads consume quota in parallel across cores
- **Know your throttle point:** If N threads exhaust quota in `(quota / N)` wall clock ms, the process sleeps for the remainder of the period

## The Question to Sit With

If your container's CPU quota resets every 100ms with no rollover and no borrowing, **how many of your production services are configured with CPU limits that their thread model can never actually reach?**
