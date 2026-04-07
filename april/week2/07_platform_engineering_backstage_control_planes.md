# Platform Engineering: Why Backstage Isn't a Platform and Golden Paths Need Control Planes

## 5 Intuitive Takeaways

1. **Product mindset for internal platforms means treating developers as customers, not captive users** — most organizations have strong product skills for external customers but never apply them internally. The result: platforms built under time pressure that "get things done" but create terrible developer experiences. Without product thinking (hypotheses, success criteria, user feedback loops), platforms become maintenance burdens that nobody wants to use.

2. **Backstage is a portal, not a platform — and confusing the two is the #1 anti-pattern** — teams adopt Backstage thinking it IS the platform, then stuff all business logic into plugins. Backstage was designed as a UI touchpoint, not an execution engine. Without proper APIs, control planes, and domain boundaries behind it, Backstage becomes a "crap magnet" — a pretty frontend hiding architectural chaos that gets exponentially harder to fix at scale.

3. **Control planes built on the Kubernetes API give you a battle-tested reconciliation loop for free** — instead of building custom health-checking, drift-detection, and self-healing logic from scratch, you extend Kubernetes' declarative reconciliation model (desired state → observe → correct). Users don't even need to know it's Kubernetes underneath — they just get resilient, self-healing infrastructure through a clean API boundary.

4. **If your platform team owns the pipelines, you've already failed** — pipelines are developer concerns, not platform concerns. The moment platform engineers maintain application CI/CD pipelines, you've recreated the ops silo you were trying to eliminate. The platform provides the golden path (standardized APIs, guardrails, self-service), but teams own their own delivery pipelines. This is the single highest-leverage boundary to get right.

5. **Vibe-coding infrastructure with AI is a nightmare without tests and domain boundaries** — 9 out of 10 developers now use AI for infrastructure file generation, but AI doesn't know if what it generated is resilient, secure, or scalable. If you can't write the tests that validate the generated infrastructure, and you don't have clean domain boundaries (separate SDLC for control plane vs. workloads vs. service mesh), AI will amplify every architectural mistake at speed. The rule: if a human doing what AI just did would get fired, don't accept it from AI either.
