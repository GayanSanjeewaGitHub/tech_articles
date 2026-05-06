# The Loop Nobody Draws on the Architecture Diagram

### The scene

You inherit an "agent" built on a popular orchestration framework. Chains, retrievers, state machines, memory connectors — the diagram is beautiful. But the agent can't finish a task without someone nudging it between steps. Every tool call stalls, waiting for human interpretation. It is not autonomous. It never was.

### Why it hurts

You've built a cockpit with no autopilot. The framework handed you LEGO bricks and assumed you'd wire them into something that runs. You did. But "running" and "autonomous" are not the same thing. Your team is the loop. They decide what comes next. The model is just a very expensive autocomplete inside a scaffolding that was designed for a human architect, not an agent.

### What's actually happening underneath

Frameworks — chains, state graphs, retrieval pipelines — are built for humans to assemble agents. A harness is the opposite direction entirely. No assembly step. It ships a working agent. At its core, **a harness is a while loop with a tool registry and a permission layer**. The model reads the system prompt, picks a tool, runs it, gets the result back in context, and loops again — until it produces a text-only response or hits an iteration cap. Everything else exists to support that loop: context compaction when the window fills, append-only session logs so a crash loses nothing, lifecycle hooks so you can intercept tool calls without touching the core.

### The shift

A framework is built for a human to assemble an agent. A harness is built for the agent to run a task. That distinction sounds semantic. It isn't. When you hand a framework to an agent, it breaks at every gap you forgot to wire. When you hand a harness a goal, it finishes.

### The fix

A minimal harness needs: an iteration loop with a max-cap, a tool registry (name, permission level, handler), context compaction before the window overflows, and a permission hierarchy — read, workspace, full — enforced at dispatch time before any tool runs. Session state written to disk on every event means a crash mid-task costs nothing. Lifecycle hooks let you audit or deny tool calls without forking the core. You don't need all of this on day one. But without the loop, the registry, and the permission layer, you don't have a harness. You have a chatbot with a business card that says "agent."

### The question to sit with

If your agent can't finish a task without you approving each step — who is actually the agent?
