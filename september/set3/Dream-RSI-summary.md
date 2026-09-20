# Dream-RSI: The Agent That Practices in Its Dreams

*A story-style summary of Google's "Dream-RSI: Recursive Self-Improvement through Evolving Worlds"*

## The Problem: Learning Is Expensive When Every Lesson Costs Money

Imagine a coding agent whose job is to discover a faster GPU kernel, or a better Lasso solver, or a denser circle-packing. It doesn't just write one solution — it runs a **discovery loop**: propose an idea, evaluate it, learn from the result, propose the next idea. Do this hundreds or thousands of times and you get real scientific discovery.

But *how* the agent explores — which branches to chase, how many to run in parallel, when to give up on a dead end — is itself a decision, made by an "exploration policy." And that policy is usually hand-written once and never improved. Why? Because to test whether a *new* exploration strategy is better, you'd have to actually run it — a full, expensive, hours-long discovery session. Testing 50 candidate strategies means 50 expensive online experiments. That's the bottleneck.

## The Insight: You Already Have a World Model — It's Called History

Here's the trick Dream-RSI is built on: **every past discovery run is already a recording of "what happens if you explore this way."**

Think of it like a video game speedrunner who has already played through a level once, recording every route, every death, every treasure found. A second runner doesn't need to replay the level for real to test a new route through the *same* level — they can just rewind the tape and walk a different path through what was already recorded, as long as they don't need to explore anywhere not already filmed.

That recorded tape is called a **discovery tree**: every attempt (node) knows its parent, its score, and its outcome. Because the outcomes are already sitting there, a totally different exploration policy — pick different branches, batch them differently, stop earlier or later — can be tried against that same tree for free. No re-running the coding agent, no re-evaluating candidates. This is called **"dreaming"**: the agent imagines thousands of alternative strategies against a replay simulator built from real history, instead of testing them for real.

## How Dream-RSI Actually Works (Three Steps, on Repeat)

1. **① Online Explore** — The current exploration policy drives a real (expensive) discovery run. A coding agent proposes solutions, an evaluator scores them, and everything gets logged into a discovery tree.
2. **② Construct Replay Simulator** — That discovery tree, plus every tree from every past round, becomes a pool of "worlds" the agent can replay against — cheaply, instantly, with zero real computation.
3. **③ Dreaming-based Policy Improvement** — A policy-development agent proposes many candidate exploration policies and tests each one by replaying it through the simulator pool. It sees which policy would have found the best score, fastest, with the least wasted computation — all without spending a single real API call. The winning policy gets promoted.

Then the loop repeats: the improved policy goes back online for a real round of exploration, which produces a new (bigger, richer) discovery tree, which feeds back into the simulator pool for the next round of dreaming. Each cycle, the "world" the agent can dream in gets larger and more informative — hence "Evolving Worlds."

## The Analogy That Makes It Click

It's the same idea as DeepMind's **Dreamer** agents in reinforcement learning: an agent learns a compact model of its environment from real experience, then improves its behavior by imagining rollouts inside that learned model rather than acting in the real world every time. Dream-RSI applies the same principle **one level up** — not to physical actions, but to *meta-level* exploration strategy. The "environment" being modeled isn't a maze or an Atari game; it's the shape of the search space itself, as recorded in the discovery tree.

## Why It Matters: The Numbers

Across three very different domains — algorithm engineering (Lasso solvers), math optimization (circle packing, autocorrelation inequalities), and GPU kernel engineering (VGG16, LayerNorm) — Dream-RSI matched or beat strong baselines while using **dramatically fewer expensive real-world evaluations**: up to 162× fewer agent calls than one baseline, and 1.7–2.4× fewer than a fixed-policy baseline, in some settings reaching the same performance with half the generations or better performance at the same budget.

The one key design choice that mattered: giving the agent the *full replay simulator* — letting it interactively navigate history and see consequences — beat simply *summarizing* history into text guidance injected into the prompt. Being able to "walk through" what happened, branch by branch, taught the policy far more than being told about it in prose.

## Short Take: How to Use This in Real-World Agentic Applications

The pattern generalizes far beyond scientific discovery. Anywhere you run an **agentic loop with expensive, delayed feedback** — a coding agent doing multi-step refactors, an AI SRE triaging incidents, a research agent doing multi-hop web search — you can apply the same trick:

- **Log every attempt as a tree**, not just a flat chat transcript: what was tried, what it cost, what happened.
- **Treat that tree as a cheap simulator** for testing alternative orchestration strategies (which sub-agent to call next, how much to parallelize, when to stop) — instead of re-running the real (costly) agent every time you want to tune the orchestrator.
- **Periodically "dream"**: let a policy-improvement agent try many orchestration variants against replayed history, pick the best, and redeploy it — closing a self-improving loop on the *meta*-layer (how the agent explores) rather than only the object layer (what the agent produces).

In short: don't just log agent runs for debugging — turn that log into a replayable world your orchestration logic can practice against, for free, before you spend real money testing it live.

---

## Q&A Deep Dive (for later reference)

### Q1: If I'm at step 6 and fail, but a new idea shares steps 1–4 with an existing branch, can I fork from step 4? Or if a main branch fails, should I just prune its sub-branches?

Both are valid moves — but they are **object-level exploration decisions**, not something dreaming itself invents.

- **Forking from a shared prefix (step 4)** and **pruning a dead branch** are both real actions an exploration policy can take. They require actually running something new (a fresh generation-evaluation), so they happen during **online exploration** — real agent calls, real cost.
- **Dreaming cannot invent your new step-5 idea.** Replay only reveals outcomes that were *already recorded*. For any node `v`, `Child(v)` deterministically returns "v's unique recorded child, if one exists." So during replay you can choose which recorded branches to reveal, in what order, how to batch them, and when to stop/prune — but you cannot get feedback on a branch that was never actually tried in any historical tree. There is no recorded score for an idea nobody ran.

**What dreaming *is* for:** not "should I branch at step 4 this one time," but "what *general rule* for branching/pruning/batching performs best on average, across all the trees I've collected so far?" A candidate rule like *"if main branch fails, don't bother with its sub-branches"* is exactly the kind of policy dreaming tests — cheaply, by replaying that rule against every historical tree and comparing its average score (quality − execution cost + parallelism bonus, per the paper's Eq. 1) against alternative rules (e.g., "keep exploring one level deeper since recoveries sometimes happen").

| | Object-level (fork/prune, right now) | Meta-level (dreaming) |
|---|---|---|
| Decides | "fork here", "prune that branch" | "in general, fork at shared prefixes / prune after N failures — or not" |
| Tested against | reality (costs money) | replayed history (free) |
| Can discover brand-new ideas? | Yes | No — only reshuffles known outcomes |
| Output | one exploration trace | an improved *policy* that will make many such calls online later |

### Q2: Is the exploration policy hardcoded? And this "metadata" that grows over time — is that like RAM/context?

No to both, with an important correction on the second part:

- **The exploration policy is not hardcoded.** It's literal source code — a small program deciding "which node to pick, how big a batch, when to stop." A separate fixed LLM (the *policy-development agent*) reads dreaming/replay feedback and **rewrites this code** each round, the way you'd edit a script based on test results. It is not fine-tuned into any model's weights.
- **The history is not ephemeral RAM/context** — it's a **persistent, cumulative store** of past discovery trees:
  ```
  H_0 = ()
  H_1 = H_0 ∪ {tree from round 1}
  H_2 = H_1 ∪ {tree from round 2}
  ...
  ```
  This growing store is exactly the "**Evolving Worlds**" in the title — the simulator pool a policy can dream against gets bigger and richer every round, and needs to persist across many outer iterations, not just survive one session.

Three moving parts, three different lifespans:
- **Model weights** (coding agent, evaluator, policy-development agent) — fixed forever.
- **Exploration-policy code** — rewritten every outer round, based on dreaming.
- **Discovery-tree history** — append-only, grows every outer round, makes dreaming increasingly informed over time.

### Q3: What are the main "agents" in this system? Is the simulator an agent too?

| Role | What it does | Changes over time? |
|---|---|---|
| **Discovery agent** (coding agent) | The LLM that generates candidate solutions during real online exploration | Fixed |
| **Evaluator** | Scores each candidate (runtime, correctness, objective value) | Fixed |
| **Policy-development agent** | The LLM that reads dreaming/replay feedback and rewrites the exploration-policy's code | Fixed |
| **Exploration policy** | Executable code deciding which branch to expand, batch size, when to stop | **This one evolves**, round over round |

**The replay simulator is *not* an agent.** It has no reasoning and involves no LLM call — it's just the discovery tree exposed through a lookup interface ("if you pick this node next, here's the child and score already recorded"). That absence of a model call during replay is precisely what makes dreaming free. Calling it a "simulator agent" is a slight misnomer; it's better thought of as a frozen environment/dataset.

```
Online round:  exploration policy (code) → drives → discovery agent (LLM) → scored by → evaluator
                        ↓ (results logged)
                 discovery tree → added to → replay simulator pool (just data, no LLM)
                        ↓
Offline round: policy-development agent (LLM) → proposes new exploration-policy code
                        ↓
               new exploration policy → tested by replaying against → simulator pool (no LLM call)
                        ↓
               best-scoring version → redeployed → next online round
```

### Q4: A simple made-up scenario showing the policy-development agent reacting to evaluator feedback

**Round 1 — current policy:** *"Always try 5 totally different algorithms in parallel, then refine the best one 5 more times"* (task: fastest sorting function).

Discovery tree from the real run:
```
root
 ├─ QuickSort      (score 40)
 ├─ MergeSort      (score 55)
 ├─ HeapSort       (score 38)
 ├─ RadixSort      (score 90)  ← best
 ├─ BubbleSort     (score 5)
      └─ refine RadixSort ×5 → scores 91, 93, 93, 94, 94 (plateaued after attempt 3)
```

**Evaluator's feedback:** best score = 94, but cost = 10 attempts; 2 of the 5 refinement attempts added ~zero improvement (wasted budget); 3 of the 5 initial algorithms (QuickSort, HeapSort, BubbleSort) never had a chance of winning — a stronger prior could've skipped them.

**Policy-development agent's move** — it never touches the coding agent, only the policy's code:
```diff
- Try 5 random algorithms in parallel, then refine best one 5 more times
+ Try only algorithms historically strong for this input shape (skip BubbleSort-class)
+ Stop refining a branch after 2 consecutive attempts with <1% improvement
```
It validates this for free by replaying it against the *same* tree: stopping RadixSort refinement at attempt 3 (score 93) instead of attempt 5 (score 94) loses 1% quality but saves 2 attempts — net score (quality − cost) comes out higher. Skipping BubbleSort/HeapSort-class starts never would have lost the winner. Both changes score better on average → promoted, then deployed for Round 2's real run.

### Q5: Does this improved sorting policy transfer directly to a different task, e.g. "find the best clustering algorithm"?

**No** — you can't drop the sorting-tuned policy onto clustering and expect it to work. Both learned rules only mean something *inside the sorting search space*:

- *"skip BubbleSort-class"* is a fact about sorting algorithms. Clustering's candidate zoo (KMeans, DBSCAN, GMM, spectral, hierarchical...) is completely different — the policy has zero evidence about which of *those* are weak.
- *"2 consecutive attempts <1% improvement → stop"* was calibrated to sorting's specific plateau behavior and cost-per-attempt. Clustering may converge differently or cost far more per evaluation (e.g., DBSCAN on 1M points), so the same threshold could be wrong.

This mirrors how the paper itself runs experiments: each task (Lasso, sum-difference, circle packing, kernel engineering) gets its **own separate history `H_t`** and its own recursive rounds. Dreaming only replays over trees *from the same domain* — there's no tree for clustering yet, so nothing to dream against.

**What *does* transfer** is the *shape* of the lesson, not its content: "use a prior to avoid known-weak candidates," "add early-stopping for diminishing returns," "balance parallel exploration vs. deep refinement." These are transferable *policy-design principles* — not transferable numbers or transferable facts about which algorithms are good.

**Practical path for clustering:**
1. **Bootstrap** a generic policy with the same *mechanisms* (early-stopping, prior-weighting) but clustering-blank priors.
2. **Online explore for real** across clustering algorithms/datasets, logging a clustering-specific discovery tree.
3. **Dream over that tree** to discover clustering-specific facts (e.g., "DBSCAN with default eps never wins on high-dimensional sparse data").
4. Only now does the policy earn clustering-specific rules.

### Q6: So is this like a cache mechanism — evolve a policy once, then hand it to another group for the "same kind of question"?

Yes, with one important nuance about what the "cache key" actually is.

- **Cache key = the shape of the problem/domain**, not the literal instance.
- **Cache hit** = same domain, new instance → the evolved policy transfers directly, no re-dreaming needed.
- **Cache miss** = structurally different domain → the policy's content is invalid; must recompute (fresh online-explore + dream cycle), as in Q5.

The paper actually demonstrates the hit case for Lasso: the policy was evolved using 17 synthetic training instances, then deployed **as-is** on 6 completely different held-out datasets — including biological ones (DNA, Leukemia, Colon, Duke Breast) never seen during dreaming — and still outperformed baselines. Same domain shape ("find an efficient Lasso path"), different concrete inputs → cache hit.

**Giving it to another group is a good instinct, but treat it as a *warm* cache, not a guaranteed hit:**
1. **Validate before fully trusting it** — the other group's cost/quality tradeoffs may differ (e.g., different vendor price elasticity, different "cost of a round"). Run a small batch of real trials, or replay it against whatever history they already have, and let dreaming lightly recalibrate numeric thresholds.
2. **Cache invalidation still applies within a domain** — if the environment drifts (new tactics, new algorithms, shifting market conditions), even a same-domain cached policy goes stale and needs a refresh round.

So: ship the evolved policy as a strong prior/warm-start, but let one cheap round of dreaming (or a handful of real trials) confirm or recalibrate it for the new group's specific slice of the same domain — rather than assuming zero-shot transfer.

### Q7: Real-world example — a software-purchasing agent that negotiates vendor pricing

Goal: avoid dragging out negotiations while still landing the best price, and let the negotiation strategy *improve itself* over time instead of being hand-tuned forever.

| Dream-RSI role | Negotiation-agent equivalent |
|---|---|
| **Discovery agent** (fixed LLM) | The agent that actually emails/talks to the vendor, drafts offers and counter-offers |
| **Evaluator** (fixed) | Scores a *completed* negotiation: final price vs. target, discount %, number of rounds, days elapsed, relationship-risk flag |
| **Discovery tree** | One tree per negotiation: root = opening ask → each node = one offer/counter round → leaf = deal closed or walked away |
| **History (simulator pool)** | All past vendor negotiations logged as trees (SaaS renewals, hardware buys, etc.) |
| **Exploration policy** (what gets improved) | The negotiation strategy: opening anchor %, how many counters before conceding, when to escalate, when to walk away, whether to bundle multi-year commitment |
| **Policy-development agent** | An LLM that reviews past negotiation trees + scores and rewrites the negotiation-strategy rules |

**Flow:**
1. **Online:** run the current policy across ~8 real vendor negotiations, logging every round (offer, counter, response, final price, days taken).
2. **Evaluator scores each**, e.g. `score = (target_price − final_price) − λ·(rounds_taken) − μ·(relationship_risk)` — the negotiation equivalent of the paper's Eq. 1.
3. **Dreaming (free replay):** the policy-development agent asks, e.g., "what if we'd conceded after round 2 instead of round 4 whenever the vendor's counter was already within 8% of target?" — checked for free against negotiations where that pattern already occurred in the recorded data.
4. **Pattern found:** e.g., "when the vendor's first counter is within 10% of our ask, further counters rarely gain more than 2% but add 5+ days — concede immediately. But when the vendor moves <3% across 2 rounds, escalating or signaling walk-away gets a much better result than endless counter-offers."
5. **New policy code deployed** for the next quarter, e.g.:
   ```
   if vendor_counter within 10% of target: accept, don't counter again
   elif vendor movement < 3% after 2 rounds: escalate / signal walk-away
   else: counter once more with data-backed anchor, then re-evaluate
   ```
6. **Next quarter's real negotiations** produce new trees → feed history → next dreaming round refines further (e.g., discovers how multi-year bundling changes the calculus).

**Minimum viable version (without the full RSI machinery):** log every negotiation as a structured trace (offer, counter, outcome, time), define a numeric score like above, and periodically have an LLM review recent traces and propose one rule change to the playbook — testing that rule against historical traces before adopting it live. That's Dream-RSI's core idea, right-sized for a purchasing team instead of a research lab.
