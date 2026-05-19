# The Machine That Couldn't Sleep

### The scene

The agent has been running for 3 hours. It cloned a repo, installed packages, spun up a dev server, and is mid-migration. The user goes to lunch. The machine keeps running — fully charged, fully billed — waiting. Or you kill it, and lose everything. Neither answer is acceptable at scale.

### Why it hurts

Production agents aren't a novelty anymore. They run for hours. The capacity to do meaningful work is doubling every 4 to 7 months. Keeping machines live the entire time is financially untenable. Killing them discards state that took hours to build. The infrastructure model that powered the last 30 years of backends wasn't designed for this.

### What's actually happening underneath

Thirty years of backend architecture was built on one principle: stateless compute. Request comes in, compute runs, response goes out, state lives in the database. Workflow engines added durability by replaying a journal of every step — which works beautifully for transactions. But an agent isn't a transaction. **An agent is a session.** The replay journal grows without bound across turns. It hits limits. And it can't capture what the compute layer actually holds: the cloned repository, the installed packages, the subprocess that's been running for 40 minutes.

### The shift

**You can't replay your way to a durable session.** The replay model rebuilds state from a log. But execution state — a dev server, a file system mid-edit, a dataset loaded into memory — can't be logged. It has to be saved whole.

### The fix

Split the problem. Context durability is just an append-only log — every message, tool call, and response persisted to a database. Cheap, scalable, already solved. Execution durability is snapshot and restore. When the user goes to lunch, snapshot the entire VM to disk and shut it down. When they return, restore it in under 200 milliseconds — right where it left off, no replay, no rebuild. Compressed to roughly 14 megabytes, the machine state that took hours to construct costs almost nothing to preserve.

### The question to sit with

If your agent crashes mid-task tonight, what exactly does it lose — and have you ever designed for that answer?
