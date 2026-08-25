"""Synthetic character-transform 'skills' and their compositions.

Each base skill is a pure string -> string function. A 'composite task' is
just skill_j applied after skill_i on the same random input -- the toy
analogue of Composite-SNI's "task requiring the combined skill sets of two
input tasks".
"""

import random

random.seed(0)

LOWER = "abcdefghijklmnopqrstuvwxyz"


def reverse_fn(s):
    return s[::-1]


def upper_fn(s):
    return s.upper()


def dup_fn(s):
    return "".join(ch * 2 for ch in s)


def shift_fn(s):
    def shift_char(c):
        if c in LOWER:
            return LOWER[(LOWER.index(c) + 1) % 26]
        return c
    return "".join(shift_char(c) for c in s)


SKILLS = {
    "reverse": reverse_fn,
    "upper": upper_fn,
    "dup": dup_fn,
    "shift": shift_fn,
}

SKILL_DESCRIPTIONS = {
    "reverse": "Task: reverse the order of characters in the input string.",
    "upper": "Task: convert every letter in the input string to uppercase.",
    "dup": "Task: duplicate every character in the input string twice.",
    "shift": "Task: shift every lowercase letter forward by one in the alphabet.",
}


def random_input(min_len=3, max_len=6):
    n = random.randint(min_len, max_len)
    return "".join(random.choice(LOWER) for _ in range(n))


def make_skill_dataset(skill_name, n_examples=400):
    fn = SKILLS[skill_name]
    data = []
    for _ in range(n_examples):
        x = random_input()
        y = fn(x)
        data.append((x, y))
    return data


def compose_name(i, j):
    return f"{i}+{j}"


def make_composite_dataset(skill_i, skill_j, n_examples=400):
    fi, fj = SKILLS[skill_i], SKILLS[skill_j]
    data = []
    for _ in range(n_examples):
        x = random_input()
        y = fj(fi(x))
        data.append((x, y))
    return data


def combination_text(skill_i, skill_j):
    return (
        f"Combine the two source skills in sequence to solve the target task: "
        f"first apply '{skill_i}', then apply '{skill_j}' to the result."
    )


# All ordered pairs (i != j) over the 4 base skills -> 12 possible composites.
ALL_PAIRS = [(i, j) for i in SKILLS for j in SKILLS if i != j]

# Split into meta-train (SkillSmith learns to fuse these) and meta-test
# (SkillSmith must generalize to these combinations, never trained on them,
# mirroring the paper's held-out "Neither-Seen"-style composite evaluation).
META_TRAIN_PAIRS = [
    ("reverse", "upper"),
    ("upper", "reverse"),
    ("reverse", "dup"),
    ("dup", "reverse"),
    ("upper", "dup"),
    ("dup", "upper"),
    ("shift", "upper"),
    ("upper", "shift"),
]
META_TEST_PAIRS = [
    ("reverse", "shift"),
    ("shift", "reverse"),
    ("dup", "shift"),
    ("shift", "dup"),
]

assert set(META_TRAIN_PAIRS) | set(META_TEST_PAIRS) == set(ALL_PAIRS)
assert set(META_TRAIN_PAIRS).isdisjoint(META_TEST_PAIRS)
