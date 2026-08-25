"""Single entry point: runs the whole toy SkillSmith reproduction end to end.

    python run_pipeline.py

Steps:
  1. Pretrain the frozen base model on a generic 'copy' task.
  2. Train one prefix-tuning 'skill' per base transform (reverse/upper/dup/shift).
  3. Meta-train SkillSmith to fuse pairs of skills into new composite prefixes.
  4. Evaluate every method (LERP, Concat, Direct, ICL, SkillSmith zero-shot,
     SkillSmith fine-tuned) on both seen (meta-train) and unseen (meta-test)
     skill combinations, and print comparison tables.
"""

import os
import time
import torch

from model import Config
from train_base import train_base_model
from train_skill_prefix import train_all_skill_prefixes
from skillsmith import meta_train_skillsmith
import tasks
import evaluate

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def main():
    t0 = time.time()
    torch.manual_seed(0)
    os.makedirs("skill_prefixes", exist_ok=True)

    print(f"Device: {DEVICE}\n")

    print("### Step 1/4: pretrain frozen base model on generic 'copy' task ###")
    base_model = train_base_model(steps=800)
    torch.save(base_model.state_dict(), "base_model.pt")

    print("\n### Step 2/4: train one prefix per base skill ###")
    skill_prefixes = train_all_skill_prefixes(base_model)
    skill_descriptions = tasks.SKILL_DESCRIPTIONS

    print("\n### Step 3/4: meta-train SkillSmith on seen skill combinations ###")
    skillsmith = meta_train_skillsmith(
        base_model, skill_prefixes, skill_descriptions, tasks.META_TRAIN_PAIRS,
        steps=600,
    )
    torch.save(skillsmith.state_dict(), "skillsmith.pt")

    print("\n### Step 4/4: evaluate all methods ###")
    rows_train = evaluate.run_comparison(
        base_model, skill_prefixes, skillsmith, tasks.META_TRAIN_PAIRS,
        split_name="SEEN combinations (meta-train pairs)",
    )
    rows_test = evaluate.run_comparison(
        base_model, skill_prefixes, skillsmith, tasks.META_TEST_PAIRS,
        split_name="UNSEEN combinations (meta-test pairs, held out)",
    )

    evaluate.print_summary(rows_train, "SEEN combinations")
    evaluate.print_summary(rows_test, "UNSEEN combinations")

    print(f"\nTotal wall-clock time: {time.time() - t0:.1f}s")
    print(
        "\nExpected qualitative result (matching the paper's Figure 3 / Table 1):\n"
        "  - LERP and Concat (naive weight-space merging) are mediocre on both splits.\n"
        "  - Direct-from-scratch is weak on the SEEN split too (little data) but can\n"
        "    catch up somewhat since these toy tasks are simple.\n"
        "  - ICL is a strong zero-shot baseline but doesn't improve with more compute.\n"
        "  - SkillSmith (zero-shot) should already beat LERP/Concat.\n"
        "  - SkillSmith (fine-tuned) should be the best or tied-best method overall,\n"
        "    including on the UNSEEN split -- i.e. it generalizes to skill\n"
        "    combinations it never saw fused during meta-training."
    )


if __name__ == "__main__":
    main()
