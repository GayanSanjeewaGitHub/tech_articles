"""Naive weight-space baselines (LERP, Concat), direct-from-scratch prefix
training, and an in-context-learning (ICL) baseline -- the four families of
uni-modal baselines the paper compares SkillSmith against (Section 4.3).
"""

import torch

from model import Config, new_prefix_param, encode, BOS, SEP, EOS
from train_base import build_batch, compute_loss
import tasks

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def lerp(prefix_i, prefix_j):
    """Simple average -- the paper's LERP / task-arithmetic baseline."""
    return (prefix_i + prefix_j) / 2.0


def concat(prefix_i, prefix_j):
    """Concatenate along the prefix-length axis -- doubles prefix length,
    giving this baseline strictly more raw capacity than every other method
    (as noted in the paper), yet it still under-performs SkillSmith."""
    # prefix shape: [n_layers, 2, n_heads, prefix_len, d_head]
    return torch.cat([prefix_i, prefix_j], dim=3)


def train_direct_prefix(base_model, skill_i, skill_j, steps=150, batch_size=32, lr=1e-2,
                         n_examples=40):
    """Train a fresh prefix from scratch on ONLY the (data-scarce) composite
    task -- no reuse of the individually-trained skill prefixes at all."""
    cfg = Config()
    prefix = new_prefix_param(cfg).to(DEVICE)
    prefix.requires_grad_(True)
    opt = torch.optim.AdamW([prefix], lr=lr)

    dataset = tasks.make_composite_dataset(skill_i, skill_j, n_examples=n_examples)

    for step in range(steps):
        batch = [dataset[i % len(dataset)] for i in
                 torch.randint(0, len(dataset), (batch_size,)).tolist()]
        input_ids, loss_mask = build_batch(batch)
        loss = compute_loss(base_model, input_ids, loss_mask, prefix=prefix)
        opt.zero_grad()
        loss.backward()
        opt.step()

    return prefix.detach()


def finetune_prefix(base_model, init_prefix, skill_i, skill_j, steps=150,
                     batch_size=32, lr=1e-2, n_examples=40):
    """Continue training a given initial prefix on the (small) composite
    dataset -- used both for the 'Source-Task-Transfer + fine-tune' baseline
    and for 'SkillSmith as initialization + fine-tune'."""
    prefix = init_prefix.clone().detach().to(DEVICE)
    prefix.requires_grad_(True)
    opt = torch.optim.AdamW([prefix], lr=lr)

    dataset = tasks.make_composite_dataset(skill_i, skill_j, n_examples=n_examples)

    for step in range(steps):
        batch = [dataset[i % len(dataset)] for i in
                 torch.randint(0, len(dataset), (batch_size,)).tolist()]
        input_ids, loss_mask = build_batch(batch)
        loss = compute_loss(base_model, input_ids, loss_mask, prefix=prefix)
        opt.zero_grad()
        loss.backward()
        opt.step()

    return prefix.detach()


def icl_loss(base_model, skill_i, skill_j, eval_pairs, n_shots=4):
    """In-context-learning baseline: no prefix at all. Instead, literally
    prepend a few worked examples of the composite task as text, then ask
    the frozen base model to continue -- the paper's ICL baseline, and the
    one that stays competitive zero-shot but loses once fine-tuning is
    allowed."""
    shots = tasks.make_composite_dataset(skill_i, skill_j, n_examples=n_shots)
    shot_ids = [BOS]
    for x, y in shots:
        shot_ids += encode(x) + [SEP] + encode(y) + [SEP]

    total_loss, total_tokens = 0.0, 0
    for x, y in eval_pairs:
        query_ids = encode(x) + [SEP] + encode(y) + [EOS]
        full_ids = shot_ids + query_ids
        input_ids = torch.tensor([full_ids], dtype=torch.long, device=DEVICE)

        loss_mask = torch.zeros_like(input_ids, dtype=torch.bool)
        y_start_in_query = len(encode(x)) + 1  # position of first y token within query
        y_start = len(shot_ids) + y_start_in_query
        loss_mask[0, y_start - 1: len(full_ids) - 1] = True

        loss = compute_loss(base_model, input_ids, loss_mask)
        n_tok = loss_mask[:, :-1].sum().item()
        total_loss += loss.item() * n_tok
        total_tokens += n_tok

    return total_loss / max(total_tokens, 1)
