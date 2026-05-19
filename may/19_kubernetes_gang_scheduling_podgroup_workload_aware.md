# The 400 Workers Doing Nothing

### The scene

A 512-GPU training job starts binding. Workers come up one by one. After 20 minutes, 400 are running — GPUs allocated, processes warm, memory loaded. The job is doing zero work. The remaining 112 pods are pending. The 400 are just waiting. And they'll keep waiting until the cluster finds capacity that may never come.

### Why it hurts

At $3 per GPU-hour, 400 idle GPUs cost $1,200 every hour they wait. The cluster looks busy. Other jobs can't schedule. No alert fires — nothing is broken. The workload is in a perfectly valid state by every metric the scheduler tracks. That's the problem.

### What's actually happening underneath

Since Kubernetes v1.0, pods are the unit of scheduling. The scheduler pops one pod off the queue, evaluates it, picks a node, binds it, and repeats. For stateless services, this is right — one replica starting late provides incremental value. For distributed training, it's catastrophic. **Scheduling five out of six pods isn't 83% success. It's 0% useful progress plus 83% resource occupancy.** The scheduler committed too early because the API never told it these pods belonged together. It had no concept of the group — no quorum, no collective admission boundary, nothing.

### The shift

**The commit point has to move from the pod to the group.** Partial placement below quorum shouldn't consume resources. The scheduler needs a meaningful decision boundary before it starts binding — not after.

### The fix

Kubernetes introduces a native gang primitive: pods reference a `PodGroup`, which declares a `minCount` quorum. The scheduler holds all pods at a permit barrier until that quorum can be met simultaneously. If the cluster can't fit the group, nothing binds. No partial placement, no idle GPUs. The PreEnqueue plugin parks pods until enough siblings are visible, waking only when a relevant event fires — a new pod or a new PodGroup — not on a polling loop. The commit moves from "this pod fits" to "this group fits."

### The question to sit with

In your cluster today, how many GPU-hours are billing for pods that are technically running but doing no useful work?
