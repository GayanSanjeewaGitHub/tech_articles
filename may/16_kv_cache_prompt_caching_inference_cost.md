# The Dollar and the Nickel

### The scene

Same prompt. Same model. First call: $1.00. Second call: $0.05. Nothing changed except that you sent it twice. The invoice doesn't explain it. Your intuition says it should cost the same. It doesn't — and the reason is one of the oldest tricks in computer science, finally applied at scale.

### Why it hurts

On an agent loop running hundreds of calls per hour against a long system prompt, that 20x gap compounds fast. Teams notice the bill before they understand the cause. They shorten prompts, strip context, degrade the agent — solving the wrong problem entirely.

### What's actually happening underneath

At inference time, transformers lose the parallelism they were designed for. Each new token is sequential. And for every token generated, the model runs an expensive matrix multiplication — a 4,000-dimension embedding through a 4,000×4,000 grid — across every layer, for every prior token, to produce its Key and Value vectors. That's roughly 2 billion math operations per token just in setup. A thousand tokens deep, you've recomputed the K vector for the word "the" a thousand times. Identical inputs. Identical outputs. Wasted.

### The shift

**You're not paying for compute. You're paying for GPU memory bandwidth.** Donald Michie named the fix in 1968: memoization — save the answer, don't compute it twice. Applied to attention, that's the KV cache. The expensive intermediates get stored after each token and reused on the next. The memory wall (Wolf & McKee, 1995) predicted this exact constraint: compute keeps doubling, bandwidth doesn't.

### The fix

Prompt caching lets the provider keep your KV cache across API calls. The first call builds it. Every subsequent call with the same prefix rents it — no matrix multiplications, no setup cost. But there's a catch: **token order is a cache invalidation strategy.** Change anything in the prefix and every cache entry after that point is gone. Put your system prompt, tools, and documents first — the stable content. Put the user's query last. Same tokens, different order: 10x cheaper inference on agent loops.

### The question to sit with

Does your agent prompt put the user's question first — and are you paying for that every single call?
