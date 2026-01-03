# The "Open Door" Paradox: Why Unauthenticated Health Checks Are Industry Standard (And How to Secure Them)

You have deployed your Node.js app on AWS ECS Fargate. You have an Envoy proxy guarding the front door. But there is a nagging worry: you created a `/health` endpoint that bypasses authentication so the load balancer can check it.

Is this a security hole? Did you just leave a window open in your fortress?

## The "What If" Questions for Your Brain

To understand health check security, you must stop thinking about "Authentication" (who are you?) and start thinking about "Network Reachability" (where are you coming from?).

**Imagine this:**
*   **What if** your heart surgeon had to show an ID card every time they checked your pulse? The patient (your app) would die while the surgeon (the load balancer) fumbled for their wallet. Health checks must be fast, lightweight, and unhindered.
*   **What if** the "Open Door" was only visible from the hallway, not the street? If your `/health` endpoint is only accessible from within your AWS VPC (Virtual Private Cloud), does it matter that it doesn't require a password?
*   **Think deeper:** If your health check returns sensitive data (like "Database connected: true, DB_HOST: 10.0.0.5"), you have a problem. But if it just returns `{"status": "ok"}`, what can an attacker actually do with that information?

## The Industry Standard: Unauthenticated but Isolated

The short answer is: **Yes, it is industry standard to have unauthenticated health check endpoints.**

AWS Application Load Balancers (ALB) and ECS Orchestrators do not support signing requests with complex auth tokens easily. They expect a simple `200 OK`.

However, "Unauthenticated" does not mean "Insecure." Here is how the industry secures this:

### 1. Network Isolation (The Real Security)
In ECS Fargate, your containers run in a private subnet. The only thing that can reach them is the Load Balancer and the Envoy proxy.
*   **Security Groups:** Configure your ECS Security Group to **only** allow inbound traffic on the health check port from the **Load Balancer's Security Group**.
*   **Result:** Even if a hacker knows the IP, they cannot reach the port. The door is unlocked, but there is a wall in front of it.

### 2. Envoy Bypass Configuration
Since you are using Envoy, you likely have a configuration that enforces authentication for user traffic. You must explicitly **exclude** the health check path from this policy.

**Common Mistake:** Applying the same auth filter to `/health` as `/api/users`.
**Fix:** In your Envoy config, create a specific route for `/health` that skips the `ext_authz` or JWT filter.

### 3. The "Management Port" Pattern
A best practice (often missed) is to run your health check on a **different port** than your main application traffic.
*   **App Traffic (Port 8080):** Goes through Envoy, requires Auth, logs everything.
*   **Health Traffic (Port 9090):** Direct to Node.js (or a lightweight sidecar), no Auth, no logging (to save disk space).
*   **Why?** This prevents the "noisy neighbor" problem where a flood of user traffic starves the health check, causing a false restart.

## Common Mistakes to Avoid (The "Don'ts")

Based on common Node.js pitfalls, here is what *not* to do:

1.  **The "Deep" Liveness Check:** Do not check your database connection in your **Liveness** probe.
    *   *Scenario:* Your DB slows down.
    *   *Result:* Your Liveness check fails. ECS kills your container. The new container also can't connect. You enter a restart loop.
    *   *Fix:* Liveness should only check "Is the Node.js process running?" (e.g., `return 200`). Use a **Readiness** probe for DB checks.
2.  **Heavy Computation:** Never calculate anything in a health check. It should be a static return. If the event loop is blocked by a heavy calculation, the health check will time out, and your healthy app will be killed.
3.  **Leaking Info:** Never return stack traces, environment variables, or version numbers in the health check body. A simple `{"status": "up"}` is sufficient.

## Final Verdict

Your setup is correct. An unauthenticated `/health` endpoint behind Envoy is standard practice. Your security comes from **Network Layer rules (Security Groups)**, not Application Layer passwords.

**Action Item:**
1.  Ensure your `/health` endpoint returns a simple JSON.
2.  Configure Envoy to bypass auth for this path.
3.  Lock down the Security Group so only the Load Balancer can talk to your ECS tasks.
