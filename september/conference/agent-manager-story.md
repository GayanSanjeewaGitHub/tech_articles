### The scene

A customer support agent answers a cancellation request. Clean. Confident. Correct-looking. You open the trace and count 32 spans for one message. The agent guessed an order ID, the tool call failed, it silently re-fetched all orders, guessed again, and finally got it right. The user never saw the stumble. You almost shipped it without ever knowing.

### Why it hurts

Multiply that by five teams, five frameworks, one guardrail written in code here, another bolted onto a gateway there. No shared view of cost, no shared view of what an agent is allowed to touch. Incidents start showing up in public databases. Nobody can answer "what are our agents doing right now" with a straight face.

### What's actually happening underneath

The agent looked fine because "it answered correctly" was the only signal anyone was checking. Correctness hides retries, wrong tool calls, silent recoveries — the actual risk surface. And every team solving this alone means governance, identity, and observability get reinvented five different fragmented ways instead of once, properly.

### The shift

**An agent isn't a deployment, it's a blueprint plus an instance.** Separate the harness — the code, the trust boundary, the instrumentation — from the configuration a non-developer fills in to spin up their own copy. That's the "agent kind": one source, many governed instances.

### The fix

A control plane sits underneath every agent, platform-hosted or external, and does three things automatically: zero-code OpenTelemetry tracing (so every span is captured without touching agent code), built-in evaluators that score traces on a schedule instead of a human reading logs, and guardrails enforced at the platform layer, not scattered across codebases.

### The question to sit with

If you opened the full trace of your last "successful" agent response right now, would it still look successful?
