### The scene

An agent gets asked "who's speaking about AI at the conference?" It calls the agenda API, gets back a list of AI sessions — each one holding a speaker ID, not a name. So it calls the speaker API next, tries to map each ID back to the right person, and answers.

### Why it hurts

Two API calls where one would do means two chances for the reasoning to go sideways. The agent might grab the wrong speaker for an ID, or skip the second call entirely and just report the IDs back to the user, useless as they are. Every extra round trip is also an extra LLM iteration — more latency, more tokens, more dollars, for a question that should've been instant.

### What's actually happening underneath

That two-step API shape isn't a bug — it's correct REST design for a deterministic caller. A human developer writes the join once, in code, and it's fast and cheap forever after. But an agent doesn't have code to write; it has to perform that join *live*, in its own reasoning, every single time the question comes up. What was a one-time engineering decision for a human integrator becomes a repeated, fallible act of inference for the agent — decomposition that's free for deterministic systems costs accuracy, latency, and money for a probabilistic one.

### The shift

**Whether an API is "well-designed" depends on who's calling it — an agent needs the join already done, not the pieces to assemble itself.** Reusing existing decomposed endpoints as agent tools quietly moves engineering work from your codebase into the model's fallible reasoning.

### The fix

Where a question always needs two pieces of data together — the session and the speaker it belongs to — wrap them into a single tool that returns both, resolved, in one call. Fewer iterations, no ID-mapping step to get wrong, lower cost, lower latency. Not every endpoint needs this — only the ones an agent will always need combined.

### The question to sit with

Are the "tools" you're handing your agent the same decomposed APIs you built for human developers — or ones actually shaped for how an agent has to use them?
