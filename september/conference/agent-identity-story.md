### The scene

A developer wires up a new agent the fast way: reuse the user's existing login token. It already has access to everything the agent needs to touch, so why build a separate identity? Ship it, move on.

### Why it hurts

Now anything that can go wrong with that token — interception, a scope creep, an agent that decides on its own to call an endpoint nobody expected — inherits the full blast radius of a real user's session. Long-lived, full-privilege, no separate audit trail for "the agent did this" versus "the person did this." A security review can't even tell the two apart.

### What's actually happening underneath

Traditional software was scripted — a developer wrote every branch, so the code was never going to do more than what the identity behind it was already trusted to do. The user's token was a safe boundary because the code was predictable. An agent breaks that assumption: it decides its own steps, autonomously, task by task. It's not an extension of the user anymore — Karpathy's framing is closer: think of it as a new hire, not a script. And a new hire doesn't inherit the CEO's badge on day one just because it's convenient.

### The shift

**An agent needs its own identity, separate from the user who launched it — because unscripted execution means the old assumption "this code only does what I'd do" no longer holds.**

### The fix

Give agents short-lived, machine-scoped tokens by default — not the user's long-lived session. When a task genuinely requires the user's authority, elevate through an explicit on-behalf-of flow the user consents to at that moment, not a blanket credential handed over once. The agent keeps a dual persona: machine identity for its own actions, delegated identity only when it's acting for someone, and each is auditable separately.

### The question to sit with

If your agent went rogue for five minutes, would your logs show what the agent did — or would they just show what "you" did?
