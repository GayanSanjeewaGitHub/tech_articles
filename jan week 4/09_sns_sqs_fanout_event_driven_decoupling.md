# Event-Driven Fan-Out: Stop Chaining Services—Start Broadcasting Events

## The Trap: We Think "Notify Multiple Systems" Means "Call Multiple Systems"

When one event needs to trigger multiple downstream actions, the instinct is straightforward: call each system in sequence. Order placed? Call inventory. Call shipping. Call analytics. Call email. Done.

This mental model is borrowed from function calls—synchronous, predictable, debuggable. It feels like control.

The trap is that **sequential notification creates an invisible dependency chain**. Your order service doesn't just process orders anymore—it becomes responsible for the health, speed, and retry logic of four unrelated systems.

---

## The "Stop Time" Moment: Who Owns the Failure?

Imagine this scenario: An e-commerce platform processes thousands of orders daily. Each order must notify four downstream systems:

1. **Inventory management** — reserve stock
2. **Shipping service** — prepare labels
3. **Analytics pipeline** — track metrics
4. **Email service** — send confirmation

Each system processes at different speeds. The email service takes 2 seconds. Analytics takes 50ms. Shipping occasionally times out under load.

**Ask yourself: Where does the failure live?**

If your order service calls these systems directly:
- One slow system blocks the entire order response
- One failed system means the order service must handle retries
- One crashed system means customers see errors for unrelated functionality

**What is being wasted here?**

- **Latency budget**: Your order response waits for the slowest downstream system.
- **Availability**: Your order service's uptime becomes the *product* of all downstream uptimes.
- **Cognitive load**: Your order service code now contains retry logic for systems it shouldn't know exist.

The invisible mechanic is this: **tight coupling doesn't just create dependencies—it transfers ownership of failure to the wrong component**.

---

## The Mental Model Shift: From "Caller" to "Publisher"

Stop thinking: "My service calls downstream services."

Start thinking: "My service publishes events. Consumers decide what to do."

### Thinking Shifts

- **From "call four systems" → "publish one event"**
- **From "caller handles retries" → "each consumer handles its own retries"**
- **From "slowest system determines latency" → "fire-and-forget with buffered delivery"**
- **From "shared fate" → "isolated failure domains"**

The order service's job is to record the order and announce it happened. Period. What downstream systems do with that announcement is not the order service's concern.

---

## The "What If" Scenarios: How Naive Approaches Break

### 1) Direct Invocation (The Tight Coupling Trap)

You configure the order service to invoke four Lambda functions directly—one for each downstream system.

**What breaks:** If the email Lambda is slow, the order API response is slow. If shipping Lambda fails, the order service must decide: retry? fail the order? ignore? Your order service is now tightly coupled to systems it shouldn't know about. One slow Lambda blocks the customer's checkout experience.

### 2) Single Shared Queue (The Competition Problem)

You create one SQS queue that all four systems poll for new order messages.

**What breaks:** SQS delivers each message to *one* consumer only. Four consumers polling the same queue means each order goes to one system, not all four. Inventory gets the message; shipping, analytics, and email get nothing.

It's like having one parking spot for four cars. Three cars don't park.

### 3) Database Polling (The Scaling Anti-Pattern)

Each downstream system polls the orders database table for new records every minute.

**What breaks:** 
- Database load scales with number of consumers × poll frequency
- One-minute polling means up to 60 seconds of latency
- All systems are tightly coupled to your database schema
- Schema changes break all consumers simultaneously

You've turned your database into a message queue it was never designed to be.

---

## The Architecture: SNS + SQS Fan-Out

The pattern that solves this is **publish-subscribe with buffered consumers**:

```
Order Service
     │
     ▼
  SNS Topic (broadcast)
     │
     ├──► SQS Queue → Inventory Service
     ├──► SQS Queue → Shipping Service  
     ├──► SQS Queue → Analytics Pipeline
     └──► SQS Queue → Email Service
```

### How It Works

1. **Order service publishes once** — A single message to an SNS topic. The order service doesn't know (or care) how many subscribers exist.

2. **SNS broadcasts instantly** — The topic delivers the message to all subscribers simultaneously. One-to-many fan-out.

3. **Each consumer has its own queue** — Messages land in dedicated SQS queues. Each system processes at its own speed.

4. **Failure isolation** — If the email service crashes, messages wait in its queue. Inventory, shipping, and analytics continue unaffected. When email recovers, it processes the backlog.

### Why This Works

| Concern | Direct Invocation | SNS + SQS Fan-Out |
|---------|-------------------|-------------------|
| Latency | Slowest consumer | Fire-and-forget |
| Failure handling | Caller's responsibility | Each consumer's queue |
| Adding consumers | Change order service code | Subscribe to topic |
| Consumer speed differences | Blocks others | Independent processing |
| Retry logic | Centralized (wrong place) | Per-consumer (right place) |

---

## The Principle to Keep

**Decoupling is not about avoiding communication—it's about making the publisher ignorant of consumers.**

The order service publishes an event: "Order 12345 was placed." It returns immediately. It doesn't know if there are 4 consumers or 40. It doesn't know if analytics is fast and email is slow. It doesn't handle retries for systems it didn't design.

Each consumer owns its queue, its processing speed, its retry policy, its failure recovery.

---

## When to Reach for This Pattern

The SNS + SQS fan-out pattern fits when you see:

- **One event, multiple consumers** — Fan-out is the signal
- **Independent processing speeds** — Consumers shouldn't wait for each other
- **Resilience requirement** — One consumer's failure shouldn't affect others
- **Loose coupling mandate** — Publisher shouldn't know consumer details

---

## Closing Challenge

The next time you're about to write code that calls multiple downstream services from one event, pause. Ask:

- What happens if one of these calls is slow?
- What happens if one of these services is down?
- Who should own the retry logic?
- Does my service really need to know these consumers exist?

If the answers make you uncomfortable, the path forward is clear: **stop calling services—start publishing events**.
