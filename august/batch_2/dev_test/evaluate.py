"""Compare every method on held-out composite tasks: naive weight-space
baselines (LERP, Concat), direct-from-scratch training, ICL, and SkillSmith
(zero-shot and fine-tuned) -- a toy-scale version of the paper's Table 1 /
Figure 3 / Figure 7 comparison.
"""

import torch

from model import Config, encode, decode, BOS, SEP, EOS
from train_base import build_batch, compute_loss
import tasks
import baselines

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

N_EVAL_LOSS = 60      # examples used for the average cross-entropy metric
N_EVAL_ACC = 20       # (smaller) subset used for exact-match accuracy (decoding is slower)


@torch.no_grad()
def generate_with_prefix(base_model, prefix, x_str, max_new_tokens=14):
    ids = [BOS] + encode(x_str) + [SEP]
    prefix_len_tokens = len(ids)
    for _ in range(max_new_tokens):
        input_ids = torch.tensor([ids], dtype=torch.long, device=DEVICE)
        logits = base_model(input_ids, prefix=prefix)
        next_id = logits[0, -1].argmax().item()
        ids.append(next_id)
        if next_id == EOS:
            break
    y_ids = ids[prefix_len_tokens:]
    if y_ids and y_ids[-1] == EOS:
        y_ids = y_ids[:-1]
    return decode(y_ids)


@torch.no_grad()
def generate_icl(base_model, shot_ids, x_str, max_new_tokens=14):
    ids = list(shot_ids) + encode(x_str) + [SEP]
    prefix_len_tokens = len(ids)
    for _ in range(max_new_tokens):
        input_ids = torch.tensor([ids], dtype=torch.long, device=DEVICE)
        logits = base_model(input_ids, prefix=None)
        next_id = logits[0, -1].argmax().item()
        ids.append(next_id)
        if next_id == EOS:
            break
    y_ids = ids[prefix_len_tokens:]
    if y_ids and y_ids[-1] == EOS:
        y_ids = y_ids[:-1]
    return decode(y_ids)


def eval_with_prefix(base_model, prefix, skill_i, skill_j):
    eval_pairs = tasks.make_composite_dataset(skill_i, skill_j, n_examples=N_EVAL_LOSS)
    input_ids, loss_mask = build_batch(eval_pairs)
    with torch.no_grad():
        loss = compute_loss(base_model, input_ids, loss_mask, prefix=prefix)

    correct = 0
    for x, y in eval_pairs[:N_EVAL_ACC]:
        pred = generate_with_prefix(base_model, prefix, x)
        if pred == y:
            correct += 1
    return loss.item(), correct / N_EVAL_ACC


def eval_icl(base_model, skill_i, skill_j, n_shots=4):
    eval_pairs = tasks.make_composite_dataset(skill_i, skill_j, n_examples=N_EVAL_LOSS)
    loss = baselines.icl_loss(base_model, skill_i, skill_j, eval_pairs, n_shots=n_shots)

    shots = tasks.make_composite_dataset(skill_i, skill_j, n_examples=n_shots)
    shot_ids = [BOS]
    for sx, sy in shots:
        shot_ids += encode(sx) + [SEP] + encode(sy) + [SEP]

    correct = 0
    for x, y in eval_pairs[:N_EVAL_ACC]:
        pred = generate_icl(base_model, shot_ids, x)
        if pred == y:
            correct += 1
    return loss, correct / N_EVAL_ACC


def run_comparison(base_model, skill_prefixes, skillsmith, pairs, split_name):
    print(f"\n=== {split_name} ===")
    header = f"{'pair':<14}{'method':<22}{'avg_CE_loss':>12}{'exact_match':>14}"
    print(header)
    print("-" * len(header))

    rows = []
    for (i, j) in pairs:
        prefix_i = skill_prefixes[i].to(DEVICE)
        prefix_j = skill_prefixes[j].to(DEVICE)
        pair_name = f"{i}+{j}"

        methods = {}

        methods["LERP"] = baselines.lerp(prefix_i, prefix_j)
        methods["Concat"] = baselines.concat(prefix_i, prefix_j)
        methods["Direct (from scratch)"] = baselines.train_direct_prefix(base_model, i, j)

        bundles = [
            (tasks.SKILL_DESCRIPTIONS[i], prefix_i),
            (tasks.SKILL_DESCRIPTIONS[j], prefix_j),
        ]
        combo_text = tasks.combination_text(i, j)
        ss_prefix = skillsmith.generate_prefix(bundles, combo_text).detach()
        methods["SkillSmith (zero-shot)"] = ss_prefix
        methods["SkillSmith (fine-tuned)"] = baselines.finetune_prefix(
            base_model, ss_prefix, i, j
        )

        for method_name, prefix in methods.items():
            loss, acc = eval_with_prefix(base_model, prefix, i, j)
            print(f"{pair_name:<14}{method_name:<22}{loss:>12.4f}{acc:>14.2%}")
            rows.append((pair_name, method_name, loss, acc))

        icl_loss_val, icl_acc = eval_icl(base_model, i, j)
        print(f"{pair_name:<14}{'ICL (few-shot)':<22}{icl_loss_val:>12.4f}{icl_acc:>14.2%}")
        rows.append((pair_name, "ICL (few-shot)", icl_loss_val, icl_acc))

    return rows


def print_summary(rows, split_name):
    from collections import defaultdict
    agg = defaultdict(list)
    for _, method, loss, acc in rows:
        agg[method].append((loss, acc))

    print(f"\n=== {split_name}: averaged across pairs ===")
    header = f"{'method':<22}{'avg_CE_loss':>12}{'avg_exact_match':>18}"
    print(header)
    print("-" * len(header))
    for method, vals in sorted(agg.items(), key=lambda kv: sum(v[0] for v in kv[1])):
        avg_loss = sum(v[0] for v in vals) / len(vals)
        avg_acc = sum(v[1] for v in vals) / len(vals)
        print(f"{method:<22}{avg_loss:>12.4f}{avg_acc:>18.2%}")


if __name__ == "__main__":
    # Expects base_model.pt, skill_prefixes/*.pt and a trained skillsmith to
    # already exist -- run run_pipeline.py for the full end-to-end flow.
    raise SystemExit("Run `python run_pipeline.py` for the full pipeline.")
