# Building a Redis Drop-In Replacement: Why PING Teaches You More Than You Think

## The Problem: You Can't Replace What You Don't Speak

You want to build a custom in-memory data store — faster, simpler, or specialized for your use case. You write a TCP server, accept connections, handle bytes. But when you point `redis-cli` at it, **nothing works**.

- The client sends bytes your server can't parse
- Your server responds with raw strings the client can't decode
- Error messages don't render — the CLI just hangs or crashes
- You can't use any existing Redis tooling (benchmarks, test suites, monitoring) against your implementation

**The core problem:** Redis clients and servers communicate through a strict wire protocol called **RESP (Redis Serialization Protocol)**. If your server doesn't encode and decode RESP exactly right, it's not a drop-in replacement — it's a toy that speaks a different language.

## Why This Happens

- Most developers think "Redis is a key-value store" — but at the network layer, **Redis is a protocol**
- Every command, every response, every error has a specific byte-level encoding format
- Simple strings (`+OK\r\n`), bulk strings (`$5\r\nhello\r\n`), and errors (`-ERR message\r\n`) are **different wire types** — mixing them up breaks client parsing
- A command like `PING` looks trivial, but it exercises **three different response paths**: simple string, bulk string, and error

**Ask yourself:** If `PING` requires handling three distinct encoding cases, how many edge cases does `SET` or `GET` introduce?

## The Mental Model Shift

> **Stop thinking of Redis commands as functions. Start thinking of them as RESP decode → evaluate → RESP encode pipelines.**

- **Old thinking:** "PING returns PONG" → just write `conn.Write([]byte("PONG"))`
- **New thinking:** Every command is: `raw bytes → decode to string array → route to eval function → encode response to RESP → write bytes`
- The command name and arguments always arrive as a **RESP array of bulk strings** — regardless of what the command does
- The response type depends on the command semantics, not the input type

## What Happens If You Ignore This

- **Scenario 1:** Your server responds with raw `"PONG"` instead of `"+PONG\r\n"`. The redis-cli receives garbage, displays nothing, or disconnects. You spend hours debugging "why the client doesn't work" when the server is the one speaking broken protocol.
- **Scenario 2:** `PING hello` should return a **bulk string** (`$5\r\nhello\r\n`), but your server returns a simple string (`+hello\r\n`). Most clients silently accept it — until a client library parses the type prefix and throws an unexpected-type error in production.
- **Scenario 3:** `PING hello world` should return an error. Without argument validation, your server silently picks the first argument or concatenates both — now your drop-in replacement has subtly different behavior that breaks integration tests.

## The Approach: Command Structure + RESP Pipeline

Every Redis command follows the same skeleton:

- **Decode** incoming bytes into an array of strings
- **Route** based on `tokens[0]` (the command name)
- **Evaluate** with `tokens[1:]` (the arguments)
- **Encode** the result back into the correct RESP type
- **Write** encoded bytes to the TCP connection

```go
// Command structure — every Redis command has this shape
type RedisCmd struct {
    Cmd  string   // "PING", "SET", "GET", etc.
    Args []string // everything after the command name
}

// Decoding: raw bytes → structured command
tokens := decodeArrayString(buffer) // RESP decode + typecast
cmd := RedisCmd{
    Cmd:  strings.ToUpper(tokens[0]),
    Args: tokens[1:],
}
```

### The PING Evaluation — Three Cases, Three Encodings

```go
func evalPing(args []string) ([]byte, error) {
    if len(args) > 1 {
        // Case 3: too many args → RESP error
        return nil, errors.New("ERR wrong number of arguments for 'ping' command")
    }
    if len(args) == 0 {
        // Case 1: no args → simple string "PONG"
        return encode("PONG", true), nil  // +PONG\r\n
    }
    // Case 2: one arg → bulk string echo
    return encode(args[0], false), nil     // $N\r\n<arg>\r\n
}
```

### Encoding: Simple String vs. Bulk String

```go
func encode(value string, isSimple bool) []byte {
    if isSimple {
        // Simple string: +<value>\r\n
        return []byte(fmt.Sprintf("+%s\r\n", value))
    }
    // Bulk string: $<length>\r\n<value>\r\n
    return []byte(fmt.Sprintf("$%d\r\n%s\r\n", len(value), value))
}

func respondError(conn net.Conn, err error) {
    // Error: -<message>\r\n
    conn.Write([]byte(fmt.Sprintf("-%s\r\n", err.Error())))
}
```

## The Solution: A Testable Drop-In Replacement

| Aspect | Toy TCP Server | RESP-Compliant Drop-In |
|---|---|---|
| Client compatibility | Custom client only | Any Redis client/CLI works |
| Testability | Write your own tests | Use `redis-benchmark` out of the box |
| Error handling | Silent failures | Protocol-correct error responses |
| Response types | One format fits all | Correct encoding per command semantics |
| Extensibility | Rewrite parsing per command | Same decode→eval→encode pipeline for every command |

The key architectural win of building a **drop-in replacement** rather than a custom protocol:

- **Reuse `redis-benchmark`** to stress-test your server (10,000 PINGs at comparable throughput to real Redis)
- **Reuse `redis-cli`** for interactive debugging — zero custom tooling needed
- **Every new command** follows the same pipeline: add an eval function, handle argument validation, encode the response
- **Benchmark comparison is trivial** — same tool, different port

## The Question to Sit With

PING is the simplest Redis command — and it already requires three response encodings, argument validation, and strict protocol compliance. **If the simplest command has this much hidden structure, what does that tell you about the real engineering cost of the commands you actually care about — SET, GET, and everything that touches persistence?**

And the deeper question: this implementation is single-threaded and single-client. What happens when you run the benchmark with `-c 2` instead of `-c 1`? It hangs forever. **The next problem isn't protocol — it's concurrency without threads.**
