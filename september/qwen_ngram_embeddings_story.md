### The scene

At 2:13 a.m., the context window crossed 120,000 tokens. Latency jumped from four seconds to nineteen. GPUs were busy rereading a conversation they had already processed, while the model still stumbled over simple phrases like "hot dog" as if the words had never met.

### Why it hurts

The service was not down. That would have been easier.

Requests kept finishing, slowly enough to exhaust queues and expensively enough to light up the billing dashboard. Adding hardware bought temporary relief, but every longer conversation pushed attention toward the same quadratic wall. Twice the context meant roughly four times the comparison work.

### What's actually happening underneath

We had treated every token as an isolated starting point.

The model generated one token at a time and initially represented each token through its own embedding. Deeper layers then had to rediscover that `hot dog` carried meaning beyond `hot` and `dog`. Meanwhile, full attention compared each token with nearly every earlier token, even when most of that history was irrelevant.

The architecture was spending expensive computation reconstructing local patterns while searching globally through an ever-growing archive.

### The shift

**Token-by-token generation does not require token-by-token understanding.**

The decoder could keep producing one token per step while receiving richer representations of known token sequences. Local phrases could become cheap lookup features. Long-range history could be searched selectively.

### The fix

We added learned n-gram embeddings during training. Adjacent token IDs were combined into deterministic bigram and trigram keys, then mapped into an embedding table. When `hot` and `dog` appeared together, the current representation included the token embedding and a learned feature for the pair.

Nobody manually encoded what the phrase meant. Repeated training examples shaped that vector through backpropagation.

Generation remained autoregressive. After producing `dog`, the model used the `hot+dog` feature to predict the next token.

For distant context, sparse attention grouped tokens into blocks and searched only promising regions. Local recognition became a lookup. Global retrieval became selective. The expensive layers stopped repeatedly rebuilding information the input could provide upfront.

### The question to sit with

How much of your system's expensive reasoning is really repeated reconstruction of patterns you could represent directly?
