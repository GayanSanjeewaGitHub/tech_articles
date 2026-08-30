# The Postal Code Problem

## The scene
Your favorite hot sauce is out of stock. The system looks it up. All it has is a SKU — a random number, like a social security digit — and a taxonomy node called "hot sauce" holding thousands of items, from Scotch bonnet to gochujang. It has to guess a substitute. It guesses wrong.

## Why it hurts
Wrong substitute, lost trust, one more churned order. Add a new item to a catalog of 55 million SKUs and it lands nowhere — no neighbors, no signal, cold start from zero. Try to hand any of this to an LLM and it stalls: language models learn from words, not arbitrary integers.

## What's actually happening underneath
Taxonomy is a human artifact — coarse buckets nobody had time to subdivide. "Hot sauce" is one node holding hundreds of genuinely different things. The ID itself carries no relationship to anything; two adjacent SKU numbers could be a sauce and a basketball. The catalog has structure. Nothing in the system encodes it.

## The shift
**Stop assigning IDs. Learn addresses instead.** An item's identity shouldn't be arbitrary — it should be a coordinate in the space of things like it.

## The fix
Cluster all 55 million items by embedding similarity — a coarse pass, like sorting by country. Subtract each item from its cluster center, cluster the residual — now you're at the state level. Repeat: city, street, house number. Four numbers deep, you have a semantic ID — a postal code, not a social security number. The old "hot sauce" node dissolves into 327 subclusters nobody hand-tagged. Now substitution means walking to the next house on the street. Cold start means dropping a new house into a street that already exists. And a small language model can finally output an item, because now an item is just four numbers that mean something.

## The question to sit with
Every random ID in your system is hiding a map nobody drew — what does yours actually look like?
