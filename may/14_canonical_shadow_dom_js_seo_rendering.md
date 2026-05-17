# What Google Actually Sees On Your Page

Most developers assume: if it renders on screen, Google indexes it. That assumption quietly kills rankings.

---

## The Canonical Problem

When a URL lives at `www.site.com/page`, `site.com/page`, `site.com/page?utm=email`, and `site.com/page/`, search engines see four separate pages. Same content, four addresses. Every backlink pointing at a variant instead of the master dilutes ranking power across copies instead of stacking it on one.

The `rel="canonical"` tag is the fix — it tells Google which URL is the authoritative version and to consolidate all signals there. Without it, you compete against yourself. With it, the crawler deprioritizes duplicates and stops burning crawl budget on variants that contribute nothing.

Canonical is a hint, not a command. Google cross-checks it against internal links and your sitemap. If all three agree, consolidation happens fast. If they contradict, Google decides for itself.

---

## The Shadow DOM Problem

Web components introduce a second invisible trap. A component can take your `<p>` tag and render it inside its shadow DOM — a private, encapsulated bubble the component controls. The content appears on screen. But Google's crawler reads raw HTML first, renders JavaScript later (sometimes days later, sometimes never). Content born inside JavaScript and injected into shadow DOM may never make it into the index.

The slot element fixes this. A `<slot>` cuts a hole through the shadow boundary — your light DOM content stays in the original HTML (safe, always readable), but displays visually through the component's template. Google sees it from the raw HTML. No rendering gamble.

The rule is simple: content you want indexed should live in HTML you wrote, not in content a component generates.

---

## Five Questions Worth Asking About Your Site

1. Do your internal links, sitemap, and canonical tags all point to the same URL for every important page — or are they contradicting each other silently?

2. How many of your URLs are duplicate variants (trailing slashes, UTM parameters, filter combinations) currently splitting ranking signals that should be stacked on one page?

3. If your JavaScript failed to execute entirely, how much of your page content would Google still be able to read from the raw HTML alone?

4. Are any of your web components generating text content (descriptions, headings, prices) inside shadow DOM rather than projecting light DOM content through a slot?

5. When did you last check Search Console's URL Inspection tool to compare what Google actually indexed against what your browser renders?
