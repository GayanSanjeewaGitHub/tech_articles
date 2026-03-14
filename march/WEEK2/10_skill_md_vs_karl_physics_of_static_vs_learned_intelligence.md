# The Physics of Static vs. Learned Intelligence: Skill Files, Reinforcement Learning, and the Weight of Knowledge

## The Trap: Longer Instructions = Smarter Agents

We think building a capable AI agent means writing better instructions. More bullet points. More guardrails. More edge-case corrections appended to a markdown file at 2 AM after the agent hallucinated a chart title for the third time.

This is the **Skill MD paradigm** — a reusable markdown file that packages instructions, tool definitions, search strategies, script invocations, and failure handling into a static cognitive scaffold. Three layers: a metadata layer (routing), a workflow instruction layer (reasoning logic executed by the LLM), and a runtime execution layer (deterministic scripts in Python, C++, whatever). Elegant in theory.

In practice? One production-grade financial analysis skill file runs to *hundreds* of lines. Not because the task is complex — but because every single hallucination the agent ever committed had to be patched with another explicit instruction: *"Use exactly that slide title, not a paraphrase." "Do not substitute creative alternatives." "When in doubt, reread the prompt — it's a requirement."*

**Ask yourself: If your agent needs a 500-line instruction manual to avoid calling a section "Financial Year 2024 Segment Contribution Analysis" instead of "Overview and Competitive Scope" — what exactly did the pre-training buy you?**

## The Stop-Time Moment

Imagine this scenario. You have 10,000 internal documents — supplier delay logs, revenue reports, contract agreements. You need the agent to find a bottleneck you *don't even know exists*. No human has pre-defined the search path. No skill file can anticipate which queries to construct, which documents cross-reference, which numbers to compare.

**What is being wasted here?**

Every token the model spends *reading your instruction file* is a token not spent *reasoning about your data*. The skill MD doesn't teach the model anything — it *constrains* it. The model's weights remain unchanged. The intelligence is cosplaying as intelligence: it's an autoregressive system slavishly following concatenated human instructions until it collapses under their weight.

The skill file is a *prosthetic brain*, not a trained one.

## The Mental Model Shift

> **Stop writing longer prompts. Start training shorter weights.**

The distinction is architectural, not cosmetic:

- **Skill MD** = runtime guidance. Intelligence lives in the *file system*. The model is a generic executor. Knowledge is *loaded*, not *learned*.
- **KARL** (Knowledge Agents via Reinforcement Learning) = trained search behavior. Intelligence lives in the *tensor weights*. The model is a specialist. Knowledge is *baked*, not *appended*.

Here's how KARL inverts the paradigm:

1. **Synthetic curriculum generation** — An AI reads your document corpus, *invents* questions, and another AI attempts to answer them by *actually searching* the documents through trial and error.
2. **Trajectory storage** — Every search attempt (query → open reports → extract numbers → compare → answer) is stored as a step-by-step training trajectory. Run it 10,000 times. Now you have a dataset of *search behavior*, not search instructions.
3. **Reinforcement learning** — Filter the best trajectories (pass-rate filtering for clarity, logic, correctness), then train the model's weights using a custom policy optimization (OAPO — Optimal Advantage-based Policy Optimization with Lagged Inference Policy). The search strategy is now *encoded in the transformer weights*.
4. **Test-time compute amplification** — At inference, spawn 10–50 parallel reasoning rollouts, aggregate via an evaluator agent. Cost stays low. Performance climbs.

The result? Competitive with frontier models at a fraction of the cost and latency — using only a *single tool* (vector search).

## The "What If" Scenarios

**What if your domain shifts?** A skill file breaks immediately — every hardcoded query template, every predefined phase, every "correct formulation" becomes irrelevant. KARL's RL-trained weights generalize: out-of-distribution performance exceeds distilled models because the model learned the *strategy*, not the *answers*.

**What if you distill the knowledge?** KARL's intelligence transfers. A small model (GLM 4.5 Air) jumps from ~55% to 70% accuracy through supervised fine-tuning on KARL's trajectories. The skill file's knowledge? It transfers by *copy-pasting more markdown*. One is compression. The other is accumulation.

**What if you add more tools?** KARL achieved its benchmarks with a *single* vector search tool. Imagine structured retrieval, code execution, sub-agents as callable tools. The action space explodes — and RL scales with action space. The skill file? Every new tool means another section of "tool usage rules" manually authored by exhausted engineers.

## The Architecture

The physics here is thermodynamic. A skill file is *potential energy that never converts* — it sits in the file system, consumed at inference time, occupying context window, adding latency, contributing zero gradient updates. KARL is *kinetic energy* — the search behavior has been converted into weight updates through the work of reinforcement learning.

The hierarchy becomes clear:

| Dimension | Skill MD | KARL |
|---|---|---|
| Knowledge location | File system (context window) | Tensor weights |
| Learning | None — appends corrections | RL on search trajectories |
| Scaling law | More lines → more fragility | More training → more generalization |
| Failure mode | Silent instruction drift | Measurable reward degradation |
| Transfer | Copy-paste | Distillation |

**The deeper question:** Every line in your skill file is a confession — a place where pre-training failed and a human had to intervene with duct tape. KARL asks: *what if we trained the model to never need that line in the first place?*

The skill file is where intelligence goes to be *described*. Reinforcement learning is where intelligence goes to be *acquired*.

---

**Thinking Shifts:**

- A 500-line skill file isn't a sign of thoroughness — it's a *measurement of pre-training failure*
- Static instructions scale linearly (more edge cases = more lines); learned behavior scales logarithmically (more training = diminishing corrections)
- The context window is not free storage — every instruction token displaces a reasoning token
- Distillation proves intelligence is *compressible*; skill files prove instructions are *not*
- The future agent doesn't load its playbook — it *is* the playbook
