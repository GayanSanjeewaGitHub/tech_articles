# The Physics of Shared vs. Private Resources: PostgreSQL's io_uring Design Decision

## The Trap

We think resource sharing is always the "mature" engineering choice. Pooling, sharing, reusing — these words carry an implicit virtue in systems design. **More sharing = less waste**, right?

So when a new high-performance I/O primitive like `io_uring` arrives — a kernel-bypass mechanism that lets userspace submit I/O operations through a shared ring buffer — the instinct is obvious: **create a pool of io_uring instances and let all PostgreSQL backend processes share them.**

Fewer file descriptors. Less memory overhead. Elegant.

Except it's wrong.

## The "Stop Time" Moment

**Ask yourself: What is the actual cost you're optimizing for?**

An `io_uring` instance is, at its core, just a file descriptor — the same atomic unit as an `epoll` instance. When PostgreSQL spawns a backend process per connection (default: 100 connections = 100 processes), a private `io_uring` per backend means 100 additional file descriptors.

That sounds expensive. But pause.

**Imagine this scenario:** Two backend processes submit I/O jobs to the same shared `io_uring` ring. Process A writes a page to disk. Process B writes a different page. Their submissions interleave on the same ring buffer. Without a mutex, they corrupt each other's work. With a mutex, they serialize — and now your "high-performance I/O path" has a lock in it.

**What is being wasted here?** Not file descriptors. *Latency.*

## The Mental Model Shift

> **Stop thinking in resource counts. Start thinking in contention surfaces.**

The trap is measuring cost in the wrong unit. File descriptors are cheap — they're integers backed by kernel structures that consume kilobytes. Contention is expensive — it's a *time* cost that compounds non-linearly under load.

Here's the thinking shift:

- **Old model:** "Fewer resources = more efficient." You count objects.
- **New model:** "Fewer lock acquisitions = more efficient." You count *wait events*.

This is the same physics that governs every shared-resource decision in systems engineering:

| Approach | Visible Cost | Hidden Cost |
|---|---|---|
| **Shared pool** | Fewer file descriptors | Mutex contention, serialized I/O, priority inversion |
| **Private instance** | More file descriptors | Slightly higher memory footprint |

The hidden cost of sharing *always* dominates at scale.

## The "What If" Scenarios

**Scenario 1: The Connection Pool Analogy.**
Think of database connection pools. Why don't we just have *one* connection shared by all threads? Because the locking overhead to protect a single connection from concurrent use would annihilate throughput. The same principle applies to `io_uring`. A shared ring is a shared connection — and shared connections under contention become bottlenecks, not assets.

**Scenario 2: The Parking Lot Problem.**
A shared `io_uring` pool is like a parking garage with 10 spots for 100 cars. Yes, you've saved land (file descriptors). But now every car circles the garage waiting for a spot (lock acquisition). A private driveway per house costs more land but eliminates the circling entirely. **The waste isn't in the driveways — it's in the circling.**

**Scenario 3: The False Economy.**
You "save" 90 file descriptors by sharing 10 `io_uring` instances instead of allocating 100 private ones. But Linux's default `ulimit` for file descriptors is 1024 (soft) and easily tunable to millions. You've optimized a constraint that *isn't binding* — while introducing a constraint (contention) that *is*.

## The Architecture

The PostgreSQL developers explored both designs — and the verdict was definitive.

**The shared pool model** required mutexes to prevent concurrent submissions from corrupting ring state. The locking overhead and resulting latency *exceeded* the cost of simply maintaining private instances. The elegant solution was slower than the "wasteful" one.

**The private model** — one `io_uring` file descriptor per backend process — won. Each backend owns its ring. No locks. No contention. No coordination overhead. The cost is linear in the number of backends, and the resource (file descriptors) is trivially scalable on modern Linux.

**The deeper lesson?** When you find yourself optimizing for a resource that the operating system gives you cheaply (file descriptors, memory pages, thread-local storage), ask whether you're *actually* introducing a resource the operating system handles poorly (locks, context switches, cache invalidation).

*Hint: The most expensive resource in any concurrent system is never the one you can count in `htop`. It's the one that only shows up in `perf lock`.*

---

**Thinking Shift Summary:**
- Sharing isn't free — it costs *coordination*.
- Contention is a hidden tax that doesn't appear in resource dashboards.
- The correct unit of cost in concurrent systems isn't *objects* — it's *wait time*.
- When in doubt, prefer isolation. The kernel is better at managing file descriptors than your application is at managing mutexes.
