# The Physics of Prompt Optimization: Why Better Reasoning Still Fails on Broken Inputs

## The Trap

We assume stronger models fail because they cannot reason enough. A model can reason and still collapse if the seed prompt encodes the wrong structure. **What if the real failure is not intelligence, but the shape of the search space?**

## The Shift

Stop thinking in smarter models. Start thinking in better hypothesis coverage.

- A prompt can trap optimization in a local basin.
- More iterations do not escape missing categories.
- Structural defects survive when the system cannot name them.

## The Architecture

The optimizer separates:

- hypothesis generation
- prompt rewriting
- empirical verification

That matters because prompt optimization is not rewriting text. It is diagnosing failure modes, testing fixes, and recording traces.

## Sit With This

If the mistake never enters the model's hypothesis space, what are you scaling?