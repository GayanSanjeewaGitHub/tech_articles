# AI Agents Ship Fast and Break Everything: Why Your Codebase Needs Friction

## The Problem: Months of Technical Debt in Days

Your team adopted AI coding agents. Output tripled. Pull requests got bigger. Reviews got skipped. Then production broke — and the engineer who committed the faulty code didn't even recognize it as their own.

- **Agents optimize for "code that runs," not "code that's correct"** — reinforcement learning rewards making progress, not making good decisions
- **Review capacity hasn't scaled with creation capacity** — every engineer now produces 3–5x more code, but reviews at the same speed
- **Non-engineers are shipping code** — marketing, former-CEOs-turned-coders, anyone with a prompt. Responsibility still rests with the engineering team
- **Codebases are growing past the agent's own comprehension** — the agent creates entropy, then can't read the codebase it created. It duplicates code, misses files, adds state that shouldn't exist
- **Silent failure modes multiply** — agents write fallback-to-defaults patterns that hobble along instead of failing loudly. You discover the config was never loaded after two hours of writing bad database records

## Why This Happens

- **Agents don't feel bad about bad code.** Humans develop an emotional signal — discomfort — when writing brittle workarounds. Agents have no such friction. They silently create recovery paths around local failures, building systems that appear to work but are fundamentally fragile
- **Speed creates the illusion of productivity.** High output volume tricks both individuals and teams into believing they're being more efficient, when they're actually skipping the design thinking that prevents rework
- **Context windows can't hold product complexity.** Libraries work well — tight constraints, clear APIs, simple cores. Products don't — UI, permissions, feature flags, billing, all intertwined. **The agent is locally reasonable but globally incoherent**
- **The addictive loop:** You never know if the next prompt will nail the feature or be the last drop of slop that crashes production. So you keep prompting

**Ask yourself:** If your team is producing 5x more code but reviewing at the same rate, who is carrying the responsibility for the 4x that goes unreviewed?

## The Mental Model Shift

> **Stop treating friction as the enemy. Start treating it as your steering mechanism.**

- **Old:** Friction in shipping = waste to eliminate
- **New:** Friction = where human judgment inserts itself. Without it, there's no steering
- **Old:** More code output = more productivity
- **New:** More output without proportional review = accelerated technical debt
- **Old:** The agent handles implementation, I handle direction
- **New:** The agent optimizes for local progress. **You** must enforce global coherence

## What Happens If You Ignore This

- **Config fallback disaster:** Agent writes "read config, fall back to defaults on failure." No one notices the config never loaded. Two hours of database writes with wrong data before anyone realizes
- **The 5,000-line PR:** Agent generates a massive change. It's overwhelming to review. It gets rubber-stamped. A hidden permission change ships to production — underdocumented, untested against real access patterns
- **Codebase entropy spiral:** Agent creates a new utility file for something that already exists elsewhere. Next session, it creates another. Within weeks, the codebase has 3 implementations of the same logic, inconsistent behavior, and no human fully understands the structure

## The Approach: Agent-Legible Codebases + Mechanical Enforcement

Design your codebase as infrastructure the agent can navigate — and enforce rules it can't break:

- **Modularize code flow, not just components** — define clear steps (receive input → process → output) so the agent can't add fuzz between stages
- **No bare catch blocks** — enforce via linting. Agents love catch-all error handling; it's how they unblock themselves. It's also how failures go silent
- **One query interface for database access** — if the agent has to hunt across files, it will miss one. That missed one becomes a breaking change
- **One primitives/components library** — no raw input boxes, no ad-hoc styling. Consistent behavior the agent can't deviate from
- **Unique function names** — better grep results = fewer tokens wasted = agent finds the right code faster
- **No dynamic imports, no ORMs hiding intent** — if the agent can't see it, it can't respect it

## The Solution: Separate Machine-Fixable from Human-Required

| Review Category | Who Acts | Examples |
|---|---|---|
| **Mechanical bugs** | Agent fixes automatically | Lint violations, type errors, CLAUDE.md rule breaks |
| **Human judgment required** | Engineer must engage | Database migrations (lock implications, data size), permission changes, new dependencies, architectural decisions |

The key insight: **build tooling that wakes the human up at the right moment.** Not for everything — that's unsustainable. But for the specific categories where missing it means regretting it:

- Database migrations → human reviews lock behavior against production data size
- Permission changes → human verifies against actual access patterns
- New dependencies → human evaluates maintainer trust, license, attack surface
- Architectural boundaries → human ensures global coherence the agent can't see

## The Question to Sit With

SLOs were intentionally designed to add friction — to force engineers to ask "do I need this reliability? Am I staffed to run this?" We accepted that friction because the cost of skipping it was obvious. **AI agents just removed the friction from code creation without removing the consequences of shipping bad code.** If you're producing months of technical debt in days, at what point does the speed stop being a feature and start being the failure mode?
