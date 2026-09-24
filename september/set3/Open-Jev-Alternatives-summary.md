# Open JEV Alternatives: Fast, Local, No-Training Classifiers

*A summary of a video walkthrough comparing open-source replications of JEV — a universal LLM-based classifier — run locally on an RTX Pro 6000.*

## The Problem: Every Classifier Used to Need Its Own Training Run

Text/decision classification isn't new — BERT, ModernBERT, TextCNN have done it for years, often fast and cheap. But they all share the same catch: **change your labels, retrain the model.** That's a real cost for teams constantly iterating on categories (sentiment buckets, support-ticket routing, moderation policies), and it's exactly the workflow the presenter lived through running NLP classification for a previous startup.

Reasoning LLMs solve the "any label, no training" problem, but at the wrong price: too slow and too expensive to call for every routine yes/no or multiple-choice decision in a pipeline.

**JEV's pitch:** a single frozen model that classifies *any* schema — choice / score / null — with no fine-tuning, by treating classification as an entailment/logit-readout problem instead of a generation problem. Since JEV launched, in ~24–48 hours the open-source community produced 20–30+ replications, benchmarked on a new leaderboard called **JevBench** (scored on intelligence, calibration, speed, and cost).

## The Core Trick: Read the Logits, Don't Generate the Answer

Classification-via-entailment isn't a new idea — papers reframing it this way go back to 2019, and BERT-era models could already do simple "does sentence B follow from sentence A?" judgments. What's different now is that the base model has enough general world knowledge baked into its weights to generalize across arbitrary schemas, not just the entailment task it was tuned for.

The mechanical trick underlying JEV and nearly every open clone:
1. Put the question and the answer options directly in the prompt.
2. Run only the **prefill** pass (process the prompt once) — don't let the model autoregressively generate text.
3. Read the logits for just the option tokens (or a hidden-state projection onto them) and **softmax** over those to get a calibrated probability distribution.

This is one forward pass instead of a generation loop, which is where the speed and cost advantage comes from — you get a probability-scored answer to a choice/score/null-style question almost for free.

## The Open Field, Six Ways

| Project | Base model | Approach | Where it shines |
|---|---|---|---|
| **SEM/OpenJV** | Frozen Qwen 3.5 4B, zero training | Pure logit-readout on stock weights | Closest overall JevBench score (74.3 vs JEV's 75.3); works with any model you already have loaded |
| **Nimble (Bespoke)** | Qwen 3.5 9B + LoRA | Same readout trick, but with a small LoRA trained on <3,000 **contrastive** examples (near-identical pairs where changing one fact flips the answer) | Best on narrow, well-defined policy decisions (~90% on its own hold-out vs ~66% base) — but drops to ~44% on JevBench's hard tier, showing it doesn't generalize past what it was trained on |
| **Decider (Mapa)** | Qwen 3.5 2B (small) | Reads *hidden states* at each answer slot and projects onto options, rather than reading output logits; serves the same wire format as a typed API | Speed + self-contained server — ~33ms/answer; but noticeably more "on the fence"/indecisive than JEV, which tends to answer with high confidence |
| **OpenJEV (Alex Ortega)** | Entailment-style, vision-capable | Same readout idea, extended to accept **images** | Multimodal decision-making — demoed playing Doom and Minecraft by turning game actions into multiple-choice questions |
| **Diffusion Gemma** | 26B diffusion model | Denoising steps instead of autoregressive decoding; reads log-probs at answer slots | Raw throughput — extremely high concurrency/decisions-per-second, at the cost of being visibly undertrained relative to similarly sized autoregressive models |
| **NanoJEV** | ~600M params | Tiny model, same choice-schema idea | Proof that even a very small model can do real-time sequential decision-making (demoed playing Snake) when the task is reframed as repeated multiple-choice |
| **Leila** (bonus) | ModernBERT-large (~420M) | Classic BERT-style encoder, not an LLM readout | Multilingual (~100 languages), answers choice/score/null in a single forward pass; solid but clearly behind the LLM-based approaches on JevBench's accuracy-weighted score — the "old way" still works, just doesn't generalize as well as a bigger pretrained LLM's world knowledge does |

Common thread: **none of these needed JEV's actual weights.** They're either using a stock open model's own logits directly, or lightly steering one with a small LoRA — no distillation from JEV claimed by any of them.

## What's Genuinely New Here

1. **Confirmation that the "prefill + logit readout" trick generalizes across many base models** — not just whatever model JEV itself uses. Within ~24 hours of the original JEV video's speculation, ~30 independent teams converged on essentially the same mechanism.
2. **A shared benchmark (JevBench)** emerged fast enough to actually rank these against each other on intelligence/calibration/speed/cost — turning "which one should I use" into a data-backed question instead of vibes.
3. **A clear, reusable recipe for domain-specific accuracy**: Nimble's "contrastive data curation" (near-duplicate examples where one fact flips the label) is a cheap, small-data (<3,000 examples) way to sharpen a general open model for one recurring policy decision, at the known cost of hurting generalization elsewhere.
4. **Proof that the schema (choice/score/null answered as multiple-choice) is a general enough interface** to repurpose for things that don't look like "classification" at all — Doom/Minecraft action selection, Snake — by turning any decision into a scored-options question.
5. **A visible frontier**: on JevBench's "hard" tier (multi-hop reasoning, date arithmetic), every open replica — and JEV itself, relatively — falls off compared to a full reasoning LLM like GPT-5.6, which stays far ahead on hard tasks but costs ~6x more and is much slower.

## Real-World Usage Intuition: When and How to Reach for This

The mental model: **this is "System 1" for your pipeline** — a fast, cheap, confident-when-it's-easy classifier you put in front of an expensive "System 2" reasoning model, not a replacement for it.

Practical decision guide from the comparison:

- **No time/no data to train, want it today** → do the SEM/OpenJV-style logit-readout trick on whatever model you already have deployed. It's just a different way of *calling* an existing model, not a new model to host.
- **Need a small, self-contained server that speaks a stable typed API/wire format** → Decider's approach (hidden-state projection + fixed schema) is the one built for that integration shape, accepting some indecisiveness in exchange for a clean API and strong latency (~33ms).
- **Have one narrow, recurring policy decision** (e.g., "is this refund authorized," "does this ticket need escalation") and a handful of labeled examples → Nimble's LoRA + contrastive-pair recipe (flip one fact, keep everything else identical) is the cheapest path to high accuracy on *that specific decision* — but don't expect it to generalize to anything outside that policy's shape.
- **Need to classify or reason over images**, not just text → OpenJEV's vision variant is the only one of the six built for that.
- **Need maximum throughput / massive concurrency** (bulk ticket triage, real-time filtering at scale) → Diffusion Gemma's non-autoregressive denoising pass is dramatically faster per decision, at the cost of some undertrained-feeling accuracy.
- **Resource-constrained or edge deployment** → NanoJEV (600M) or Leila (420M, multilingual, BERT-based) run on far less hardware, trading away some of the larger LLMs' world-knowledge generalization.

**The real production pattern the video lands on: cascade, don't choose one.** Let a fast local classifier (any of the above) handle the bulk of routine choice/score/null decisions where it answers with high confidence, and only escalate the low-confidence or genuinely hard cases (multi-hop reasoning, date math, ambiguous edge cases) up to a real reasoning LLM on low/medium effort. That gets you System 2's accuracy on the tail of hard cases while paying System 1's speed and cost on the (much larger) bulk of easy ones — which is the actual economic argument for why "universal fast classifiers" matter in an agent pipeline, independent of which specific open implementation you pick.
