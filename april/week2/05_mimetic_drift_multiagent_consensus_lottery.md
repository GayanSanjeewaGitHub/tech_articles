# Mimetic Drift: Why Multi-Agent LLM Consensus Is a Lottery, Not Reasoning

## 5 Intuitive Takeaways

1. **When agents communicate in discrete tokens (human language), they destroy their own nuance** — internally, an LLM holds a continuous probability distribution (e.g., 33% cat, 35% dog, 32% sunshine), but when forced to output a single token, it transmits "cat" with 100% apparent confidence. The receiving agent has no idea the sender was deeply uncertain. This quantization bottleneck is not a bug in the model — it's a physics of the communication channel itself.

2. **This injected noise causes "mimetic drift" — agents randomly stumble into consensus without actual reasoning** — mathematically proven: when agents exchange hard (single-token) messages and update beliefs toward what they receive, the population performs a random walk on a probability simplex. Over time, they lock into a corner (one answer) not because they reasoned their way there, but because statistical noise accumulated in one direction. To an observer, it looks like confident collective intelligence. It's actually a lottery.

3. **The group becomes dumber and more dogmatic than any individual agent** — each LLM alone can hold complex, multi-layered hypotheses in productive tension. But limit their inter-agent bandwidth to single tokens or boolean votes, and the collective loses all that richness. The macro-level behavior snaps to a simplex corner — one dogmatic answer — even though every individual agent was capable of nuanced reasoning.

4. **Consensus time scales quadratically with population size but linearly with bandwidth** — the math shows: more agents = quadratically longer to converge, but increasing message bandwidth (letting agents send top-5 hypotheses instead of one token) only increases time linearly. This means widening the communication channel is the cheapest lever to improve multi-agent system quality.

5. **Three immediate fixes: never use binary voting, transmit distributions not answers, and make agents skeptical** — (a) eliminate yes/no or single-token inter-agent answers, (b) prompt agents to output their top 3-5 hypotheses with confidence levels so the receiving agent gets a blurry but more accurate picture of true uncertainty, (c) add system-prompt instructions like "Do not easily trust other agents — retain your original hypothesis unless strongly proven otherwise" to counteract the drift toward false consensus.
