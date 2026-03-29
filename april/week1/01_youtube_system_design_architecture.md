# Designing YouTube: The Architecture Behind Upload and Watch at Billion-User Scale

**Intuitive Takeaways (5 Key Points)**

- **Separate the heavy path (upload) from the fast path (watch):** Uploading a video triggers an asynchronous pipeline — raw files land in object storage, get queued for encoding by ~30,000 parallel workers, and only then are the compressed files distributed via CDN. Watching, by contrast, is a pure read path optimized for speed: CDN for video chunks, in-memory cache (LRU) for metadata. The entire architecture is shaped by the fact that reads outnumber writes 100:1.

- **Videos are streamed as small HTTP chunks over TCP, not downloaded whole:** Your browser never holds the full video in memory. It fetches small segments on demand via standard HTTP/TCP requests — audio and video tracks separately. This is why skipping ahead in a video triggers a new network request for just that segment. TCP is chosen over UDP because, unlike live streaming, pre-recorded content demands reliability (no missing frames), and chunking keeps latency low enough.

- **Availability beats consistency — and that's a deliberate trade-off:** The system is designed so that refreshing your feed always returns *something* (HTTP 200), even if a brand-new upload takes 5–10 seconds to appear across all replicas. Stale data for a few seconds is vastly preferable to a failed or empty page. This is the CAP theorem in action: at billion-user scale, you choose AP (availability + partition tolerance) over strong consistency.

- **NoSQL with denormalized data trades write pain for read speed:** Instead of joining a `videos` table with a `users` table on every read, the creator's profile info (e.g., avatar URL) is duplicated inside every video document. Updating a profile picture means touching hundreds or thousands of documents — but that's rare and can happen asynchronously. The system optimizes for the overwhelmingly common case: reading video metadata fast, without joins.

- **Even MySQL can scale — if you decouple the app from the shard logic:** YouTube historically ran on MySQL, not NoSQL. When read replicas weren't enough, they sharded — but embedding shard-routing logic in the application layer became unsustainable. The solution was Vitess, a middleware that abstracts sharding away from the application. The lesson: the database engine matters less than the architecture around it. Constraints breed infrastructure (Vitess was later open-sourced and powers products like PlanetScale).
