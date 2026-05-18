# The Memory Tax

### The scene

The agent is doing a customer refund. It opens a ticket, fetches the customer record, searches policy docs, re-reads the entitlement table, and burns 85% of its token budget before writing a single word of the response. Every run. The same sources. The same rediscovery. The useful work happens in the last 15%.

### Why it hurts

Token budgets aren't free. Latency compounds. And worse — the agent isn't even consistent. One run it finds the right policy clause. The next run it finds a semantically similar one that says something slightly different. No audit trail. No authoritative source. Just whichever paragraph happened to land closest to the query vector that day.

### What's actually happening underneath

Classic RAG was built for a chatbot: embed a question, find three similar chunks, hand them to the model. That loop works when the answer lives in a paragraph and the user doesn't need it to be exactly right. Agents don't work like that. An agent runs a task — and a task needs a **bundle**: the customer record plus the plan plus the refund policy plus the prior exceptions plus the authorization level, assembled into the right shape before reasoning starts. Vector search finds relevant text. It doesn't assemble operating context. So the agent reassembles it from scratch, every single run, from raw search noise.

### The shift

**The retrieval unit has to match the shape of the work — not the shape of the database you already bought.** A chunk works for FAQ. A document tree works for a contract. A governed table works for a revenue number. A graph works for dependency reasoning. Pick the wrong shape and the model compensates — expensively, inconsistently.

### The fix

Don't pick the database first. Write down the bundle your agent needs to do the job reliably — every field, every source, every permission. When you write it out, three things become obvious: the fields don't all live in one system, some need to be governed not just retrieved, and your agent's actual work is reasoning over the bundle — not searching for docs. Now go shopping. Choose primitives that deliver your specific bundle. The choice stops being a vendor debate and starts being an engineering decision.

### The question to sit with

How many retrieval calls does your agent make before useful work starts — and have you ever actually counted?
