# The 270M Parameter Model That Was Wrong Half the Time

### The scene

The feature is voice-to-action on a mobile app. Say "add this to my calendar" and the model calls the right function. Out of the box, the 270-million-parameter model hits 46% accuracy. Half of all user commands fail silently. The model just doesn't do what it's told.

### Why it hurts

You can't swap in a bigger model. On-device means fitting inside 200MB. Latency budget is under 100ms. Cloud isn't an option — offline use is the whole point. So you're stuck: a model that's wrong half the time and no obvious lever to pull.

### What's actually happening underneath

A 7B model can reason through a system prompt. Describe ten functions, give examples, and it figures out the rest. A 270M model has no reasoning budget left for that. Every parameter was spent learning language. When you hand it a task at runtime via prompt, there's nothing left to execute it reliably. The model reads your instructions. It just can't act on them consistently.

**Below ~1B parameters, the model cannot generalize from your prompt. It needs the task baked into its weights.**

### The shift

Prompting is a runtime instruction. Fine-tuning is a structural change. At tiny scale, the line between "model behavior" and "model configuration" collapses into one thing: training data. If you want it to do something reliably, you have to teach it — not describe it.

### The fix

Generate synthetic examples for your specific functions — use a larger model to fabricate hundreds of input/output pairs. Fine-tune on that data. The 270M model goes from 46% to 90%+ on 8 of 10 functions. The remaining two need more examples, not more prompting. More work than a system prompt. But the task lives in the weights now, not a fragile string you maintain forever.

### The question to sit with

Which behaviors in your deployed model are you prompting for that should have been trained in?
