# Prefill as a Service: Why LLM Inference Can Finally Split Across Data Centers

## The Problem: Prefill and Decode Are Glued Together

When you send a long prompt to an LLM — a 50-page report, a massive codebase — the system does two fundamentally different jobs on the same expensive hardware:

- **Prefill stage:** Read and encode the entire input into a KV cache. This is **compute-bound** — it needs raw GPU throughput
- **Decode stage:** Generate tokens one at a time. This is **memory-bandwidth-bound** — it needs fast access to the KV cache

Both stages are forced into the same high-speed cluster because the KV cache between them is enormous — gigabytes of data that must transfer at ultra-low latency. The result:

- **Clusters sit half-idle** — prefill needs compute, decode needs memory bandwidth. Neither fully utilizes the hardware the other needs
- **Long-context requests choke during peak hours** — prefill and decode compete for the same GPUs
- **Scaling means buying more of the same expensive, rigid clusters** — you can't independently scale the part that's bottlenecked

## Why This Happens

- Traditional transformer KV caches are **massive** — every attention layer stores full key-value pairs for every token. A long-context request generates GBs of cache
- Transferring GBs between clusters requires **dedicated high-speed interconnects** (InfiniBand, NVLink) — not regular Ethernet
- This forces both stages into the **same physical data center**, on the **same network fabric**

**The hidden assumption:** We treat prefill and decode as inseparable because the data bridge between them has always been too large to move cheaply.

## The Mental Model Shift

> **Stop treating prefill and decode as one monolithic job. Treat them as two independent services with a small data contract between them.**

- **Old:** KV cache is too large to move → both stages must co-locate
- **New:** Hybrid models (MLA/GQA) shrink KV caches dramatically → the cache fits over regular Ethernet → stages can live in separate data centers

## The Solution: Disaggregated Inference

New hybrid model architectures compress the KV cache small enough to transfer over commodity networks. This enables:

- **Dedicated prefill clusters** — optimized purely for compute throughput, located wherever GPU capacity is cheapest
- **Dedicated decode clusters** — optimized for memory bandwidth, co-located with users for low latency
- **Smart cache pooling** — reusable cache segments (system prompts, shared context) stay local; only the small unique portions transfer cross-datacenter
- **Short requests stay local** — only long-context, compute-heavy prefills get routed to the remote cluster

| Aspect | Co-located (Today) | Disaggregated (PRFast) |
|---|---|---|
| Hardware | Same expensive cluster for both stages | Best hardware for each job independently |
| Scaling | Scale everything together | Scale prefill and decode independently |
| Network requirement | High-speed interconnect (InfiniBand) | Regular Ethernet sufficient for compressed KV cache |
| Utilization | GPUs half-idle (wrong bottleneck) | Each cluster fully utilized for its workload |
| Long-context cost | Expensive, competes with decode | Offloaded to cheap compute clusters |

## The Question to Sit With

If the only thing keeping LLM inference expensive and rigid was the **size of the data bridge between two stages** — and new model architectures just shrunk that bridge by orders of magnitude — **how much of your current inference infrastructure is over-provisioned for a constraint that no longer exists?**
