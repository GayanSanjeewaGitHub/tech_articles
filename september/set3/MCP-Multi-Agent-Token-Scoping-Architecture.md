# Multi-Agent MCP Authorization — Scoping Tools Per User, Per Sub-Agent Call

## The problem

An orchestrator agent authenticates a user once, then fans out to sub-agents that each expose an MCP server with multiple tools. Some tools are read-only, some are writes. A given logged-in user (say, a non-admin) is only entitled to a subset of a sub-agent's tools (5 of 10). The question: **where does that per-tool authorization decision live, and how does it get from the orchestrator down to the sub-agent/tool-call boundary — without stuffing the whole permission matrix into the login JWT?**

The instinct in the prompt — *"maybe I make another call to get a temporary token that includes what I can access"* — is exactly the pattern the industry has converged on. It has names: **Token Exchange (RFC 8693)**, **downscoping / delegation tokens**, and (Okta's specific implementation of it) **ID-JAG (Identity Assertion JWT Authorization Grant)**. AWS/industry blogs call the service that issues these on demand a **Token Vending Machine (TVM)**.

---

## Why not just put everything in the JWT

- A login JWT is long-lived-ish and travels with every request — bloating it with a full permission matrix means re-minting/re-signing it every time a role or ACL changes, and it leaks the *entire* entitlement surface to every service that sees the token (over-exposure).
- MCP tool grants are **per-resource** (audience-bound) and often **short-lived / per-task** — that doesn't fit a session-lifetime identity token.
- Industry consensus (Okta, Microsoft Entra Agent ID, SuperTokens, GitGuardian's MCP auth writeups): keep the primary identity token **thin** (who + tenant/org + coarse role), and mint a **separate, short-lived, audience-scoped delegation token** per hop, per target resource — evaluated fresh against a policy store each time, not decoded client-side from a fat JWT.

---

## The architecture (bird's-eye)

```
 ┌──────────┐     ┌──────────────┐     ┌────────────────────┐     ┌───────────────┐
 │  User /   │────▶│  API Gateway  │────▶│  Orchestrator Agent │────▶│  Sub-Agent(s)  │
 │  Client   │     │ (JWT verify)  │     │   (intent router)   │     │  + MCP Server  │
 └──────────┘     └──────────────┘     └──────────┬──────────┘     └───────────────┘
                                                    │
                                                    ▼
                                    ┌───────────────────────────────┐
                                    │  Authorization Server (PDP)     │
                                    │  = "Token Vending Machine"      │
                                    │  Token Exchange (RFC 8693)      │
                                    │  + Policy Store (OPA/Cedar/     │
                                    │    Entra/Okta policy engine)    │
                                    └───────────────────────────────┘
```

Key rule: **the orchestrator never decides authorization itself.** It asks the Authorization Server "for user X, calling sub-agent Y, what am I allowed to do?" — every single time it's about to cross a trust boundary. The sub-agent's MCP server *also* re-checks the token independently (defense in depth) instead of trusting the orchestrator's word.

---

## Granular sequence diagram

```
 USER/CLIENT      API GATEWAY        IDP (Okta/         ORCHESTRATOR        AUTH SERVER / PDP        SUB-AGENT 1          MCP TOOL SERVER
                                       Entra)              AGENT           ("Token Vending           (LLM runtime)         (10 tools registered,
                                                                             Machine" + Policy                              5 = read, 5 = write)
                                                                             Store)
     │                 │                  │                  │                    │                      │                       │
     │ 1. Login         │                  │                  │                    │                      │                       │
     ├────────────────▶│                  │                  │                    │                      │                       │
     │                 │ 2. Redirect to    │                  │                    │                      │                       │
     │                 │    IdP (OIDC)     │                  │                    │                      │                       │
     │                 ├─────────────────▶│                  │                    │                      │                       │
     │                 │                  │ 3. Authenticate   │                    │                      │                       │
     │                 │                  │    user, issue    │                    │                      │                       │
     │                 │                  │    THIN id_token  │                    │                      │                       │
     │                 │                  │    {sub, org_id,  │                    │                      │                       │
     │                 │                  │     role:"member"}│                    │                      │                       │
     │                 │◀─────────────────┤                  │                    │                      │                       │
     │ 4. id_token       │                  │                  │                    │                      │                       │
     │◀────────────────┤                  │                  │                    │                      │                       │
     │                 │                  │                  │                    │                      │                       │
     │ 5. Query +        │                  │                  │                    │                      │                       │
     │    Bearer token   │                  │                  │                    │                      │                       │
     ├────────────────▶│                  │                  │                    │                      │                       │
     │                 │ 6. Verify JWT     │                  │                    │                      │                       │
     │                 │    signature only │                  │                    │                      │                       │
     │                 │    (identity, NOT │                  │                    │                      │                       │
     │                 │     permissions)  │                  │                    │                      │                       │
     │                 │ 7. Forward request │                  │                    │                      │                       │
     │                 │    + id_token      │                  │                    │                      │                       │
     │                 ├──────────────────────────────────▶│                    │                      │                       │
     │                 │                  │                  │ 8. Parse intent:    │                      │                       │
     │                 │                  │                  │    needs Sub-Agent-1 │                      │                       │
     │                 │                  │                  │    "org_reports"     │                      │                       │
     │                 │                  │                  │                    │                      │                       │
     │                 │                  │                  │ 9. TOKEN EXCHANGE   │                      │                       │
     │                 │                  │                  │    request (RFC 8693)│                      │                       │
     │                 │                  │                  │    subject_token=id_token                  │                       │
     │                 │                  │                  │    audience=sub-agent-1-mcp                │                       │
     │                 │                  │                  │    requested_scope="tools:*"                │                       │
     │                 │                  │                  ├────────────────────▶│                      │                       │
     │                 │                  │                  │                    │ 10. Look up user's    │                       │
     │                 │                  │                  │                    │     entitlements:      │                       │
     │                 │                  │                  │                    │     org_id + role +     │                       │
     │                 │                  │                  │                    │     resource=sub-agent-1│                       │
     │                 │                  │                  │                    │     against Policy Store│                       │
     │                 │                  │                  │                    │     (RBAC/ABAC rules,   │                       │
     │                 │                  │                  │                    │      e.g. OPA/Cedar)    │                       │
     │                 │                  │                  │                    │                      │                       │
     │                 │                  │                  │                    │ 11. Decision:          │                       │
     │                 │                  │                  │                    │     role="member" =>   │                       │
     │                 │                  │                  │                    │     allow 5 of 10 tools │                       │
     │                 │                  │                  │                    │     (read_* only, no    │                       │
     │                 │                  │                  │                    │      write_* tools)     │                       │
     │                 │                  │                  │                    │                      │                       │
     │                 │                  │                  │                    │ 12. Mint DELEGATION    │                       │
     │                 │                  │                  │                    │     TOKEN (short-lived, │                       │
     │                 │                  │                  │                    │     e.g. Okta ID-JAG    │                       │
     │                 │                  │                  │                    │     style):             │                       │
     │                 │                  │                  │                    │     {aud: sub-agent-1,  │                       │
     │                 │                  │                  │                    │      sub: user_id,      │                       │
     │                 │                  │                  │                    │      scope: "read_tbl,  │                       │
     │                 │                  │                  │                    │       read_summary,     │                       │
     │                 │                  │                  │                    │       read_export,      │                       │
     │                 │                  │                  │                    │       read_status,      │                       │
     │                 │                  │                  │                    │       read_metrics",    │                       │
     │                 │                  │                  │                    │      exp: now+60s,      │                       │
     │                 │                  │                  │                    │      jti: one-time-use} │                       │
     │                 │                  │                  │◀────────────────────┤                      │                       │
     │                 │                  │                  │ 13. delegation_token │                      │                       │
     │                 │                  │                  │     (NOT the user's  │                      │                       │
     │                 │                  │                  │      original id_token)                    │                       │
     │                 │                  │                  │                    │                      │                       │
     │                 │                  │                  │ 14. Invoke sub-agent │                      │                       │
     │                 │                  │                  │     + delegation_token│                      │                       │
     │                 │                  │                  ├─────────────────────────────────────────▶│                       │
     │                 │                  │                  │                    │                      │ 15. tools/list request │
     │                 │                  │                  │                    │                      │     + delegation_token  │
     │                 │                  │                  │                    │                      ├──────────────────────▶│
     │                 │                  │                  │                    │                      │                       │ 16. PEP: validate token
     │                 │                  │                  │                    │                      │                       │     sig + aud + exp +
     │                 │                  │                  │                    │                      │                       │     jti (replay check)
     │                 │                  │                  │                    │                      │                       │ 17. FILTER: return only
     │                 │                  │                  │                    │                      │                       │     the 5 tools whose
     │                 │                  │                  │                    │                      │                       │     names are in the
     │                 │                  │                  │                    │                      │                       │     token's scope claim
     │                 │                  │                  │                    │                      │◀──────────────────────┤
     │                 │                  │                  │                    │                      │ 18. tools/list = [5    │
     │                 │                  │                  │                    │                      │     tools] — model     │
     │                 │                  │                  │                    │                      │     never even sees the │
     │                 │                  │                  │                    │                      │     5 write tools exist │
     │                 │                  │                  │                    │                      │                       │
     │                 │                  │                  │                    │                      │ 19. LLM picks a tool,   │
     │                 │                  │                  │                    │                      │     tools/call          │
     │                 │                  │                  │                    │                      │     + same delegation   │
     │                 │                  │                  │                    │                      │     token               │
     │                 │                  │                  │                    │                      ├──────────────────────▶│
     │                 │                  │                  │                    │                      │                       │ 20. PEP re-checks scope
     │                 │                  │                  │                    │                      │                       │     AGAIN on the actual
     │                 │                  │                  │                    │                      │                       │     call (never trust the
     │                 │                  │                  │                    │                      │                       │     earlier tools/list
     │                 │                  │                  │                    │                      │                       │     filtering alone)
     │                 │                  │                  │                    │                      │                       │ 21a. In scope → execute
     │                 │                  │                  │                    │                      │                       │ 21b. Out of scope → 403,
     │                 │                  │                  │                    │                      │                       │      even if the model
     │                 │                  │                  │                    │                      │                       │      "guessed" a write
     │                 │                  │                  │                    │                      │                       │      tool name
     │                 │                  │                  │                    │                      │◀──────────────────────┤
     │                 │                  │                  │◀─────────────────────────────────────────┤ 22. result              │
     │                 │                  │                  │                    │                      │                       │
     │◀───────────────┤◀──────────────────────────────────┤                    │                      │                       │
     │ 23. Final answer  │                  │                  │                    │                      │                       │
     │                 │                  │                  │                    │                      │                       │
     │                 │                  │                  │ 24. delegation_token expires (60s) / is    │                      │                       │
     │                 │                  │                  │     one-time-use — discarded, not cached   │                      │                       │
     │                 │                  │                  │     beyond this run                       │                      │                       │
```

---

## Answering the specific sub-questions

**"Do I need to make a call to another server to get a temporary user-agent token that says what I can access?"**
Yes — that's step 9–13 above. This is a standard **OAuth 2.0 Token Exchange (RFC 8693)** call from the orchestrator to an Authorization Server, requesting a token **downscoped** to one specific downstream resource (`audience = sub-agent-1`). Don't reuse one token across multiple sub-agents — each sub-agent/MCP server is a distinct `audience` (RFC 8707 Resource Indicators), so a request touching 3 sub-agents does 3 scoped token-exchange calls (or one batched call that returns per-audience tokens, if your PDP supports it).

**Where does the "5 of 10 tools" filtering actually happen?**
Twice, redundantly, by design:
1. **Soft filter at `tools/list`** (step 17) — so the LLM's context window only ever contains the 5 permitted tool schemas. This also directly solves the "too many tools bloats context" problem from your earlier question — permission scoping and context hygiene collapse into the same mechanism.
2. **Hard enforcement at `tools/call`** (step 20) — the MCP server's Policy Enforcement Point (PEP) checks the token's scope claim on the *actual* invocation, independent of what the `tools/list` response said. This matters because a model can hallucinate or be prompt-injected into calling a tool name it was never shown.

**Is per-call token exchange too slow?**
Cache the delegation token for the lifetime of one orchestration run (a few seconds to a couple minutes), keyed by `(user_id, audience)`. Don't cache it session-long — permissions can change mid-session (e.g., admin revokes a role), and a short TTL + `jti` replay-guard is what keeps this "zero standing privilege" instead of "long-lived god token."

**Isn't this what RBAC roles in the JWT are for?**
Coarse RBAC roles (`admin`/`member`) are fine to keep in the *identity* JWT as a hint, but the actual tool-level grant should still be resolved against a live Policy Store per call — because real deployments need per-org, per-resource, sometimes per-record exceptions (ABAC-style) that a static role string can't express, and because propagating a broad role blindly through every orchestrator → sub-agent hop is exactly the lateral-movement risk flagged in current AI-agent security writeups (a compromised sub-agent inherits the full ambient role instead of only what that one call needed).

---

## Named patterns to search for / adopt

| Concept | What it is |
|---|---|
| **OAuth 2.0 Token Exchange** (RFC 8693) | The standard grant type for "exchange this token for a narrower one scoped to a different audience." This is the mechanism behind step 9–13. |
| **Resource Indicators** (RFC 8707) | Binds a token to one specific `audience` (one MCP server), so a stolen/leaked token for Sub-Agent-1 is useless against Sub-Agent-2. |
| **Token Vending Machine (TVM)** | Industry nickname (AWS-popularized) for a service whose whole job is "mint short-lived, narrowly-scoped credentials on demand" — this is your Authorization Server box. |
| **ID-JAG (Identity Assertion JWT Authorization Grant)** | Okta's concrete implementation of a short-lived, one-time-use, downscoped delegation token for exactly this agent-to-agent handoff case. |
| **PDP / PEP** (Policy Decision Point / Policy Enforcement Point) | PDP = the Authorization Server evaluating policy once; PEP = each MCP server re-checking the resulting token on every call. Never collapse these into one trust hop. |
| **MCP Authorization spec** (OAuth 2.1 + Protected Resource Metadata) | The MCP spec itself now expects MCP servers to publish where their authorization server is, and expects clients to send resource-bound tokens — this whole architecture is what the spec is designed to carry. |

---

## Follow-up Q&A

**What exactly is the "Token Exchange (RFC 8693)" request?**
A concrete OAuth grant type — the orchestrator does `POST /token` with `grant_type=token-exchange`, `subject_token=<user's id_token>`, `audience=<sub-agent-1>`. The Authorization Server responds with a new token scoped to just that audience. It's a named IETF standard, not a custom/home-grown flow.

**What is the PDP, and is the policy registry just a database keyed by role?**
PDP = **Policy Decision Point**, the piece that evaluates "is this allowed?" — often a library/sidecar (OPA, Cedar) called by the Authorization Server, not necessarily its own server. And yes: the policy registry is typically a table mapping `role → allowed tools/scopes` (e.g., `member → [read_*]`, `admin → [read_*, write_*]`), stored separately from the IdP.

**Doesn't storing roles in two places (IdP and Policy Store) cause drift?**
Only if you duplicate the *assignment*. Correct split: the **IdP is the single source of truth for "what role does this user have"** (`role: "member"` in the id_token). The **Policy Store only hardcodes `role → permissions` mappings**, never a copy of who has which role — it looks up the user's role from the id_token fresh on every evaluation. Nothing to drift because the role assignment itself is never duplicated.

**What happens when a role is added or removed?**
Nothing needs to happen anywhere except the Policy Store's mapping table — no token revocation, no redeploy, no touching the IdP.
- *Add a role*: insert one new `role → permissions` row; start assigning that role string to users in the IdP. Effective on the next token-exchange call.
- *Remove a role*: delete/disable that mapping row. Any user still tagged with the old role in the IdP now gets a lookup miss — the Policy Store must **fail closed** (return zero scopes) on an unknown/removed role, never fail open.
- Because nothing is cached beyond one short-lived (~60s) delegation token, the maximum staleness after any role change is one token lifetime — no revocation/blacklist infrastructure needed, unlike baking permissions into a long-lived JWT.

**What does ID-JAG mean?**
**Identity Assertion JWT Authorization Grant** — Okta's spec-based token type for this exact handoff: the IdP asserts a user's identity + scope to another app/service without re-prompting the user. It's the concrete token format behind the "delegation token" minted in step 12.

**How is `jti: one-time-use` actually enforced — do we just increment a counter?**
No. `jti` is a random unique ID per token, not a counter. Enforcement = a replay cache (e.g., Redis) records every `jti` accepted, with TTL equal to the token's expiry. On each use, check "have I seen this `jti`?" — reject if yes. Entries age out naturally once the token itself expires.

**What does "PEP" mean?**
**Policy Enforcement Point** — the component that actually enforces the PDP's decision at the moment of use (here: the MCP server checking the token on `tools/call`). PDP decides once; PEP enforces on every call, even if they run in the same process.

**If tools are hardcoded in the MCP server's code, isn't per-role filtering hard to maintain?**
Yes — hardcoded `if tool_name == "write_x": ...` branches scattered through the code drift and are hard to audit. Fix: each tool declares its **required scope as metadata** in a registry/manifest (`{name: "write_x", scope: "write_x"}`), and one generic middleware checks `token.scopes contains tool.scope` uniformly for every tool. Adding a tool then only means declaring its scope — no filtering-logic changes.

**Once the short-lived, one-time token is handed to the sub-agent, is checking Redis for reuse the sub-agent's job, or the MCP server's?**
The **MCP server's** — it's the PEP/resource server. The sub-agent is only a *bearer* of the token: it attaches it to `tools/list`/`tools/call` requests but never validates it. It can't be trusted to self-police, because the sub-agent is LLM-driven and can be prompt-injected or otherwise compromised — if replay-protection lived there, a hijacked sub-agent could just skip its own check. Security only holds if **whoever executes the privileged action** (the MCP server) is the one doing the `jti` Redis lookup, signature check, audience check, and expiry check — every time, on every call.

---

## Sources

- [OAuth for MCP — Emerging Enterprise Patterns for Agent Authorization (GitGuardian)](https://blog.gitguardian.com/oauth-for-mcp-emerging-enterprise-patterns-for-agent-authorization/)
- [Multi-User AI Agent Auth: OAuth & MCP Guide (Arcade.dev)](https://www.arcade.dev/blog/ai-agent-authentication-authorization/)
- [MCP, OAuth 2.1, PKCE, and the Future of AI Authorization (Aembit)](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/)
- [How to secure AI agents in the enterprise — ID-JAG (Okta)](https://www.okta.com/blog/ai/okta-securing-ai-agent-identity/)
- [Least privilege for AI agents with Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/security/zero-trust/sfi/least-privilege-for-ai-agents)
- [Secure AI agents with scoped tokens, DPoP, tool-level policies (SuperTokens)](https://supertokens.com/blog/auth-for-ai-agents)
- [RBAC Is Not Enough for AI Agents: A Practical Authorization Model](https://tianpan.co/blog/2026-04-20-rbac-ai-agents-authorization)
- [Multi-user Authorization — MCP spec discussion #234](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/234)
