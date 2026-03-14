# The Physics of Copy-on-Write: Why Your Fork Costs Nothing Until It Doesn't

## The Trap

We think `fork()` copies a process. We read the man page — "creates a child process" — and imagine the kernel duplicating the entire memory space: heap, stack, data segments, everything. A full photocopy of the parent, byte by byte.

If that were true, forking a process with 2 GB of resident memory would require allocating another 2 GB instantly. Every fork would be an expensive, blocking operation. Web servers that fork per request would collapse under their own weight. Process pools would be memory suicide.

But they don't collapse. Redis forks to snapshot its dataset. PostgreSQL forks for every new connection. Nginx forks worker processes routinely. **How are they forking gigabytes of memory without doubling their RAM footprint?**

Because `fork()` copies almost nothing.

## The "Stop Time" Moment

**Imagine this scenario:** A parent process holds 4 GB of mapped memory across thousands of pages. You call `fork()`. The kernel creates a child process with a brand-new virtual address space that looks *almost identical* to the parent's.

**Ask yourself: where does the physical memory live?**

Both processes — parent and child — have their own virtual memory mappings. But those mappings point to **the same physical pages**. The kernel did not copy a single byte of data. It copied the *page tables* — the lookup structure that translates virtual addresses to physical locations.

Two processes. One set of physical pages. Shared.

**What is being wasted if we copy eagerly?** Every byte of memory that the child *never modifies*. If the child reads 3.8 GB and writes to 200 MB, an eager copy wasted 3.8 GB of allocation, 3.8 GB of memory bandwidth, and the wall-clock time to copy it — all for pages that were already perfectly valid in physical RAM.

So the kernel makes a bet: *most of that memory will only be read, not written.* And it defers the cost of copying until proof arrives that copying is actually necessary.

That proof? A **page fault**.

## The Mental Model Shift

> **Stop thinking of fork as "copy the process." Start thinking of fork as "share everything, then pay per write."**

This is **Copy-on-Write** (CoW), and it reveals a deeper principle that applies far beyond operating systems: **the cheapest operation is the one you never perform.**

Here is what actually happens during `fork()`:

1. The kernel creates a new process descriptor and a new virtual memory address space for the child.
2. It copies the parent's **page table entries** — not the pages themselves. Both parent and child now have virtual addresses pointing to the same physical frames.
3. The kernel marks all shared pages as **read-only** in both processes' page tables. Even pages that were previously writable.
4. Both processes resume execution. As long as they only *read*, they share physical memory seamlessly. Zero duplication.

Now the child tries to write to a variable. It accesses a page that is mapped as read-only. The CPU raises a **page fault**.

But this is not the page fault you learned about in textbooks — where the page is absent from physical memory and must be loaded from disk. **The page is present.** The data is right there in RAM. The fault fires because the page is *protected*.

The kernel catches this fault and recognizes it as a CoW trigger:

1. **Copy the page** — allocate a new physical frame, duplicate the contents.
2. **Update the child's page table** — remap the child's virtual address to the new physical frame, now with write permissions.
3. **Perform the write** — the child's modification lands on its private copy.

The parent's mapping is untouched. Isolation preserved. Cost deferred until the exact moment it was unavoidable.

## The "What If" Scenarios

### Scenario 1: The Redis Snapshot Trap
Redis calls `fork()` to create a background child that writes the entire dataset to disk (RDB persistence). The dataset is 8 GB. Without CoW, forking would require 8 GB of free RAM — meaning you could only safely use 50% of your server's memory. **With CoW, the child shares the parent's pages and only copies the ones the parent modifies while the snapshot runs.** If the write rate is low during the snapshot window, the actual memory overhead is a tiny fraction of the dataset size. *But* — and here is the trap — if *write-heavy* traffic hits during the snapshot, every modified page triggers a CoW copy. Suddenly your 8 GB Redis instance needs 12 GB. The swapper kicks in. Latency spikes. *The cost was deferred, not eliminated.*

### Scenario 2: The Forked Worker That Never Diverges
A web server forks 16 worker processes. Each loads the same application code, the same shared libraries, the same read-only configuration. With eager copying, you would need 16x the code segment memory. **With CoW, all 16 workers share the same physical pages for code and read-only data forever.** The only pages that get copied are per-request heap allocations — a tiny working set. This is why pre-forking architectures scale: the memory cost per worker is not a full copy, it is *only the delta*.

### Scenario 3: The Invisible GC Tsunami
A garbage-collected runtime (Java, Go, Ruby) forks a child process. The GC walks the heap, touching every object to mark reachability. Each touch is a *write* (setting mark bits). Every page the GC walks triggers a CoW fault. **The GC — which modified zero application data — just caused the kernel to copy the entire heap.** The deferred cost arrived all at once, triggered not by business logic but by the runtime's internal bookkeeping. *Hint: this is why some runtimes are hostile to fork-based architectures.*

## The Architecture

Copy-on-Write is not a memory management trick. It is an instance of a universal systems design principle: **lazy evaluation of expensive operations, triggered by demand signals.**

The page fault is the demand signal. It is not an error — it is a **control flow mechanism** that the kernel uses to intercept access patterns and make deferred decisions:

| Page Fault Type | Page Present? | Cause | Kernel Action |
|---|---|---|---|
| Hard fault | No | Page on disk, not in RAM | Load from swap/file, map it |
| Soft fault | Yes (in cache) | Not yet mapped to this process | Map existing frame, no I/O |
| **CoW fault** | **Yes** | **Write to shared read-only page** | **Copy frame, remap, permit write** |

All three are page faults. The CPU does not distinguish between them. The kernel's fault handler inspects the page table entry and the VMA (Virtual Memory Area) metadata to determine *which kind* of fault occurred and what action to take.

**The profound implication:** the kernel is not copying memory. It is *intercepting writes* and making isolation decisions at the granularity of a single page (typically 4 KB). This means:

- Memory isolation between processes is not a property of `fork()`. It is a property of the **page fault handler**.
- The cost of isolation is proportional to the **write surface area**, not the total memory footprint.
- Any system that reads far more than it writes — which is *most* systems — gets near-zero-cost process duplication.

## The Question to Sit With

The next time you call `fork()`, or design a system that uses pre-forking, or run a Redis instance with background persistence — ask yourself:

**What is my write surface area?**

Because Copy-on-Write means your memory cost is not what you *have*. It is what you *change*. And the most expensive page fault is the one triggered by code you did not know was writing — a GC cycle, a logging buffer, a timestamp update on a shared structure.

The kernel deferred the cost. It did not delete it. **Lazy is not free. Lazy is a bet that most of the work will never be needed.** When that bet pays off, fork is magic. When it does not, you get a 2 AM page storm that no dashboard predicted.

---

*The cheapest copy is the one you never make. The most dangerous copy is the one you did not know you triggered.*
