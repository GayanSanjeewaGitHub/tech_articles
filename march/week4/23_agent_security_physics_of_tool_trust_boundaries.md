# The Physics of Agent Security: Why the Real Risk Is Not the Model but the Authority Around It

## The Trap

They worry that the model might say something strange, rude, or incorrect. But the real architectural danger appears when the model is no longer just generating text. The moment an agent gets tools, credentials, APIs, or retrieval access, the problem changes completely.

That is the trap: we think agent security is about controlling model output. In reality, the harder problem is controlling what the model is allowed to cause.

Ask the harder question: **if an attacker cannot directly reach your database, payment system, or internal API, can they still reach it indirectly by persuading your agent to use it on their behalf?**

If the answer is yes, your agent is a new attack surface with delegated power.

## The Stop-Time Moment

Pause and think about what an agent really is.

It is a system that accepts untrusted input, interprets it probabilistically, and may choose among tools that carry real-world consequences.

**What happens if the prompt is malicious but looks plausible?**

**What happens if a tool returns sensitive data and the model helpfully reformats it for the user?**

**What happens if the agent has more permissions than the user who triggered it?**

This is where security stops being a content-moderation problem and becomes a trust-boundary problem. The model does not need to be “hacked” in the classic sense. It only needs to be convinced.

The most dangerous failures are often ordinary-looking:

- a prompt that routes the agent toward an unauthorized query
- a tool response that contains sensitive data the model was never meant to reveal
- a shared credential that lets one user indirectly exercise another user's power
- logs that preserve private content long after the live interaction ends

## The Mental Model Shift

Stop thinking in model safety. Start thinking in authority containment.

An agent is not secure because the model has good intentions. It is secure only when every boundary around the model assumes the model can be manipulated, confused, or over-helpful.

### Thinking Shifts

- Stop treating the prompt as just conversation.
- Start treating the prompt as untrusted input aimed at a decision-making system.
- Stop thinking tools are helpful extensions.
- Start thinking tools are privilege boundaries that must be defended.
- Stop thinking the model alone should catch dangerous behavior.
- Start thinking layered controls should catch what the model misses.

## The What-If Scenarios

### 1. Prompt Injection Becomes Indirect Action

What if the prompt does not ask for nonsense, but instead nudges the agent toward behavior that looks legitimate?

The risk is not merely embarrassing output. It is downstream action. A malicious instruction can push the agent toward database access, internal queries, unsafe URLs, or misuse of external tools. The attack succeeds by borrowing the agent's authority.

### 2. Helpful Formatting Becomes Data Exfiltration

What if the tool response is technically valid, but contains information the user should never see?

The model may obediently summarize, reformat, or explain the response, accidentally turning raw sensitive data into clean exfiltration. This is why output handling matters as much as input filtering.

### 3. Convenience Becomes Excessive Agency

What if the agent uses a broad shared credential because it is easier to build that way?

Now the user is no longer limited by their own permissions. They are limited by the agent's permissions, which may be much larger. “Helpful automation” becomes a privilege amplifier.

## The Architecture

### Core Controls

- **Input filtering before model execution.** Inspect prompts for injection attempts, malicious URLs, unsafe content, and inbound sensitive data before wasting inference or reaching a tool.
- **Output filtering after tool and model responses.** Redact or block sensitive data and unsafe disclosures before they reach the model or the user.
- **Tool-local authentication.** Credentials should live with the tool or downstream service boundary, not inside the agent's reasoning loop.
- **Least privilege authorization.** The agent should never hold more authority than the task requires, and ideally should act only within the user's allowed scope.
- **Secrets isolation.** API keys and tokens should be retrieved from proper secret storage, not embedded in prompts, client code, or casual environment sprawl.
- **Logging with redaction.** Observability is essential, but logs that capture unfiltered prompts, outputs, or credentials become delayed breaches.

The deeper point is architectural: the model is not the root of trust. If your design assumes the model will reliably refuse malicious instructions, you have built security on probabilistic behavior.

## Beyond the Model

Agent security also inherits old truths from traditional systems:

- infrastructure access still needs identity and access management
- dependencies still need provenance and vulnerability review
- downstream tools still need trust evaluation
- human oversight still depends on usable logs, revocable access, and auditability

Agents compress many old problems into one deceptively simple interface.

## The Question to Sit With

If an agent can read untrusted input, reason imperfectly, call tools, access secrets, touch external systems, and return polished answers to users, then what exactly are you securing when you say you have secured “the model”?

And if the real risk lives in the permissions, boundaries, and trust relationships around it, should your security architecture begin with the model at all, or with the damage the model is allowed to cause when it is wrong?