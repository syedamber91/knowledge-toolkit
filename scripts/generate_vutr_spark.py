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
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Caveat:wght@400;600;700&display=swap');
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

/* Scribble layer — hand-drawn sketches, margin notes, big facts (GRINDE: Non-verbal + Emphasized) */
.sketch{margin:4mm 0 1mm;text-align:center;page-break-inside:avoid}
.sketch svg{max-width:100%;height:auto}
.sketch-cap{font-family:'Caveat',cursive;font-size:12pt;color:#44446a;text-align:center;margin:0 0 4mm;line-height:1.25}
.scribble{font-family:'Caveat',cursive;font-size:13pt;line-height:1.25;color:#7c2d12;background:#fffbeb;border:1.5px solid #f59e0b;border-radius:8px 14px 10px 16px;padding:2.5mm 4mm;margin:2.5mm 6mm 3.5mm;transform:rotate(-0.6deg);page-break-inside:avoid}
.scribble .who{font-size:9.5pt;color:#b45309;display:block;margin-top:0.5mm}
.bigfacts{margin:5mm 0;padding:4mm 5mm;background:#fefce8;border:2px dashed #ca8a04;border-radius:6px;page-break-inside:avoid}
.bigfacts-head{font-family:'Caveat',cursive;font-size:15pt;font-weight:700;color:#92400e;margin-bottom:2mm}
.bigfact{font-family:'Caveat',cursive;font-size:16.5pt;font-weight:600;line-height:1.3;color:#1c1c2e;margin-bottom:1.5mm}
.bigfact .n{color:#dc2626;font-weight:700;margin-right:2mm}
.retrieval-note{font-family:'Caveat',cursive;font-size:12.5pt;color:#166534;text-align:center;margin:1mm 0 3mm}

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

<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <filter id="squig1" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="3" result="n"/>
      <feDisplacementMap in="SourceGraphic" in2="n" scale="2.6"/>
    </filter>
  </defs>
</svg>

<div class="sketch">
<svg viewBox="0 0 700 320" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <ellipse cx="350" cy="150" rx="80" ry="36" fill="#eff6ff" stroke-width="3.4"/>
    <rect x="40"  y="20"  width="184" height="76" rx="12" fill="#f0fdf4"/>
    <rect x="476" y="16"  width="192" height="92" rx="12" fill="#faf5ff"/>
    <rect x="24"  y="212" width="196" height="86" rx="12" fill="#f0f9ff"/>
    <rect x="480" y="210" width="196" height="90" rx="12" fill="#fff1f2"/>
    <path d="M274 128 C232 108, 206 96, 200 96" marker-end="url(#arr)"/>
    <path d="M426 130 C460 110, 484 98, 496 98" marker-end="url(#arr)"/>
    <path d="M284 176 C240 198, 214 208, 198 216" marker-end="url(#arr)"/>
    <path d="M420 174 C458 196, 484 206, 508 214" marker-end="url(#arr)"/>
  </g>
  <text x="350" y="146" text-anchor="middle" font-size="24" font-weight="700" fill="#1c1c2e">RDD</text>
  <text x="350" y="168" text-anchor="middle" font-size="13.5" fill="#44446a">lazy recipe, not a container</text>
  <text x="132" y="46"  text-anchor="middle" font-size="16" font-weight="700" fill="#14532d">WHY RDDs EXIST</text>
  <text x="132" y="66"  text-anchor="middle" font-size="13" fill="#14532d">MapReduce = disk every pass</text>
  <text x="132" y="82"  text-anchor="middle" font-size="13" fill="#14532d">100 iters = 200 disk trips</text>
  <text x="572" y="40"  text-anchor="middle" font-size="16" font-weight="700" fill="#581c87">5 RDD PROPERTIES</text>
  <text x="572" y="60"  text-anchor="middle" font-size="12.5" fill="#581c87">partitions · compute fn</text>
  <text x="572" y="76"  text-anchor="middle" font-size="12.5" fill="#581c87">dependencies · partitioner</text>
  <text x="572" y="92"  text-anchor="middle" font-size="12.5" fill="#581c87">preferred locations</text>
  <text x="122" y="238" text-anchor="middle" font-size="16" font-weight="700" fill="#0c4a6e">NARROW vs WIDE</text>
  <text x="122" y="258" text-anchor="middle" font-size="13" fill="#0c4a6e">1→1 = pipelined, free</text>
  <text x="122" y="274" text-anchor="middle" font-size="13" fill="#0c4a6e">1→N = shuffle, new stage</text>
  <text x="578" y="234" text-anchor="middle" font-size="16" font-weight="700" fill="#881337">CATALYST (4 phases)</text>
  <text x="578" y="254" text-anchor="middle" font-size="12.5" fill="#881337">analyze → logical opt →</text>
  <text x="578" y="270" text-anchor="middle" font-size="12.5" fill="#881337">physical plan → codegen</text>
  <text x="350" y="308" text-anchor="middle" font-size="13.5" fill="#44446a">immutability + laziness = everything downstream follows from these two ideas</text>
</svg>
</div>
<div class="sketch-cap">The whole chapter on one napkin. Diagram: RDD at the hub, with four branches — why RDDs exist (the MapReduce disk problem), the 5 RDD properties, narrow vs wide dependencies, and Catalyst's four optimization phases.</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>Before Spark, iterative machine learning algorithms using MapReduce were extraordinarily expensive. MapReduce writes all intermediate data to disk between the map phase and the reduce phase. A gradient descent algorithm requiring 100 passes over the data means 100 full disk round-trips to HDFS — each pass launching a separate MapReduce job that rewrites everything to disk before the next job can read it. Spark was invented specifically to fix this: it keeps intermediate data in memory across iterations. Understanding <em>how</em> it does this — via RDDs, lineage, and lazy evaluation — is the foundation for every tuning decision you will ever make.</p>
</div>

<div class="topic">
<h2>The Historical Problem: Why MapReduce Failed for Iterative Workloads</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>MapReduce is like doing your homework one step at a time, but after each step you put your work in a filing cabinet, go home, come back, and retrieve it again before the next step. Spark lets you keep your work on the desk across all steps.</p>
</div>

<div class="sketch">
<svg viewBox="0 0 700 190" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.2" stroke-linecap="round">
    <rect x="16" y="26" width="90" height="34" rx="6" fill="#fce7f3"/>
    <rect x="16" y="120" width="90" height="34" rx="6" fill="#fce7f3"/>
  </g>
  <g filter="url(#squig1)" fill="#fff1f2" stroke="#dc2626" stroke-width="2.6">
    <rect x="140" y="20" width="72" height="46" rx="6"/><rect x="248" y="20" width="72" height="46" rx="6"/>
    <rect x="356" y="20" width="72" height="46" rx="6"/><rect x="464" y="20" width="72" height="46" rx="6"/>
    <rect x="572" y="20" width="90" height="46" rx="6"/>
  </g>
  <g filter="url(#squig1)" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round">
    <path d="M110 43 L136 43" marker-end="url(#arr-r)"/><path d="M216 43 L244 43" marker-end="url(#arr-r)"/>
    <path d="M324 43 L352 43" marker-end="url(#arr-r)"/><path d="M432 43 L460 43" marker-end="url(#arr-r)"/>
    <path d="M540 43 L568 43" marker-end="url(#arr-r)"/>
  </g>
  <text x="61"  y="47"  text-anchor="middle" font-size="13" fill="#9d174d">iter 1</text>
  <text x="61"  y="141" text-anchor="middle" font-size="13" fill="#9d174d">iter 2</text>
  <text x="176" y="47" text-anchor="middle" font-size="11" fill="#7f1d1d">HDFS</text>
  <text x="284" y="47" text-anchor="middle" font-size="11" fill="#7f1d1d">HDFS</text>
  <text x="392" y="47" text-anchor="middle" font-size="11" fill="#7f1d1d">HDFS</text>
  <text x="500" y="47" text-anchor="middle" font-size="11" fill="#7f1d1d">HDFS</text>
  <text x="617" y="47" text-anchor="middle" font-size="11" fill="#7f1d1d">…100×</text>
  <text x="340" y="12" text-anchor="middle" font-size="15" fill="#dc2626" font-weight="700">MapReduce: 200 disk round-trips for 100 iterations</text>
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.2" stroke-linecap="round">
    <rect x="16" y="120" width="90" height="34" rx="6" fill="#fce7f3"/>
  </g>
  <g filter="url(#squig1)" fill="#dcfce7" stroke="#16a34a" stroke-width="2.6">
    <rect x="140" y="106" width="522" height="60" rx="10"/>
  </g>
  <path d="M110 137 L136 137" fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arr-g)"/>
  <text x="401" y="132" text-anchor="middle" font-size="16" fill="#14532d" font-weight="700">one load into RAM — all 100 iterations stay here</text>
  <text x="401" y="152" text-anchor="middle" font-size="12.5" fill="#14532d">(RDD lineage means a lost partition just gets recomputed, not re-read from disk)</text>
  <text x="340" y="184" text-anchor="middle" font-size="15" fill="#16a34a" font-weight="700">Spark: 1 disk read, 100 in-memory passes</text>
</svg>
</div>
<div class="sketch-cap">Diagram: MapReduce's iterative loop bounces to HDFS and back on every single pass (100 iterations = 200 disk round-trips), while Spark loads once into memory and keeps all 100 passes there.</div>

<div class="scribble">it's not that MapReduce is "bad" — it's that NOTHING kept your data warm between steps. Spark's whole trick is just: stop putting it back in the filing cabinet. <span class="who">— Alex, margin note</span></div>

<p>Google introduced MapReduce in 2004 as a paradigm for distributing data processing across hundreds of machines. The model is clean: a <strong>Map</strong> function processes records and emits key-value pairs; a <strong>Shuffle</strong> redistributes all pairs by key across the network; a <strong>Reduce</strong> function aggregates pairs sharing the same key. Disk writes buffer every phase boundary.</p>

<p>For a single-pass ETL job (Extract, Transform, Load — a single sweep through data that reads it once, transforms it, and writes the result) this is fine. For iterative workloads — any machine learning algorithm that makes multiple passes over data — it is catastrophic. Gradient descent (an algorithm that repeatedly adjusts model parameters to minimise prediction error, requiring many passes over the same data) on a neural network requires 10–100 passes. With MapReduce, each pass must be written as a separate job and launched individually on the cluster. The output of pass N is written to HDFS (Hadoop Distributed File System — a fault-tolerant storage layer that spreads large files across many machines' disks); pass N+1 reads it back from HDFS. This means 100 full disk round-trips for 100 gradient descent iterations.</p>

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
  <li><strong>List of Partitions:</strong> The RDD is divided into partitions — the primary unit of parallelism. Each partition is a logical chunk of data processed by one task on one executor (an executor is a JVM process Spark launches on a worker node to run tasks and store cached data). More partitions = more parallelism (up to available cores).</li>
  <li><strong>Compute Function per Partition:</strong> A function that, given a partition of the parent RDD and an iterator over its records, produces the output records for the corresponding partition of this RDD.</li>
  <li><strong>List of Dependencies:</strong> Each RDD records which parent RDDs it depends on and whether those dependencies are narrow or wide. This is the lineage graph — a chain of parent-to-child RDD relationships, like a family tree where each RDD knows exactly which parent it came from and how it was produced.</li>
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

<p>RDDs are immutable. This is not a design preference borrowed from functional programming aesthetics — it is a structural guarantee that makes lineage-based fault recovery possible. A distributed systems necessity driven by four concrete requirements:</p>

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

<p><strong>Transformations</strong> define how data should be transformed but do not execute immediately. They are lazy — calling <code>map()</code>, <code>filter()</code>, or <code>groupByKey()</code> on an RDD does not compute anything. Instead, Spark records the operation as a node in the DAG (Directed Acyclic Graph — a one-way chain of computation steps where data flows forward only; no step can loop back to an earlier step) and returns a new RDD object representing the future result. The original RDD is not modified (immutability).</p>

<p>Common transformations: <code>map</code>, <code>filter</code>, <code>flatMap</code>, <code>groupByKey</code>, <code>reduceByKey</code>, <code>join</code>, <code>repartition</code>, <code>coalesce</code>, <code>sortBy</code>.</p>

<p><strong>Actions</strong> trigger DAG execution. When an action is called, Spark submits the accumulated DAG to the DAGScheduler, which compiles it into stages and tasks, submits TaskSets to the TaskScheduler, and the cluster begins executing.</p>

<p>Common actions: <code>collect()</code>, <code>count()</code>, <code>take(n)</code>, <code>first()</code>, <code>saveAsTextFile()</code>, <code>write()</code>, <code>show()</code>.</p>

<p><strong>Why laziness matters for optimization:</strong> By accumulating the full transformation pipeline before executing, Spark's optimizer can inspect the entire DAG and apply optimizations impossible in eager execution. Predicate pushdown (skipping rows before loading all data — explained in the Catalyst section below), projection pruning (reading only needed columns), and stage fusion (combining narrow transformations into one pass) all require visibility into the full pipeline.</p>

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

<p><strong>Narrow dependency:</strong> Each partition in the child RDD depends on at most one partition in the parent RDD. The compute function for a child partition needs data from exactly one parent partition — no data from other partitions is required. Examples: <code>map</code>, <code>filter</code>, <code>flatMap</code>, <code>coalesce</code> (merging partitions down to a smaller count without shuffling). Narrow transformations can be <em>pipelined</em> — Spark chains them into a single stage, processing records through all narrow transformations in one pass without writing intermediate results to disk.</p>

<p><strong>Wide dependency:</strong> A single partition of a parent RDD contributes to multiple partitions of the child RDD. The compute function for a child partition requires data from <em>multiple</em> parent partitions. Examples: <code>groupByKey</code>, <code>reduceByKey</code>, <code>join</code>, <code>repartition</code>, <code>sort</code>. Wide dependencies create stage boundaries — Spark must complete the parent stage entirely (writing shuffle files to disk) before the child stage can begin reading them.</p>

<div class="sketch">
<svg viewBox="0 0 700 220" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.2" stroke-linecap="round">
    <rect x="10"  y="14" width="330" height="196" rx="12" fill="#f8f8fc"/>
    <rect x="358" y="14" width="332" height="196" rx="12" fill="#f8f8fc"/>
  </g>
  <g fill="#dbeafe" stroke="#1e3a8a" stroke-width="2">
    <rect x="50"  y="52" width="42" height="30" rx="4"/><rect x="102" y="52" width="42" height="30" rx="4"/>
    <rect x="154" y="52" width="42" height="30" rx="4"/>
  </g>
  <g fill="#dcfce7" stroke="#16a34a" stroke-width="2">
    <rect x="50"  y="130" width="42" height="30" rx="4"/><rect x="102" y="130" width="42" height="30" rx="4"/>
    <rect x="154" y="130" width="42" height="30" rx="4"/>
  </g>
  <g stroke="#16a34a" stroke-width="2.4" fill="none">
    <path d="M71 82 L71 130" marker-end="url(#arr-g)"/><path d="M123 82 L123 130" marker-end="url(#arr-g)"/>
    <path d="M175 82 L175 130" marker-end="url(#arr-g)"/>
  </g>
  <text x="175" y="40" text-anchor="middle" font-size="16" font-weight="700" fill="#1c1c2e">NARROW</text>
  <text x="175" y="188" text-anchor="middle" font-size="13.5" fill="#14532d">1 parent → 1 child</text>
  <text x="175" y="204" text-anchor="middle" font-size="13" fill="#16a34a" font-weight="700">pipelined — no stage break, free</text>
  <g fill="#dbeafe" stroke="#1e3a8a" stroke-width="2">
    <rect x="400" y="52" width="42" height="30" rx="4"/><rect x="452" y="52" width="42" height="30" rx="4"/>
    <rect x="504" y="52" width="42" height="30" rx="4"/>
  </g>
  <g fill="#fecaca" stroke="#dc2626" stroke-width="2">
    <rect x="400" y="130" width="42" height="30" rx="4"/><rect x="452" y="130" width="42" height="30" rx="4"/>
    <rect x="504" y="130" width="42" height="30" rx="4"/>
  </g>
  <g stroke="#dc2626" stroke-width="2" fill="none" stroke-dasharray="5 4">
    <path d="M421 82 L421 130 M421 82 L473 130 M421 82 L525 130" marker-end="url(#arr-r)"/>
    <path d="M473 82 L421 130 M473 82 L473 130 M473 82 L525 130" marker-end="url(#arr-r)"/>
    <path d="M525 82 L421 130 M525 82 L473 130 M525 82 L525 130" marker-end="url(#arr-r)"/>
  </g>
  <text x="470" y="40" text-anchor="middle" font-size="16" font-weight="700" fill="#1c1c2e">WIDE</text>
  <text x="470" y="188" text-anchor="middle" font-size="13.5" fill="#881337">1 parent → N children</text>
  <text x="470" y="204" text-anchor="middle" font-size="13" fill="#dc2626" font-weight="700">SHUFFLE — new stage, disk + net</text>
</svg>
</div>
<div class="sketch-cap">Diagram: narrow dependencies (map, filter) draw one clean line per partition and pipeline for free; wide dependencies (groupByKey, join) tangle every parent partition into every child partition — that tangle IS the shuffle.</div>

<div class="scribble">so a "stage boundary" isn't some abstract Spark concept — it's just the point where the arrows stop being 1-to-1 and start being everyone-to-everyone. <span class="who">— Alex, margin note</span></div>

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
  <li><strong>PROCESS_LOCAL</strong> — data in the same JVM (Java Virtual Machine — the runtime process Spark executes inside) as the executor (ideal; RDD in same executor's cache)</li>
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

<div class="sketch">
<svg viewBox="0 0 700 160" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.2" stroke-linecap="round">
    <rect x="10"  y="30" width="150" height="86" rx="10" fill="#eff6ff"/>
    <rect x="188" y="30" width="150" height="86" rx="10" fill="#f0fdf4"/>
    <rect x="366" y="30" width="150" height="86" rx="10" fill="#faf5ff"/>
    <rect x="544" y="30" width="150" height="86" rx="10" fill="#fff7ed"/>
    <path d="M164 73 L184 73" marker-end="url(#arr)"/>
    <path d="M342 73 L362 73" marker-end="url(#arr)"/>
    <path d="M520 73 L540 73" marker-end="url(#arr)"/>
  </g>
  <text x="85"  y="18" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">1. ANALYSIS</text>
  <text x="85"  y="60" text-anchor="middle" font-size="12.5" fill="#1e3a8a">resolve column names</text>
  <text x="85"  y="76" text-anchor="middle" font-size="12.5" fill="#1e3a8a">against the catalog</text>
  <text x="85"  y="98" text-anchor="middle" font-size="11.5" fill="#666680">"column not found" here</text>
  <text x="263" y="18" text-anchor="middle" font-size="15" font-weight="700" fill="#14532d">2. LOGICAL OPT</text>
  <text x="263" y="60" text-anchor="middle" font-size="12.5" fill="#14532d">predicate pushdown</text>
  <text x="263" y="76" text-anchor="middle" font-size="12.5" fill="#14532d">projection pruning</text>
  <text x="263" y="98" text-anchor="middle" font-size="11.5" fill="#666680">pure logic, no physical yet</text>
  <text x="441" y="18" text-anchor="middle" font-size="15" font-weight="700" fill="#581c87">3. PHYSICAL PLAN</text>
  <text x="441" y="60" text-anchor="middle" font-size="12.5" fill="#581c87">picks BHJ/SMJ/SHJ</text>
  <text x="441" y="76" text-anchor="middle" font-size="12.5" fill="#581c87">using cost estimates</text>
  <text x="441" y="98" text-anchor="middle" font-size="11.5" fill="#666680">Ch3! · AQE redoes this (Ch5)</text>
  <text x="619" y="18" text-anchor="middle" font-size="15" font-weight="700" fill="#9a3412">4. CODEGEN</text>
  <text x="619" y="60" text-anchor="middle" font-size="12.5" fill="#9a3412">Janino compiles a</text>
  <text x="619" y="76" text-anchor="middle" font-size="12.5" fill="#9a3412">single tight JVM loop</text>
  <text x="619" y="98" text-anchor="middle" font-size="11.5" fill="#666680">Tungsten runs it (Ch4)</text>
  <text x="350" y="140" text-anchor="middle" font-size="13.5" fill="#44446a">always in THIS order — never skipped, never reordered</text>
</svg>
</div>
<div class="sketch-cap">Diagram: Catalyst's four phases as a left-to-right pipeline — analysis validates, logical optimization rewrites, physical planning picks a join strategy, code generation compiles the final JVM loop.</div>

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

<p><strong>Phase 1 — Analysis:</strong> Resolves the query against the Catalog (Spark's internal metadata registry that stores table names, column names, data types, and statistics for all registered datasets). Column names are validated against the schema, ambiguous references are resolved, types are checked for compatibility. If you reference a column that doesn't exist, the error surfaces here.</p>

<p><strong>Phase 2 — Logical Optimization:</strong> Rule-based transformations applied to the logical plan. No physical decisions yet — pure logical equivalence transformations:</p>
<ul>
  <li><strong>Predicate pushdown:</strong> Move filter operations as close to the data source as possible. A <code>WHERE year = 2024</code> filter pushed to the Parquet file scan means the data source skips non-matching rows at read time — fewer bytes ever enter Spark's memory. Without pushdown, Spark would read all 500M rows into memory and then filter; with pushdown, only matching rows are loaded.</li>
  <li><strong>Projection pruning:</strong> Drop unused columns as early as possible. If your query only needs 3 of 50 columns, Catalyst eliminates the other 47 from the scan — reducing I/O and memory consumption significantly.</li>
  <li><strong>Constant folding:</strong> Pre-compute constant expressions at planning time. <code>WHERE amount > 10 * 100</code> becomes <code>WHERE amount > 1000</code>.</li>
  <li><strong>Null propagation:</strong> Eliminate branches that cannot produce non-null results.</li>
</ul>

<p><strong>Phase 3 — Physical Planning:</strong> Generates <em>multiple</em> candidate physical plans and selects the best via a cost-based model.

<div class="box n"><div class="box-lbl">Join Strategy Quick Reference — BHJ / SMJ / SHJ</div>
<table>
  <thead><tr><th>Strategy</th><th>Use When</th><th>Key Risk</th></tr></thead>
  <tbody>
    <tr><td><strong>Broadcast Hash Join (BHJ)</strong></td><td>Either table &lt; 10 MB (autoBroadcastJoinThreshold)</td><td>OOM if broadcast table × num executors exceeds cluster Storage memory</td></tr>
    <tr><td><strong>Sort Merge Join (SMJ)</strong></td><td>Default for large-large joins — both tables exceed broadcast threshold</td><td>Slower (two full shuffles + sort) but always safe — can spill to disk</td></tr>
    <tr><td><strong>Shuffle Hash Join (SHJ)</strong></td><td>Build side confirmed to fit in executor Execution memory per partition</td><td>OOM if build partition is skewed — cannot spill, no recovery path</td></tr>
  </tbody>
</table>
</div> The cost model uses statistics collected by <code>ANALYZE TABLE</code> or inferred at runtime: estimated row counts, column cardinality, and min/max values. Catalyst scores each candidate plan using these statistics — for example, it computes the estimated cost of shuffling table A vs broadcasting table B, and chooses the lower-cost option. The most important physical planning decision is <strong>join strategy selection</strong> — Catalyst chooses between Broadcast Hash Join (BHJ), Sort Merge Join (SMJ), and Shuffle Hash Join (SHJ) based on estimated table sizes and the cost model. When statistics are absent or stale, the cost model may select a suboptimal plan; AQE (Ch5) corrects these mistakes at runtime with actual statistics.</p>

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
<p><strong>The three costs of UDF opacity:</strong> (1) No predicate pushdown past the UDF — filters after the UDF cannot be moved before it, so more data is processed; (2) No projection pruning through the UDF — all columns must be available even if the UDF only reads two of them; (3) No Tungsten binary encoding (Tungsten is Spark's off-heap binary memory format that stores data without JVM object overhead — covered in Ch4) — data must be deserialized from UnsafeRow to Python objects before the UDF executes, then re-serialized back. Every row crosses the JVM/Python process boundary with Pickle serialization.</p>
<p><strong>The fix: rewrite UDF logic using native <code>pyspark.sql.functions</code>.</strong> Every built-in function in <code>pyspark.sql.functions</code> — <code>when()</code>, <code>coalesce()</code>, <code>regexp_replace()</code>, <code>to_date()</code>, <code>substring()</code>, <code>concat()</code>, etc. — is a first-class Catalyst expression node. Replacing a Python UDF with equivalent built-in function combinations makes the logic fully transparent to Catalyst: predicate pushdown works, projection pruning works, Tungsten encoding works, and no JVM/Python process boundary is crossed. For complex logic not expressible with built-ins, use a Pandas UDF (vectorized, Arrow-based batch transfer) as the next-best option — it still lacks Catalyst transparency but eliminates the per-row serialization cost.</p>
</div>

<div class="scribble">a Python UDF isn't just "slow" — it's INVISIBLE to Catalyst. The optimizer can't push a filter through a box it can't see inside. Black box in, zero optimization out. <span class="who">— Alex, margin note</span></div>

<div class="box l"><div class="box-lbl">Cross-Connections from This Chapter</div>
<ul>
  <li><strong>Ch3 (Join Strategy):</strong> Catalyst Phase 3 selects BHJ vs SMJ vs SHJ based on table size estimates. Understanding those join strategies requires first understanding how Catalyst makes the choice.</li>
  <li><strong>Ch5 (AQE):</strong> Adaptive Query Execution extends Catalyst Phase 3 into runtime — after each shuffle stage completes, AQE re-runs physical planning with actual statistics rather than estimates. AQE is Catalyst's Phase 3 applied dynamically.</li>
  <li><strong>Ch4 (Code Generation):</strong> Catalyst Phase 4 generates the JVM bytecode that Tungsten executes. Photon replaces this JVM bytecode with native C++ for Lakehouse workloads.</li>
</ul>
</div>
</div>

<div class="bigfacts">
<div class="bigfacts-head">If you forget everything else in this chapter, keep these three:</div>
<div class="bigfact"><span class="n">1.</span>An RDD is a lazy recipe, not a dataset — nothing runs until an action fires.</div>
<div class="bigfact"><span class="n">2.</span>Narrow deps pipeline for free. Wide deps = shuffle = new stage.</div>
<div class="bigfact"><span class="n">3.</span>Catalyst always runs Analysis → Logical Opt → Physical Plan → Codegen, in that order.</div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#666680" stroke-width="2.4" stroke-linecap="round">
    <ellipse cx="350" cy="150" rx="78" ry="34" fill="#f8f8fc" stroke="#1c1c2e" stroke-width="3"/>
    <rect x="44"  y="24"  width="176" height="72" rx="12" fill="#fff"/>
    <rect x="480" y="20"  width="184" height="88" rx="12" fill="#fff"/>
    <rect x="30"  y="206" width="188" height="80" rx="12" fill="#fff"/>
    <rect x="486" y="204" width="178" height="80" rx="12" fill="#fff"/>
    <path d="M274 128 C232 108, 206 96, 200 96" marker-end="url(#arr)"/>
    <path d="M426 130 C460 110, 484 98, 496 98" marker-end="url(#arr)"/>
    <path d="M284 176 C240 198, 214 208, 198 216" marker-end="url(#arr)"/>
    <path d="M420 174 C458 196, 484 206, 508 214" marker-end="url(#arr)"/>
  </g>
  <text x="350" y="146" text-anchor="middle" font-size="22" font-weight="700" fill="#1c1c2e">RDD</text>
  <text x="350" y="168" text-anchor="middle" font-size="14" fill="#666680">a ______, not a ________</text>
  <text x="132" y="46"  text-anchor="middle" font-size="15" font-weight="700" fill="#666680">WHY RDDs EXIST</text>
  <text x="132" y="66"  text-anchor="middle" font-size="14" fill="#666680">________ every pass</text>
  <text x="132" y="82"  text-anchor="middle" font-size="14" fill="#666680">100 iters = ___ disk trips</text>
  <text x="572" y="42"  text-anchor="middle" font-size="15" font-weight="700" fill="#666680">5 RDD PROPERTIES</text>
  <text x="572" y="62"  text-anchor="middle" font-size="13.5" fill="#666680">p_________ · c______ fn</text>
  <text x="572" y="78"  text-anchor="middle" font-size="13.5" fill="#666680">d____________ · partitioner</text>
  <text x="572" y="94"  text-anchor="middle" font-size="13.5" fill="#666680">preferred l_________</text>
  <text x="124" y="234" text-anchor="middle" font-size="15" font-weight="700" fill="#666680">N_____ vs W___</text>
  <text x="124" y="254" text-anchor="middle" font-size="14" fill="#666680">1→1 = _________, free</text>
  <text x="124" y="270" text-anchor="middle" font-size="14" fill="#666680">1→N = _______, new stage</text>
  <text x="575" y="230" text-anchor="middle" font-size="15" font-weight="700" fill="#666680">CATALYST (4 phases)</text>
  <text x="575" y="250" text-anchor="middle" font-size="13.5" fill="#666680">a______ → l_____ opt →</text>
  <text x="575" y="266" text-anchor="middle" font-size="13.5" fill="#666680">p_______ plan → c_____gen</text>
</svg>
</div>
<div class="retrieval-note">✍️ Close the chapter and redraw this map from memory, saying every blank OUT LOUD — then flip back and check. Recall, not recognition.</div>

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

<div class="sketch">
<svg viewBox="0 0 700 320" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <ellipse cx="350" cy="150" rx="82" ry="34" fill="#eff6ff" stroke-width="3.4"/>
    <rect x="30"  y="20"  width="200" height="82" rx="12" fill="#f0fdf4"/>
    <rect x="470" y="16"  width="200" height="98" rx="12" fill="#faf5ff"/>
    <rect x="20"  y="212" width="204" height="84" rx="12" fill="#f0f9ff"/>
    <rect x="476" y="214" width="196" height="82" rx="12" fill="#fff1f2"/>
    <path d="M274 128 C232 108, 206 96, 200 96" marker-end="url(#arr)"/>
    <path d="M426 130 C460 110, 484 98, 496 98" marker-end="url(#arr)"/>
    <path d="M284 176 C240 198, 214 208, 198 216" marker-end="url(#arr)"/>
    <path d="M420 174 C458 196, 484 206, 508 214" marker-end="url(#arr)"/>
  </g>
  <text x="350" y="146" text-anchor="middle" font-size="24" font-weight="700" fill="#1c1c2e">OOM</text>
  <text x="350" y="168" text-anchor="middle" font-size="13.5" fill="#44446a">why the same job passes Mon, fails Thu</text>
  <text x="130" y="42"  text-anchor="middle" font-size="16" font-weight="700" fill="#14532d">3 MEMORY REGIONS</text>
  <text x="130" y="62"  text-anchor="middle" font-size="13" fill="#14532d">reserved (300MB) · user</text>
  <text x="130" y="78"  text-anchor="middle" font-size="13" fill="#14532d">unified (exec + storage)</text>
  <text x="130" y="94"  text-anchor="middle" font-size="12" fill="#16a34a" font-weight="700">soft boundary, not hard!</text>
  <text x="570" y="38"  text-anchor="middle" font-size="16" font-weight="700" fill="#581c87">EVICTION ASYMMETRY</text>
  <text x="570" y="58"  text-anchor="middle" font-size="13" fill="#581c87">exec borrows storage freely</text>
  <text x="570" y="74"  text-anchor="middle" font-size="13" fill="#581c87">storage NEVER reclaims exec</text>
  <text x="570" y="94"  text-anchor="middle" font-size="12" fill="#dc2626" font-weight="700">= cache silently evicted</text>
  <text x="122" y="238" text-anchor="middle" font-size="16" font-weight="700" fill="#0c4a6e">SKEW ≠ SIZE</text>
  <text x="122" y="258" text-anchor="middle" font-size="13" fill="#0c4a6e">doubling memory does NOT</text>
  <text x="122" y="274" text-anchor="middle" font-size="13" fill="#0c4a6e">fix a skewed partition</text>
  <text x="574" y="240" text-anchor="middle" font-size="16" font-weight="700" fill="#881337">TUNGSTEN</text>
  <text x="574" y="260" text-anchor="middle" font-size="13" fill="#881337">off-heap binary, GC never</text>
  <text x="574" y="276" text-anchor="middle" font-size="13" fill="#881337">scans it — 4B stays 4B</text>
  <text x="350" y="312" text-anchor="middle" font-size="13.5" fill="#44446a">scheduling nondeterminism decides WHICH executor gets the hot partition on a given day</text>
</svg>
</div>
<div class="sketch-cap">The whole chapter on one napkin. Diagram: OOM at the hub, with four branches — the 3 memory regions, the eviction asymmetry rule, skew vs raw size, and Tungsten's off-heap trick.</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>OOM errors in Spark feel random. The same job passes on Monday and fails on Thursday. The data volume didn't change. What changed? A different scheduling order put a different partition on the same executor. Or a slightly different data distribution created a skewed partition that needed 80% of executor memory. Vu Trinh captures this precisely: "This is why the same job can pass on Monday and fail on Thursday. It's not the data volume that changed. A different scheduling order, a different outcome." To debug OOMs reliably, you must understand <em>exactly</em> how Spark allocates memory inside an executor and what causes one task to consume far more than its share.</p>
<p>Two failure modes are commonly confused: <strong>insufficient total memory</strong> (adding executor memory fixes it) and <strong>data skew</strong> (adding memory does not fix it — the skewed task still receives the same disproportionate share of data regardless of executor size). Understanding the unified memory model makes the difference between a 10-minute fix and a wasted day.</p>
</div>

<div class="topic">
<h2>The Unified Memory Model (Spark 1.6+)</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Each executor's JVM heap (the total pool of RAM that the Java-based Spark executor is allowed to use) is divided into three zones: a small locked zone Spark keeps for itself (300MB), a zone for your application's own data structures, and a large shared zone that Spark splits between "working memory for computations" and "cache storage." The key insight: the working memory can borrow from cache storage, but cache storage cannot borrow back from working memory once it's been taken.</p>
</div>

<div class="sketch">
<svg viewBox="0 0 700 230" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.4" stroke-linecap="round">
    <rect x="20"  y="40" width="100" height="90" fill="#fecaca" stroke="#dc2626"/>
    <rect x="120" y="40" width="230" height="90" fill="#dbeafe" stroke="#1e3a8a"/>
    <rect x="350" y="40" width="165" height="90" fill="#dcfce7" stroke="#16a34a"/>
    <rect x="515" y="40" width="165" height="90" fill="#fef9c3" stroke="#ca8a04"/>
  </g>
  <path d="M400 40 C420 20, 460 20, 480 40" fill="none" stroke="#16a34a" stroke-width="2.6" marker-end="url(#arr-g)"/>
  <path d="M480 130 C460 150, 420 150, 400 130" fill="none" stroke="#dc2626" stroke-width="2.6" stroke-dasharray="6 5"/>
  <text x="440" y="16" text-anchor="middle" font-size="13" fill="#16a34a" font-weight="700">execution borrows freely →</text>
  <text x="440" y="164" text-anchor="middle" font-size="13" fill="#dc2626" font-weight="700">✕ storage can NEVER take back</text>
  <text x="70"  y="70"  text-anchor="middle" font-size="13" font-weight="700" fill="#7f1d1d">RESERVED</text>
  <text x="70"  y="88"  text-anchor="middle" font-size="12" fill="#7f1d1d">300MB</text>
  <text x="70"  y="104" text-anchor="middle" font-size="11" fill="#7f1d1d">hardcoded</text>
  <text x="235" y="70"  text-anchor="middle" font-size="13" font-weight="700" fill="#1e3a8a">USER MEMORY</text>
  <text x="235" y="88"  text-anchor="middle" font-size="12" fill="#1e3a8a">your own objects</text>
  <text x="235" y="104" text-anchor="middle" font-size="11" fill="#1e3a8a">40% of remaining heap</text>
  <text x="432" y="70"  text-anchor="middle" font-size="14" font-weight="700" fill="#14532d">EXECUTION</text>
  <text x="432" y="90"  text-anchor="middle" font-size="12" fill="#14532d">shuffle, sort, hash tbl</text>
  <text x="432" y="106" text-anchor="middle" font-size="11" fill="#14532d">never evicted mid-task</text>
  <text x="597" y="70"  text-anchor="middle" font-size="14" font-weight="700" fill="#92400e">STORAGE</text>
  <text x="597" y="90"  text-anchor="middle" font-size="12" fill="#92400e">cache(), broadcast</text>
  <text x="597" y="106" text-anchor="middle" font-size="11" fill="#92400e">LRU-evictable</text>
  <text x="350" y="150" text-anchor="middle" font-size="12" fill="#666680">(the last two together = "unified memory" — 60% of remaining heap, soft split)</text>
  <text x="350" y="200" text-anchor="middle" font-size="16" fill="#dc2626" font-weight="700">heavy shuffles can silently evict your ENTIRE cache</text>
  <text x="350" y="220" text-anchor="middle" font-size="13" fill="#44446a">— the next query re-reads from disk and nobody knows why</text>
</svg>
</div>
<div class="sketch-cap">Diagram: the executor heap as four blocks — reserved, user memory, execution, storage. The green arrow shows execution freely taking space from storage; the red dashed arrow shows the reverse never happens.</div>

<div class="scribble">this is a one-way door: execution can walk into storage's room and take the couch, but storage can never walk into execution's room and take it back. <span class="who">— Alex, margin note</span></div>

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

<p><strong>Storage memory</strong> is used for: cached RDD partitions (<code>cache()</code> and <code>persist()</code>), broadcast variables (read-only lookup tables that Spark copies to every executor so tasks don't have to fetch them repeatedly), and accumulator values. Storage memory <strong>can be evicted</strong> using a Least Recently Used (LRU) policy (LRU evicts whichever cached partition was accessed furthest in the past) when execution needs more space.</p>

<div class="box f"><div class="box-lbl">The Eviction Asymmetry — The Most Important Rule in Spark Memory</div>
<p><strong>Execution can borrow from storage freely.</strong> When execution needs more space and storage has free room, execution takes it without restriction. There is no limit on how much execution can consume from storage's initial allocation.</p>
<p><strong>Storage cannot take back from execution.</strong> When storage needs space and execution has borrowed it, storage cannot evict execution memory. The design explicitly prioritizes execution over storage. Storage will instead evict its own cached blocks (LRU) until it falls below the <code>spark.memory.storageFraction</code> threshold.</p>
<p><strong>The practical consequence:</strong> A job that performs heavy shuffles and aggregations (execution-heavy) may push every single cached RDD partition out of memory. If your job pattern is "cache a large table once, then run many queries," heavy computation on those queries can silently evict the cache — and the next query re-reads from disk, negating the entire caching strategy. Design around this asymmetry: if caching is critical, use <code>MEMORY_AND_DISK</code> storage level so evicted partitions spill to disk rather than being lost.</p>
</div>

<h3>Storage Cache Levels</h3>
<p>When you call <code>cache()</code>, Spark always uses <code>MEMORY_AND_DISK</code>. When you call <code>persist(storageLevel)</code>, you choose explicitly:</p>
<ul>
  <li><code>MEMORY_ONLY</code> — deserialized Java objects in heap. Fastest reads; most memory usage; if evicted, the data is <em>recomputed</em> from lineage (not spilled to disk). Use when recomputation is cheap and you want maximum read speed.</li>
  <li><code>MEMORY_AND_DISK</code> — deserialized in memory; if evicted by execution memory, serialized to disk instead of dropped. Use when recomputation is expensive and you want a safety net. What <code>cache()</code> uses.</li>
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
  <li><strong>Executor load is nondeterministic at the moment of task assignment.</strong> At any given instant, different executors have different amounts of free memory — some are processing other task waves, some have more cached data, some ran GC recently. The TaskScheduler assigns tasks to available slots based on current load and data locality (data locality means the scheduler prefers to assign a task to an executor that already has the data stored nearby, to avoid network transfer), not on partition size. There is no mechanism to "match a big partition to a big-memory executor."</li>
  <li><strong>The skewed partition may or may not hit a constrained executor.</strong> On Monday, the oversized partition was assigned to executor E4, which happened to have 3GB free — it processed without OOM. On Thursday, executor E4 was processing another large partition from a concurrent job, leaving only 900MB free — the same oversized partition arrives, and OOM occurs.</li>
</ol>

<div class="box f"><div class="box-lbl">Why "Same Job, Different Day" Is a Scheduling Problem, Not a Data Problem</div>
<p>The data distribution (the skew) is the <em>structural cause</em>, but the scheduling assignment determines whether a given run <em>experiences</em> the OOM. If the skewed partition always lands on the same executor, the job is deterministically succeeding or failing. Because it sometimes passes: the skewed partition is finding enough memory on the randomly-assigned executor. Because it sometimes fails: the executor happens to be under pressure from other concurrent tasks on that run.</p>
<p>This is why the "Monday passes, Thursday fails" pattern points to <strong>data skew</strong> as the root cause — not a transient infrastructure problem. The fix must eliminate the unequal partition sizes — the specific options (repartition, salting, AQE skew handling) are covered in the OOM Root Cause section below. Adding memory raises the threshold but does not change the scheduling nondeterminism: the skewed partition still lands on a random executor, and on a bad day, that executor is still under pressure.</p>
</div>
</div>

<div class="topic">
<h2>Off-Heap Memory and Project Tungsten</h2>

<p>The JVM's garbage collector (GC) is the core performance problem for large-scale Spark jobs. The GC periodically stops all application threads to scan the heap and free memory no longer in use — during this pause, all Spark tasks on that executor are frozen. On heaps larger than 64GB, GC pauses become severe — Databricks engineers observed this directly when building Photon.</p>

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

<div class="scribble">every object pays a "box tax" whether or not it needs the box. Tungsten's whole move is: skip the box, write the bytes straight to the shelf. <span class="who">— Alex, margin note</span></div>
</div>

<p>Project Tungsten is Spark's initiative to bypass JVM object overhead entirely. Tungsten's memory manager operates directly against binary data (the <code>UnsafeRow</code> format) in off-heap memory, bypassing the JVM garbage collector. The key insight: a 4-character string that occupies 48–64 bytes as a JVM heap object is stored as exactly <strong>4 bytes</strong> in Tungsten's binary UnsafeRow format — compact binary without object headers, without the char[] wrapper object, without alignment padding. More importantly, the JVM GC does not scan off-heap memory at all — those 4 bytes are invisible to the GC regardless of how many billions of such strings exist in the executor's Tungsten memory. GC pause time is determined by the number of live objects on the JVM heap; Tungsten removes the entire data plane from the heap, keeping GC overhead low even as data volume grows to hundreds of gigabytes. Three components:</p>
<ol>
  <li><strong>Off-heap memory management via <code>sun.misc.Unsafe</code>:</strong> <code>sun.misc.Unsafe</code> is a special, non-public Java class that allows programs to read and write arbitrary memory addresses directly — bypassing Java's normal safety checks, similar to how C code uses raw pointers. Data stored in compact binary format at raw physical memory addresses, outside the JVM heap entirely. The JVM GC never scans this memory — it is invisible to the garbage collector. This eliminates GC pause pressure for the data plane, which matters most when heaps exceed 32–64 GB where GC pauses become multi-second events. Data is accessed via <code>sun.misc.Unsafe</code> pointer arithmetic — essentially C-style memory management inside the JVM.</li>
  <li><strong>Cache-aware computation:</strong> Data structures are designed around CPU cache line sizes (64 bytes). A CPU cache line is the chunk of memory the CPU loads in one operation — if your data is arranged sequentially, the CPU loads one 64-byte chunk and processes all of it. If data is scattered, the CPU must fetch a new chunk for every read. It's like reading a book straight through vs. finding each sentence on a random page. Spark's columnar layout keeps all values of column A contiguous so the CPU can prefetch and process them efficiently.</li>
  <li><strong>Code generation (Janino compiler):</strong> Catalyst Phase 4 uses Scala quasiquotes to generate a custom Java class at runtime and compiles it to JVM bytecode using the <strong>Janino</strong> compiler. Janino is a lightweight Java compiler embedded inside Spark — unlike <code>javac</code> (the standard Java compiler you'd install on your machine), Janino can compile new code at runtime without requiring a full Java Development Kit on every worker node. For each query, this produces a single tight loop that inlines all filter conditions, projections, and hash computations — no virtual dispatch between operators, no generic interpreter overhead. The JIT compiler can optimize this hot method as a single unit.</li>
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
<p>In a hash join, the <em>build side</em> is the smaller table loaded entirely into a hash table in memory; the <em>probe side</em> is the larger table whose rows are streamed through and looked up in that hash table. SHJ's build phase loads the entire build-side partition into an in-memory hash table. SHJ works in two explicit steps:
<ol>
  <li><strong>Build phase:</strong> Each executor reads its partition of the build (smaller) table and loads all rows into an in-memory hash table — one hash table per executor partition.</li>
  <li><strong>Probe phase:</strong> Rows from the probe (larger) table stream through partition by partition; each row's join key is hashed and looked up in the hash table in O(1).</li>
</ol>
A hash table cannot spill — a partially-resident hash table cannot serve lookups correctly because the lookup key might map to a row that was spilled. If that slot doesn't exist in memory, the lookup either fails or returns a wrong answer.
Spark has no mechanism to bring spilled hash table entries back on demand. Therefore: <strong>if the build-side partition exceeds available Execution memory, SHJ throws OOM with no recourse</strong>. Unlike SMJ, there is no "SHJ with spill" mode. The only options are: reduce the build-side partition size (more shuffle partitions), add executor memory, or switch to SMJ.</p>

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
<div class="sketch">
<svg viewBox="0 0 700 210" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.2" stroke-linecap="round">
    <rect x="40"  y="100" width="140" height="80" fill="#fff"/>
    <rect x="330" y="60"  width="140" height="120" fill="#fff"/>
  </g>
  <g fill="#fecaca" stroke="#dc2626" stroke-width="2.4">
    <rect x="60" y="116" width="100" height="64"/>
  </g>
  <g fill="#fecaca" stroke="#dc2626" stroke-width="2.4">
    <rect x="350" y="76"  width="100" height="104"/>
  </g>
  <path d="M200 140 C240 140, 260 140, 310 130" fill="none" stroke="#666680" stroke-width="2.2" marker-end="url(#arr)"/>
  <text x="255" y="118" text-anchor="middle" font-size="14" fill="#666680">double the</text>
  <text x="255" y="134" text-anchor="middle" font-size="14" fill="#666680">executor...</text>
  <text x="110" y="76"  text-anchor="middle" font-size="15" font-weight="700" fill="#1c1c2e">8GB executor</text>
  <text x="110" y="150" text-anchor="middle" font-size="14" font-weight="700" fill="#7f1d1d">80% skew</text>
  <text x="110" y="166" text-anchor="middle" font-size="13" fill="#7f1d1d">≈3.6GB → OOM</text>
  <text x="400" y="48"  text-anchor="middle" font-size="15" font-weight="700" fill="#1c1c2e">16GB executor</text>
  <text x="400" y="120" text-anchor="middle" font-size="14" font-weight="700" fill="#7f1d1d">STILL 80% skew</text>
  <text x="400" y="140" text-anchor="middle" font-size="13" fill="#7f1d1d">≈7.5GB → STILL OOM</text>
  <text x="400" y="196" text-anchor="middle" font-size="14" fill="#dc2626" font-weight="700">the SHARE never changed, only the number</text>
  <text x="350" y="18" text-anchor="middle" font-size="15" fill="#16a34a" font-weight="700">fix the split, not the size — repartition / salt / AQE</text>
</svg>
</div>
<div class="sketch-cap">Diagram: an 8GB executor with an 80%-skewed partition OOMs at ~3.6GB; doubling it to 16GB just OOMs again at ~7.5GB — the skewed task always consumes the same 80% share, whatever the executor's total size.</div>

<div class="scribble">"just add more memory" is the wrong instinct here — it's like buying a bigger backpack when the problem is that one book weighs as much as all the others combined. <span class="who">— Alex, margin note</span></div>

<p><strong>The correct fix requires breaking the partition.</strong> Options: (1) <strong>Repartition / increase shuffle.partitions</strong> — more partitions means smaller absolute partition sizes, but a single dominant skewed key still concentrates in one partition; (2) <strong>Salting</strong> — artificially split the hot key into N sub-keys so data distributes across N partitions. For example, if 70% of rows have <code>user_id = 'anonymous'</code>, salting adds a random suffix so 'anonymous' becomes 'anonymous_1', 'anonymous_2', ..., 'anonymous_5' — spreading one giant partition into five roughly equal ones; (3) <strong>AQE skew join handling</strong> — detects oversized shuffle partitions at runtime and automatically splits them into sub-partitions without code changes. All three fix the partition size directly. Adding executor memory fixes nothing.</p>
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
  <li><strong>AQE replicates the matching portion of the other join side.</strong> For P3 from table A, AQE identifies the corresponding P3 partition of table B (the portion co-located by join key). Because each of the 10 sub-partitions of A's P3 still needs to join against the same matching rows from table B, Spark creates 10 copies of those B rows — one for each sub-task. The B partition is now read 10 times rather than once — but each read is small, and the 10 resulting joins execute in parallel.</li>
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

<div class="bigfacts">
<div class="bigfacts-head">If you forget everything else in this chapter, keep these three:</div>
<div class="bigfact"><span class="n">1.</span>Execution borrows from Storage freely. Storage can NEVER take it back.</div>
<div class="bigfact"><span class="n">2.</span>Skew ≠ size — doubling executor memory OOMs again at the same 80% share.</div>
<div class="bigfact"><span class="n">3.</span>Off-heap Tungsten data is invisible to the GC — 4 bytes stays 4 bytes.</div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#666680" stroke-width="2.4" stroke-linecap="round">
    <ellipse cx="350" cy="150" rx="80" ry="34" fill="#f8f8fc" stroke="#1c1c2e" stroke-width="3"/>
    <rect x="34"  y="22"  width="196" height="78" rx="12" fill="#fff"/>
    <rect x="474" y="18"  width="196" height="92" rx="12" fill="#fff"/>
    <rect x="24"  y="210" width="200" height="80" rx="12" fill="#fff"/>
    <rect x="480" y="212" width="192" height="78" rx="12" fill="#fff"/>
    <path d="M274 128 C232 108, 206 96, 200 96" marker-end="url(#arr)"/>
    <path d="M426 130 C460 110, 484 98, 496 98" marker-end="url(#arr)"/>
    <path d="M284 176 C240 198, 214 208, 198 216" marker-end="url(#arr)"/>
    <path d="M420 174 C458 196, 484 206, 508 214" marker-end="url(#arr)"/>
  </g>
  <text x="350" y="146" text-anchor="middle" font-size="22" font-weight="700" fill="#1c1c2e">OOM</text>
  <text x="350" y="168" text-anchor="middle" font-size="14" fill="#666680">same job: pass ____, fail ____</text>
  <text x="132" y="44"  text-anchor="middle" font-size="15" font-weight="700" fill="#666680">3 MEMORY REGIONS</text>
  <text x="132" y="64"  text-anchor="middle" font-size="13.5" fill="#666680">r_______ (___MB) · user</text>
  <text x="132" y="80"  text-anchor="middle" font-size="13.5" fill="#666680">u_______ (exec + storage)</text>
  <text x="572" y="40"  text-anchor="middle" font-size="15" font-weight="700" fill="#666680">EVICTION ASYMMETRY</text>
  <text x="572" y="60"  text-anchor="middle" font-size="13.5" fill="#666680">exec b_______ storage freely</text>
  <text x="572" y="76"  text-anchor="middle" font-size="13.5" fill="#666680">storage NEVER _______ exec</text>
  <text x="124" y="236" text-anchor="middle" font-size="15" font-weight="700" fill="#666680">SKEW ≠ SIZE</text>
  <text x="124" y="256" text-anchor="middle" font-size="13.5" fill="#666680">doubling memory does ___</text>
  <text x="124" y="272" text-anchor="middle" font-size="13.5" fill="#666680">fix a ______ partition</text>
  <text x="576" y="238" text-anchor="middle" font-size="15" font-weight="700" fill="#666680">TUNGSTEN</text>
  <text x="576" y="258" text-anchor="middle" font-size="13.5" fill="#666680">_____-heap binary, GC</text>
  <text x="576" y="274" text-anchor="middle" font-size="13.5" fill="#666680">never _____ it</text>
</svg>
</div>
<div class="retrieval-note">✍️ Close the chapter and redraw this map from memory, saying every blank OUT LOUD — then flip back and check. Recall, not recognition.</div>

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

<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <filter id="squig" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="7" result="n"/>
      <feDisplacementMap in="SourceGraphic" in2="n" scale="2.6"/>
    </filter>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L9,5 L0,10 L3,5 z" fill="#1c1c2e"/>
    </marker>
    <marker id="arr-r" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L9,5 L0,10 L3,5 z" fill="#dc2626"/>
    </marker>
    <marker id="arr-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L9,5 L0,10 L3,5 z" fill="#16a34a"/>
    </marker>
  </defs>
</svg>

<div class="sketch">
<svg viewBox="0 0 700 360" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <ellipse cx="350" cy="178" rx="86" ry="38" fill="#eff6ff" stroke-width="3.4"/>
    <rect x="42"  y="34"  width="180" height="74" rx="12" fill="#f0fdf4"/>
    <rect x="472" y="24"  width="198" height="118" rx="12" fill="#faf5ff"/>
    <rect x="30"  y="238" width="200" height="92" rx="12" fill="#f0f9ff"/>
    <rect x="486" y="238" width="184" height="80" rx="12" fill="#fff1f2"/>
    <rect x="258" y="300" width="184" height="52" rx="12" fill="#fff7ed"/>
    <path d="M272 156 C230 140, 200 128, 208 108" marker-end="url(#arr)"/>
    <path d="M430 158 C462 140, 486 128, 496 142" marker-end="url(#arr)"/>
    <path d="M282 202 C240 220, 210 228, 190 238" marker-end="url(#arr)"/>
    <path d="M424 200 C462 218, 490 226, 510 238" marker-end="url(#arr)"/>
    <path d="M350 216 L350 298" marker-end="url(#arr)"/>
  </g>
  <g filter="url(#squig)" fill="none" stroke="#16a34a" stroke-width="2.4" stroke-dasharray="7 5" stroke-linecap="round">
    <path d="M560 142 C560 168, 470 186, 438 182" marker-end="url(#arr-g)"/>
  </g>
  <g filter="url(#squig)" fill="none" stroke="#dc2626" stroke-width="2.4" stroke-dasharray="7 5" stroke-linecap="round">
    <path d="M578 318 C578 342, 470 350, 444 336" marker-end="url(#arr-r)"/>
  </g>
  <text x="350" y="172" text-anchor="middle" font-size="27" font-weight="700" fill="#1c1c2e">SHUFFLE</text>
  <text x="350" y="196" text-anchor="middle" font-size="14" fill="#44446a">disk + network at EVERY stage boundary</text>
  <text x="132" y="58"  text-anchor="middle" font-size="17" font-weight="700" fill="#14532d">WHY DISK?</text>
  <text x="132" y="78"  text-anchor="middle" font-size="13" fill="#14532d">any reducer may need it,</text>
  <text x="132" y="94"  text-anchor="middle" font-size="13" fill="#14532d">must survive task death</text>
  <text x="571" y="48"  text-anchor="middle" font-size="17" font-weight="700" fill="#581c87">3 WAYS TO JOIN</text>
  <text x="571" y="70"  text-anchor="middle" font-size="13.5" fill="#581c87">SMJ — sort both, safe, spills</text>
  <text x="571" y="88"  text-anchor="middle" font-size="13.5" fill="#581c87">SHJ — hash table, fast, OOMs</text>
  <text x="571" y="106" text-anchor="middle" font-size="13.5" fill="#581c87">BHJ — mail small table to all</text>
  <text x="571" y="126" text-anchor="middle" font-size="12.5" font-weight="600" fill="#16a34a">BHJ = zero shuffle!</text>
  <text x="130" y="262" text-anchor="middle" font-size="16" font-weight="700" fill="#0c4a6e">DODGE THE SHUFFLE</text>
  <text x="130" y="282" text-anchor="middle" font-size="13" fill="#0c4a6e">bucket join (pay at write)</text>
  <text x="130" y="298" text-anchor="middle" font-size="13" fill="#0c4a6e">reduceByKey (shrink first)</text>
  <text x="130" y="314" text-anchor="middle" font-size="13" fill="#0c4a6e">broadcast (skip entirely)</text>
  <text x="578" y="264" text-anchor="middle" font-size="16" font-weight="700" fill="#881337">SKEW</text>
  <text x="578" y="284" text-anchor="middle" font-size="13" fill="#881337">1 hot key → 1 giant task</text>
  <text x="578" y="300" text-anchor="middle" font-size="13" fill="#881337">199 done, 1 still running…</text>
  <text x="350" y="322" text-anchor="middle" font-size="15" font-weight="700" fill="#7c2d12">AT SCALE: Uber RSS</text>
  <text x="350" y="340" text-anchor="middle" font-size="12.5" fill="#7c2d12">shuffle gets its own servers</text>
  <text x="497" y="175" font-size="12.5" fill="#16a34a" transform="rotate(-4 497 175)">no Exchange node!</text>
  <text x="470" y="352" font-size="12.5" fill="#dc2626">AQE auto-splits it (Ch5)</text>
</svg>
</div>
<div class="sketch-cap">The whole chapter on one napkin — everything below hangs off this map. Diagram: a hub-and-spoke mind map with SHUFFLE at the center and five grouped branches: why disk, the 3 join strategies, shuffle-dodging tricks, skew, and Uber's RSS at scale.</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>Despite Spark's reputation as an "in-memory" engine, shuffle writes to disk. Every groupBy, join, repartition, and sort crosses a stage boundary where Spark writes shuffle output files to local disk, transfers them over the network to the next stage's executors, and reads them back from disk. This disk + network cost is the dominant bottleneck in most production Spark jobs. The three join strategies — Sort Merge Join, Shuffle Hash Join, and Broadcast Hash Join — exist because different data sizes and distributions call for radically different approaches. Choosing the wrong one silently costs 10× performance or causes OOM. Three threads run through this chapter that are worth holding onto explicitly: <strong>why</strong> shuffle is disk-based at all (the fault-tolerance rationale — a lost reducer is cheap to retry, a lost mapper is not, and Google's Dremel paper showed why coupling compute to shuffle storage doesn't scale), <strong>which</strong> of two similar-looking problems you're actually facing when a task hangs (a skewed key needs data-side fixes; a bad executor needs speculative execution — the fixes are not interchangeable), and <strong>how</strong> the same modular arithmetic that makes bucket joins fast also silently breaks them the moment bucket counts don't match.</p>
</div>

<div class="topic">
<h2>Why Shuffle Writes to Disk (The In-Memory Myth)</h2>

<div class="box f"><div class="box-lbl">The Most Common Spark Misconception</div>
<p>Spark is routinely described as an "in-memory" engine. This is true for narrow transformations within a stage — data flows from one transformation to the next in memory, never touching disk. But at every wide dependency boundary (every shuffle), Spark writes to disk. The data path for a shuffle is: task writes output → <strong>disk</strong> → network transfer → <strong>disk</strong> → next stage task reads. Two disk operations and a network transfer for every stage boundary. Vu Trinh explicitly corrects this misconception: shuffle is disk-based even in Spark.</p>
</div>

<div class="sketch">
<svg viewBox="0 0 700 210" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <rect x="18" y="70" width="118" height="58" rx="10" fill="#eff6ff"/>
    <rect x="564" y="70" width="118" height="58" rx="10" fill="#eff6ff"/>
    <path d="M140 99 L184 99" marker-end="url(#arr)"/>
    <path d="M300 99 C336 84, 366 84, 400 99" stroke-dasharray="8 6" marker-end="url(#arr)"/>
    <path d="M516 99 L560 99" marker-end="url(#arr)"/>
    <path d="M77 66 C160 34, 540 34, 623 66" stroke="#16a34a" stroke-dasharray="7 5" marker-end="url(#arr-g)"/>
  </g>
  <g filter="url(#squig)" fill="#fff1f2" stroke="#dc2626" stroke-width="3">
    <ellipse cx="242" cy="78" rx="52" ry="13"/>
    <path d="M190 78 L190 128 A52 13 0 0 0 294 128 L294 78" fill="#fff1f2"/>
    <ellipse cx="458" cy="78" rx="52" ry="13"/>
    <path d="M406 78 L406 128 A52 13 0 0 0 510 128 L510 78" fill="#fff1f2"/>
  </g>
  <text x="77" y="94" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">Stage N task</text>
  <text x="77" y="114" text-anchor="middle" font-size="12.5" fill="#1e3a8a">(map side)</text>
  <text x="623" y="94" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">Stage N+1 task</text>
  <text x="623" y="114" text-anchor="middle" font-size="12.5" fill="#1e3a8a">(reduce side)</text>
  <text x="242" y="108" text-anchor="middle" font-size="16" font-weight="700" fill="#dc2626">DISK #1</text>
  <text x="242" y="124" text-anchor="middle" font-size="11.5" fill="#881337">shuffle files</text>
  <text x="458" y="108" text-anchor="middle" font-size="16" font-weight="700" fill="#dc2626">DISK #2</text>
  <text x="458" y="124" text-anchor="middle" font-size="11.5" fill="#881337">read back</text>
  <text x="162" y="88" text-anchor="middle" font-size="12.5" fill="#44446a">write</text>
  <text x="350" y="80" text-anchor="middle" font-size="13" fill="#44446a">network</text>
  <text x="538" y="88" text-anchor="middle" font-size="12.5" fill="#44446a">read</text>
  <text x="350" y="18" text-anchor="middle" font-size="14" fill="#16a34a">inside a stage: pure memory, no disk — this is the "in-memory" part</text>
  <text x="350" y="168" text-anchor="middle" font-size="17" font-weight="700" fill="#dc2626">every shuffle = 2 disk hits + 1 network trip</text>
  <text x="350" y="192" text-anchor="middle" font-size="13.5" fill="#44446a">…and stage N+1 can't even START until every stage N task has finished writing</text>
</svg>
</div>
<div class="sketch-cap">Diagram: the shuffle data path. A map task writes to local disk (disk #1), files cross the network, land on disk again (disk #2), and only then does the reduce task read them. A green dashed arc over the top shows the in-memory path that exists only <em>inside</em> a stage.</div>

<div class="scribble">wait — the "in-memory" engine hits disk TWICE on every shuffle?? So "in-memory" only means inside one stage. The stage boundary is where the speed goes to die. <span class="who">— Alex, margin note</span></div>

<p>The shuffle mechanism works as follows. When stage N contains a wide dependency (e.g., a <code>groupByKey</code>), each task in stage N must redistribute its output records by key so that all records with the same key arrive at the same partition in stage N+1. Each task:</p>
<ol>
  <li>Partitions its output records by <code>key.hashCode() % numPartitions</code></li>
  <li>Writes the partitioned records to local disk as <strong>shuffle map output files</strong> (one file per output partition)</li>
  <li>Registers the file locations with the BlockManager (a per-executor service that tracks the location of all data blocks — cached partitions and shuffle files — and serves them to other executors on request)</li>
</ol>
<p>Stage N+1 cannot begin until all tasks in stage N have completed and registered their shuffle files. Then each task in stage N+1 fetches its assigned partition's files from the disk of all stage N executors over the network, reads them from disk, and processes them.</p>

<p>Why disk at the shuffle boundary? Because stage N+1 tasks may need to read data from any stage N task — the data must be durable and accessible from any executor in the cluster. In-memory shuffle would require all stage N outputs to remain in memory until all stage N+1 tasks complete reading them — this would require holding both stages' data in memory simultaneously, defeating the memory model.</p>

<div class="box n"><div class="box-lbl">Fault Tolerance Rationale for Disk-Based Shuffle</div>
<p>Beyond memory constraints, durability of shuffle files on disk provides a critical fault tolerance property: <strong>if a reducer task (stage N+1) fails, it can be restarted and re-read its shuffle input from the map-side disk files without requiring stage N to be recomputed</strong>. The map-side shuffle files persist on disk until the job completes. Only if a <em>map task</em> (stage N) executor dies and the shuffle files it produced are lost must stage N be re-executed. This asymmetry — reducer failures are cheap (just re-read existing shuffle files), mapper failures are expensive (must re-run the map stage) — is why the <code>ExternalShuffleService</code> exists: it decouples shuffle file serving from executor lifecycle so that even if the map-side executor is killed, the shuffle files remain available, making reducer restarts trivially cheap without any stage re-execution.</p>
</div>

<h3>The Quadratic Scaling Problem (from BigQuery's Dremel paper)</h3>
<p>Google's Dremel paper (cited by Vu) identified that traditional MapReduce shuffle has quadratic scaling: as the number of mappers (M) and reducers (R) both grow, the number of network connections is M × R. With 1,000 mappers and 1,000 reducers: 1,000,000 network connections. The coupling of compute and temporary storage cannot scale independently — this was a major bottleneck. Google's solution: a separate distributed transient shuffle storage system where shuffle data is written once and consumed by reducers independently of the producing executor's lifecycle. Industry parallels: Uber's "Shuffle as a Service," Meta's Riffle (EuroSys 2018).</p>

<h3>Data Locality in Shuffle Reads</h3>
<p>Spark's <code>ExternalShuffleService</code> (a separate long-running daemon process on each worker node, outside the executor JVM, that serves shuffle files independently) decouples shuffle file serving from executor lifecycle. When enabled, shuffle files are served from the external service rather than from executor processes. If an executor dies, its shuffle output files are still available for the next stage — without this, executor failure in stage N would require re-running all of stage N.</p>
</div>

<div class="sketch">
<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig)" fill="none" stroke="#1c1c2e" stroke-width="2.2" stroke-linecap="round">
    <rect x="10"  y="14" width="212" height="222" rx="12" fill="#f8f8fc"/>
    <rect x="244" y="14" width="212" height="222" rx="12" fill="#f8f8fc"/>
    <rect x="478" y="14" width="212" height="222" rx="12" fill="#f8f8fc"/>
    <!-- SMJ: two sorted decks merging -->
    <rect x="34"  y="66" width="52" height="16" rx="3" fill="#dbeafe"/>
    <rect x="38"  y="86" width="52" height="16" rx="3" fill="#dbeafe"/>
    <rect x="42"  y="106" width="52" height="16" rx="3" fill="#dbeafe"/>
    <rect x="142" y="66" width="52" height="16" rx="3" fill="#fce7f3"/>
    <rect x="146" y="86" width="52" height="16" rx="3" fill="#fce7f3"/>
    <rect x="150" y="106" width="52" height="16" rx="3" fill="#fce7f3"/>
    <path d="M70 130 C80 152, 96 162, 108 168" marker-end="url(#arr)"/>
    <path d="M168 130 C158 152, 142 162, 130 168" marker-end="url(#arr)"/>
    <rect x="84" y="170" width="66" height="22" rx="5" fill="#dcfce7"/>
    <!-- SHJ: hash table + probe stream -->
    <rect x="278" y="58" width="82" height="74" rx="6" fill="#fef9c3"/>
    <path d="M278 82 L360 82 M278 106 L360 106 M318 58 L318 132"/>
    <path d="M394 150 C376 142, 366 130, 362 120" marker-end="url(#arr)"/>
    <path d="M420 160 L440 160 M420 172 L446 172 M420 184 L438 184" stroke="#666680"/>
    <!-- BHJ: one small table copied to 3 executors -->
    <rect x="560" y="40" width="46" height="30" rx="5" fill="#dcfce7" stroke-width="2.8"/>
    <rect x="496" y="150" width="54" height="40" rx="6" fill="#eff6ff"/>
    <rect x="558" y="150" width="54" height="40" rx="6" fill="#eff6ff"/>
    <rect x="620" y="150" width="54" height="40" rx="6" fill="#eff6ff"/>
    <path d="M568 74 C540 100, 528 124, 522 146" stroke="#16a34a" marker-end="url(#arr-g)"/>
    <path d="M583 74 L584 146" stroke="#16a34a" marker-end="url(#arr-g)"/>
    <path d="M598 74 C626 100, 638 124, 646 146" stroke="#16a34a" marker-end="url(#arr-g)"/>
  </g>
  <text x="116" y="42" text-anchor="middle" font-size="17" font-weight="700" fill="#1c1c2e">SMJ — sort &amp; merge</text>
  <text x="60"  y="60" text-anchor="middle" font-size="11.5" fill="#1e3a8a">table A, sorted</text>
  <text x="170" y="60" text-anchor="middle" font-size="11.5" fill="#9d174d">table B, sorted</text>
  <text x="117" y="186" text-anchor="middle" font-size="12" fill="#14532d">one pass</text>
  <text x="116" y="212" text-anchor="middle" font-size="12.5" fill="#44446a">2 full shuffles, but spills to</text>
  <text x="116" y="227" text-anchor="middle" font-size="12.5" fill="#44446a">disk safely. Slow &amp; steady.</text>
  <text x="350" y="42" text-anchor="middle" font-size="17" font-weight="700" fill="#1c1c2e">SHJ — hash table</text>
  <text x="319" y="50" text-anchor="middle" font-size="11" fill="#92400e">build side, ALL in memory</text>
  <text x="404" y="166" text-anchor="middle" font-size="11.5" fill="#666680">probe rows</text>
  <text x="350" y="212" text-anchor="middle" font-size="12.5" fill="#44446a">O(1) lookups — but the table</text>
  <text x="350" y="227" text-anchor="middle" font-size="12.5" fill="#dc2626" font-weight="700">CANNOT spill. Too big = OOM.</text>
  <text x="583" y="34" text-anchor="middle" font-size="17" font-weight="700" fill="#1c1c2e">BHJ — broadcast</text>
  <text x="583" y="60" text-anchor="middle" font-size="11" fill="#14532d">&lt;10MB</text>
  <text x="523" y="174" text-anchor="middle" font-size="10.5" fill="#1e3a8a">exec 1</text>
  <text x="585" y="174" text-anchor="middle" font-size="10.5" fill="#1e3a8a">exec 2</text>
  <text x="647" y="174" text-anchor="middle" font-size="10.5" fill="#1e3a8a">exec 3</text>
  <text x="584" y="212" text-anchor="middle" font-size="12.5" fill="#44446a">copy the small table to everyone.</text>
  <text x="584" y="227" text-anchor="middle" font-size="12.5" fill="#16a34a" font-weight="700">ZERO shuffle. No Exchange node.</text>
</svg>
</div>
<div class="sketch-cap">Diagram: the three join strategies side by side — SMJ merges two sorted decks after shuffling both; SHJ builds an in-memory hash table that cannot spill; BHJ mails a copy of the small table to every executor so no shuffle happens at all.</div>

<div class="scribble">so it's: SAFE (SMJ) vs FAST-BUT-FRAGILE (SHJ) vs FREE-IF-IT-FITS (BHJ). Don't shuffle 500GB to meet 8MB — mail the 8MB to everyone instead. <span class="who">— Alex, margin note</span></div>

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
<p>SHJ requires the build side partition to fit entirely in memory. If the build side is large, or if data is skewed such that one partition of the build side is disproportionately large, the executor runs out of memory building the hash table. <strong>Unlike SMJ, SHJ cannot spill to disk</strong> — a hash table must be fully resident to serve lookups correctly. This caused enough production OOMs that Spark 1.6 removed SHJ entirely. Spark 2.0 reintroduced it, but with the optimizer's default preference strongly favoring SMJ — Catalyst only selects SHJ when the build-side partition is confirmed small enough to fit safely in memory, and in practice this makes SHJ selection rare unless a query hint explicitly requests it. Vu Trinh's production rule reflects this: know exactly what you're doing before enabling SHJ, because the guardrail is a preference, not a hard safety net. Even with AQE's dynamic join switching, SHJ is only selected when the build-side partition is confirmed to fit in memory at runtime.</p>
</div>

<p>Vu's production rule: "In a production Spark application, make sure you know what you're doing when enabling SHJ; it's only efficient when the build-side partitions fit in memory. If they get larger for some reason, your application will likely get an OOM error."</p>

<div class="scribble">a hash table is all-or-nothing — you can't look things up in half a table that's on disk. That's the whole reason SHJ got kicked out of Spark 1.6. SMJ survives by spilling; SHJ just dies. <span class="who">— Alex, margin note</span></div>
</div>

<div class="topic">
<h2>Broadcast Hash Join (BHJ): The Best Join When It Fits</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>The small table is broadcast (sent as a complete copy) to every single executor in the cluster. Then every executor can perform the join locally — no network shuffle at all. The network cost is one broadcast (small table × num executors) instead of two full shuffles.</p>
</div>

<p>BHJ has one requirement: one side must fit in memory on every executor simultaneously. Spark's automatic broadcast threshold: if Catalyst estimates a table is smaller than <code>spark.sql.autoBroadcastJoinThreshold</code> (default <strong>10MB</strong>), it automatically selects BHJ. The broadcast table is serialized on the driver, sent to all executors via the BlockManager's broadcast channel, and each executor deserializes and stores it in Storage memory.</p>

<div class="box f"><div class="box-lbl">BHJ: Shuffle Eliminated, Not Reduced</div>
<p>The critical distinction between BHJ and the other join strategies is that BHJ <strong>eliminates</strong> the shuffle — it does not merely reduce it. SMJ and SHJ both require a full shuffle of both tables to co-locate matching keys. BHJ requires zero shuffle of either table: the large table is read directly from its source partitions without repartitioning, and the small table is broadcast as a complete copy to every executor. In an execution plan, an Exchange operator is Spark's internal name for a shuffle node — the point where data is redistributed across partitions. A BHJ appears with <strong>no <code>Exchange</code> operator</strong> on either side — the exchange step literally does not exist in the physical plan. This is why BHJ is so dramatically faster than SMJ for small-large joins: the dominant cost (two full shuffles) is entirely absent, not merely reduced. The trade-off is that the broadcast table must fit in executor Storage memory on every executor simultaneously — if any executor runs low on storage memory, the broadcast variable can be evicted, triggering OOM or re-broadcast.</p>
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

<p>The constraint: <code>bucketBy()</code> only works with <code>saveAsTable()</code>, not with <code>write.parquet()</code>. Bucketing metadata must be stored in the Hive metastore (a relational database, typically embedded or external like MySQL, that stores table schemas, partition layouts, and bucketing information so Spark and other engines can discover and use it at query time) so Spark can use it at join time. Both tables must be bucketed with the same number of buckets on the join key — if one has 50 buckets and the other has 100 buckets, key K hashes to a <em>different</em> bucket number in each table. Worked example with key K = 253: in table A (50 buckets), 253 % 50 = 3, so K lands in bucket 3. In table B (100 buckets), 253 % 100 = 53, so the same K lands in bucket 53. Bucket 3 of A and bucket 3 of B no longer contain the same keys — the co-partitioning property breaks and Spark must shuffle anyway.</p>

<div class="scribble">bucket join = pay the shuffle ONCE at write time, then join for free forever after. Only worth it if you join this table again and again — like pre-sorting your closet. <span class="who">— Alex, margin note</span></div>

<h3>Join Strategy Hint Priority</h3>
<p>Spark 3.0+ allows query hints to suggest a join strategy. When multiple hints conflict, Spark enforces this priority order:</p>
<ol>
  <li><strong>BROADCAST</strong> — highest priority; triggers BHJ</li>
  <li><strong>MERGE</strong> — triggers SMJ</li>
  <li><strong>SHUFFLE_HASH</strong> — triggers SHJ</li>
  <li><strong>SHUFFLE_REPLICATE_NL</strong> — nested loop join: for each row in the left table, scan every row in the right table looking for a match. O(n × m) complexity — extremely slow, used only when no equi-join condition exists.</li>
</ol>
<p>Important caveat: hints are suggestions, not mandates. The optimizer can reject a hint if the selected strategy is incompatible with the logical join type or if required conditions (like a build side fitting in memory for SHJ) are not met.</p>
</div>

<div class="topic">
<h2>Data Skew: The Silent Production Killer</h2>

<p>Data skew occurs when one key (or a small set of keys) has far more values than other keys. After a shuffle, all values for the skewed key land in one partition — one task processes 80% of the data while 199 other tasks process the remaining 20%. Symptoms: 199 tasks finish in 5 seconds; one task runs for 10 minutes; the entire stage waits for that one task.</p>

<div class="sketch">
<svg viewBox="0 0 700 200" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig)" stroke="#1c1c2e" stroke-width="2" stroke-linecap="round">
    <path d="M30 168 L672 168" fill="none" stroke-width="2.6"/>
    <g fill="#dcfce7" stroke="#16a34a">
      <rect x="40"  y="152" width="11" height="16" rx="2"/><rect x="56"  y="150" width="11" height="18" rx="2"/>
      <rect x="72"  y="153" width="11" height="15" rx="2"/><rect x="88"  y="151" width="11" height="17" rx="2"/>
      <rect x="104" y="152" width="11" height="16" rx="2"/><rect x="120" y="150" width="11" height="18" rx="2"/>
      <rect x="136" y="153" width="11" height="15" rx="2"/><rect x="152" y="151" width="11" height="17" rx="2"/>
      <rect x="168" y="152" width="11" height="16" rx="2"/><rect x="184" y="150" width="11" height="18" rx="2"/>
      <rect x="200" y="153" width="11" height="15" rx="2"/><rect x="216" y="151" width="11" height="17" rx="2"/>
      <rect x="232" y="152" width="11" height="16" rx="2"/><rect x="248" y="150" width="11" height="18" rx="2"/>
      <rect x="264" y="153" width="11" height="15" rx="2"/><rect x="280" y="151" width="11" height="17" rx="2"/>
      <rect x="296" y="152" width="11" height="16" rx="2"/><rect x="312" y="150" width="11" height="18" rx="2"/>
      <rect x="328" y="153" width="11" height="15" rx="2"/><rect x="344" y="151" width="11" height="17" rx="2"/>
      <rect x="360" y="152" width="11" height="16" rx="2"/><rect x="376" y="150" width="11" height="18" rx="2"/>
      <rect x="392" y="153" width="11" height="15" rx="2"/><rect x="408" y="151" width="11" height="17" rx="2"/>
      <rect x="424" y="152" width="11" height="16" rx="2"/><rect x="440" y="150" width="11" height="18" rx="2"/>
    </g>
    <rect x="490" y="22" width="60" height="146" rx="4" fill="#fecaca" stroke="#dc2626" stroke-width="3.4"/>
    <path d="M636 60 C606 46, 580 36, 558 32" fill="none" stroke="#dc2626" stroke-width="2.4" marker-end="url(#arr-r)"/>
  </g>
  <text x="248" y="140" text-anchor="middle" font-size="14.5" fill="#14532d">199 tasks · ~5 seconds each · done ✓</text>
  <text x="520" y="14"  text-anchor="middle" font-size="15" font-weight="700" fill="#dc2626">task #147</text>
  <text x="520" y="100" text-anchor="middle" font-size="21" font-weight="700" fill="#7f1d1d" transform="rotate(-90 520 100)">12 MINUTES</text>
  <text x="646" y="80"  text-anchor="middle" font-size="13.5" fill="#dc2626">the WHOLE stage</text>
  <text x="646" y="97"  text-anchor="middle" font-size="13.5" fill="#dc2626">waits for THIS guy</text>
  <text x="350" y="192" text-anchor="middle" font-size="13.5" fill="#44446a">(drawn to scale it'd be even worse — 144× longer than its neighbours)</text>
</svg>
</div>
<div class="sketch-cap">Diagram: a task-duration bar chart — 26 tiny green bars stand in for the 199 finished tasks, and one absurdly tall red bar (task #147, 12 minutes) towers over them. Skew means parallelism collapses to a single straggler.</div>

<div class="scribble">adding more executors does NOTHING here — the hot key all lands in ONE partition no matter how many machines you buy. Fix the data split, not the cluster size. <span class="who">— Alex, margin note</span></div>

<p>Three solutions for skew:</p>
<ul>
  <li><strong>AQE Skew Join Handling (Spark 3.0+, automatic):</strong> AQE detects skewed shuffle partitions by comparing partition sizes to the stage's median partition size. It automatically splits the large (skewed) partition into sub-partitions and replicates the non-skewed side to match. The join runs on the sub-partitions in parallel. No code changes required. Covered in depth in Ch5.</li>
  <li><strong>Salting (manual):</strong> Add a random prefix (0-9) to skewed keys before the join, and replicate the non-skewed side's matching rows with each prefix. The skewed key is now 10 different keys — each goes to a different partition. Cost: the non-skewed side is replicated 10×, increasing memory and network usage.</li>
  <li><strong>Repartition with higher partition count:</strong> More partitions means more tasks, each with a smaller slice. The skewed key still lands in one partition, but that partition is smaller as a fraction of total data. Only works if the skew is across many distinct keys; for a single heavily-skewed key, repartition does not help.</li>
</ul>
</div>

<div class="topic">
<h2>The Real-World Shuffle Problem at Scale: Uber's RSS</h2>
<div class="box why"><div class="box-lbl">Why This Matters</div>
<p>Shuffle is already expensive in theory. At Uber's scale — 137 million monthly active users, thousands of Spark jobs running concurrently — the local shuffle model created a new class of failure nobody expected. Not OOM. Not skew. <strong>SSD wear-out.</strong> Understanding how Uber fixed this reveals a fundamental truth: the shuffle architecture that works at 1TB breaks at 1PB, and the fix requires rethinking the paradigm entirely.</p>
</div>

<p>The standard Spark shuffle model is <strong>executor-local</strong>: each executor writes its shuffle output to local disk, and downstream executors pull from those locations. This design made sense when Spark was born. At Uber's scale, it created three compounding problems:</p>

<ul>
<li><strong>SSD wear-out</strong>: shuffle writes were burning through SSDs in approximately <strong>3 months</strong>. SSDs have a finite number of write cycles per cell; Spark's shuffle model continuously writes every partition's output to local SSD at every stage boundary, and at thousands of concurrent jobs this constant random-write load exhausts the SSD's rated write endurance far faster than expected. Hardware replacement cost was enormous.</li>
<li><strong>Shuffle failure cascades</strong>: if an executor died mid-job, its shuffle data was gone. The entire stage had to restart from scratch.</li>
<li><strong>Node coupling</strong>: compute and shuffle storage were tied to the same machines, making independent scaling impossible.</li>
</ul>

<div class="box s"><div class="box-lbl">The RSS Insight</div>
<p>Uber's Remote Shuffle Service (RSS) reverses the MapReduce paradigm. Instead of each executor managing its own shuffle data locally, <strong>RSS centralizes shuffle storage on dedicated servers</strong>. Executors push shuffle data to RSS nodes; downstream executors pull from RSS. Compute nodes no longer touch shuffle data at all — compute and shuffle storage are fully decoupled.</p>
</div>

<p>The results were measurable:</p>
<ul>
<li>SSD lifespan: <strong>3 months → approximately 3 years</strong> (10× improvement)</li>
<li>Shuffle failure rates: <strong>reduced by 95%</strong></li>
<li>Compute and shuffle storage can now scale independently</li>
</ul>

<div class="box n"><div class="box-lbl">The Trade-off</div>
<p>RSS adds network hops. In the standard model, shuffle writes go to local disk (zero network cost on write) and the read pulls over the network (one network hop). With RSS, both write and read cross the network — two hops. For small-to-medium jobs this overhead is not worth it. RSS is a solution to a <em>scale</em> problem — not a general replacement for local shuffle. <strong>Every decision has a trade-off.</strong></p>
</div>

<div class="box gap"><div class="box-lbl">Cross-Chapter Connection</div>
<p>RSS is evidence that Spark's shuffle-to-disk design (this chapter) and OOM-from-skew (Ch2) are not solved problems — they are active engineering areas. At sufficient scale, even correct designs require architectural replacement.</p>
</div>
</div>


<div class="bigfacts">
<div class="bigfacts-head">If you forget everything else in this chapter, keep these three:</div>
<div class="bigfact"><span class="n">1.</span>Shuffle = disk + network, ALWAYS. "In-memory" only applies inside a stage.</div>
<div class="bigfact"><span class="n">2.</span>BHJ doesn't reduce the shuffle — it DELETES it. No Exchange node at all.</div>
<div class="bigfact"><span class="n">3.</span>199 tasks done, 1 still running = skew. Fix the data split, not the cluster.</div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig)" fill="none" stroke="#666680" stroke-width="2.4" stroke-linecap="round">
    <ellipse cx="350" cy="150" rx="82" ry="34" fill="#f8f8fc" stroke="#1c1c2e" stroke-width="3"/>
    <rect x="46"  y="30"  width="170" height="60" rx="12" fill="#fff"/>
    <rect x="482" y="24"  width="184" height="96" rx="12" fill="#fff"/>
    <rect x="36"  y="204" width="184" height="72" rx="12" fill="#fff"/>
    <rect x="492" y="210" width="172" height="62" rx="12" fill="#fff"/>
    <path d="M276 130 C236 114, 212 102, 208 92" marker-end="url(#arr)"/>
    <path d="M428 132 C458 116, 478 106, 490 100" marker-end="url(#arr)"/>
    <path d="M284 172 C246 190, 220 198, 200 206" marker-end="url(#arr)"/>
    <path d="M422 170 C458 188, 486 198, 508 210" marker-end="url(#arr)"/>
  </g>
  <text x="350" y="146" text-anchor="middle" font-size="22" font-weight="700" fill="#1c1c2e">SHUFFLE</text>
  <text x="350" y="168" text-anchor="middle" font-size="14" fill="#666680">= ______ + ______ at every stage boundary</text>
  <text x="131" y="56"  text-anchor="middle" font-size="15" font-weight="700" fill="#666680">WHY DISK?</text>
  <text x="131" y="78"  text-anchor="middle" font-size="14" fill="#666680">__________________</text>
  <text x="574" y="46"  text-anchor="middle" font-size="15" font-weight="700" fill="#666680">3 WAYS TO JOIN</text>
  <text x="574" y="68"  text-anchor="middle" font-size="14" fill="#666680">S____ — safe, spills</text>
  <text x="574" y="86"  text-anchor="middle" font-size="14" fill="#666680">S____ — fast, ______</text>
  <text x="574" y="104" text-anchor="middle" font-size="14" fill="#666680">B____ — ____ shuffle</text>
  <text x="128" y="230" text-anchor="middle" font-size="15" font-weight="700" fill="#666680">DODGE THE SHUFFLE</text>
  <text x="128" y="250" text-anchor="middle" font-size="14" fill="#666680">________ join (pay at write)</text>
  <text x="128" y="268" text-anchor="middle" font-size="14" fill="#666680">______ByKey (shrink first)</text>
  <text x="578" y="236" text-anchor="middle" font-size="15" font-weight="700" fill="#666680">SKEW</text>
  <text x="578" y="258" text-anchor="middle" font-size="14" fill="#666680">1 ___ key → 1 _____ task</text>
</svg>
</div>
<div class="retrieval-note">✍️ Before the questions: close the chapter and redraw this map from memory — say every blank OUT LOUD, then flip back and check. Recall, not recognition.</div>

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
  <li><strong>NODE_LOCAL</strong> — Data is on the same physical node but a different JVM process. Common when an HDFS data block replica is stored on the same machine as the executor but served from the DataNode process, not executor memory. One IPC (Inter-Process Communication) call — a local call between two processes on the same machine, faster than a network call but slower than in-memory access; no network transfer.</li>
  <li><strong>NO_PREF</strong> — The data has no locality preference. This level applies to data sources that are uniformly accessible from any node — for example, data read from a JDBC database over a network connection, or data in object storage (S3/GCS) where every executor is equally distant. Spark assigns these tasks to any available executor immediately without waiting.</li>
  <li><strong>RACK_LOCAL</strong> — Data is on a different node but within the same network rack. One network hop through the top-of-rack switch. Better than ANY but worse than NODE_LOCAL.</li>
  <li><strong>ANY</strong> — Data is anywhere in the cluster. Cross-rack network transfer; highest latency.</li>
</ol>

<div class="box n"><div class="box-lbl">spark.locality.wait — Scheduling Trade-off</div>
<p>Spark does not immediately fall back to worse locality levels when better ones are unavailable. It waits up to <code>spark.locality.wait</code> (default: <strong>3 seconds</strong>) for a PROCESS_LOCAL slot to open before trying NODE_LOCAL, then another 3 seconds before RACK_LOCAL, then another 3 seconds before ANY. This waiting can improve performance when a task's preferred executor is momentarily busy — but it introduces latency when preferred executors are persistently overloaded. For shuffle-heavy jobs, setting <code>spark.locality.wait = 0</code> eliminates this wait and lets tasks start immediately. The reason locality matters less for shuffles: shuffle files are spread across all executors by design — there is no preferred local copy for a given task, so waiting for locality gains nothing and only delays task start. For cache-heavy jobs (e.g., iterative ML reading the same RDD 100 times), keeping locality wait high ensures tasks land near cached partitions.</p>
</div>
</div>

<div class="topic">
<h2>reduceByKey vs groupByKey — Minimize Data Movement Before Shuffle</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>The single most powerful principle in Spark performance: push computation as close to the data source as possible. For aggregations, this means reducing data volume <em>before</em> the shuffle, not after. reduceByKey does this; groupByKey does not.</p>
</div>

<p>In the context of shuffle optimization, the groupByKey vs reduceByKey choice is really about <strong>how much data crosses the network</strong>:</p>

<p><strong>groupByKey shuffle mechanics:</strong> Every raw value for every key is written to shuffle map files and transferred to the reducer over the network. The reducer receives a complete iterator over all values for its keys — only then can it begin aggregating. No work is done on the mapper side to reduce data volume. For a key with 10M values spread across 200 partitions: all 10M values cross the shuffle boundary.</p>

<p><strong>reduceByKey local partial reduction (combiner):</strong> On each mapper partition, reduceByKey applies a local partial reduction: all values with the same key within that partition are combined into a single per-partition aggregate using the provided associative and commutative function (associative and commutative means combining values in any order gives the same result — addition or set union qualify, but subtraction does not). Only this single combined value per key per partition is written to the shuffle file. For 10M values across 200 partitions: at most 200 aggregated values per key cross the network — a potential 50,000× reduction in shuffle data for a highly repeated key.</p>

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

<div class="scribble">shrink the data BEFORE it travels — like zipping a file before emailing it. 10,000,000 values → 200 values crossing the network, just by picking the right function. <span class="who">— Alex, margin note</span></div>
</div>

<div class="topic">
<h2>Speculative Execution: Handling Slow Tasks</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>If one task in a stage is running much slower than all the others — a "straggler" — Spark can launch a duplicate copy of that task on a different executor. Whichever copy finishes first wins; the other is killed. This is speculative execution: betting that the slowness is caused by a bad executor, not by the task itself.</p>
</div>

<p>Speculative execution addresses straggler tasks — tasks that run significantly longer than the median task in their stage. Stragglers occur due to hardware issues (slow disk, network degradation, memory pressure on one node), GC pauses on one executor, or data skew (one partition has disproportionately more data). The straggler blocks stage completion, holding up all downstream stages.</p>

<p>When enabled (<code>spark.speculation = true</code>), Spark monitors task progress and detects slow tasks whose completion time is more than a configurable multiple of the stage median (default threshold: <code>spark.speculation.multiplier = 1.5</code>). For each such task, Spark launches a <strong>speculative copy</strong> on a different executor. The <em>first copy to complete</em> wins — its output is used for the next stage. The slower copy is killed.</p>

<div class="box f"><div class="box-lbl">Speculative Execution Trade-offs and Risks</div>
<p><strong>Risk — duplicate processing:</strong> Two copies of the same task run simultaneously and may produce side effects twice (e.g., writing duplicate rows to an external database, double-counting an accumulator). Speculative execution is only safe with idempotent operations (idempotent means running the same operation twice produces the same result as running it once — writing the same row to Delta Lake using MERGE is idempotent; inserting a raw row twice without deduplication is not) or when using exactly-once output semantics (Delta Lake, transactional sinks).</p>
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

<div class="sketch">
<svg viewBox="0 0 700 320" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <ellipse cx="350" cy="150" rx="86" ry="34" fill="#eff6ff" stroke-width="3.4"/>
    <rect x="26"  y="18"  width="208" height="86" rx="12" fill="#f0fdf4"/>
    <rect x="470" y="16"  width="204" height="98" rx="12" fill="#faf5ff"/>
    <rect x="18"  y="210" width="208" height="84" rx="12" fill="#f0f9ff"/>
    <rect x="478" y="212" width="196" height="82" rx="12" fill="#fff1f2"/>
    <path d="M272 128 C230 108, 204 96, 198 96" marker-end="url(#arr)"/>
    <path d="M428 130 C462 110, 486 98, 498 98" marker-end="url(#arr)"/>
    <path d="M282 176 C238 198, 212 208, 196 216" marker-end="url(#arr)"/>
    <path d="M418 174 C456 196, 482 206, 506 214" marker-end="url(#arr)"/>
  </g>
  <text x="350" y="146" text-anchor="middle" font-size="22" font-weight="700" fill="#1c1c2e">PERFORMANCE</text>
  <text x="350" y="168" text-anchor="middle" font-size="13.5" fill="#44446a">3 layers, one story</text>
  <text x="130" y="40"  text-anchor="middle" font-size="16" font-weight="700" fill="#14532d">PYSPARK BRIDGE</text>
  <text x="130" y="60"  text-anchor="middle" font-size="13" fill="#14532d">2 processes, Py4J glue</text>
  <text x="130" y="76"  text-anchor="middle" font-size="13" fill="#14532d">UDF = row-by-row tax</text>
  <text x="130" y="92"  text-anchor="middle" font-size="12" fill="#16a34a" font-weight="700">Arrow batches fix it</text>
  <text x="572" y="38"  text-anchor="middle" font-size="16" font-weight="700" fill="#581c87">TUNGSTEN</text>
  <text x="572" y="58"  text-anchor="middle" font-size="13" fill="#581c87">4B string costs 48B</text>
  <text x="572" y="74"  text-anchor="middle" font-size="13" fill="#581c87">as a JVM object</text>
  <text x="572" y="94"  text-anchor="middle" font-size="12" fill="#dc2626" font-weight="700">off-heap = GC invisible</text>
  <text x="122" y="236" text-anchor="middle" font-size="16" font-weight="700" fill="#0c4a6e">PHOTON (C++)</text>
  <text x="122" y="256" text-anchor="middle" font-size="13" fill="#0c4a6e">vectorized, JNI = 0.06%</text>
  <text x="122" y="272" text-anchor="middle" font-size="13" fill="#0c4a6e">enhances, not replaces</text>
  <text x="576" y="238" text-anchor="middle" font-size="16" font-weight="700" fill="#881337">PERF HIERARCHY</text>
  <text x="576" y="258" text-anchor="middle" font-size="13" fill="#881337">built-in &lt; Pandas UDF</text>
  <text x="576" y="274" text-anchor="middle" font-size="13" fill="#881337">&lt;&lt; Python UDF (200×!)</text>
  <text x="350" y="312" text-anchor="middle" font-size="13.5" fill="#44446a">every layer here exists because the JVM has a cost the engineers refused to accept</text>
</svg>
</div>
<div class="sketch-cap">The whole chapter on one napkin. Diagram: Performance at the hub, with four branches — the PySpark process bridge, Tungsten's binary format, Photon's native C++ engine, and the resulting performance hierarchy.</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>In 2013, 92% of Databricks users wrote Spark in Scala. By 2020, 47% used Python and 41% used SQL — Scala dropped to 12%. Python is now the dominant Spark language. But Spark runs on the JVM. Python is a separate process. Every operation crosses a process boundary with serialization overhead. Understanding where that overhead occurs — and which modern APIs eliminate it — is essential for any PySpark engineer writing production code on large datasets.</p>
</div>

<div class="topic">
<h2>The PySpark Two-Process Architecture</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>When you run a PySpark script, two separate processes start: a Python process (your code) and a JVM process (the actual Spark engine). Your Python code talks to Spark through a library called Py4J that translates Python method calls into Java calls. Most of the time this is fast because you're only sending small amounts of data (file paths, configuration). The problem: Python UDFs send every single row of your data through this bridge, one row at a time.</p>
</div>

<div class="sketch">
<svg viewBox="0 0 700 210" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.4" stroke-linecap="round">
    <rect x="30"  y="40" width="170" height="120" rx="10" fill="#dbeafe"/>
    <rect x="500" y="40" width="170" height="120" rx="10" fill="#dcfce7"/>
  </g>
  <g stroke="#dc2626" stroke-width="2" fill="none">
    <path d="M204 66 L496 66" marker-end="url(#arr-r)"/><path d="M496 84 L204 84" marker-end="url(#arr-r)"/>
    <path d="M204 102 L496 102" marker-end="url(#arr-r)"/><path d="M496 120 L204 120" marker-end="url(#arr-r)"/>
    <path d="M204 138 L496 138" marker-end="url(#arr-r)"/>
  </g>
  <text x="115" y="30" text-anchor="middle" font-size="16" font-weight="700" fill="#1e3a8a">JVM (Spark)</text>
  <text x="115" y="90" text-anchor="middle" font-size="13" fill="#1e3a8a">DAGScheduler</text>
  <text x="115" y="108" text-anchor="middle" font-size="13" fill="#1e3a8a">BlockManager</text>
  <text x="115" y="126" text-anchor="middle" font-size="13" fill="#1e3a8a">real data lives here</text>
  <text x="585" y="30" text-anchor="middle" font-size="16" font-weight="700" fill="#14532d">Python worker</text>
  <text x="585" y="90" text-anchor="middle" font-size="13" fill="#14532d">your UDF code</text>
  <text x="585" y="108" text-anchor="middle" font-size="13" fill="#14532d">Pickle in, Pickle out</text>
  <text x="350" y="60"  text-anchor="middle" font-size="12.5" fill="#dc2626">row 1 →</text>
  <text x="350" y="96"  text-anchor="middle" font-size="12.5" fill="#dc2626">← row 1 result</text>
  <text x="350" y="114" text-anchor="middle" font-size="12.5" fill="#dc2626">row 2 →</text>
  <text x="350" y="150" text-anchor="middle" font-size="12.5" fill="#dc2626">…10,000,000 more times</text>
  <text x="350" y="186" text-anchor="middle" font-size="16" font-weight="700" fill="#dc2626">one row = one round trip across the socket</text>
  <text x="350" y="204" text-anchor="middle" font-size="13" fill="#44446a">Pandas UDFs replace this with ONE big Arrow batch, not 10M little ones</text>
</svg>
</div>
<div class="sketch-cap">Diagram: the JVM process and Python worker process as two boxes connected by a socket; a Python UDF forces every single row to cross that socket individually via Pickle serialization.</div>

<div class="scribble">imagine mailing a letter for every single word of a book instead of just mailing the whole book once. That's a Python UDF vs a Pandas UDF. <span class="who">— Alex, margin note</span></div>

<p>PySpark is a wrapper around Apache Spark's JVM implementation. When a PySpark script executes, two processes start simultaneously:</p>
<ul>
  <li><strong>Python process (port 25334 by default):</strong> Your driver code — DataFrame operations, configurations, control flow. This is the Python process you write.</li>
  <li><strong>JVM process (port 25333 by default):</strong> The actual Spark driver running on the JVM — DAGScheduler, TaskScheduler, BlockManager, shuffle management. This is where Spark actually runs.</li>
</ul>

<p>Communication between these two processes uses the <strong>Py4J</strong> library. Py4J runs as a small gateway server inside the JVM process; the matching Python-side library sends Python method calls to that gateway over a local IPC socket (IPC — Inter-Process Communication — a channel that lets two processes on the same machine exchange bytes, similar to a private network connection that never leaves the machine). When your Python code calls <code>df.read.load('data.parquet')</code>, Py4J serializes this call, sends it to the JVM process over the socket, the JVM executes it, and any result is serialized back.</p>

<p>For most DataFrame operations — reading files, applying built-in SQL functions, writing output — the IPC overhead is negligible. You're sending a file path string or a plan description, not data. The JVM handles the actual data processing. Built-in SQL functions are already implemented inside the JVM, so Spark processes rows there without ever leaving the JVM. The Python code just drives.</p>

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

<p>This happens for <strong>every single row</strong>. On a 10M-row DataFrame, that is 10M serialization round-trips. The combined overhead — JVM/Python process switching, Pickle serialization, socket transfer, deserialization — typically makes Python UDFs 50–200× slower than equivalent built-in Spark functions (the exact multiplier depends on row size and UDF complexity, but the mechanism — one round trip per row — is constant).</p>

<p>Python UDFs also lose two Spark performance features:</p>
<ul>
  <li><strong>No Catalyst optimization:</strong> Catalyst cannot see inside a Python function. No predicate pushdown (skipping rows before reading all data), no projection pruning (reading only the columns the query needs), no plan rewriting around the UDF.</li>
  <li><strong>No Tungsten binary encoding:</strong> Tungsten's UnsafeRow format cannot be used — the data must be deserialized to Python objects before the UDF can process it.</li>
</ul>
</div>

<div class="topic">
<h2>Pandas UDFs (Vectorized UDFs) and Arrow Transfer</h2>

<p>Spark 2.3 introduced <strong>Pandas UDFs</strong> (also called vectorized UDFs) as a high-performance alternative to Python UDFs. The key difference: instead of sending one row at a time through the IPC bridge, Pandas UDFs send entire batches of rows using <strong>Apache Arrow</strong>'s columnar format.</p>

<p>Apache Arrow organizes memory in columnar format — all values of column A are stored contiguously, then all values of column B, etc. Think of it like sorting a deck of cards by suit: all hearts together, all spades together (columnar) rather than in the order they were dealt (row-oriented). This columnar layout lets the CPU scan one column efficiently without touching others. The critical property: Arrow is a <strong>zero-copy</strong> serialization format. Normally, sending data between two processes means the OS copies bytes from one process's memory into the other's. Zero-copy means both processes map the same physical block of RAM — no copying happens. The JVM and Python processes share the same Arrow buffer via shared memory, eliminating the most expensive part of the IPC overhead.</p>

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
  <li><strong>gRPC</strong> (a modern framework from Google for making structured remote procedure calls over HTTP/2 — think of it as a fast, typed, binary alternative to REST) as the transport protocol between client and server</li>
  <li><strong>Protocol Buffers</strong> (Google's binary serialization format — compact, fast, language-agnostic) for encoding query plans</li>
  <li><strong>Apache Arrow record batches</strong> for returning results</li>
</ul>

<p>The Python Spark Connect client requires only Python — no JVM, no Py4J, no local Spark installation. The client converts a DataFrame query to an unresolved logical plan, encodes it in Protobuf, and sends it to the remote Spark Connect Server via gRPC. The server hosts a long-running Spark application, analyzes the plan, optimizes it with Catalyst, executes it on the cluster, and streams results back as Arrow record batches.</p>

<p>Practical benefits: because each Spark Connect client sends self-contained plans over gRPC rather than sharing a single JVM driver's in-memory state, the server can give each client a fully isolated session — OOM errors in one client session don't affect other clients (isolated sessions); the Spark driver can be upgraded independently of client applications; thin clients (IoT devices, CI/CD jobs, notebooks) can submit Spark jobs without a local JVM.</p>

<p>Limitations: Spark Connect supports only the DataFrame API — RDD API and SparkContext API are not available through the Connect interface. Resource configuration (executor count, memory) is set at server startup, not per-client.</p>
</div>

<div class="topic">
<h2>Project Tungsten: Bypassing JVM Object Overhead</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Every Java object on the heap carries an unavoidable 16-byte "tax" — the object header. A 4-byte string isn't 4 bytes; it's 48+ bytes because of this tax plus the string's internal structure. Tungsten bypasses the JVM entirely: it stores data as raw compact binary at memory addresses it manages directly, the same way C programs manage memory. The garbage collector never touches this data — GC pauses shrink dramatically.</p>
</div>

<h3>The JVM Object Header Problem — Why a 4-byte String Costs 48+ Bytes</h3>

<p>Think of it like mailing a sticky note (4 bytes of actual data) but the postal service requires a padded shipping box with a mandatory 16-byte customs label on the outside — you always pay for the box, no matter how small the contents. Every Java heap object carries a mandatory <strong>object header</strong> of 16 bytes on a 64-bit JVM:</p>
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

<div class="sketch">
<svg viewBox="0 0 700 190" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.2" stroke-linecap="round">
    <rect x="30"  y="30" width="280" height="130" rx="10" fill="#fff1f2"/>
    <rect x="390" y="30" width="280" height="130" rx="10" fill="#dcfce7"/>
  </g>
  <rect x="50"  y="56" width="16" height="88" fill="#fecaca" stroke="#dc2626" stroke-width="1.6"/>
  <rect x="70"  y="130" width="200" height="14" fill="#fee2e2" stroke="#dc2626" stroke-width="1.6"/>
  <text x="170" y="46" text-anchor="middle" font-size="16" font-weight="700" fill="#7f1d1d">"ABCD" as a JVM object</text>
  <text x="58"  y="100" font-size="10.5" fill="#7f1d1d" transform="rotate(-90 58 100)">header 16B</text>
  <text x="170" y="140" text-anchor="middle" font-size="12" fill="#7f1d1d">char[] array object + refs + padding</text>
  <text x="170" y="158" text-anchor="middle" font-size="18" font-weight="700" fill="#dc2626">≈ 48–64 bytes for 4 bytes of data</text>
  <rect x="410" y="90" width="32" height="20" fill="#bbf7d0" stroke="#16a34a" stroke-width="2"/>
  <text x="530" y="46" text-anchor="middle" font-size="16" font-weight="700" fill="#14532d">"ABCD" in Tungsten UnsafeRow</text>
  <text x="530" y="104" text-anchor="middle" font-size="13" fill="#14532d">← literally just 4 bytes</text>
  <text x="530" y="140" text-anchor="middle" font-size="18" font-weight="700" fill="#16a34a">no header. no wrapper. no GC scan.</text>
</svg>
</div>
<div class="sketch-cap">Diagram: the same 4-byte string drawn to scale — as a JVM object it balloons to 48-64 bytes of header, wrapper, and padding; in Tungsten's UnsafeRow it is exactly the 4 bytes it needs to be.</div>

<div class="scribble">12-28× overhead for a FOUR-BYTE string?? and the garbage collector has to walk past every one of those bloated boxes. off-heap just... removes the boxes. <span class="who">— Alex, margin note</span></div>

<p>Project Tungsten addresses this with three components:</p>

<h3>Component 1: Off-Heap Binary Storage via UnsafeRow and <code>sun.misc.Unsafe</code></h3>
<p>The <code>UnsafeRow</code> format stores rows as compact binary data using Java's <code>sun.misc.Unsafe</code> API to perform direct memory access at raw physical addresses — outside the JVM heap entirely. <code>sun.misc.Unsafe</code> exposes C-style pointer arithmetic: you can read and write arbitrary bytes at a memory address without going through the JVM's object model. Tungsten allocates off-heap memory blocks and manages them manually, storing row data with zero object overhead: a 4-byte integer is stored as exactly 4 bytes at a known offset within a row buffer, not as a 24-byte boxed <code>java.lang.Integer</code>.</p>

<p>The critical consequence: <strong>the JVM GC never scans Tungsten's off-heap memory.</strong> GC pause duration scales with the number of live objects on the heap. With Tungsten, the data plane (billions of rows of table data) lives in off-heap memory that the GC is completely unaware of — even if executors hold 128GB of data, GC pause time remains low because the GC heap is nearly empty. Only Spark's own framework objects (schedulers, metadata, user objects) live on the GC heap.</p>

<p>A row of (integer, long, double) takes exactly 4 + 8 + 8 = 20 bytes in UnsafeRow vs potentially 72+ bytes as JVM objects. Variable-width fields (strings) are stored in a separate variable-length section with fixed-width offsets in the main row body, allowing O(1) random access to any field without scanning the entire row.</p>

<h3>Component 2: Cache-Aware Computation</h3>
<p>Data structures are designed around CPU cache line sizes (64 bytes). Sort algorithms that access memory sequentially rather than randomly benefit from hardware prefetching. Hash tables are laid out so that the probe sequence stays within a cache line, reducing cache misses. Columnar layout (all values of column A contiguous, then column B) is fundamentally more cache-friendly than row layout when aggregating a single column — the CPU can prefetch a full cache line of column A values and process 16 integers at once.</p>

<h3>Component 3: Whole-Stage Code Generation via Janino</h3>
<p>Catalyst Phase 4 generates query-specific JVM bytecode at runtime using Scala quasiquotes to construct the AST of a Java class, then compiles it using <strong>Janino</strong> — a lightweight Java compiler embedded in Spark (not the full <code>javac</code>, the standard Java compiler you'd install on your machine; Janino compiles code at runtime without needing a full JDK on every worker). For a specific query, Catalyst generates a single Java class with a tight <code>processNext()</code> loop that inlines all operators — filter conditions, projection expressions, hash key computation, and aggregation — into a single method body. The JIT compiler (Just-In-Time compiler — the JVM subsystem that identifies frequently-run bytecode and compiles it to native machine code at runtime) receives one large hot method rather than a chain of polymorphic virtual dispatch calls (virtual dispatch is what happens when the JVM must decide at runtime which version of a method to call because multiple operators share the same interface — this decision overhead accumulates across millions of rows), and can optimize the loop as a unit (loop unrolling, register allocation, constant folding). There is no interpreter overhead: no switch statements routing rows through operator interfaces, no virtual dispatch between filter → project → aggregate. Everything is one inlined loop.</p>

<div class="box n"><div class="box-lbl">HashAggregate Operator: Tungsten in Practice</div>
<p>When Spark executes a <code>GROUP BY</code> with numeric aggregations (SUM, COUNT, AVG on integers/longs), it uses the <code>HashAggregate</code> operator backed by Tungsten's off-heap hash table (UnsafeFixedWidthAggregationMap). Keys and values are stored as UnsafeRow binary data — tight packing, no GC pressure.</p>
<p>When aggregation involves String columns, Tungsten's fixed-width hash table cannot accommodate variable-length mutable values. Spark falls back to <code>SortAggregate</code>, which sorts by key and streams through — slower, more spill. This is why avoiding String-typed groupBy keys (when possible, use integer IDs) improves aggregation performance significantly.</p>
<p><strong>Why fixed-width, mechanistically:</strong> <code>UnsafeFixedWidthAggregationMap</code> locates every aggregation buffer with direct pointer arithmetic — <code>slot_address = base_address + (slot_index × fixed_slot_size)</code> — the same O(1) addressing trick that makes UnsafeRow field access fast. This requires every slot to be exactly <code>fixed_slot_size</code> bytes, known in advance, so the map can jump straight to any slot without scanning. A running SUM or COUNT is a fixed-width value (8 bytes for a long) that is mutated <em>in place</em> at that address on every incoming row — no reallocation, no GC. A variable-length String value breaks this: its size isn't known until the value arrives, and if a new value is longer than the one already in the slot, an in-place update would overwrite adjacent memory. There is no way to grow a slot without either reallocating (defeating the in-place mutation model) or over-allocating for a worst-case length up front (wasting memory across millions of slots). <code>SortAggregate</code> avoids the problem entirely by never doing in-place random-access mutation — it sorts first so identical keys become adjacent, then streams through with a regular (variable-length-safe) accumulator.</p>
</div>
</div>

<div class="topic">
<h2>Photon: C++ Vectorized Execution for the Lakehouse</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Photon is a C++ query engine that Databricks built inside Databricks Runtime (DBR) for Lakehouse workloads (Lakehouse combines the low-cost open-format storage of a data lake — files on object storage like S3 — with the query performance and ACID transaction guarantees of a data warehouse; Delta Lake is Databricks' implementation). It replaces specific JVM physical operators with C++ operators that process data in columnar batches with SIMD-style vectorized operations (SIMD — Single Instruction, Multiple Data — a CPU feature that processes multiple values with one instruction; for example, adding eight integers in a single CPU cycle instead of eight separate cycles). It's not a replacement for Spark — it's an enhancement that activates for supported operations and falls back to standard JVM Spark for unsupported ones.</p>
</div>

<h3>Why Databricks Needed Native C++</h3>
<p>Even with Tungsten's off-heap storage and code generation, the JVM has fundamental ceilings that only a fully native engine can break past. Databricks identified five JVM performance ceilings they could not overcome in the existing engine:</p>
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

<div class="box f"><div class="box-lbl">What Code Generation Buys That Vectorized Execution Gives Up</div>
<p>The trade-off is not one-sided. Code generation's advantage is <strong>operator fusion</strong>: Catalyst's Janino-generated code inlines every operator in the query — filter, project, hash computation, aggregation — into a single specialized tight loop with zero per-operator dispatch overhead (this is the same mechanism from Ch1's Catalyst Phase 4). A vectorized engine like Photon, by contrast, still dispatches to a separate operator implementation for each column batch at each step of the plan — the batching amortizes that dispatch cost over thousands of rows instead of one, but the dispatch still happens once per operator per batch, not zero times. This per-operator-per-batch cost is the classic "Volcano-style iterator overhead" that whole-stage code generation was invented to eliminate. Photon accepts this residual cost in exchange for the weeks-not-months build time, native debuggability, and runtime adaptivity described above — it is a deliberate trade of a small, amortized overhead for engineering velocity, not a strictly better technique.</p>
</div>

<h3>Photon's Data Model: Column Vectors and Position Lists</h3>
<p>The fundamental data unit in Photon is a <strong>column vector</strong>: all values of one column for a batch of rows, stored contiguously. A <strong>column batch</strong> is a set of column vectors representing a set of rows. Each column vector also carries a byte vector for NULL information.</p>

<p>Photon's filter implementation is elegant: instead of removing filtered rows from the batch (expensive memory movement), Photon maintains a <strong>position list</strong>. Think of it like a bouncer's guest list — instead of physically removing people from a room who fail the filter, the bouncer marks them off the active list. Everyone stays in place; only the list changes. Photon maintains an array of indices of the "active" rows (those not yet filtered out). The filter expression marks positions as inactive in the position list. Downstream operators check the position list and skip inactive rows. No data movement; no copying.</p>

<div class="scribble">it's the classroom trick where instead of physically moving kids who failed the quiz to the back of the room, the teacher just crosses their names off the "still in the game" list. Nobody moves — the list moves. <span class="who">— Alex, margin note</span></div>

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
    <tr><td>JVM Spark ↔ Photon (C++)</td><td class="g">Intra-process: JNI (Java Native Interface — a standard mechanism that lets JVM code call functions written in C or C++ within the same process) call within the same JVM process; passing a pointer to a column batch buffer</td><td class="g">One JNI call per column batch (thousands of rows); pointer arithmetic, no data copying</td><td class="g">0.06% of execution time — negligible</td></tr>
  </tbody>
</table>
<p>The key insight: Python UDF overhead is a <strong>process boundary problem</strong> — two separate OS processes communicating over a socket, with data serialized and deserialized row by row. Crossing a process boundary requires the OS kernel to mediate every data transfer, adding copy overhead and scheduling latency. JNI overhead is an <strong>intra-process function call</strong> — the JVM and C++ code share the same memory space; no kernel involvement, no copying. JNI passes a pointer to a column vector buffer, not a copy of the data. When data is passed as batched column vector pointers rather than row-by-row, the JNI call overhead is amortized over thousands of rows and becomes immeasurably small.</p>
</div>

<p>Photon participates in AQE: its operators implement the required interfaces to export shuffle statistics (e.g., shuffle file sizes) for AQE's runtime re-optimization decisions.</p>
</div>

<div class="bigfacts">
<div class="bigfacts-head">If you forget everything else in this chapter, keep these three:</div>
<div class="bigfact"><span class="n">1.</span>A Python UDF crosses a process boundary PER ROW. Pandas UDFs cross it per batch.</div>
<div class="bigfact"><span class="n">2.</span>A 4-byte string costs 48+ bytes as a JVM object. Tungsten stores it as 4 bytes, off-heap.</div>
<div class="bigfact"><span class="n">3.</span>Photon enhances Spark, it doesn't replace it — JNI intra-process calls cost ~0.06%.</div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#666680" stroke-width="2.4" stroke-linecap="round">
    <ellipse cx="350" cy="150" rx="86" ry="34" fill="#f8f8fc" stroke="#1c1c2e" stroke-width="3"/>
    <rect x="26"  y="18"  width="208" height="86" rx="12" fill="#fff"/>
    <rect x="470" y="16"  width="204" height="98" rx="12" fill="#fff"/>
    <rect x="18"  y="210" width="208" height="84" rx="12" fill="#fff"/>
    <rect x="478" y="212" width="196" height="82" rx="12" fill="#fff"/>
    <path d="M272 128 C230 108, 204 96, 198 96" marker-end="url(#arr)"/>
    <path d="M428 130 C462 110, 486 98, 498 98" marker-end="url(#arr)"/>
    <path d="M282 176 C238 198, 212 208, 196 216" marker-end="url(#arr)"/>
    <path d="M418 174 C456 196, 482 206, 506 214" marker-end="url(#arr)"/>
  </g>
  <text x="350" y="146" text-anchor="middle" font-size="20" font-weight="700" fill="#1c1c2e">PERFORMANCE</text>
  <text x="350" y="168" text-anchor="middle" font-size="13.5" fill="#666680">3 layers, ___ story</text>
  <text x="130" y="42"  text-anchor="middle" font-size="15" font-weight="700" fill="#666680">PYSPARK BRIDGE</text>
  <text x="130" y="62"  text-anchor="middle" font-size="13.5" fill="#666680">2 processes, ____ glue</text>
  <text x="130" y="78"  text-anchor="middle" font-size="13.5" fill="#666680">UDF = ______-by-_____ tax</text>
  <text x="572" y="40"  text-anchor="middle" font-size="15" font-weight="700" fill="#666680">TUNGSTEN</text>
  <text x="572" y="60"  text-anchor="middle" font-size="13.5" fill="#666680">4B string costs ___B</text>
  <text x="572" y="76"  text-anchor="middle" font-size="13.5" fill="#666680">off-heap = ___ invisible</text>
  <text x="122" y="238" text-anchor="middle" font-size="15" font-weight="700" fill="#666680">PHOTON (___)</text>
  <text x="122" y="258" text-anchor="middle" font-size="13.5" fill="#666680">vectorized, JNI = ____%</text>
  <text x="576" y="240" text-anchor="middle" font-size="15" font-weight="700" fill="#666680">PERF HIERARCHY</text>
  <text x="576" y="260" text-anchor="middle" font-size="13.5" fill="#666680">built-in &lt; ______ UDF &lt;&lt; Python UDF</text>
</svg>
</div>
<div class="retrieval-note">✍️ Close the chapter and redraw this map from memory, saying every blank OUT LOUD — then flip back and check. Recall, not recognition.</div>

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

<div class="sketch">
<svg viewBox="0 0 700 320" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <ellipse cx="350" cy="150" rx="86" ry="34" fill="#eff6ff" stroke-width="3.4"/>
    <rect x="26"  y="18"  width="204" height="86" rx="12" fill="#f0fdf4"/>
    <rect x="472" y="16"  width="202" height="98" rx="12" fill="#faf5ff"/>
    <rect x="18"  y="210" width="204" height="84" rx="12" fill="#f0f9ff"/>
    <rect x="478" y="212" width="196" height="82" rx="12" fill="#fff1f2"/>
    <path d="M272 128 C230 108, 204 96, 198 96" marker-end="url(#arr)"/>
    <path d="M428 130 C462 110, 486 98, 498 98" marker-end="url(#arr)"/>
    <path d="M282 176 C238 198, 212 208, 196 216" marker-end="url(#arr)"/>
    <path d="M418 174 C456 196, 482 206, 506 214" marker-end="url(#arr)"/>
  </g>
  <text x="350" y="146" text-anchor="middle" font-size="20" font-weight="700" fill="#1c1c2e">STREAM = TABLE</text>
  <text x="350" y="168" text-anchor="middle" font-size="13.5" fill="#44446a">that keeps growing</text>
  <text x="128" y="40"  text-anchor="middle" font-size="16" font-weight="700" fill="#14532d">MICRO-BATCHES</text>
  <text x="128" y="60"  text-anchor="middle" font-size="13" fill="#14532d">same DataFrame API</text>
  <text x="128" y="76"  text-anchor="middle" font-size="13" fill="#14532d">no separate streaming API</text>
  <text x="128" y="92"  text-anchor="middle" font-size="12" fill="#16a34a" font-weight="700">trigger controls the cadence</text>
  <text x="570" y="38"  text-anchor="middle" font-size="16" font-weight="700" fill="#581c87">WATERMARKS</text>
  <text x="570" y="58"  text-anchor="middle" font-size="13" fill="#581c87">how late is "too late"</text>
  <text x="570" y="74"  text-anchor="middle" font-size="13" fill="#581c87">bounds memory state</text>
  <text x="570" y="94"  text-anchor="middle" font-size="12" fill="#dc2626" font-weight="700">no watermark = state forever</text>
  <text x="120" y="236" text-anchor="middle" font-size="16" font-weight="700" fill="#0c4a6e">AQE = CATALYST v2</text>
  <text x="120" y="256" text-anchor="middle" font-size="13" fill="#0c4a6e">re-plans after each shuffle</text>
  <text x="120" y="272" text-anchor="middle" font-size="13" fill="#0c4a6e">facts, not estimates</text>
  <text x="576" y="238" text-anchor="middle" font-size="16" font-weight="700" fill="#881337">AQE'S 3 FIXES</text>
  <text x="576" y="258" text-anchor="middle" font-size="13" fill="#881337">coalesce · switch join ·</text>
  <text x="576" y="274" text-anchor="middle" font-size="13" fill="#881337">split skewed partitions</text>
  <text x="350" y="312" text-anchor="middle" font-size="13.5" fill="#44446a">this chapter closes the loop — Ch1's Catalyst finally gets to see real numbers</text>
</svg>
</div>
<div class="sketch-cap">The whole chapter on one napkin. Diagram: Structured Streaming's "stream as table" idea at the hub, branching into micro-batches, watermarks, AQE as runtime Catalyst, and AQE's three concrete fixes.</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>Batch Spark processes data in minutes to hours. Fraud detection, real-time dashboards, and operational alerts require sub-minute latency. Structured Streaming delivers this without a different programming model — it's the same DataFrame API applied to streams. AQE matters because Catalyst's static optimizer operates on estimates, not facts: it guesses table sizes and partition distributions before execution. AQE corrects those guesses at runtime, automatically coalescing tiny shuffle partitions, switching join strategies based on actual data sizes, and handling skewed joins without manual salting. Understanding both systems completes the Spark engineer's toolkit.</p>
</div>

<div class="topic">
<h2>Structured Streaming: Treating Streams as Bounded Data</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Instead of thinking about a stream as an infinite river of events, Structured Streaming treats it as a very large table that keeps getting new rows appended to it. Every N seconds, Spark takes the new rows that arrived since last time, processes them as a micro-batch (a small, time-bounded slice of the incoming stream processed as a regular batch job), and writes results. You write the same DataFrame query you'd write for batch data — Spark handles the continuous execution loop.</p>
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
    <tr><td>Fixed interval (e.g., 1 minute)</td><td>Process every N minutes regardless of data availability; skips if previous batch still running (for example, if the 1-minute batch takes 90 seconds, the trigger at minute 2 is skipped entirely — the next batch fires at minute 3)</td><td>Time-aligned reporting; predictable schedules</td></tr>
    <tr><td>One-time (deprecated, Spark 3.3)</td><td>Process all available data in a single micro-batch, then stop</td><td>Replaced by available-now; see note below</td></tr>
    <tr><td>Available-now (Spark 3.3+)</td><td>Process all currently available data in <em>multiple</em> batches (up to maxFilesPerTrigger at a time), then stop</td><td>Replaces one-time; safe for large backlogs; incremental batch processing</td></tr>
    <tr><td>Continuous processing (Spark 2.3+)</td><td>Sub-millisecond latency; limited operations; at-least-once semantics</td><td>Ultra-low latency with reduced guarantees</td></tr>
  </tbody>
</table>
</div>

<div class="box f"><div class="box-lbl">Why One-Time Trigger Was Deprecated — The Single-Batch OOM Risk</div>
<p>The <code>Trigger.Once()</code> trigger processes <em>all</em> currently available data in a <strong>single micro-batch</strong> before stopping. If the stream has been offline for hours or days and a large backlog has accumulated — say, 500 GB of unprocessed data — the single-batch approach forces Spark to process the entire 500 GB in one query execution. This creates OOM (Out of Memory — when a program tries to use more memory than the computer has available, it crashes) risk: the entire backlog's shuffle data must be held in executor memory within a single batch, with no opportunity to release resources between batches.</p>
<p><strong>Available-now</strong> (<code>Trigger.AvailableNow()</code>, Spark 3.3+) solves this by spreading the backlog across <em>multiple</em> micro-batches (bounded by <code>maxFilesPerTrigger</code> per batch), still stopping when all available data is consumed. Each micro-batch processes a manageable chunk of data, releases its resources, and begins the next batch. The result: large backlogs are processed safely and incrementally without OOM risk, while still completing automatically when caught up — giving the best of batch and streaming behavior. This is why available-now is the correct replacement for the deprecated one-time trigger.</p>
</div>
</div>

<div class="topic">
<h2>Output Modes: Append, Complete, and Update</h2>

<p>Structured Streaming's output modes define what data is written to the sink (the destination system where Spark writes streaming results — for example, a Kafka topic, a Delta table, or a database) on each trigger:</p>

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

<div class="box n"><div class="box-lbl">Why Complete Mode Is Not Allowed for Simple Transformations</div>
<p>Complete mode writes the entire result table on every trigger — but "entire result table" only has a well-defined meaning when there is an aggregation. For a simple transformation like <code>filter()</code>, there is no aggregation result to rewrite; Spark has no mechanism to determine which prior rows belong in the complete output. Complete mode requires an aggregation to be meaningful, which is why it is forbidden for non-aggregated queries.</p>
</div>
</div>

<div class="topic">
<h2>Watermarks: Handling Late-Arriving Events</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Real-world events don't arrive in order. A mobile app event recorded at 10:00 AM might not reach Kafka until 10:15 AM due to network delays or offline buffering. A watermark tells Spark: "Events can arrive up to N minutes late. Wait that long before closing a time window. Events that arrive more than N minutes late will be dropped." Watermarks let Spark bound how much state it must keep in memory.</p>
</div>

<p>Without watermarks, Spark must keep all intermediate state in memory forever. State here refers to the partial aggregation result for each open time window — for example, the running count of events for the [10:00, 11:00) window. Because a late event from an hour ago could theoretically arrive at any time and change an old window's result, Spark cannot discard any window's state. This is unbounded state growth, which eventually causes OOM.</p>

<p>A watermark of 10 minutes means: Spark tracks the highest event_time it has ever processed across all prior micro-batches — that value is <code>max(event_time_seen)</code>. The current watermark is <code>max(event_time_seen) - 10 minutes</code>. Events with event_time &lt; watermark are considered late and dropped. Windows whose end time is before the watermark are considered complete and their state can be freed from memory.</p>

<p><strong>Watermarks enable Append output mode for aggregations:</strong> Once a window is closed (its end time &lt; watermark), its result can never change (no more late events will be accepted). It's safe to append this result to the output. Without a watermark, Spark cannot guarantee a window's result is final, so Append mode is disallowed for aggregations.</p>

<div class="box f"><div class="box-lbl">Late Event Handling with Watermarks — Concrete Example</div>
<p>Query: <code>df.withWatermark("event_time", "10 minutes").groupBy(window("event_time", "1 hour")).count()</code></p>
<p>Scenario: current max event_time seen = 11:05 AM. Watermark = 11:05 - 10min = 10:55 AM.</p>
<p>An event with event_time = 10:40 AM arrives. Is it accepted? Window [10:00, 11:00] ends at 11:00 AM &gt; watermark 10:55 AM — window is still open. The 10:40 AM event is 25 minutes late but within the 10-minute watermark? No — 10:40 AM &lt; watermark 10:55 AM. <strong>The event is dropped.</strong></p>
<p>An event with event_time = 11:00 AM arrives. 11:00 AM &gt; watermark 10:55 AM. <strong>The event is accepted</strong> and added to the [11:00, 12:00] window.</p>
</div>

<div class="sketch">
<svg viewBox="0 0 700 190" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.4" stroke-linecap="round">
    <path d="M30 100 L670 100" stroke-width="2.8" marker-end="url(#arr)"/>
  </g>
  <line x1="600" y1="70" x2="600" y2="130" stroke="#dc2626" stroke-width="2.4" stroke-dasharray="6 4"/>
  <text x="600" y="60" text-anchor="middle" font-size="14" font-weight="700" fill="#dc2626">watermark = 10:55</text>
  <circle cx="230" cy="100" r="9" fill="#fecaca" stroke="#dc2626" stroke-width="2.2"/>
  <circle cx="470" cy="100" r="9" fill="#dcfce7" stroke="#16a34a" stroke-width="2.2"/>
  <text x="230" y="128" text-anchor="middle" font-size="13.5" fill="#7f1d1d">10:40 event</text>
  <text x="230" y="146" text-anchor="middle" font-size="16" font-weight="700" fill="#dc2626">DROPPED — too late</text>
  <text x="470" y="128" text-anchor="middle" font-size="13.5" fill="#14532d">11:00 event</text>
  <text x="470" y="146" text-anchor="middle" font-size="16" font-weight="700" fill="#16a34a">ACCEPTED — new window</text>
  <text x="350" y="180" text-anchor="middle" font-size="13" fill="#44446a">anything left of the line is closed forever; state for it is freed</text>
</svg>
</div>
<div class="sketch-cap">Diagram: a timeline with the current watermark marked as a red dashed line. An event from before the line (10:40) is dropped as too late; an event at or after the line (11:00) is accepted into a fresh window.</div>

<div class="scribble">a watermark is basically Spark saying "I'll wait for stragglers, but not forever." Without one, it has to keep EVERY window's state alive in case a message from last Tuesday shows up. <span class="who">— Alex, margin note</span></div>

<h3>Window Types</h3>
<ul>
  <li><strong>Tumbling windows:</strong> Fixed-size, non-overlapping. <code>window("event_time", "1 hour")</code> — events belong to exactly one window: [0:00–1:00), [1:00–2:00), etc.</li>
  <li><strong>Sliding windows:</strong> Fixed-size, overlapping. <code>window("event_time", "1 hour", "15 minutes")</code> — 1-hour windows starting every 15 minutes. Each event belongs to multiple overlapping windows.</li>
  <li><strong>Session windows (Spark 3.2+):</strong> Variable-length, defined by inactivity gap. A session groups events with gaps smaller than the timeout; a new session starts after the timeout expires. For example, a 5-minute session window would group together clicks at 10:01, 10:03, and 10:06 into one session, then start a new session when the next click arrives at 10:15 — because the 9-minute gap exceeds the timeout.</li>
</ul>

<div class="box n"><div class="box-lbl">Worked Example: State Cost of Sliding vs Tumbling Windows</div>
<p>With <code>window("event_time", "1 hour")</code> (tumbling), one event at 10:20 belongs to exactly <strong>one</strong> open window — [10:00, 11:00) — so Spark maintains exactly one aggregation state entry for it. With <code>window("event_time", "1 hour", "15 minutes")</code> (sliding), the same event at 10:20 falls inside <strong>four</strong> overlapping 1-hour windows simultaneously: [9:30,10:30), [9:45,10:45), [10:00,11:00), [10:15,11:15). Spark must update all four windows' state on every micro-batch that touches this event. General rule: a sliding window of size <code>W</code> with slide interval <code>S</code> keeps <code>W / S</code> windows concurrently open per event — here 60min / 15min = 4×. State memory therefore scales roughly linearly with <code>W/S</code>: doubling the overlap (slide of 7.5 min instead of 15) doubles the concurrent windows to 8, and doubles the state store's memory footprint for the same input volume.</p>
</div>

<div class="sketch">
<svg viewBox="0 0 700 200" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.2" stroke-linecap="round">
    <path d="M30 170 L670 170" stroke-width="2.6" marker-end="url(#arr)"/>
  </g>
  <rect x="220" y="30" width="140" height="16" fill="#dbeafe" stroke="#1e3a8a" stroke-width="1.6"/>
  <text x="290" y="20" text-anchor="middle" font-size="12" fill="#1e3a8a">tumbling: 1 window</text>
  <circle cx="290" cy="170" r="7" fill="#fecaca" stroke="#dc2626" stroke-width="2"/>
  <text x="290" y="192" text-anchor="middle" font-size="12" fill="#7f1d1d">event @ 10:20</text>
  <g stroke="#16a34a" stroke-width="2" fill="#dcfce7" opacity="0.85">
    <rect x="130" y="60" width="140" height="14"/>
    <rect x="165" y="78" width="140" height="14"/>
    <rect x="200" y="96" width="140" height="14"/>
    <rect x="235" y="114" width="140" height="14"/>
  </g>
  <text x="490" y="70" font-size="12" fill="#14532d">4 windows open</text>
  <text x="490" y="88" font-size="12" fill="#14532d">at once for the</text>
  <text x="490" y="106" font-size="12" fill="#14532d">SAME event —</text>
  <text x="490" y="124" font-size="12" fill="#14532d" font-weight="700">sliding, 15min step</text>
  <text x="350" y="10" text-anchor="middle" font-size="14" fill="#44446a">W / S = concurrent windows per event (here: 60min / 15min = 4×)</text>
</svg>
</div>
<div class="sketch-cap">Diagram: one event at 10:20 belongs to exactly one tumbling window (top bar), but to four overlapping sliding windows simultaneously (stacked green bars) — each one needs its own state entry updated.</div>

<div class="scribble">tumbling windows are lockers — one item, one locker. Sliding windows are more like sticky notes on a shared board — the same event gets copied onto every overlapping note, and Spark has to update all of them. <span class="who">— Alex, margin note</span></div>
</div>

<div class="topic">
<h2>AQE: Adaptive Query Execution (Spark 3.0, 2020)</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Catalyst picks a query plan before execution starts, based on statistics estimates that may be wrong. AQE lets Spark pause after each shuffle stage, look at the actual data sizes and distributions it just produced, and re-optimize the next stage's plan based on facts instead of estimates. Three specific problems it fixes: too many shuffle partitions, wrong join strategy choice, and data skew in joins.</p>
</div>

<p>Apache Spark 3.0 (released 2020) introduced Adaptive Query Execution (AQE) as a way to extend Catalyst optimization into runtime. The key insight: shuffle stages create a natural pause point. Every exchange (shuffle) operator forces all tasks in the current stage to complete before the next stage can begin. During this pause, the actual shuffle output statistics are available: how many bytes in each partition, how many rows, how the data distributes across partitions. AQE collects these statistics and re-runs the physical planner for the next stage.</p>

<div class="sketch">
<svg viewBox="0 0 700 180" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.4" stroke-linecap="round">
    <rect x="20"  y="46" width="160" height="80" rx="10" fill="#eff6ff"/>
    <rect x="270" y="46" width="160" height="80" rx="10" fill="#fef9c3"/>
    <rect x="520" y="46" width="160" height="80" rx="10" fill="#dcfce7"/>
    <path d="M184 86 L266 86" marker-end="url(#arr)"/>
    <path d="M434 86 L516 86" marker-end="url(#arr)"/>
  </g>
  <path d="M225 46 C225 20, 275 20, 275 46" fill="none" stroke="#ca8a04" stroke-width="2.2" marker-end="url(#arr)"/>
  <text x="100" y="34" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">Catalyst plans</text>
  <text x="100" y="76" text-anchor="middle" font-size="13" fill="#1e3a8a">using ESTIMATES</text>
  <text x="100" y="94" text-anchor="middle" font-size="13" fill="#1e3a8a">(may be stale/wrong)</text>
  <text x="350" y="20" text-anchor="middle" font-size="13" fill="#92400e">stage completes → real stats exist!</text>
  <text x="350" y="76" text-anchor="middle" font-size="15" font-weight="700" fill="#92400e">SHUFFLE happens</text>
  <text x="350" y="94" text-anchor="middle" font-size="13" fill="#92400e">(natural pause point)</text>
  <text x="600" y="34" text-anchor="middle" font-size="15" font-weight="700" fill="#14532d">AQE re-plans</text>
  <text x="600" y="76" text-anchor="middle" font-size="13" fill="#14532d">coalesce · switch join</text>
  <text x="600" y="94" text-anchor="middle" font-size="13" fill="#14532d">· split skewed part.</text>
  <text x="350" y="150" text-anchor="middle" font-size="15" fill="#16a34a" font-weight="700">every shuffle boundary is a free re-optimization checkpoint</text>
  <text x="350" y="170" text-anchor="middle" font-size="13" fill="#44446a">Catalyst can't do this — the real numbers don't exist until the stage finishes</text>
</svg>
</div>
<div class="sketch-cap">Diagram: Catalyst plans a stage using estimates, the shuffle at the stage boundary produces real statistics, and AQE uses those real numbers to re-plan the next stage — coalescing partitions, switching join strategy, or splitting a skewed one.</div>

<div class="scribble">AQE isn't a new optimizer — it's Catalyst getting a second try with the answer key. Every shuffle is a checkpoint where guesses become facts. <span class="who">— Alex, margin note</span></div>

<p>The unit of AQE re-optimization is the <strong>query stage</strong>. Each Exchange operator (Spark's internal name for a shuffle node in the physical plan — the point where data is redistributed across partitions, forcing all upstream tasks to finish before downstream tasks begin; a query stage corresponds exactly to one stage in the DAG (Directed Acyclic Graph — a diagram of the steps in a computation where arrows show dependencies and nothing loops back) between two Exchange boundaries) creates a query stage boundary. AQE collects statistics after each query stage completes, then re-optimizes the next query stage's plan before it begins executing.</p>

<h3>AQE Feature 1 — Coalescing Shuffle Partitions</h3>
<p><strong>Problem:</strong> <code>spark.sql.shuffle.partitions = 200</code> by default. For a query producing 10MB of shuffle output, 200 partitions means each partition averages 50KB — hundreds of tiny tasks that spend more time on task scheduling overhead than actual computation.</p>
<p><strong>AQE solution:</strong> After the shuffle stage completes, AQE inspects the actual partition sizes. If most partitions are tiny, AQE coalesces adjacent small partitions (adjacent here means consecutive by partition number — AQE merges partition 3 + 4 + 5 if all three are undersized, not arbitrary small partitions from across the range) into fewer, larger ones before the next stage reads them. A 200-partition shuffle producing 10MB of data might be coalesced by AQE into 5 partitions of 2MB each — 40× fewer tasks, each with meaningful work.</p>
<p><strong>Configuration:</strong> <code>spark.sql.adaptive.coalescePartitions.enabled = true</code> (default in Spark 3.0+). Target partition size: <code>spark.sql.adaptive.advisoryPartitionSizeInBytes</code> (default 64MB).</p>

<h3>AQE Feature 2 — Dynamic Join Strategy Switching</h3>
<p><strong>Problem:</strong> Catalyst chooses a join strategy (SMJ, SHJ, BHJ) based on estimated table sizes from statistics that may be stale, absent, or wrong. A table estimated at 100MB may actually produce only 1MB of shuffle output after filtering. Catalyst chose SMJ (correct for 100MB); AQE at runtime sees 1MB and switches to BHJ.</p>
<p><strong>AQE solution:</strong> After stage 1 (reading and filtering one side of the join) completes, AQE sees the actual shuffle output size. If it's below the broadcast threshold, AQE switches the join strategy from SMJ to BHJ for stage 2 — without re-planning the entire query, just the next stage. This eliminates an unnecessary shuffle of the smaller table.</p>
<p><strong>Why Catalyst can't do this at planning time:</strong> Before execution starts, the 1MB result doesn't exist yet — it's produced by a filter applied at execution time. Catalyst had only the pre-filter table size estimate. AQE has post-filter actual sizes.</p>

<h3>AQE Feature 3 — Skew Join Handling</h3>
<p><strong>Problem:</strong> One shuffle partition is 100× larger than others due to data skew. One task processes 80% of the data; all other tasks finish in 5 seconds; this one task runs for 15 minutes. The stage waits for it.</p>
<p><strong>AQE solution:</strong> AQE detects skewed partitions by comparing each partition's size against the stage's median partition size (with configurable thresholds). For each skewed partition, AQE:</p>
<ol>
  <li>Splits the skewed partition into N sub-partitions. For example, if partition 7 is 2GB and the target is 64MB, AQE splits it into ~32 sub-partitions of ~64MB each (each sub-partition reads a range of the original shuffle files).</li>
  <li>Replicates the corresponding partition from the other join side N times — because each of the 32 sub-partitions of table A's partition 7 still needs to join against the same matching rows from table B, Spark creates 32 copies of those B rows, one per sub-task.</li>
  <li>Runs N parallel join tasks instead of 1 massive task — 32 × 64MB tasks instead of 1 × 2GB task.</li>
</ol>
<p>This is automatic — no salting, no code changes required. <code>spark.sql.adaptive.skewJoin.enabled = true</code> (default in Spark 3.0+). Threshold: <code>spark.sql.adaptive.skewJoin.skewedPartitionFactor</code> (default 5) and <code>spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes</code> (default 256MB).</p>

<div class="box f"><div class="box-lbl">Why BHJ on a Skewed Probe Side Creates a CPU/Memory Hotspot — and Why SMJ with AQE Is Safer</div>
<p>AQE Feature 2 can dynamically switch a join from SMJ to BHJ when the build side is small. This switch is almost always beneficial for uniformly-distributed data — but it can backfire when the <strong>probe side is skewed</strong>.</p>
<p><strong>How BHJ handles skew:</strong> Recall from Ch3: in a hash join, the <em>build side</em> is the smaller table loaded into a hash table in memory; the <em>probe side</em> is the larger table whose rows are looked up in that hash table. In BHJ, the build table is broadcast as a complete copy to <em>every</em> executor. Then each executor processes its partition of the probe (large) table, looking up each probe row in the local hash table. If the probe side has a skewed key — say, key <code>"category_X"</code> appears in 40% of probe rows — then the executor holding that skewed probe partition must process 40% of all rows. Every matching probe row still triggers a lookup in the broadcast hash table, consuming CPU proportional to the number of hits. The result: one executor is overwhelmed with CPU and memory pressure from the disproportionate probe workload while all other executors finish quickly. This is a <strong>CPU/memory hotspot</strong> caused by probe-side skew, not by the broadcast table itself.</p>
<p><strong>Why SMJ with AQE skew-join handling is safer on skewed data:</strong> SMJ shuffles both sides by join key. A skewed probe partition ends up in one shuffle partition — which AQE then detects as oversized (larger than median × skewedPartitionFactor). AQE's skew-join feature automatically splits this oversized probe partition into multiple sub-partitions and replicates the matching portion of the build side for each sub-partition. The skewed load is spread across multiple parallel tasks. BHJ — once the broadcast is sent — has no mechanism to redistribute a skewed probe partition: the probe is read directly from its source, and a skewed partition just means one executor gets far more work. AQE's dynamic join switching prefers BHJ for smaller build sides, but if you know the probe side is severely skewed, forcing SMJ (via <code>/*+ MERGE */</code> hint) and letting AQE handle skew in the SMJ path is often the safer choice.</p>
</div>

<div class="box n"><div class="box-lbl">AQE's Three Features — Summary</div>
<table>
  <thead><tr><th>Feature</th><th>Problem Fixed</th><th>How It Works</th><th>Manual Alternative</th></tr></thead>
  <tbody>
    <tr><td>Coalesce shuffle partitions</td><td>200 tiny partitions for small data</td><td>After shuffle: merge adjacent small partitions</td><td>Tune spark.sql.shuffle.partitions manually</td></tr>
    <tr><td>Dynamic join switching</td><td>Wrong join strategy from stale estimates</td><td>After stage 1: check actual size, switch to BHJ if small</td><td>Manually broadcast hint; requires knowing sizes in advance</td></tr>
    <tr><td>Skew join handling</td><td>One task processes 80% of data</td><td>After shuffle: split skewed partitions; replicate other side</td><td>Salting — a manual workaround where you add a random prefix to skewed keys to spread them across more partitions, then remove the prefix after joining; requires explicit code changes (manual key prefix + non-skewed side replication)</td></tr>
  </tbody>
</table>
</div>

<h3>AQE + Structured Streaming</h3>
<p>AQE re-optimization applies within each micro-batch independently. Each micro-batch is a complete Spark SQL query with its own query stages. AQE collects statistics and re-optimizes within each micro-batch. Since micro-batches are short (seconds to minutes), the AQE overhead (collecting stage statistics) is a small fraction of total batch time.</p>
</div>

<div class="bigfacts">
<div class="bigfacts-head">If you forget everything else in this chapter, keep these three:</div>
<div class="bigfact"><span class="n">1.</span>A stream is just a table that keeps growing. Same DataFrame API, no new API to learn.</div>
<div class="bigfact"><span class="n">2.</span>A watermark trades "wait for stragglers" against "stop state from growing forever."</div>
<div class="bigfact"><span class="n">3.</span>AQE = Catalyst's Phase 3 re-run after every shuffle, with real numbers instead of guesses.</div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#666680" stroke-width="2.4" stroke-linecap="round">
    <ellipse cx="350" cy="150" rx="86" ry="34" fill="#f8f8fc" stroke="#1c1c2e" stroke-width="3"/>
    <rect x="26"  y="18"  width="204" height="86" rx="12" fill="#fff"/>
    <rect x="472" y="16"  width="202" height="98" rx="12" fill="#fff"/>
    <rect x="18"  y="210" width="204" height="84" rx="12" fill="#fff"/>
    <rect x="478" y="212" width="196" height="82" rx="12" fill="#fff"/>
    <path d="M272 128 C230 108, 204 96, 198 96" marker-end="url(#arr)"/>
    <path d="M428 130 C462 110, 486 98, 498 98" marker-end="url(#arr)"/>
    <path d="M282 176 C238 198, 212 208, 196 216" marker-end="url(#arr)"/>
    <path d="M418 174 C456 196, 482 206, 506 214" marker-end="url(#arr)"/>
  </g>
  <text x="350" y="146" text-anchor="middle" font-size="18" font-weight="700" fill="#1c1c2e">STREAM = ______</text>
  <text x="350" y="168" text-anchor="middle" font-size="13.5" fill="#666680">that keeps growing</text>
  <text x="128" y="42"  text-anchor="middle" font-size="15" font-weight="700" fill="#666680">MICRO-______</text>
  <text x="128" y="62"  text-anchor="middle" font-size="13.5" fill="#666680">same _________ API</text>
  <text x="570" y="40"  text-anchor="middle" font-size="15" font-weight="700" fill="#666680">WATERMARKS</text>
  <text x="570" y="60"  text-anchor="middle" font-size="13.5" fill="#666680">how ____ is too late</text>
  <text x="570" y="76"  text-anchor="middle" font-size="13.5" fill="#666680">bounds memory _____</text>
  <text x="120" y="238" text-anchor="middle" font-size="15" font-weight="700" fill="#666680">AQE = _______ v2</text>
  <text x="120" y="258" text-anchor="middle" font-size="13.5" fill="#666680">re-plans after each ________</text>
  <text x="576" y="240" text-anchor="middle" font-size="15" font-weight="700" fill="#666680">AQE'S 3 FIXES</text>
  <text x="576" y="260" text-anchor="middle" font-size="13.5" fill="#666680">________ · switch join ·</text>
  <text x="576" y="276" text-anchor="middle" font-size="13.5" fill="#666680">split ______ partitions</text>
</svg>
</div>
<div class="retrieval-note">✍️ Close the chapter and redraw this map from memory, saying every blank OUT LOUD — then flip back and check. Recall, not recognition. This is the last chapter — try redrawing Ch1-4's maps too before you stop.</div>

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
