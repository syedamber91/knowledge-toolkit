#!/usr/bin/env python3
"""
Apache Spark Internals: A Data Engineer's Complete Reference
Based on Vu Trinh's research at vutr.substack.com
Run: python3 scripts/generate_vutr_spark.py
"""
import os

# ─────────────────────────────────────────────────────────────────────────────
# CSS — copied verbatim from generate_learning_pack.py
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --ink:#1c1c2e; --body:#2d2d3e; --muted:#666680; --border:#d8d8e8; --bg:#fff; --alt:#f8f8fc;
  --s-bg:#f0fdf4; --s-bd:#22c55e; --s-tx:#14532d;
  --n-bg:#eff6ff; --n-bd:#3b82f6; --n-tx:#1e3a8a;
  --d-bg:#faf5ff; --d-bd:#a855f7; --d-tx:#581c87;
  --f-bg:#fff1f2; --f-bd:#f43f5e; --f-tx:#881337;
  --r-bg:#fff7ed; --r-bd:#f97316; --r-tx:#7c2d12;
  --l-bg:#f0f9ff; --l-bd:#0ea5e9; --l-tx:#0c4a6e;
}
*{box-sizing:border-box;margin:0;padding:0}
@page{size:A4;margin:18mm 16mm 18mm 16mm}
body{font-family:'Source Serif 4',Georgia,serif;font-size:9.5pt;line-height:1.72;color:var(--ink);background:#fff}

/* Cover */
.cover{page-break-after:always;display:flex;flex-direction:column;justify-content:center;min-height:250mm;padding:0 8mm}
.eyebrow{font-family:'Inter',sans-serif;font-size:7.5pt;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#3b82f6;margin-bottom:5mm}
.cover h1{font-family:'Inter',sans-serif;font-size:26pt;font-weight:700;line-height:1.15;color:var(--ink);margin-bottom:4mm}
.cover .sub{font-size:12pt;color:var(--muted);font-style:italic;margin-bottom:9mm}
.rule{width:14mm;height:3px;background:#3b82f6;margin-bottom:7mm}
.cover-desc{font-family:'Inter',sans-serif;font-size:9pt;color:var(--body);line-height:1.6;max-width:130mm;margin-bottom:10mm}
.toc-head{font-family:'Inter',sans-serif;font-size:7.5pt;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:3mm}
.ti{display:flex;align-items:baseline;padding:2mm 0;border-bottom:1px solid var(--border);font-family:'Inter',sans-serif;font-size:8.5pt}
.ti-n{font-weight:700;color:#3b82f6;width:10mm;flex-shrink:0}
.ti-t{flex:1;color:var(--ink)}
.ti-s{color:var(--muted);font-size:7.5pt;margin-left:3mm}

/* Chapter */
.chapter{page-break-before:always}
.ch-head{margin-bottom:7mm;padding-bottom:4mm;border-bottom:2px solid var(--border)}
.ch-eye{font-family:'Inter',sans-serif;font-size:7.5pt;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#3b82f6;margin-bottom:2mm}
.chapter h1{font-family:'Inter',sans-serif;font-size:18pt;font-weight:700;line-height:1.2;color:var(--ink);margin-bottom:2mm}
.ch-src{font-family:'Inter',sans-serif;font-size:8pt;color:var(--muted);margin-bottom:3mm}
.ch-sum{font-size:10pt;font-style:italic;color:var(--body);line-height:1.6}

/* Topics */
.topic{margin-bottom:8mm}
.topic h2{font-family:'Inter',sans-serif;font-size:12pt;font-weight:700;color:var(--ink);margin:6mm 0 2mm;padding-bottom:1.5mm;border-bottom:1px solid var(--border)}
.topic h3{font-family:'Inter',sans-serif;font-size:10.5pt;font-weight:600;color:var(--body);margin:4mm 0 1.5mm}
.topic p{margin-bottom:2.5mm}
.topic ul,.topic ol{padding-left:5mm;margin-bottom:2.5mm}
.topic li{margin-bottom:1.2mm}
.topic strong{font-weight:700;color:var(--ink)}
code{font-family:'JetBrains Mono',monospace;font-size:8pt;background:var(--alt);padding:1px 3px;border-radius:3px;color:#c2410c}
pre{font-family:'JetBrains Mono',monospace;font-size:8pt;background:#1e1e2e;color:#cdd6f4;padding:3.5mm;border-radius:4px;margin:2.5mm 0;page-break-inside:avoid;line-height:1.5}

/* Callouts */
.box{margin:3mm 0;border-left:4px solid;padding:3.5mm 4.5mm;border-radius:0 4px 4px 0;page-break-inside:avoid}
.box-lbl{font-family:'Inter',sans-serif;font-size:7pt;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:1.5mm}
.box.s{background:var(--s-bg);border-color:var(--s-bd)}.box.s .box-lbl{color:var(--s-bd)}
.box.n{background:var(--n-bg);border-color:var(--n-bd)}.box.n .box-lbl{color:var(--n-bd)}
.box.d{background:var(--d-bg);border-color:var(--d-bd)}.box.d .box-lbl{color:var(--d-bd)}
.box.f{background:var(--f-bg);border-color:var(--f-bd)}.box.f .box-lbl{color:var(--f-bd)}
.box.r{background:var(--r-bg);border-color:var(--r-bd)}.box.r .box-lbl{color:var(--r-bd)}
.box.l{background:var(--l-bg);border-color:var(--l-bd)}.box.l .box-lbl{color:var(--l-bd)}
.box p{margin-bottom:1.5mm}.box p:last-child{margin-bottom:0}
.box ul{padding-left:4.5mm}.box li{margin-bottom:1mm}

/* Tables */
table{width:100%;border-collapse:collapse;margin:2.5mm 0;font-size:8.5pt;font-family:'Inter',sans-serif;page-break-inside:avoid}
thead{background:var(--alt)}
th{text-align:left;font-weight:700;padding:2mm 2.5mm;border-bottom:2px solid var(--border);color:var(--ink);font-size:8pt;text-transform:uppercase;letter-spacing:.3px}
td{padding:1.8mm 2.5mm;border-bottom:1px solid var(--border);vertical-align:top;line-height:1.5}
tr:last-child td{border-bottom:none}
.g{color:#15803d;font-weight:600}.y{color:#d97706}.rd{color:#dc2626;font-weight:600}
.hr{background:#fefce8}

/* Recall section */
.recall{margin-top:6mm;padding:4mm;background:var(--alt);border:1px solid var(--border);border-radius:4px;page-break-inside:avoid}
.recall-head{font-family:'Inter',sans-serif;font-size:7.5pt;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:3mm}
.q{margin-bottom:2.5mm;padding-left:4mm;border-left:2px solid var(--border)}
.q-n{font-family:'Inter',sans-serif;font-size:7.5pt;font-weight:700;color:#3b82f6}

/* Quote */
.quote{font-style:italic;color:var(--muted);border-left:3px solid var(--border);padding:2mm 0 2mm 4mm;margin:4mm 0;font-size:9pt}
.quote cite{display:block;font-style:normal;font-size:8pt;margin-top:1mm}

/* New callout box variants */
.box.xr{background:#f5f3ff;border-color:#7c3aed}.box.xr .box-lbl{color:#7c3aed}
.box.teach{background:#fefce8;border-color:#ca8a04}.box.teach .box-lbl{color:#92400e}
.box.gap{background:#fff7f7;border-color:#9f1239}.box.gap .box-lbl{color:#9f1239}
.box.why{background:#f0fdf4;border-color:#16a34a}.box.why .box-lbl{color:#14532d}

/* Mermaid diagrams */
.mermaid{margin:3mm 0;text-align:center;page-break-inside:avoid}
.mermaid svg{max-width:100%;height:auto}
.diagram-cap{font-family:'Inter',sans-serif;font-size:7.5pt;color:var(--muted);text-align:center;margin-top:-1mm;margin-bottom:3mm;font-style:italic}

/* Cover extras for Spark pack */
.cover-title{font-family:'Inter',sans-serif;font-size:26pt;font-weight:700;line-height:1.15;color:var(--ink);margin-bottom:4mm}
.cover-sub{font-size:12pt;color:var(--muted);font-style:italic;margin-bottom:9mm}
.cover-toc{margin-top:4mm}
.toc-item{display:flex;align-items:baseline;padding:2mm 0;border-bottom:1px solid var(--border);font-family:'Inter',sans-serif;font-size:8.5pt}
.toc-n{font-weight:700;color:#3b82f6;width:16mm;flex-shrink:0}
"""

# ─────────────────────────────────────────────────────────────────────────────
# COVER
# ─────────────────────────────────────────────────────────────────────────────
COVER = """
<div class="cover">
  <div class="cover-title">Apache Spark Internals</div>
  <div class="cover-sub">A Data Engineer's Complete Reference<br>Based on Vu Trinh's research at vutr.substack.com</div>
  <div class="cover-toc">
    <div class="toc-item"><span class="toc-n">Ch 1</span><span>RDDs, DAGs, and the Catalyst Optimizer</span></div>
    <div class="toc-item"><span class="toc-n">Ch 2</span><span>Spark Memory Model and OOM Mechanics</span></div>
    <div class="toc-item"><span class="toc-n">Ch 3</span><span>Shuffle, Joins (SMJ / SHJ / Broadcast), and Skew</span></div>
    <div class="toc-item"><span class="toc-n">Ch 4</span><span>PySpark, Tungsten, and Photon</span></div>
    <div class="toc-item"><span class="toc-n">Ch 5</span><span>Spark Structured Streaming and AQE</span></div>
  </div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 1 — RDDs, DAGs, and the Catalyst Optimizer
# ─────────────────────────────────────────────────────────────────────────────
CH1 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 1 of 5</div>
  <h1>RDDs, DAGs, and the Catalyst Optimizer</h1>
  <div class="ch-src">Source: vutr.substack.com — The Overview of Apache Spark · Why Apache Spark RDD is Immutable · The Spark Scheduling Process</div>
  <p class="ch-sum">Spark's entire execution model — stages, shuffles, fault tolerance, and query optimization — follows from two foundational ideas: the RDD abstraction and lazy evaluation. Every performance decision in Spark is traceable to the concepts in this chapter.</p>
</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>Before Spark, iterative machine learning algorithms using MapReduce were extraordinarily expensive. MapReduce writes all intermediate data to disk between the map phase and the reduce phase. A gradient descent algorithm requiring 100 passes over the data means 100 full disk round-trips to HDFS — each pass launching a separate MapReduce job that rewrites everything to disk before the next job can read it. Spark was invented specifically to fix this: it keeps intermediate data in memory across iterations. Understanding <em>how</em> it does this — via RDDs, lineage, and lazy evaluation — is the foundation for every tuning decision you will ever make.</p>
</div>

<div class="topic">
<h2>The Historical Problem: Why MapReduce Failed for Iterative Workloads</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>MapReduce is like doing your homework one step at a time, but after each step you put your work in a filing cabinet, go home, come back, and retrieve it again before the next step. Spark lets you keep your work on the desk across all steps.</p>
</div>

<p>Google introduced MapReduce in 2004 as a paradigm for distributing data processing across hundreds of machines. The model is clean: a <strong>Map</strong> function processes records and emits key-value pairs; a <strong>Shuffle</strong> redistributes all pairs by key across the network; a <strong>Reduce</strong> function aggregates pairs sharing the same key. Disk writes buffer every phase boundary.</p>

<p>For a single-pass ETL job this is fine. For iterative workloads — any machine learning algorithm that makes multiple passes over data — it is catastrophic. Gradient descent on a neural network requires 10–100 passes. With MapReduce, each pass must be written as a separate job and launched individually on the cluster. The output of pass N is written to HDFS; pass N+1 reads it back from HDFS. This means 100 full disk round-trips for 100 gradient descent iterations.</p>

<p>UC Berkeley's AMPLab saw this problem in 2009 and built Spark. The solution: a functional programming-based API that keeps intermediate results in memory across computation steps via a new abstraction called the <strong>Resilient Distributed Dataset (RDD)</strong>.</p>

<div class="box n"><div class="box-lbl">MapReduce vs Spark — The Disk I/O Difference</div>
<table>
  <thead><tr><th>Operation</th><th>MapReduce</th><th>Spark</th></tr></thead>
  <tbody>
    <tr><td>Single-pass ETL</td><td>Read HDFS → Map → Shuffle → Reduce → Write HDFS</td><td>Same logical steps, but intermediate state stays in memory</td></tr>
    <tr><td>100-iteration ML training</td><td class="rd">100 × (Read HDFS + Write HDFS) = 200 full disk passes</td><td class="g">1 load into memory + 100 in-memory iterations</td></tr>
    <tr><td>Interactive queries</td><td class="rd">Each query reads fresh from disk — no caching</td><td class="g">RDD caching keeps hot data in RAM across queries</td></tr>
    <tr><td>Intermediate fault recovery</td><td>Shuffle files on disk — restart from last checkpoint</td><td>Lineage graph — recompute lost partitions from parent RDDs</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="topic">
<h2>The RDD: Resilient Distributed Dataset</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>An RDD is a recipe, not a dataset. It describes <em>how</em> to produce a collection of data items distributed across a cluster — but it does not hold the data itself until an action forces evaluation. Think of it as a lazy computation graph rather than a container.</p>
</div>

<p>An RDD is not a traditional collection like an array or list. It is an abstraction that represents a large collection of data distributed across a cluster, stored in memory for as long and as much as possible. Every DataFrame or Dataset you write in Spark compiles to RDDs behind the scenes.</p>

<p>An RDD has exactly <strong>five internal properties</strong>:</p>
<ol>
  <li><strong>List of Partitions:</strong> The RDD is divided into partitions — the primary unit of parallelism. Each partition is a logical chunk of data processed by one task on one executor. More partitions = more parallelism (up to available cores).</li>
  <li><strong>Compute Function per Partition:</strong> A function that, given a partition of the parent RDD and an iterator over its records, produces the output records for the corresponding partition of this RDD.</li>
  <li><strong>List of Dependencies:</strong> Each RDD records which parent RDDs it depends on and whether those dependencies are narrow or wide. This is the lineage graph.</li>
  <li><strong>Optional Partitioner (key-value RDDs only):</strong> For RDDs holding key-value pairs, an optional <code>Partitioner</code> specifies how keys are hashed to partitions. For example, <code>HashPartitioner(200)</code> means key.hashCode() % 200 determines the partition. This matters for avoiding reshuffles on chained operations.</li>
  <li><strong>Optional Preferred Locations:</strong> For data-locality scheduling. An HDFS-backed RDD knows which HDFS block replicas are on which nodes; Spark's scheduler tries to assign the task to a node holding the data (PROCESS_LOCAL or NODE_LOCAL).</li>
</ol>

<div class="box n"><div class="box-lbl">The 5 RDD Properties — Quick Reference</div>
<table>
  <thead><tr><th>Property</th><th>What It Is</th><th>Why It Matters</th></tr></thead>
  <tbody>
    <tr><td>List of partitions</td><td>Sequence of partition objects</td><td>Determines parallelism; one task per partition per stage</td></tr>
    <tr><td>Compute function</td><td>Iterator[T] given parent iterator</td><td>The actual computation; evaluated lazily on action</td></tr>
    <tr><td>Dependencies</td><td>List of (parent RDD, dependency type)</td><td>Drives stage boundary detection and fault recovery</td></tr>
    <tr><td>Partitioner (optional)</td><td>HashPartitioner or RangePartitioner</td><td>Avoids re-shuffle on chained key-value operations</td></tr>
    <tr><td>Preferred locations (optional)</td><td>List of hostnames per partition</td><td>Data locality — reduces network I/O by keeping compute near data</td></tr>
  </tbody>
</table>
</div>

<h3>RDD Immutability: A Distributed Systems Necessity</h3>

<p>RDDs are immutable. This is not a design preference borrowed from functional programming aesthetics — it is a distributed systems necessity driven by four concrete requirements:</p>

<p><strong>1. Lineage and fault tolerance (the primary reason).</strong> If a partition is lost due to node failure, Spark recomputes it by replaying the sequence of transformations from the parent partitions — the lineage graph. This requires that parent RDDs be stable (immutable) at the time of recomputation. If parent RDDs were mutable, they might have changed since the child RDD was computed, making deterministic recomputation impossible. Immutability guarantees that <em>reapplying the same transformation to the same parent always yields the same child</em>.</p>

<p><strong>2. Concurrent consumption without synchronization.</strong> Multiple tasks across multiple executors can read the same parent RDD partition simultaneously. If the RDD were mutable, concurrent reads while another task modified the data would require locks, atomic operations, or other coordination — dramatically increasing complexity and reducing throughput. Immutable data needs zero synchronization: any reader can safely read at any time.</p>

<p><strong>3. In-memory computing without cache invalidation.</strong> When an RDD partition is cached in executor memory, it can be served to many downstream consumers without verification. If the data could change, every cache hit would need a validity check. Immutability means a cached partition is always valid — no invalidation logic needed.</p>

<p><strong>4. Functional programming model.</strong> Spark's API is built on the functional programming principle that functions should have no side effects — given the same input, always produce the same output. This property, combined with immutability, is what makes lineage-based recovery possible and what makes Spark's execution model compositional.</p>

<div class="box f"><div class="box-lbl">The Lost-Partition Failure Scenario — Why Mutability Would Break Recovery</div>
<p>Concretely, here is what happens when a partition is lost and why immutability is load-bearing:</p>
<ol>
  <li><strong>Partition P3 of RDD C is lost</strong> because executor E2 crashes mid-execution. All data that was in E2's memory for that partition is gone.</li>
  <li><strong>Spark traces the lineage graph backward.</strong> RDD C was produced by applying transformation T2 to RDD B. RDD B was produced by applying T1 to RDD A (the original file on HDFS). Spark identifies the exact recomputation path: read the corresponding partition of A from HDFS → apply T1 → apply T2 → produce P3 of C.</li>
  <li><strong>Spark schedules a new task on a healthy executor</strong> to recompute P3 by executing this lineage path.</li>
  <li><strong>The result is identical</strong> to the original P3 because the transformation functions are pure (same input → same output) and the parent RDDs have not changed (immutable). No coordinator, no log, no checkpoint required — just reapply the same transformations.</li>
</ol>
<p><strong>Why mutability breaks this:</strong> If any parent RDD (A or B) could have been modified after the child C was computed, step 4 fails. Reapplying T1 to a mutated A produces a different result than the original C — deterministic recomputation is impossible. The only recovery option for a mutable distributed system is either (a) full replication of every partition to multiple nodes (expensive), or (b) write-ahead logs capturing every mutation (complex, slow). Immutability eliminates both: the lineage graph is sufficient.</p>
</div>

<div class="quote">"If RDDs were mutable, it would be challenging to deterministically regenerate the previous state in case of node failures. Immutability ensures that the lineage information remains intact and allows Spark to recompute lost data reliably."<cite>— luminousmen (Kirill Bobrov, Sr. Data Engineer at Spotify), vutr.substack.com</cite></div>
</div>

<div class="topic">
<h2>Transformations vs Actions: The Lazy Evaluation Contract</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Transformations are instructions written on paper. Actions are handing the paper to a chef and saying "cook it now." Until you say "cook it," nothing happens — Spark just accumulates instructions and builds an execution plan.</p>
</div>

<p>Every Spark operation is either a <strong>transformation</strong> or an <strong>action</strong>.</p>

<p><strong>Transformations</strong> define how data should be transformed but do not execute immediately. They are lazy — calling <code>map()</code>, <code>filter()</code>, or <code>groupByKey()</code> on an RDD does not compute anything. Instead, Spark records the operation as a node in the DAG (Directed Acyclic Graph) and returns a new RDD object representing the future result. The original RDD is not modified (immutability).</p>

<p>Common transformations: <code>map</code>, <code>filter</code>, <code>flatMap</code>, <code>groupByKey</code>, <code>reduceByKey</code>, <code>join</code>, <code>repartition</code>, <code>coalesce</code>, <code>sortBy</code>.</p>

<p><strong>Actions</strong> trigger DAG execution. When an action is called, Spark submits the accumulated DAG to the DAGScheduler, which compiles it into stages and tasks, submits TaskSets to the TaskScheduler, and the cluster begins executing.</p>

<p>Common actions: <code>collect()</code>, <code>count()</code>, <code>take(n)</code>, <code>first()</code>, <code>saveAsTextFile()</code>, <code>write()</code>, <code>show()</code>.</p>

<p><strong>Why laziness matters for optimization:</strong> By accumulating the full transformation pipeline before executing, Spark's optimizer can inspect the entire DAG and apply optimizations impossible in eager execution. Predicate pushdown (push filters early), projection pruning (drop unused columns), and stage fusion (combine narrow transformations into one pass) all require visibility into the full pipeline.</p>

<h3>reduceByKey vs groupByKey — The Most Important Performance Choice</h3>

<div class="box f"><div class="box-lbl">Critical Performance Decision: Always Prefer reduceByKey</div>
<p><strong>groupByKey — all raw values cross the network:</strong> groupByKey performs zero map-side reduction. Every value for every key travels from the mapper to the reducer over the network. If key <code>"user_123"</code> has 10 million values spread across 200 partitions, all 10 million values cross the network to the single reducer responsible for that key. That reducer must accumulate all 10 million values in memory before it can begin processing — creating an iterator that could consume many gigabytes for a single hot key. This is both a network problem (massive shuffle volume) and a memory problem (all values for one key must fit in one executor's memory simultaneously).</p>
<p><strong>reduceByKey — local partial reduction (combiner) before shuffle:</strong> reduceByKey applies a local combining step <em>within each partition before the shuffle</em>. This is the same concept as a MapReduce combiner. For each partition, all values with the same key are reduced to a single per-partition aggregate. Only this one aggregated value per key per partition crosses the network — not the raw values. For 10 million values across 200 partitions: at most 200 values per key cross the network (one from each partition), not 10 million. Network traffic shrinks by orders of magnitude.</p>
<p><strong>OOM risk from high-cardinality keys in groupByKey:</strong> Because groupByKey collects all values for a key into a single in-memory iterator at the reducer, a skewed key can cause OOM. If one key holds 50% of all values in a 100GB dataset, the reducer task for that key must hold 50GB of values in memory simultaneously — no spill-safe path exists until the entire collection is available. reduceByKey avoids this entirely: the per-partition aggregate is a single value, never the full collection.</p>
<p>Vu Trinh's rule: <strong>always prefer reduceByKey over groupByKey.</strong> The only valid use case for groupByKey is when you specifically need the <em>complete list</em> of values per key (not just an aggregate result). For any sum, count, min, max, or concatenation, use reduceByKey, aggregateByKey, or combineByKey.</p>
</div>
</div>

<div class="topic">
<h2>Narrow vs Wide Dependencies and Stage Boundaries</h2>

<p>The most important structural property of an RDD DAG is the distinction between narrow and wide dependencies, because this distinction determines where Spark inserts stage boundaries and therefore shuffles.</p>

<p><strong>Narrow dependency:</strong> Each partition in the child RDD depends on at most one partition in the parent RDD. The compute function for a child partition needs data from exactly one parent partition — no data from other partitions is required. Examples: <code>map</code>, <code>filter</code>, <code>flatMap</code>, <code>coalesce</code> (reducing partition count). Narrow transformations can be <em>pipelined</em> — Spark chains them into a single stage, processing records through all narrow transformations in one pass without writing intermediate results to disk.</p>

<p><strong>Wide dependency:</strong> A single partition of a parent RDD contributes to multiple partitions of the child RDD. The compute function for a child partition requires data from <em>multiple</em> parent partitions. Examples: <code>groupByKey</code>, <code>reduceByKey</code>, <code>join</code>, <code>repartition</code>, <code>sort</code>. Wide dependencies create stage boundaries — Spark must complete the parent stage entirely (writing shuffle files to disk) before the child stage can begin reading them.</p>

<div class="box n"><div class="box-lbl">Narrow vs Wide: Visual Distinction</div>
<table>
  <thead><tr><th>Property</th><th>Narrow Dependency</th><th>Wide Dependency</th></tr></thead>
  <tbody>
    <tr><td>Data flow</td><td>1 parent partition → 1 child partition</td><td>1 parent partition → N child partitions</td></tr>
    <tr><td>Examples</td><td>map, filter, flatMap, coalesce</td><td>groupByKey, reduceByKey, join, repartition, sort</td></tr>
    <tr><td>Stage boundary</td><td class="g">No — pipelined into same stage</td><td class="rd">Yes — requires shuffle; new stage</td></tr>
    <tr><td>Shuffle required</td><td class="g">No</td><td class="rd">Yes — disk write + network + disk read</td></tr>
    <tr><td>Fault recovery</td><td>Recompute one partition from one parent partition</td><td>May need to recompute entire parent stage</td></tr>
  </tbody>
</table>
</div>

<div class="box f"><div class="box-lbl">Stage Boundary Trigger: Why All Parents Must Finish First</div>
<p>A wide dependency forces a <strong>pipeline break</strong>: every partition in the parent stage must write its shuffle output to disk and register it with the BlockManager before any task in the child stage can begin reading. This is because child partition P needs data from <em>all</em> parent partitions whose keys hash to P — it cannot start until every upstream task has finished. The physical operation at the boundary is the <strong>shuffle</strong>: each parent task (1) writes records partitioned by key to local shuffle files on disk (<em>shuffle write</em>), (2) registers file locations, then the cluster transfers those files over the network to destination executors (<em>network transfer</em>), and each child task reads its slice from local disk (<em>shuffle read</em>). Two disk operations and a full network transfer for every stage boundary — this is why minimising wide dependencies is the single most impactful Spark performance lever.</p>
</div>

<h3>Key Skew and groupByKey: The Amplification Effect</h3>
<p>Data skew occurs when one key holds a disproportionate share of values. With <code>groupByKey</code>, <em>all</em> values for each key must travel over the network and land on the same reducer partition — no map-side pre-aggregation is applied. A skewed key — say, <code>"user_001"</code> with 50 million values in a 500-million-record dataset — means a single reducer task receives 10% of total data. That task's in-memory shuffle read buffer swells while all other tasks finish quickly. The result: stragglers, memory pressure, and potential OOM on the hot-key partition. Because <code>groupByKey</code> performs no local combining, there is no mechanism to reduce data volume before the shuffle — every value travels the network regardless. <code>reduceByKey</code> avoids this when the goal is aggregation (not collecting the full value list) because it collapses values locally within each partition before the shuffle, drastically shrinking hot-key network traffic. Vu's rule: always prefer <code>reduceByKey</code> unless you specifically need the complete list of values per key.</p>

<h3>Jobs, Stages, and Tasks: The Execution Hierarchy</h3>

<p>When an action fires, Spark's execution model has a strict three-level hierarchy:</p>
<ul>
  <li><strong>Job:</strong> One job per action. A Spark application can contain many jobs. Each job represents the full computation required to produce the action's output, from reading the original data through all transformations.</li>
  <li><strong>Stage:</strong> A job is divided into stages at wide dependency (shuffle) boundaries. All transformations within a stage are narrow and can be pipelined. Stages must run in topological order — a stage cannot begin until all its parent stages have completed and written their shuffle output.</li>
  <li><strong>Task:</strong> The smallest unit of execution. Each stage spawns one task per partition. Tasks run in parallel across executor cores. A stage with 200 partitions spawns 200 tasks; if the cluster has 50 cores, 50 tasks run simultaneously in four waves.</li>
</ul>

<p>The <strong>DAGScheduler</strong> builds the DAG, detects stage boundaries at wide dependencies, creates a topological ordering of stages, and generates a <code>TaskSet</code> for each stage. The <strong>TaskScheduler</strong> assigns individual tasks from each TaskSet to available executor cores, taking data locality preferences into account.</p>

<h3>Data Locality: Nearest to Farthest</h3>
<p>Spark's scheduler attempts to assign each task to an executor with the best data locality, waiting briefly before settling for a worse tier:</p>
<ol>
  <li><strong>PROCESS_LOCAL</strong> — data in the same JVM as the executor (ideal; RDD in same executor's cache)</li>
  <li><strong>NODE_LOCAL</strong> — data on the same machine, different JVM (e.g., HDFS block on same node)</li>
  <li><strong>NO_PREF</strong> — data has no locality preference (e.g., data from a database over JDBC)</li>
  <li><strong>RACK_LOCAL</strong> — data on a different node in the same rack (network hop within rack switch)</li>
  <li><strong>ANY</strong> — data anywhere in the cluster (cross-rack network transfer)</li>
</ol>
</div>

<div class="topic">
<h2>The Catalyst Optimizer: Four Phases</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>When you write a DataFrame query, Catalyst is the engine that figures out the most efficient physical way to execute it. It works in four phases: validate your query, apply logical simplifications, choose a physical execution strategy, and then compile optimized JVM bytecode for that strategy.</p>
</div>

<p>DataFrames and Datasets expose a schema — column names and types — that Spark can reason about before execution. This schema visibility is what allows the Catalyst Optimizer to apply optimizations that are impossible with raw RDDs or Python UDFs (which are black boxes).</p>

<p>Catalyst works in <strong>four sequential phases</strong>, always in this exact order:</p>

<div class="box n"><div class="box-lbl">Catalyst's Four Phases — Names, Order, and Purpose</div>
<table>
  <thead><tr><th>#</th><th>Phase Name</th><th>Input → Output</th><th>What It Does</th></tr></thead>
  <tbody>
    <tr><td>1</td><td><strong>Analysis</strong></td><td>Unresolved Logical Plan → Resolved Logical Plan</td><td>Resolves column names against the Catalog; validates types; catches "column not found" errors</td></tr>
    <tr><td>2</td><td><strong>Logical Optimization</strong></td><td>Resolved Logical Plan → Optimized Logical Plan</td><td>Rule-based rewrites: predicate pushdown, projection pruning, constant folding, null propagation — no physical decisions yet</td></tr>
    <tr><td>3</td><td><strong>Physical Planning</strong></td><td>Optimized Logical Plan → Physical Plan (selected)</td><td>Generates multiple candidate physical plans; selects the best via cost-based model using statistics (row counts, cardinality, min/max)</td></tr>
    <tr><td>4</td><td><strong>Code Generation</strong></td><td>Physical Plan → JVM Bytecode</td><td>Uses Scala quasiquotes + Janino compiler to emit a single tight JVM loop — no virtual dispatch, fully JIT-optimizable</td></tr>
  </tbody>
</table>
</div>

<p><strong>Phase 1 — Analysis:</strong> Resolves the query against the Catalog. Column names are validated against the schema, ambiguous references are resolved, types are checked for compatibility. If you reference a column that doesn't exist, the error surfaces here.</p>

<p><strong>Phase 2 — Logical Optimization:</strong> Rule-based transformations applied to the logical plan. No physical decisions yet — pure logical equivalence transformations:</p>
<ul>
  <li><strong>Predicate pushdown:</strong> Move filter operations as close to the data source as possible. A <code>WHERE year = 2024</code> filter pushed all the way to the Parquet file scan means Spark reads only the matching row groups from disk, rather than reading all data and filtering afterward.</li>
  <li><strong>Projection pruning:</strong> Drop unused columns as early as possible. If your query only needs 3 of 50 columns, Catalyst eliminates the other 47 from the scan — reducing I/O and memory consumption significantly.</li>
  <li><strong>Constant folding:</strong> Pre-compute constant expressions at planning time. <code>WHERE amount > 10 * 100</code> becomes <code>WHERE amount > 1000</code>.</li>
  <li><strong>Null propagation:</strong> Eliminate branches that cannot produce non-null results.</li>
</ul>

<p><strong>Phase 3 — Physical Planning:</strong> Generates <em>multiple</em> candidate physical plans and selects the best via a cost-based model. The cost model uses statistics collected by <code>ANALYZE TABLE</code> or inferred at runtime: estimated row counts, column cardinality, and min/max values. Catalyst scores each candidate plan using these statistics — for example, it computes the estimated cost of shuffling table A vs broadcasting table B, and chooses the lower-cost option. The most important physical planning decision is <strong>join strategy selection</strong> — Catalyst chooses between Broadcast Hash Join (BHJ), Sort Merge Join (SMJ), and Shuffle Hash Join (SHJ) based on estimated table sizes and the cost model. When statistics are absent or stale, the cost model may select a suboptimal plan; AQE (Ch5) corrects these mistakes at runtime with actual statistics.</p>

<p><strong>Phase 4 — Code Generation:</strong> Spark uses Scala's quasiquotes to generate JVM bytecode at runtime via the Janino compiler. Rather than interpreting a query plan row by row through a generic execution engine, Catalyst generates specific, inlined JVM bytecode for the exact query — eliminating virtual dispatch overhead and enabling JIT optimization of the hot loop.</p>

<div class="box n"><div class="box-lbl">Catalyst Phase 3 — Join Strategy Selection: BHJ vs SMJ vs SHJ</div>
<p>The most consequential physical planning decision is which join algorithm to use. Catalyst selects among three strategies based on estimated table sizes:</p>
<ul>
  <li><strong>Broadcast Hash Join (BHJ):</strong> Selected when either table is estimated below <code>spark.sql.autoBroadcastJoinThreshold</code> (default <strong>10 MB</strong> / 10,485,760 bytes). The small table is fully serialized on the driver and replicated as a copy to <em>every executor</em> in the cluster. No shuffle of either table — zero Exchange nodes in the physical plan. Memory cost is <code>O(number_of_executors × table_size)</code>: broadcasting a 2 MB table to 200 executors consumes 400 MB of executor Storage memory in total. The fastest join when applicable, but the threshold must be managed carefully — broadcasting a 2 GB table to 200 executors means 400 GB of heap pressure across the cluster, causing simultaneous OOM on every executor. Override with: <code>spark.sql.autoBroadcastJoinThreshold = -1</code> to disable, or a positive byte value to raise the limit.</li>
  <li><strong>Sort Merge Join (SMJ):</strong> Selected when both tables exceed the broadcast threshold and neither fits within a single partition of executor memory for SHJ. Both tables are shuffled by join key, sorted within each partition, then merged in one pass. Can spill to disk safely — this is the default and safe fallback for large-large joins. SMJ is chosen over SHJ when Catalyst cannot guarantee the build-side partition fits in Execution memory.</li>
  <li><strong>Shuffle Hash Join (SHJ):</strong> Selected for medium-sized tables when the build side is estimated to fit in executor memory per partition. The build side is hashed into an in-memory hash table per partition; the probe side streams through. Cannot spill — OOM if the build-side partition exceeds available memory. Covered in depth in Ch3.</li>
</ul>
<p><strong>The BHJ selection rule in production:</strong> BHJ is safe when the broadcast table fits comfortably in every executor's Storage memory simultaneously. With 200 executors each having 2 GB Storage memory: a 5 MB table → 1 GB total broadcast memory → safe. A 500 MB table → 100 GB total → may exhaust executor Storage memory on each executor, evicting cached partitions or causing OOM. The threshold <code>spark.sql.autoBroadcastJoinThreshold</code> is a size limit on <em>one side</em> of the join, not a safety guarantee — always verify that table_size × num_executors fits within total cluster Storage memory before raising the threshold.</p>
</div>

<div class="box f"><div class="box-lbl">Why Python UDFs Break Catalyst — and the Fix</div>
<p>DataFrames give Catalyst full visibility into the computation. A Python UDF (<code>@udf</code>) is a <strong>semantic black box</strong> — Catalyst cannot see inside it, cannot optimize it, cannot inline it into the code generation pipeline, and cannot apply Tungsten binary encoding to its inputs/outputs.</p>
<p><strong>The opacity mechanism:</strong> During Phase 2 (Logical Optimization), Catalyst applies predicate pushdown by inspecting each operator's expression tree. For built-in functions, the expression tree is transparent — Catalyst can determine exactly which input columns each expression reads and what it returns. A Python UDF is registered as an opaque node with no inspectable expression tree. Catalyst cannot determine whether the UDF output depends on a given input column, whether the UDF is deterministic, or whether a filter placed before the UDF would return identical results to a filter placed after it. Because Catalyst cannot determine predicate-pushdown safety through an opaque UDF node, it must conservatively block pushdown at the UDF boundary. Similarly, projection pruning cannot eliminate columns that <em>might</em> be read by the UDF, because Catalyst has no way to inspect which columns the Python function actually accesses.</p>
<p><strong>The three costs of UDF opacity:</strong> (1) No predicate pushdown past the UDF — filters after the UDF cannot be moved before it, so more data is processed; (2) No projection pruning through the UDF — all columns must be available even if the UDF only reads two of them; (3) No Tungsten binary encoding — data must be deserialized from UnsafeRow to Python objects before the UDF executes, then re-serialized back. Every row crosses the JVM/Python process boundary with Pickle serialization.</p>
<p><strong>The fix: rewrite UDF logic using native <code>pyspark.sql.functions</code>.</strong> Every built-in function in <code>pyspark.sql.functions</code> — <code>when()</code>, <code>coalesce()</code>, <code>regexp_replace()</code>, <code>to_date()</code>, <code>substring()</code>, <code>concat()</code>, etc. — is a first-class Catalyst expression node. Replacing a Python UDF with equivalent built-in function combinations makes the logic fully transparent to Catalyst: predicate pushdown works, projection pruning works, Tungsten encoding works, and no JVM/Python process boundary is crossed. For complex logic not expressible with built-ins, use a Pandas UDF (vectorized, Arrow-based batch transfer) as the next-best option — it still lacks Catalyst transparency but eliminates the per-row serialization cost.</p>
</div>

<div class="box l"><div class="box-lbl">Cross-Connections from This Chapter</div>
<ul>
  <li><strong>Ch3 (Join Strategy):</strong> Catalyst Phase 3 selects BHJ vs SMJ vs SHJ based on table size estimates. Understanding those join strategies requires first understanding how Catalyst makes the choice.</li>
  <li><strong>Ch5 (AQE):</strong> Adaptive Query Execution extends Catalyst Phase 3 into runtime — after each shuffle stage completes, AQE re-runs physical planning with actual statistics rather than estimates. AQE is Catalyst's Phase 3 applied dynamically.</li>
  <li><strong>Ch4 (Code Generation):</strong> Catalyst Phase 4 generates the JVM bytecode that Tungsten executes. Photon replaces this JVM bytecode with native C++ for Lakehouse workloads.</li>
</ul>
</div>
</div>

<div class="recall">
<div class="recall-head">Spark Engineer's Checkpoint</div>
<div class="q"><span class="q-n">Q1 </span>Name all five properties of an RDD. For each one, explain what would break if that property did not exist.</div>
<div class="q"><span class="q-n">Q2 </span>Why is RDD immutability a distributed systems necessity rather than a functional programming preference? Name the specific distributed systems failure mode that mutable RDDs would introduce.</div>
<div class="q"><span class="q-n">Q3 </span>A job has the transformations: <code>map → filter → groupByKey → map → reduceByKey → collect</code>. How many stages does Spark create? Draw the stage boundaries and explain why each boundary exists.</div>
<div class="q"><span class="q-n">Q4 </span>What does predicate pushdown do in Catalyst Logical Optimization, and why does it reduce I/O rather than just CPU?</div>
<div class="q"><span class="q-n">Q5 </span>You have a query using a Python UDF on a 500M-row DataFrame. A colleague suggests replacing it with a Spark SQL built-in function that does the same thing. Explain every layer at which the built-in function is faster.</div>
</div>

<div class="box teach"><div class="box-lbl">How to Teach This Chapter</div>
<p><strong>Junior engineer (5 min):</strong> Start with the MapReduce disk-write problem — ask them to calculate how many disk writes 100 gradient descent iterations require with MapReduce. Then show the RDD model: same iterations, one memory load. The performance difference is visceral. End: "Everything in Spark is an RDD. DataFrames compile to RDDs. Now you understand why lazy evaluation exists."</p>
<p><strong>Senior engineer (20 min):</strong> Walk through the five RDD properties and derive why each one exists from first principles. Then trace a <code>groupByKey</code> vs <code>reduceByKey</code> on a skewed dataset through the DAG — show the shuffle volume difference. Cover Catalyst phases with emphasis on Phase 3 (join selection) as a preview of Ch3.</p>
</div>

<div class="box gap"><div class="box-lbl">Questions This Chapter Doesn't Answer</div>
<ul>
  <li>How does the DAGScheduler handle stage re-submission when shuffle map output files are lost (different failure mode from task failure)?</li>
  <li>What is the cost model Catalyst uses in Phase 3 — exactly which statistics does it collect and how does column skew affect the model?</li>
  <li>At what point does RDD lineage become too deep (hundreds of transformations) and checkpointing becomes necessary?</li>
</ul>
</div>
</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 2 — Spark Memory Model and OOM Mechanics
# ─────────────────────────────────────────────────────────────────────────────
CH2 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 2 of 5</div>
  <h1>Spark Memory Model and OOM Mechanics</h1>
  <div class="ch-src">Source: vutr.substack.com — If you're learning Apache Spark, this article is for you · A small hands-on project to 2× your Apache Spark learning process</div>
  <p class="ch-sum">OOM errors are the most common production failure in Spark. Understanding the unified memory model — its regions, borrowing rules, and eviction asymmetry — is the difference between debugging an OOM in 10 minutes and spending a day adding memory that doesn't fix anything.</p>
</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>OOM errors in Spark feel random. The same job passes on Monday and fails on Thursday. The data volume didn't change. What changed? A different scheduling order put a different partition on the same executor. Or a slightly different data distribution created a skewed partition that needed 80% of executor memory. Vu Trinh captures this precisely: "This is why the same job can pass on Monday and fail on Thursday. It's not the data volume that changed. A different scheduling order, a different outcome." To debug OOMs reliably, you must understand <em>exactly</em> how Spark allocates memory inside an executor and what causes one task to consume far more than its share.</p>
<p>Two failure modes are commonly confused: <strong>insufficient total memory</strong> (adding executor memory fixes it) and <strong>data skew</strong> (adding memory does not fix it — the skewed task still receives the same disproportionate share of data regardless of executor size). Understanding the unified memory model makes the difference between a 10-minute fix and a wasted day.</p>
</div>

<div class="topic">
<h2>The Unified Memory Model (Spark 1.6+)</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Each executor's heap is divided into three zones: a small locked zone Spark keeps for itself (300MB), a zone for your application's own data structures, and a large shared zone that Spark splits between "working memory for computations" and "cache storage." The key insight: the working memory can borrow from cache storage, but cache storage cannot borrow back from working memory once it's been taken.</p>
</div>

<p>Before Spark 1.6, memory was partitioned statically — a fixed fraction went to execution, a fixed fraction to storage, and the two could never share. If execution needed more space during a large sort, it could not borrow from an underutilized storage region, and it would spill to disk. This rigidity wasted memory on every workload that didn't perfectly match the static split.</p>

<p>Spark 1.6 introduced the <strong>Unified Memory Manager</strong>, which allows execution and storage to share a single region and borrow from each other. The full executor heap is divided into three regions:</p>

<h3>Region 1: Reserved Memory — 300MB Hardcoded</h3>
<p>Spark sets aside exactly <strong>300MB</strong> for its own internal objects — the SparkContext, DAGScheduler, TaskScheduler, block manager metadata, and other framework components. This value is hardcoded in <code>UnifiedMemoryManager.scala</code> (line 200 in the Apache Spark GitHub repo). It cannot be changed without recompiling Spark. Every memory calculation must subtract this 300MB first.</p>

<h3>Region 2: User Memory</h3>
<p>Controlled by the formula: <code>(executor_heap - 300MB) × (1 - spark.memory.fraction)</code>. With the default <code>spark.memory.fraction = 0.6</code>, user memory gets 40% of the remaining heap after reserving 300MB. This region is for user data structures — your hash maps, arrays, custom serialized objects. Spark does not manage this region; it is allocated by your application code via normal JVM allocation.</p>

<h3>Region 3: Unified Memory (Execution + Storage)</h3>
<p>Controlled by: <code>(executor_heap - 300MB) × spark.memory.fraction</code>. Default: 60% of the post-reserved heap. With the defaults of <code>spark.memory.fraction = 0.6</code> and <code>spark.memory.storageFraction = 0.5</code>, Storage and Execution each initially occupy 30% of total heap (50% × 60% = 30%). The split is dynamic — the boundary is <strong>soft</strong>, not hard. The initial storageFraction only defines the minimum guaranteed Storage region; actual allocations can diverge based on runtime demand.</p>

<div class="box n"><div class="box-lbl">The Soft Boundary — What "Dynamic" Actually Means</div>
<p>When no data is cached (Storage region is empty), <strong>Execution can borrow the entire Storage allocation</strong>. A shuffle aggregation that needs 1.8GB of unified memory on an executor where nothing is cached can take all 2.2GB of unified pool — the Storage region's initial 1.1GB is fully available. When a cache() call then needs space, Storage cannot take back memory that Execution is actively using. Storage can only evict its <em>own</em> already-cached blocks (LRU policy) until it falls below the storageFraction threshold. The asymmetry is absolute: Execution takes freely from idle Storage; Storage waits or evicts, never reclaims from active Execution tasks.</p>
</div>

<div class="box n"><div class="box-lbl">Exact Memory Calculation for a 4GB Executor</div>
<table>
  <thead><tr><th>Region</th><th>Formula</th><th>Value (4GB executor)</th></tr></thead>
  <tbody>
    <tr><td>Reserved (Spark internals)</td><td>Hardcoded 300MB</td><td class="rd">300 MB</td></tr>
    <tr><td>Remaining heap</td><td>4096 - 300</td><td>3796 MB</td></tr>
    <tr><td>User memory</td><td>3796 × (1 - 0.6)</td><td>1518.4 MB</td></tr>
    <tr><td>Unified memory (total)</td><td>3796 × 0.6</td><td>2277.6 MB</td></tr>
    <tr><td>Storage (initial fraction)</td><td>2277.6 × 0.5</td><td>1138.8 MB</td></tr>
    <tr><td>Execution (initial fraction)</td><td>2277.6 × 0.5</td><td>1138.8 MB</td></tr>
  </tbody>
</table>
<p>For a 2GB executor: usable unified memory = (2048 - 300) × 0.6 = <strong>1048.8 MB</strong>. Remember this number — it governs every task running on that executor.</p>
</div>

<div class="box n"><div class="box-lbl">Worked Arithmetic: Step-by-Step Layout for a 4GB Executor (Default Config)</div>
<p>Work through this once from scratch so you can reproduce it without looking it up. The critical insight is that <code>spark.memory.storageFraction</code> is applied to the <em>Unified pool</em>, not to the total heap — a common exam mistake.</p>
<ol>
  <li><strong>Start: total JVM heap = 4096 MB.</strong></li>
  <li><strong>Subtract Reserved Memory (hardcoded 300 MB):</strong><br>
      Post-reserved heap = 4096 − 300 = <strong>3796 MB</strong>.<br>
      This is the base for every subsequent calculation. Never apply <code>spark.memory.fraction</code> to the raw 4096 MB.</li>
  <li><strong>Split post-reserved heap into User Memory vs Unified Memory using <code>spark.memory.fraction = 0.6</code>:</strong><br>
      Unified Memory = 3796 × 0.6 = <strong>2277.6 MB</strong>.<br>
      User Memory = 3796 × (1 − 0.6) = 3796 × 0.4 = <strong>1518.4 MB</strong>.</li>
  <li><strong>Split Unified Memory into Storage and Execution using <code>spark.memory.storageFraction = 0.5</code>:</strong><br>
      Storage (initial) = <strong>2277.6</strong> × 0.5 = <strong>1138.8 MB</strong>.<br>
      Execution (initial) = <strong>2277.6</strong> × 0.5 = <strong>1138.8 MB</strong>.<br>
      <em>Note: 0.5 is applied to 2277.6 (the Unified pool), NOT to 4096 (total heap) and NOT to 3796 (post-reserved heap). Applying storageFraction to the wrong base is the most common arithmetic mistake.</em></li>
  <li><strong>Sanity check — the four regions must sum to 4096 MB:</strong><br>
      300 + 1518.4 + 1138.8 + 1138.8 = 4096 MB. ✓</li>
</ol>
<p><strong>Common wrong answer to avoid:</strong> "Storage = 4096 × 0.5 = 2048 MB." This is wrong because it skips both the 300 MB Reserved subtraction and the <code>spark.memory.fraction</code> step. Storage is a fraction of a fraction of the post-reserved heap — not a fraction of the raw heap.</p>
<p><strong>Changing only storageFraction:</strong> If you set <code>spark.memory.storageFraction = 0.3</code> (keeping everything else default on a 4 GB executor): Unified pool stays 2277.6 MB. Storage initial = 2277.6 × 0.3 = 683.3 MB. Execution initial = 2277.6 × 0.7 = 1594.3 MB. Total still = 4096 MB. This gives shuffle-heavy jobs more initial Execution headroom without changing total unified pool size.</p>
</div>
</div>

<div class="topic">
<h2>Execution Memory vs Storage Memory — and the Eviction Asymmetry</h2>

<p><strong>Execution memory</strong> is used for computations during task execution: shuffle aggregations (building hash tables for groupBy), sort buffers (sort-merge join sorting), join hash tables (building the hash table for shuffle hash join), and any intermediate data structures during record processing. Execution memory is <strong>never evicted</strong> — tasks that need execution memory get it, and if there's not enough, they spill to disk or fail.</p>

<div class="box f"><div class="box-lbl">Why Execution Memory Cannot Be Evicted — The Rollback Impossibility</div>
<p>The reason Execution memory is protected from eviction is mechanistic, not arbitrary: <strong>in-progress tasks cannot be rolled back mid-execution</strong>. Spark's execution model does not support transactional undo of partial computations. If Spark attempted to evict memory holding a half-built sort buffer or a partially constructed hash table to free space for a storage cache, the task would be left in an inconsistent, unrecoverable state. The task would have to be killed and restarted from scratch — at which point it would immediately re-request the same execution memory, creating an infinite eviction loop. Therefore the design rule is absolute: once execution memory is claimed by a running task, it cannot be reclaimed until the task completes or fails. Storage memory, by contrast, holds already-computed results (cached RDD partitions, broadcast variables) that are fully reproducible — evicting a cached partition does not destroy partial computation, it only means the data must be re-read or recomputed on the next access.</p>
</div>

<p><strong>Storage memory</strong> is used for: cached RDD partitions (<code>cache()</code> and <code>persist()</code>), broadcast variables (the small table in a Broadcast Hash Join lives here), and accumulator values. Storage memory <strong>can be evicted</strong> using a Least Recently Used (LRU) policy when execution needs more space.</p>

<div class="box f"><div class="box-lbl">The Eviction Asymmetry — The Most Important Rule in Spark Memory</div>
<p><strong>Execution can borrow from storage freely.</strong> When execution needs more space and storage has free room, execution takes it without restriction. There is no limit on how much execution can consume from storage's initial allocation.</p>
<p><strong>Storage cannot take back from execution.</strong> When storage needs space and execution has borrowed it, storage cannot evict execution memory. The design explicitly prioritizes execution over storage. Storage will instead evict its own cached blocks (LRU) until it falls below the <code>spark.memory.storageFraction</code> threshold.</p>
<p><strong>The practical consequence:</strong> A job that performs heavy shuffles and aggregations (execution-heavy) may push every single cached RDD partition out of memory. If your job pattern is "cache a large table once, then run many queries," heavy computation on those queries can silently evict the cache — and the next query re-reads from disk, negating the entire caching strategy. Design around this asymmetry: if caching is critical, use <code>MEMORY_AND_DISK</code> storage level so evicted partitions spill to disk rather than being lost.</p>
</div>

<h3>Storage Cache Levels</h3>
<p>When you call <code>cache()</code>, Spark always uses <code>MEMORY_AND_DISK</code>. When you call <code>persist(storageLevel)</code>, you choose explicitly:</p>
<ul>
  <li><code>MEMORY_ONLY</code> — deserialized Java objects in heap. Fastest reads; most memory usage; if evicted, recomputed (not spilled)</li>
  <li><code>MEMORY_AND_DISK</code> — deserialized in memory; if evicted, serialized to disk. What <code>cache()</code> uses.</li>
  <li><code>DISK_ONLY</code> — serialized to disk only; no heap storage</li>
  <li><code>OFF_HEAP</code> — Tungsten binary format in off-heap memory</li>
  <li><code>_SER</code> suffix — serialized format (saves space, adds deserialization overhead on read)</li>
  <li><code>_2</code> or <code>_3</code> suffix — replication factor across nodes for fault tolerance</li>
</ul>
</div>

<div class="topic">
<h2>Scheduling Nondeterminism and OOM Nondeterminism</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Spark's scheduler doesn't guarantee which partition lands on which executor. The same skewed partition might hit a lightly-loaded executor on Monday (succeeds) and a memory-constrained executor on Thursday (OOM). Same job, same data, different outcome — because scheduling order is nondeterministic.</p>
</div>

<p>One of the most disorienting properties of Spark OOM failures is their <strong>intermittency</strong>: the same job passes on Monday and fails on Thursday. No data volume change. No code change. The culprit is the interaction between two sources of nondeterminism: <strong>data distribution across partitions</strong> and <strong>scheduling assignment of partitions to executors</strong>.</p>

<p>Here is the chain of causation:</p>
<ol>
  <li><strong>Data skew creates unequal partitions.</strong> After a shuffle, key distribution is never perfectly uniform. A skewed key might cause one shuffle partition to hold 800MB while the median partition holds 40MB.</li>
  <li><strong>Executor load is nondeterministic at the moment of task assignment.</strong> At any given instant, different executors have different amounts of free memory — some are processing other task waves, some have more cached data, some ran GC recently. The TaskScheduler assigns tasks to available slots based on current load and data locality, not on partition size. There is no mechanism to "match a big partition to a big-memory executor."</li>
  <li><strong>The skewed partition may or may not hit a constrained executor.</strong> On Monday, the oversized partition was assigned to executor E4, which happened to have 3GB free — it processed without OOM. On Thursday, executor E4 was processing another large partition from a concurrent job, leaving only 900MB free — the same oversized partition arrives, and OOM occurs.</li>
</ol>

<div class="box f"><div class="box-lbl">Why "Same Job, Different Day" Is a Scheduling Problem, Not a Data Problem</div>
<p>The data distribution (the skew) is the <em>structural cause</em>, but the scheduling assignment determines whether a given run <em>experiences</em> the OOM. If the skewed partition always lands on the same executor, the job is deterministically succeeding or failing. Because it sometimes passes: the skewed partition is finding enough memory on the randomly-assigned executor. Because it sometimes fails: the executor happens to be under pressure from other concurrent tasks on that run.</p>
<p>This is why the "Monday passes, Thursday fails" pattern points to <strong>data skew</strong> as the root cause — not a transient infrastructure problem. The fix must eliminate the unequal partition sizes (repartition, salting, AQE skew handling), not just add more memory. Adding memory raises the threshold but does not change the scheduling nondeterminism: the skewed partition still lands on a random executor, and on a bad day, that executor is still under pressure.</p>
</div>
</div>

<div class="topic">
<h2>Off-Heap Memory and Project Tungsten</h2>

<p>The JVM's garbage collector is the core performance problem for large-scale Spark jobs. The GC must periodically pause all threads to reclaim heap memory. On heaps larger than 64GB, GC pauses become severe — Databricks engineers observed this directly when building Photon.</p>

<p>The deeper problem is JVM object overhead. A Java integer stored as a heap object is not 4 bytes:</p>

<div class="box n"><div class="box-lbl">JVM Object Overhead vs Compact Binary Format</div>
<table>
  <thead><tr><th>Data Type</th><th>True Size</th><th>JVM Heap Size</th><th>Overhead Factor</th></tr></thead>
  <tbody>
    <tr><td>4-byte integer</td><td>4 bytes</td><td class="rd">&gt;48 bytes (object header 16B + padding + boxing)</td><td class="rd">12×</td></tr>
    <tr><td>String "AB" (2 chars)</td><td>2 bytes</td><td class="rd">~56 bytes (object header + char array header + ref)</td><td class="rd">28×</td></tr>
    <tr><td>Long (64-bit)</td><td>8 bytes</td><td class="rd">24 bytes (16B header + 8B field)</td><td class="rd">3×</td></tr>
    <tr><td>Integer in Tungsten UnsafeRow</td><td>4 bytes</td><td class="g">4 bytes (compact binary, no object overhead)</td><td class="g">1×</td></tr>
  </tbody>
</table>
</div>

<div class="box n"><div class="box-lbl">Why a 4-byte String Becomes 48+ Bytes in JVM — Step by Step</div>
<p>Every Java object on the heap carries a mandatory <strong>object header</strong> of 16 bytes: 8 bytes for the class pointer (reference to the class metadata / klass word) and 8 bytes for the identity hash code, GC flags, and lock state. This 16-byte header exists on every object, even an object that holds a single boolean.</p>
<p>A Java <code>String</code> is not a primitive — it is a heap object. When Spark represents a 4-byte string <code>"ABCD"</code> on the JVM heap:</p>
<ol>
  <li><strong>String object itself:</strong> 16B header + 4B field (reference to char array) + 4B field (hash code cache) + 4B field (length / coder byte in Java 9+) = ~28 bytes minimum</li>
  <li><strong>char[] array object</strong> holding the actual characters: 16B header + 4B for array length + 4 chars × 2 bytes each = 28 bytes</li>
  <li><strong>Object reference from String to array:</strong> 8 bytes on 64-bit JVM</li>
  <li><strong>Alignment padding:</strong> JVM aligns objects to 8-byte boundaries, adding up to 7 bytes of padding per object</li>
</ol>
<p>Total for a 4-byte string: approximately 28 + 28 + 8 + alignment ≈ <strong>48–64 bytes</strong>. Databricks measured this overhead directly when building Tungsten and published the ">48 bytes for a 4-byte string" figure. The same logic applies to boxed integers: a <code>java.lang.Integer</code> is 16B header + 4B field + 4B padding = 24 bytes for what should be 4 bytes of data.</p>
</div>

<p>Project Tungsten is Spark's initiative to bypass JVM object overhead entirely. Tungsten's memory manager operates directly against binary data (the <code>UnsafeRow</code> format) in off-heap memory, bypassing the JVM garbage collector. The key insight: a 4-character string that occupies 48–64 bytes as a JVM heap object is stored as exactly <strong>4 bytes</strong> in Tungsten's binary UnsafeRow format — compact binary without object headers, without the char[] wrapper object, without alignment padding. More importantly, the JVM GC does not scan off-heap memory at all — those 4 bytes are invisible to the GC regardless of how many billions of such strings exist in the executor's Tungsten memory. GC pause time is determined by the number of live objects on the JVM heap; Tungsten removes the entire data plane from the heap, keeping GC overhead low even as data volume grows to hundreds of gigabytes. Three components:</p>
<ol>
  <li><strong>Off-heap memory management via <code>sun.misc.Unsafe</code>:</strong> Data stored in compact binary format at raw physical memory addresses, outside the JVM heap entirely. The JVM GC never scans this memory — it is invisible to the garbage collector. This eliminates GC pause pressure for the data plane, which matters most when heaps exceed 32–64 GB where GC pauses become multi-second events. Data is accessed via <code>sun.misc.Unsafe</code> pointer arithmetic — essentially C-style memory management inside the JVM.</li>
  <li><strong>Cache-aware computation:</strong> Data structures are designed around CPU cache line sizes (64 bytes), so sequential access patterns remain in cache and avoid cache misses.</li>
  <li><strong>Code generation (Janino compiler):</strong> Catalyst Phase 4 uses Scala quasiquotes to generate a custom Java class at runtime and compiles it to JVM bytecode using the <strong>Janino</strong> compiler (a lightweight Java compiler embedded in Spark). For each query, this produces a single tight loop that inlines all filter conditions, projections, and hash computations — no virtual dispatch between operators, no generic interpreter overhead. The JIT compiler can optimize this hot method as a single unit.</li>
</ol>

<div class="box n"><div class="box-lbl">RDD String vs DataFrame Tungsten Binary — Concrete Memory Comparison</div>
<p>Consider a dataset of 1 million rows, each containing a 4-character string ID (e.g., <code>"ABCD"</code>) and an integer value.</p>
<table>
  <thead><tr><th>Storage Mode</th><th>Per-row heap cost</th><th>Total for 1M rows</th><th>GC pressure</th></tr></thead>
  <tbody>
    <tr><td>RDD[String] — JVM heap objects</td><td class="rd">~72 bytes (String obj 28B + char[] 28B + ref 8B + Integer obj 24B)</td><td class="rd">~72 MB on JVM heap</td><td class="rd">High — millions of objects to scan</td></tr>
    <tr><td>DataFrame — Tungsten UnsafeRow (off-heap)</td><td class="g">8 bytes (4B compact binary string + 4B integer, no object headers)</td><td class="g">~8 MB, zero JVM heap objects</td><td class="g">None — off-heap is GC-invisible</td></tr>
  </tbody>
</table>
<p>The same logical data consumes 9× more heap in RDD format and generates millions of JVM objects that the GC must trace. In a DataFrame with Tungsten encoding, those objects don't exist on the heap at all — GC has nothing to scan. For a 10 GB dataset, this can reduce GC pause time from minutes to near-zero.</p>
</div>

<p>Off-heap memory is disabled by default. Enable with: <code>spark.memory.offHeap.enabled = True</code> and <code>spark.memory.offHeap.size</code> (a positive byte count). Off-heap has only two regions: execution and storage (split by <code>spark.memory.storageFraction</code>). The 300MB reserved memory is heap-only and still applies.</p>
</div>

<div class="topic">
<h2>Join Strategy Memory Impact: SHJ vs SMJ Spill Behavior</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>The join strategy Catalyst selects directly determines whether your executor can survive a large or skewed partition. Sort Merge Join can always spill to disk when a partition is too large — it keeps running, just slower. Shuffle Hash Join has no spill path for the build phase: if the build-side partition is too large, the executor throws OOM with no recovery. This distinction is critical for production OOM diagnosis.</p>
</div>

<h3>Sort Merge Join (SMJ) — Disk-Safe Memory Behavior</h3>
<p>SMJ works in three phases: shuffle both sides, sort within each partition, then merge the sorted iterators. Critically, the <strong>sort step can spill to disk</strong>. Spark's external sort algorithm writes sorted runs to local disk when the sort buffer exceeds a threshold, then performs a multi-way merge over those runs. This means an SMJ partition can be larger than executor memory — the operation slows down due to disk I/O, but it completes successfully. SMJ is the correct choice for large-large joins precisely because it degrades gracefully under memory pressure.</p>

<h3>Shuffle Hash Join (SHJ) — No Spill Path for the Build Phase</h3>
<p>SHJ's build phase loads the entire build-side partition into an in-memory hash table. A hash table cannot spill — a partially-resident hash table cannot serve lookups correctly because the lookup key might map to a row that was spilled. Spark has no mechanism to bring spilled hash table entries back on demand. Therefore: <strong>if the build-side partition exceeds available Execution memory, SHJ throws OOM with no recourse</strong>. Unlike SMJ, there is no "SHJ with spill" mode. The only options are: reduce the build-side partition size (more shuffle partitions), add executor memory, or switch to SMJ.</p>

<div class="box f"><div class="box-lbl">SHJ OOM: Why Skewed Data Makes It Catastrophic</div>
<p>Data skew amplifies SHJ's no-spill constraint. Suppose the build side has 10 partitions averaging 100MB each — well within executor memory. But one hot key concentrates 40% of build-side data into a single partition: 400MB in one SHJ build phase. If the executor's available Execution memory is 300MB, this single partition throws OOM. The other 9 partitions succeed; only the skewed one fails — making it look like an intermittent failure rather than a structural problem. The root cause: SHJ build phase has no spill path, so any partition exceeding available Execution memory causes failure. SMJ on the same data would slow down (sort spills to disk) but complete successfully.</p>
<p><strong>Production rule:</strong> Reserve SHJ for cases where you have tight control over build-side partition sizes and know skew is absent. For general production joins with unknown data distributions, prefer SMJ (Spark's default) or BHJ (if one side is small enough to broadcast).</p>
</div>

<h3>Broadcast Hash Join, autoBroadcastJoinThreshold, and the OOM Risk of Over-Broadcasting</h3>
<p>When Catalyst estimates a table is below <code>spark.sql.autoBroadcastJoinThreshold</code> (default <strong>10 MB</strong> / 10,485,760 bytes), it automatically selects Broadcast Hash Join. The entire small table is serialized on the driver and replicated to <strong>every executor</strong>, stored in <strong>executor Storage memory</strong>. This is why table size relative to the threshold is directly relevant to memory planning:</p>

<div class="box n"><div class="box-lbl">BHJ: The Serialization-and-Broadcast Sequence — What Happens Step by Step</div>
<p>Understanding the physical sequence of a BHJ explains both its performance advantage and its OOM risk:</p>
<ol>
  <li><strong>Catalyst selects BHJ</strong> because the estimated size of the small table is below <code>autoBroadcastJoinThreshold</code> (default 10 MB). No Exchange (shuffle) node is inserted for either table in the physical plan.</li>
  <li><strong>The small table is fully collected on the driver.</strong> All tasks reading the small table complete and send their partitions to the driver. The driver assembles the entire small table into a single in-memory structure.</li>
  <li><strong>The driver serializes the table into a compact binary format</strong> (Tungsten UnsafeRow binary). This serialized blob is what gets broadcast — not JVM objects.</li>
  <li><strong>The driver sends the serialized blob to every executor</strong> via Spark's BlockManager broadcast channel (HTTP multicast, typically a torrent-like distributed protocol). Every executor in the cluster receives a full copy simultaneously.</li>
  <li><strong>Each executor deserializes the blob and stores it in executor Storage memory</strong> as a broadcast variable. This Storage memory comes from the Unified pool — the same pool shared with cached RDD partitions. A 10 MB broadcast table uses 10 MB of Storage memory on every executor.</li>
  <li><strong>The large table is read directly from source</strong> (no shuffle or repartition). Each partition of the large table is processed by a task on the co-located executor, which looks up each row's join key in the locally-held broadcast hash table. Hash lookup is O(1).</li>
  <li><strong>No Exchange operator exists in the plan</strong> — the absence of an Exchange node for either input is how you identify BHJ in the Spark UI "Physical Plan" tab. SMJ and SHJ both show Exchange nodes; BHJ shows none.</li>
</ol>
<p><strong>Memory consequence:</strong> The broadcast variable persists in executor Storage memory for the entire duration of the job (it can be manually unpersisted via <code>spark.sparkContext.broadcast(table).unpersist()</code>). On a 200-executor cluster, a 10 MB broadcast table occupies 10 MB × 200 = 2 GB of total cluster Storage memory for as long as the job runs.</p>
<p><strong>SMJ as the default fallback when BHJ is not selected:</strong> When Catalyst estimates both tables exceed <code>autoBroadcastJoinThreshold</code>, the default fallback is Sort Merge Join — not Shuffle Hash Join. SMJ shuffles both sides by join key, sorts within each partition, and merges the sorted iterators in one pass, spilling safely to disk if partitions are large. SHJ is only selected if explicitly enabled or if AQE's runtime statistics confirm the build-side partition fits in Execution memory.</p>
</div>

<ul>
  <li>A 2 MB dimension table → BHJ selected automatically → zero shuffle of either table; 2 MB per executor in Storage memory → negligible memory cost, maximum performance</li>
  <li>A 6 MB dimension table → also below 10 MB → BHJ selected automatically; one copy of 6 MB per executor in Storage memory</li>
  <li>A 15 MB dimension table → above 10 MB → Catalyst picks SMJ instead; both sides are shuffled by join key, sorted, and merged with disk-spill safety.</li>
</ul>

<div class="box f"><div class="box-lbl">BHJ OOM Arithmetic — Why Raising the Threshold Is Dangerous at Scale</div>
<p>BHJ memory cost is <code>table_size × number_of_executors</code> — not table_size alone. Every executor in the cluster receives a full copy of the broadcast table simultaneously:</p>
<ul>
  <li><strong>10 MB table, 200 executors:</strong> 10 MB × 200 = 2 GB total cluster memory for the broadcast. Each executor uses 10 MB of Storage memory. Safe.</li>
  <li><strong>2 GB table, 200 executors:</strong> 2 GB × 200 = <strong>400 GB</strong> of cluster-wide heap pressure. Each executor must hold a 2 GB copy in Storage memory. If executor Storage memory (unified pool) is ~1 GB, this exceeds available Storage memory on every executor <em>simultaneously</em> — causing OOM on every executor at the same moment the broadcast arrives. This is not a single-executor failure; it is a cluster-wide simultaneous OOM event.</li>
</ul>
<p>This is why <code>autoBroadcastJoinThreshold</code> must be set with awareness of executor count and executor Storage memory, not just the table size in isolation. Raising the threshold to 500 MB on a 500-executor cluster could demand 250 GB of broadcast memory — exceeding the entire cluster's Storage pool. The safe rule: <code>table_size × executor_count ≤ 50% of total cluster Storage memory</code>.</p>
<p><strong>Override options:</strong> Set <code>spark.sql.autoBroadcastJoinThreshold = -1</code> to disable automatic broadcast entirely. Use <code>/*+ BROADCAST(small_table) */</code> hint to broadcast selectively on a per-query basis. Use <code>spark.sql.autoBroadcastJoinThreshold = 52428800</code> to raise to 50 MB.</p>
</div>

</div>

<div class="topic">
<h2>OOM Root Cause: Data Skew and the Memory Dilution Effect</h2>

<div class="box f"><div class="box-lbl">The Fundamental OOM Insight — Adding Memory Does Not Fix Skew</div>
<p>The most common and most expensive mistake when debugging Spark OOMs: increasing executor memory. This works only when OOM is caused by insufficient total memory. It <strong>does not work</strong> when OOM is caused by data skew.</p>
<p><strong>The arithmetic:</strong> Suppose partition 1 has 80% of the data after a shuffle. The task processing partition 1 needs 80% of its executor's unified memory pool. If the executor has 8GB heap (unified pool ≈ 4.5GB), that task needs ~3.6GB. It fails. You double the executor to 16GB (unified pool ≈ 9.4GB). The task still receives the same 80% skewed partition — it still needs 80% of the unified pool ≈ 7.5GB. Still OOM, just at a higher absolute threshold. <strong>Adding memory scales the allocation but not the imbalance.</strong> The skewed task's share of total data — 80% — is unchanged by executor sizing. Whatever memory you provide, the task consumes 80% of it, because the partition holds 80% of the data.</p>
<p><strong>The correct fix requires breaking the partition.</strong> Options: (1) <strong>Repartition / increase shuffle.partitions</strong> — more partitions means smaller absolute partition sizes, but a single dominant skewed key still concentrates in one partition; (2) <strong>Salting</strong> — artificially split the hot key into N sub-keys so data distributes across N partitions; (3) <strong>AQE skew join handling</strong> — detects oversized shuffle partitions at runtime and automatically splits them into sub-partitions without code changes. All three fix the partition size directly. Adding executor memory fixes nothing.</p>
</div>

<p><strong>spark.sql.shuffle.partitions defaults to 200 — hardcoded, not derived from data size or cluster size.</strong> This value is a static default in Spark's configuration. It does not adapt to the amount of data in the job, the number of executors, or the executor memory. Whether you're processing 10 MB or 500 GB of data, Spark creates exactly 200 shuffle partitions by default.</p>

<div class="box f"><div class="box-lbl">The 200-Partition Default: Memory Consequences and Parallelism Waste</div>
<p><strong>On large data (e.g., 500 GB):</strong> 500 GB ÷ 200 partitions = <strong>2.5 GB per partition per task</strong>. A 4 GB executor with ~2.3 GB unified memory cannot hold a 2.5 GB sort buffer or hash table for that task without spilling. Spill increases disk I/O and execution time; in a Shuffle Hash Join, 2.5 GB per build-side partition causes OOM immediately since SHJ cannot spill. Even with SMJ (which can spill), the sort buffer pressure causes heavy disk I/O that negates Spark's in-memory advantage.</p>
<p><strong>Parallelism waste — idle cores:</strong> With only 200 shuffle partitions, the cluster spawns exactly 200 tasks for the shuffle stage. If the cluster has 500 executor cores available, 300 cores sit idle while the 200 tasks execute. All 200 tasks must complete before the next stage can begin — so even if each task runs quickly, the absolute wall-clock time is bounded by the slowest of 200 tasks, not by cluster parallelism. The cluster's additional capacity is wasted.</p>
<p><strong>On small data:</strong> 200 partitions on a 10 MB dataset means each partition averages 50 KB — 200 tasks each doing trivial work with high scheduling overhead per task (driver-to-executor round-trip, serialization, task setup). The overhead may exceed the actual computation time.</p>
<p><strong>Fix paths:</strong></p>
<ol>
  <li><strong>Manual tuning:</strong> Set <code>spark.sql.shuffle.partitions</code> to approximately <code>total_shuffle_data_GB × 4</code> as a starting point — targeting ~250 MB per partition. For 500 GB: set to 2000. For 10 MB: set to 5.</li>
  <li><strong>AQE adaptive coalescing (recommended for Spark 3.0+):</strong> Enable <code>spark.sql.adaptive.enabled = true</code> and <code>spark.sql.adaptive.coalescePartitions.enabled = true</code>. AQE inspects actual partition sizes after each shuffle stage and automatically merges adjacent small partitions into fewer, larger ones. This eliminates the need to manually predict partition counts — you can set <code>spark.sql.shuffle.partitions</code> high (e.g., 2000) and let AQE coalesce them down to a reasonable number based on actual data volume. Target partition size is controlled by <code>spark.sql.adaptive.advisoryPartitionSizeInBytes</code> (default 64 MB).</li>
</ol>
</div>

<p><strong>Parquet inflation in memory:</strong> Do not use Parquet file size on disk to estimate memory requirements. Parquet is compressed (SNAPPY or ZSTD by default). When read into memory, it must be decompressed and deserialized. In Vu Trinh's measured experiment: a 2.6GB Parquet file on disk consumed 3.7GB in executor memory — a 1.42× inflation factor. Multiply your compressed file sizes by at least 1.5× when estimating executor memory needs.</p>

<p><strong>More cores per executor = less memory per task.</strong> If you have 4GB executor memory and 4 cores, 4 tasks can run simultaneously. Each task gets 1GB of the unified memory pool. If you increase to 8 cores on the same executor, 8 tasks run simultaneously — each task gets only 500MB. More parallelism squeezes every individual task's memory budget. For memory-intensive operations (large shuffles, hash join build phases), fewer cores per executor (more memory per task) is sometimes better.</p>

<p><strong>HashAggregate vs SortAggregate:</strong> Spark prefers HashAggregate, which builds an in-memory hash table for groupBy operations using the Tungsten UnsafeRow binary format. This works efficiently when the groupBy column has a fixed-size type (integer, long, double). When the aggregation involves variable-width types (String), the UnsafeRow format cannot efficiently represent a mutable-size field in the hash table — Spark falls back to SortAggregate, which sorts the data first and then aggregates in a streaming pass. SortAggregate is slower and spills more.</p>

<div class="box n"><div class="box-lbl">Key Configuration Parameters</div>
<table>
  <thead><tr><th>Config</th><th>Default</th><th>What It Controls</th></tr></thead>
  <tbody>
    <tr><td><code>spark.memory.fraction</code></td><td>0.6</td><td>Fraction of (heap - 300MB) going to unified memory</td></tr>
    <tr><td><code>spark.memory.storageFraction</code></td><td>0.5</td><td>Initial split of unified memory between storage and execution</td></tr>
    <tr><td><code>spark.sql.shuffle.partitions</code></td><td class="rd">200</td><td>Number of shuffle partitions — tune to data size</td></tr>
    <tr><td><code>spark.sql.autoBroadcastJoinThreshold</code></td><td>10MB</td><td>Max table size for auto-broadcast hash join</td></tr>
    <tr><td><code>spark.memory.offHeap.enabled</code></td><td>false</td><td>Enable Project Tungsten off-heap storage</td></tr>
    <tr><td><code>spark.sql.files.maxPartitionBytes</code></td><td>256MB</td><td>Max bytes per partition when reading Parquet</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="topic">
<h2>AQE Skew Join Handling: Runtime Detection and Automatic Partition Splitting</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>AQE watches the size of every shuffle partition after it's written to disk. If one partition is much larger than the others (a skewed partition), AQE splits it into smaller sub-partitions and duplicates the matching portion of the other join side for each sub-partition. The skewed partition is now processed by multiple tasks in parallel instead of one stalled task — and no code changes are required.</p>
</div>

<p>Data skew in join operations is one of the most damaging OOM and straggler patterns in Spark. Without AQE, the only fixes are manual: salting (adding random prefixes to split hot keys) or repartitioning with more partitions. Both require code changes and knowledge of which keys are skewed. AQE's skew join handling solves this automatically, at runtime, using the actual shuffle statistics that are already available at every stage boundary.</p>

<h3>How AQE Detects Skewed Partitions</h3>
<p>After a shuffle stage completes, AQE collects the size of every output partition. It computes the <strong>median partition size</strong> across all partitions in that stage. A partition is flagged as skewed if it satisfies <em>both</em> of the following conditions:</p>
<ul>
  <li>Its size exceeds <code>median × spark.sql.adaptive.skewJoin.skewedPartitionFactor</code> (default: <strong>5</strong>)</li>
  <li>Its absolute size exceeds <code>spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes</code> (default: <strong>256 MB</strong>)</li>
</ul>
<p>Both conditions must be true. The two-condition rule prevents false positives: a tiny stage with all partitions under 1MB won't flag a "skewed" 2MB partition (the absolute threshold blocks it), and a stage where every partition is 300MB won't flag the 320MB partition as skewed (the median factor is too close).</p>

<div class="box n"><div class="box-lbl">AQE Skew Join — The Step-by-Step Splitting Mechanism</div>
<p>Suppose a join between table A and table B produces 5 shuffle partitions. The partition sizes after the shuffle stage are: P0=50MB, P1=55MB, P2=48MB, P3=600MB (skewed), P4=52MB. Median = 52MB. <code>skewedPartitionFactor = 5</code> → threshold = 52 × 5 = 260 MB. P3 at 600 MB exceeds both the factor threshold (260 MB) and the absolute threshold (256 MB). AQE flags P3 as skewed.</p>
<ol>
  <li><strong>AQE splits the skewed partition P3 into sub-partitions.</strong> Spark divides the 600MB partition into multiple sub-partitions, each targeting approximately <code>spark.sql.adaptive.advisoryPartitionSizeInBytes</code> (default 64 MB). A 600 MB skewed partition is split into ~10 sub-partitions of ~60 MB each.</li>
  <li><strong>AQE replicates the matching portion of the other join side.</strong> For P3 from table A, AQE identifies the corresponding P3 partition of table B (the portion co-located by join key). It creates a copy of this B partition for each of the 10 sub-partitions of A's P3. The B partition is now read 10 times rather than once — but each read is small, and the 10 resulting joins execute in parallel.</li>
  <li><strong>The 10 sub-join tasks run in parallel</strong> instead of one giant task processing 600 MB. Each task processes ~60 MB — well within executor memory. The straggler disappears. The other four partitions (P0–P2, P4) are processed normally as single tasks.</li>
  <li><strong>Results are unioned.</strong> AQE inserts a Union operator to combine the results of the 10 sub-joins back into a single logical partition. The join result is semantically identical to the non-AQE version.</li>
</ol>
<p><strong>Memory consequence of skew splitting:</strong> Each of the 10 sub-tasks processes ~60 MB instead of 600 MB. If the join uses SHJ (build phase into a hash table), the build-side partition is now 60 MB instead of 600 MB — easily within Execution memory. If the join uses SMJ, the sort buffer needs only 60 MB per task instead of 600 MB. AQE's skew join handling directly prevents the OOM that the skewed partition would have caused in SHJ, and eliminates the straggler that the large partition would have caused in SMJ.</p>
</div>

<div class="box f"><div class="box-lbl">AQE Skew Handling vs Manual Salting — When to Use Which</div>
<p><strong>AQE skew join handling</strong> is the first choice for Spark 3.0+ jobs. It is automatic, requires no code changes, does not require knowing which keys are skewed in advance, and adapts to changing data distributions in each run. Enable with <code>spark.sql.adaptive.enabled = true</code> and <code>spark.sql.adaptive.skewJoin.enabled = true</code> (both default to true in Spark 3.2+).</p>
<p><strong>Limitation of AQE skew handling:</strong> AQE can only split skewed partitions at existing join stage boundaries. It cannot help with skew in non-join aggregations (e.g., a <code>groupBy</code> producing a skewed result for a subsequent window function). AQE also requires the join to be performed as SMJ or SHJ — BHJ (where one side is broadcast) has no shuffle partitions for AQE to inspect and split. For BHJ, a skewed probe side cannot be split by AQE, because there is no shuffle of the probe side — data is read directly from source partitions with no redistribution step.</p>
<p><strong>Manual salting</strong> is the fallback for cases AQE cannot handle: (1) skewed aggregations without a join, (2) BHJ where AQE cannot intervene, (3) Spark 2.x environments without AQE, or (4) extreme skew where AQE's sub-partition sizes are still too large. Salting adds a random salt prefix (e.g., 0-9) to the skewed key in both join sides, artificially multiplying the key cardinality by the salt factor. The hot key's 600 MB partition becomes 10 keys of ~60 MB each — but both sides must be transformed, requiring explicit code changes.</p>
</div>

<div class="box n"><div class="box-lbl">Join Strategy × Skew Interaction — Which Strategy Handles Skew Best</div>
<table>
  <thead><tr><th>Join Strategy</th><th>Skew effect on memory</th><th>AQE skew handling available?</th><th>Manual fix needed?</th></tr></thead>
  <tbody>
    <tr><td>SMJ</td><td class="y">Straggler (slow task, not OOM — SMJ can spill)</td><td class="g">Yes — splits probe partition, replicates build</td><td>Not needed for Spark 3.0+</td></tr>
    <tr><td>SHJ</td><td class="rd">OOM (build-side partition cannot spill; large partition → task fails)</td><td class="g">Yes — splits build partition, replicates probe</td><td>Not needed for Spark 3.0+ if AQE enabled</td></tr>
    <tr><td>BHJ</td><td class="y">CPU hotspot (one executor processes all probe rows for hot key)</td><td class="rd">No — probe side is not shuffled; no AQE split opportunity</td><td class="rd">Yes — salting or force SMJ for skewed probe</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="recall">
<div class="recall-head">Spark Engineer's Checkpoint</div>
<div class="q"><span class="q-n">Q1 </span>Draw the three memory regions of a Spark executor on a 4GB heap. Provide exact byte calculations for each region with default configuration values. Show each arithmetic step explicitly — which fraction is applied to which base.</div>
<div class="q"><span class="q-n">Q2 </span>Explain the eviction asymmetry between execution and storage memory. A job that caches a 2GB table and then runs heavy aggregations starts failing with cache misses. What memory phenomenon caused this, and how would you fix it?</div>
<div class="q"><span class="q-n">Q3 </span>A colleague's solution to an OOM error is to double executor memory from 8GB to 16GB. Under what conditions will this fix the problem? Under what conditions will it not fix the problem? How do you tell which situation you are in?</div>
<div class="q"><span class="q-n">Q4 </span>spark.sql.shuffle.partitions is 200. You're processing a 50GB dataset. What are the consequences of leaving it at 200? How would you estimate the right value?</div>
<div class="q"><span class="q-n">Q5 </span>Why does a 4-byte integer in a JVM object consume more than 48 bytes on the heap? What does Project Tungsten do differently, and how does this affect GC behavior?</div>
<div class="q"><span class="q-n">Q6 </span>A Shuffle Hash Join on a skewed build side throws OOM. Explain why SHJ cannot handle this by spilling to disk (unlike SMJ). What happens inside the SHJ build phase when the partition exceeds Execution memory?</div>
<div class="q"><span class="q-n">Q7 </span>Your dimension table is 6 MB. What join strategy does Spark select automatically, and why? Walk through the BHJ serialization-and-broadcast sequence step by step. What configuration parameter controls the threshold, what is its default value, and what is the memory cost on each executor?</div>
<div class="q"><span class="q-n">Q8 </span>A job fails with OOM on Thursday but passed Monday. Data volume and code are identical. Explain the chain of causation: what role does scheduling nondeterminism play, why does the skewed partition sometimes hit a constrained executor, and what is the correct fix?</div>
<div class="q"><span class="q-n">Q9 </span>A colleague doubles executor memory from 8GB to 16GB to fix a skew-induced OOM. The job still fails. Explain why doubling memory does not help when the OOM is caused by data skew — walk through the arithmetic showing why the skewed task's memory requirement scales proportionally with the executor size.</div>
<div class="q"><span class="q-n">Q10 </span>AQE is enabled and your SMJ join has a 600 MB skewed partition while the median is 50 MB. Walk through exactly what AQE does: how does it detect the skew, how does it split the partition, and what happens to the matching partition of the other join side? Under what circumstances would AQE's skew handling NOT help?</div>
</div>

<div class="box teach"><div class="box-lbl">How to Teach This Chapter</div>
<p><strong>Junior engineer (10 min):</strong> Start with the 4GB executor calculation. Walk through the three regions step by step, emphasizing that <code>storageFraction</code> applies to the Unified pool (not total heap). Then ask: "If you cache a 1.5GB RDD and immediately run a large shuffle, what happens to the cache?" Use the eviction asymmetry to explain. End with the skew/OOM insight — draw the 80% skew scenario on a whiteboard.</p>
<p><strong>Senior engineer (25 min):</strong> Cover the Parquet inflation factor (2.6GB → 3.7GB). Derive the memory-per-task formula as you add more cores. Walk through the SHJ vs SMJ spill distinction: draw an in-memory hash table and ask "what happens when this partition grows past available Execution memory?" (SHJ: OOM; SMJ: disk spill, continue). Cover AQE skew handling: draw the partition size histogram (P0–P4), show AQE identifying P3 as skewed (600MB > median 52MB × 5), split into 10 sub-partitions, replicate B side 10 times. End: "Given this memory model, design the executor configuration for a job that joins a 50GB fact table with a 6MB dimension table — and explain why the 6MB matters."</p>
</div>

<div class="box gap"><div class="box-lbl">Questions This Chapter Doesn't Answer</div>
<ul>
  <li>How does dynamic resource allocation interact with the unified memory model — does memory per executor change as executors are added or removed?</li>
  <li>What is the exact spill mechanism — how does Spark decide when to spill, and where on disk does the spill land?</li>
  <li>How do Spark's memory metrics (Storage Memory Used, Execution Memory Used) map to JVM heap profiling tools like JVisualVM or async-profiler?</li>
  <li>Can AQE be extended to detect and handle skew in non-join aggregations (e.g., a GROUP BY producing skewed output for a subsequent window function)?</li>
</ul>
</div>
</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 3 — Shuffle, Joins, and Skew
# ─────────────────────────────────────────────────────────────────────────────
CH3 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 3 of 5</div>
  <h1>Shuffle, Joins (SMJ / SHJ / Broadcast), and Skew</h1>
  <div class="ch-src">Source: vutr.substack.com — 10 Minutes to Learn Apache Spark JOINs · Lesson learned after reading the BigQuery paper: Shuffle operation · The Spark Scheduling Process</div>
  <p class="ch-sum">Shuffle is the single most expensive operation in Spark — it crosses stage boundaries with disk writes and network transfers. Understanding the three join strategies, when Catalyst chooses each one, and how data skew turns any join into a production incident gives you the complete picture for join optimization.</p>
</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>Despite Spark's reputation as an "in-memory" engine, shuffle writes to disk. Every groupBy, join, repartition, and sort crosses a stage boundary where Spark writes shuffle output files to local disk, transfers them over the network to the next stage's executors, and reads them back from disk. This disk + network cost is the dominant bottleneck in most production Spark jobs. The three join strategies — Sort Merge Join, Shuffle Hash Join, and Broadcast Hash Join — exist because different data sizes and distributions call for radically different approaches. Choosing the wrong one silently costs 10× performance or causes OOM.</p>
</div>

<div class="topic">
<h2>Why Shuffle Writes to Disk (The In-Memory Myth)</h2>

<div class="box f"><div class="box-lbl">The Most Common Spark Misconception</div>
<p>Spark is routinely described as an "in-memory" engine. This is true for narrow transformations within a stage — data flows from one transformation to the next in memory, never touching disk. But at every wide dependency boundary (every shuffle), Spark writes to disk. The data path for a shuffle is: task writes output → <strong>disk</strong> → network transfer → <strong>disk</strong> → next stage task reads. Two disk operations and a network transfer for every stage boundary. Vu Trinh explicitly corrects this misconception: shuffle is disk-based even in Spark.</p>
</div>

<p>The shuffle mechanism works as follows. When stage N contains a wide dependency (e.g., a <code>groupByKey</code>), each task in stage N must redistribute its output records by key so that all records with the same key arrive at the same partition in stage N+1. Each task:</p>
<ol>
  <li>Partitions its output records by <code>key.hashCode() % numPartitions</code></li>
  <li>Writes the partitioned records to local disk as <strong>shuffle map output files</strong> (one file per output partition)</li>
  <li>Registers the file locations with the BlockManager</li>
</ol>
<p>Stage N+1 cannot begin until all tasks in stage N have completed and registered their shuffle files. Then each task in stage N+1 fetches its assigned partition's files from the disk of all stage N executors over the network, reads them from disk, and processes them.</p>

<p>Why disk at the shuffle boundary? Because stage N+1 tasks may need to read data from any stage N task — the data must be durable and accessible from any executor in the cluster. In-memory shuffle would require all stage N outputs to remain in memory until all stage N+1 tasks complete reading them — this would require holding both stages' data in memory simultaneously, defeating the memory model.</p>

<div class="box n"><div class="box-lbl">Fault Tolerance Rationale for Disk-Based Shuffle</div>
<p>Beyond memory constraints, durability of shuffle files on disk provides a critical fault tolerance property: <strong>if a reducer task (stage N+1) fails, it can be restarted and re-read its shuffle input from the map-side disk files without requiring stage N to be recomputed</strong>. The map-side shuffle files persist on disk until the job completes. Only if a <em>map task</em> (stage N) executor dies and the shuffle files it produced are lost must stage N be re-executed. This asymmetry — reducer failures are cheap (just re-read existing shuffle files), mapper failures are expensive (must re-run the map stage) — is why the <code>ExternalShuffleService</code> exists: it decouples shuffle file serving from executor lifecycle so that even if the map-side executor is killed, the shuffle files remain available, making reducer restarts trivially cheap without any stage re-execution.</p>
</div>

<h3>The Quadratic Scaling Problem (from BigQuery's Dremel paper)</h3>
<p>Google's Dremel paper (cited by Vu) identified that traditional MapReduce shuffle has quadratic scaling: as the number of mappers (M) and reducers (R) both grow, the number of network connections is M × R. With 1,000 mappers and 1,000 reducers: 1,000,000 network connections. The coupling of compute and temporary storage cannot scale independently — this was a major bottleneck. Google's solution: a separate distributed transient shuffle storage system where shuffle data is written once and consumed by reducers independently of the producing executor's lifecycle. Industry parallels: Uber's "Shuffle as a Service," Meta's Riffle (EuroSys 2018).</p>

<h3>Data Locality in Shuffle Reads</h3>
<p>Spark's <code>ExternalShuffleService</code> decouples shuffle file serving from executor lifecycle. When enabled, shuffle files are served from the external service rather than from executor processes. If an executor dies, its shuffle output files are still available for the next stage — without this, executor failure in stage N would require re-running all of stage N.</p>
</div>

<div class="topic">
<h2>Sort Merge Join (SMJ): The Default for Large-Large Joins</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Both tables are sorted by join key so that matching records appear next to each other. Then two read heads scan through both sorted lists simultaneously — like merging two sorted decks of cards. Because both are sorted, you only need one pass through each. And if a partition is too big for memory, it can safely spill to disk.</p>
</div>

<p>Sort Merge Join works in three phases:</p>
<ol>
  <li><strong>Shuffle both sides:</strong> Both tables are repartitioned by join key using the same hash function and partition count. All records with key K from both tables end up in the same partition on the same executor. Requires a shuffle of both tables — two full network transfers.</li>
  <li><strong>Sort within each partition:</strong> Both sides are sorted by join key within each partition. This creates a sorted order that the merge step exploits.</li>
  <li><strong>Merge:</strong> Two sorted iterators scan through both sides simultaneously. O(n + m) complexity — Spark only needs one pass through each dataset. When keys match, emit the joined row; when one side's key is smaller, advance that side's iterator.</li>
</ol>

<p>Critical property: SMJ <strong>can spill to disk safely</strong>. The sort operation can write sorted runs to disk and merge them externally. This means SMJ works correctly even when partitions are larger than executor memory — it just becomes slower. This disk-safe property is why SMJ is the default for large-large joins before Spark 3.0.</p>

<div class="box n"><div class="box-lbl">SMJ Technical Specifications</div>
<table>
  <thead><tr><th>Property</th><th>Value</th></tr></thead>
  <tbody>
    <tr><td>Algorithm complexity</td><td>O(n + m) — single merged pass after sorting</td></tr>
    <tr><td>Shuffle required</td><td class="rd">Yes — both tables fully shuffled by join key</td></tr>
    <tr><td>Memory requirement</td><td>Sort buffer per partition; can spill to disk</td></tr>
    <tr><td>Disk spill safety</td><td class="g">Yes — external sort handles partitions larger than memory</td></tr>
    <tr><td>Best for</td><td>Large-large table joins when neither table fits in broadcast threshold</td></tr>
    <tr><td>Pre-sorted tables (bucketed)</td><td class="g">No shuffle needed — see Bucket Join section</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="topic">
<h2>Shuffle Hash Join (SHJ): Fast But Fragile</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>The smaller table (build side) is loaded entirely into a hash table in memory. The larger table (probe side) streams through, looking up each key in the hash table. Very fast — hash lookup is O(1). But if the build side's partition doesn't fit in memory, the executor throws OOM with no recourse.</p>
</div>

<p>SHJ has two phases:</p>
<ol>
  <li><strong>Build phase:</strong> The smaller table (build side) is shuffled to executors. Each executor reads its partition of the build side and loads it entirely into an in-memory hash table. The hash table maps join key → list of matching rows.</li>
  <li><strong>Probe phase:</strong> The larger table (probe side) streams through partition by partition. Each row's join key is looked up in the hash table — O(1) per lookup.</li>
</ol>

<div class="box f"><div class="box-lbl">Why SHJ Was Removed in Spark 1.6 and Reintroduced in Spark 2.0</div>
<p>SHJ requires the build side partition to fit entirely in memory. If the build side is large, or if data is skewed such that one partition of the build side is disproportionately large, the executor runs out of memory building the hash table. <strong>Unlike SMJ, SHJ cannot spill to disk</strong> — a hash table must be fully resident to serve lookups correctly. This caused enough production OOMs that Spark 1.6 removed SHJ entirely. Spark 2.0 reintroduced it with stricter guardrails: <code>spark.sql.adaptive.maxShuffledHashJoinLocalMapThreshold = 0</code> by default, meaning the optimizer always skips SHJ unless explicitly enabled. Even with AQE's dynamic join switching, SHJ is only selected when the build-side partition is confirmed to fit in memory at runtime.</p>
</div>

<p>Vu's production rule: "In a production Spark application, make sure you know what you're doing when enabling SHJ; it's only efficient when the build-side partitions fit in memory. If they get larger for some reason, your application will likely get an OOM error."</p>
</div>

<div class="topic">
<h2>Broadcast Hash Join (BHJ): The Best Join When It Fits</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>The small table is broadcast (sent as a complete copy) to every single executor in the cluster. Then every executor can perform the join locally — no network shuffle at all. The network cost is one broadcast (small table × num executors) instead of two full shuffles.</p>
</div>

<p>BHJ has one requirement: one side must fit in memory on every executor simultaneously. Spark's automatic broadcast threshold: if Catalyst estimates a table is smaller than <code>spark.sql.autoBroadcastJoinThreshold</code> (default <strong>10MB</strong>), it automatically selects BHJ. The broadcast table is serialized on the driver, sent to all executors via the BlockManager's broadcast channel, and each executor deserializes and stores it in Storage memory.</p>

<div class="box f"><div class="box-lbl">BHJ: Shuffle Eliminated, Not Reduced</div>
<p>The critical distinction between BHJ and the other join strategies is that BHJ <strong>eliminates</strong> the shuffle — it does not merely reduce it. SMJ and SHJ both require a full shuffle of both tables to co-locate matching keys. BHJ requires zero shuffle of either table: the large table is read directly from its source partitions without repartitioning, and the small table is broadcast as a complete copy to every executor. In an execution plan, a BHJ appears with <strong>no <code>Exchange</code> operator</strong> on either side — the exchange step literally does not exist in the physical plan. This is why BHJ is so dramatically faster than SMJ for small-large joins: the dominant cost (two full shuffles) is entirely absent, not merely reduced. The trade-off is that the broadcast table must fit in executor Storage memory on every executor simultaneously — if any executor runs low on storage memory, the broadcast variable can be evicted, triggering OOM or re-broadcast.</p>
</div>

<p>The key advantage: <strong>BHJ eliminates shuffle entirely</strong>. In the execution plan, you will see no <code>Exchange</code> nodes before a BHJ — the typical shuffle step simply doesn't exist. The large table can be read directly from its source (no repartitioning needed) because the small table comes to every partition of the large table, not the other way around.</p>

<div class="box n"><div class="box-lbl">Broadcast Hash Join vs Sort Merge Join — When BHJ Wins Massively</div>
<table>
  <thead><tr><th>Property</th><th>Broadcast Hash Join</th><th>Sort Merge Join</th></tr></thead>
  <tbody>
    <tr><td>Small table shuffle</td><td class="g">None — broadcast copy to all executors</td><td class="rd">Full shuffle of both tables</td></tr>
    <tr><td>Large table shuffle</td><td class="g">None</td><td class="rd">Full shuffle</td></tr>
    <tr><td>Memory requirement</td><td>Small table must fit in executor Storage memory</td><td>Sort buffer; can spill</td></tr>
    <tr><td>Join algorithm</td><td>Hash table lookup O(1) per row</td><td>Merge of sorted iterators O(n+m)</td></tr>
    <tr><td>Auto-selected when</td><td>Either side &lt; 10MB (autoBroadcastJoinThreshold)</td><td>Neither side qualifies for BHJ or SHJ</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="topic">
<h2>Bucket Join: Paying the Shuffle at Write Time</h2>

<p>The most powerful join optimization for repeatedly-joined tables. Vu Trinh's verbatim definition: <em>"A bucket join is when you shuffle the data during write time rather than during join time, which is helpful when you know how the tables are joined and aggregated beforehand."</em></p>

<p>When two tables are bucketed on the same column with the same number of buckets (using <code>bucketBy(n, column).saveAsTable()</code>), the data is pre-shuffled at write time. All rows with join key K from both tables land in the same bucket file. At join time, Spark reads bucket N of table A and bucket N of table B — they are already co-partitioned. <strong>No shuffle is needed.</strong></p>

<p>The constraint: <code>bucketBy()</code> only works with <code>saveAsTable()</code>, not with <code>write.parquet()</code>. Bucketing metadata (which column, how many buckets) must be stored in the Hive metastore so Spark can use it at join time. Both tables must be bucketed with the same number of buckets on the join key — if one has 50 buckets and the other has 100 buckets, the co-partitioning property breaks and Spark must shuffle anyway.</p>

<h3>Join Strategy Hint Priority</h3>
<p>Spark 3.0+ allows query hints to suggest a join strategy. When multiple hints conflict, Spark enforces this priority order:</p>
<ol>
  <li><strong>BROADCAST</strong> — highest priority; triggers BHJ</li>
  <li><strong>MERGE</strong> — triggers SMJ</li>
  <li><strong>SHUFFLE_HASH</strong> — triggers SHJ</li>
  <li><strong>SHUFFLE_REPLICATE_NL</strong> — nested loop join (no index; expensive)</li>
</ol>
<p>Important caveat: hints are suggestions, not mandates. The optimizer can reject a hint if the selected strategy is incompatible with the logical join type or if required conditions (like a build side fitting in memory for SHJ) are not met.</p>
</div>

<div class="topic">
<h2>Data Skew: The Silent Production Killer</h2>

<p>Data skew occurs when one key (or a small set of keys) has far more values than other keys. After a shuffle, all values for the skewed key land in one partition — one task processes 80% of the data while 199 other tasks process the remaining 20%. Symptoms: 199 tasks finish in 5 seconds; one task runs for 10 minutes; the entire stage waits for that one task.</p>

<p>Three solutions for skew:</p>
<ul>
  <li><strong>AQE Skew Join Handling (Spark 3.0+, automatic):</strong> AQE detects skewed shuffle partitions by comparing partition sizes to the stage's median partition size. It automatically splits the large (skewed) partition into sub-partitions and replicates the non-skewed side to match. The join runs on the sub-partitions in parallel. No code changes required. Covered in depth in Ch5.</li>
  <li><strong>Salting (manual):</strong> Add a random prefix (0-9) to skewed keys before the join, and replicate the non-skewed side's matching rows with each prefix. The skewed key is now 10 different keys — each goes to a different partition. Cost: the non-skewed side is replicated 10×, increasing memory and network usage.</li>
  <li><strong>Repartition with higher partition count:</strong> More partitions means more tasks, each with a smaller slice. The skewed key still lands in one partition, but that partition is smaller as a fraction of total data. Only works if the skew is across many distinct keys; for a single heavily-skewed key, repartition does not help.</li>
</ul>
</div>

<div class="recall">
<div class="recall-head">Spark Engineer's Checkpoint</div>
<div class="q"><span class="q-n">Q1 </span>Explain why Spark's shuffle writes to disk even though Spark is marketed as an in-memory engine. What is the specific data path at a shuffle boundary?</div>
<div class="q"><span class="q-n">Q2 </span>A Shuffle Hash Join throws OOM. Explain the root cause. Why can't SHJ handle this by spilling to disk the way SMJ can?</div>
<div class="q"><span class="q-n">Q3 </span>You have a 500GB fact table joined to a 8MB dimension table. Spark chooses Sort Merge Join. What configuration change would make it choose Broadcast Hash Join, and what does this change eliminate at the execution plan level?</div>
<div class="q"><span class="q-n">Q4 </span>What does a Bucket Join eliminate and at what cost? Under what conditions does a bucket join fail to eliminate the shuffle?</div>
<div class="q"><span class="q-n">Q5 </span>199 tasks in a stage finish in 4 seconds. One task has been running for 12 minutes. What is the root cause? Will adding more executors fix it? What are the three solutions?</div>
</div>

<div class="box teach"><div class="box-lbl">How to Teach This Chapter</div>
<p><strong>Junior engineer (10 min):</strong> Start with the shuffle myth — ask "Is Spark in-memory?" then walk through the shuffle disk path. Show the three join types with a visual comparison table. End with the skew scenario — draw 199 × 5s + 1 × 12min on a timeline to show why skew destroys parallelism.</p>
<p><strong>Senior engineer (25 min):</strong> Cover SHJ's history (removed in 1.6, back in 2.0) and derive why — hash table cannot spill. Work through a bucket join design: given a table pair joined 100 times per day, calculate the one-time shuffle cost at write vs the saved shuffle cost at read. Cover AQE skew join as a preview of Ch5.</p>
</div>

<div class="topic">
<h2>Data Locality: Scheduler Preferences and the Locality Wait</h2>

<p>Before a task is assigned to an executor, Spark's TaskScheduler ranks candidate executors by data locality — how close the executor is to the data the task needs to read. Spark defines five locality levels in strict preference order:</p>
<ol>
  <li><strong>PROCESS_LOCAL</strong> — Data is in the same JVM process as the executor. The ideal case: an RDD partition is already cached in this executor's memory. No serialization, no network, no disk.</li>
  <li><strong>NODE_LOCAL</strong> — Data is on the same physical node but a different JVM process. Common when an HDFS data block replica is stored on the same machine as the executor but served from the DataNode process, not executor memory. One IPC call; no network transfer.</li>
  <li><strong>NO_PREF</strong> — The data has no locality preference. This level applies to data sources that are uniformly accessible from any node — for example, data read from a JDBC database over a network connection, or data in object storage (S3/GCS) where every executor is equally distant. Spark assigns these tasks to any available executor immediately without waiting.</li>
  <li><strong>RACK_LOCAL</strong> — Data is on a different node but within the same network rack. One network hop through the top-of-rack switch. Better than ANY but worse than NODE_LOCAL.</li>
  <li><strong>ANY</strong> — Data is anywhere in the cluster. Cross-rack network transfer; highest latency.</li>
</ol>

<div class="box n"><div class="box-lbl">spark.locality.wait — Scheduling Trade-off</div>
<p>Spark does not immediately fall back to worse locality levels when better ones are unavailable. It waits up to <code>spark.locality.wait</code> (default: <strong>3 seconds</strong>) for a PROCESS_LOCAL slot to open before trying NODE_LOCAL, then another 3 seconds before RACK_LOCAL, then another 3 seconds before ANY. This waiting can improve performance when a task's preferred executor is momentarily busy — but it introduces latency when preferred executors are persistently overloaded. For shuffle-heavy jobs where data locality is less relevant (shuffle data can be fetched from any executor), setting <code>spark.locality.wait = 0</code> eliminates this wait and lets tasks start immediately. For cache-heavy jobs (e.g., iterative ML reading the same RDD 100 times), keeping locality wait high ensures tasks land near cached partitions.</p>
</div>
</div>

<div class="topic">
<h2>reduceByKey vs groupByKey — Minimize Data Movement Before Shuffle</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>The single most powerful principle in Spark performance: push computation as close to the data source as possible. For aggregations, this means reducing data volume <em>before</em> the shuffle, not after. reduceByKey does this; groupByKey does not.</p>
</div>

<p>In the context of shuffle optimization, the groupByKey vs reduceByKey choice is really about <strong>how much data crosses the network</strong>:</p>

<p><strong>groupByKey shuffle mechanics:</strong> Every raw value for every key is written to shuffle map files and transferred to the reducer over the network. The reducer receives a complete iterator over all values for its keys — only then can it begin aggregating. No work is done on the mapper side to reduce data volume. For a key with 10M values spread across 200 partitions: all 10M values cross the shuffle boundary.</p>

<p><strong>reduceByKey local partial reduction (combiner):</strong> On each mapper partition, reduceByKey applies a local partial reduction: all values with the same key within that partition are combined into a single per-partition aggregate using the provided associative and commutative function. Only this single combined value per key per partition is written to the shuffle file. For 10M values across 200 partitions: at most 200 aggregated values per key cross the network — a potential 50,000× reduction in shuffle data for a highly repeated key.</p>

<div class="box n"><div class="box-lbl">groupByKey vs reduceByKey — Shuffle Data Volume Comparison</div>
<table>
  <thead><tr><th>Property</th><th>groupByKey</th><th>reduceByKey</th></tr></thead>
  <tbody>
    <tr><td>Map-side work</td><td class="rd">None — all raw values pass through</td><td class="g">Local partial reduction per partition</td></tr>
    <tr><td>Shuffle volume (10M values, 200 partitions)</td><td class="rd">10,000,000 values cross the network</td><td class="g">At most 200 values cross the network</td></tr>
    <tr><td>Reducer memory requirement</td><td class="rd">Must hold ALL values for one key in memory simultaneously</td><td class="g">Accumulates one partial result per arriving value — O(1) memory per key</td></tr>
    <tr><td>OOM risk on hot keys</td><td class="rd">High — all values for one key must fit in one executor</td><td class="g">None — partial reduction is constant-size</td></tr>
    <tr><td>Valid use cases</td><td>Need the complete list of values per key</td><td>Any associative aggregation: sum, count, min, max, set union</td></tr>
  </tbody>
</table>
</div>

<p>This is the design principle Vu Trinh frames as "pushing computation close to the data source." The reducer is far from the data (after a shuffle); the mapper is close (operating on local partition data before any network transfer). Every byte eliminated before the shuffle saves disk I/O, network bandwidth, and reducer memory. Always ask: "Can I reduce this key's data volume before it leaves the mapper?" If yes, use reduceByKey, aggregateByKey, or combineByKey over groupByKey.</p>
</div>

<div class="topic">
<h2>Speculative Execution: Handling Slow Tasks</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>If one task in a stage is running much slower than all the others — a "straggler" — Spark can launch a duplicate copy of that task on a different executor. Whichever copy finishes first wins; the other is killed. This is speculative execution: betting that the slowness is caused by a bad executor, not by the task itself.</p>
</div>

<p>Speculative execution addresses straggler tasks — tasks that run significantly longer than the median task in their stage. Stragglers occur due to hardware issues (slow disk, network degradation, memory pressure on one node), GC pauses on one executor, or data skew (one partition has disproportionately more data). The straggler blocks stage completion, holding up all downstream stages.</p>

<p>When enabled (<code>spark.speculation = true</code>), Spark monitors task progress and detects slow tasks whose completion time is more than a configurable multiple of the stage median (default threshold: <code>spark.speculation.multiplier = 1.5</code>). For each such task, Spark launches a <strong>speculative copy</strong> on a different executor. The <em>first copy to complete</em> wins — its output is used for the next stage. The slower copy is killed.</p>

<div class="box f"><div class="box-lbl">Speculative Execution Trade-offs and Risks</div>
<p><strong>Risk — duplicate processing:</strong> Two copies of the same task run simultaneously and may produce side effects twice (e.g., writing duplicate rows to an external database, double-counting an accumulator). Speculative execution is only safe with idempotent operations or when using exactly-once output semantics (Delta Lake, transactional sinks).</p>
<p><strong>Risk — false positive on data skew:</strong> A task is slow because its partition genuinely has more data (skew), not because the executor is bad. The speculative copy runs on a different executor but gets the same skewed partition data — it will also run slowly. You've now doubled the resource consumption without helping. AQE's skew join handling is the correct solution for skew-induced stragglers; speculative execution is the correct solution for executor-induced stragglers.</p>
<p><strong>When to enable:</strong> Speculative execution is off by default. Enable it when jobs have occasional stragglers traced to executor hardware issues, and when output operations are idempotent. Disable when output operations have side effects or when stragglers are consistently the same partition (indicating skew, not hardware).</p>
</div>
</div>

<div class="box gap"><div class="box-lbl">Questions This Chapter Doesn't Answer</div>
<ul>
  <li>How does Spark's shuffle block size interact with the network layer — at what point does shuffle become network-bound rather than disk-bound?</li>
  <li>When does salting break join semantics (e.g., on non-equi joins) and what alternative skew handling applies?</li>
  <li>How does the ExternalShuffleService change fault tolerance behavior when an executor dies mid-shuffle?</li>
</ul>
</div>
</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 4 — PySpark, Tungsten, and Photon
# ─────────────────────────────────────────────────────────────────────────────
CH4 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 4 of 5</div>
  <h1>PySpark, Tungsten, and Photon</h1>
  <div class="ch-src">Source: vutr.substack.com — I spent 6 hours learning PySpark · Why did Databricks build the Photon engine? · A Closer Look Into Databricks's Photon Engine · How is Databricks' Spark different from Open-Source Spark?</div>
  <p class="ch-sum">PySpark's Python-to-JVM bridge is a measurable performance cost — every Python UDF pays a per-row serialization tax. Tungsten cuts JVM object overhead at the binary level. Photon replaces JVM bytecode execution with native C++ for Lakehouse workloads. Together these three layers define the full performance story of modern Spark.</p>
</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>In 2013, 92% of Databricks users wrote Spark in Scala. By 2020, 47% used Python and 41% used SQL — Scala dropped to 12%. Python is now the dominant Spark language. But Spark runs on the JVM. Python is a separate process. Every operation crosses a process boundary with serialization overhead. Understanding where that overhead occurs — and which modern APIs eliminate it — is essential for any PySpark engineer writing production code on large datasets.</p>
</div>

<div class="topic">
<h2>The PySpark Two-Process Architecture</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>When you run a PySpark script, two separate processes start: a Python process (your code) and a JVM process (the actual Spark engine). Your Python code talks to Spark through a library called Py4J that translates Python method calls into Java calls. Most of the time this is fast because you're only sending small amounts of data (file paths, configuration). The problem: Python UDFs send every single row of your data through this bridge, one row at a time.</p>
</div>

<p>PySpark is a wrapper around Apache Spark's JVM implementation. When a PySpark script executes, two processes start simultaneously:</p>
<ul>
  <li><strong>Python process (port 25334 by default):</strong> Your driver code — DataFrame operations, configurations, control flow. This is the Python process you write.</li>
  <li><strong>JVM process (port 25333 by default):</strong> The actual Spark driver running on the JVM — DAGScheduler, TaskScheduler, BlockManager, shuffle management. This is where Spark actually runs.</li>
</ul>

<p>Communication between these two processes uses the <strong>Py4J</strong> library via an Inter-Process Communication (IPC) socket. When your Python code calls <code>df.read.load('data.parquet')</code>, Py4J serializes this call, sends it to the JVM process over the socket, the JVM executes it, and any result is serialized back.</p>

<p>For most DataFrame operations — reading files, applying built-in SQL functions, writing output — the IPC overhead is negligible. You're sending a file path string or a plan description, not data. The JVM handles the actual data processing. The Python code just drives.</p>

<h3>Where the Cost Appears: Python UDFs</h3>

<p>Python UDFs (<code>@udf</code> decorated functions) break the abstraction. When Spark encounters a Python UDF in an execution plan:</p>
<ol>
  <li>For each partition, the JVM executor spawns a <strong>separate Python worker process</strong></li>
  <li>The JVM serializes each row to Python's Pickle format</li>
  <li>The serialized row is sent to the Python process via IPC socket</li>
  <li>Python deserializes the row, executes the UDF function, serializes the result back to Pickle</li>
  <li>The result is sent back to the JVM via IPC socket</li>
  <li>The JVM deserializes the result and continues processing</li>
</ol>

<p>This happens for <strong>every single row</strong>. On a 10M-row DataFrame, that is 10M serialization round-trips. The combined overhead — JVM/Python process switching, Pickle serialization, socket transfer, deserialization — typically makes Python UDFs 10–100× slower than equivalent built-in Spark functions.</p>

<p>Python UDFs also lose two Spark performance features:</p>
<ul>
  <li><strong>No Catalyst optimization:</strong> Catalyst cannot see inside a Python function. No predicate pushdown, no projection pruning, no plan rewriting around the UDF.</li>
  <li><strong>No Tungsten binary encoding:</strong> Tungsten's UnsafeRow format cannot be used — the data must be deserialized to Python objects before the UDF can process it.</li>
</ul>
</div>

<div class="topic">
<h2>Pandas UDFs (Vectorized UDFs) and Arrow Transfer</h2>

<p>Spark 2.3 introduced <strong>Pandas UDFs</strong> (also called vectorized UDFs) as a high-performance alternative to Python UDFs. The key difference: instead of sending one row at a time through the IPC bridge, Pandas UDFs send entire batches of rows using <strong>Apache Arrow</strong>'s columnar format.</p>

<p>Apache Arrow organizes memory in columnar format — all values of column A are stored contiguously, then all values of column B, etc. This is the same layout used by Parquet on disk. The critical property: Arrow is a <strong>zero-copy</strong> serialization format — the JVM and Python processes can share the same Arrow buffer via shared memory without copying, eliminating the most expensive part of the IPC overhead.</p>

<p>The Pandas UDF flow:</p>
<ol>
  <li>A batch of rows (configurable, default ~10,000 rows) is converted to Arrow columnar format in JVM memory</li>
  <li>The Arrow buffer is shared with the Python process (zero-copy transfer via shared memory)</li>
  <li>Python uses PyArrow to access the buffer as a Pandas DataFrame — no deserialization needed</li>
  <li>The Pandas UDF function runs on the entire Pandas DataFrame at once (vectorized)</li>
  <li>The result Pandas DataFrame is converted back to Arrow format and shared back to JVM</li>
</ol>

<p><strong>Spark 3.5+</strong> introduced Arrow-optimized Python UDFs that extend this Arrow-based approach further. A Pandas UDF requires the developer to explicitly declare the function signature as accepting and returning Pandas Series objects — the API itself is different from a regular <code>@udf</code>. Arrow-optimized Python UDFs allow regular <code>@udf</code> decorated functions to receive data in Arrow columnar format at the transfer layer, bypassing Pickle serialization entirely while keeping the familiar row-oriented UDF API. The architectural difference: Pandas UDFs transmit a full Pandas DataFrame per batch (explicit batch API), while Arrow-optimized Python UDFs transmit Arrow record batches but present individual row values to the Python function (transparent Arrow transfer, row-level API). This allows existing <code>@udf</code> code to gain Arrow's batch-transfer efficiency without rewriting function signatures to be batch-aware.</p>

<div class="box n"><div class="box-lbl">Python UDF vs Pandas UDF vs Built-in Function — Performance Hierarchy</div>
<table>
  <thead><tr><th>Type</th><th>Serialization</th><th>Granularity</th><th>Catalyst Optimization</th><th>Relative Speed</th></tr></thead>
  <tbody>
    <tr><td>Built-in SQL function</td><td>None (JVM native)</td><td>Whole column via code gen</td><td class="g">Full</td><td class="g">1× (baseline)</td></tr>
    <tr><td>Pandas UDF (vectorized)</td><td>Arrow columnar (zero-copy)</td><td>Batch of rows</td><td class="y">Partial</td><td class="y">5–20× slower</td></tr>
    <tr><td>Python UDF (@udf)</td><td>Pickle (row-by-row copy)</td><td>One row at a time</td><td class="rd">None</td><td class="rd">50–200× slower</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="topic">
<h2>Spark Connect (Spark 3.4+): Eliminating Py4J</h2>

<p>Spark Connect restructures the PySpark architecture at the protocol level. Instead of Py4J (JVM-to-JVM RPC), Spark Connect uses:</p>
<ul>
  <li><strong>gRPC</strong> as the transport protocol between client and server</li>
  <li><strong>Protocol Buffers</strong> for encoding query plans (language-agnostic, compact binary)</li>
  <li><strong>Apache Arrow record batches</strong> for returning results</li>
</ul>

<p>The Python Spark Connect client requires only Python — no JVM, no Py4J, no local Spark installation. The client converts a DataFrame query to an unresolved logical plan, encodes it in Protobuf, and sends it to the remote Spark Connect Server via gRPC. The server hosts a long-running Spark application, analyzes the plan, optimizes it with Catalyst, executes it on the cluster, and streams results back as Arrow record batches.</p>

<p>Practical benefits: OOM errors in one client session don't affect other clients (isolated sessions); the Spark driver can be upgraded independently of client applications; thin clients (IoT devices, CI/CD jobs, notebooks) can submit Spark jobs without a local JVM.</p>

<p>Limitations: Spark Connect supports only the DataFrame API — RDD API and SparkContext API are not available through the Connect interface. Resource configuration (executor count, memory) is set at server startup, not per-client.</p>
</div>

<div class="topic">
<h2>Project Tungsten: Bypassing JVM Object Overhead</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Every Java object on the heap carries an unavoidable 16-byte "tax" — the object header. A 4-byte string isn't 4 bytes; it's 48+ bytes because of this tax plus the string's internal structure. Tungsten bypasses the JVM entirely: it stores data as raw compact binary at memory addresses it manages directly, the same way C programs manage memory. The garbage collector never touches this data — GC pauses shrink dramatically.</p>
</div>

<h3>The JVM Object Header Problem — Why a 4-byte String Costs 48+ Bytes</h3>

<p>Every Java heap object carries a mandatory <strong>object header</strong> of 16 bytes on a 64-bit JVM:</p>
<ul>
  <li><strong>Mark word (8 bytes):</strong> Encodes the object's identity hash code, GC age, GC mark bits, and lock state. This information is needed for GC tracing, synchronized() locking, and identity comparison. Present on every object regardless of what data it holds.</li>
  <li><strong>Class pointer (8 bytes):</strong> A reference to the object's class metadata (the "klass" word in HotSpot JVM internals) so the JVM knows the object's type. Present on every object.</li>
</ul>

<p>A Java <code>String</code> is not a primitive type — it is a heap object with an internal structure:</p>
<ol>
  <li><strong>String object itself:</strong> 16B header + 4B reference to the backing char[] array + 4B cached hash code + 4B length/coder field = ~28 bytes minimum</li>
  <li><strong>char[] array object</strong> for the actual characters: 16B header + 4B array length field + (N chars × 2 bytes) = 28 bytes for a 4-character string</li>
  <li><strong>Object reference</strong> from the String to its array: 8 bytes on a 64-bit JVM without compressed oops</li>
  <li><strong>Alignment padding:</strong> JVM aligns all objects to 8-byte boundaries, adding up to 7 bytes per object</li>
</ol>
<p>Total for a 4-character string <code>"ABCD"</code>: 28 + 28 + 8 + alignment ≈ <strong>48–64 bytes</strong>. Databricks engineers measured this directly and published it as "a 4-byte string would have over 48 bytes in the JVM object." The same overhead applies to boxed integers: a <code>java.lang.Integer</code> is 16B header + 4B field + 4B padding = <strong>24 bytes</strong> for 4 bytes of actual data.</p>

<p>Project Tungsten addresses this with three components:</p>

<h3>Component 1: Off-Heap Binary Storage via UnsafeRow and <code>sun.misc.Unsafe</code></h3>
<p>The <code>UnsafeRow</code> format stores rows as compact binary data using Java's <code>sun.misc.Unsafe</code> API to perform direct memory access at raw physical addresses — outside the JVM heap entirely. <code>sun.misc.Unsafe</code> exposes C-style pointer arithmetic: you can read and write arbitrary bytes at a memory address without going through the JVM's object model. Tungsten allocates off-heap memory blocks and manages them manually, storing row data with zero object overhead: a 4-byte integer is stored as exactly 4 bytes at a known offset within a row buffer, not as a 24-byte boxed <code>java.lang.Integer</code>.</p>

<p>The critical consequence: <strong>the JVM GC never scans Tungsten's off-heap memory.</strong> GC pause duration scales with the number of live objects on the heap. With Tungsten, the data plane (billions of rows of table data) lives in off-heap memory that the GC is completely unaware of — even if executors hold 128GB of data, GC pause time remains low because the GC heap is nearly empty. Only Spark's own framework objects (schedulers, metadata, user objects) live on the GC heap.</p>

<p>A row of (integer, long, double) takes exactly 4 + 8 + 8 = 20 bytes in UnsafeRow vs potentially 72+ bytes as JVM objects. Variable-width fields (strings) are stored in a separate variable-length section with fixed-width offsets in the main row body, allowing O(1) random access to any field without scanning the entire row.</p>

<h3>Component 2: Cache-Aware Computation</h3>
<p>Data structures are designed around CPU cache line sizes (64 bytes). Sort algorithms that access memory sequentially rather than randomly benefit from hardware prefetching. Hash tables are laid out so that the probe sequence stays within a cache line, reducing cache misses. Columnar layout (all values of column A contiguous, then column B) is fundamentally more cache-friendly than row layout when aggregating a single column — the CPU can prefetch a full cache line of column A values and process 16 integers at once.</p>

<h3>Component 3: Whole-Stage Code Generation via Janino</h3>
<p>Catalyst Phase 4 generates query-specific JVM bytecode at runtime using Scala quasiquotes to construct the AST of a Java class, then compiles it using <strong>Janino</strong> — a lightweight Java compiler embedded in Spark (not the full <code>javac</code>). For a specific query, Catalyst generates a single Java class with a tight <code>processNext()</code> loop that inlines all operators — filter conditions, projection expressions, hash key computation, and aggregation — into a single method body. The JIT compiler receives one large hot method rather than a chain of polymorphic virtual dispatch calls, and can optimize the loop as a unit (loop unrolling, register allocation, constant folding). There is no interpreter overhead: no switch statements routing rows through operator interfaces, no virtual dispatch between filter → project → aggregate. Everything is one inlined loop.</p>

<div class="box n"><div class="box-lbl">HashAggregate Operator: Tungsten in Practice</div>
<p>When Spark executes a <code>GROUP BY</code> with numeric aggregations (SUM, COUNT, AVG on integers/longs), it uses the <code>HashAggregate</code> operator backed by Tungsten's off-heap hash table (UnsafeFixedWidthAggregationMap). Keys and values are stored as UnsafeRow binary data — tight packing, no GC pressure.</p>
<p>When aggregation involves String columns, Tungsten's fixed-width hash table cannot accommodate variable-length mutable values. Spark falls back to <code>SortAggregate</code>, which sorts by key and streams through — slower, more spill. This is why avoiding String-typed groupBy keys (when possible, use integer IDs) improves aggregation performance significantly.</p>
</div>
</div>

<div class="topic">
<h2>Photon: C++ Vectorized Execution for the Lakehouse</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Photon is a C++ query engine that Databricks built inside Databricks Runtime (DBR). It replaces specific JVM physical operators with C++ operators that process data in columnar batches with SIMD-style vectorized operations. It's not a replacement for Spark — it's an enhancement that activates for supported operations and falls back to standard JVM Spark for unsupported ones.</p>
</div>

<h3>Why Databricks Needed Native C++</h3>
<p>Databricks identified five JVM performance ceilings they could not overcome in the existing engine:</p>
<ol>
  <li>Lakehouse workloads stress JVM in-memory performance in ways traditional Spark was not designed for</li>
  <li>Improving JVM performance requires deep JVM internals knowledge to ensure the JIT compiler generates optimal machine code — fragile and unpredictable</li>
  <li>No control over lower-level optimizations: cannot write custom SIMD kernels, cannot control memory layout at the byte level</li>
  <li>GC performance degrades on heaps larger than 64GB — had to manually manage off-heap memory in JVM, adding complexity</li>
  <li>JVM code generation (Tungsten's Janino approach) is constrained by the Java method size limit and JVM code cache size</li>
</ol>

<h3>Vectorized Execution vs Code Generation: Why Photon Chose Interpreted</h3>
<p>Two approaches exist for high-performance OLAP engines:</p>
<ul>
  <li><strong>Code generation</strong> (Spark SQL, Apache Impala): generate specific code for each query at runtime; no virtual function call overhead; but complex to build and debug</li>
  <li><strong>Interpreted vectorized execution</strong> (MonetDB/X100 lineage, DuckDB): process data in column batches; use virtual function dispatch to select operator implementations; benefit from SIMD by amortizing virtual call overhead over large batches</li>
</ul>

<p>Databricks prototyped both for Photon. The code-generated C++ prototype took <strong>two months</strong>. The vectorized (interpreted) C++ prototype took <strong>a couple of weeks</strong>. The vectorized approach also enables native debugging (print statements work; native tools like gdb apply) and allows runtime adaptivity — choosing different code paths based on input data characteristics (nulls present, ASCII-only strings, sparse batches). Databricks chose vectorized.</p>

<h3>Photon's Data Model: Column Vectors and Position Lists</h3>
<p>The fundamental data unit in Photon is a <strong>column vector</strong>: all values of one column for a batch of rows, stored contiguously. A <strong>column batch</strong> is a set of column vectors representing a set of rows. Each column vector also carries a byte vector for NULL information.</p>

<p>Photon's filter implementation is elegant: instead of removing filtered rows from the batch (expensive memory movement), Photon maintains a <strong>position list</strong> — an array of indices of the "active" rows (those not yet filtered out). The filter expression marks positions as inactive in the position list. Downstream operators check the position list and skip inactive rows. No data movement; no copying.</p>

<h3>Photon Benchmarks (from the SIGMOD 2022 paper)</h3>
<div class="box n"><div class="box-lbl">Photon vs Standard DBR Performance</div>
<table>
  <thead><tr><th>Benchmark</th><th>Photon vs DBR</th><th>Primary Cause</th></tr></thead>
  <tbody>
    <tr><td>Hash join (1GB integer tables)</td><td class="g">3.5× faster</td><td>Vectorized hash table; better memory hierarchy utilization</td></tr>
    <tr><td>GroupBy aggregation (string col)</td><td class="g">Up to 5.7× faster</td><td>Columnar batch processing; position list filter</td></tr>
    <tr><td>Parquet write (200M rows)</td><td class="g">2× faster</td><td>Columnar encoding avoids column-to-row pivoting</td></tr>
    <tr><td>JNI overhead (Java→C++ boundary)</td><td class="g">0.06% of execution</td><td>Batched pointer passing — negligible</td></tr>
  </tbody>
</table>
</div>

<h3>Photon Integration: Physical Operators Inside Databricks Runtime — Not a Spark Replacement</h3>

<div class="box f"><div class="box-lbl">Critical Distinction: Photon ≠ Spark Replacement</div>
<p>Photon is <strong>not</strong> a replacement for Apache Spark. It is a set of C++ physical operators that run <em>inside</em> Databricks Runtime (DBR) — the same JVM process, in the same execution environment, within the same Spark query plan framework. Spark's logical planning, Catalyst optimization, DataFrame API, AQE, and cluster management all remain unchanged. Photon replaces only the physical execution operators (scan, filter, project, join, aggregate) for supported operations. When a Photon-unsupported operator appears (e.g., Python UDFs, certain complex aggregations), a transition adapter node converts Photon's columnar batch format back to Spark's internal row format (UnsafeRow) and hands off to the standard JVM Spark operator. The query runs partially in Photon C++ operators and partially in JVM Spark operators — mixed execution within one query plan.</p>
</div>

<p>Photon runs as physical operators inside DBR — the same JVM process, accessed via JNI. The query plan conversion starts at scan nodes; Photon-supported operators are mapped to Photon physical nodes; when an unsupported operator appears, a transition node converts columnar data back to Spark's row format and hands off to JVM Spark. The query can run partially in Photon and partially in standard Spark SQL with no correctness issue — only performance implications.</p>

<div class="box n"><div class="box-lbl">Two Different Boundaries: Python-JVM Process vs JVM-Photon JNI</div>
<table>
  <thead><tr><th>Boundary</th><th>Mechanism</th><th>Overhead Source</th><th>Measured Cost</th></tr></thead>
  <tbody>
    <tr><td>Python UDF → JVM Spark</td><td class="rd">Inter-process: Python process ↔ JVM process via IPC socket (Pickle serialization per row)</td><td class="rd">Process context switch + Pickle serialization + socket transfer — per row</td><td class="rd">50–200× slower than built-in functions; dominant bottleneck</td></tr>
    <tr><td>JVM Spark ↔ Photon (C++)</td><td class="g">Intra-process: JNI call within the same JVM process; passing a pointer to a column batch buffer</td><td class="g">One JNI call per column batch (thousands of rows); pointer arithmetic, no data copying</td><td class="g">0.06% of execution time — negligible</td></tr>
  </tbody>
</table>
<p>The key insight: Python UDF overhead is a <strong>process boundary problem</strong> — two separate OS processes communicating over a socket, with data serialized and deserialized row by row. JNI overhead is an <strong>intra-process function call</strong> — the JVM and C++ code share the same memory space; JNI passes a pointer to a column vector buffer, not a copy of the data. When data is passed as batched column vector pointers rather than row-by-row, the JNI call overhead is amortized over thousands of rows and becomes immeasurably small.</p>
</div>

<p>Photon participates in AQE: its operators implement the required interfaces to export shuffle statistics (e.g., shuffle file sizes) for AQE's runtime re-optimization decisions.</p>
</div>

<div class="recall">
<div class="recall-head">Spark Engineer's Checkpoint</div>
<div class="q"><span class="q-n">Q1 </span>Walk through what happens at the process level when PySpark executes a Python UDF on a 10M-row DataFrame. Name every serialization step and explain why it occurs.</div>
<div class="q"><span class="q-n">Q2 </span>Why are Pandas UDFs faster than Python UDFs? What format do they use for data transfer, and what specific overhead does this format eliminate?</div>
<div class="q"><span class="q-n">Q3 </span>A Java integer stored as a boxed object takes how many bytes in JVM heap? What does Project Tungsten's UnsafeRow format store it as, and how does this affect GC behavior?</div>
<div class="q"><span class="q-n">Q4 </span>Why did Databricks choose interpreted (vectorized) execution for Photon rather than code generation? What was the practical timeline difference in the prototype phase?</div>
<div class="q"><span class="q-n">Q5 </span>Photon's JNI overhead is 0.06%. Why is it so low when JNI overhead is usually cited as a performance concern? What is Photon doing differently from row-by-row JNI calls?</div>
</div>

<div class="box teach"><div class="box-lbl">How to Teach This Chapter</div>
<p><strong>Junior engineer (10 min):</strong> Draw the two-process model — Python box, JVM box, socket between them. Ask: "When you call df.count(), which box does the counting happen in?" (JVM.) "When you call a Python UDF, which box executes your function?" (Python.) "What crosses the socket?" (Every single row.) Then show the performance table — built-in vs Pandas UDF vs Python UDF.</p>
<p><strong>Senior engineer (25 min):</strong> Work through Tungsten's UnsafeRow: calculate the exact byte savings for a row of (int, long, String). Cover Photon's position list filter approach — ask them to compare it to a naive filter that copies non-filtered rows. Close with: "Databricks cannot replace Spark. So how did they build a 3.5× faster engine inside it?"</p>
</div>

<div class="box gap"><div class="box-lbl">Questions This Chapter Doesn't Answer</div>
<ul>
  <li>At what dataset size does the Pandas UDF Arrow batch overhead become negligible vs the per-row cost of Python UDFs — is there a crossover point where Python UDFs are better?</li>
  <li>How does Spark Connect change the executor-side execution (does the Python process at executor level still exist for UDFs)?</li>
  <li>What operations does Photon not yet support, and when does the column-to-row transition node introduce measurable overhead?</li>
</ul>
</div>
</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 5 — Spark Structured Streaming and AQE
# ─────────────────────────────────────────────────────────────────────────────
CH5 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 5 of 5</div>
  <h1>Spark Structured Streaming and AQE</h1>
  <div class="ch-src">Source: vutr.substack.com — If you're learning Apache Spark, this article is for you · A small hands-on project to 2× your Apache Spark learning process</div>
  <p class="ch-sum">Structured Streaming extends the same DataFrame API to continuous data streams by treating them as unbounded tables processed in micro-batches. Adaptive Query Execution closes the loop on the Catalyst Optimizer by re-planning queries at runtime using actual statistics from completed shuffle stages — fixing the three most expensive problems Catalyst gets wrong at plan time.</p>
</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>Batch Spark processes data in minutes to hours. Fraud detection, real-time dashboards, and operational alerts require sub-minute latency. Structured Streaming delivers this without a different programming model — it's the same DataFrame API applied to streams. AQE matters because Catalyst's static optimizer operates on estimates, not facts: it guesses table sizes and partition distributions before execution. AQE corrects those guesses at runtime, automatically coalescing tiny shuffle partitions, switching join strategies based on actual data sizes, and handling skewed joins without manual salting. Understanding both systems completes the Spark engineer's toolkit.</p>
</div>

<div class="topic">
<h2>Structured Streaming: Treating Streams as Bounded Data</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Instead of thinking about a stream as an infinite river of events, Structured Streaming treats it as a very large table that keeps getting new rows appended to it. Every N seconds, Spark takes the new rows that arrived since last time, processes them as a batch (a "micro-batch"), and writes results. You write the same DataFrame query you'd write for batch data — Spark handles the continuous execution loop.</p>
</div>

<p>Vu Trinh's verbatim definition of Structured Streaming's core design principle: <em>"Structured Streaming is a stream processing engine built on the Spark SQL engine. Its core design principle is to treat a continuous stream as a subset of bounded data."</em></p>

<p>This design choice has a profound implication: every optimization, API, and operator that works in batch Spark also works in Structured Streaming. There is no separate streaming API to learn. The Catalyst Optimizer applies to streaming queries. AQE applies within each micro-batch. The join strategies from Ch3 all apply.</p>

<h3>Micro-Batch Processing</h3>
<p>The default execution model: Spark continuously checks the input source (Kafka, S3, files, Delta table) for new data. When new data arrives, it collects it into a micro-batch and processes it as a standard Spark SQL query. The output is written. The next cycle begins.</p>
<p><strong>Latency trade-off:</strong> Micro-batch latency is bounded by the batch interval — typically 1 second to several minutes. This is sufficient for most streaming use cases. For sub-millisecond requirements, Continuous Processing mode (Spark 2.3+) is available but with limited operation support.</p>

<h3>Trigger Types</h3>
<div class="box n"><div class="box-lbl">Structured Streaming Triggers</div>
<table>
  <thead><tr><th>Trigger Type</th><th>Behavior</th><th>Use Case</th></tr></thead>
  <tbody>
    <tr><td>Default (unspecified)</td><td>Process as fast as possible — next batch starts immediately after previous completes</td><td>Maximum throughput, latency = processing time</td></tr>
    <tr><td>Fixed interval (e.g., 1 minute)</td><td>Process every N minutes regardless of data availability; skips if previous batch still running</td><td>Time-aligned reporting; predictable schedules</td></tr>
    <tr><td>One-time (deprecated, Spark 3.3)</td><td>Process all available data in a single micro-batch, then stop</td><td>Replaced by available-now; see note below</td></tr>
    <tr><td>Available-now (Spark 3.3+)</td><td>Process all currently available data in <em>multiple</em> batches (up to maxFilesPerTrigger at a time), then stop</td><td>Replaces one-time; safe for large backlogs; incremental batch processing</td></tr>
    <tr><td>Continuous processing (Spark 2.3+)</td><td>Sub-millisecond latency; limited operations; at-least-once semantics</td><td>Ultra-low latency with reduced guarantees</td></tr>
  </tbody>
</table>
</div>

<div class="box f"><div class="box-lbl">Why One-Time Trigger Was Deprecated — The Single-Batch OOM Risk</div>
<p>The <code>Trigger.Once()</code> trigger processes <em>all</em> currently available data in a <strong>single micro-batch</strong> before stopping. If the stream has been offline for hours or days and a large backlog has accumulated — say, 500 GB of unprocessed data — the single-batch approach forces Spark to process the entire 500 GB in one query execution. This creates OOM risk: the entire backlog's shuffle data must be held in executor memory within a single batch, with no opportunity to release resources between batches.</p>
<p><strong>Available-now</strong> (<code>Trigger.AvailableNow()</code>, Spark 3.3+) solves this by spreading the backlog across <em>multiple</em> micro-batches (bounded by <code>maxFilesPerTrigger</code> per batch), still stopping when all available data is consumed. Each micro-batch processes a manageable chunk of data, releases its resources, and begins the next batch. The result: large backlogs are processed safely and incrementally without OOM risk, while still completing automatically when caught up — giving the best of batch and streaming behavior. This is why available-now is the correct replacement for the deprecated one-time trigger.</p>
</div>
</div>

<div class="topic">
<h2>Output Modes: Append, Complete, and Update</h2>

<p>Structured Streaming's output modes define what data is written to the sink on each trigger:</p>

<p><strong>Append mode:</strong> Only newly added rows (rows not present in the previous output) are written. Requires that rows, once output, never change. Works for: simple transformations without aggregations, aggregations with watermarks where the window is closed. Cannot be used for aggregations without watermarks (the aggregation result changes as new data arrives, violating the "never change" constraint).</p>

<p><strong>Complete mode:</strong> The entire result table is written on every trigger. Works only with aggregations — the full aggregated result is rewritten each time. Expensive for large result tables (every trigger writes everything), but correct for aggregations where every row in the output might change as new input arrives.</p>

<p><strong>Update mode:</strong> Only the rows that changed since the last trigger are written. The most efficient mode for aggregations — only changed aggregate values are emitted. Not all sinks support Update mode (requires the sink to handle row-level updates, such as a database or Delta table).</p>

<div class="box n"><div class="box-lbl">Output Mode Compatibility Matrix</div>
<table>
  <thead><tr><th>Query Type</th><th>Append</th><th>Complete</th><th>Update</th></tr></thead>
  <tbody>
    <tr><td>Simple transformations (no aggregation)</td><td class="g">Yes</td><td class="rd">No</td><td class="g">Yes (= Append)</td></tr>
    <tr><td>Aggregations without watermark</td><td class="rd">No</td><td class="g">Yes</td><td class="g">Yes</td></tr>
    <tr><td>Aggregations with watermark</td><td class="g">Yes (windows closed by watermark)</td><td class="g">Yes</td><td class="g">Yes</td></tr>
    <tr><td>Joins (stream-stream)</td><td class="g">Yes</td><td class="rd">No</td><td class="rd">No</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="topic">
<h2>Watermarks: Handling Late-Arriving Events</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Real-world events don't arrive in order. A mobile app event recorded at 10:00 AM might not reach Kafka until 10:15 AM due to network delays or offline buffering. A watermark tells Spark: "Events can arrive up to N minutes late. Wait that long before closing a time window. Events that arrive more than N minutes late will be dropped." Watermarks let Spark bound how much state it must keep in memory.</p>
</div>

<p>Without watermarks, Spark must keep all intermediate state (aggregation results, window data) in memory forever — because a late event from an hour ago could theoretically arrive at any time and change an old window's result. This is unbounded state growth, which eventually causes OOM.</p>

<p>A watermark of 10 minutes means: the current watermark is <code>max(event_time_seen) - 10 minutes</code>. Events with event_time &lt; watermark are considered late and dropped. Windows whose end time is before the watermark are considered complete and their state can be freed from memory.</p>

<p><strong>Watermarks enable Append output mode for aggregations:</strong> Once a window is closed (its end time &lt; watermark), its result can never change (no more late events will be accepted). It's safe to append this result to the output. Without a watermark, Spark cannot guarantee a window's result is final, so Append mode is disallowed for aggregations.</p>

<div class="box f"><div class="box-lbl">Late Event Handling with Watermarks — Concrete Example</div>
<p>Query: <code>df.withWatermark("event_time", "10 minutes").groupBy(window("event_time", "1 hour")).count()</code></p>
<p>Scenario: current max event_time seen = 11:05 AM. Watermark = 11:05 - 10min = 10:55 AM.</p>
<p>An event with event_time = 10:40 AM arrives. Is it accepted? Window [10:00, 11:00] ends at 11:00 AM &gt; watermark 10:55 AM — window is still open. The 10:40 AM event is 25 minutes late but within the 10-minute watermark? No — 10:40 AM &lt; watermark 10:55 AM. <strong>The event is dropped.</strong></p>
<p>An event with event_time = 11:00 AM arrives. 11:00 AM &gt; watermark 10:55 AM. <strong>The event is accepted</strong> and added to the [11:00, 12:00] window.</p>
</div>

<h3>Window Types</h3>
<ul>
  <li><strong>Tumbling windows:</strong> Fixed-size, non-overlapping. <code>window("event_time", "1 hour")</code> — events belong to exactly one window: [0:00–1:00), [1:00–2:00), etc.</li>
  <li><strong>Sliding windows:</strong> Fixed-size, overlapping. <code>window("event_time", "1 hour", "15 minutes")</code> — 1-hour windows starting every 15 minutes. Each event belongs to multiple overlapping windows.</li>
  <li><strong>Session windows (Spark 3.2+):</strong> Variable-length, defined by inactivity gap. A session groups events with gaps smaller than the timeout; a new session starts after the timeout expires.</li>
</ul>
</div>

<div class="topic">
<h2>AQE: Adaptive Query Execution (Spark 3.0, 2020)</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Catalyst picks a query plan before execution starts, based on statistics estimates that may be wrong. AQE lets Spark pause after each shuffle stage, look at the actual data sizes and distributions it just produced, and re-optimize the next stage's plan based on facts instead of estimates. Three specific problems it fixes: too many shuffle partitions, wrong join strategy choice, and data skew in joins.</p>
</div>

<p>Apache Spark 3.0 (released 2020) introduced Adaptive Query Execution (AQE) as a way to extend Catalyst optimization into runtime. The key insight: shuffle stages create a natural pause point. Every exchange (shuffle) operator forces all tasks in the current stage to complete before the next stage can begin. During this pause, the actual shuffle output statistics are available: how many bytes in each partition, how many rows, how the data distributes across partitions. AQE collects these statistics and re-runs the physical planner for the next stage.</p>

<p>The unit of AQE re-optimization is the <strong>query stage</strong>. Each Exchange (shuffle) operator creates a query stage boundary. AQE collects statistics after each query stage completes, then re-optimizes the next query stage's plan before it begins executing.</p>

<h3>AQE Feature 1 — Coalescing Shuffle Partitions</h3>
<p><strong>Problem:</strong> <code>spark.sql.shuffle.partitions = 200</code> by default. For a query producing 10MB of shuffle output, 200 partitions means each partition averages 50KB — hundreds of tiny tasks that spend more time on task scheduling overhead than actual computation.</p>
<p><strong>AQE solution:</strong> After the shuffle stage completes, AQE inspects the actual partition sizes. If most partitions are tiny, AQE coalesces adjacent small partitions into fewer, larger ones before the next stage reads them. A 200-partition shuffle producing 10MB of data might be coalesced by AQE into 5 partitions of 2MB each — 40× fewer tasks, each with meaningful work.</p>
<p><strong>Configuration:</strong> <code>spark.sql.adaptive.coalescePartitions.enabled = true</code> (default in Spark 3.0+). Target partition size: <code>spark.sql.adaptive.advisoryPartitionSizeInBytes</code> (default 64MB).</p>

<h3>AQE Feature 2 — Dynamic Join Strategy Switching</h3>
<p><strong>Problem:</strong> Catalyst chooses a join strategy (SMJ, SHJ, BHJ) based on estimated table sizes from statistics that may be stale, absent, or wrong. A table estimated at 100MB may actually produce only 1MB of shuffle output after filtering. Catalyst chose SMJ (correct for 100MB); AQE at runtime sees 1MB and switches to BHJ.</p>
<p><strong>AQE solution:</strong> After stage 1 (reading and filtering one side of the join) completes, AQE sees the actual shuffle output size. If it's below the broadcast threshold, AQE switches the join strategy from SMJ to BHJ for stage 2 — without re-planning the entire query, just the next stage. This eliminates an unnecessary shuffle of the smaller table.</p>
<p><strong>Why Catalyst can't do this at planning time:</strong> Before execution starts, the 1MB result doesn't exist yet — it's produced by a filter applied at execution time. Catalyst had only the pre-filter table size estimate. AQE has post-filter actual sizes.</p>

<h3>AQE Feature 3 — Skew Join Handling</h3>
<p><strong>Problem:</strong> One shuffle partition is 100× larger than others due to data skew. One task processes 80% of the data; all other tasks finish in 5 seconds; this one task runs for 15 minutes. The stage waits for it.</p>
<p><strong>AQE solution:</strong> AQE detects skewed partitions by comparing each partition's size against the stage's median partition size (with configurable thresholds). For each skewed partition, AQE:</p>
<ol>
  <li>Splits the skewed partition into N sub-partitions (each reads a range of the shuffle files)</li>
  <li>Replicates the corresponding partition from the other join side N times</li>
  <li>Runs N parallel join tasks instead of 1 massive task</li>
</ol>
<p>This is automatic — no salting, no code changes required. <code>spark.sql.adaptive.skewJoin.enabled = true</code> (default in Spark 3.0+). Threshold: <code>spark.sql.adaptive.skewJoin.skewedPartitionFactor</code> (default 5) and <code>spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes</code> (default 256MB).</p>

<div class="box f"><div class="box-lbl">Why BHJ on a Skewed Probe Side Creates a CPU/Memory Hotspot — and Why SMJ with AQE Is Safer</div>
<p>AQE Feature 2 can dynamically switch a join from SMJ to BHJ when the build side is small. This switch is almost always beneficial for uniformly-distributed data — but it can backfire when the <strong>probe side is skewed</strong>.</p>
<p><strong>How BHJ handles skew:</strong> In BHJ, the build table is broadcast as a complete copy to <em>every</em> executor. Then each executor processes its partition of the probe (large) table, looking up each probe row in the local hash table. If the probe side has a skewed key — say, key <code>"category_X"</code> appears in 40% of probe rows — then the executor holding that skewed probe partition must process 40% of all rows. Every matching probe row still triggers a lookup in the broadcast hash table, consuming CPU proportional to the number of hits. The result: one executor is overwhelmed with CPU and memory pressure from the disproportionate probe workload while all other executors finish quickly. This is a <strong>CPU/memory hotspot</strong> caused by probe-side skew, not by the broadcast table itself.</p>
<p><strong>Why SMJ with AQE skew-join handling is safer on skewed data:</strong> SMJ shuffles both sides by join key. A skewed probe partition ends up in one shuffle partition — which AQE then detects as oversized (larger than median × skewedPartitionFactor). AQE's skew-join feature automatically splits this oversized probe partition into multiple sub-partitions and replicates the matching portion of the build side for each sub-partition. The skewed load is spread across multiple parallel tasks. BHJ — once the broadcast is sent — has no mechanism to redistribute a skewed probe partition: the probe is read directly from its source, and a skewed partition just means one executor gets far more work. AQE's dynamic join switching prefers BHJ for smaller build sides, but if you know the probe side is severely skewed, forcing SMJ (via <code>/*+ MERGE */</code> hint) and letting AQE handle skew in the SMJ path is often the safer choice.</p>
</div>

<div class="box n"><div class="box-lbl">AQE's Three Features — Summary</div>
<table>
  <thead><tr><th>Feature</th><th>Problem Fixed</th><th>How It Works</th><th>Manual Alternative</th></tr></thead>
  <tbody>
    <tr><td>Coalesce shuffle partitions</td><td>200 tiny partitions for small data</td><td>After shuffle: merge adjacent small partitions</td><td>Tune spark.sql.shuffle.partitions manually</td></tr>
    <tr><td>Dynamic join switching</td><td>Wrong join strategy from stale estimates</td><td>After stage 1: check actual size, switch to BHJ if small</td><td>Manually broadcast hint; requires knowing sizes in advance</td></tr>
    <tr><td>Skew join handling</td><td>One task processes 80% of data</td><td>After shuffle: split skewed partitions; replicate other side</td><td>Salting (manual key prefix + non-skewed side replication)</td></tr>
  </tbody>
</table>
</div>

<h3>AQE + Structured Streaming</h3>
<p>AQE re-optimization applies within each micro-batch independently. Each micro-batch is a complete Spark SQL query with its own query stages. AQE collects statistics and re-optimizes within each micro-batch. Since micro-batches are short (seconds to minutes), the AQE overhead (collecting stage statistics) is a small fraction of total batch time.</p>
</div>

<div class="recall">
<div class="recall-head">Spark Engineer's Checkpoint</div>
<div class="q"><span class="q-n">Q1 </span>What are AQE's three runtime optimization features? For each one: what problem does Catalyst's static planning cause, what data does AQE collect to fix it, and what action does AQE take?</div>
<div class="q"><span class="q-n">Q2 </span>A Structured Streaming job writes output in Append mode with a 10-minute watermark. An event arrives 15 minutes late. What happens, and why? What output mode would you use if you needed late events included at the cost of rewriting results?</div>
<div class="q"><span class="q-n">Q3 </span>Why does AQE Feature 2 (dynamic join switching) require shuffle statistics that are unavailable to Catalyst at static planning time? What specific information becomes available after stage 1 completes that didn't exist before?</div>
<div class="q"><span class="q-n">Q4 </span>Explain the difference between tumbling and sliding windows in Structured Streaming with a concrete example. If an event belongs to multiple overlapping windows, how does Spark track state for each window?</div>
<div class="q"><span class="q-n">Q5 </span>Without watermarks, why does Structured Streaming's state grow unboundedly? What specifically does a watermark enable that stops state growth? What is the trade-off of setting the watermark too aggressively (too short)?</div>
</div>

<div class="box teach"><div class="box-lbl">How to Teach This Chapter</div>
<p><strong>Junior engineer (10 min):</strong> Start with the micro-batch mental model — draw a Kafka topic as an ever-growing table. Show that a <code>df.groupBy().count()</code> query is identical in batch and streaming. Then explain watermarks with the 10-minute late arrival example — draw a timeline showing which events are accepted and dropped.</p>
<p><strong>Senior engineer (25 min):</strong> Cover all three AQE features with the problem → statistics → solution structure. Then work through a skew scenario: sketch the timing diagram showing 199 tasks at 5s and 1 task at 15min. Show how AQE's skew join handling converts it to 200 × 5s tasks. Close with: "AQE is Catalyst Phase 3 applied at runtime. What would it look like to apply Phase 2 (logical optimization) at runtime as well?"</p>
</div>

<div class="box xr"><div class="box-lbl">Cross-Connections — Completing the Book</div>
<ul>
  <li><strong>Ch1 (Catalyst):</strong> AQE is Catalyst Phase 3 (physical planning) running again after each query stage, with real statistics replacing estimates. The full optimizer pipeline from Ch1 runs on each AQE re-planning.</li>
  <li><strong>Ch2 (Memory):</strong> AQE's coalesced partitions reduce task count → each remaining task gets more of the executor memory pool → fewer spills. AQE's skew join splitting reduces per-task memory pressure → prevents OOM from skewed partitions.</li>
  <li><strong>Ch3 (Joins):</strong> AQE Feature 2 dynamically selects between SMJ and BHJ — the same join strategies from Ch3, now chosen at runtime with real data rather than estimates.</li>
  <li><strong>Ch4 (Photon):</strong> Photon operators participate in AQE by implementing statistics export interfaces. Photon also uses AQE-adjacent features like shuffle/exchange reuse and dynamic file pruning.</li>
</ul>
</div>

<div class="box gap"><div class="box-lbl">Questions This Chapter Doesn't Answer</div>
<ul>
  <li>How does Structured Streaming handle exactly-once semantics end-to-end — from Kafka source to transactional sink?</li>
  <li>What is the performance overhead of watermark state management at scale — how much memory does the watermark state store consume per hour of streaming data?</li>
  <li>Can AQE be extended to re-optimize beyond join strategy and partition count — for example, dynamically pushing predicates to a data source after runtime statistics reveal new filtering opportunities?</li>
</ul>
</div>
</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLY + GENERATION
# ─────────────────────────────────────────────────────────────────────────────
HTML_CONTENT = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>Apache Spark Internals — Vu Trinh</title>
<style>{CSS}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>document.addEventListener('DOMContentLoaded',()=>mermaid.initialize({{startOnLoad:true,theme:'neutral'}}));</script>
</head>
<body>
{COVER}
{CH1}
{CH2}
{CH3}
{CH4}
{CH5}
</body>
</html>"""

os.makedirs('output', exist_ok=True)
with open('output/vutr_spark.html', 'w') as f:
    f.write(HTML_CONTENT)
print('Written: output/vutr_spark.html')

try:
    import subprocess
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    pdf_path = "output/vutr_spark.pdf"
    html_path = "output/vutr_spark.html"
    result = subprocess.run(
        [chrome, "--headless", "--disable-gpu",
         f"--print-to-pdf={pdf_path}",
         "--print-to-pdf-no-header", html_path],
        capture_output=True, text=True
    )
    if "bytes written" in result.stderr or "written to file" in result.stderr:
        size = os.path.getsize(pdf_path)
        print(f"PDF written: {pdf_path} ({size:,} bytes)")
    else:
        print("Chrome output:", result.stderr[-200:])
        print(f"HTML is ready at {html_path} — open in browser and Print → Save as PDF")
except Exception as e:
    print(f"PDF generation error: {e}")
    print(f"HTML is ready at output/vutr_spark.html")
