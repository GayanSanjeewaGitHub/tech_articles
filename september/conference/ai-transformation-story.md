### The scene

A travel booking platform wants an AI assistant. Someone in the room says "let's build an agent" before anyone has described the problem. That instinct — agent first, question later — is exactly the trap.

### Why it hurts

Agents are autonomous, expensive to get right, and hard to roll back once customers depend on them. Reach for one by default and you inherit its failure modes everywhere: unpredictable tool calls, unclear authorization boundaries, and a system nobody can fully reason about — for a problem that maybe just needed a prompt.

### What's actually happening underneath

The platform actually had three distinct problems wearing one costume. Turning raw booking history and reviews into a personalization profile is a one-shot transformation — data in, structured summary out, no decisions to make. Answering "does this hotel allow pets?" is a lookup against hotel-specific documents — a retrieval problem, not a reasoning problem. Only planning a multi-day trip and executing a real booking requires something that listens, decides, and calls live APIs autonomously. Three different shapes, three different tools.

### The shift

**Match the pattern to the task before writing a line of code: a plain generative call for transformation, retrieval for grounded lookup, and an agent only for autonomous multi-step action.** Picking the heaviest pattern by default is the expensive mistake, not the safe one.

### The fix

The personalization step became a single LLM call over aggregated API data — no agent, no memory needed. Hotel-specific questions became a RAG pipeline scoped by hotel ID metadata, so one hotel's policy never leaks into another's answer. Only the trip planner — the part that decides, checks availability, and books — became an agent, sitting on top of the other two as tools it can call. The existing booking APIs never changed.

### The question to sit with

Before your next AI feature, which of your three problems are you actually solving — and does it really need an agent?
