### The scene

You spend an afternoon rewriting a prompt. Better wording, a role assignment, a few-shot example. The model still confidently invents a fact that doesn't exist. Not once — every session, on a different question.

### Why it hurts

That fabricated answer ships into a real workflow — a SQL query against the wrong column, a trip planner booking a cab for a hotel it already forgot it canceled. Nobody notices until the downstream system breaks, because the model states the wrong thing with the same fluency as the right one.

### What's actually happening underneath

A language model is a function over tokens, trained to predict the next most likely one — nothing more. It has no memory, no database, no notion of "I don't know." When the information it needs isn't in front of it, the training objective doesn't stop, it guesses — fluency was always the target, accuracy was never guaranteed. And the context window itself has a limit: pack it with too much, and the attention mechanism that decides what to focus on starts spreading itself thin. More text in the prompt doesn't mean more signal.

### The shift

**Hallucination isn't a wording problem, it's an information-gap problem — so the fix lives in architecture, not phrasing.** Prompt engineering polishes the request; it can't manufacture facts the model was never given.

### The fix

Treat everything feeding the model as a system to design: what short- and long-term memory gets carried forward, what state an agent must track across steps, what retrieval fetches only the relevant slice of a knowledge base instead of dumping it all in, what a tool's output reports back before the next step runs. Prompt engineering becomes the last, smallest layer on top — not the whole strategy.

### The question to sit with

When your model gets something wrong, are you rewriting the prompt — or checking what information it never had?
