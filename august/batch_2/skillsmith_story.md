# Teaching a Model to Read Its Own Weights

## The scene

An agent has two things sitting in its memory: a trained prefix-cache for English-to-Twi translation, and a pile of notes on parsing legal documents. A new task shows up — a legal contract written in Twi. The agent can *say*, in plain English, exactly which two skills it needs to combine. It just has no way to actually do it.

## Why it hurts

This is the quiet failure mode of every agent that "learns from experience." Text-based reflection scales beautifully but hits the context window wall — you can't paste a whole skill's worth of examples into every prompt forever. Weight-space skills (LoRA adapters, prefix caches) scale the other way: compact and reusable, but merged with dumb arithmetic — averaging two KV-caches together, or just concatenating them and hoping.

## What's actually happening underneath

Averaging two prefix-caches assumes the skills live in compatible, linearly combinable directions in weight-space. They usually don't. The system has rich text explaining *how* two skills relate to a new goal, and it has the actual trained weights for each skill — but nothing ever reads both at once. Two full modalities, developed in the same agent, that never talk to each other.

## The shift

**Treat model weights as just another sequence the model can read — not cargo to be shipped, but tokens to be reasoned over.** A KV-cache gets projected into the same latent space as text, interleaved with source descriptions and a combination-text explaining the target task, then fed through the model itself.

## The fix

The model — SkillSmith — ingests interleaved text-and-cache "bundles" and outputs a brand-new prefix-cache, generated the way it would generate any other token sequence. Fine-tuned further on the actual target task, this beats both naive weight-averaging and pure in-context learning, especially when data is scarce.

## The question to sit with

How much of what your system "knows" is sitting in two formats that have never been asked to talk to each other?
