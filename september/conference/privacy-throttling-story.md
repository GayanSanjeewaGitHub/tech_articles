### The scene

A city opens up its public CCTV feed to the public — real cameras, real locations, real time. Someone builds a map that plugs straight into it. Click a camera, watch the intersection live. It's exactly the transparency everyone asked for.

### Why it hurts

Real-time plus full frame rate means anyone can pick a single car and just... follow it. Door to door, block to block, camera to camera, live. That's not traffic monitoring anymore, that's stalking-as-a-feature — and it's exactly the reason most cities never open this data at all. The useful thing and the dangerous thing turn out to be the same feed.

### What's actually happening underneath

The risk was never really about resolution, and it was never really about freshness — it's about having both at once. High spatial detail plus continuous temporal sampling is what lets you stitch a stream of frames into a trajectory: this car, this street, this time, and the next one, and the next. Break either axis alone and the picture you actually want — where's it congested right now — barely changes. Break both, and you've killed the feed's usefulness along with its risk.

### The shift

**Privacy isn't a resolution problem, it's a reconstruction problem — so you don't have to blur the picture, you just have to break the chain that lets frames become a trajectory.**

### The fix

Ship the real, full-resolution image — but refresh it once every five to ten minutes instead of thirty times a second. A snapshot that sharp is useless for tracking a specific vehicle continuously, since it vanishes into a gap before you can follow it anywhere. But it's more than enough to show a city-wide congestion map in real time, hotspots and all. One throttled axis, both goals intact.

### The question to sit with

In your own system, is there one axis — frequency, granularity, latency — you could quietly degrade to remove the misuse case without touching the value case?
