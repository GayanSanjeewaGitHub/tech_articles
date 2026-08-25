"""SkillSmith: the hyper-network that reads (text + skill-prefix) bundles and
directly generates a brand-new prefix for the frozen base model.

Mirrors Figure 1 / Figure 2 of the paper:

    [preamble] <src> [desc_1 text] <kv> [KV_1 projected] <kve>
               <src> [desc_2 text] <kv> [KV_2 projected] <kve>
    [combination text] <gen> [slot_1 ... slot_L] <gene>

SkillSmith is itself a small transformer (its own separate weights -- NOT
the frozen base model). It reads the whole thing as one sequence of
embeddings (text positions embedded normally via its own token table; KV
positions embedded via a learned "input adapter" MLP instead of a token
lookup), then reads OUT a new prefix from the hidden states at the L
placeholder slot positions, via a learned "output adapter" MLP.

Simplification vs. the paper (documented in PLAN.md): each source skill's
entire prefix tensor is projected down to a SINGLE input token, rather than
one token per layer/position. The output side is not simplified: one
placeholder slot per output prefix position, matching the paper's mechanism.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

from model import (
    TinyTransformer, Config, encode,
    BOS, SEP, EOS, SRC, KV, KVE, GEN, GENE,
    prefix_numel,
)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

PREAMBLE = "Compose the following source skills to solve a new target task."


class _SkillSmithBackboneConfig(Config):
    """Same architecture as the base model's Config (d_model/n_heads/n_layers/
    d_head/prefix_len all inherited unchanged -- this matters because
    in_adapter/out_adapter dimensions below are computed from the BASE
    model's Config and must line up with this one's d_model). The only
    thing that needs to differ is max_len: SkillSmith's own sequence
    (preamble + 2 skill descriptions + combination text + output slots) is
    much longer than any sequence the base model itself ever processes."""
    max_len = 512


class SkillSmith(nn.Module):
    def __init__(self, cfg: Config = Config()):
        super().__init__()
        self.cfg = cfg  # the BASE model's config -- defines the shape of the prefix we generate
        self.backbone = TinyTransformer(_SkillSmithBackboneConfig())
        # Input K-V adapter: flattened source-skill prefix -> one token embedding.
        self.in_adapter = nn.Linear(prefix_numel(cfg), cfg.d_model)
        # Output K-V adapter: per-slot hidden state -> one prefix "position"
        # worth of (K,V) values across every base-model layer/head at once.
        per_slot_dim = cfg.n_layers * 2 * cfg.n_heads * cfg.d_head
        self.out_adapter = nn.Linear(cfg.d_model, per_slot_dim)
        # Distinct learnable placeholder embedding per output slot (z_1..z_L
        # in the paper), so the model can tell the L slots apart before any
        # attention has happened.
        self.slot_emb = nn.Embedding(cfg.prefix_len, cfg.d_model)

    def _text_embeds(self, ids_list):
        ids = torch.tensor([ids_list], dtype=torch.long, device=DEVICE)
        return self.backbone.tok_emb(ids)[0]  # [T, D], no position yet

    def _build_sequence(self, bundles, combo_text):
        """bundles: list of (description_str, skill_prefix_tensor[on DEVICE])
        of length 2. Returns (embeds [1,T,D], gen_slot_start_index)."""
        cfg = self.cfg
        rows = []

        rows.append(self._text_embeds([BOS] + encode(PREAMBLE)))
        for desc, skill_prefix in bundles:
            rows.append(self._text_embeds([SRC] + encode(desc) + [KV]))
            kv_token = self.in_adapter(skill_prefix.reshape(-1)).unsqueeze(0)  # [1,D]
            rows.append(kv_token)
            rows.append(self._text_embeds([KVE]))
        rows.append(self._text_embeds(encode(combo_text) + [GEN]))

        gen_slot_start_index = sum(r.shape[0] for r in rows)

        slot_ids = torch.arange(cfg.prefix_len, device=DEVICE)
        rows.append(self.slot_emb(slot_ids))  # [prefix_len, D]
        rows.append(self._text_embeds([GENE, EOS]))

        x = torch.cat(rows, dim=0).unsqueeze(0)  # [1, T, D]
        T = x.shape[1]
        pos = torch.arange(T, device=DEVICE).unsqueeze(0)
        x = x + self.backbone.pos_emb(pos)
        return x, gen_slot_start_index

    def generate_prefix(self, bundles, combo_text):
        """Returns a new prefix tensor, same shape as new_prefix_param(cfg):
        [n_layers, 2, n_heads, prefix_len, d_head]."""
        cfg = self.cfg
        x, slot_start = self._build_sequence(bundles, combo_text)
        hidden = self.backbone.forward_hidden(x)  # [1, T, D]
        slot_hidden = hidden[0, slot_start: slot_start + cfg.prefix_len, :]  # [P, D]
        raw = self.out_adapter(slot_hidden)  # [P, n_layers*2*n_heads*d_head]
        raw = raw.view(cfg.prefix_len, cfg.n_layers, 2, cfg.n_heads, cfg.d_head)
        prefix = raw.permute(1, 2, 3, 0, 4)  # -> [n_layers,2,n_heads,prefix_len,d_head]
        return prefix


def meta_train_skillsmith(base_model, skill_prefixes, skill_descriptions,
                           pairs, steps=600, batch_size=16, lr=3e-4):
    """Trains SkillSmith end-to-end: for randomly sampled composite tasks
    from `pairs`, generate a prefix and backprop the frozen base model's
    cross-entropy loss on the *actual composite target* into SkillSmith's
    parameters (Section 3.4's objective). The base model and the individual
    skill prefixes are both frozen throughout -- only SkillSmith learns."""
    from train_base import build_batch, compute_loss
    import tasks as task_mod

    cfg = Config()
    skillsmith = SkillSmith(cfg).to(DEVICE)
    opt = torch.optim.AdamW(skillsmith.parameters(), lr=lr)

    datasets = {
        (i, j): task_mod.make_composite_dataset(i, j, n_examples=200)
        for (i, j) in pairs
    }

    for step in range(steps):
        i, j = pairs[torch.randint(0, len(pairs), (1,)).item()]
        bundles = [
            (skill_descriptions[i], skill_prefixes[i].to(DEVICE)),
            (skill_descriptions[j], skill_prefixes[j].to(DEVICE)),
        ]
        combo_text = task_mod.combination_text(i, j)

        generated_prefix = skillsmith.generate_prefix(bundles, combo_text)

        dataset = datasets[(i, j)]
        batch = [dataset[k % len(dataset)] for k in
                 torch.randint(0, len(dataset), (batch_size,)).tolist()]
        input_ids, loss_mask = build_batch(batch)
        loss = compute_loss(base_model, input_ids, loss_mask, prefix=generated_prefix)

        opt.zero_grad()
        loss.backward()
        opt.step()

        if step % 50 == 0 or step == steps - 1:
            print(f"[skillsmith meta-train] step {step:4d}  pair={i}+{j}  loss {loss.item():.4f}")

    skillsmith.eval()
    return skillsmith
