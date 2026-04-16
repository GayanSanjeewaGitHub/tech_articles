# Pi Agent: The Fully Customizable Agentic Harness

> **Core idea:** Stop adapting to your AI agent — make the agent adapt to you.

---

- **Bare-bones by design, not by limitation.** Pi Agent ships with the smallest possible system prompt and only four default tools (bash, read, edit, write). Unlike Claude Code or Codex, which bake in opinionated workflows, sub-agents, MCPs, and permission guardrails you never asked for, Pi Agent starts empty so *you* decide what belongs in your workflow and what doesn't.

- **Extensions as the single customization primitive.** Every feature — to-do lists, sub-agents, memory, custom commands — is built through a lifecycle-hook extension system. Pi Agent fires events (session start, tool call, message sent), and you write small TypeScript modules that subscribe to those events. This means your agent's behavior is composed, not inherited from a vendor's defaults.

- **YOLO mode removes the interrupt tax.** Most coding agents constantly ask "Are you sure you want to modify this file?" — forcing you to babysit approvals across multiple instances. Pi Agent removes those guardrails by default, betting that monitoring output is cheaper than context-switching back to click "Enter" every five minutes. The trade-off is intentional: *you* own the responsibility.

- **No MCPs, no bloat, no lock-in.** Pi Agent deliberately excludes MCPs (Model Context Protocol integrations) from its core. The argument: as context windows scale to millions of tokens, most tool-routing overhead MCPs introduce becomes unnecessary weight. If you need one, install it as an extension — but the default is lean.

- **The real product is ownership of your workflow.** The deeper point isn't about a specific tool — it's that closed-source agents lock you into someone else's opinion of how coding should work (their system prompt, their UI, their bundled features). Pi Agent inverts this: you think about *how you actually work*, then build exactly that — nothing more, nothing less.
