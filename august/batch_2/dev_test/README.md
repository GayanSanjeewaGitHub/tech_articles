# SkillSmith — Toy, Runnable Reproduction

This folder is a small, fully offline (no downloaded pretrained models, no internet needed)
implementation that reproduces the *mechanism* described in `../skillsmith_story.md`,
`../skillsmith_intuitive_explainer.md`, and `../skillsmith_qa_notes.md` — see `PLAN.md` for the
full design writeup.

**⚠️ I could not run or test this code myself.** This machine has no Python installed
(`python`, `py`, `python3` all resolve to nothing but Windows Store stubs). Everything below was
written carefully and reviewed line-by-line for shape/logic correctness, but it has **not been
executed**. Please run it locally and report back if anything breaks — happy to debug from an
actual traceback.

## What this demonstrates

1. A frozen "base LLM" (tiny GPT-style transformer, trained from scratch on a generic
   character-copy task so it has *no* prior knowledge of the specific skills below).
2. Four **parametric skills**, each a literal prefix-tuning KV-cache tensor (not a prompt, not
   a LoRA) trained against the frozen base model: `reverse`, `upper`, `dup`, `shift`.
3. Naive weight-space combination baselines: **LERP** (average) and **Concat**.
4. A **direct-from-scratch** prefix-training baseline (no reuse of existing skills at all).
5. An **in-context-learning (ICL)** baseline (few-shot text examples, no prefix at all).
6. **SkillSmith**: a second small transformer that reads two skill bundles (description text +
   projected KV-cache) plus a combination instruction, and *generates* a brand-new KV-cache for
   the composite task — evaluated both zero-shot and after a short fine-tune.
7. A held-out generalization test: SkillSmith is meta-trained to fuse 8 skill-pairs, then
   evaluated on 4 entirely unseen pairs it never learned to fuse.

## How to run

```bash
cd august/batch_2/dev_test
python -m venv .venv && .venv/Scripts/activate   # or source .venv/bin/activate on mac/linux
pip install -r requirements.txt
python run_pipeline.py
```

Takes roughly a few minutes on CPU (everything is tiny: 3-layer, 64-dim transformers, short
strings). No GPU required, though it'll use one automatically if available.

## What you should see

A printed table for each of the two splits (seen combinations / unseen combinations), listing
average cross-entropy loss and exact-match accuracy per method per skill-pair, followed by an
averaged summary table. The expected qualitative ranking (matching the paper's Figure 3 / Table 1):

```
LERP / Concat            <  mediocre, especially Concat despite having 2x prefix capacity
Direct (from scratch)    <  weak zero-shot equivalent isn't applicable, but data-scarce fine-tune is mediocre
ICL (few-shot)           <  competitive zero-shot, doesn't benefit from further optimization
SkillSmith (zero-shot)   <  should already beat LERP/Concat with no target-task training at all
SkillSmith (fine-tuned)  <  best or tied-best overall, including on UNSEEN skill combinations
```

If SkillSmith doesn't clearly win, the most likely causes (in order of likelihood) and what to
try:
- **Too few meta-training steps/pairs** — bump `steps` in `meta_train_skillsmith` (skillsmith.py)
  and/or add more meta-train pairs in `tasks.py`.
- **Learning rate too high/low for the tiny model** — try `1e-3` to `1e-4` range in
  `skillsmith.meta_train_skillsmith`.
- **Base model undertrained** — increase `steps` in `train_base_model` (train_base.py) so it has
  robust enough generic sequence-copying ability for prefixes to steer.

## File-by-file map

See `PLAN.md` for the full architecture-to-code mapping table. Quick summary:

| File | Purpose |
|---|---|
| `model.py` | Vocab/tokenizer + `TinyTransformer` with prefix-K/V-injectable attention |
| `tasks.py` | The 4 base skills, synthetic data generation, composite task pairs + seen/unseen split |
| `train_base.py` | Pretrains + freezes the base model; shared batch-building / loss helpers |
| `train_skill_prefix.py` | Trains one prefix per base skill against the frozen base model |
| `baselines.py` | LERP, Concat, direct-from-scratch, ICL |
| `skillsmith.py` | The `SkillSmith` hyper-network + its meta-training loop |
| `evaluate.py` | Cross-entropy + exact-match evaluation and comparison-table printing |
| `run_pipeline.py` | Single command that runs everything end to end |

## Known simplifications (see PLAN.md for the full list)

The two biggest ones: (1) skill prefixes have a fixed length here, so LERP needs no padding logic
(the paper samples variable lengths); (2) SkillSmith's input adapter collapses each source skill's
*entire* prefix into a single projected token rather than one token per position — a scale
simplification, done purely to keep the toy model small and fast to train, not a change to the
underlying mechanism.
