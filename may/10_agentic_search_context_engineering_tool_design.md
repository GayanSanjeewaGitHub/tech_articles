# The Tool You Reach For

### The scene

The agent returned three sessions. None were about GDPA. One matched because an embedding model thought GDPA was close enough to Gemma. Another was about harness engineering. The agent didn't hesitate — it called the tool, got results, and answered with quiet confidence.

### Why it hurts

In production this looks fine until it doesn't. Users stop trusting the system. Support tickets say "it returned the wrong thing." Nobody files a ticket saying "semantic search failed on acronyms." They just stop using it. By then, the retrieval layer has become invisible — and invisibly broken.

### What's actually happening underneath

Vector embeddings cluster by semantic neighborhood. GDPA is a specific token — a regulatory framework with an exact name. The model tokenizes it into something that resembles Gemma. The embedding space doesn't care. It finds the nearest neighbor and returns it.

**Semantic search cannot find what it cannot understand semantically.** It's not a bug. It's the design.

The same tool that finds "sessions about regulatory constraints" by clustering synonyms will confidently return neighbors for any specific acronym, internal identifier, or exact-match query. The tool works. It's just answering a different question than the one you asked.

### The shift

**The search tool you reach for defines what's findable.** One semantic search tool is not a retrieval layer. It's a bet on what your users will ask — and that bet has sharp edges.

### The fix

Replace the fixed retrieval with a general-purpose query executor. Let the agent write the search query itself. Add an agent skill — a small markdown file with syntax rules — loaded only when the tool is called. The agent tried `%GDPA%` first. Got zero results. The error response came back as signal, not failure. It self-corrected to `*GDPA*`. Found the session.

No hard-coded fallback. No retry logic. Error as input.

### The question to sit with

What percentage of your users' real queries does your current retrieval tool actually handle correctly?
