# WebRTC: When Peer-to-Peer Eats Itself

### The scene

Eight people join the video call. The bandwidth monitor spikes. Faces pixelate, audio cuts out, someone says "can you hear me?" for the third time. The call is six minutes old. Nothing is broken. The math just caught up.

### Why it hurts

Your peer-to-peer design was elegant in the demo — two browsers, one direct connection, no servers in the middle. But eight people means each person uploads seven simultaneous video streams. Home upload bandwidth can't survive that. Laptops encoding seven copies of the same face in real time can't either. The call collapses — not from a bug, from geometry.

### What's actually happening underneath

Pure peer-to-peer grows quadratically. N people means N×(N-1) total streams. Ten people: 90 streams. And underneath all of it sits a second decision that shaped the whole design: **WebRTC runs on UDP, not TCP**.

TCP blocks the entire stream to retransmit a lost packet. That pause — 100 to 200ms — is fine when loading a webpage. For a live call, it's catastrophic. A packet that arrives 300ms late is worse than one that never arrives. You'd rather drop one frame than freeze the entire call waiting for it.

### The shift

**Late data is dead data.** Once you internalize this, the whole architecture makes sense. You aren't trading reliability for speed as a compromise. You're trading correctness for time — deliberately, correctly.

### The fix

The SFU — selective forwarding unit — collapses the quadratic. Every peer uploads once. The SFU forwards to everyone else. Linear, not squared. It never decodes video. It rewrites packet headers and routes. Cheap. Fast. And because it sits in the middle, it makes per-viewer decisions: low resolution to the thumbnail, full HD to the pinned speaker, silence to the muted mic. That's what "selective" means.

Pure peer-to-peer works for two people. Maybe three. The SFU is how the rest of production ships.

### The question to sit with

How many streams is your "simple" real-time feature actually generating when ten users connect at once?
