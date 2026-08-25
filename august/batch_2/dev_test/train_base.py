"""Pretrain the frozen base model on a generic 'copy' task.

Why copy, and not one of the real skills? Because in the paper, M_phi is a
generic pretrained LLM that was NOT specifically trained on 'reverse this
string' or 'translate English to Twi'. It just has broad sequence-modeling
ability, and prefix-tuning is what teaches it a specific new behavior
without touching its weights. 'Copy' (output = input) gives our toy base
model that same kind of generic, task-agnostic competence: it learns
attention/positional mechanics, but not any of the 4 transforms we'll test.

Format for every example, for both this script and all downstream training:
    <bos> x_1 x_2 ... x_n <sep> y_1 y_2 ... y_m <eos>
Loss is computed only on the y_1..y_m <eos> portion (standard prefix-LM
fine-tuning setup -- the same objective the real prefix-tuning paper uses).
"""

import torch
import torch.nn.functional as F

from model import TinyTransformer, Config, encode, PAD, SEP, BOS, EOS
import tasks

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def build_batch(pairs, device=DEVICE):
    """pairs: list[(x_str, y_str)] -> padded (input_ids, loss_mask, targets)."""
    seqs = []
    for x, y in pairs:
        ids = [BOS] + encode(x) + [SEP] + encode(y) + [EOS]
        seqs.append(ids)
    max_len = max(len(s) for s in seqs)
    input_ids = torch.full((len(seqs), max_len), PAD, dtype=torch.long)
    loss_mask = torch.zeros((len(seqs), max_len), dtype=torch.bool)
    for i, (s, (x, y)) in enumerate(zip(seqs, pairs)):
        input_ids[i, : len(s)] = torch.tensor(s, dtype=torch.long)
        # loss applies to every position that PREDICTS a token belonging to
        # y_1..y_m<eos>. Predicting position t means using logits at t-1.
        y_start = 1 + len(encode(x)) + 1  # index of first y token
        loss_mask[i, y_start - 1 : len(s) - 1] = True
    return input_ids.to(device), loss_mask.to(device)


def compute_loss(model, input_ids, loss_mask, prefix=None):
    logits = model(input_ids, prefix=prefix)  # [B, T, V]
    pred_logits = logits[:, :-1, :]
    targets = input_ids[:, 1:]
    mask = loss_mask[:, :-1]
    loss_per_tok = F.cross_entropy(
        pred_logits.reshape(-1, pred_logits.size(-1)),
        targets.reshape(-1),
        reduction="none",
    ).view_as(targets)
    loss = (loss_per_tok * mask).sum() / mask.sum().clamp(min=1)
    return loss


def train_base_model(steps=800, batch_size=32, lr=3e-4, seed=0):
    torch.manual_seed(seed)
    cfg = Config()
    model = TinyTransformer(cfg).to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)

    for step in range(steps):
        batch_pairs = []
        for _ in range(batch_size):
            x = tasks.random_input()
            batch_pairs.append((x, x))  # identity/copy target
        input_ids, loss_mask = build_batch(batch_pairs)
        loss = compute_loss(model, input_ids, loss_mask)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 100 == 0 or step == steps - 1:
            print(f"[train_base] step {step:4d}  loss {loss.item():.4f}")

    for p in model.parameters():
        p.requires_grad_(False)
    model.eval()
    return model


if __name__ == "__main__":
    model = train_base_model()
    torch.save(model.state_dict(), "base_model.pt")
    print("Saved base_model.pt")
