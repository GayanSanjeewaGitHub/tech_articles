### The scene

Two teams build two different agents. Both need the same hotel API. Both end up writing their own glue code: call the endpoint, strip the XML noise, reshape the JSON, decide what's worth feeding the model. Same API, same cleanup logic, written twice — and a third team is about to write it a third time.

### Why it hurts

Every new agent, every new IDE, every new AI host that wants that same data pays the integration tax again. The wrapper code isn't hard, but it has to be correct, has to be maintained, has to handle edge cases — and now it's duplicated across N codebases that will drift out of sync the moment the API changes.

### What's actually happening underneath

An LLM can't consume a raw API response — it can't parse metadata-heavy JSON or XML without wasting tokens and attention on noise. So every integration needs a translation layer: fetch, clean, reshape, decide what's relevant. That layer has nothing to do with the agent's reasoning — it's pure plumbing. But because there was no standard shape for that plumbing, everyone kept rebuilding it inside their own agent instead of once, in one place.

### The shift

**Move the plumbing out of the agent and behind a fixed protocol, so any agent can plug into any data source without rewriting the adapter.** That's what MCP is — not a smarter agent framework, a standard socket.

### The fix

An MCP server holds the connection logic once — list available tools, execute a tool by name, return a clean result. Any MCP client, generic and reusable, talks to it the same way every time. The agent that used to embed five bespoke API wrappers now holds one client and points it at whichever server exposes the data it needs. Swap the client's endpoint, not its code.

### The question to sit with

How many times has your team rewritten the same "clean up the API response for the LLM" logic — and called it a different integration each time?
