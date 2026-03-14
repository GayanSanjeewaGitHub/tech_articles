# The Physics of Compaction: Why Coding Agents Fail Long Before the Model Does

## The Trap

We think coding agents fail because the models are not smart enough.

That explanation is comforting because it places the problem somewhere far away, inside the model vendor, the benchmark chart, or the next release. If the agent produces churn, rewrites working code, bloats the diff, or gets lost in a brownfield codebase, we tell ourselves the intelligence simply is not there yet.

But that is only part of the story, and often not the important part.

Many teams are discovering the same pattern: AI looks impressive in greenfield demos, then becomes expensive and erratic in real systems. It ships faster, but the throughput is polluted by rework. You produce code, then produce more code to clean up the previous code, then spend human time trying to restore coherence. The output goes up while net progress becomes ambiguous.

This is the trap. We think the bottleneck is model intelligence when the real bottleneck is often context quality.

An agent does not operate on the codebase directly. It operates on a compressed narrative of the codebase inside its context window. If that narrative is noisy, incomplete, stale, or too large, the agent is not reasoning over reality. It is reasoning over a distorted memory of reality.

## The Stop-Time Moment

**Imagine this scenario:** you ask a coding agent to implement a medium-sized feature in a ten-year-old codebase. It searches files, reads unrelated modules, pulls in build logs, absorbs tool output, consumes test failures, gets corrected three times, and keeps going.

Now pause.

**Ask yourself: What is being wasted here?**

Is the waste happening in token cost alone? Or is the deeper waste the gradual degradation of decision quality as the context window fills with stale branches, half-correct assumptions, and the residue of failed attempts?

**Ask yourself: Where does the state live?**

Does the real understanding of the task live in the codebase itself? In the human's head? In the ticket? In the agent's rolling conversation history? If those four are not aligned, which one wins?

This is the uncomfortable truth most teams miss: once the active context gets bloated enough, the model stops acting like a careful engineer and starts acting like a tired intern trying to remember an argument from three meetings ago.

Hints for the reader:

- Wrong context is worse than missing context.
- Large context is not the same as useful context.
- Repeated correction can poison trajectory instead of improving it.

## The Mental Model Shift

> **Stop thinking of context as memory. Start thinking of context as working memory under severe pressure.**

That distinction changes everything.

A coding agent is not a persistent software engineer with durable understanding. It is a stateless reasoner repeatedly making its next move based only on what remains inside the active window. Every unnecessary search result, giant JSON blob, verbose test log, and circular correction competes with the actual problem for scarce cognitive space.

This is why compaction matters. Compaction is not a convenience trick. It is the act of converting sprawling conversational residue into a smaller, truer representation of the task. You preserve the files that matter, the exact constraints, the relevant observations, the intended trajectory, and the validation path. Everything else is entropy.

**Thinking Shifts:**

- Old model: keep the conversation going until the task is done. New model: reset aggressively and preserve only what is true and useful.
- Old model: subagents are roleplay for fake employees. New model: subagents are isolation boundaries for context.
- Old model: more history means more intelligence. New model: more history often means more contamination.
- Old model: planning is bureaucracy. New model: planning is compression of intent.

## The What-If Scenarios

### Scenario 1: The Agent That Learns the Wrong Pattern

What if every few turns you tell the model it is wrong, then let it continue in the same conversation? The agent is no longer just learning the task. It is learning the trajectory of failure. It sees a conversation full of bad attempts and reprimands, then predicts from that sequence. This is why a long session can feel cursed. You are not refining the system; you are steeping it in its own mistakes.

### Scenario 2: The Giant Codebase That Looks Smaller Than It Is

What if a monorepo contains millions of lines, but the agent starts by ingesting broad onboarding context, multiple tool traces, and irrelevant repository knowledge? You have spent the smartest part of the context window learning things that are technically true but locally useless. This is like filling your backpack with the entire library before a one-hour exam.

### Scenario 3: The Team That Ships Faster but Understands Less

What if AI doubles output, but reviewers only see walls of generated code with no distilled reasoning, no explicit plan, and no evidence trail? The technical problem is no longer code generation. It is mental alignment. Teams fall apart when the system evolves faster than humans can retain a shared model of why it changed.

## The Architecture

The answer is to build the workflow around context discipline.

Start with research. Not vague exploration, but scoped investigation. Find the relevant files, trace the exact code paths, and compress only the parts of the system that are actually true for the task at hand.

Then plan. A good plan is not management theater. It is executable intent compressed into a form that both humans and models can validate. It should contain the affected files, the expected modifications, and the verification path. If the plan is weak, implementation becomes high-speed drift.

Then implement in short, controlled contexts. Use subagents not as anthropomorphic specialists, but as disposable context containers. Let one isolated process search widely and return only the essential result. Compact often. Reset before the window turns dumb. Treat onboarding context as progressive disclosure, not a giant front-loaded document dump.

Most importantly, keep the human focused on the highest-leverage checkpoints: validating the research, reviewing the plan, and correcting misunderstandings before they expand into code. A bad line of code is cheap. A bad plan can manufacture hundreds of bad lines with perfect confidence.

This is the larger lesson. Context engineering is not prompt decoration. It is operational control over how truth, intent, and working memory are compressed for a stateless system.

The question to sit with is not whether today's models are smart enough to code.

The real question is **whether your workflow preserves enough clean, high-signal context for that intelligence to remain useful under real-world complexity**.

Because once you understand that, coding-agent performance stops looking like a pure model problem and starts looking like what it really is: a systems design problem about memory, trajectory, and human alignment.