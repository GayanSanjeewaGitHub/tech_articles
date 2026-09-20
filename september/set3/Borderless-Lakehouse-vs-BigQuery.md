# Google Cloud Borderless Lakehouse vs. BigQuery — What's Actually Being Compared

## Background

At Google Cloud Next 2026, Google announced the **Borderless Lakehouse**: a managed, Apache Iceberg-based data layer that lets BigQuery, Spark, Flink, Trino, and AlloyDB read and write the *same* tables — including tables sitting in AWS or Azure — without copying data first. It replaces the old open-lakehouse pain of self-hosting a Hive Metastore and hand-syncing metadata across engines with a fully managed Iceberg REST catalog built directly on Cloud Storage.

The natural framing — "Lakehouse vs. BigQuery" — is a bit of a trap, though, and worth untangling before comparing feature lists.

---

## The Question Behind the Question: This Isn't Really an Either/Or

BigQuery isn't competing with the Borderless Lakehouse. **BigQuery is one of the engines that runs on top of it.** The real comparison is between two different ways of storing and accessing your data:

1. **BigQuery native tables** — data lives in BigQuery's own managed, proprietary columnar storage. Fast, simple, but BigQuery is the only engine with first-class native access.
2. **Borderless Lakehouse (open Iceberg tables)** — data lives as Parquet files on Cloud Storage (or S3/Azure Blob), described by an open Iceberg REST catalog. BigQuery can query it — so can Spark, Flink, Trino, and now Databricks/Snowflake/AWS Glue's own catalogs, federated in.

So the useful comparison isn't "which product do I pick," it's "which storage/access model fits this dataset" — and most real organizations end up running both side by side.

---

## So What Gap Does It Actually Fill?

Spark, Trino, and BigQuery could all already read Apache Iceberg tables before this announcement — that's not new. The gap is **who has to run the catalog coordinating them, and what happens when your engines are already anchored to different catalogs across different clouds.**

**Before — BigQuery alone, everything else is a separate island:**

```
   Three places data already lives — no lakehouse involved yet:

   +-------------+     +-------------+     +-------------+
   |  GCS        |     |  AWS S3     |     |  Azure Blob |
   |  (Spark's   |     |  (AWS-      |     |  (Azure-    |
   |   own data) |     |   native)   |     |   native)   |
   +-------------+     +-------------+     +-------------+
         |                    |                    |
   Spark/Trino read these DIRECTLY, in place — no copy needed for THEM.
         |                    |                    |
         v                    v                    v
   +---------------------------------------------------------+
   | BUT BigQuery can't read any of these natively. To query   |
   | this data IN BigQuery, each source needs its OWN separate |
   | ETL pipeline INTO BigQuery's managed storage:              |
   +---------------------------------------------------------+
         |                    |                    |
     ETL/copy             ETL/copy             ETL/copy
   (slow, manual)     ($$ egress, manual)   (slow, manual)
         v                    v                    v
   +-------------+     +-------------+     +-------------+
   | copy #1 in  |     | copy #2 in  |     | copy #3 in  |
   | BigQuery    |     | BigQuery    |     | BigQuery    |
   +-------------+     +-------------+     +-------------+

   THE ACTUAL PROBLEM: not "one table duplicated 3x" — it's that
   BigQuery alone needs a private copy of EVERY source it touches,
   no matter where that source already lives, because its native
   engine only reads its own storage format. Spark/Trino never had
   this problem — they were built to read open files in place.
```

**After — the Lakehouse is the routing layer, not another copy of the data:**

```
                    +--------------------------------+
                    |     BORDERLESS LAKEHOUSE        |
                    |  (managed Iceberg REST catalog  |
                    |   = a routing/traffic map only) |
                    +--------------------------------+
                       ^        ^        ^        ^
              "where is|        |        |        |"where is
               table X?"        |        |        | table Y?"
                       |        |        |        |
            +----------+  +----+   +----+   +-----+-----+
            |             |         |         |            |
      +-----------+ +--------+ +-------+ +--------+  +----------+
      | BigQuery  | | Spark  | | Trino | | Flink  |  | AlloyDB  |
      +-----------+ +--------+ +-------+ +--------+  +----------+
            |             |         |         |            |
            +-------------+---------+---------+------------+
                                |
                 each engine reads the FILES itself —
                 the lakehouse only pointed the way, never
                 carried the data
                                |
            +-------------------+--------------------+
            |                   |                     |
      +-----------+     +--------------+      +----------------+
      |  Cloud    |     |  AWS S3      |      |  Azure Blob    |
      |  Storage  |     |  (via Glue   |      |  (federated)   |
      +-----------+     |  federation) |      +----------------+
                         +--------------+

   ROLE OF THE LAKEHOUSE:
   - ONE place every engine asks "where's the current table right now?"
   - data never moves or duplicates — engines fetch it directly
   - AWS/Azure catalogs plug IN as-is (federated), nothing migrates
   - everyone gets the same answer at the same moment = one source of truth
```

In short: before, BigQuery solved "one engine, one copy of data" — every other engine or cloud meant a new pipeline and a new stale copy. The Lakehouse doesn't replace that storage, it replaces the *N pipelines* with one shared routing/catalog layer every engine and every cloud points at instead.

---

## What Borderless Lakehouse Actually Adds

- **Serverless Runtime Catalog** — a managed Apache Iceberg REST catalog (Iceberg V2/V3) as the single source of truth, so nobody has to run their own Hive Metastore.
- **Multi-Engine Interoperability** — BigQuery, Spark, Flink, Trino, and AlloyDB read/write the same physical tables with no duplication and no manual metadata sync.
- **Catalog Federation (preview)** — the runtime catalog can federate *other* clouds' own catalogs: AWS Glue, Databricks Unity Catalog, and Snowflake Horizon, so BigQuery/Spark can discover and query tables registered there directly.
- **Cross-Cloud Caching (preview)** — frequently accessed Parquet column chunks from AWS/Azure get cached locally in Google Cloud, cutting repeat cross-cloud transfer costs.
- **Storage-Level Governance via Knowledge Catalog** — centralized IAM enforcement, automated column-level lineage, customer-managed encryption keys, Cloud Storage Autoclass tiering, and business-term mapping across *all* federated catalogs, not just BigQuery's own.
- **Zero-copy SaaS access** — direct, live querying against SAP, Salesforce, and Workday data without an ETL pipeline.
- **Flat-rate Cross-Cloud Interconnects** — pricing tiers from 1G–100G, with variable egress on AWS reads going to zero.

---

## How the Read Path Actually Works: Metadata vs. Data

It's easy to picture the lakehouse as a middleman that fetches files on an engine's behalf. It isn't — the Iceberg REST catalog is a **metadata directory**, not a data proxy, and it normally never touches the actual data bytes. It tracks schema, partitioning, and a manifest of which data files currently make up the table — the files themselves stay exactly where they are, untouched, almost always as Parquet (Iceberg's spec also allows ORC/Avro, but not arbitrary formats).

```
Same-cloud read (data already in Cloud Storage):

  Spark  ──1. "where's table X's current snapshot?"──▶  Iceberg REST Catalog
  Spark  ◀──2. pointer: manifest list + file paths────   (Borderless Lakehouse)
  Spark  ──3. reads the actual Parquet files directly──▶ Cloud Storage (GCS)

  BigQuery does the exact same three steps, completely independently.
  Neither engine goes "through" the other — both just ask the same catalog
  and read the same files straight from GCS.
```

Think of the catalog as a library's card catalog rather than a librarian: it tells every engine which shelf (which files, which snapshot) currently makes up a valid version of the table, and coordinates writes so two engines never commit conflicting versions at once. It deliberately stays out of the heavy data-moving path — a REST endpoint serving small JSON responses can fan out to hundreds of engines; something that streamed every Parquet byte through itself would become the bottleneck it was supposed to remove.

The one place the lakehouse *does* sit inside the actual byte transfer is a cross-cloud read. If a table's real files live in S3 and BigQuery is querying it from Google Cloud, that first read has to pull real bytes across the cloud boundary — and that's exactly where cross-cloud caching kicks in, caching the Parquet column chunks locally in Google Cloud so the next read, by any engine, hits the local cache instead of paying the cross-cloud hop again:

```
Cross-cloud read (data lives in S3):

  BigQuery ──1. ask catalog (federated to AWS Glue)──▶ Iceberg REST Catalog
  BigQuery ◀──2. pointer: s3://bucket/table/data/...──
  BigQuery ──3. read───────────────────────────────▶ [GCP cross-cloud cache] ──▶ S3
                                                        (only cache misses go to S3;
                                                         hits stay local)
```

So: the metadata plane (catalog) is in the loop for every engine, every time — thin, fast, just coordinating truth. The data plane (actual file reads) normally bypasses the lakehouse entirely, going straight from engine to storage; the lakehouse only inserts itself into the data path for cross-cloud reads, and there it's caching bytes, not carrying every read forever.

---

## Side-by-Side

| | **BigQuery native tables** | **Borderless Lakehouse (Iceberg)** |
|---|---|---|
| **Storage format** | Proprietary, BigQuery-managed columnar storage | Open Parquet files on Cloud Storage / S3 / Azure Blob |
| **Catalog** | Internal BigQuery metastore | Managed Iceberg REST catalog, federatable to Glue / Unity / Horizon |
| **Who else can read/write it** | BigQuery only (natively) | BigQuery, Spark, Flink, Trino, AlloyDB — same table, no copies |
| **Cross-cloud access** | Requires BigQuery Omni or a data transfer/export step | Native federation + zero-copy caching against AWS/Azure |
| **Governance** | Dataplex + native IAM, scoped to BigQuery's own catalog | Knowledge Catalog, unified across every federated catalog |
| **Vendor lock-in** | Higher — storage format is BigQuery-specific | Lower — open table format, engine is swappable |
| **Peak performance** | Generally fastest for BigQuery-only workloads — tightest possible integration | Slightly more overhead from the open format/metadata layer, though the gap is narrowing |
| **Ingestion/streaming** | Best-in-class native streaming inserts | Streaming into Iceberg is improving but still generally behind native BigQuery ingestion |
| **Cost shape** | Storage + compute often bundled or on-demand per BigQuery pricing | Cheaper open storage on Cloud Storage, compute billed per engine used, plus flat-rate interconnect fees for cross-cloud reads |

---

## When Each One Actually Wins

**Reach for BigQuery native tables when:**
- Everything lives in one cloud and BigQuery is the only engine touching this data
- You need maximum query performance and don't want to think about table formats at all
- You're doing high-throughput streaming ingestion or latency-sensitive dashboards
- The team is small enough that "just use BigQuery" is a feature, not a limitation

**Reach for Borderless Lakehouse when:**
- Your stack is already multi-engine — Spark or Trino jobs and BigQuery both need the same tables
- Data legitimately lives across clouds (AWS Glue tables, a Databricks lakehouse, a Snowflake estate) and copying it everywhere isn't realistic
- Avoiding lock-in to one warehouse's proprietary format is a real requirement, not a nice-to-have
- You're building AI agents (via Gemini Enterprise / Data Agent Kit / MCP) that need grounded, governed access to data wherever it actually sits, not just what's already inside BigQuery

---

## The Nuance That's Easy to Miss

BigQuery could already query external Iceberg tables before this announcement, through BigLake — this isn't a brand-new capability appearing from nothing. What's actually new is turning that one-off, per-connection federation into a **fully managed, bidirectional, multi-cloud catalog layer**: a serverless REST catalog Google runs for you, federation *into* other clouds' own catalogs (not just reading their files), cross-cloud caching to control repeat-transfer cost, and Knowledge Catalog stitching governance together across all of it.

In practice, the pitch isn't "replace BigQuery with the lakehouse" — it's "keep your hot, BigQuery-only workloads on native storage, and put shared, cross-engine, cross-cloud datasets into open Iceberg tables that the *same* BigQuery compute can still query." Same engine, two storage strategies, chosen per dataset rather than per company.

---

## Bottom Line

If your data and your query engines never leave BigQuery, native tables remain the simpler, faster default — the Borderless Lakehouse adds a catalog and federation layer you don't need. The moment a second engine (Spark, Trino, Flink) or a second cloud enters the picture, the calculus flips: paying the small overhead of an open Iceberg table buys you one physical copy of the data instead of N, a single governance layer instead of N, and the option to swap or add engines later without a migration.

---

## Q&A: Practical Follow-Ups

### Q1: We're already committed to putting data in BigQuery — is layering the Lakehouse on top actually worth it?

Yes, and it isn't either/or. The practical pattern: keep your core, high-traffic tables as **native BigQuery tables** for maximum speed, and register the **shared/cross-source** tables as Iceberg so the Lakehouse can route BigQuery (or any other engine) to them the moment something outside BigQuery needs the same data. Same BigQuery compute either way — you're just choosing, per dataset, whether it lives in BigQuery's private storage or in an open Iceberg table the Lakehouse can point multiple engines at.

### Q2: When BigQuery actually reads a table, does it download the file, or does something fetch it on BigQuery's behalf?

BigQuery's own compute does the fetching itself — nothing downloads on its behalf. The sequence is always: engine asks the Lakehouse catalog "where's table X's data right now?" → catalog returns a pointer (a path, not bytes) → the requesting engine's own compute reads directly from that path into its own memory and computes there. If the pointer says "BigQuery's native storage," BigQuery reads it the normal native way. If the pointer says "S3," BigQuery's compute reaches into S3 itself — the Lakehouse was never in that download path, it only supplied the address.

### Q3: Can the Lakehouse connect to an on-prem PostgreSQL database over HTTPS?

Not directly, for two reasons:
1. Lakehouse federation targets **catalogs** (AWS Glue, Databricks Unity, Snowflake Horizon, SAP Business Data Cloud) — not arbitrary databases.
2. Postgres doesn't speak HTTPS/REST in the first place — it's its own TCP wire protocol on port 5432, so there's nothing REST-shaped for the catalog to call.

The realistic path to bring on-prem Postgres data into this picture is the normal GCP toolset, not a Lakehouse feature: **Datastream** (CDC replication into BigQuery/GCS) to land the data as Iceberg/BigQuery tables, or a **federated query** from BigQuery to Postgres over private connectivity (Cloud VPN/Interconnect) — never a raw DB port exposed over public HTTPS.

### Q4: We use Denodo, which has its own catalog — does the Lakehouse federate with that?

No, not currently. The only catalogs Borderless Lakehouse federates with today (preview) are AWS Glue, Databricks Unity Catalog, Snowflake Horizon Catalog, and SAP Business Data Cloud — Denodo isn't among them.

There's also a directional mismatch worth noting: Denodo is a **virtualization layer that connects out to sources**, so the natural integration runs the other way — Denodo treating BigQuery/Iceberg as one of *its* sources — rather than the Lakehouse reaching into Denodo's catalog the way it reaches into Glue or Unity Catalog.

### Q5: So bottom line — is the Lakehouse just a central place every engine calls to find any catalog?

Directionally yes, with one correction: it's a central routing/metadata layer that engines (BigQuery, Spark, Trino, Flink, AlloyDB) all query for "where's this table right now," and it in turn federates out to a specific, currently-supported list of external catalogs — not literally any catalog or database that exists. It's central *for the catalogs it explicitly supports*; anything outside that list (an on-prem database, a virtualization tool like Denodo) still needs its own connectivity or replication step to get in.

---

## Sources

- [Introducing the borderless Lakehouse — Google Cloud Blog](https://cloud.google.com/blog/products/data-analytics/introducing-the-borderless-lakehouse)
- [What is borderless Lakehouse? — Google Cloud Documentation](https://docs.cloud.google.com/lakehouse/docs/introduction)
- [About borderless Lakehouse — Google Cloud Documentation](https://docs.cloud.google.com/lakehouse/docs/about-borderless-lakehouse)
- [Apache Iceberg Lakehouse — Google Cloud](https://cloud.google.com/products/lakehouse)
- [Google's borderless lakehouse wires AWS, Databricks and Snowflake catalogs into one Iceberg REST surface — DEV Community](https://dev.to/leobaniak/googles-borderless-lakehouse-wires-aws-databricks-and-snowflake-catalogs-into-one-iceberg-rest-7a6)
- [Borderless Lakehouse cross-cloud caching and connections — daily.dev](https://daily.dev/posts/borderless-lakehouse-cross-cloud-caching-and-connections-xctvphcsx)
- [Google Cloud expands borderless Lakehouse across clouds — itbrief](https://itbrief.ca/story/google-cloud-expands-borderless-lakehouse-across-clouds)
