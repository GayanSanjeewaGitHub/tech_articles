# The Forgotten Algorithm: Why the Oldest Way to Sort is Still the Fastest

*Based on "The Fastest Way to Sort a Million Integers"*

## The Interview Trap

**What if the "standard" answer to a programming question is actually the slow one?**

You are in an interview. The question drops: "How do you sort a million 32-bit integers?" Your brain immediately jumps to Quicksort or Mergesort—the $O(N \log N)$ algorithms you learned in school. They are safe, reliable, and standard.

**But imagine this:** You are a librarian trying to organize a million books. Quicksort is like picking up two books, comparing them, and swapping them, over and over again, millions of times. It works, but it's exhausting.

**Now imagine a different way:** You don't compare books at all. You just look at the first letter of the title. "A" goes in the "A" bin. "B" goes in the "B" bin. You do this once for the first letter, once for the second, and so on. No comparisons. Just placing things where they belong. This is **Radix Sort**. And for integers, it is 7 times faster than Quicksort.

**Why learn this?** Because sometimes, the "best practice" is a generalist tool, while the "best solution" is a specialist one. Understanding why Radix Sort wins teaches you to look for constraints (like "integers only") that unlock massive performance gains.

## The Magic of Buckets

**What if you could sort without ever asking "is X smaller than Y"?**

Radix Sort is built on **Bucket Sort**. If you have numbers 0-9, you just make 10 buckets. You drop each number in its bucket. Then you pour the buckets out in order. Done. $O(N)$ time.

**Imagine this:** You have a million numbers, but they are 32-bit integers (0 to 4 billion). You can't make 4 billion buckets; you'd run out of memory. So, Radix Sort uses a trick. It treats the number like a word with "digits." It sorts by the last digit first, then the second-to-last, and so on.

**Why learn this?** It introduces the concept of **stable sorting**. Sorting by the last digit only works if the order of the *previous* sorts is preserved. This is a deep lesson in algorithmic properties: sometimes, doing things "backwards" (least significant digit first) is the only way to move forward.

## The Floating Point Hack

**What if a decimal number was just an integer in disguise?**

Here is where it gets wild. Radix Sort works on integers. But what if you need to sort floating-point numbers (like 3.14)? Standard wisdom says you must use Quicksort.

**Imagine this:** You look at the raw binary bits of a float. The IEEE 754 standard (which defines floats) was designed by a genius named William Kahan. He arranged the bits (sign, exponent, mantissa) so that if you interpret the bits as an integer, the order is preserved! A larger float *looks* like a larger integer in binary.

**Why learn this?** This is the ultimate "hacker" insight. It teaches you that data types are just abstractions. Under the hood, everything is bits. If you understand the representation, you can cheat the system—convincing the computer to sort complex decimals using a simple integer algorithm.

## Conclusion: The Power of Constraints

Radix Sort is faster because it is *less* powerful. It can't sort strings or objects or custom classes. It only sorts numbers. But because it accepts that constraint, it can shed the weight of comparison logic.

**So, ask yourself:** In your own code, are you using a heavy, general-purpose tool when a specialized, constrained one would be 10x faster? The oldest algorithm in the book (literally used on punch cards in 1958) is still the king of speed. Sometimes, to go fast, you have to stop comparing and start bucketing.
