# vLLM & Paged Attention: Why the Inference Engine Matters More Than the Model

## 5 Intuitive Takeaways

1. **The same model runs at wildly different speeds depending on the inference engine** — LLMs don't have a fixed "speed." The system serving them (vLLM, llama.cpp, TensorRT-LLM, etc.) determines tokens-per-second. Choosing the wrong engine is like putting a race car engine on a bicycle frame — the model's capability is bottlenecked by the serving infrastructure.

2. **The KV cache is the hidden bottleneck killing multi-user performance** — during inference, every request stores key-value pairs in GPU memory. Traditional systems pre-allocate worst-case memory for every request, meaning a short 10-token prompt gets the same memory block as a 2,000-token one. Result: 60-80% of GPU memory is wasted on empty space, and you can only serve a fraction of the concurrent users your hardware could actually handle.

3. **Paged attention solves this by stealing an idea from operating systems** — just like your OS doesn't pre-allocate all RAM for a process but uses virtual memory pages allocated on demand, vLLM breaks the KV cache into small fixed-size pages that grow dynamically. Memory utilization jumps from ~20% to ~95%, meaning 4-5x more concurrent users on the same GPU.

4. **vLLM's OpenAI-compatible API means zero migration cost** — it exposes the same API contract as OpenAI, so any app already using the OpenAI SDK can switch to a self-hosted vLLM server by changing one URL. This decouples your application code from your inference provider — a critical architectural boundary for production systems.

5. **Production LLM serving is a tuning game, not a deploy-and-forget task** — you must tune `max_model_len` (memory per request) and `max_num_seqs` (concurrency limit) for your specific workload. Short prompts need lower context lengths; high-traffic apps need higher sequence limits. Without monitoring tokens/sec and latency in production, you're flying blind on when to scale.
