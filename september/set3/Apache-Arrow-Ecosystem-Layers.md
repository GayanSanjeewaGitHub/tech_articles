# Apache Arrow, Layer by Layer: What the Name Actually Covers

"Apache Arrow" gets used to mean at least four different things depending on who's talking: a memory format, a set of language libraries, a wire protocol, and lately a family of engines and drivers built on top of it. That looseness is part of why it's hard to place if you haven't worked with it directly. This piece — based on the [the-arrow-ecosystem](https://github.com/Felix-Mutinda/the-arrow-ecosystem) repo and its accompanying notebooks — tries to pin down what's actually there, one layer at a time, rather than treating "Arrow" as a single feature to adopt.

## The Core Idea: One Memory Layout, Many Processes

At its core, Arrow specifies a columnar in-memory layout: how a table's data sits in RAM, byte for byte. That's it. The interesting part is that this specification is language- and process-agnostic — a Rust process, a C++ process, and a Python process can all point at the same block of memory and read it as the same table, with no parsing or copying between them, provided each one implements the spec.

That property holds within a process, or across processes sharing memory. It doesn't extend across a network on its own — a query sent to a remote database still goes out as bytes on a socket, same as anything else. What the rest of the ecosystem does is make sure that once those bytes land, turning them back into a usable table doesn't cost you a second, different kind of conversion: protocols like Arrow Flight SQL and APIs like ADBC hand the client data that's already framed as Arrow, so there's no row-to-column reassembly waiting on the other end.

The repo is a small, running setup that demonstrates where that property holds, layer by layer.

## High-Level Design: The Layers, in Order

The stack has five layers, and each one earns its place by being a real hop that could otherwise force a conversion:

1. **Object storage (the foundation).** Data at rest, as Parquet files, in an S3-compatible store (MinIO here). This is the layer everything else reads from — nothing above it assumes a database has already loaded the data.

2. **Format.** Parquet on disk, Arrow in memory. They're related but not identical: Parquet is a compressed, disk-oriented columnar format designed for storage and scan efficiency; Arrow is the uncompressed, in-memory layout designed for direct access without a parsing step. A query engine's job at this boundary is decoding Parquet into Arrow.

3. **Persistence / query engine.** ClickHouse, reading Parquet directly off object storage via its `s3()` table function — no separate ingestion step, no materialized copy sitting in a MergeTree table.

4. **Wire protocol.** Arrow Flight SQL, a gRPC-based protocol for submitting SQL and getting results back. The data still goes out over the network as bytes. What Flight SQL buys you is on the receiving end: what comes back is already framed as Arrow record batches, so the client doesn't have to reassemble a row-oriented result set into columns itself. ClickHouse exposes this as an alternate interface alongside its usual TCP/HTTP ports.

5. **Client API.** ADBC (Arrow Database Connectivity) — a driver-manager pattern, similar in spirit to ODBC/JDBC, but returning Arrow tables natively instead of returning rows a client library then has to reassemble into columns.

Everything from that last handoff onward — DuckDB, DataFusion, pandas 2's Arrow-backed dtypes, native `pyarrow.compute` — is a consumer of the same in-memory table, shown in `notebooks/02_arrow_in_practice.ipynb`.

## How Docker Compose Sets It Up

The `docker-compose.yml` brings up three services:

- **minio** — the S3-compatible object store holding the Parquet files the rest of the stack reads.
- **clickhouse** — a high-performance, column-oriented SQL database management system (DBMS) for online analytical processing (OLAP), configured with Arrow Flight via `clickhouse/config.d/arrow-flight.xml`.
- **jupyter** — built from `notebooks/Dockerfile`, installing the ADBC/Flight SQL client stack (`requirements.txt`) plus the engines used in notebook 2 (DuckDB, DataFusion, pandas 2, scikit-learn, matplotlib, PyTorch). It mounts the `notebooks/` folder and serves JupyterLab on `localhost:8888`.

The two notebooks map directly onto the layers above:

- `01_driver_foundry.ipynb` covers the wire protocol and client API layers — installing an ADBC Flight SQL driver via the `dbc` CLI, connecting with `adbc_driver_manager`, and pulling a table back from ClickHouse as Arrow, compared side by side against the plain DBAPI row-fetch path.
- `02_arrow_in_practice.ipynb` picks up from there — the same table, queried through DuckDB and DataFusion, bridged into pandas (plain and Arrow-backed), plotted, and carried into scikit-learn and PyTorch.

## Cloning It and Following Along

```bash
git clone https://github.com/Felix-Mutinda/the-arrow-ecosystem
cd the-arrow-ecosystem
cp .env.example .env
docker compose up -d --build
```

Then open `http://localhost:8888/lab`, and work through `01_driver_foundry.ipynb` before `02_arrow_in_practice.ipynb`.

---

## Why Arrow, Really — A Q&A

### Isn't this just format conversion (CSV/JSON/Parquet)?

No — that's a side effect, not the point. The real problem Arrow solves is the **serialization/deserialization tax paid every time data crosses a process or language boundary while already in memory.**

Without Arrow, every hop between tools works like this:
1. The source's internal representation (often row-oriented — a list of tuples, a database cursor) gets serialized into some interchange format.
2. The destination deserializes it back into *its own* internal representation (usually a different columnar layout).

That round trip does no useful work — it's just reshaping data — and it happens at *every* hop. A pipeline like `database → Python → NumPy → Spark → back to Python` pays this tax three or four times over. On small data you never notice; at GB scale it can dominate runtime.

What Arrow does: define one in-memory columnar byte layout that every participating library implements identically. If both sides speak Arrow, there's no conversion step — one process just points at the memory and reads it.

### Why wasn't this already built into every library?

Because every library was born alone, years apart, solving its own problem — not coordinating with tools that didn't exist yet. NumPy (2006) invented its own array layout to be fast at math. Pandas (2008) invented its own internal block layout to be flexible for tables. Spark (2009) uses JVM objects. Every database engine has its own internal row/column storage tuned for its own disk and query engine. None of them were designed to talk to each other — they were designed to be self-sufficient. Interop wasn't the problem anyone was solving yet.

Arrow (started 2016, co-founded by the creator of pandas) is the first deliberate, cross-company agreement to standardize on one shared in-memory shape. That kind of standard doesn't happen automatically — it takes explicit coordination, and retrofitting a dozen already-entrenched projects onto a new internal format is slow (pandas only got optional Arrow-backed dtypes in pandas 2, ~15 years after pandas 1.0).

### A simple story: before and after

Before shipping containers existed, moving cargo overseas meant dockworkers unloaded a truck by hand, repacked the goods into the ship's hold by hand (whatever shape fit — bags, barrels, boxes), then at the destination other workers unloaded it all by hand again and repacked it onto a train, then again onto a truck. Every handoff meant physically repacking cargo into a new shape, because the truck, ship, and train all expected different container shapes.

Now picture Priya, a data scientist. Her company's data lives in ClickHouse, and she wants to pull a table into Python to train a model.

**Before Arrow:** ClickHouse hands rows over the wire in its own row format. Python's database driver unpacks those rows into a list of Python tuples (repack #1). Pandas takes that list and repacks it into its internal block-manager arrays (repack #2). Priya calls `.values` to get a NumPy array for scikit-learn — repack #3. Handing a batch to PyTorch is repack #4. Every repack is CPU time and memory copying spent doing nothing except changing the box shape. On a 50GB table, this is where half her runtime goes.

**After Arrow:** ClickHouse ships results already boxed as Arrow (via Flight SQL). Python's driver hands Priya the same Arrow box, unmodified. Pandas 2 (Arrow-backed) holds that box directly. PyArrow compute, scikit-learn-compatible arrays, and PyTorch tensors can all read straight off it. Nobody repacks anything until the very last mile, if ever — same idea as the shipping container: one box shape, and every crane, ship, and truck in the chain was built to grab that exact box.

### How much faster, in real numbers?

There's no single multiplier — it depends on what's being compared and where the bottleneck was. Grounded reference points from published benchmarks:

- Databricks documents Spark's `toPandas()` with Arrow enabled as **up to ~10x faster** than the row-by-row Java→Python serialization it replaced.
- `connectorx` (an Arrow/ADBC-based DB connector) benchmarks at roughly **3–10x faster** than `pandas.read_sql()` (a traditional row-cursor DBAPI driver), with the gap widening as row count grows.
- Dremio/InfluxDB have published Flight SQL vs. JDBC/ODBC benchmarks showing **10–20x** on large analytical pulls — the old bottleneck wasn't "serialization" abstractly, it was per-row Python/Java object creation.

Why the range is wide:
- **Row count matters most.** At 1,000 rows the overhead is milliseconds either way. At 50 million rows, per-row object creation in the old path dominates.
- **What's being compared.** Arrow vs. a hand-rolled efficient binary protocol is a small win; Arrow vs. a legacy row-by-row JDBC/ODBC cursor is a large one.
- **How much of total time is transport vs. compute.** If 90% of your pipeline's time is model training, even a 10x load-time speedup barely moves the total.

A plausible real-world figure for a typical large-result-set fetch through a modern Arrow connector vs. a legacy row-based one is around **5x** — but the honest range spans from barely measurable (small data, compute-bound pipeline) to 20x+ (huge result sets, old JDBC-style baseline).

### Do both ends need to speak Arrow to get the benefit?

Yes — and more precisely, **every link in the chain does**, not just the two ends. The speedup only holds between two points if *both* sides of that specific handoff understand Arrow natively. The moment one link doesn't, that link converts back to rows (or NumPy, or whatever its own format is), and the repacking tax reappears right there — even if every other link in the chain is Arrow-native.

Concrete example, continuing Priya's pipeline:
- **ClickHouse → Python driver**: needs Flight SQL / ADBC support on both sides. Plain ODBC/JDBC drivers don't speak Arrow — they hand you rows no matter how fast ClickHouse is internally.
- **Python driver → pandas**: needs pandas 2 with Arrow-backed dtypes (`pd.ArrowDtype`). Regular pandas (`pd.read_sql`, pandas 1.x, or pandas 2 without explicitly requesting Arrow dtypes) still repacks everything into its old NumPy block-manager format.
- **pandas → scikit-learn / PyTorch**: these generally still expect NumPy arrays or tensors, not Arrow tables directly — so there's often one unavoidable conversion at the very last mile.

The practical rule: **the benefit is only as strong as the weakest non-Arrow link.** Using an Arrow-native database connector but then loading into legacy pandas gets a fast fetch and a slow load — one hop got fixed, not the whole chain.

