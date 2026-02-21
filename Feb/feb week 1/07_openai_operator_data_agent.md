# The "Text-to-SQL" Fallacy: Why Data Agents Need to Read Code, Not Just Schemas

## The Trap: The Dictionary Delusion

We tend to think of data warehouses as libraries. If you want to know something, you just need to find the right book (table) and read the right page (column). We assume that the *schema*—the list of table names and column types—is the map of reality.

We build "Chat with Data" tools based on this dictionary delusion. We feed a Large Language Model (LLM) a list of table names (`users`, `orders`, `events`) and expect it to answer business questions.

**The Trap:** We confuse **Structure** (what the table looks like) with **Semantics** (what the table means).

## The "Stop Time" Moment

**Imagine this scenario:** You have two tables in your warehouse: `dim_users_active` and `dim_users_engaged`. Both have a `user_id` column. Both have a `last_login` timestamp.

A stakeholder asks: "How many users were active yesterday?"

Your LLM—looking only at the schema—picks `dim_users_active`. It writes valid SQL. It gets a number: 10,000.

But the *truth* is hidden. The `dim_users_active` table includes bot traffic. The `dim_users_engaged` table filters it out.

**Ask yourself: Where does that distinction live?**

It is not in the column name. It is not in the database comments (which are always outdated).
It lives in the **ETL Code**—the Python or SQL script that *created* the table multiple hops upstream.

**What is being wasted here?**
Trust. The moment an agent gives a confident, wrong number, the tool dies.

## The Mental Model Shift: From "DBA" to "Code Archaeologist"

To build a data agent that actually works, you must shift your perspective on what constitutes "Context."

**Stop thinking in "Schemas" (The End State). Start thinking in "Lineage" (The Creation Process).**

A schema is just a fossil—a footprint left by a process. To understand the fossil, you must study the creature that made it.

*   **Old Model:** The Agent looks at the database metadata.
*   **New Model:** The Agent reads the *application code* that populates the database.

The shift is from **Retrieving Data** to **Reasoning about Provenance**. The agent shouldn't just ask "What is in this table?" It should ask "How was this table built?"

## The "What If" Scenarios

### Scenario 1: The "Silent Filter"
An executive asks for "Revenue." The Agent sums the `amount` column in the `transactions` table.
*   **The Context Gap:** The finance team defines "Revenue" as *recognized* revenue (excluding refunds), but the `transactions` table is raw.
*   **The "Code Reading" Solution:** If the agent reads the dbt/Airflow transformation logic, it sees that `finance_reports` is derived from `transactions` via a filter `WHERE status != 'refunded'`. It knows to use the downstream table.

### Scenario 2: The "Ambiguous Join"
The Agent needs to join `customers` to `orders`. There are three foreign keys.
*   **The Guess:** The Agent picks the first key it sees.
*   **The Reality:** The join logic depends on the *business context* (e.g., "billing address" vs "shipping address").
*   **The "Usage" Solution:** By analyzing *other* query logs (history), the Agent detects that 95% of human analysts join on `shipping_address_id` for logistics questions. behavior implies intent.

## The Architecture: The Context Pyramid

OpenAI's internal "Operator" agent succeeds because it ignores the superficial "Text-to-SQL" approach and builds a **Context Pyramid**:

1.  **Base Layer: Codex Enrichment (The "How"):** The agent crawls the codebase (Python, Spark, Airflow). It learns that `table_A` is just a filtered view of `table_B`. It derives meaning from the *source code*, not just the database definition.
2.  **Middle Layer: Institutional Memory (The "Why"):** It ingests Slack threads and Notion docs. It knows that "Project Omega" launched on Nov 13th, which explains the data dip.
3.  **Top Layer: Self-Correction (The Loop):** It doesn't just return the first SQL result. It acts like a scientist.
    *   *Plan:* "I need to find active users."
    *   *Execute:* Run SQL.
    *   *Evaluate:* "Wait, this result has zero rows. That's suspicious."
    *   *Refine:* "Ah, I missed a partition filter." -> Re-run.

**The takeaway:**
Data is not a static asset; it is a flowing river produced by logic. A data agent that only looks at the "water" (the rows) will drown. A data agent that understands the "riverbed" (the code and pipeline) can navigate.
