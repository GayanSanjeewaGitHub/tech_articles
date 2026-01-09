# Parallel Agents for Massive Refactors: The Real Skill Isn’t “Using AI” — It’s Designing Work

It’s easy to hear “parallel agents can refactor whole codebases” and treat it like another productivity trick. But the deeper lesson in this talk is not a tool lesson. It’s a *work design* lesson.

So instead of asking, “How do I run multiple agents?” ask:

**What kinds of software work become possible when you can delegate repeatable engineering labor to a fleet of sand-boxed workers—and what new failure modes does that create?**

## 1) The shift: from writing code to managing work
The speaker describes a progression: code snippets → context-aware autocomplete → autonomous agents → orchestration (agents coordinating agents).

Think:
- If almost every line of code can be produced by an agent, what becomes your core job: typing, or choosing what should exist?
- What if “being productive” stops meaning “how fast I code” and starts meaning “how well I design tasks that can be verified”?
- Are you ready for the psychological jump: from individual contributor to manager—except your “team” is non-human and nondeterministic?

## 2) Why orchestration exists: the limits of a single agent
Large refactors fail for familiar reasons: limited context windows, compounding errors, missing domain intuition, and the “laziness”/early-stopping behavior.

Ask:
- When an agent fails, is the problem model capability—or the way the work was packaged?
- What if the biggest risk isn’t a wrong answer, but a small wrong assumption repeated across 200 files?
- If you can’t clearly define “done,” are you asking for engineering—or asking for a guess?

## 3) The orchestration loop: decomposition, parallelism, verification
The key workflow is simple to say, hard to execute: break a big change into “one-shot” tasks, run agents in parallel, and merge results with human review.

Pressure-test it:
- Can this task fit in a single commit/PR with a clear success signal?
- Can you verify correctness cheaply (tests, lint, CI), or will you need deep manual review?
- If you run 5 agents at once, can your brain review 5 streams of changes without collapsing? What’s your real concurrency limit?

## 4) Choosing a decomposition strategy is the real architecture
Three strategies show up:
- Piece-by-piece (files/directories/components)
- Dependency-ordered (leaf nodes first)
- Scaffolding (support both “old world” and “new world” during migration)

Questions:
- What if the “best” decomposition isn’t the smallest chunks, but the chunks that minimize cross-team merge conflicts?
- When should you add scaffolding even if it’s ugly—because it buys you continuous verification?
- If your dependency graph is tangled, is the refactor problem actually a design debt problem?

## 5) Context sharing: coordination without drowning
Sharing everything across agents kills context budgets. Sharing nothing repeats mistakes. The talk explores human-pasted notes, shared files (like an `agents.md`), and agent-to-agent messaging.

Ask:
- What knowledge should be global (conventions, versions, migration rules) versus local (file-specific fixes)?
- What if agents start writing “helpful” but wrong guidance into shared context—who curates truth?
- If agents talk directly, do you get faster convergence—or do you get new chaos?

## The point
You don’t learn this to “use OpenHands.” You learn it to build a new skill: **designing refactors as a sequence of verifiable, parallelizable decisions.**

The question to practice after any demo is: *If I had to make this safe for production, what would I measure, what would I review, and where would I refuse automation?*
