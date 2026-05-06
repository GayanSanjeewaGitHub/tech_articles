# The harness is the system

### The scene

The dashboard shows one task: fix a bug. The model has been running for 20 minutes. Token count: 13 million consumed, 50,000 generated. It's still looping. Nobody touched it. Nobody had to. This is the job now.

### Why it hurts

The bill isn't the main concern — yet. The agent is failing at subtasks it solved an hour ago. It's retracing steps, asking the same questions it already answered. Something critical is gone, and the loop doesn't know it. Every retry burns more tokens. The latency compounds.

### What's actually happening underneath

Context windows degrade. A 1 million token window sounds enormous until you're halfway through a debugging session and the model stops referencing the plan it wrote at the start. Models reliably lose information past roughly 50% utilization. One bad tool call dumped 20,000 lines of error output into the window. The context didn't just fill — **it degraded silently**. And the harness was compacting in the background, summarizing, deciding what survived. Nobody audited that decision. The logic lived on a remote server. You got the output. You never saw what it discarded.

### The shift

**The harness isn't scaffolding around your model. The harness is the system.**

Same model, two harnesses: 95% benchmark performance versus 42%. The model didn't change. The compaction policy, the loop structure, the memory strategy — that's what changed.

### The fix

Know exactly what your harness does, or write it yourself. Explicit compaction: summarize older turns, truncate tool output to 2,000 lines, not 20,000. Add a plan file the agent writes to and checks at every loop iteration — a markdown it can refer back to instead of reconstructing context from scratch. Build hypothesis-then-verify into the loop so learning accumulates across iterations rather than evaporating. Validate every skill file against your current model — instructions that helped three months ago may now add tokens and reduce performance.

### The question to sit with

When your context fills and your harness compacts — do you know what it decided your agent should forget?
