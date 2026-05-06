# Why JWTs Break Authorization: The Irrevocable Token Problem

## The Problem: You Revoke Access, but the Token Doesn't Know

You remove a user from your organization. Their JWT still contains `"role": "admin"` in the scope. Until that token expires, **they still have full access**. You have no meaningful way to revoke it.

- **JWTs are self-contained and stateless** — once issued, no central authority validates reality
- **Scopes become stale** — the token says "admin" but reality says "removed 10 minutes ago"
- **No revocation mechanism by design** — the token is the proof, and there's nothing to check it against
- **100% of apps tested by OWASP had broken access control** — this is the #1 web app risk

## Why This Happens

- **The "new enemy" problem** (described in Google's Zanzibar paper, 2019): a formerly trusted user retains access because the token outlives the permission change
- **JWTs were designed for data exchange**, not authorization. The `scope` field isn't even in the original JWT spec — it's borrowed from the OAuth 2 Token Exchange spec
- **Coarse-grained roles don't fit modern systems** — `"scope": "admin"` tells you nothing about which resources, which actions, which boundaries

**If your distributed system has 10 microservices and a JWT is created at the entry point, can you predict every permission decision it will authorize downstream?**

## The Mental Model Shift

> **Stop asking "what does this token say?" Start asking "what does the system say right now?"**

- **Old:** Token carries permissions → services trust the token → no verification at decision time
- **New:** Token carries identity → services ask a central authority → decision reflects current reality
- **Old:** RBAC role = access to everything in that role
- **New:** Fine-grained: can *this user* do *this action* on *this resource* — checked at query time

## Real Consequences

- **Revoked admin still has access:** User removed from org at 2:00 PM. JWT expires at 2:30 PM. For 30 minutes, they read, modify, or delete data they shouldn't touch
- **Token explosion:** Fine-grained permissions require dozens of scopes. JWT payload grows. Stack Overflow fills with "how do I fit 50 scopes in a token?"
- **Privilege escalation downstream:** JWT created with broad scope at API gateway. Microservice 4 hops later uses the same token to authorize a write it was never intended to permit

## The Solution: Centralized Authorization at Decision Time

Two modern approaches:

**1. Relationship-Based Access Control (ReBAC) — Zanzibar model:**
- Every permission is a relationship: `user:alice` → `editor` → `doc:budget`
- Checking access = graph traversal
- Implementations: SpiceDB, OpenFGA, Ory Keto, Permify

**2. Policy Decision Points (PDP):**
- Authorization as logic evaluation: policy + context → yes/no
- Implementations: OPA (Open Policy Agent), Cedar, Cerbos

| Aspect | JWT-Based AuthZ | Centralized AuthZ |
|---|---|---|
| State | Stale from the moment of issuance | Real-time system state |
| Revocation | Impossible without infrastructure hacks | Immediate |
| Granularity | Coarse roles crammed into scope | Per-resource, per-action |
| Downstream control | Token over-scoped for safety | Decision made at each service |
| Complexity | Simple to implement | Requires architectural investment |

**JWTs are still fine for:** email verification links, short-lived one-time tokens, authentication (identity). **They are not fine for:** long-lived sessions, app authorization decisions, fine-grained permissions.

## The Question to Sit With

Your JWT says `"role": "admin"`. The user was removed from the organization 5 minutes ago. **Who in your system knows reality — the token, or the authorization service you haven't built yet?**
