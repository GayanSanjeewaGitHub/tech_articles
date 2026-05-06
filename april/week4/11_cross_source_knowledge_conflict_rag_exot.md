# Cross-Source Knowledge Conflicts: Why Your RAG System Trusts the Wrong Evidence

## The Problem: Conflicting Sources Collapse Your LLM's Reasoning

You have a multi-agent RAG system. One agent retrieves structured knowledge graph triples. Another retrieves unstructured text from documents or the web. Both return evidence for the same query. **The evidence contradicts itself.** Your LLM picks the wrong one — not based on content, but based on format.

- **With coherent data:** GPT-class models achieve ~87% accuracy
- **With one conflicting source:** accuracy drops to **32%** — a 55-percentage-point collapse
- **For smaller models (8B):** accuracy drops from 76% to **7%** — a 90% loss of system capability
- The LLM doesn't verify. It picks whichever format *looks* more authoritative and **actively hallucinates reasoning to justify the wrong answer**

## Why This Happens

- **Format bias from pre-training:** LLMs were trained on internet data where long, detailed text correlates with accuracy. So they treat verbose paragraphs as inherently more trustworthy — even when the content is false
- **Concise triples trigger shortcutting:** Knowledge graph triples are so dense that in direct Q&A, the model skips reasoning entirely and jumps to the entity — even if it's adversarially injected
- **Chain-of-thought makes it worse for text conflicts:** CoT forces the model to attend heavily to narrative-rich text, creating a positive feedback loop that locks onto the wrong source

**The rationalization trap:** When the LLM encounters a correct knowledge graph triple and an incorrect verbose text, it doesn't just make an error — it **uses its intelligence to construct a sophisticated, logically-sounding narrative** that bridges the true starting fact to the false conclusion. The model hallucinates a coherent reasoning chain to justify the wrong answer.

## The Mental Model Shift

> **Stop feeding heterogeneous evidence formats directly to your LLM. Normalize all evidence into a format-agnostic representation before any reasoning begins.**

- **Old:** Knowledge graph triple + text paragraph → feed both to LLM → trust the output
- **New:** Knowledge graph triple → normalize to neutral sentence. Text paragraph → normalize to neutral sentence. **Then** reason over structurally identical inputs
- **Old:** Chain-of-thought always improves reasoning
- **New:** CoT amplifies format bias — it's not a universal fix

## The Solution: Explanation-Based Thinking (ExoT)

A two-stage cognitive architecture that decouples evidence normalization from judgment:

**Stage 1 — Format-Agnostic Normalization (zero judgment):**
- For each candidate answer, generate a supporting explanation as a plain sentence
- Knowledge graph `(Nixon, place_of_death, NYC)` → "Nixon's place of death was New York City"
- 300-word text passage → "LA is mentioned as a place of death for Nixon"
- Both are now structurally identical strings of roughly equal token length

**Stage 2 — Homogeneous Logical Arbitration:**
- Evaluate normalized explanations against the query constraints
- Integrate the LLM's parametric knowledge
- Decide based on **content and logic**, not format

| Aspect | Direct RAG Fusion | ExoT Normalization |
|---|---|---|
| Evidence format | Heterogeneous (triples + paragraphs) | Homogeneous (neutral sentences) |
| Attention bias | Format hijacks reasoning | Format stripped before reasoning |
| CoT behavior | Amplifies verbose-text bias | Operates on equal-length inputs |
| Judgment basis | Surface form of evidence | Semantic content of evidence |

**Critical caveat:** This is a workaround, not a cure. The root pathology lives in pre-training data representation — how formats were correlated with accuracy during training. Until models are pre-trained with adversarial format diversity, this architectural firewall is necessary.

## The Question to Sit With

Your multi-agent system sends three agents to three different sources. They return contradictory evidence in different formats. **Your LLM is choosing which source to trust based on whether the answer came as a paragraph or a triple — not based on whether the answer is correct.** How many of your RAG system's "wrong answers" are actually format-preference bugs masquerading as reasoning failures?
