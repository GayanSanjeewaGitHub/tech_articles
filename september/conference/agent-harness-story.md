### The scene

Same customer request, same LLM, two agents. "Cancel my order, I'm unhappy with the delivery." One agent cancels it and refunds the full amount — then narrates a total that's off by an order of magnitude. The other checks a refund policy, notices the customer already got a partial credit earlier, and pays out exactly the remainder it's allowed to.

### Why it hurts

That first agent just gave away money it had no authority to give away, and hallucinated the number while doing it. Nobody touched the model between the two runs. Whatever went wrong wasn't the model's fault — which means the usual instinct, "let's try a bigger model," won't fix it.

### What's actually happening underneath

Most teams spend 80% of their effort picking the model and 20% on everything around it — when the split should be reversed. The failing agent had one "modify_order" tool doing cancel, refund, and address changes all at once, with no description of what it should check first. The working agent had separate, well-documented tools, plus a "skill" — a markdown file of domain rules loaded into context only when relevant — telling it to check refund history and policy caps before acting. Frontier models are converging in capability; tool design and injected expertise are where the real gap lives now.

### The shift

**An agent's reliability lives in the harness around the model — tool design, skills, memory — not in which model you plugged in.** The reasoning loop itself stays a few hundred lines and never changes; everything that makes the agent trustworthy is injected around it.

### The fix

Split gold tools into atomic ones with explicit descriptions and error-recovery guidance. Move domain policy out of the prompt and into skill files the agent loads on demand. Keep the agent loop itself boring and static — swap tools and skills, not code.

### The question to sit with

When your agent gets something wrong, do you reach for a bigger model — or check what the harness never told it?
