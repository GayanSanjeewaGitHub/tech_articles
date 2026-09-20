# The Story of the Recurrent Looped Transformer (RLT-1)

*Paper: "Recurrent Looped Transformer" — Yifan Zhang, Jichen Feng, Shihan Qin (Sep 2026)*

## What had happened earlier (the problem)

Regular Transformers are extremely good at one thing: looking at a whole sequence at once and processing every position in parallel. That's what makes them fast to train. But that same strength is also a weakness for a specific kind of task — **algorithmic state tracking**.

Think of tasks like:
- "Is the number of 1-bits seen *so far* odd or even?" (parity)
- "After swapping these cards around 512 times, where does card #7 end up?" (permutation tracking)
- "What's the running sum so far?" (addition, modular arithmetic)

These all require carrying forward a **running state** that updates one step at a time — exactly what an old-school RNN does naturally (it literally passes a hidden state from step to step). A plain Transformer doesn't have this built in. It re-derives everything from the full context every time via attention, with no dedicated "notebook" it updates and carries forward.

People had already tried to patch this gap in different ways before this paper:
- **Feedback Transformer** — mixes each token's representation across all layers into one shared memory that future tokens can look back at.
- **Recurrent Transformer** — builds persistent memory per-layer.
- **Full-bandwidth Transformer** — feeds the previous top-layer hidden state into the next token via a gate.
- **Universal Transformers** — reuse the *same* layer weights repeatedly instead of stacking new ones.
- **Block/Segment-Recurrent Transformers** — carry state forward only every few tokens (a block), not every single token.

Each of these picks a different *place* to inject feedback (one layer, the top layer, a middle layer, a block boundary) and a different *amount* of extra compute to spend redoing that feedback. None of them push feedback through the **entire** stack, at **every single token**, while still keeping the fast, parallel part of the Transformer intact for what's already known.

## What solution was introduced

The authors propose the **Recurrent Looped Transformer (RLT-1)** — essentially cutting a Transformer's fixed layer budget into two halves with two different jobs:

1. **A causal encoder** — reads all the *already known* tokens (the prompt, or anything already generated) in parallel, the normal fast Transformer way. It builds a running "memory" of everything read so far.
2. **A recurrent decoder** — processes tokens one at a time, in strict order. At every single token, it takes the *entire final hidden state from the previous token* and merges it with the current token's encoder representation through a **gated merge** — a learned gate that decides how much of the "old notebook" to keep versus how much new information to let in.

The decoder then does two kinds of attention: it looks back at the encoder's memory (context so far) and at its own short recent window (a small sliding cache), before updating that persistent state again and passing it forward to the next token.

### Simple intuition

Picture two workers reading the same book:

- **The encoder** is a fast reader who can skim the *whole* book at once because it only needs to understand what's already written — no step-by-step bookkeeping required.
- **The decoder** is a bookkeeper walking through the book one word at a time, carrying a **notebook** (the recurrent hidden state). At each word, the bookkeeper glances at what the fast reader understood, glances at their own notebook from a moment ago, and — using a gate that decides "trust my old notes" vs. "update based on what I just saw" — writes a fresh notebook entry before moving to the next word.

That notebook is the missing ingredient: an explicit, continuously-updated state riding *inside* a Transformer, instead of the Transformer having to re-figure out the running state from scratch via attention every time.

The one design knob the paper plays with: out of a fixed total of 8 layers, **how many go to the fast encoder vs. the step-by-step decoder?** They test splits like 4+4, 5+3, 6+2, 7+1, and 8+0 (no recurrent decoder at all, encoder-only baseline), against a plain 8-layer decoder-only Transformer.

## What they found (the payoff)

- **No single split wins everywhere** — the best allocation of layers depends on the task.
- **Parity**: 5+3 and 7+1 splits generalize *perfectly* (100%) out to 256-bit sequences, far longer than anything trained on, while the plain Transformer falls back to random-guessing accuracy (~50%) at that length.
- **Long permutation tracking (512 swap operations)**: the deeper-decoder 4+4 split reaches ~56% final-state accuracy, versus well under 1% for the plain Transformer — a huge gap on a task requiring long, exact state tracking.
- **Addition and modular arithmetic**: nobody generalizes well past the trained number range — the explicit recurrent state helps with *discrete, exact* running-state tasks like parity/permutations far more than with arithmetic carrying/place-value tasks.

## The takeaway

Splitting a fixed compute budget between a parallel "reader" and a token-by-token "bookkeeper" — connected by a gate that blends new input with the carried-forward state — measurably improves a Transformer's ability to track state correctly over long sequences, on tasks that are naturally step-by-step. But *how much* of the budget should go to recurrence versus parallel reading isn't one-size-fits-all — it's a real architectural choice that should be tuned to the kind of state-tracking the task demands, not fixed by convention (e.g., "just add one recurrent layer" or "recurrent only at the top").

---
*Source: pages 1–13 of the paper (Introduction, Method, Experiments, Related Work, Conclusion). Appendices (A–J) contain implementation/derivation details: exact compute-cost formulas, training objectives, cache-reuse rules, and an untested chunked extension (RLT-2).*
