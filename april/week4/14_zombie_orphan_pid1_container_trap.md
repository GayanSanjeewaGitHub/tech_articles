# Zombie Processes and the PID 1 Trap in Containers

## The Problem: Your Container Leaks Processes Until It Dies

Your app runs as PID 1 inside a container. Child processes exit, but nobody reaps them. The process table fills with zombies — processes that consume no CPU or memory but **occupy process table entries**. Eventually, the kernel refuses to create new processes. Your container is alive but can't do anything.

- **Zombies accumulate silently** — they don't consume resources until hundreds pile up and exhaust PID space
- **SIGTERM is ignored** — your app is PID 1 but never registered a signal handler, so the kernel sends SIGKILL instead. No graceful shutdown
- **Database connections hang open** — no chance to drain requests, flush buffers, or close connections
- **Orphan processes go unreaped** — if a parent dies before its child, the child becomes orphan. Normally PID 1 (init) adopts and reaps it. Your app is PID 1 but **doesn't know how to be init**

## Why This Happens

The normal process exit sequence:

1. Child calls `exit()` → kernel sets state to **Z (zombie)**
2. Kernel sends exit code to parent
3. Parent calls `wait()` / `waitpid()` → reads exit code
4. Kernel removes child from process table

**If the parent never calls `wait()`**, step 4 never happens. The zombie stays forever.

In containers, your app inherits PID 1 — a role designed for init systems that:
- Reap orphaned child processes
- Forward signals to children
- Handle `SIGTERM` for graceful shutdown

**Your application does none of this.** It wears the PID 1 hat without knowing the responsibilities.

## The Mental Model Shift

> **Your containerized app isn't just a process — it's accidentally the init system. If it doesn't act like one, the container rots from the inside.**

| Process State | Meaning | Danger |
|---|---|---|
| **Running** | Actively executing | Normal |
| **Sleeping** | Waiting for I/O | Normal for web servers |
| **Uninterruptible Sleep** | Waiting for I/O, unkillable | NFS hangs, can't even `kill -9` |
| **Zombie (Z)** | Exited, parent hasn't called `wait()` | Process table fills up |
| **Stopped** | Paused, needs explicit resume | Different from sleeping |

## Real Consequences

- **Zombie flood:** A web server forks handler processes. Each exits but the parent never calls `waitpid()`. After hours, hundreds of zombies fill the process table → container can't spawn new workers → **service down**
- **No graceful shutdown:** Kubernetes sends SIGTERM to PID 1. Your app doesn't handle it. After 30s, Kubernetes sends SIGKILL. In-flight requests drop, DB transactions left half-committed
- **Orphan leak:** Parent process crashes. Its children become orphans. PID 1 (your app) doesn't adopt them. They become unreapable zombies

## The Solution

```dockerfile
# Use tini as a lightweight init to handle PID 1 responsibilities
ENTRYPOINT ["tini", "--"]
CMD ["node", "server.js"]
```

Or handle signals explicitly in your app:

```javascript
// Register SIGTERM handler — your app IS PID 1
process.on('SIGTERM', async () => {
  await server.close();       // stop accepting new connections
  await db.disconnect();      // close DB pool
  process.exit(0);            // clean exit
});
```

- **Use a proper init** (tini, dumb-init) as PID 1 entrypoint — it reaps zombies and forwards signals
- **Register signal handlers** if your app must be PID 1
- **Call `wait()`/`waitpid()`** in any process that spawns children

## The Question to Sit With

Your app runs as PID 1 in every container. **Is it designed to be an init system — reaping orphans, forwarding signals, handling graceful shutdown? Or is it just the first process that happened to start, wearing a hat it doesn't know how to use?**
