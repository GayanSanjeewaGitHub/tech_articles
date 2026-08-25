"""Tiny GPT-style decoder-only transformer with prefix-K/V injectable attention.

This is the "frozen base model" M_phi from the SkillSmith paper, shrunk to
character-level toy scale. The important part is `CausalSelfAttention`:
it accepts an optional `prefix_kv` tensor and prepends it to the real
sequence's Key/Value tensors at every layer, before the causal softmax.
That splice is exactly what "prefix-tuning" / a "parametric skill" means in
the paper -- nothing about the base model's weights changes; only what's
prepended to attention changes.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F

# ---------------------------------------------------------------------------
# Vocabulary / tokenizer
# ---------------------------------------------------------------------------

SPECIAL_TOKENS = [
    "<pad>", "<sep>", "<bos>", "<eos>",
    # SkillSmith-only control tokens (Figure 2 in the paper)
    "<src>", "<kv>", "<kve>", "<gen>", "<gene>",
]
CHARS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ")
VOCAB = SPECIAL_TOKENS + CHARS
STOI = {ch: i for i, ch in enumerate(VOCAB)}
ITOS = {i: ch for i, ch in enumerate(VOCAB)}
VOCAB_SIZE = len(VOCAB)

PAD, SEP, BOS, EOS = STOI["<pad>"], STOI["<sep>"], STOI["<bos>"], STOI["<eos>"]
SRC, KV, KVE, GEN, GENE = (
    STOI["<src>"], STOI["<kv>"], STOI["<kve>"], STOI["<gen>"], STOI["<gene>"],
)


def encode(text):
    """String -> list[int]. Unknown characters are dropped (toy vocab only)."""
    return [STOI[ch] for ch in text if ch in STOI]


def decode(ids):
    return "".join(ITOS[i] for i in ids if i not in (PAD, BOS, EOS, SEP))


# ---------------------------------------------------------------------------
# Model config
# ---------------------------------------------------------------------------

class Config:
    vocab_size = VOCAB_SIZE
    d_model = 64
    n_layers = 3
    n_heads = 4
    d_head = d_model // n_heads
    d_ff = 4 * d_model
    max_len = 128
    prefix_len = 8  # fixed prefix length used by every trained skill


# ---------------------------------------------------------------------------
# Attention with optional prefix K/V splice
# ---------------------------------------------------------------------------

class CausalSelfAttention(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.n_heads = cfg.n_heads
        self.d_head = cfg.d_head
        self.q_proj = nn.Linear(cfg.d_model, cfg.d_model)
        self.k_proj = nn.Linear(cfg.d_model, cfg.d_model)
        self.v_proj = nn.Linear(cfg.d_model, cfg.d_model)
        self.out_proj = nn.Linear(cfg.d_model, cfg.d_model)

    def _split_heads(self, x):
        # x: [B, T, D] -> [B, H, T, Dh]
        B, T, D = x.shape
        return x.view(B, T, self.n_heads, self.d_head).transpose(1, 2)

    def forward(self, x, prefix_kv=None):
        """
        x: [B, T, D] real-token hidden states.
        prefix_kv: optional (prefix_k, prefix_v), each [H, P, Dh] (shared
            across the batch) -- this IS the trained "skill" for this layer.
        """
        B, T, D = x.shape
        q = self._split_heads(self.q_proj(x))  # [B,H,T,Dh]
        k = self._split_heads(self.k_proj(x))  # [B,H,T,Dh]
        v = self._split_heads(self.v_proj(x))  # [B,H,T,Dh]

        if prefix_kv is not None:
            pk, pv = prefix_kv  # [H, P, Dh] each
            P = pk.shape[1]
            pk = pk.unsqueeze(0).expand(B, -1, -1, -1)  # [B,H,P,Dh]
            pv = pv.unsqueeze(0).expand(B, -1, -1, -1)
            k = torch.cat([pk, k], dim=2)  # [B,H,P+T,Dh]
            v = torch.cat([pv, v], dim=2)
        else:
            P = 0

        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.d_head)
        # [B,H,T,P+T]

        # Build the mask: prefix columns (first P) are always visible.
        # Real-token columns (last T) follow standard causal masking.
        causal = torch.tril(torch.ones(T, T, device=x.device, dtype=torch.bool))
        prefix_visible = torch.ones(T, P, device=x.device, dtype=torch.bool)
        full_mask = torch.cat([prefix_visible, causal], dim=1)  # [T, P+T]
        attn_scores = attn_scores.masked_fill(~full_mask, float("-inf"))

        attn = F.softmax(attn_scores, dim=-1)
        out = torch.matmul(attn, v)  # [B,H,T,Dh]
        out = out.transpose(1, 2).contiguous().view(B, T, D)
        return self.out_proj(out)


class Block(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.d_model)
        self.attn = CausalSelfAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg.d_model)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.d_model, cfg.d_ff),
            nn.GELU(),
            nn.Linear(cfg.d_ff, cfg.d_model),
        )

    def forward(self, x, prefix_kv=None):
        x = x + self.attn(self.ln1(x), prefix_kv=prefix_kv)
        x = x + self.mlp(self.ln2(x))
        return x


class TinyTransformer(nn.Module):
    """Decoder-only causal LM. Also used, unmodified, as SkillSmith's own
    backbone in skillsmith.py (a second independent instance)."""

    def __init__(self, cfg: Config = Config()):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.pos_emb = nn.Embedding(cfg.max_len, cfg.d_model)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layers)])
        self.ln_f = nn.LayerNorm(cfg.d_model)
        self.head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        self.head.weight = self.tok_emb.weight  # weight tying

    def embed_tokens(self, ids):
        """ids: [B, T] -> token+pos embeddings [B, T, D]. Exposed separately
        so SkillSmith can splice in non-token embeddings at chosen positions."""
        B, T = ids.shape
        pos = torch.arange(T, device=ids.device).unsqueeze(0).expand(B, T)
        return self.tok_emb(ids) + self.pos_emb(pos)

    def forward_hidden(self, x, prefix=None):
        """x: [B, T, D] already-built input embeddings.
        prefix: optional per-layer prefix tensor, shape
            [n_layers, 2, n_heads, prefix_len, d_head] (the trained "skill").
        Returns final hidden states [B, T, D] (post-LN, pre-head) -- this is
        what SkillSmith reads out at its placeholder-slot positions."""
        for l, block in enumerate(self.blocks):
            layer_prefix = None
            if prefix is not None:
                layer_prefix = (prefix[l, 0], prefix[l, 1])  # (k, v) each [H,P,Dh]
            x = block(x, prefix_kv=layer_prefix)
        return self.ln_f(x)

    def forward_embeds(self, x, prefix=None):
        """x: [B, T, D] already-built input embeddings.
        Returns logits [B, T, vocab_size]."""
        hidden = self.forward_hidden(x, prefix=prefix)
        return self.head(hidden)

    def forward(self, ids, prefix=None):
        x = self.embed_tokens(ids)
        return self.forward_embeds(x, prefix=prefix)


def new_prefix_param(cfg: Config = Config(), init_scale=0.02):
    """A trainable 'skill' tensor: [n_layers, 2, n_heads, prefix_len, d_head]."""
    shape = (cfg.n_layers, 2, cfg.n_heads, cfg.prefix_len, cfg.d_head)
    return nn.Parameter(torch.randn(shape) * init_scale)


def prefix_numel(cfg: Config = Config()):
    return cfg.n_layers * 2 * cfg.n_heads * cfg.prefix_len * cfg.d_head
