# Dev Test — SkillSmith Toy Reproduction: Plan

## Goal

Build a small, fully self-contained (offline, no downloaded pretrained models) demo that reproduces
the *mechanics* of the SkillSmith paper at toy scale, so the ideas in `skillsmith_intuitive_explainer.md`
and `skillsmith_qa_notes.md` can be seen running instead of just read about.

We are NOT trying to reproduce the paper's actual benchmark numbers (Composite-SNI, Gemma 3 4B, etc.).
We ARE trying to faithfully reproduce the *mechanism*:

1. A frozen base model.
2. Per-skill "parametric skills" = trained prefix K/V caches (real prefix-tuning, not LoRA, not prompts).
3. Naive baselines for combining two skills (average, concatenate).
4. A small hyper-network ("SkillSmith") that reads two skill-prefixes + their text descriptions + a
   combination instruction, and *generates* a brand-new prefix for an unseen composite task.
5. A comparison table showing SkillSmith beats the naive baselines and direct-from-scratch training,
   the same qualitative result as Figure 3 / Table 1 in the paper.

## Toy task design

- Character-level vocabulary (a-z, A-Z, space) + control tokens (`<pad> <sep> <bos> <eos>` and
  SkillSmith-only control tokens `<src> <kv> <kve> <gen> <gene>`).
- **Base skills** (functions on a random lowercase string):
  - `reverse` — reverse the string
  - `upper` — uppercase it
  - `dup` — double every character
  - `shift` — Caesar-shift lowercase letters by 1
- **Composite tasks** = apply skill *i* then skill *j* (`compose(s) = skill_j(skill_i(s))`), for a
  chosen subset of ordered pairs.
  - **Meta-train pairs**: used to train SkillSmith's fusion ability.
  - **Meta-test pairs**: entirely held out — SkillSmith must generalize to a skill *combination* it
    never trained the fusion for, using individually-trained skill prefixes it also never saw combined.

## Components (mirrors the paper's architecture 1:1)

| Paper concept | This repo |
|---|---|
| Frozen base LLM `M_phi` | `model.py: TinyTransformer` (tiny GPT-style decoder), pretrained once on an identity/"copy" task, then frozen |
| Prefix-tuning skill module `m_i` | `train_skill_prefix.py` — a trainable `[layers, 2, heads, prefix_len, head_dim]` tensor, spliced into the frozen base model's attention at every layer |
| Task bundle `(m_i, w_i)` | one skill prefix `.pt` file + one text description string |
| SkillSmith coprocessor | `skillsmith.py: SkillSmith` — a second small transformer that reads interleaved text + projected-prefix "tokens" and outputs a new prefix |
| Input K-V Adapter / Out K-V Adapter | small MLPs in `skillsmith.py` |
| LERP / Concat baselines | `baselines.py` |
| Direct Prefix Tuning baseline | `baselines.py: train_direct_prefix` |
| ICL baseline | `baselines.py: icl_eval` |
| Global comparison | `evaluate.py` |

## Files

- `model.py` — tokenizer/vocab + `TinyTransformer` with prefix-K/V-injectable attention.
- `tasks.py` — skill functions, synthetic dataset generation, composite task definitions and splits.
- `train_base.py` — pretrains the frozen base model on a generic copy task (so it has generic
  sequence-modeling ability but does **not** already know reverse/upper/etc. — mirrors "the base LLM
  didn't see this task pretrained in weights").
- `train_skill_prefix.py` — trains one prefix per base skill against the frozen base model.
- `baselines.py` — LERP, Concat, Direct-from-scratch, ICL implementations.
- `skillsmith.py` — the SkillSmith coprocessor model + its meta-training loop.
- `evaluate.py` — runs every method on meta-train and meta-test composite tasks, prints an NLL +
  exact-match table (a mini version of the paper's Table 1 / Figure 3).
- `run_pipeline.py` — single entry point that runs steps 1-6 in order.
- `requirements.txt` — just `torch`.

## How to run (once you have Python + torch locally)

```bash
cd august/batch_2/dev_test
pip install -r requirements.txt
python run_pipeline.py
```

Expect a printed table at the end, ranking methods by average cross-entropy loss (lower is better) and
exact-match accuracy, split into "seen combo" and "unseen combo" tasks — the toy analogue of the
paper's Both-Seen / Neither-Seen breakdown (Figure 7).

## Known simplifications vs. the real paper (documented, not hidden)

- Prefix length is fixed across skills (paper samples variable lengths); this makes LERP well-defined
  without extra padding logic.
- SkillSmith's "KV adapter" collapses a whole skill prefix into a *single* projected token rather than
  one token per layer/position — a scale simplification, not a mechanism change.
- No RoPE / rotary position embeddings — plain learned absolute positions — so the paper's inverse-RoPE
  de-rotation step is skipped entirely (not needed here).
- Base model is trained from scratch on a toy "copy" task rather than being a real pretrained LLM.
- No retrieval step — source tasks for each composite are given directly (equivalent to the paper's
  "ground-truth mapping known" Composite-SNI setting, not the noisy retrieval setting).
- The toy vocabulary is letters + space only; `encode()` silently drops any other character (e.g.
  punctuation in description/combination text) rather than erroring. Harmless here — descriptions
  stay readable minus punctuation — but worth knowing if you extend the text templates.
