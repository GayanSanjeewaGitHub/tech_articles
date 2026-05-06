# The Context Window Tax: Why Your MCP Agent Is Burning Tokens Before It Does Anything

## The Problem (What Breaks in the Real World)

Your agent hasn't run a single query. It hasn't touched a database, called an API, or read a document. And it has already consumed **55,000 tokens**.

That's what happens when you connect a typical multi-server MCP setup and let it eagerly load every tool definition into the context window. The model spends its budget reading schema before it can spend it thinking.

The symptoms are predictable:

- **Cost explosions** on every agent run, even for simple single-tool tasks
- **Latency spikes** as the model processes 150,000+ token contexts when 2,000 would have been enough
- **Accuracy degradation** — documented to occur once tool counts pass 30 to 50, because the model struggles to select correctly from a dense, undifferentiated list
- **Privacy leakage** — intermediate results like emails and phone numbers flowing through the context window when they never needed to

The naive assumption is that giving the agent more tools makes it more capable. The reality is that past a threshold, more tools make it worse — and dramatically more expensive.

---

## Why This Happens (Root Cause Analysis)

The root cause is **eager loading combined with verbose schema serialization**.

- MCP servers announce their capabilities by sending full tool definitions — name, description, and input schema — for every available tool at connection time
- JSON repeats field names on every record; a list of 100 tool schemas is 100× the verbosity of a single one
- Context windows are finite; every token spent on definitions is a token not available for reasoning, retrieval, or output
- Tool selection accuracy is a function of signal-to-noise ratio in the context, not raw tool count

**Ask yourself this:** If your agent only ever uses 4 out of 60 available tools for a given workflow, why does the model need to read all 60 before starting?

And if intermediate results — filtered datasets, API responses, transformed records — never need to be reasoned over by the model, why are they in the context at all?

---

## The Mental Model Shift

**Stop thinking about tools as a flat list the model must memorize. Start thinking about tools as a file system the agent navigates on demand.**

| Old Assumption | New Understanding |
|---|---|
| Load all tools upfront so the agent knows what's available | Load only what the current task requires; discover the rest lazily |
| The model reasons over tool results | The model reasons over summaries; execution stays outside the context |
| More tools = more capability | More tools = more noise; capability comes from precise loading |
| JSON is the natural output format | JSON repeats field names; columnar encoding can cut that cost 30-60% |
| Context window is a workspace | Context window is a cost center; minimize its surface area |

---

## What Happens If You Ignore This (Real Consequences)

**Scenario 1 — The 150k Token Document Transfer**
An agent moves a document between two external services. With eager tool loading and direct tool calls, the full round-trip pushes ~150,000 tokens through the context. At GPT-4-class pricing, this is 30-75× more expensive than necessary. Run this 10,000 times a day and the bill becomes the engineering problem.

**Scenario 2 — The Selection Accuracy Cliff**
A multi-server setup exposes 80 tools. The model is asked a simple question that requires one tool. With all 80 definitions loaded, selection accuracy degrades measurably — the model picks adjacent but incorrect tools, or hedges across multiple. The agent loops. Costs compound. The failure isn't obvious from logs; it looks like a reasoning failure, not a context problem.

**Scenario 3 — The Privacy Audit Failure**
An agentic workflow processes customer records. Phone numbers, email addresses, and account details flow through intermediate tool calls and land in the context window as the model processes them. A compliance audit reveals that PII was retained in conversation logs it was never supposed to enter. The issue was never the data policy — it was that intermediate results were routed through the model when they should have stayed in the execution environment.

---

## The Approach (How to Think About the Solution)

The design principle is **progressive disclosure**: reveal information to the model only when it has demonstrated a need for it, and keep intermediate computation outside the context wherever possible.

There are two orthogonal axes to optimize:

1. **Input tokens** — how much schema, definition, and metadata the model loads before it acts
2. **Output tokens** — how much data from tool responses re-enters the context after execution

Stack optimizations along both axes. The techniques below compose — applying several layers simultaneously produces multiplicative gains.

---

## The Solution (Architecture / Pattern / Implementation)

### Layer 1: Code Execution — 98% Input + Output Reduction

Instead of loading tool definitions directly, give the agent a **sandboxed execution environment** where each tool is represented as a file. The agent explores the file system to discover what's available and reads only the files relevant to the current task.

```
/mcp-tools/
  google-drive/
    list_files.ts
    move_file.ts
  crm/
    create_record.ts
    update_contact.ts
```

- Agent reads `list_files.ts` when it needs that specific capability — not all of `google-drive/` upfront
- Intermediate results (filtered datasets, API responses) stay in the execution environment
- **Only the final result enters the context** — ~2,000 tokens vs. ~150,000 for the same workflow

Secondary benefits:
- **Loops and conditionals stay in code**, not in model reasoning steps — no round-trip to the model between each iteration
- **PII stays outside context** — emails, phone numbers flow through execution without ever entering the window
- **Large datasets can be filtered in code** before any portion is surfaced to the model

```python
# NAIVE: Every tool call returns to the model
results = []
for file in drive.list_files():          # model sees every file
    results.append(crm.create_record(file))  # model reasons over each result

# CORRECT: Code runs the loop; model only sees the summary
# Tool marked: allowed_callers=["code_execution"]
summary = execute_in_sandbox("""
  files = drive_list_files()
  records = [crm_create_record(f) for f in files if f.type == 'contract']
  return f"Migrated {len(records)} contracts"
""")
# Only the string "Migrated 47 contracts" enters the context
```

**Complexity cost:** Requires a real sandbox with isolation and resource limits. High ceiling, but not a drop-in change.

---

### Layer 2: Tool Search — 85% Input Reduction

The agent starts with a small set of core tools plus a **search tool**. When it needs capability it doesn't have, it queries the catalog — the same way a developer searches documentation rather than reading all of it.

- Supports regex or BM25 (natural language ranking) search over the tool catalog
- Tools not needed immediately have `default_loading: false` — they exist but consume zero tokens
- Degrades gracefully at scale: works across thousands of tools without loading context proportionally

This preserves the MCP contract (the server owns tool definitions) while eliminating the eager-load problem.

---

### Layer 3: Scope Loading — Load by Group

Group tools by functional domain and load only the relevant group at connection time:

```json
// MCP connection config — only finance tools loaded
{
  "url": "mcp://data-server",
  "params": { "groups": "finance" }
}
```

- An e-commerce agent loads `["catalog", "orders"]` — not social media or finance tools
- Groups are declared by the server, selected by the client at session init
- **Composable**: combine multiple groups in one session; pay only for what you specify

For production agents with a known job, go one step further: whitelist exact tool names via an environment variable. If your workflow uses 4 tools out of 60, load 4.

---

### Layer 4: Dynamic Context Loading — Three-Level Disclosure

Instead of schema-on-connect, implement staged revelation:

| Level | What the Agent Receives | Token Cost |
|---|---|---|
| 1 | List of available MCP server names | Minimal |
| 2 | Tool names + one-line summaries for a chosen server | Low |
| 3 | Full name, description, and input schema for a specific tool | Normal |

The model walks down levels as it narrows its intent. It never reads schemas for tools it doesn't use.

---

### Layer 5: Programmatic Tool Calling

A variant of code execution that works with tools defined directly in your application. The model writes Python that calls tools as functions. Intermediate results stay in the execution environment.

```python
# Tool definition
@tool(allowed_callers=["code_execution"])
def search_documents(query: str) -> list[dict]: ...

# Model generates this code — intermediate pages never enter context
def run():
    pages = []
    for q in ["contract", "invoice", "amendment"]:
        pages.extend(search_documents(q))  # stays in sandbox
    return summarize(pages[:10])           # only summary reaches model
```

**Caveat:** Tools provided through MCP connectors cannot currently be called programmatically. This composes with application-defined tools only — a gap flagged for future MCP versions.

---

### Layer 6: Output Token Optimization

Tool responses are often over-formatted for model consumption. Two practical cuts:

1. **Strip formatting before returning to context** — remove Markdown, HTML, and boilerplate from web results before they enter the window. The model doesn't need visual structure; it needs content.
2. **TOON (Token-Oriented Object Notation)** for flat tabular data — declare field names once, stream values as rows:

```
# Standard JSON — field names repeated N times
[{"id":1,"name":"A","price":10}, {"id":2,"name":"B","price":20}]

# TOON — field names declared once
fields: [id, name, price]
rows: [[1,"A",10],[2,"B",20]]
```

- **30-60% token reduction** on flat uniform data
- **Does not apply** to deeply nested structures (e.g., profiles with nested arrays) — know your data shape before applying

---

### Stacking the Layers

No single technique is sufficient at scale. The recommended production stack:

```
Connection layer:    tool groups → scope what loads
Discovery layer:     tool search → handle overflow beyond groups
Execution layer:     programmatic tool calling → keep intermediate results out
Output layer:        formatting strip → reduce response verbosity
Serialization layer: TOON encoding → cut repetitive field names on flat data
Nuclear option:      code execution mode → replace direct tool calls entirely
```

| Technique | Token Reduction | Complexity | Best For |
|---|---|---|---|
| Code execution | ~98% | High | High-scale, privacy-sensitive workflows |
| Tool search | ~85% input | Medium | Agents with 50+ tools |
| Scope/group loading | High | Low | Domain-specific agents |
| Specific tool whitelist | Highest | Low | Locked-down production agents |
| Dynamic context loading | High | Medium | General-purpose agents |
| Programmatic tool calling | High | Medium | Multi-step app-defined workflows |
| Output formatting strip | Moderate | Low | Any tool returning web/doc data |
| TOON encoding | 30-60% output | Low | Tools returning flat tabular data |

---

## The Question to Sit With

**If your agent's context window were a bank account and every token cost real money, would you still load 60 tool definitions before deciding which one to use — or would you build a system that asks first?**

The architecture of your context window is an architecture decision. Right now, most MCP setups make that decision by default — and the default is expensive, inaccurate, and leaky. The techniques above aren't optimizations on a working system. They are corrections to a broken default.
