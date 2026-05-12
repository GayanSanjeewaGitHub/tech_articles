# The Partition Tax

### The scene

It's Black Friday minus two days. The order processing pipeline is backed up. The Kafka consumer lag dashboard shows 800,000 messages sitting unprocessed. You have twelve worker pods idle. Kafka has six partitions on that topic. Six pods are working. Six are doing nothing — no messages to pull, no lag to drain.

### Why it hurts

You call the on-call engineer. The answer comes back immediately: "We can't rebalance twelve workers onto six partitions. Kafka won't let us." The fix is to re-partition the topic. That means a migration window, a coordinated restart, and a post-incident review. Tonight. Two days before the peak you've been planning for since August.

### What's actually happening underneath

Kafka's Consumer Group model is partition-bound. One partition belongs to one consumer at a time. If you have six partitions and twelve workers, six workers are always idle — by design. The only way to use more consumers is to add more partitions. Partitions are pre-declared. You cannot add them without operational friction.

**This was never a bug. It's the streaming model applied to a task queue problem.** Kafka was built for ordered, replayable event streams. Consumer Groups are excellent at that. They are awkward for worker pools — where ordering doesn't matter, where you just need the next available job to land on the next available worker.

### The shift

**Share Groups decouple consumption from partition assignment.** Any consumer in a Share Group can claim any available message — regardless of partition. The partition is still there for storage and durability. It just stops being the unit of work distribution.

### The fix

With Kafka 4.2, you create a Share Group instead of a Consumer Group. Twelve workers start. Messages are dispatched to whichever worker is free first. No partition math. No pre-planning. No idle pods while lag climbs.

```java
// Before: partition-bound, six partitions = six active workers max
KafkaConsumer<String, Order> consumer = new KafkaConsumer<>(props);
consumer.subscribe(List.of("orders"));

// After: Share Group — any of twelve workers can pull next message
props.put("group.type", "share");
KafkaConsumer<String, Order> consumer = new KafkaConsumer<>(props);
consumer.subscribe(List.of("orders"));
```

Same topic. Same durability. Same Kafka. The consumer group type is the only change.

### The question to sit with

How many of your Kafka topics are actually task queues that have been paying the partition tax for years?
