### The scene

A data team spends months building a proper multi-agent pipeline — a query agent hands off to a planning agent, which hands off to an execution agent, which hands off to reporting. Each one gets a narrow, hand-picked set of tools. Eval scores look great, 30% and climbing. They hand it to real users. The verdict comes back: it's awful.

### Why it hurts

The gap between "passing our evals" and "actually useful" isn't a tuning problem you can eval your way out of — real questions don't look like the scenarios you anticipated, and no amount of manually mapping edge cases into the pipeline scales. Months of careful architecture, and the thing falls over on exactly the questions it exists to answer.

### What's actually happening underneath

Every hand-built tool in that pipeline was bespoke — a custom API surface the model had never seen much of during training. Then a coding agent shows up using nothing but list-file, read-file, run-bash against a plain sandboxed filesystem, and it outperforms the whole hand-crafted pipeline without even trying hard. The tools weren't smarter, they were just *familiar* — bash and file operations are what these models have been trained on constantly. A custom pipeline doesn't add capability, it adds a translation layer the model has to learn on the fly, on your dime.

### The shift

**Capability doesn't come from a cleverer pipeline, it comes from handing the model tools it's already fluent in and letting it figure out the steps itself.**

### The fix

Drop the prescribed multi-agent chain. Dump the whole semantic layer into files in a sandbox, give the agent list/read/write/bash, and let it explore. Eval score doubled overnight. Once real usage revealed which query shapes kept recurring, those got distilled into reusable skill files loaded at the start of a run — pre-loaded context instead of starting from nothing every time.

### The question to sit with

Are the tools you built your agent narrowing it into a bespoke interface — or letting it use the patterns it already knows cold?
