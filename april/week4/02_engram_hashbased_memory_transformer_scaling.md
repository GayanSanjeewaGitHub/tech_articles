# Engram: Why Your Transformer Wastes Half Its Depth Just Remembering Who People Are

## The Trap

Most developers think of a transformer as a unified reasoning engine — attention captures relationships, feed-forward networks store knowledge, and depth equals intelligence. More layers, more parameters, more capability. Simple.

But here's what that mental model hides: **a staggering fraction of your model's layers are not reasoning at all. They are doing lookup.** They spend compute reconstructing facts that could have been fetched from a table in constant time. You are burning floating-point operations to simulate memory retrieval.

The naive view treats all parameters as equally valuable. The architectural truth is that static factual knowledge and dynamic compositional reasoning have fundamentally different compute profiles — and cramming both into the same dense matrix is an engineering mistake.

## The Stop-and-Think Moment

Consider the phrase *"Diana, Princess of Wales."*

- After layer 1, the model barely knows these are English words.
- After layer 2, "Wales" resolves to "a country in the UK."
- After layer 4, "Princess" shifts from fairy-tale noun to institutional title.
- After layer 6, the full entity finally assembles: a specific historical person.

**Six transformer layers consumed — not to reason, but to reconstruct a fact that exists as a static association.**

Now ask yourself:

- **What if the model already knew who Diana was before attention even started?**
- **How many of your model's "reasoning layers" are actually doing glorified dictionary lookups?**
- **What would those layers do if they were freed from factual reconstruction?**

## The Mental Model Shift

> **Stop thinking of transformers as monolithic reasoners. Start thinking of them as two interleaved systems: a memory system and a reasoning system — currently forced to share the same hardware.**

Feed-forward networks encode facts by learning weight matrices where each row asks a semantic question and each column stores an associated fact. This works, but it's compute-bound recall. Every token pays the full cost of dense matrix multiplication even when most hidden units are irrelevant.

Mixture of Experts improved this by activating only a sparse subset of experts per token. But even MoE retrieves knowledge *via computation* — routing decisions, expert forward passes, gating networks. It's still simulating memory through arithmetic.

**What if you could just look it up?**

## The What-If Scenarios

**Scenario 1: The Entity Grounding Tax.**
A question-answering model encounters "Alexander the Great led his army across..." Before it can reason about military strategy, it must first spend layers establishing who Alexander is, what era he belongs to, what army means in that context. Every factual entity in the input imposes a "grounding tax" — layers consumed before reasoning can begin. Scale the input to a document full of named entities, and your model is half-depleted before it starts thinking.

**Scenario 2: The Collision Between Knowledge and Capacity.**
You want a model that knows more facts. With dense FFNs, you increase hidden dimensions — but training slows, memory balloons, and most of those new dimensions fire for barely any tokens. With MoE, you add experts — but each expert still stores knowledge in learned weights. Neither approach separates the *how much the model knows* from *how hard it computes per token*.

**Scenario 3: The GPU Memory Ceiling.**
Your factual knowledge tables grow to billions of entries. Dense weights and MoE experts must live on GPU HBM. But a lookup table? It only needs the rows you're fetching. The rest can sit in CPU RAM — orders of magnitude cheaper and larger.

## The Architecture: Engram as Constraint-Driven Design

Engram resolves these tensions with a deceptively simple insight: **hash the token n-grams, look up embeddings from a table, gate the injection contextually.**

- **Hash-based indexing:** For each unigram, bigram, and trigram, compute a multiplicative XOR hash of token IDs. This gives you a table index in constant time — two multiplications, one XOR, one modulo. No router. No dense matmul.
- **Multi-head hashing to fight collisions:** Eight independent tables with distinct multipliers. Even if "Harry Potter" and "Ron Weasley" collide in one table, they almost certainly won't collide in all eight. Concatenate the retrieved rows for a rich, collision-resistant embedding.
- **Context-aware gating:** Not every n-gram carries useful factual knowledge. The hidden state acts as a query; the retrieved embedding provides a key. Their dot product, passed through sigmoid after RMS normalization, produces a scalar gate. Irrelevant memories are suppressed to near zero. Relevant ones pass through.
- **Depthwise causal convolution:** A short conv block over the gated values widens the receptive field slightly beyond the local n-gram window and adds nonlinearity, all while preserving information through a residual connection.
- **Placement at layer 2:** One round of attention is enough to make gating meaningful. From that point, every subsequent layer benefits from enriched context. A second block at a middle layer catches residual associations that only emerge after partial processing.

The key result: **Engram's layer 2 produces representations that resemble a much deeper MoE layer.** The model has effectively gained depth without increasing compute cost.

## The Hidden Mechanics Most People Miss

- **Prefetchability:** The hash depends only on token IDs, known at input time. All table lookups can be issued *before the first transformer layer starts computing.* By the time a layer needs the embedding, it's already arrived. Memory latency is hidden behind computation.
- **CPU offloading:** The embedding tables don't need GPU HBM. They sit in CPU RAM — larger, cheaper, and the prefetch pipeline makes the transfer invisible.
- **The 75/25 split:** Pure MoE and pure Engram both underperform. The sweet spot is ~75% MoE, ~25% Engram. MoE handles flexible compositional reasoning. Engram handles fast factual recall. Together they outperform either alone — on knowledge benchmarks *and* on reasoning, code, and math.
- **Scaling as a power law:** More table slots mean lower loss, following a clean, predictable power-law curve. Engram offers a scaling pathway orthogonal to adding parameters or compute.

## Intuitive Summary

- **Transformers waste early layers reconstructing facts** (who is Diana? what is Hogwarts?) before any real reasoning begins — Engram eliminates this tax by injecting factual knowledge via direct hash-table lookup before attention even starts.
- **Hash-based memory replaces compute-based recall:** Instead of routing through dense matrices or expert networks, Engram computes a simple hash of token n-grams and fetches pre-stored embeddings in constant time.
- **Collisions are managed, not eliminated:** Multi-head hashing across eight independent tables makes it statistically near-impossible for two different entities to collide in all tables simultaneously.
- **Context-aware gating prevents noise injection:** A learned sigmoid gate ensures only factually relevant retrieved embeddings modify the hidden state — function words like "the" produce near-zero activations.
- **The result is a functionally deeper model at the same compute cost:** Freeing early layers from entity grounding lets them focus on reasoning, effectively giving the transformer extra depth for free.

## The Question to Sit With

If 20-25% of your model's optimal parameter budget belongs in a lookup table rather than learned weights, **what other components of your architecture are pretending to compute when they should be remembering — and what would your system look like if you honestly separated the two?**
