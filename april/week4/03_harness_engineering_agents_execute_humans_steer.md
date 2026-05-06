# Harness Engineering: The Discipline of Building Systems Where Humans Steer and Agents Execute

## The Trap

Most teams adopt coding agents the way they adopted autocomplete — faster typing, same workflow. They paste a ticket into a chat window, review the diff line by line, fix the mistakes by hand, and call it "AI-assisted development."

This is not delegation. This is supervision with extra steps.

The deeper trap is subtler: we still treat **implementation as the scarce resource.** We stack-rank priorities because human hands are limited. We defer P3 work indefinitely. We leave migrations half-finished for months because the last 20% isn't worth the engineer-hours. The entire machinery of how we plan, schedule, and review software is built on the assumption that producing code is expensive.

**What happens to your entire operating model when code becomes free?**

## The Stop-and-Think Moment

Consider what you actually do in a day. Not what you think you do — what you *actually* do.

- How much time is spent writing code versus waiting for CI, waiting for review, or re-explaining the same non-functional requirement to a different teammate?
- How many of your P3 tickets exist not because they're unimportant, but because you can't justify the human cost?
- **Every time you type "continue" to an agent, what context failure does that represent?**
- **Every piece of code review feedback you give more than once — why isn't that already a lint rule?**

Here's the uncomfortable realization: the bottleneck was never the code. It was always the system around the code — the instructions, the guardrails, the feedback loops, the definition of "done." You've been optimizing the wrong layer.

## The Mental Model Shift

> **Stop thinking of yourself as an implementer who uses agents. Start thinking of yourself as a systems architect who programs the environment in which agents operate.**

Your job is no longer to write code. Your job is to make the *definition of acceptable code* so legible, so structurally embedded, that an agent can converge on it without you watching. Every skill file, every custom lint rule, every review agent, every test that asserts source structure — these aren't developer experience niceties. They are **the actual product of your engineering effort.**

The code is a build artifact. The harness is the source.

## The What-If Scenarios

**Scenario 1: The Merge Conflict Death Spiral.**
Three engineers each produce three to five PRs per day. PRs are large. They touch overlapping files. Merge conflicts multiply. PRs stay open because they need human review. The longer they stay open, the more conflicts accumulate. The bottleneck isn't the agent writing code — it's the human blocking the merge. The fix isn't faster review; it's eliminating the *need* for human review by encoding what "acceptable" means into the repository itself.

**Scenario 2: The Slop Accumulation Problem.**
An agent writes network code without retries or timeouts. You catch it in review, fix it, merge, move on. Next week, a different agent does the same thing. You are now a human lint rule — synchronous, non-durable, and unreliable. The architectural failure is that your knowledge about non-functional requirements lives in your head instead of in a test, a lint, or a reviewer agent that fires on every push.

**Scenario 3: The Context Evaporation Problem.**
Your agent starts a long task. Midway through, auto-compaction pages out the instructions you gave it at the start. It finishes the work, but the output violates constraints it no longer remembers. Frontloading all instructions doesn't work — you overwhelm the context window early. The solution is **just-in-time context injection**: surface the right constraint at the right phase. Let the agent prototype freely, then use tests and review agents to re-inject the guardrails at the moment they matter.

## The Architecture: What a Well-Engineered Harness Actually Looks Like

A good harness is not a wrapper around an agent. It is an **environment that makes the tokens the agent must produce easy to predict.**

- **Structural uniformity as prompt engineering.** One way to write a bounded concurrency helper. One ORM. One way to add lint rules. One programming language. The more identical the codebase looks across packages, the more transferable context the agent builds — and the fewer tokens it wastes on local adaptation. Code in the filesystem is text. Text is prompt. Make the prompt consistent.
- **Progressive guard rails, not upfront instruction dumps.** Skills and docs are surfaced at the phase they matter. A React component decomposition rule fires at lint time, not at task kickoff. The agent prototypes first, then refines against constraints. This respects the scarcity of the context window.
- **Source-level structural tests.** Not just behavior tests — tests that assert files stay under 350 lines, that Zod schemas aren't duplicated across packages, that dependency edges between layers are valid. These are **codebase-as-prompt optimizations** that keep the agent operating within a context-efficient structure.
- **Reviewer agents as durable knowledge.** Instead of one engineer's expertise living in their head and leaking out during synchronous code review, that expertise is written into a persona document. A reviewer agent — security, reliability, front-end architecture — runs on every push, evaluating the diff against those docs. The human's knowledge becomes asynchronous, parallelizable, and permanent.
- **Garbage collection as a discipline.** One day per week, every engineer takes the slop observed during the week and categorically eliminates it — not by fixing individual instances, but by adding the lint rule, the test, or the doc that prevents the entire class of failure from recurring. This is the feedback loop that makes the harness self-improving.

The end state is not "agents write code and humans review it." The end state is: **humans define what acceptable code looks like, and the environment enforces it without human presence.**

## Intuitive Summary

- **Code is now free to produce, refactor, and delete** — the scarce resources are human attention, model context window, and the *definition of what "good" means*, not implementation capacity.
- **Every recurring code review comment is a harness failure** — if you've given the same feedback twice, it should already be a lint rule, a test, or a reviewer agent that fires automatically.
- **The codebase itself is a prompt to your agent** — structural uniformity (one pattern, one language, one way to do things) makes the agent's output more predictable and reduces wasted tokens on local adaptation.
- **Just-in-time context beats upfront instruction loading** — surface constraints at the phase they matter (lint time, test time, review time) instead of overwhelming the agent's context window at task start.
- **Your engineering output is no longer code — it's the harness** — skills, structural tests, reviewer agents, and docs that encode what "acceptable" means are the durable artifacts; the code they produce is a disposable build artifact.

## The Question to Sit With

If every piece of review feedback you give more than once is a failure of your environment rather than a failure of the agent — **how much of what you call "engineering" today is actually just repeated, undocumented, synchronous human labor that should have been compiled into your harness months ago?**
