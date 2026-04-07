# LLM Quantization: Why Inference Costs Dwarf Training and How Compression Saves You 3x GPUs

## 5 Intuitive Takeaways

1. **The majority of AI cost is in inference, not training** — training happens once; inference runs 24/7 for every chatbot query, RAG lookup, and agent action across all your users. Every AI application (chatbots, document processing, vibe coding, agents) is powered by inference under the hood. Optimizing inference is where the real money is saved.

2. **Quantization shrinks model precision from 16-bit to 8-bit or 4-bit, cutting GPU requirements by 2-3x** — a 109B parameter model at BFLOAT16 needs ~220GB (three 80GB GPUs). At INT8, it's ~109GB (two GPUs). At INT4, it's ~55GB (one GPU). You go from $30,000+ in GPU hardware to $10,000 by applying smart scaling algorithms that preserve the model's behavior while halving or quartering the bytes per parameter.

3. **The accuracy loss is surprisingly negligible** — after 500,000+ evaluations on quantized models, benchmarks show less than 1% degradation in accuracy from the original full-precision model. In some cases, quantization's regularization effect can even slightly improve performance. You're not trading quality for cost — you're eliminating waste.

4. **Online vs. offline inference need different quantization strategies** — for real-time apps (chatbots, agents) where latency matters and GPUs aren't always fully utilized, weight-only quantization (W8A16) is optimal. For batch processing (analyzing thousands of transcripts) where GPUs run at full capacity, formats like FP8 or INT8 accelerate computation throughput. The quantization scheme must match the workload pattern.

5. **The practical workflow: Hugging Face → LLM Compressor → vLLM → API endpoint** — you pull a pre-trained model from Hugging Face, apply quantization using open-source tools like LLM Compressor (part of the vLLM ecosystem), save the compressed model, and serve it through vLLM as an OpenAI-compatible API. This pipeline takes you from a 3-GPU monster to a single-GPU production server your developers can share across the organization.
