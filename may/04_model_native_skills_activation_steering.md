# The Skill You Wrote Down Was Never the Skill the Model Learned

## The scene

You write a 600-line `skill.md`. "You are a senior Python engineer. Handle exceptions cleanly. Follow PEP 8." Tokens flood the context on every call. The model still hallucinates a missing `try/except`. You add another paragraph. Then another. The bill climbs. The behavior barely moves.

## Why it hurts

Every prompt token is paid forward — input cost, latency, context pressure. Skill markdown files compound: ten skills loaded means tens of thousands of tokens consumed before the model sees the user's question. And the worst part — the more you write, the less reliable the steering becomes. You're scaffolding around a probabilistic core with English text and hoping it lands.

## What's actually happening underneath

The model has no concept of "senior Python engineer." Inside the transformer, every behavior is a **direction in a 4,096-dimensional activation space** — not a name, not a category, not a paragraph. When you write skill markdown, you're describing a vector in human language and praying the embedding lands near the right axis. It usually doesn't. The model's own basis isn't organized around human syllabi like "math" or "exception handling" — it's organized around whatever directions minimized pre-training loss. Often non-human. Often spanning categories your taxonomy can't see.

## The shift

**A skill is not a paragraph. It is an eigenvector on the activation manifold.**

You don't teach it with words. You locate it with sparse autoencoders, then steer the residual stream directly along that axis at inference time.

## The fix

Stop writing the persona. **Compute it.** Average the activations across known-good outputs, extract the principal direction, and inject that vector into the residual stream at runtime. The persona becomes a tensor, not a prompt. Context window cost drops to zero. Behavior becomes deterministic along that axis. For fine-tuning, identify the model's weak directions first — then curate 1,000 targeted examples instead of 100,000 random ones. One paper reports 41% gains on math benchmarks using this curriculum, with a fraction of the data.

## The question to sit with

If your "skill" only exists as English text in a markdown file — what makes you think the model ever learned the same skill you wrote?
