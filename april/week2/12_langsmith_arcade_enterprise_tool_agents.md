# LangSmith Fleet + Arcade: 8,000 Enterprise Tools for Natural Language Agents

## 5 Intuitive Takeaways

1. **Arcade gives LangSmith agents access to 8,000+ enterprise-ready tools through a single MCP gateway** — instead of building custom integrations for each SaaS product, you configure an Arcade MCP gateway that bundles tools like Google Docs, Reddit, Slack, and thousands more. The agent discovers available tools from the gateway, and you add them to your agent's toolbox with a few clicks. One connection point replaces hundreds of bespoke API integrations.

2. **Just-in-time OAuth means the agent requests user authorization only when it actually needs a tool** — the agent doesn't require all permissions upfront. When it hits a Reddit API call and the user hasn't authorized Reddit yet, it surfaces an auth URL in the conversation. The user clicks, authorizes, and the agent continues the thread. This is least-privilege access at the tool level, not blanket API key sharing.

3. **The real power is chaining tools across services in a single agent conversation** — the demo shows an agent that reads top Reddit posts from a subreddit, summarizes them, and posts the summary to a Slack channel — all in one natural language request. A second example reads a Reddit article, summarizes it, and creates a Google Doc. The agent orchestrates cross-service workflows that would normally require dedicated automation pipelines or custom code.

4. **Admin-level gateway configuration separates tool governance from agent building** — workspace admins in LangSmith configure which Arcade organization, project, and gateways are available. This means the people building agents don't need to manage API credentials, OAuth scopes, or tool availability. Security policy is set once at the gateway level, and every agent in the workspace inherits it.

5. **This is the "tool supply chain" pattern for agents — and it changes who can build production workflows** — by abstracting tool connectivity into a managed gateway layer, non-engineers can create agents with natural language that perform real enterprise actions (post to Slack, create documents, query databases). The bottleneck shifts from "can we integrate this API" to "should the agent have access to this API" — a governance question, not an engineering one.
