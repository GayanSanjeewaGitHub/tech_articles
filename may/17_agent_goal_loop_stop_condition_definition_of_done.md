# The Agent That Quit Too Early

### The scene

You asked the agent to fix all failing tests. It ran for 12 minutes, came back confident: "All issues resolved." You ran the suite. Fourteen tests still red. You nudged it. It ran again. Came back confident again. This loop — you nudging, it declaring premature victory — is not a bug. It's the default.

### Why it hurts

On a simple ticket, you catch it fast. On a 6-hour migration — JavaScript to TypeScript, 200 files, visual regression tests — you don't find out until morning. The agent stopped at 40%. It looked done to itself. Nobody told it what done actually meant.

### What's actually happening underneath

Early agentic loops used a dumb programmatic exit: run N iterations, stop. That's not a completion check — it's a timeout. The agent hits the cap and reports success regardless of state. Replacing the cap with "keep going until finished" doesn't help either. Without a grounded definition of done, the model pattern-matches against its own prior output, sees effort, and infers completion. **Effort is not a stop condition.**

### The shift

**The definition of done has to be written before the first step, not discovered at the last.** An LLM-judged loop is the right primitive — a separate model call evaluates the artifact against the stated objective after each round. But that evaluator is only as good as the spec you give it. Fuzzy goals produce fuzzy exits.

### The fix

Write the goal prompt like a contract: what to achieve, what not to touch, how to validate progress, and when to stop — with a measurable signal. For a migration: "All screens visually match reference screenshots under Playwright. Zero TypeScript errors. Stop when both conditions hold." The agent now has an oracle, not an opinion. Run it overnight. Check the oracle output, not the agent's summary.

### The question to sit with

In your current agent workflows, who defines done — you, or the model that just finished the work?
