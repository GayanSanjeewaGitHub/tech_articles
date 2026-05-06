# The Cache Miss You're Paying For Every Turn

### The scene

The monthly bill arrives and the input token cost is three times the estimate. The agent is working correctly — multi-turn conversations, tool calls, conversation history appended faithfully on every turn. The code is clean. Nothing is broken. And yet you're paying full price for tokens the model already processed last request.

### Why it hurts

Cached input tokens cost 90% less. That's not a rounding error — it's the difference between a viable unit economics and a product that's expensive at every scale. A 20% cache hit rate at full price costs the same as a 60% hit rate at discount. Miss the cache consistently across thousands of sessions and the bill compounds quietly, invisibly, correctly.

### What's actually happening underneath

Prefix caching works on exact byte matches from the start of the prompt. The model encodes the prefix once, stores the KV activations, and reuses them on the next call — if the prefix is identical. When you manage conversation history client-side, entropy creeps in. A whitespace character stripped by a frontend input handler. A message trimmed to fit a UI. An empty string appended mid-turn. Any mutation after the cache boundary is a full miss. **You broke the cache and the logs show nothing wrong.**

### The shift

Stop managing conversation history on the client when you don't have to. The server holding state means the server controls the byte sequence — no mutations, no accidental misses. Teams that switched to server-side state management saw 2–3x better cache hit rates without changing a single model call.

### The fix

With server-side state, each turn sends a `previous_interaction_id` instead of replaying the full history array. The server appends the new turn to the existing context, unmodified — same bytes, same prefix, cache hit. You keep the escape hatch: omit the ID and manage context yourself when you need surgical control over what the model sees. But the default should be server-held state. Let the infrastructure preserve the prefix. Reach in only when you have a specific reason to.

### The question to sit with

How many bytes of your prompt actually change between turns — and have you ever measured what that mutation costs you?
