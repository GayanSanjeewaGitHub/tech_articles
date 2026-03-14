# The Physics of GraphQL Federation: Why Unified APIs Are About Ownership, Not Schema Merging

## The Trap

We think GraphQL Federation is about taking multiple schemas and merging them into one big schema. Copy-paste three files together, resolve a few naming conflicts, and you have a "unified API."

This is schema stitching. It is the old way. And it collapses under its own weight the moment your team grows beyond a handful of engineers.

The real trap is subtler: we confuse **aggregation** with **composition**. Aggregation glues things together at the surface. Composition defines clear ownership boundaries and lets a system assemble itself at query time. One scales to three services. The other scales to three hundred.

## The "Stop Time" Moment

Imagine this scenario: You have three microservices — Users, Movies, and Reviews. A review has an author (a user) and a subject (a movie). The review service needs user data and movie data to return a complete response.

**Ask yourself: Who should fetch the user's name?**

- Should the review service call the user service directly via HTTP? Now you have service-to-service coupling. Every deployment of the user service risks breaking the review service.
- Should they share a database? Now you have data coupling. Schema migrations become coordination nightmares across teams.
- Should you duplicate user data into the review service? Now you have consistency problems. Which copy is the truth?

**What is being wasted here?** Engineering time. Every "integration" meeting, every shared library version bump, every cross-team deployment freeze — all of it is the tax you pay for coupling that should never have existed.

## The Mental Model Shift

> **Stop thinking of services as API providers that call each other. Start thinking of services as owners of entity slices that a router assembles at query time.**

In a federated architecture, no service calls another service. Services do not even know other services exist. Each service owns a **subgraph** — a slice of the total schema. These subgraphs compose into a **supergraph**: the unified API that clients actually see.

**Thinking Shifts:**

- **From "Services call services"** → **To "Services declare identity; a router resolves references."** The review service does not fetch user data. It returns a lightweight pointer: *"This review was written by User 2."* The router sees that pointer and knows where to resolve it.
- **From "Merge schemas"** → **To "Declare ownership boundaries."** Each subgraph decides three things: what data it owns, how its entities are identified (the `@key` directive), and what it exposes to the supergraph. Nothing more.
- **From "Shared libraries for coordination"** → **To "Shared contract through entity identity."** The `@key` directive is a contract — like a primary key, but at the API layer instead of the database layer. Any service can reference a User by ID without importing a single line of code from the user service.

## The "What If" Scenarios

**Scenario 1: The Deployment Freeze.** Without federation, the review team cannot ship a new field without coordinating with the user team and the movie team. Why? Because their schemas are entangled. One team's deploy can break another team's types. Federation eliminates this. Each subgraph is independently deployable. The users team ships on Monday. The movies team ships on Wednesday. They never step on each other's code. **This is not just a technical pattern — it is an organizational pattern.** It is why federation scales at companies serving billions of requests.

**Scenario 2: The Entity Extension Trap.** You want to add a `reviews` field to the User type. In a monolithic schema, the review team would need write access to the user schema file. In federation, the review subgraph simply *extends* the User entity with its own field. It declares the same `@key`, adds `reviews`, and provides the resolver. The user subgraph never changes. **Ownership boundaries are enforced by the schema itself**, not by team agreements or code review policies.

**Scenario 3: The N+1 Query Avalanche.** A client queries all users with their reviews and each review's movie details. Without a query planner, this fans out into dozens of redundant calls. The federated router handles **query planning** — it determines which subgraphs to call, in what order, and how to batch requests. It performs **late binding**: resolving entity references only when the client actually requests those fields. The client sends one query. It gets one response. It never sees the subgraphs.

## The Architecture

The system that emerges has four interlocking components:

1. **Subgraphs with `@key` Directives:** Each service declares its entity's identity. User is identified by `id`. Movie is identified by `id`. This is the federation contract — the only coordination point between services.

2. **Entity References (Lightweight Pointers):** When the review service returns an author, it does not fetch user data. It returns `{ __typename: "User", id: "2" }`. Just the type name and the key. Nothing more.

3. **`__resolveReference` Functions:** When the router receives an entity reference, it forwards it to the owning subgraph. The user subgraph's `__resolveReference` takes `{ id: "2" }` and returns the full user object. No HTTP calls between services. No shared databases. Just identity resolution.

4. **The Router (Query Planner + Orchestrator):** Written in Rust for raw throughput, the router composes all subgraph schemas into one supergraph. At query time, it plans execution — which subgraphs to call, in what sequence — and stitches all responses into one clean result. The client sees one graph, one endpoint, one API.

## The Deeper Question

The next time you design a multi-service API, ask yourself:

**Are your services communicating with each other, or are they declaring ownership and letting a smarter layer resolve the relationships?**

Direct service-to-service communication is the distributed equivalent of tight coupling in a monolith. Federation replaces it with something more powerful: **identity-based composition**, where services stay decoupled and a router assembles reality at query time.

*Hint: This ownership model extends beyond APIs. Think about event-driven systems, data mesh architectures, and platform engineering. How many of your integration problems are actually ownership problems in disguise?*
