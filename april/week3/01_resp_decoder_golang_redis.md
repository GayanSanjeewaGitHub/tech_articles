# RESP Decoder in Golang — Building Redis from Scratch

## Intuitive Explanation (5 Key Points)

- **RESP is a prefix-based protocol** — Every Redis data type starts with a single special character (`+` for simple strings, `-` for errors, `:` for integers, `$` for bulk strings, `*` for arrays). The decoder just switches on the first byte to know what it's parsing. That one-byte prefix is the entire dispatch mechanism.

- **The "delta" is the real design insight** — The decoder doesn't just return the parsed value; it also returns *how many bytes it consumed*. This delta lets you chain multiple values back-to-back in a single byte slice and decode them one at a time by advancing a position pointer — no slicing, no copying, just arithmetic.

- **`decodeOne` is the recursive primitive** — Instead of writing separate logic for nested structures, a single `decodeOne` function decodes exactly one RESP value from any offset. Arrays just call `decodeOne` in a loop, which means arrays-within-arrays-within-arrays work for free — infinite nesting with zero extra code.

- **Integer reconstruction is manual, not library-based** — Rather than calling `strconv`, the decoder rebuilds integers digit-by-digit (`value = value * 10 + int64(byte - '0')`). This keeps parsing tight, avoids allocations, and mirrors how the protocol actually lays out digits as sequential bytes terminated by `\r\n`.

- **Bulk strings use a two-phase read: length first, then payload** — The `$` type first reads an integer (the string length), then reads exactly that many bytes forward. This length-prefixed design means the parser never has to scan for delimiters inside the payload — it knows the exact boundary upfront, making it safe for binary data.
