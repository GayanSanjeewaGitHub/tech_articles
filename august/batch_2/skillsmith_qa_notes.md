# SkillSmith — Q&A Notes: Where Do Skills Actually Live?

## Q: This "skill" — is it just a prompt in the code sent to the LLM alongside the query? Or is it some other weight, like a small model that's good at that thing? Then when making an LLM call, where do these skills stay?

Not a prompt, not a separate small model — it's a **KV-cache** (a form of prefix-tuning).

| Type | What it is | Analogy |
|---|---|---|
| **Prompt / text ICL** | Plain text sent alongside your input every time | Sticky notes you re-read every conversation |
| **LoRA / small adapter model** | Extra trainable weight matrices bolted onto the model's layers, changing how it computes | Swapping in a different lens for the camera |
| **Prefix-tuning KV-cache (what SkillSmith uses)** | A block of numbers representing **cached attention states** — Key and Value tensors, one set per layer/head | Pre-loaded "memories" injected directly into the model's attention, as if some invisible text had already been read |

**What a KV-cache actually is, mechanically:**

When a transformer processes real text, at every layer it computes **Key** and **Value** vectors for each token — these are what later tokens "attend to." Normally you'd get these by actually running text through the model.

Prefix-tuning skips that: you directly **train** a fixed-size block of K/V vectors (via gradient descent, not by writing English) so that when they're spliced in front of the real input's attention computation, the model behaves as if it had read some ideal, optimized context — even though no such text ever existed.

So a "skill" (like *English→Twi*) is stored as:
- a tensor file, shape roughly `[num_layers, 2 (K and V), num_heads, prefix_length, head_dim]`
- tied to one specific frozen base model (Gemma 3 4B in this paper)
- much smaller than a full model checkpoint, comparable in spirit to a LoRA adapter file, but living in **activation space**, not **weight space**

**Where it "stays" between calls:** On disk, as a saved checkpoint — same as you'd save any adapter. It's not re-derived from a prompt each time; it's loaded and spliced in.

**What happens during an actual LLM call:**
1. Take the frozen base model.
2. At every attention layer, **prepend** the skill's stored K/V vectors to the K/V vectors of the real input tokens — as if `prefix_length` invisible tokens came first.
3. Every real token's attention now sees both the real context *and* these injected "virtual tokens" — cheaply, without spending your actual context window on them, and without ever generating them from text.
4. The rest of the forward pass proceeds normally.

**Where SkillSmith fits:** SkillSmith is a *second*, separate LLM whose job is to read several stored KV-cache files + text descriptions of what each does + a note on how to combine them, and output a **brand-new KV-cache** of the same shape. That new cache is then spliced into the frozen downstream model exactly as described above — it's not itself "used" for inference; it *manufactures* the prefix-cache that gets used.

---

## Q: This sits in the middle of inference where the query text comes in. If we get a new open-source model, do we have to fine-tune to put this KV thing in the middle layer, or can we do this on an already-trained model?

No architecture change or fine-tuning of the base model itself is needed. The base model stays completely frozen. You only need to *train the prefix vectors themselves* (via gradient descent on some task data) — that's the "prefix-tuning" step. Once trained, they plug into *any* forward pass of that same frozen model, for any new input, forever. You don't retrain the model each time, only once per skill.

## Q: But how come they don't consume the context window? Don't they need to load into the context window?

No — that's the key trick. It never becomes text tokens. It skips the embedding + early layers entirely and is injected **directly into the attention computation** at each layer, as extra K/V entries. Nothing is added to the tokenizer's input sequence, so your actual context window (the text budget) is untouched.

## Q: Or is it affecting the middle of actual inference happening like an already-defined rule — does model weight/size increase slightly due to this?

No, model weights don't change at all (they stay frozen, byte-for-byte identical). What increases is just the **compute per forward pass slightly** — attention at each layer scans a few extra K/V pairs (the prefix length, e.g. 32) in addition to your real tokens. Tiny cost, no permanent size increase, and the cache itself is a small separate file (not merged into model weights).

**One-line mental model:** it's not a bigger model and not a bigger prompt — it's a small removable "memory implant" spliced into attention math at inference time, trained once offline, reusable forever, invisible to the tokenizer.

---

## Q: So can we just keep multiple skills like this and attach/remove and reuse whenever needed?

Yes — that's exactly the intended use case, and it's literally why the paper calls them a "skill library." A few practical notes though:

**What works cleanly:**
- Train once, save as a small file, reuse indefinitely — no retraining needed to reuse.
- Attach/detach freely per request: skill A for this call, skill B for the next, no skill at all for a third. Zero cost when detached.
- Store dozens/hundreds of these cheaply (they're small compared to full model weights).

**Constraints to know:**
- **Same base model only.** A cache trained for Gemma-3-4B only works spliced into that exact frozen Gemma-3-4B — it's tied to that model's internal attention geometry. Swap the base model, the cache is garbage.
- **Naively combining multiple attached skills doesn't just work.** This is literally the paper's whole point — if you attach both "translation" and "legal parsing" caches side by side (concatenate) or average them, results are mediocre. Real synthesis needs something like SkillSmith to actually *fuse* them into one new cache when you want cross-skill behavior, rather than just stacking many independently-trained ones.
- **Fixed prefix length per cache** (e.g. 32 tokens' worth) — you decide that at training time.
- Order/interaction between multiple simultaneously-attached raw caches isn't well-defined without a fusion step — it's not like plugging in independent USB drives that just coexist peacefully; attention lets them "see" each other, which can help or hurt unpredictably.

**Practical pattern this paper suggests:** keep a library of single-skill caches (cheap, reusable, swappable), and when a *new* task needs a combination nobody trained directly, use a SkillSmith-like model to synthesize a fresh, purpose-built cache from the relevant library entries — rather than trying to naively stack raw skills together at inference time.
