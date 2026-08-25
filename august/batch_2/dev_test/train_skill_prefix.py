"""Train one prefix-tuning 'skill' per base transform, against the frozen
base model. This is the literal `m_i` from the paper: after this script,
each skill is nothing but a small tensor file plus a one-line text
description -- no base-model weights are touched.
"""

import torch

from model import Config, new_prefix_param
from train_base import train_base_model, build_batch, compute_loss
import tasks

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def train_prefix_for_skill(base_model, skill_name, steps=400, batch_size=32, lr=1e-2):
    cfg = Config()
    prefix = new_prefix_param(cfg).to(DEVICE)
    prefix.requires_grad_(True)
    opt = torch.optim.AdamW([prefix], lr=lr)

    dataset = tasks.make_skill_dataset(skill_name, n_examples=2000)

    for step in range(steps):
        batch = [dataset[i % len(dataset)] for i in
                 torch.randint(0, len(dataset), (batch_size,)).tolist()]
        input_ids, loss_mask = build_batch(batch)
        loss = compute_loss(base_model, input_ids, loss_mask, prefix=prefix)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 100 == 0 or step == steps - 1:
            print(f"[skill={skill_name}] step {step:4d}  loss {loss.item():.4f}")

    return prefix.detach()


def train_all_skill_prefixes(base_model, out_dir="skill_prefixes"):
    prefixes = {}
    for skill_name in tasks.SKILLS:
        prefix = train_prefix_for_skill(base_model, skill_name)
        prefixes[skill_name] = prefix
        torch.save(prefix.cpu(), f"{out_dir}/{skill_name}.pt")
        with open(f"{out_dir}/{skill_name}.txt", "w") as f:
            f.write(tasks.SKILL_DESCRIPTIONS[skill_name])
        print(f"Saved {out_dir}/{skill_name}.pt")
    return prefixes


if __name__ == "__main__":
    import os
    os.makedirs("skill_prefixes", exist_ok=True)

    print("=== Pretraining frozen base model on generic copy task ===")
    base_model = train_base_model()
    torch.save(base_model.state_dict(), "base_model.pt")

    print("\n=== Training one prefix per skill (base model stays frozen) ===")
    train_all_skill_prefixes(base_model)
