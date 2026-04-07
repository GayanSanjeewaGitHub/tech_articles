# AI Evals: Why Vibes-Based Shipping Fails & Agentic vs Vector Search

## 5 Intuitive Takeaways

1. **Shipping AI features based on "vibes" is engineering malpractice** — saying "a PM tried a few prompts and it looked good" is not a ship decision. Evals let you quantify quality: "we ran 200 test cases, 94% passed" or "this change improved tone but dropped accuracy by 5%." Without evals, you're flying blind every time a model updates or a prompt changes.

2. **An eval has four parts: dataset, task, scorer, experiment** — you build a golden dataset (happy paths + edge cases + failure modes), define a task (prompt + model), write scoring criteria (deterministic checks, LLM-as-judge, or human review), then run experiments. Each configuration = one experiment run, and you compare runs to catch regressions before shipping.

3. **Agentic search beats vector search because it preserves the *connective tissue* of code** — vector search returns isolated chunks that are *near* the answer semantically, but strips away imports, type definitions, and call chains. Agentic search reads files like a human: finds a function, follows its references, reads the full file, and navigates the dependency graph. Proximity to relevant code is not the same as understanding the code.

4. **Vector search's failure mode is expensive guessing** — in the eval, one vector search run made 26 separate search calls trying to guess-and-check its way to the bug location because chunks lacked enough context. Agentic search found it faster by following the logic chain. The result: vector search consumed significantly more tokens and cost, while performing the same or worse.

5. **No single eval run is trustworthy — LLMs are non-deterministic** — running the same eval with identical criteria can swing results 10-15%. A rigorous eval requires multiple trials averaged together, expanded datasets (10 rows means one failure = 10% swing), and iterating on the implementation itself (e.g., better chunking strategies for vector search). Evals are a living, iterative process, not a one-shot validation.
