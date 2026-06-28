#!/usr/bin/env python3
"""
Database Internals: A Complete Reference for the Aspiring Architect
Phase 1 — Storage Foundations
Run: python3 scripts/generate_learning_pack.py
Then: chrome --headless --print-to-pdf=output/ben_dicken_phase1.pdf output/ben_dicken_phase1.html
"""
import os
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
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
"""

# ─────────────────────────────────────────────────────────────────────────────
# COVER
# ─────────────────────────────────────────────────────────────────────────────
COVER = """
<div class="cover">
  <div class="eyebrow">Ben Dicken · Architect's Lens · Phase 1</div>
  <h1>Database Internals</h1>
  <div class="sub">A Complete Reference for the Aspiring Architect</div>
  <div class="rule"></div>
  <div class="cover-desc">
    Five foundational topics explained at full architectural depth — from the physics of storage media
    to the internals of production database engines. Every decision framework, failure mode, tuning
    parameter, and cross-system connection you need to design, debate, build, and teach database
    architecture at any level — from a first-year student to a 50-year systems veteran.
  </div>
  <div class="toc-head">Contents — Phase 1: Storage Foundations</div>
  <div class="ti"><span class="ti-n">01</span><span class="ti-t">How Storage Devices Work</span><span class="ti-s">HDD · SSD · NVMe · Page Abstraction · I/O Cost Model</span></div>
  <div class="ti"><span class="ti-n">02</span><span class="ti-t">The Full Software + Hardware Stack</span><span class="ti-s">Kernel · System Calls · io_uring · Memory Hierarchy · mmap</span></div>
  <div class="ti"><span class="ti-n">03</span><span class="ti-t">Data Organisation: The Read-Write Trade-off</span><span class="ti-s">B+ Trees · LSM Trees · Hash Indexes · Three Amplifications</span></div>
  <div class="ti"><span class="ti-n">04</span><span class="ti-t">The Cell Layout: How a Database Page Works</span><span class="ti-s">Slotted Pages · HOT Updates · TOAST · VACUUM · Fill Factor</span></div>
  <div class="ti"><span class="ti-n">05</span><span class="ti-t">The 5 Core Components of a Storage Engine</span><span class="ti-s">ACID · MVCC · WAL · Buffer Pool · Locks · ARIES Recovery</span></div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 1: STORAGE DEVICES
# ─────────────────────────────────────────────────────────────────────────────
CH1 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 1 of 5</div>
  <h1>How Storage Devices Work</h1>
  <div class="ch-src">Source: Hard Drives, SSDs, and Tape Storage</div>
  <p class="ch-sum">Every database design decision traces back to one physical reality: how data is stored on disk and what it costs to access it. Master the I/O cost model here and every subsequent design choice — B+ trees, WAL, buffer pools, VACUUM — becomes obvious rather than arbitrary.</p>
</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>Every performance problem you will ever debug in a database traces back to one root cause: someone made a decision without understanding the I/O cost model. When a query that should take 2ms takes 2 seconds, when a table that should be 5GB is 50GB, when a perfectly written index makes zero difference — the answer is always in the physics of how data moves between storage and CPU. This chapter gives you the mental model that makes every subsequent design decision derivable instead of memorised.</p>
</div>

<div class="topic">
<h2>The Page Abstraction: The Foundation of All Database Design</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>You can't pick up a single grain of sand — you scoop a handful. Storage devices work the same way: they can never read or write a single byte in isolation. The device always moves a fixed-size chunk called a <strong>page</strong>. Everything in database design flows from this one physical constraint.</p></div>

<div class="box n"><div class="box-lbl">WHY Storage Devices Use Pages — The Hardware Rationale</div>
<p>The page (block) abstraction is not a software convenience — it is a physical constraint imposed by three independent hardware realities:</p>
<ul>
  <li><strong>Magnetic HDDs: track geometry.</strong> A hard disk stores data in concentric circular tracks. The read head can only read an entire sector at once — typically 512 bytes (legacy) or 4KB (Advanced Format). Reading less than one sector is physically impossible: the magnetic head reads continuously as the platter rotates. The OS groups multiple sectors into a page for efficiency.</li>
  <li><strong>NAND Flash: wordline architecture.</strong> Flash cells are arranged in arrays sharing wordlines (row select lines). A single wordline activates an entire row of cells simultaneously — typically 4–16KB. You cannot read one cell without reading its entire row. This is a fundamental property of the NAND flash array circuit, not a design choice.</li>
  <li><strong>Error Detection and Correction (ECC): block granularity.</strong> Every storage device computes ECC codes over each block of data to detect and correct bit errors. Computing ECC per byte would be prohibitively expensive in silicon area and latency. Computing it per 4KB block amortises the ECC overhead (typically 512 bytes of ECC per 4KB of data) to an acceptable ~12% overhead. This ECC block size directly determines the minimum I/O unit.</li>
</ul>
<p>These three hardware constraints — track geometry, wordline architecture, ECC block size — all independently converge on the same conclusion: the minimum unit of storage device I/O is a fixed-size block (page). This is why the page abstraction appears identically in every storage technology from magnetic tapes (1950s) to NVMe SSDs (2010s) to future 3D XPoint memory.</p>
</div>

<p>Storage devices do not operate on individual bytes. They operate on <strong>pages</strong> — fixed-size blocks that are the minimum unit of I/O. This is not a software convention: it is a physical property of every storage medium ever built. Magnetic tapes, hard disks, solid-state drives, and even RAM (via 64-byte cache lines) all operate on fixed-size blocks.</p>

<p>The practical implication is profound. If you want to read a single byte at offset 1000 in a file, the storage device reads the entire page containing that byte — typically 4KB to 16KB of data — and returns it to the CPU. You pay the same I/O cost whether you needed 1 byte or the full page. This is the source of <strong>read amplification</strong>: a 100-byte row in an 8KB page means you paid 8,192 bytes of I/O to retrieve 100 bytes — 81× amplification.</p>

<p>This constraint drives every core database design decision:</p>
<ul>
  <li><strong>B+ tree node size = one page</strong> — traversing one tree level costs exactly one I/O operation</li>
  <li><strong>Buffer pool caches entire pages</strong> — caching partial pages would waste the I/O already paid</li>
  <li><strong>Write-Ahead Log is append-only sequential</strong> — avoids the random I/O cost on every commit</li>
  <li><strong>VACUUM reclaims whole pages</strong> — byte-level fragmentation is invisible; only page-level waste matters</li>
  <li><strong>Clustered indexes store related rows on the same page</strong> — so one I/O fetches multiple needed rows</li>
</ul>

<div class="box n"><div class="box-lbl">Why B+ Tree Nodes Are Exactly One Page — The Core Insight</div>
<p>This is not a coincidence. It is the foundational design decision that makes B+ trees viable on disk.</p>
<p>A disk read always transfers exactly one page — no more, no less. So if a B+ tree node fits exactly one page:</p>
<ul>
  <li><strong>One node traversal = one I/O operation.</strong> Reading a node costs exactly what you already paid to access any byte on that page.</li>
  <li><strong>If the node were smaller than a page</strong> (e.g., 512 bytes in an 8KB page), you'd waste 15× the I/O bandwidth — paying for 8KB but only using 512 bytes of tree data.</li>
  <li><strong>If the node were larger than a page</strong> (e.g., 32KB spanning 4 pages), a single node traversal costs 4 I/Os instead of 1 — compounding across every level of the tree.</li>
</ul>
<p><strong>This is not a coincidence — it is the ORIGINAL DESIGN MOTIVATION.</strong> When Rudolf Bayer and Edward McCreight invented B-trees at Boeing in 1972, the question they were answering was: <em>"Given that disk reads always return a fixed-size page, how do you design a search tree that minimises page I/Os per lookup?"</em> Their answer: make each tree node exactly one page. Every subsequent B-tree property — sorted keys for binary search within a node, high fanout, balanced height, leaf-only values in B+ trees — follows from this single constraint. Binary search trees predated B-trees but were designed for RAM. B-trees were designed FROM SCRATCH for page-based disk I/O. The node = page equivalence is not incidental to B-tree design; it IS B-tree design.</p>
</div>

<div class="box n"><div class="box-lbl">Page Sizes Across Systems</div>
<table>
  <thead><tr><th>System</th><th>Page Size</th><th>Why This Size</th></tr></thead>
  <tbody>
    <tr><td>Linux / macOS / Windows (OS)</td><td>4 KB</td><td>Matches x86-64 virtual memory page; hardware MMU granularity</td></tr>
    <tr><td>PostgreSQL (default)</td><td>8 KB</td><td>Compile-time constant; 2× OS page reduces syscall overhead while staying cache-line friendly</td></tr>
    <tr><td>MySQL InnoDB (default)</td><td>16 KB</td><td>Higher sequential I/O efficiency; configurable 4KB–64KB</td></tr>
    <tr><td>SQLite</td><td>4 KB</td><td>Matches OS page; relies on kernel mmap rather than a separate buffer pool</td></tr>
    <tr><td>Oracle (default)</td><td>8 KB</td><td>Configurable; can have multiple buffer pools with different page sizes</td></tr>
    <tr><td>SQL Server</td><td>8 KB</td><td>Fixed; not configurable</td></tr>
  </tbody>
</table>
</div>

<p><strong>Why not use a 1MB page?</strong> Larger pages reduce I/O operation count for sequential scans but increase read amplification for point reads. A 1MB page means every single-row lookup pulls 1MB off disk. Typical web application queries are 90% point reads or small range scans — 8KB is the empirically validated sweet spot for mixed OLTP workloads. Analytics databases (Redshift, BigQuery) use column-oriented layouts with large blocks (1MB+) because their workload is pure sequential scan.</p>
</div>

<div class="topic">
<h2>Hard Disk Drives (HDD)</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>An HDD is like a vinyl record player. Data is stored on magnetic tracks on spinning platters. A read arm physically moves to the right track, then waits for the right sector to rotate under it. This mechanical movement — 5 to 10 milliseconds — is the bottleneck. No amount of software engineering eliminates physics.</p></div>

<p>A hard disk drive has one or more <strong>platters</strong> — circular disks coated in magnetic material where bits are stored as north/south magnetic orientations. The platters spin continuously (7,200 RPM for typical server drives, 15,000 RPM for high-performance enterprise drives). A <strong>read/write arm</strong> with an electromagnetic head floats nanometers above the platter surface, reading and writing bits as they rotate underneath.</p>

<h3>The Three Components of HDD Latency</h3>

<p><strong>1. Seek time</strong> — the time to physically move the arm from its current track to the target track. This is the dominant cost for random I/O. Full-stroke seek (innermost to outermost track): 15–20ms. Average seek (one-third of full stroke, the statistical average for random access): 5–9ms. Adjacent-track seek: &lt;1ms.</p>

<p><strong>2. Rotational latency</strong> — after the arm reaches the right track, it waits for the target sector to spin around to the head. At 7,200 RPM, one full rotation = 60/7200 = 8.33ms. Average rotational latency = half a rotation = 4.17ms. Best case: 0ms (you get lucky). Worst case: 8.33ms (almost a full rotation).</p>

<p><strong>3. Transfer time</strong> — the time to read the actual data once the head is positioned. Sequential data flows past the head at 100–200 MB/s. For a 4KB page: 4096 / 150,000,000 = 0.027ms. Negligible compared to seek and rotational latency.</p>

<div class="box s"><div class="box-lbl">Why HDD Sequential Reads Are Fast — The Positive Mechanism</div>
<p>Random reads are slow because the arm must seek. Sequential reads are fast for the opposite reason: <strong>the arm does not move at all</strong>. Once positioned at the first sector, the platter continues rotating at 7,200 RPM. Each subsequent sector arrives at the stationary head automatically — driven by rotation. The arm simply reads the magnetic field as sectors stream past at ~150 MB/s, requiring no additional mechanical movement. This is the positive physical mechanism: <em>rotation delivers the data to the head</em>. The database gets to exploit this by storing related pages on adjacent tracks (clustered indexes, heap storage) so a single seek pays for thousands of sequential page reads.</p>
</div>

<div class="box n"><div class="box-lbl">HDD Latency Breakdown (7,200 RPM)</div>
<table>
  <thead><tr><th>Component</th><th>Best Case</th><th>Average</th><th>Worst Case</th></tr></thead>
  <tbody>
    <tr><td>Seek time</td><td>&lt;1ms</td><td>5–9ms</td><td>15–20ms</td></tr>
    <tr><td>Rotational latency</td><td>~0ms</td><td>4.2ms</td><td>8.3ms</td></tr>
    <tr><td>Transfer time (4KB)</td><td colspan="3">~0.03ms (negligible)</td></tr>
    <tr class="hr"><td><strong>Total random read</strong></td><td><strong>~1ms</strong></td><td><strong>~9–13ms</strong></td><td><strong>~28ms</strong></td></tr>
    <tr><td>Sequential read (after initial seek)</td><td colspan="3">~0.03ms per 4KB page (~150 MB/s)</td></tr>
    <tr><td>Random IOPS</td><td colspan="3">~75–120 IOPS (1000ms / 10ms average)</td></tr>
  </tbody>
</table>
</div>

<p><strong>Why this number matters:</strong> At 100 IOPS, a query touching 1,000 random pages takes 10 seconds. Those same 1,000 pages read sequentially (4MB total) at 150 MB/s takes 27ms — a 370× difference. This single number — 100 IOPS for random reads — is why database architectures exist. Every data structure, every caching layer, every write-ahead log is an engineering response to this physical constraint.</p>

<p><strong>RAID configurations</strong> multiply IOPS by adding spindles: RAID-10 with 8 drives gives ~800 IOPS random read. For write-heavy workloads, RAID-10 (mirroring + striping) outperforms RAID-5 (parity) because parity RAID reads old data + old parity before each write — 4 I/Os per logical write vs 2 for RAID-10.</p>
</div>

<div class="topic">
<h2>Solid State Drives (SSD)</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>An SSD stores data in flash memory cells — no moving parts, no spinning platters. Reading is nearly instant because there's no physical seek. But writing has a catch: you can't overwrite a flash cell directly. You must erase an entire block (containing hundreds of pages) before rewriting any part of it. This read/write asymmetry drives almost all SSD architecture decisions.</p></div>

<h3>NAND Flash Cell Types: The Density vs Durability Trade-off</h3>

<p>The fundamental storage unit is a NAND flash cell — a floating-gate transistor storing charge levels that represent bits. More charge levels per cell = more bits per cell = cheaper per GB, but also less reliable and slower.</p>

<div class="box n"><div class="box-lbl">Flash Cell Type Comparison</div>
<table>
  <thead><tr><th>Type</th><th>Bits/Cell</th><th>Endurance (P/E Cycles)</th><th>Read Latency</th><th>Cost/GB</th><th>Best For</th></tr></thead>
  <tbody>
    <tr><td><strong>SLC</strong> (Single-Level)</td><td>1</td><td class="g">100,000+</td><td class="g">25μs</td><td class="rd">Very high</td><td>Write-intensive enterprise (WAL devices)</td></tr>
    <tr><td><strong>MLC</strong> (Multi-Level)</td><td>2</td><td class="y">10,000</td><td class="y">50μs</td><td class="y">High</td><td>Enterprise mixed workloads</td></tr>
    <tr><td><strong>TLC</strong> (Triple-Level)</td><td>3</td><td class="rd">1,000–3,000</td><td>70–100μs</td><td class="g">Low</td><td>Consumer, read-heavy databases</td></tr>
    <tr><td><strong>QLC</strong> (Quad-Level)</td><td>4</td><td class="rd">100–1,000</td><td class="rd">130μs</td><td class="g">Very low</td><td>Cold storage, read-only archives</td></tr>
  </tbody>
</table>
</div>

<p><em>P/E cycle</em> = Program/Erase cycle — how many times a cell can be written and erased before becoming unreliable. A TLC consumer SSD under heavy database random-write workloads can wear out in months. Enterprise database servers use MLC or enterprise-grade TLC with larger over-provisioning reserves.</p>

<h3>Flash Hierarchy and the Erase Asymmetry</h3>

<p>NAND flash is organized in a strict hierarchy. Understanding this hierarchy explains write amplification and why SSD performance degrades under sustained writes:</p>
<ul>
  <li><strong>Page (4–16KB)</strong> — minimum unit of read and write. You can read or program (write) one page at a time, but only to a previously erased page.</li>
  <li><strong>Block (128–512 pages = 512KB–8MB)</strong> — minimum unit of erase. To overwrite any page in a block, you must first erase the entire block. This is the root of write amplification.</li>
  <li><strong>Plane</strong> — multiple blocks; enables parallel operations within one die.</li>
  <li><strong>Die</strong> — one silicon chip; typically 4–8 per SSD package.</li>
</ul>

<h3>The Flash Translation Layer (FTL)</h3>

<p>The FTL is firmware on the SSD controller that abstracts the erase-before-write constraint. The OS sees a simple block device with stable logical addresses; the FTL handles the complexity underneath:</p>
<ul>
  <li><strong>Logical-to-physical mapping:</strong> When the OS writes to logical address X, the FTL writes to a fresh physical page and updates the mapping table. The old physical page is marked stale — not immediately erased.</li>
  <li><strong>Wear leveling:</strong> Distributes writes evenly across all blocks so no single block wears out first. Dynamic wear leveling sends new writes to the least-worn free blocks. Static wear leveling periodically moves cold data from pristine blocks to worn ones, freeing pristine blocks for heavy write traffic.</li>
  <li><strong>Garbage collection:</strong> Periodically reads the live pages from partially-stale blocks, writes them to a fresh block, then erases the old block. Runs in the background but competes with foreground I/O — the source of SSD latency spikes under heavy write load.</li>
</ul>

<div class="box f"><div class="box-lbl">The SSD Write Cliff</div>
<p>A new SSD writes to pre-erased empty blocks — fast. As the drive fills, fewer empty blocks exist and garbage collection must run before writes can proceed. Under sustained write load at &gt;80% capacity, write throughput can drop to 20–30% of peak. This is the <strong>write cliff</strong>.</p>
<p><strong>Architectural rule:</strong> Provision SSDs for database WAL and data files at ≤70–75% capacity. Monitor with <code>iostat -xz 1</code> — watch <code>await</code> rising as the sign of GC pressure. Enterprise SSDs ship with 28–100% over-provisioning specifically to delay this cliff.</p>
</div>

<div class="box n"><div class="box-lbl">SSD Performance Numbers (SATA vs NVMe)</div>
<table>
  <thead><tr><th>Metric</th><th>SATA SSD</th><th>NVMe (PCIe 3.0)</th><th>NVMe (PCIe 4.0)</th></tr></thead>
  <tbody>
    <tr><td>Sequential read</td><td>~550 MB/s</td><td>~3,400 MB/s</td><td>~7,000 MB/s</td></tr>
    <tr><td>Sequential write</td><td>~520 MB/s</td><td>~3,000 MB/s</td><td>~6,500 MB/s</td></tr>
    <tr><td>Random read IOPS (4KB)</td><td>~80,000–100,000</td><td>~500,000</td><td>~800,000–1,000,000</td></tr>
    <tr><td>Random read latency</td><td>~80–100μs</td><td>~20–50μs</td><td>~15–30μs</td></tr>
    <tr><td>Command queues</td><td class="rd">1 queue / 32 cmds (AHCI)</td><td class="g">65,535 queues / 65,535 cmds</td><td class="g">65,535 queues</td></tr>
  </tbody>
</table>
</div>

<div class="mermaid">
graph LR
    R[Random Read Request]
    A[Seek Arm] --> B[Rotate Platter]
    B --> C[Transfer 4KB]
    D[Flash Controller] --> E[FTL Lookup]
    E --> F[Read Flash Page]
    R -->|HDD| A
    R -->|SSD| D
</div>
<p class="diagram-cap">Figure 1.2 — HDD requires sequential arm + rotation; SSD goes direct through controller.</p>

<p><strong>Why queue depth matters more than raw speed:</strong> A database server with 200 concurrent connections each issuing I/O will immediately saturate SATA's 32-command queue, forcing requests to wait in a software queue. NVMe's 65,535 queues allow all 200 connections to submit I/O simultaneously with no queuing overhead. This is why database IOPS on NVMe are 5–10× higher than SATA even though the sequential bandwidth ratio is only 6×.</p>

<div class="box f"><div class="box-lbl">SSD Failure Modes Architects Must Know</div>
<ul>
  <li><strong>Wear-out:</strong> TLC cells die after 1,000–3,000 P/E cycles. Monitor with <code>smartctl -a /dev/nvme0</code> — check "Percentage Used" (SMART attribute). At 100%, the drive may enter read-only mode.</li>
  <li><strong>Write cliff under high load:</strong> GC can't keep up with writes — average latency spikes from 50μs to 5ms+. Solution: over-provision + monitor utilization.</li>
  <li><strong>Power-loss data corruption:</strong> Consumer SSDs often lack capacitors to flush volatile write buffers on power loss. Enterprise SSDs have power-loss protection (PLP) capacitors. Never use consumer SSDs for database WAL without verifying PLP or using UPS.</li>
  <li><strong>Firmware bugs:</strong> SSD firmware is complex. Several high-profile firmware bugs have caused data corruption (Samsung 840 Evo, Intel 320 series). Run enterprise SSDs with validated firmware versions.</li>
</ul>
</div>
</div>

<div class="topic">
<h2>Sequential vs Random I/O: The Universal Law</h2>

<p>Regardless of storage medium — tape, HDD, SSD, NVMe — sequential access outperforms random access. The gap shrinks as technology advances but never disappears:</p>

<div class="box n"><div class="box-lbl">Sequential vs Random Read — All Storage Media</div>
<table>
  <thead><tr><th>Medium</th><th>Sequential Read</th><th>Random Read (4KB)</th><th>Seq/Rand Ratio</th><th>Physical Reason</th></tr></thead>
  <tbody>
    <tr><td>Magnetic Tape</td><td>~100 MB/s</td><td class="rd">Effectively 0</td><td class="rd">∞</td><td>Must physically wind/rewind — sequential only</td></tr>
    <tr><td>HDD (7,200 RPM)</td><td>~150 MB/s</td><td>~0.4 MB/s (100 IOPS)</td><td class="rd">~375×</td><td>Mechanical seek + rotational latency ~10ms each</td></tr>
    <tr><td>SATA SSD</td><td>~550 MB/s</td><td>~400 MB/s (100K IOPS)</td><td class="y">~1.4×</td><td>FTL overhead + AHCI queue depth limit</td></tr>
    <tr><td>NVMe SSD</td><td>~7,000 MB/s</td><td>~3,200 MB/s (800K IOPS)</td><td>~2.2×</td><td>Internal NAND parallelism; PCIe protocol overhead</td></tr>
    <tr><td>RAM</td><td>~50,000 MB/s</td><td>~15,000 MB/s</td><td>~3×</td><td>DRAM row activation + cache line / prefetch effects</td></tr>
  </tbody>
</table>
</div>

<div class="box f"><div class="box-lbl">Why 5× Sounds Fine But Tape Random Access Is Still Catastrophic</div>
<p>A 5× sequential-vs-random penalty sounds modest compared to HDD (100×) or SSD (4×). Here is why the number is misleading at scale:</p>
<ul>
  <li><strong>The 5× figure is a best-case benchmark</strong> on warm, nearby data at the start of a tape reel. The benchmark reads blocks that are physically close — minimal winding required.</li>
  <li><strong>At petabyte/exabyte scale</strong>, the average distance between random positions on a tape is meters of tape, not millimeters. Physical winding at 3–4 m/s means minutes of latency per random seek, not milliseconds.</li>
  <li><strong>Tape jukebox mechanics</strong>: large archives use tape libraries (robot arms selecting reels). A cache miss means waiting 30–60 seconds for a tape to be physically loaded into a drive — before the first byte can be read.</li>
  <li><strong>The correct mental model</strong>: Tape random latency at archive scale = 30–300 seconds per access. HDDs are 10ms. SSDs are 50μs. Tape is 10,000–100,000× slower than HDD on random workloads at scale — the 5× figure applies only to adjacent sequential blocks.</li>
</ul>
<p><strong>The economic reason tape exists despite this</strong>: tape wins on cost and capacity. LTO-9 tape: ~$5–8/TB. Enterprise HDD: $20–30/TB. Enterprise NVMe SSD: $100–150/TB. At petabyte/exabyte scale (Amazon Glacier, Google Coldline, Meta's data archive), the 4–6× cost advantage over HDD and 20–30× over SSD makes tape the only economically viable long-term storage for data accessed at most once per year.</p>
</div>

<div class="box f"><div class="box-lbl">The SSD Residual 4× Penalty — What Causes It</div>
<p><strong>SSDs have no moving parts — no seek arm, no rotational latency. Yet SSD random reads are still ~4× slower than sequential reads. Why?</strong></p>
<p>SSDs remain page-based. NAND flash reads one page (4–16KB) at a time regardless of how many bytes you need. The 4× gap comes from two sources:</p>
<ul>
  <li><strong>Sequential access exploits internal NAND parallelism.</strong> Modern SSDs contain 8–32 NAND dies operating in parallel. Sequential reads pipeline across multiple dies simultaneously — while die 1 delivers page N, dies 2–8 are already fetching pages N+1 through N+7. The result: peak sequential bandwidth saturates all dies in parallel (7,000+ MB/s NVMe). Random reads cannot pipeline — each random address hits one die at one time, waiting for that single NAND read latency (25–130μs per flash cell type) to complete before the next request begins.</li>
  <li><strong>Flash Translation Layer (FTL) lookup overhead.</strong> Every random read requires the controller to look up the logical-to-physical address mapping in the FTL table (RAM-resident, ~1–5μs per lookup). Sequential reads amortise this across many pages; random reads pay it per operation.</li>
</ul>
<p>The 4× penalty is much smaller than HDD's 100–375× penalty — which is why SSD random I/O is practical for databases while HDD random I/O is catastrophic. But at 800K random IOPS on NVMe, you're still limited to 100 concurrent queries accessing 10,000 random pages each. At high concurrency, the ceiling is real. This is why LSM trees and WAL remain sequential-write structures even on SSDs.</p>
</div>

<p>The SSD's smaller gap (1.4–2×) might suggest random I/O optimization matters less on SSDs. It doesn't — here's why:</p>
<ol>
  <li><strong>Absolute latency compounds:</strong> At 20μs NVMe latency, reading 10,000 random pages takes 200ms minimum. The same 40MB sequentially at 7,000 MB/s takes 5.7ms. Still 35× slower for the same data.</li>
  <li><strong>IOPS ceilings are hard limits:</strong> 1,000,000 IOPS sounds enormous. At 10,000 random page reads per complex query, you can run 100 concurrent queries maximum — on a single NVMe device. Real OLTP workloads hit this ceiling.</li>
  <li><strong>The buffer pool changes the math:</strong> With a 99% buffer pool hit rate, 99% of page reads never touch disk at all. Optimizing data locality (so related rows share pages) multiplies buffer pool effectiveness.</li>
</ol>

<div class="box r"><div class="box-lbl">The Sequential Rule Violated: A Concrete Database Example</div>
<p>Understanding WHY sequential beats random is only useful if you can spot when a query violates the rule. Here is the single most common violation in production databases:</p>
<p><strong>Non-clustered (secondary) index lookups with heap fetches:</strong></p>
<p>Scenario: <code>SELECT * FROM orders WHERE customer_id = 12345</code> on a table where <code>customer_id</code> is a secondary index (not the primary key). Execution:</p>
<ol>
  <li>B+ tree index lookup: 3–4 sequential page reads from root to leaf → returns a list of heap tuple IDs (ctids)</li>
  <li>Heap fetches: for each ctid, fetch the corresponding heap page. Customer 12345 has 500 orders distributed across 500 different heap pages (because rows were inserted over time, interleaved with other customers).</li>
  <li>Result: 500 random heap page reads. At 100 IOPS on HDD → 5 seconds. At 800K IOPS on NVMe → 0.6ms.</li>
</ol>
<p>Same query with a clustered index on <code>customer_id</code>: all 500 orders for customer 12345 are stored on 3–4 consecutive pages. Cost: 3–4 sequential I/Os → 0.08ms on HDD (37× faster), 0.002ms on NVMe.</p>

<div class="box why"><div class="box-lbl">When is a non-clustered index still the right choice?</div>
<p>The heap-fetch example might suggest non-clustered indexes are always bad. They are not — the decision depends on selectivity:</p>
<ul>
  <li><strong>High selectivity + few rows returned:</strong> <code>SELECT * FROM users WHERE email = 'alice@example.com'</code> — returns 1 row. The non-clustered index navigates directly to that one heap page (2 I/Os total). A full table scan on a 10M-row table would read 10,000+ pages. Here the non-clustered index wins overwhelmingly.</li>
  <li><strong>Covering indexes eliminate the heap fetch entirely:</strong> <code>SELECT customer_id, order_date FROM orders WHERE customer_id = 12345</code> — if the index includes <code>order_date</code> as a second column, the query is answered from the index leaf page alone. No heap fetch. The 500-random-I/O penalty vanishes.</li>
  <li><strong>Write-heavy tables:</strong> a clustered index forces all inserts/updates to maintain physical key order — expensive re-ordering on page splits. A non-clustered index allows heap insertions anywhere (append to any page) and maintains only the index's sort order. For tables with 90%+ writes and rare selective reads, the clustered index maintenance cost may exceed the read benefit.</li>
</ul>
<p><strong>The rule:</strong> non-clustered indexes win on high-selectivity point lookups; clustered indexes win on range scans over many rows. The 500-row heap-fetch scenario is the worst case for non-clustered — low selectivity (500 matching rows) with no covering index. Recognising which scenario you are in is the practitioner's decision.</p>
</div>

<p><strong>Other sequential-rule violations:</strong></p>
<ul>
  <li><strong>Correlated subqueries:</strong> <code>SELECT * FROM a WHERE id IN (SELECT aid FROM b WHERE b.val = 'x')</code> — each row in the outer query triggers a separate inner query = N random I/Os</li>
  <li><strong>TOAST dereferences:</strong> a 100KB JSONB column is stored across ~50 TOAST chunks. Fetching the full value = 50 random I/Os per row</li>
  <li><strong>Non-index-covering queries:</strong> an index scan on col1 that also needs col2 (not in the index) forces a heap fetch per index hit = random I/O</li>
</ul>
<p>The sequential-vs-random law is WHY clustered indexes exist, WHY covering indexes matter, and WHY TOAST for large columns has hidden costs.</p>
</div>

<div class="mermaid">
graph TD
    L1[L1 Cache 1ns]
    L2[L2 Cache 4ns]
    L3[L3 Cache 40ns]
    RAM[DRAM 100ns]
    SSD[NVMe SSD 50000ns]
    HDD[HDD 10000000ns]
    L1 --> L2
    L2 --> L3
    L3 --> RAM
    RAM --> SSD
    SSD --> HDD
</div>
<p class="diagram-cap">Figure 1.1 — Memory hierarchy latency ladder. Each level is 4–100× slower than the one above it.</p>

<div class="box d"><div class="box-lbl">Storage Tier Selection Framework</div>
<table>
  <thead><tr><th>Workload</th><th>Storage Choice</th><th>Key Reason</th></tr></thead>
  <tbody>
    <tr><td>OLTP primary — high concurrency (&lt;1TB)</td><td class="g">NVMe SSD</td><td>Low latency + deep queues for concurrent connections</td></tr>
    <tr><td>OLTP primary — cost-sensitive (1–10TB)</td><td class="y">SATA SSD</td><td>Good IOPS; put WAL on separate NVMe to decouple commit latency</td></tr>
    <tr><td>WAL / transaction log (any size)</td><td class="g">NVMe SSD (dedicated device)</td><td>Sequential write, latency-critical; separate device avoids I/O contention with data files</td></tr>
    <tr><td>OLAP / data warehouse (large scans)</td><td class="y">NVMe SSD or HDD RAID</td><td>Sequential bandwidth dominates; HDD RAID-10 × 8 spindles can match NVMe cost-effectively</td></tr>
    <tr><td>Cold data / archival (&gt;1 year old)</td><td class="y">HDD or tape</td><td>Access frequency too low to justify SSD cost</td></tr>
  </tbody>
</table>
</div>

<div class="box n"><div class="box-lbl">Bridge: How the Page Abstraction Birthed B+ Trees — Structural Properties</div>
<p>The page-based I/O constraint does not just influence index design — it <em>determines</em> the structure of B+ trees. Every structural property follows directly from minimising page touches per operation.</p>
<p><strong>The three structural properties of a B+ tree:</strong></p>
<ul>
  <li><strong>Internal nodes hold only keys + child pointers — never values.</strong> Removing values from internal nodes makes them compact: an 8KB page fits ~580 (key + pointer) pairs. This gives fanout 580 — each internal node has 580 children. A 4-level tree covers 580⁴ = 113 billion rows. Without this, with values stored in internal nodes, fanout drops to ~60 (8KB / (key + value + pointer)), requiring 5+ levels for the same dataset — 5+ I/Os per lookup instead of 4.</li>
  <li><strong>Leaf nodes hold keys + values + sibling pointers.</strong> All actual row data (or primary key pointers in secondary indexes) lives exclusively at the bottom level. Leaf nodes also carry a doubly-linked list pointer to their left and right neighbour leaves, forming a sorted linked list of all data across the entire tree.</li>
  <li><strong>Range scans use the leaf linked list — sequential I/O.</strong> To answer <code>WHERE id BETWEEN 1000 AND 2000</code>: traverse from root to the first matching leaf (log N I/Os, ~4), then follow sibling pointers rightward until the range ends. Each pointer hop reads the adjacent page — sequential I/O at 150 MB/s instead of random I/O at 100 IOPS. The leaf linked list converts range scans from O(k × log N) random I/Os to O(log N + k) sequential I/Os, where k is the number of result pages.</li>
</ul>
<p><strong>Node splits</strong>: When a leaf node fills to capacity, B+ trees split it in half. The middle key is promoted upward to the parent internal node as a separator. If the parent also overflows, the split propagates upward — recursively — until either a parent has space or the root splits, creating a new root and increasing tree depth by 1. This is how B+ trees maintain their balance while keeping every node at exactly one page.</p>
<p><strong>Why not binary search trees?</strong> A BST node holds one key + two child pointers = ~24 bytes. An 8KB page holds ~340 BST nodes, but they are stored at arbitrary addresses — each node access is a random I/O. A 20-level BST costs 20 random I/Os = 200ms on HDD. A 4-level B+ tree with 580 fanout = 4 I/Os = 40ms. The B+ tree wins by 5× not through algorithmic cleverness but through page alignment.</p>
</div>

<div class="box l"><div class="box-lbl">Cross-Connections from This Chapter</div>
<ul>
  <li><strong>→ Ch3 (B+ Tree):</strong> Node size = one page = one I/O. A 4-level B+ tree with 400 keys/node covers 400⁴ = 25.6 billion rows in exactly 4 I/Os. This arithmetic directly follows from the page abstraction.</li>
  <li><strong>→ Ch3 (LSM Tree):</strong> LSM memtable flushes and SSTable compaction are deliberately sequential writes — exploiting the sequential-over-random law even on SSDs.</li>
  <li><strong>→ Ch5 (Buffer Manager):</strong> The entire buffer pool exists to absorb random I/O costs. Every page served from RAM eliminates one ~10ms HDD read or one ~50μs NVMe read. At 10,000 queries/sec, 99% buffer pool hit rate saves 9,900 disk reads per second.</li>
  <li><strong>→ Ch5 (WAL):</strong> WAL is append-only sequential to exploit sequential write speed. The WAL write is fast; the B+ tree random updates are deferred. This is the core WAL performance insight.</li>
  <li><strong>B+ tree leaf node sibling pointers (Chapter 3)</strong>: Leaf nodes form a doubly-linked list across pages. Range scans exploit this by reading leaves sequentially — paying the sequential I/O rate (~150 MB/s) instead of the random I/O rate (~100 IOPS). The entire motivation for this design traces back to the sequential-vs-random gap established in this chapter.</li>
</ul>
</div>

<div class="box xr"><div class="box-lbl">Related Deep Dives</div>
<ul>
  <li><strong>vutr — "What Makes OLTP Databases So Quick"</strong>: Explains why BST is wrong for disk (each node = separate non-contiguous block = 20 I/Os). Directly bridges in-memory tree structures to disk-resident B-Trees using block-based layout reasoning. (pairs with §1.1 — The Page Abstraction)</li>
  <li><strong>vutr — "How to choose the right diskless Kafka"</strong>: Shows the economic shift away from local disk optimization toward remote object storage. Relevant when evaluating modern database design trade-offs (latency vs durability vs cost). (pairs with §1.3 — NVMe)</li>
</ul>
</div>

<div class="recall">
<div class="recall-head">Architect's Checkpoint</div>
<div class="q"><span class="q-n">Q1 </span>A colleague proposes using 1MB page sizes to reduce I/O operation count. You disagree. Make the argument: what breaks at 1MB for a typical OLTP workload, and what workload <em>would</em> benefit from large pages?</div>
<div class="q"><span class="q-n">Q2 </span>You're designing a system receiving 10,000 inserts/second into a PostgreSQL table on a SATA SSD. WAL commits are taking 8ms — too slow. What storage change fixes this, and why does it work?</div>
<div class="q"><span class="q-n">Q3 </span>Explain write amplification in SSDs. Give one scenario where WA of 20× destroys performance and one design choice that reduces it. Then explain why this also matters for LSM trees (different mechanism, same problem name).</div>
</div>

<div class="box teach"><div class="box-lbl">How to Teach This Chapter</div>
<p><strong>Junior engineer (5 min):</strong> Start with one number: 100 IOPS for random reads on HDD. Then ask: "If a query touches 1,000 pages, how long does it take?" (10 seconds.) That discomfort is the entire motivation for every data structure in this book. Show the Sequential vs Random table. End with: "B+ trees, buffer pools, WAL — all of them exist to reduce random I/Os."</p>
<p><strong>Senior engineer (15 min):</strong> Walk through HDD seek + rotation math → derive the 100 IOPS ceiling. Then contrast SSD: no seek arm, but the FTL/GC complexity means SSD performance is not "solved." Cover the write cliff. Explain queue depth math (why 200 concurrent connections saturate SATA's 32-command queue). End with the storage tier selection table and ask them to justify their current production storage choice.</p>
<p><strong>Expert architect (30 min discussion):</strong> Ask: "Your company is considering moving from NVMe-backed RDS to S3-backed Aurora. What does that do to your latency floor, and which of your query patterns break?" Drive toward the tension between local NVMe (low latency, high cost, limited scale) vs remote object storage (higher latency, cheaper, elastic). The answer requires internalising NVMe vs network latency numbers from this chapter.</p>
</div>

<div class="box gap"><div class="box-lbl">Questions This Chapter Doesn't Answer</div>
<ul>
  <li>How does ZNS (Zoned Namespace) NVMe change the FTL equation — and should new database designs use it directly?</li>
  <li>When does persistent memory (Optane/PMEM) change the buffer pool architecture — is a buffer pool even needed at sub-microsecond latency?</li>
  <li>What is the real-world write amplification of PostgreSQL's WAL on an NVMe device, and how does the WAL segment size interact with GC pressure?</li>
  <li>At what point does network latency to remote storage (NFS, EBS, S3) make local NVMe indispensable vs a premature optimisation?</li>
</ul>
</div>
</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 2: SOFTWARE + HARDWARE STACK
# ─────────────────────────────────────────────────────────────────────────────
CH2 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 2 of 5</div>
  <h1>The Full Software + Hardware Stack</h1>
  <div class="ch-src">Source: The Software + Hardware Stack (and how to make it FAST)</div>
  <p class="ch-sum">Your application code is one layer in a five-layer stack. Performance problems can originate at any layer. Architects who understand the full stack — from CPU registers to network cards — can diagnose bottlenecks that are invisible to developers who only see their own code.</p>
</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>Most performance investigations stop at the application layer. The developer rewrites the query, adds an index, and moves on — never realising the bottleneck was a syscall-per-I/O loop at 200% CPU overhead, or double-caching that was silently consuming 64GB of their 128GB server. Understanding the full stack from CPU registers to NVMe controllers means you can diagnose the 20% of problems that no amount of query tuning will ever fix.</p>
</div>

<div class="topic">
<h2>The Latency Hierarchy Every Architect Carries in Their Head</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Imagine all memory speeds as physical distances. If accessing an L1 cache register takes 1 second, accessing RAM takes 6 minutes, accessing an SSD takes 2 days, and accessing a hard drive takes 3 weeks. That's why the entire engineering discipline of database systems is about moving data as far "up" the hierarchy as possible before a query asks for it.</p></div>

<div class="box n"><div class="box-lbl">Memory Latency Hierarchy (2024 Reference Numbers)</div>
<table>
  <thead><tr><th>Level</th><th>Latency</th><th>Typical Size</th><th>Managed By</th><th>Database Relevance</th></tr></thead>
  <tbody>
    <tr><td>CPU Registers</td><td class="g">&lt;0.3ns</td><td>~1KB (all registers)</td><td>CPU</td><td>Query execution, expression evaluation</td></tr>
    <tr><td>L1 Cache</td><td class="g">~1ns</td><td>32–64 KB/core</td><td>CPU hardware</td><td>Hot code paths, tight loops</td></tr>
    <tr><td>L2 Cache</td><td class="g">~4ns</td><td>256KB–1MB/core</td><td>CPU hardware</td><td>Working data for active operators</td></tr>
    <tr><td>L3 Cache (LLC)</td><td class="y">~10–40ns</td><td>4–64MB (shared)</td><td>CPU hardware</td><td>Shared across cores; hot buffer pool metadata</td></tr>
    <tr><td>RAM (DRAM)</td><td class="y">~60–100ns</td><td>GBs–TBs</td><td>OS + application</td><td>Buffer pool pages, sort spills, hash tables</td></tr>
    <tr><td>NVMe SSD</td><td class="rd">~20–100μs</td><td>100s GBs–TBs</td><td>OS (kernel + FTL)</td><td>Cold pages not in buffer pool</td></tr>
    <tr><td>SATA SSD</td><td class="rd">~80–200μs</td><td>100s GBs–TBs</td><td>OS (kernel + FTL)</td><td>Cheaper alternative to NVMe</td></tr>
    <tr><td>HDD</td><td class="rd">~5–20ms</td><td>TBs</td><td>OS + disk controller</td><td>Cold data, archival; avoid for OLTP</td></tr>
    <tr><td>LAN (same rack)</td><td>~0.1–1ms</td><td>—</td><td>Network stack + OS</td><td>Distributed database replication, remote storage</td></tr>
    <tr><td>WAN (cross-region)</td><td class="rd">~50–300ms</td><td>—</td><td>Network stack</td><td>Geographic replication; defines RPO/RTO</td></tr>
  </tbody>
</table>
</div>

<p>The most important ratio to internalize: <strong>RAM is 100,000× faster than HDD, and 1,000× faster than NVMe</strong> for random access. This gap is the entire justification for the buffer pool (Chapter 5). Serving even 90% of reads from RAM and 10% from NVMe reduces average latency by 1,000×.</p>

<p><strong>Cache line implications:</strong> CPUs read and write memory in 64-byte cache line units — not individual bytes or words. This means adjacent data in memory is often loaded together even if only one field is accessed. Database systems exploit this through <em>struct layout</em>: putting frequently-accessed fields together in the same struct (or tuple header) ensures they arrive in the same cache line, avoiding multiple cache misses per tuple scan.</p>
</div>

<div class="topic">
<h2>The Five-Layer Stack</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Think of it as a restaurant: you (the app) order food (a query). The waiter (system libraries) takes your order. The kitchen (kernel) coordinates cooking. The suppliers (hardware) provide raw ingredients. If the kitchen is slow, the food is slow — no matter how good a chef you are.</p></div>

<h3>Layer 1: Application</h3>
<p>Your code — database engine, web server, business logic. You control this entirely. Poor algorithms and unnecessary work show up here. The database engine itself is an application: the query planner, executor, buffer manager, and lock manager all live at this layer.</p>

<h3>Layer 2: System Libraries</h3>
<p>Pre-built code the application links against: <code>libc</code>, <code>libpthread</code>, <code>libssl</code>. The OS ships these; the application calls them. A slow library version is a bottleneck you cannot directly fix without an OS upgrade. PostgreSQL, for example, links <code>libz</code> for WAL compression and <code>libssl</code> for TLS connections — library performance affects database performance.</p>

<h3>System Libraries: Concrete Examples That Matter for Databases</h3>

<p>The System Libraries layer is where databases make key performance decisions — most choose to bypass it entirely or replace it with custom implementations.</p>

<p><strong>1. Buffered I/O via libc (stdio.h)</strong>: The C standard library wraps raw syscalls with a userspace buffer. <code>fwrite()</code> accumulates bytes in a 4KB buffer and issues a <code>write()</code> syscall only when the buffer fills. This reduces syscall frequency but introduces double-buffering: the libc buffer in userspace + the OS page cache in kernel. Databases disable this by using <code>O_DIRECT</code> flag on <code>open()</code>, bypassing the OS page cache entirely and issuing aligned 4KB/8KB writes directly to disk. PostgreSQL does NOT use <code>O_DIRECT</code> by default — it manages its own buffer pool and lets the OS cache on top (double caching, a known inefficiency). MySQL InnoDB supports <code>innodb_flush_method=O_DIRECT</code>.</p>

<p><strong>2. Memory Allocators</strong>: glibc's <code>malloc()</code> uses a general-purpose allocator that performs poorly under database workloads (many small allocations of varying size with high thread contention). Production databases replace it:</p>
<ul>
  <li><code>jemalloc</code> — used by Redis, RocksDB, CockroachDB: arena-based allocation reduces lock contention in multi-threaded code, better memory fragmentation behaviour</li>
  <li><code>tcmalloc</code> (Google) — used by MySQL, Abseil: thread-local caches for common sizes, avoids cross-thread contention entirely</li>
  <li>PostgreSQL uses <code>palloc()</code> — its own slab allocator for query-scoped memory, tied to memory contexts that free entire slabs at once (avoiding per-object <code>free()</code>)</li>
</ul>

<p><strong>3. SSL/TLS Libraries</strong>: OpenSSL or BoringSSL (Google's fork) encrypt the database wire protocol. This adds ~0.5–2% CPU overhead for database connections — negligible for typical OLTP but measurable at 100K+ connections/second. PostgreSQL, MySQL, and Redis all optionally wrap their socket layer in OpenSSL.</p>

<div class="box d"><div class="box-lbl">When to Investigate System Libraries</div>
<ul>
  <li><strong>Memory fragmentation under load</strong> → replace malloc with jemalloc or tcmalloc</li>
  <li><strong>High CPU on crypto operations</strong> → check SSL library + consider hardware acceleration (AES-NI, CPU affinity)</li>
  <li><strong>Unexpected double caching / memory usage</strong> → check whether O_DIRECT is configured; consider whether the buffer pool + OS page cache are both caching the same pages</li>
</ul>
</div>

<h3>Layer 3: System Calls — The Guarded Boundary</h3>
<p>Every file read, write, network operation, and memory allocation crosses from user-space into kernel-space via a <strong>system call</strong> (syscall). This boundary is guarded to prevent user processes from directly accessing kernel memory, hardware registers, or each other's address spaces — the fundamental OS isolation guarantee.</p>

<p>Crossing this boundary has measurable cost. A typical syscall on modern Linux x86-64 takes approximately <strong>1–5 microseconds</strong>: the CPU must save register state, switch privilege levels (ring 3 → ring 0), validate arguments, execute the kernel function, restore state, and return. That's 1,000–5,000 nanoseconds per syscall — which sounds small but compounds immediately:</p>
<ul>
  <li>A database doing 100,000 queries/sec, each issuing 10 read syscalls = <strong>1,000,000 syscalls/sec</strong></li>
  <li>At 2μs each = <strong>2 seconds of CPU time per second</strong> just on syscall overhead — 200% of one CPU core</li>
</ul>
<p>This is why batching I/O is a real optimization — not just "good practice".</p>

<div class="box n"><div class="box-lbl">Meltdown/Spectre Impact on Syscall Cost</div>
<p>After the Meltdown vulnerability (2018), OS kernels enabled Page Table Isolation (PTI / KPTI) on x86-64 CPUs. This flushes TLB entries on every user↔kernel transition, adding 100–500ns per syscall on non-mitigated hardware. Workloads doing millions of syscalls/sec saw 10–30% throughput degradation. This is why io_uring (which eliminates most syscalls) became critical for high-performance databases post-2018.</p>
</div>

<h3>The Core I/O System Calls a Database Uses</h3>

<p>Every database I/O operation ultimately reduces to one of these kernel calls:</p>

<div class="box n"><div class="box-lbl">Core I/O Syscalls</div>
<table>
  <thead><tr><th>Syscall</th><th>Signature</th><th>Why Databases Use It</th></tr></thead>
  <tbody>
    <tr><td><code>pread()</code></td><td><code>pread(fd, buf, count, offset)</code></td><td>Thread-safe positioned read — no shared seek pointer, safe for concurrent threads</td></tr>
    <tr><td><code>pwrite()</code></td><td><code>pwrite(fd, buf, count, offset)</code></td><td>Thread-safe positioned write — same benefit as pread</td></tr>
    <tr><td><code>fsync()</code></td><td><code>fsync(fd)</code></td><td>Flush OS page cache to disk + sync file metadata. Required for durable commit. ~1–5ms on NVMe.</td></tr>
    <tr><td><code>fdatasync()</code></td><td><code>fdatasync(fd)</code></td><td>Like fsync but skips metadata (mtime, size) unless changed. ~10–20% faster than fsync.</td></tr>
    <tr><td><code>open(O_DIRECT)</code></td><td><code>open(path, O_DIRECT|O_RDWR)</code></td><td>Bypass OS page cache. Requires 512-byte aligned buffers. InnoDB uses this.</td></tr>
    <tr><td><code>mmap()</code></td><td><code>mmap(NULL, len, PROT_READ, MAP_SHARED, fd, 0)</code></td><td>Map file into virtual address space. SQLite, LMDB use this instead of pread/pwrite.</td></tr>
  </tbody>
</table>
<p>io_uring submits these same operations asynchronously to the kernel's Submission Queue ring — eliminating the per-operation syscall by batching. The kernel polls the SQ directly via a shared memory mapping between userspace and kernelspace.</p>
</div>

<h3>Layer 4: Kernel</h3>
<p>The OS kernel manages: CPU scheduling, virtual memory and paging, device drivers, file systems, network stack, and I/O scheduling. Databases interact with the kernel primarily via:</p>
<ul>
  <li><strong>File system calls</strong> (<code>read()</code>, <code>write()</code>, <code>pread()</code>, <code>pwrite()</code>, <code>fsync()</code>) — for data and WAL files</li>
  <li><strong>Memory management</strong> (<code>mmap()</code>, <code>mprotect()</code>, <code>brk()</code>) — for buffer pool, shared memory</li>
  <li><strong>Process/thread management</strong> (<code>clone()</code>, <code>futex()</code>) — for connection handling and background workers</li>
  <li><strong>Network</strong> (<code>accept()</code>, <code>recv()</code>, <code>send()</code>, <code>epoll_wait()</code>) — for client connections</li>
</ul>

<h3>Layer 5: Hardware</h3>
<p>CPU cores, RAM DIMMs, PCIe bus, NVMe controllers, NICs. The absolute performance floor — no software optimization can exceed hardware limits. But hardware choices profoundly affect database architecture:</p>
<ul>
  <li><strong>CPU core count vs clock speed:</strong> OLTP workloads benefit from many fast cores (high concurrency); analytics workloads benefit from SIMD-capable cores (vectorized scan operations)</li>
  <li><strong>NUMA topology:</strong> Multi-socket servers have non-uniform memory access — RAM attached to socket 0 takes ~40ns from socket 0 CPUs but ~120ns from socket 1 CPUs. PostgreSQL's buffer pool is in shared memory accessible from any socket; NUMA-aware memory allocation (numactl) keeps hot buffer pool pages local to the CPUs accessing them</li>
  <li><strong>PCIe bandwidth:</strong> NVMe drives connect via PCIe; multiple NVMe devices share PCIe bandwidth. A PCIe 4.0 ×16 slot provides 32 GB/s — enough for ~4 fully saturated PCIe 4.0 NVMe drives</li>
</ul>
</div>

<div class="topic">
<h2>I/O Methods: Buffered, Direct, mmap, and io_uring</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>When your database reads a page from disk, there are four different routes between the storage device and your process. Each has different trade-offs for latency, CPU usage, and control. Choosing the wrong one can cut throughput in half or add 50% CPU overhead.</p></div>

<h3>Buffered I/O (Default — <code>read()</code> / <code>write()</code>)</h3>
<p>The default mode. Data flows: <strong>disk → kernel page cache → user-space buffer → application</strong>. The kernel keeps a copy of recently-read disk data in the kernel page cache (a portion of RAM). A second read of the same data is served from the page cache — no disk I/O.</p>

<p><strong>The double-caching problem:</strong> A database with its own buffer pool (PostgreSQL, MySQL) reads data into its buffer pool (in user-space RAM). If using buffered I/O, the kernel also caches the same data in the kernel page cache. The same data is in RAM twice — once in the database buffer pool and once in the kernel cache. This wastes RAM and CPU (extra copy operation on every read). At 128GB RAM with 64GB shared_buffers, up to 64GB can be double-cached.</p>

<h3>Direct I/O (<code>O_DIRECT</code>)</h3>
<p>Bypasses the kernel page cache entirely. Data flows: <strong>disk → DMA → user-space buffer</strong>. The database manages its own caching (its buffer pool). Eliminates double-caching. Requires reads and writes to be aligned to page size (512B or 4KB) and use aligned buffers.</p>

<p>PostgreSQL uses buffered I/O by default (historical reasons: simpler, portable). MySQL InnoDB uses <code>O_DIRECT</code> for its data files. The InnoDB approach is strictly better for large buffer pools — no double caching. PostgreSQL 16+ is adding native <code>O_DIRECT</code> support (long overdue).</p>

<h3>Memory-Mapped I/O (<code>mmap()</code>)</h3>
<p>Maps a file directly into the process virtual address space. The application accesses data via pointer dereferences — no explicit read/write syscalls. The kernel's virtual memory system handles fetching pages on demand (page faults) and writing dirty pages back to disk.</p>

<p><strong>How it works:</strong> <code>mmap()</code> creates a virtual memory area (VMA) in the process address space. When the application dereferences a pointer to an unmapped page, a <em>page fault</em> fires, the kernel fetches the page from disk, installs a page table entry (PTE), and resumes the application — transparently.</p>

<p><strong>SQLite uses mmap</strong> — the kernel manages the buffer pool, simplifying the SQLite codebase enormously. This works well for small databases (few GB) where the kernel's LRU eviction policy is acceptable. PostgreSQL deliberately avoids mmap for its data files because:</p>
<ul>
  <li><strong>TLB shootdowns:</strong> On multi-core systems, changing a page table entry requires invalidating the TLB entry on every CPU core simultaneously — an expensive inter-processor interrupt (IPI) storm under high concurrency</li>
  <li><strong>No eviction control:</strong> The kernel decides which pages to evict (LRU approximation). The database cannot implement workload-aware eviction (e.g., prioritizing index pages over table pages)</li>
  <li><strong>Async I/O is impossible:</strong> Page faults are synchronous — the thread blocks until the page is fetched. No way to prefetch or overlap I/O</li>
  <li><strong>SIGBUS on disk errors:</strong> A disk read error becomes a SIGBUS signal to the process — crash rather than graceful error handling</li>
</ul>

<h3>io_uring: Kernel-Bypass Async I/O</h3>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Instead of the application asking the kernel "please read this page" (one syscall per request), io_uring sets up a shared notebook between the app and kernel. The app writes I/O requests to the notebook's first half (submission queue). The kernel reads them, does the I/O, and writes results to the second half (completion queue). The app checks for completions whenever it wants — no syscall required for checking. Multiple I/Os can be submitted and completed with a single syscall, or with zero syscalls if the ring is set up correctly.</p></div>

<p>io_uring (Linux 5.1+, 2019) is a system call interface built around two ring buffers shared in memory between the kernel and user space:</p>
<ul>
  <li><strong>Submission Queue (SQ):</strong> The application deposits I/O requests (read page X, write page Y, fsync file Z) into the SQ as <em>submission queue entries</em> (SQEs). Each SQE specifies the operation, file descriptor, buffer, and offset.</li>
  <li><strong>Completion Queue (CQ):</strong> The kernel reads SQEs, performs the I/O asynchronously, and deposits results as <em>completion queue entries</em> (CQEs) into the CQ. The application polls the CQ for completed operations.</li>
</ul>

<p>In <strong>polling mode</strong> (<code>IORING_SETUP_SQPOLL</code>), a kernel thread continuously polls the SQ — the application can submit I/O by writing to shared memory with zero syscalls. In <strong>interrupt mode</strong>, the application calls <code>io_uring_enter()</code> once to submit a batch of N requests and wait for M completions — one syscall for N operations.</p>

<div class="mermaid">
graph LR
    U[Userspace]
    K[Kernel]
    SQ[Submission Queue<br/>shared ring buffer<br/>userspace writes]
    CQ[Completion Queue<br/>shared ring buffer<br/>kernel writes]
    U -->|push I/O request| SQ
    SQ -->|kernel polls, no syscall| K
    K -->|push result| CQ
    CQ -->|userspace reads, no syscall| U
</div>
<p class="diagram-cap">Figure 2.1 — io_uring: userspace and kernel share two ring buffers. No syscall per I/O operation — the kernel polls the SQ directly.</p>

<div class="box d"><div class="box-lbl">io_uring Trade-offs — What You Give Up</div>
<p>io_uring is not a free upgrade. The trade-offs explain why PostgreSQL took until v16 to adopt it and why most applications still use standard pread/pwrite:</p>
<ul>
  <li><strong>Linux-only.</strong> io_uring is a Linux kernel interface. It does not exist on macOS, Windows, or BSD. Any database or application using io_uring cannot be compiled or run on non-Linux systems. PostgreSQL, MySQL, SQLite, and most cross-platform databases therefore cannot make io_uring their primary I/O path — they use it as an optional Linux-specific backend.</li>
  <li><strong>Kernel version requirement: Linux 5.1+ (May 2019).</strong> Older enterprise distributions (RHEL 7, Ubuntu 18.04 LTS) running kernels 3.x–4.x cannot use io_uring at all. Many production database servers run on LTS OS releases with 3–5 year old kernels. Security patches do not backport io_uring. You cannot use io_uring until you upgrade both OS and kernel.</li>
  <li><strong>API complexity.</strong> The io_uring API requires setting up ring buffers, registering file descriptors, managing SQ/CQ indices, and handling partial completions — significantly more code than a synchronous <code>pread()</code> call. The <code>liburing</code> helper library reduces this, but the async programming model (submit now, poll for completion later) requires restructuring application I/O code.</li>
  <li><strong>Security vulnerabilities.</strong> io_uring's shared kernel/userspace memory has been a source of privilege escalation vulnerabilities (CVE-2023-2598, CVE-2022-29582 among others). Google disabled io_uring in Android and ChromeOS production environments in 2023. Some hardened cloud environments restrict it.</li>
</ul>
<p><strong>The architect's rule</strong>: Use io_uring for Linux-only write-heavy workloads (WAL, bulk ingest, log-structured storage) where the syscall overhead is measurable (>100K I/Os/sec). For cross-platform code or kernels &lt;5.1, use <code>pread</code>/<code>pwrite</code> with <code>O_DIRECT</code>. Profile before committing to the async programming model — io_uring's benefit only materialises when syscall overhead is your actual bottleneck, not disk or CPU.</p>
</div>

<div class="box s"><div class="box-lbl">Why io_uring Eliminates Syscalls — The Shared Memory Trick</div>
<p>The SQ (Submission Queue) and CQ (Completion Queue) are not separate memory regions for userspace and kernel — they are the <strong>same physical memory</strong>, mapped into both address spaces simultaneously via <code>mmap()</code>.</p>
<p>When you call <code>io_uring_setup()</code>, the kernel allocates ring buffers in physical memory, then returns file descriptors that let you <code>mmap()</code> those same pages into your process's virtual address space. Both the kernel and your process see the same bytes at the same physical addresses — no copying, no context switch needed to pass the data.</p>
<p>With <code>IORING_SETUP_SQPOLL</code>: a dedicated kernel thread polls the SQ tail pointer in a tight loop. When your process pushes a new entry (incrementing the tail), the kernel thread sees it immediately and begins processing — <strong>zero syscalls</strong> from submission to completion. The only syscall is <code>io_uring_enter()</code> to wake the kernel thread if it has gone idle (typically after 1ms of no new submissions).</p>
</div>

<div class="box n"><div class="box-lbl">I/O Method Comparison</div>
<table>
  <thead><tr><th>Method</th><th>Syscalls per I/O</th><th>Double Cache</th><th>Async?</th><th>Control</th><th>Best For</th></tr></thead>
  <tbody>
    <tr><td>Buffered I/O (<code>read()</code>)</td><td>1</td><td class="rd">Yes</td><td class="rd">No</td><td>Low</td><td>Simple apps, small databases, cold data</td></tr>
    <tr><td>Direct I/O (<code>O_DIRECT</code>)</td><td>1</td><td class="g">No</td><td class="rd">No</td><td>Medium</td><td>Databases with own buffer pools (InnoDB)</td></tr>
    <tr><td>mmap</td><td>0 (after setup)</td><td class="rd">Yes (kernel cache)</td><td class="rd">No (page faults)</td><td class="rd">Low</td><td>Read-heavy embedded databases (SQLite)</td></tr>
    <tr><td>io_uring</td><td>0–1 per batch</td><td class="g">No (with O_DIRECT)</td><td class="g">Yes</td><td class="g">High</td><td>High-throughput databases, write-heavy OLTP</td></tr>
  </tbody>
</table>
</div>

<p><strong>Real adoption:</strong> RocksDB added io_uring support in 2021. ScyllaDB was built on io_uring from the start. PostgreSQL 16+ added io_uring for WAL writes. The speedup for sequential write-heavy workloads (WAL, bulk ingest) is typically 30–60%; for random read-heavy OLTP it varies more based on buffer pool hit rate.</p>

<h3>Diagnosing Layer-Specific Bottlenecks</h3>

<p>When a database is slow, the software stack is the investigation target. Here is the diagnostic toolkit by layer:</p>

<div class="box n"><div class="box-lbl">Layer Diagnostic Toolkit</div>
<table>
  <thead><tr><th>Layer</th><th>Tool</th><th>What It Shows</th></tr></thead>
  <tbody>
    <tr><td>Application</td><td><code>pg_stat_statements</code>, slow query log</td><td>Which queries are slow; N+1 query patterns; index misses</td></tr>
    <tr><td>System Libraries</td><td><code>valgrind --tool=massif</code>, <code>heaptrack</code></td><td>Memory allocation patterns; fragmentation; allocator contention</td></tr>
    <tr><td>System Calls</td><td><code>strace -p PID -e trace=read,write,pread64,fsync -T</code></td><td>Every I/O syscall with duration; reveals fsync frequency</td></tr>
    <tr><td>System Calls</td><td><code>perf stat -e syscalls:sys_enter_read,syscalls:sys_enter_write</code></td><td>Syscall count per second; quantifies syscall overhead</td></tr>
    <tr><td>Kernel</td><td><code>bpftrace -e 'tracepoint:block:block_rq_complete { @lat = hist(args->nr_sector * 512); }'</code></td><td>Block I/O completion latency histogram</td></tr>
    <tr><td>Kernel</td><td><code>iostat -x 1</code>, <code>iotop</code></td><td>Device utilization; IOPS; await (I/O queue depth)</td></tr>
    <tr><td>Hardware</td><td><code>nvme smart-log /dev/nvme0</code></td><td>SSD wear level, temperature, write amplification factor</td></tr>
    <tr><td>Hardware</td><td><code>fio --randread --ioengine=io_uring --iodepth=32</code></td><td>Raw device IOPS/latency — baseline before blaming software</td></tr>
  </tbody>
</table>
<p><strong>Investigation order</strong>: always start at the Application Layer (slow queries, bad indexes) before descending — 80% of database performance problems are solved at layer 1. Only descend to System Call or Hardware layers when query-level fixes are exhausted and the problem persists under single-row, indexed queries.</p>
</div>

<div class="box l"><div class="box-lbl">Cross-Connections from This Chapter</div>
<ul>
  <li><strong>→ Ch1 (Storage):</strong> The latency hierarchy explains why the buffer pool (RAM) is the most impactful optimization. NVMe at 50μs vs RAM at 100ns = 500× difference; the goal is always to serve reads from the layer above.</li>
  <li><strong>→ Ch5 (Buffer Manager):</strong> PostgreSQL's shared_buffers lives in shared memory (not kernel page cache). The double-caching problem means <code>effective_cache_size</code> should account for the kernel's cache too — it's a hint to the planner, not an actual allocation.</li>
  <li><strong>→ Ch5 (WAL):</strong> WAL durability requires <code>fsync()</code> — a syscall that waits until the kernel page cache is flushed to physical storage. With io_uring, multiple WAL records can be submitted and fsynced as a batch (group commit), dramatically improving commit throughput.</li>
  <li><strong>→ Ch5 (Recovery Manager):</strong> <code>O_DIRECT</code> for WAL bypasses kernel caching — the database controls exactly when WAL hits persistent storage. Essential for accurate durability guarantees without relying on kernel flush timing.</li>
</ul>
</div>

<div class="recall">
<div class="recall-head">Architect's Checkpoint</div>
<div class="q"><span class="q-n">Q1 </span>PostgreSQL uses buffered I/O by default while MySQL InnoDB uses O_DIRECT. You're setting up a 256GB PostgreSQL server with 128GB shared_buffers. Quantify the RAM waste from double-caching and explain how <code>effective_cache_size</code> should be set to compensate in the query planner.</div>
<div class="q"><span class="q-n">Q2 </span>A colleague argues "mmap is faster than read() because it has zero syscalls." Give three specific scenarios where mmap performs worse than O_DIRECT on a multi-core database server, with the technical mechanism for each.</div>
<div class="q"><span class="q-n">Q3 </span>Explain io_uring's submission queue / completion queue architecture. Why does this architecture benefit WAL writes specifically, and what does "group commit" mean in this context?</div>
</div>

<div class="box teach"><div class="box-lbl">How to Teach This Chapter</div>
<p><strong>Junior engineer (5 min):</strong> Draw the 5-layer stack on a whiteboard. Point at the boundary between Layer 2 (libraries) and Layer 3 (kernel). Say: "Every time your code crosses this line, it costs 2 microseconds and flushes CPU registers. At 1 million crossings per second, that's 2 full CPU cores just on overhead." Then show the io_uring diagram: two ring buffers, zero syscalls per I/O. That's the entire motivation.</p>
<p><strong>Senior engineer (15 min):</strong> Start with the double-caching problem — walk through the math on a 256GB server with 128GB shared_buffers. Then contrast O_DIRECT (InnoDB) vs buffered I/O (PostgreSQL default). Cover mmap failure modes: TLB shootdowns under concurrency, no eviction control, SIGBUS on disk errors. End with io_uring adoption timeline: why post-Meltdown PTI made syscall overhead suddenly painful enough to justify io_uring's complexity.</p>
<p><strong>Expert architect (30 min discussion):</strong> "You're designing a new database engine from scratch on Linux 6.x. Which I/O method do you use for WAL vs data files vs index files — and are they different?" Drive toward: WAL = io_uring + O_DIRECT (sequential, latency-critical, must control durability exactly); data files = io_uring + O_DIRECT (own buffer pool, avoid double-cache); index files = same. Then challenge: "When would you use mmap?" — only for an embedded read-heavy database where simplicity beats performance (SQLite use case).</p>
</div>

<div class="box gap"><div class="box-lbl">Questions This Chapter Doesn't Answer</div>
<ul>
  <li>How does NUMA topology affect PostgreSQL's shared buffer pool — and what does <code>numactl --interleave</code> actually buy you on a dual-socket server?</li>
  <li>When does RDMA (Remote Direct Memory Access) change the network layer's latency enough to make remote storage competitive with local NVMe?</li>
  <li>What is the actual measured syscall overhead on ARM64 (AWS Graviton) vs x86-64 post-Meltdown mitigations — and does this change the io_uring adoption calculus?</li>
  <li>How does io_uring's fixed-buffer mode (pre-registered buffers) differ from standard mode, and when is it worth the complexity for a database WAL path?</li>
</ul>
</div>
</div>
</div>
"""

print("Part 1 (CSS + Cover + Ch1 + Ch2) defined.")
print("Writing Chapter 3, 4, 5 next...")

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 3: DATA ORGANISATION
# ─────────────────────────────────────────────────────────────────────────────
CH3 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 3 of 5</div>
  <h1>Data Organisation: The Read-Write Trade-off</h1>
  <div class="ch-src">Source: Data Organization: Making Database CRUD Operations Fast</div>
  <p class="ch-sum">How you organise data before storing it is the single biggest lever on database performance. Every data structure is a deliberate position on the read-write trade-off spectrum. Master this spectrum and every subsequent architectural decision — which index to use, when to switch to LSM, why WAL is append-only — becomes derivable rather than memorised.</p>
</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>The single most consequential architectural decision in any data-intensive system is not which cloud provider to use, or which language to write in — it is which data structure organises the data on disk. Choose a B+ tree for a write-heavy time-series system and you will spend the next three years fighting index contention, slow bulk ingest, and SSD wear. Choose an LSM tree for a read-heavy transactional system and your read latency will degrade every week as compaction falls behind. This chapter gives you the decision framework that separates architects who choose right from engineers who find out the hard way.</p>
</div>

<div class="topic">
<h2>The Spectrum: Four Structures, One Trade-off</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Filing papers on a messy desk is instant (just drop it). Finding them later takes forever. A filing cabinet sorted alphabetically takes more effort to file correctly, but anything is findable in seconds. Every database structure is a point between these extremes — and there is no free lunch.</p></div>

<h3>1. Unsorted Array (Append-Only)</h3>
<p><strong>Write: O(1)</strong> — append to end. <strong>Read: O(n)</strong> — full scan required.</p>
<p>Inserting one billion rows takes one billion O(1) appends. Finding one row requires scanning all one billion. Catastrophic for reads. Perfect for sequential writes that are rarely read during normal operation.</p>
<p><strong>Where databases actually use this:</strong> The Write-Ahead Log. WAL writes must be blindingly fast — they happen on every single transaction commit. The WAL is only read during crash recovery, which is rare. The read-cost trade-off is explicitly acceptable. This is also why time-series append logs (Kafka topics, Prometheus TSDB blocks) use this structure.</p>

<h3>2. Sorted Array (In-Place Ordered)</h3>
<p><strong>Read: O(log n)</strong> — binary search. <strong>Write: O(n)</strong> — shifting elements to maintain order.</p>
<p>Binary search on a sorted array of 1 billion rows takes log₂(1,000,000,000) ≈ 30 comparisons. Extremely fast reads. But inserting a row in the middle of a 1TB sorted file requires shifting up to 1TB of data — completely unusable for tables that receive inserts.</p>
<p><strong>Where databases use this:</strong> SSTable files in LSM trees (see below) — each SSTable is a sorted, immutable file. Immutable means no insertions, so O(n) write cost is never paid after initial creation. SSTables are always written as complete files (from a sorted memtable flush or compaction) and never modified.</p>

<h3>3. Binary Search Tree (BST)</h3>
<p><strong>Read: O(log n) average.</strong> <strong>Write: O(log n) average.</strong> Both degrade to O(n) on skewed inserts (e.g., monotonically increasing keys produce a right-leaning chain).</p>
<p>Conceptually elegant: both reads and writes are O(log n). So why don't databases use BSTs for disk indexes?</p>
<p><strong>The page waste calculation:</strong> A BST node stores exactly one key and two child pointers. On a disk page of 8,192 bytes, a BST node occupies perhaps 32 bytes (8-byte key + 2×8-byte pointers + overhead) — leaving 8,160 bytes completely unused. You pay the I/O cost of reading a full 8KB page to get 32 bytes of useful data: <strong>256× amplification</strong>. A BST for 1 billion rows is ~30 levels deep. Traversing it requires 30 random disk reads at 10ms each = 300ms per query. Completely unusable.</p>

<h3>4. B+ Tree — What Production Databases Actually Use</h3>
<p>The B+ tree solves the BST's page waste by packing as many keys as possible into each node — sized to exactly one disk page. It also eliminates the BST's imbalance problem through automatic rebalancing on every insert and delete.</p>
</div>

<div class="topic">
<h2>B+ Tree: Complete Internals</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>A B+ tree is like a library's card catalog, redesigned so each card holds 400 entries instead of one. The outer cards (internal nodes) are pure directories — they tell you which drawer to open next. Only the last drawer (leaf nodes) contains the actual books (row data). All the last drawers are connected left-to-right with a chain, so "give me all books by authors A through M" means opening the A drawer and just walking the chain — no backtracking to the top.</p></div>

<h3>Node Structure: Why Node Size = Page Size</h3>
<p>The fundamental design decision: set the B+ tree node size equal to one disk page (8KB for PostgreSQL, 16KB for InnoDB). This ensures traversing one level of the tree costs exactly one I/O operation. This is not a coincidence — it is the design intent. Every database that uses B+ trees makes this same deliberate choice.</p>

<p><strong>Key capacity per node:</strong> For a PostgreSQL index on an int8 (8-byte) primary key:</p>
<ul>
  <li>Index entry: 8-byte key + 6-byte heap pointer = 14 bytes</li>
  <li>With page header overhead (~24 bytes): roughly 580 entries per 8KB leaf page</li>
  <li>Internal nodes store only keys (no data pointers), allowing ~580–600 keys per internal page</li>
  <li>Industry rule of thumb: assume <strong>400–500 entries per node</strong> (conservative, accounts for variable overhead)</li>
</ul>

<h3>The Tree Height Math (What Architects Carry in Their Head)</h3>
<div class="box n"><div class="box-lbl">B+ Tree Height vs Row Count (500 entries/node)</div>
<table>
  <thead><tr><th>Tree Height</th><th>Max Rows Covered</th><th>I/Os per Lookup</th><th>Example Scale</th></tr></thead>
  <tbody>
    <tr><td>1 level (root = leaf)</td><td>~500</td><td>1</td><td>Tiny lookup table</td></tr>
    <tr><td>2 levels</td><td>~250,000</td><td>2</td><td>Small application</td></tr>
    <tr><td>3 levels</td><td>~125,000,000 (125M)</td><td>3</td><td>Medium-large OLTP app</td></tr>
    <tr class="hr"><td><strong>4 levels</strong></td><td><strong>~62,500,000,000 (62.5B)</strong></td><td><strong>4</strong></td><td><strong>Most production databases</strong></td></tr>
    <tr><td>5 levels</td><td>~31,250,000,000,000 (31T)</td><td>5</td><td>Beyond any current database</td></tr>
  </tbody>
</table>
</div>

<p>This is the most important fact about B+ trees: <strong>finding any row in any table containing up to 62.5 billion rows requires exactly 4 disk I/Os</strong>. 4 × 50μs (NVMe) = 200μs. 4 × 10ms (HDD) = 40ms. The tree never needs to be deeper because it fans out so aggressively at each level.</p>

<p><strong>The root page is always in the buffer pool</strong> (it is the hottest page in the entire tree). In practice, for a 3-level tree, the single root page and the ~500 second-level pages are usually all cached — meaning most index lookups touch 0–1 pages on disk (just the leaf). The theoretical "4 I/Os" is a worst case; the practical average in a well-tuned system is closer to 0.1–0.5 I/Os with a good buffer pool hit rate.</p>

<h3>Three Rules That Distinguish B+ Trees from Generic B-Trees</h3>
<ol>
  <li><strong>Internal nodes store keys only — no values.</strong> This maximises the fan-out (number of children per node). More keys per internal node = shallower tree = fewer I/Os. A generic B-tree stores both keys and values at every level, reducing fan-out and forcing a deeper tree for the same data volume.</li>
  <li><strong>Values live exclusively at leaf nodes.</strong> Every lookup ends at a leaf. This makes lookup time exactly O(tree height) — no variance based on whether the key happens to be at an internal node (as in a generic B-tree).</li>
  <li><strong>Leaf nodes are linked in a doubly-linked list.</strong> All leaves, left to right, are connected by neighbour pointers. This enables range scans (<code>WHERE id BETWEEN 1000 AND 2000</code>) to traverse the leaf level without returning to the root — find the start leaf with one root-to-leaf traversal, then walk the list. Critically, range scans on a B+ tree are sequential page reads — exploiting the sequential I/O advantage from Chapter 1.</li>
</ol>

<h3>Node Splits: How the Tree Stays Balanced</h3>
<p>When a leaf node fills completely, a <strong>node split</strong> occurs:</p>
<ol>
  <li>Allocate a new leaf node.</li>
  <li>Divide the existing leaf's entries: the lower half stays in the old node, the upper half moves to the new node.</li>
  <li>The <strong>middle key is promoted upward to the parent internal node</strong> as a separator — this is what tells future lookups "values ≤ middle go left, values &gt; middle go right."</li>
  <li>If the parent internal node is also full, it splits too, promoting its middle key to its own parent.</li>
  <li>In the rare case the root splits, a new root is created — the only way the tree grows one level.</li>
</ol>

<p>This is how B+ tree height stays bounded at O(log n) regardless of insert order. Unlike a BST which can degrade to O(n) with monotonically increasing keys, a B+ tree always stays balanced because splits propagate upward rather than skewing the tree.</p>

<div class="box f"><div class="box-lbl">B+ Tree Hot-Spot Problem Under Sequential Inserts</div>
<p>When primary keys are monotonically increasing (auto-increment integers, timestamps), every new insert goes to the rightmost leaf page. Under high concurrent insert load, multiple transactions contend on this one page — a serialization bottleneck called a <strong>right-hand contention</strong> or <strong>insert hot-spot</strong>.</p>
<p><strong>Solutions:</strong></p>
<ul>
  <li><strong>UUID v4</strong> as primary key: random distribution across the tree eliminates hot-spot. Cost: slightly worse cache locality for range scans (rows with adjacent keys are on random pages). Index size also grows ~20% due to longer key width.</li>
  <li><strong>UUID v7</strong>: time-ordered with random suffix — distributes inserts across many leaf pages (better than sequential, worse than fully random) while preserving rough time-order for range scans.</li>
  <li><strong>Hash partitioning</strong>: split the table into N partitions by hash of primary key. Each partition has its own B+ tree root — N independent insert targets instead of one.</li>
  <li><strong>Fill factor</strong>: set <code>fillfactor=70</code> on the index — leaves are only 70% full on build. Provides headroom for concurrent inserts before splits are needed.</li>
</ul>
</div>

<h3>Concurrent B+ Tree Operations: Latch Coupling</h3>
<p>B+ trees in production databases must handle many concurrent readers and writers. Locking the entire tree for each operation would serialize all queries — unacceptable. The solution is <strong>latch coupling</strong> (also called lock-coupling or crab-walking):</p>
<ul>
  <li>Acquire a latch (lightweight in-memory lock, not a database lock) on the root.</li>
  <li>Acquire a latch on the child. Release the root latch only if the child is "safe" — meaning an insert won't require a split, or a delete won't require a merge.</li>
  <li>Continue down the tree, always holding the latch on the current node while acquiring the next.</li>
  <li>At the leaf, hold the leaf latch, perform the operation, release.</li>
</ul>
<p>Read-only operations use shared latches (multiple readers simultaneously). Writes use exclusive latches (one writer, no concurrent readers on that node). This allows concurrent reads at all levels and concurrent writes to non-overlapping subtrees.</p>

<div class="mermaid">
graph TD
    Root[Root Node<br/>keys only<br/>one page]
    I1[Internal Node<br/>keys + child ptrs<br/>one page]
    I2[Internal Node<br/>keys + child ptrs<br/>one page]
    L1[Leaf Node<br/>keys + values<br/>one page]
    L2[Leaf Node<br/>keys + values<br/>one page]
    L3[Leaf Node<br/>keys + values<br/>one page]
    Root --> I1
    Root --> I2
    I1 --> L1
    I1 --> L2
    I2 --> L3
    L1 <-->|sibling ptrs| L2
    L2 <-->|sibling ptrs| L3
</div>
<p class="diagram-cap">Figure 3.1 — B+ tree structure. Internal nodes hold keys only; leaves hold values and link to neighbours for range scans.</p>

<div class="box xr"><div class="box-lbl">Related Deep Dives — B+ Tree</div>
<ul>
  <li><strong>vutr — "What Makes OLTP Databases So Quick"</strong>: Deep dive on why B-Trees maximize I/O bandwidth utilization. Key passage: "B-Tree implementations universally employ Write-Ahead Logging. The system must write any B-tree modification to this file before it can be applied to the pages." Directly connects B+ tree structure to WAL necessity.</li>
  <li><strong>lucsystemdesign — "Database Indexing Clearly Explained"</strong>: Covers cost-based optimizer decisions for index selection. Explains the write tax of indexes and why you shouldn't index everything — crucial for the architect's decision framework. Quote: "The optimizer decides to use an index when its cost model estimates that the index path is cheaper than reading the table directly."</li>
</ul>
</div>
</div>

<div class="topic">
<h2>LSM Tree: Complete Internals</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>An LSM tree treats writes like a sticky-note pad: you never cross anything out, you just keep writing new notes at the top. When the pad is full, you sort all the notes into a permanent file. Over time you have many files, and finding a note means checking all the files. A "bloom filter" on each file lets you skip the search instantly if the note definitely isn't there. Periodically, you merge the files to reduce the number you need to check.</p></div>

<h3>Write Path: Memtable → SSTable</h3>
<p>All writes first land in an in-memory sorted data structure called the <strong>memtable</strong> — typically a red-black tree or skip list that maintains sorted order. Writes to the memtable are O(log m) where m is the memtable size (usually 64MB–256MB) — very fast since it's purely in-memory.</p>

<p>When the memtable reaches its size threshold, it is <strong>flushed to disk as an SSTable</strong> (Sorted String Table): a sorted, immutable file containing all the memtable's key-value pairs. The flush is one large sequential write — exploiting sequential I/O speed. The flushed memtable becomes a new in-memory memtable for subsequent writes. Writes to WAL accompany every memtable write for crash recovery (even LSM trees need WAL).</p>

<h3>SSTable Format</h3>
<p>Each SSTable file contains:</p>
<ul>
  <li><strong>Data blocks:</strong> Sorted key-value pairs, divided into 4KB–64KB data blocks for efficient reading</li>
  <li><strong>Index block:</strong> Maps the first key of each data block to the block's file offset — enables binary search to find any key's data block in O(log (SSTable size))</li>
  <li><strong>Bloom filter:</strong> A space-efficient probabilistic data structure that answers "is key X definitely NOT in this SSTable?" with zero false negatives and configurable false positive rate (~1% at 10 bits/key). Allows read operations to skip entire SSTable files that don't contain the target key — critical for read performance</li>
  <li><strong>Footer:</strong> Offsets to index block and bloom filter block, plus checksum</li>
</ul>

<h3>Compaction: Controlling the Number of SSTables</h3>
<p>Without compaction, SSTables accumulate indefinitely — reads would need to search every SSTable file. Compaction merges SSTables, removes deleted/overwritten entries, and reorganises data into a tiered structure:</p>

<p><strong>Leveled compaction</strong> (default in RocksDB, LevelDB):</p>
<ul>
  <li><strong>L0:</strong> Freshly flushed SSTables. Files in L0 may have overlapping key ranges — reads must check all L0 files. Target: 4–8 files before triggering compaction to L1.</li>
  <li><strong>L1:</strong> Target size (e.g., 256MB). Files in L1 have non-overlapping key ranges — only one L1 file can contain any given key. Compaction picks one L1 file and all overlapping L0 files, merges them, and writes back to L1.</li>
  <li><strong>L2…Lk:</strong> Each level is 10× the size of the previous. L2 = 2.56GB, L3 = 25.6GB, etc. Key ranges are non-overlapping within each level ≥1.</li>
</ul>

<div class="mermaid">
graph LR
    W[Write] --> M[Memtable<br/>in memory]
    M -->|flush when full| L0[L0 SSTables<br/>may overlap<br/>~64MB]
    L0 -->|compact| L1[L1 SSTables<br/>non-overlapping<br/>~640MB]
    L1 -->|compact| L2[L2 SSTables<br/>non-overlapping<br/>~6.4GB]
    L2 --> Ln[Ln SSTables<br/>10x bigger each level]
</div>
<p class="diagram-cap">Figure 3.2 — LSM write path. Writes go to memory first, flush to L0, then compact down levels. Write amplification = 10–30×.</p>

<h3>The Three Amplification Factors</h3>
<div class="box n"><div class="box-lbl">LSM Tree Amplification Analysis</div>
<table>
  <thead><tr><th>Factor</th><th>Definition</th><th>Typical Value</th><th>Tuning Lever</th></tr></thead>
  <tbody>
    <tr><td><strong>Write Amplification (WA)</strong></td><td>Bytes written to storage / bytes written by application</td><td>10–30× (leveled)</td><td>Increase level size ratio (10× → 5×) reduces WA, increases space amp</td></tr>
    <tr><td><strong>Read Amplification (RA)</strong></td><td>Files checked per read in worst case</td><td>L0 files + 1 per level = ~10</td><td>Bloom filters reduce to ~1.01 (1% false positive rate)</td></tr>
    <tr><td><strong>Space Amplification (SA)</strong></td><td>Storage used / logical data size</td><td>1.1–1.5× steady state</td><td>Aggressive compaction reduces SA, increases WA</td></tr>
  </tbody>
</table>
</div>

<p><strong>Write amplification math:</strong> A key-value pair written at L0 is rewritten when compacted to L1 (1 rewrite), then from L1 to L2 (1 more), then L2 to L3 (1 more). With 5 levels and a 10× size ratio, each byte is rewritten approximately 10× total. WA of 10 means your NVMe drive's rated endurance (e.g., 600 TBW) is consumed 10× faster than expected. For SLC enterprise SSDs this is fine; for consumer TLC SSDs with 200 TBW lifetime, a 100MB/s write workload (8.64TB/day) wears out the drive in 23 days at WA=10.</p>

<div class="mermaid">
graph LR
    BTree[B+ Tree]
    LSM[LSM Tree]
    BTree -->|write| WA1[Write Amp: 1-3x<br/>random I/O per update]
    BTree -->|read| RA1[Read Amp: 1x<br/>log N I/Os]
    BTree -->|space| SA1[Space Amp: 1x<br/>no extra copies]
    LSM -->|write| WA2[Write Amp: 10-30x<br/>sequential I/O]
    LSM -->|read| RA2[Read Amp: 5-10x<br/>check all levels]
    LSM -->|space| SA2[Space Amp: 1.1-1.5x<br/>dead keys linger]
</div>
<p class="diagram-cap">Figure 3.3 — Trade-off matrix. Every index choice is a point in the (write-amp, read-amp, space-amp) triangle.</p>

<div class="box f"><div class="box-lbl">LSM Write Stall: The Operational Risk</div>
<p>When L0 file count grows faster than compaction can merge them (write burst exceeds compaction throughput), RocksDB first slows down writes (<strong>write slowdown</strong> at <code>level0_slowdown_writes_trigger</code>, default 20 files), then stops writes entirely (<strong>write stall</strong> at <code>level0_stop_writes_trigger</code>, default 36 files) until compaction catches up.</p>
<p><strong>Why it happens:</strong> Compaction is I/O bound. If write throughput temporarily exceeds compaction I/O budget, L0 fills faster than it's drained. Peak write events (batch imports, viral spikes) are the common trigger.</p>
<p><strong>Monitoring:</strong> <code>rocksdb.num-files-at-level0</code>, <code>rocksdb.estimate-pending-compaction-bytes</code>. <strong>Mitigation:</strong> Increase compaction threads (<code>max_background_compactions</code>), rate-limit incoming writes during compaction backlog, pre-allocate compaction I/O budget.</p>
</div>

<div class="box xr"><div class="box-lbl">Related Deep Dives — LSM Trees</div>
<ul>
  <li><strong>vutr — "I spent 8 hours learning the ClickHouse MergeTree Table Engine"</strong>: Real-world LSM implementation at scale. ClickHouse uses a "parts" model (LSM-inspired): immutable data chunks merged in background. Shows how sparse indexing works at scale — 8192-row granules, single index mark per granule, not per row. Key insight: MergeTree's primary index is sparse to avoid updating per-row, solving the index write amplification problem.</li>
  <li><strong>vutr — "OLTP vs OLAP: Making changes to the data"</strong>: Contrasts LSM append-only writes against B-Tree slotted page updates. Quote: "All changes — insertions, updates, or deletions — are handled by appending new records to a sequential log... To add a new row, we write at the end of the log." Also introduces Copy-on-Write (CoW) as a third alternative to LSM/B-tree for analytics databases.</li>
  <li><strong>vutr — "I spent another 6 hours understanding the design principles of Snowflake"</strong>: Shows how modern cloud data warehouses (Snowflake, Delta Lake, Iceberg) apply LSM-like principles with immutable S3 files and metadata-based versioning — delegating durability to the storage layer rather than implementing WAL.</li>
</ul>
</div>
</div>

<div class="topic">
<h2>Hash Indexes: The Forgotten Third Option</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>A hash index is like a perfectly organised phone book where every name maps to exactly one page number — you jump straight to it. But "give me everyone with last names from A to M" is impossible — the hash scrambled the names, so there's no concept of alphabetical order.</p></div>

<p>Hash indexes map each key to a hash bucket containing the row location. Lookup is O(1) — compute hash, jump to bucket, return row location. Inserts are O(1). Range queries are <strong>impossible</strong> — hashing destroys key ordering.</p>

<p><strong>When to use a hash index:</strong> Exclusively for exact-match lookups on equality predicates (<code>WHERE user_id = 42</code>, <code>WHERE session_token = 'abc'</code>). Never for range queries, sorting, or pattern matching.</p>

<div class="box d"><div class="box-lbl">Hash Index vs B+ Tree: Decision</div>
<table>
  <thead><tr><th>Criteria</th><th>Hash Index</th><th>B+ Tree Index</th></tr></thead>
  <tbody>
    <tr><td>Exact match (<code>= value</code>)</td><td class="g">O(1) — faster</td><td class="y">O(log n) — slightly slower</td></tr>
    <tr><td>Range queries (<code>BETWEEN</code>, <code>&gt;</code>, <code>&lt;</code>)</td><td class="rd">Impossible</td><td class="g">O(log n + k)</td></tr>
    <tr><td>Prefix match (<code>LIKE 'abc%'</code>)</td><td class="rd">Impossible</td><td class="g">O(log n + k)</td></tr>
    <tr><td>Sorted output (<code>ORDER BY</code>)</td><td class="rd">Impossible</td><td class="g">Leaf scan</td></tr>
    <tr><td>Multi-column index</td><td class="rd">Limited (full key only)</td><td class="g">Supports prefix queries</td></tr>
    <tr><td>Memory usage</td><td class="g">Lower (compact buckets)</td><td class="y">Higher (tree structure overhead)</td></tr>
  </tbody>
</table>
</div>

<p><strong>Real usage:</strong> PostgreSQL has a Hash index type but it was historically not WAL-logged (meaning it would be lost on crash) until PostgreSQL 10. It's rarely used. Redis is a hash table at its core — pure key-value, no range queries, maximum O(1) performance. Memcached is the same. MySQL InnoDB supports adaptive hash indexes — the engine automatically builds a hash index on B+ tree leaf pages that are accessed very frequently, adding a hash lookup shortcut on top of the B+ tree. This is transparent to the application.</p>
</div>

<div class="topic">
<h2>Beyond B+ Trees: Bitmap Indexes and When to Use Them</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>If a column has only 5 distinct values across 100 million rows (like status: PENDING/ACTIVE/CLOSED/SUSPENDED/DELETED), a B+ tree index is nearly useless — 20 million rows match each value, so the optimizer skips the index and does a full scan anyway. A bitmap index instead stores one bit per row per distinct value. To find all ACTIVE rows, you read one bitset. To find all ACTIVE AND US rows, you AND two bitsets together — a single CPU instruction handles 64 rows at once.</p></div>

<h3>Bitmap Index Architecture</h3>
<p>A bitmap index on a column with cardinality N creates N bitsets, each containing one bit per row in the table. Bit i in bitset V is 1 if row i has value V. For a 100M-row table with 5 distinct values, the index is 5 × (100M / 8) = 62.5MB — very compact. Read operations use bitwise AND/OR/NOT to combine predicates across multiple columns in hardware-accelerated operations.</p>

<p><strong>Multi-column predicates are free:</strong> <code>WHERE status = 'ACTIVE' AND region = 'US' AND tier = 'PREMIUM'</code> becomes three bitset ANDs — three passes over 12.5MB each. On modern CPUs with SIMD instructions (AVX-512), this processes 512 bits per clock cycle.</p>

<h3>PostgreSQL Bitmap Index Scans</h3>
<p>PostgreSQL does not have a native bitmap index type (unlike Oracle or Redshift), but it has a <strong>bitmap index scan operator</strong> that uses existing B-tree indexes. When the planner estimates medium selectivity (1–10% of rows), it uses a "Bitmap Heap Scan": collect all matching TIDs from the B-tree index into an in-memory bitmap, sort them by heap page, then fetch heap pages in sequential order. This converts random I/O (regular index scan) into sequential I/O — often dramatically faster for medium-selectivity predicates.</p>
<p>Multiple indexes can be combined: <code>WHERE status = 'ACTIVE' AND created_at &gt; '2024-01-01'</code> builds two bitmaps (one from each index) and ANDs them — <em>BitmapAnd</em> in EXPLAIN output.</p>

<h3>Decision: Bitmap vs B+ Tree</h3>
<div class="box d"><div class="box-lbl">Bitmap vs B+ Tree Index Decision</div>
<table>
  <thead><tr><th>Cardinality Signal</th><th>Choose</th><th>Reason</th></tr></thead>
  <tbody>
    <tr><td>Cardinality &lt; 100 distinct values, table &gt; 1M rows</td><td class="g">Bitmap (native in Oracle/Redshift)</td><td>Bitset AND/OR is O(N/64) per query; B+ tree has poor selectivity at high cardinality</td></tr>
    <tr><td>Cardinality 100–1,000 distinct values</td><td class="y">Test both; depends on query mix</td><td>Grey zone; benchmark with realistic workload</td></tr>
    <tr><td>Cardinality &gt; 1,000 distinct values</td><td class="g">B+ Tree</td><td>Each value is selective enough for good index pruning</td></tr>
    <tr><td>Write-heavy table (OLTP)</td><td class="rd">Avoid native bitmap indexes</td><td>Bitmap indexes require row-level locking across the full bitset on every insert/update — serialises concurrent writes</td></tr>
    <tr><td>Read-only or append-only (OLAP, data warehouse)</td><td class="g">Bitmap ideal</td><td>No write lock penalty; Redshift, Oracle DW, DuckDB all use native bitmap indexes for fact table columns</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="topic">
<h2>Write Skew and Lost Updates: MVCC Edge Cases</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>MVCC gives every transaction a consistent snapshot of the database and lets reads and writes proceed without blocking each other. But this non-blocking nature has two sharp edges: Lost Updates (two concurrent transactions both overwrite the same row, one overwrites the other's change) and Write Skew (two transactions each read the same constraint, both conclude it's safe to proceed, both write — and together they violate the constraint that each individual check said was fine).</p></div>

<h3>Lost Update</h3>
<p>Two transactions both read a counter (value = 100) and increment it:</p>
<ul>
  <li>T1 reads counter → 100. T2 reads counter → 100.</li>
  <li>T1 writes counter = 101 and commits.</li>
  <li>T2 writes counter = 101 and commits.</li>
  <li>Final value: 101. Expected: 102. T1's increment was silently overwritten.</li>
</ul>
<p>This happens under Read Committed and Repeatable Read isolation levels with plain <code>UPDATE counter SET value = value_from_app + 1</code> when the application reads then writes separately. The fix: use <code>UPDATE counter SET value = value + 1</code> (atomic at the database level) or <code>SELECT FOR UPDATE</code> before reading.</p>

<h3>Write Skew</h3>
<p>Two on-call doctors T1 and T2 each check: "Are there at least 2 doctors on call?" Both see yes (currently 2). Both decide to take the day off. Both commit. Now 0 doctors are on call — violating the invariant both thought they were preserving. Write skew cannot occur under Serializable isolation, but does occur under Repeatable Read (and Read Committed).</p>
<p><strong>Classic write skew examples:</strong></p>
<ul>
  <li><strong>Meeting room booking:</strong> T1 and T2 both check "is room 101 free at 3pm?" (yes). Both book it. Both commit. Double-booked.</li>
  <li><strong>Username uniqueness:</strong> T1 and T2 both check "does username 'alice' exist?" (no). Both insert it. Both commit (without a unique constraint). Duplicate username.</li>
  <li><strong>Account balance:</strong> T1 and T2 both check "is balance ≥ withdrawal amount?" Both see yes. Both withdraw. Account goes negative.</li>
</ul>

<h3>Solutions in PostgreSQL</h3>
<ul>
  <li><strong><code>SELECT FOR UPDATE</code>:</strong> Acquires an exclusive row lock before reading. T2's <code>SELECT FOR UPDATE</code> blocks until T1 commits or rolls back. T2 then re-reads with the updated data. Prevents both lost update and write skew for the locked rows. Works at Read Committed level.</li>
  <li><strong>Serializable Snapshot Isolation (SSI):</strong> Set <code>SET TRANSACTION ISOLATION LEVEL SERIALIZABLE</code>. PostgreSQL tracks read-write dependencies between transactions. If a cycle is detected (T1 read what T2 wrote, T2 read what T1 wrote), one transaction is aborted with <code>ERROR: could not serialize access due to read/write dependencies</code>. The application must retry. This prevents write skew without explicit locking, but introduces abort overhead.</li>
  <li><strong>Unique constraints + advisory locks:</strong> For uniqueness-type write skew (username example), a unique index is the correct solution — the database enforces it at the constraint level regardless of isolation level.</li>
</ul>

<div class="box n"><div class="box-lbl">Isolation Level vs Anomaly Coverage</div>
<table>
  <thead><tr><th>Anomaly</th><th>Read Committed</th><th>Repeatable Read</th><th>Serializable (SSI)</th><th>Fix</th></tr></thead>
  <tbody>
    <tr><td>Lost update (read-modify-write)</td><td class="rd">Possible</td><td class="rd">Possible</td><td class="g">Prevented</td><td>SELECT FOR UPDATE or atomic UPDATE</td></tr>
    <tr><td>Write skew</td><td class="rd">Possible</td><td class="rd">Possible</td><td class="g">Prevented</td><td>SELECT FOR UPDATE or SERIALIZABLE</td></tr>
    <tr><td>Phantom read</td><td class="rd">Possible</td><td class="g">Prevented (PG)</td><td class="g">Prevented</td><td>Repeatable Read sufficient in PostgreSQL</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="topic">
<h2>Decision Framework: Which Structure for Which Workload</h2>

<div class="box d"><div class="box-lbl">Complete Decision Framework</div>
<table>
  <thead><tr><th>Workload Signal</th><th>Choose</th><th>Real Database Example</th></tr></thead>
  <tbody>
    <tr><td>Read:write ≥ 70:30, range queries needed</td><td class="g">B+ Tree</td><td>PostgreSQL, MySQL InnoDB, SQLite</td></tr>
    <tr><td>Write-heavy (time series, event logs, metrics, IoT)</td><td class="g">LSM Tree</td><td>RocksDB, Cassandra, LevelDB, TiKV</td></tr>
    <tr><td>Exact-match only, maximum read speed, no ranges</td><td class="y">Hash Index</td><td>Redis, Memcached, InnoDB adaptive hash</td></tr>
    <tr><td>Append-only, never queried during normal ops</td><td class="y">Unsorted Array</td><td>WAL files, Kafka topics, TSDB blocks</td></tr>
    <tr><td>Large sequential scans, data never changes</td><td class="y">Sorted Array (SSTable)</td><td>Parquet files, analytics cold storage</td></tr>
    <tr><td>Mixed: high writes initially, reads later (audit log)</td><td class="y">LSM → periodic compaction</td><td>RocksDB with bulk ingest mode</td></tr>
  </tbody>
</table>
</div>

<p><strong>The crossover point:</strong> If your write:read ratio is around 50:50, you are in a grey zone. Measure with a realistic benchmark. The hidden cost of LSM trees is operational complexity (compaction tuning, write stalls, bloom filter memory); the hidden cost of B+ trees is write amplification under high-concurrency inserts (hot-spot contention). Choose based on the failure mode you can tolerate, not just the average-case performance.</p>

<div class="box l"><div class="box-lbl">Cross-Connections from This Chapter</div>
<ul>
  <li><strong>→ Ch1 (Page Abstraction):</strong> B+ tree node = one disk page = one I/O. This is the foundational connection: every tree level costs exactly one I/O because nodes are sized to pages.</li>
  <li><strong>→ Ch4 (Page Layout):</strong> Inside each B+ tree leaf page is a slotted page layout (pointer array + variable-size entries). Chapter 4 shows exactly what's inside the "node" that Chapter 3 treats as atomic.</li>
  <li><strong>→ Ch5 (Buffer Manager):</strong> The B+ tree's O(log n) I/O cost is the worst case. With a 99% buffer pool hit rate and hot root/internal pages always cached, practical I/Os per lookup drop to &lt;1. Buffer pool effectiveness multiplies B+ tree performance.</li>
  <li><strong>→ Ch5 (WAL):</strong> WAL is an unsorted append-only array. Its write speed justifies its O(n) read cost because WAL is only read during crash recovery. This directly applies the trade-off from this chapter.</li>
  <li><strong>→ Ch5 (Recovery):</strong> LSM trees need WAL too — the memtable is in-memory and lost on crash. The LSM WAL is simpler than B+ tree WAL (no page-level undo needed) but serves the same durability purpose.</li>
</ul>
</div>

<div class="recall">
<div class="recall-head">Architect's Checkpoint</div>
<div class="q"><span class="q-n">Q1 </span>A BST on a 1 billion row table would need ~30 levels. A B+ tree needs 4. Walk through the exact arithmetic that explains this 7.5× difference in tree height. What is the key structural property that gives B+ trees this advantage?</div>
<div class="q"><span class="q-n">Q2 </span>You're choosing a storage engine for a metrics ingestion system: 500,000 writes/sec, 5,000 reads/sec, all reads are "give me all metrics for host X in the last 5 minutes." Walk through the decision: B+ tree or LSM? Justify using write amplification, read amplification, and the specific access pattern.</div>
<div class="q"><span class="q-n">Q3 </span>Explain the LSM write stall. What is the trigger condition, what operational impact does it have, and what are two architectural choices that reduce the probability of a stall? What is the trade-off of each choice?</div>
<div class="q"><span class="q-n">Q4 </span>Your B+ tree index on a high-volume auto-increment primary key is causing write contention. Name three solutions with different trade-off profiles. Which would you choose for a multi-tenant SaaS application with 10,000 tenants each writing at ~50 rows/sec?</div>
</div>

<div class="box teach"><div class="box-lbl">How to Teach This Chapter</div>
<p><strong>Junior engineer (5 min):</strong> Start with the messy-desk vs filing-cabinet analogy. Ask: "How do you find a specific document in a messy desk?" (Scan everything.) "How about in a filing cabinet sorted alphabetically?" (Go straight to the letter.) "Every database structure is a point between these — and there is no free lunch." Then show the Decision Framework table and ask them to justify which structure they'd use for their current project.</p>
<p><strong>Senior engineer (15 min):</strong> Walk through B+ tree fan-out math: BST = 1 key/node = 30 levels for 1B rows. B+ tree = 500 keys/node = 4 levels. That's the entire justification for the B+ tree. Then contrast LSM: what write amplification means for SSD wear (consumer TLC at WA=10 wears out in weeks at 100MB/s write). End with the three amplifications table and ask them to identify which is the binding constraint for their current system.</p>
<p><strong>Expert architect (30 min discussion):</strong> "Your team is building a new time-series database for 1M metrics/second sustained. You've chosen LSM. Walk me through every operational risk you'll face in year 1." Drive toward: compaction thread tuning, write stall incidents, bloom filter memory budget, L0 file count monitoring, GC pressure on SSDs. Then pivot: "At what write:read ratio would you reconsider and use a B+ tree?" — the answer reveals whether they've internalised the spectrum rather than memorised a rule.</p>
</div>

<div class="box gap"><div class="box-lbl">Questions This Chapter Doesn't Answer</div>
<ul>
  <li>How does fractional cascading (used in some B-tree variants) reduce I/Os for multi-dimensional range queries, and when does it outperform a standard composite index?</li>
  <li>What is the Dostoevsky paper's analysis of the RUM conjecture — can you truly optimise for two of (Read amp, Update amp, Memory amp) simultaneously, or is the triangle fixed?</li>
  <li>When does a columnar storage format (Parquet, ORC) outperform both B+ tree and LSM — and what query pattern makes the crossover point obvious?</li>
  <li>How does FoundationDB's layer architecture allow using B+ trees and LSM concurrently in the same system — and what does this reveal about the structure vs workload mapping?</li>
</ul>
</div>
</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 4: PAGE LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
CH4 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 4 of 5</div>
  <h1>The Cell Layout: How a Database Page Works</h1>
  <div class="ch-src">Source: The BEST Way to Organize Data (in a Database)</div>
  <p class="ch-sum">A database page is 8KB of raw bytes. Inside that page, rows of arbitrary size must be stored, found, inserted, and deleted efficiently. The slotted page design — used by PostgreSQL, SQLite, and others — solves this elegantly. Understanding it explains VACUUM, HOT updates, fill factor, TOAST, and the internal structure of every B+ tree node.</p>
</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>When you run <code>VACUUM</code> and the table doesn't shrink, when HOT updates suddenly stop working and index writes spike, when a <code>jsonb</code> column causes a 50× slowdown — the cause is always inside the 8KB page. The page layout is not an implementation detail; it is the mechanism behind MVCC, VACUUM, HOT updates, and TOAST. Engineers who understand the page can diagnose these problems in minutes. Those who don't spend days adding indexes that don't help.</p>
</div>

<div class="topic">
<h2>B-Tree vs B+ Tree: Where Values Live</h2>

<h3>B-Tree vs B+ Tree: Where Values Live (A Critical Distinction)</h3>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>In a regular B-tree, every node can hold both the key and the actual data value — so a search can stop the moment it finds a key, even in the middle of the tree. In a B+ tree, only the bottom row (leaf nodes) holds values. All other nodes hold only keys used for navigation. This changes everything about how the structure performs.</p>
</div>

<p><strong>B-tree (Bayer 1970 original)</strong>: Internal nodes store <code>(key, value, left_child, right_child)</code> tuples. A search that matches a key in an internal node returns the value immediately — no need to reach a leaf. This seems efficient, but the cost is high: internal nodes are large (key + value + two child pointers), reducing the fanout (how many children per node). A B-tree with 100-byte values and 8-byte keys in an 8KB page holds roughly 60 entries per node, giving ~5 tree levels for 1 billion rows.</p>

<p><strong>B+ tree (the universal database choice)</strong>: Internal nodes store ONLY <code>(key, child_pointer)</code> pairs — no values. Values live exclusively in leaf nodes. This makes internal nodes extremely compact: an 8KB page with 8-byte keys and 6-byte pointers holds ~580 entries. With fanout 580, only 3 tree levels reach 195 million rows; 4 levels reach 113 billion rows. <strong>The fanout advantage of removing values from internal nodes is the entire reason databases use B+ trees instead of B-trees.</strong></p>

<div class="box n"><div class="box-lbl">B-tree vs B+ Tree Internal Node Comparison (8KB page)</div>
<table>
  <thead><tr><th>Property</th><th>B-tree</th><th>B+ tree</th></tr></thead>
  <tbody>
    <tr><td>Internal node stores</td><td>Key + Value + 2 child pointers</td><td>Key + 1 child pointer only</td></tr>
    <tr><td>Entries per 8KB internal node</td><td>~60 (with 100-byte values)</td><td>~580 (keys + pointers only)</td></tr>
    <tr><td>Tree levels for 1B rows</td><td>~5 levels → 5 I/Os</td><td>~3 levels → 3 I/Os</td></tr>
    <tr><td>Range scan support</td><td>Complex (values in all nodes)</td><td>Trivial (leaf sibling pointers)</td></tr>
    <tr><td>Early termination</td><td>Yes (value found in internal node)</td><td>No (must always reach leaf)</td></tr>
    <tr><td>Database usage</td><td>Rare (some file systems)</td><td>Universal (PostgreSQL, MySQL, Oracle, SQL Server)</td></tr>
  </tbody>
</table>
</div>

<p>The trade-off: B+ trees never terminate early in an internal node — every lookup must reach a leaf. But the dramatically higher fanout (580 vs 60) means the tree is 2 levels shallower on average, saving more I/Os than early termination would have recovered. At one billion rows, B+ tree requires 3 I/Os (3 levels); B-tree requires 5 (5 levels). The B+ tree wins despite never short-circuiting.</p>
</div>

<div class="topic">
<h2>The Slotted Page Architecture</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Imagine a hotel's front desk with numbered key slots on the wall. Each slot holds a small card saying "Room 247 is on floor 3, third door on the left." The actual rooms (your data rows) can be any size — a broom cupboard or a penthouse suite. The front desk (pointer array) is always compact, always sorted, always at the same location. To find any room, check the front desk first.</p></div>

<p>The <strong>slotted page</strong> (also called a "cell page" in SQLite) stores two conceptually separate things in one fixed-size page:</p>
<ol>
  <li>A compact array of fixed-size <strong>item identifiers (slots/pointers)</strong> — each just a byte offset and length — at the start of the page</li>
  <li>Variable-size <strong>tuple data</strong> (actual row content) packed from the end of the page inward</li>
</ol>
<p>These two regions grow toward each other. The gap between them is free space available for new rows.</p>

<h3>PostgreSQL Heap Page Format (8KB)</h3>
<p>PostgreSQL's heap page is the canonical slotted page implementation:</p>

<div class="box n"><div class="box-lbl">PostgreSQL Page Structure (8,192 bytes)</div>
<table>
  <thead><tr><th>Region</th><th>Size</th><th>Contents</th><th>Key Fields</th></tr></thead>
  <tbody>
    <tr><td><strong>PageHeaderData</strong></td><td>24 bytes (fixed)</td><td>Page metadata</td><td><code>pd_lsn</code> (8B, WAL position of last change), <code>pd_checksum</code> (2B), <code>pd_flags</code>, <code>pd_lower</code> (end of ItemId array), <code>pd_upper</code> (start of tuple data), <code>pd_special</code> (for index pages)</td></tr>
    <tr><td><strong>ItemId array</strong></td><td>4 bytes × N rows</td><td>Slot array — one entry per row</td><td>Each 4-byte ItemId: 15-bit offset, 2-bit flags (normal/redirect/dead/unused), 15-bit length</td></tr>
    <tr><td><strong>Free space</strong></td><td>Variable</td><td>Gap between ItemId array and tuple data</td><td>New rows take space from both ends: new ItemId from pd_lower upward; new tuple from pd_upper downward</td></tr>
    <tr><td><strong>Tuple data</strong></td><td>Variable</td><td>Actual row content, packed from page end</td><td>Each tuple has its own header (23 bytes) containing MVCC visibility info</td></tr>
    <tr><td><strong>Special space</strong></td><td>0 (heap) or variable (indexes)</td><td>Index-specific metadata</td><td>B+ tree index pages use this for left/right sibling page pointers (the leaf linked list from Ch3)</td></tr>
  </tbody>
</table>
</div>

<div class="mermaid">
graph TD
    PH[Page Header<br/>pd_lsn, pd_lower, pd_upper<br/>8KB fixed]
    IA[Item ID Array<br/>grows DOWN<br/>4 bytes per slot]
    FS[Free Space<br/>between pd_lower and pd_upper]
    TU[Tuples<br/>grow UP from bottom<br/>t_xmin t_xmax t_ctid]
    PH --> IA
    IA --> FS
    FS --> TU
</div>
<p class="diagram-cap">Figure 4.1 — Slotted page layout. Item array grows from top; tuples from bottom. Free space is between pd_lower and pd_upper.</p>

<div class="box d"><div class="box-lbl">The Node-Page Equivalence: Why B+ Tree Nodes Are Exactly One Page</div>
<p>The 8KB PostgreSQL page and the 8KB B+ tree node size are not independent choices — they are the same thing. A B+ tree node <em>is</em> a page. Here is why this alignment is the core design decision:</p>
<ul>
  <li><strong>One node traversal = one I/O</strong>: When you read any byte on a page, you pay for the full 8KB transfer. A node sized to exactly one page means reading one tree level costs exactly one I/O — no more, no less.</li>
  <li><strong>Node smaller than one page</strong>: If a node were 512 bytes in an 8KB page, you'd transfer 8KB but use only 512 bytes of tree data — 16× wasted I/O bandwidth. Worse, the OS and buffer pool cache the full 8KB page whether you needed it or not.</li>
  <li><strong>Node larger than one page</strong>: A 32KB node spanning 4 pages requires 4 sequential I/Os to load one tree node. In a 4-level tree, reading a leaf would cost 4 levels × 4 I/Os = 16 I/Os instead of 4. The entire depth advantage of B+ trees evaporates.</li>
  <li><strong>The practical implication</strong>: PostgreSQL's <code>BLCKSZ</code> compile-time constant (8KB) is the B+ tree node size. Changing BLCKSZ rebuilds the entire storage format — it is not a configuration file parameter. MySQL InnoDB uses 16KB pages (and 16KB B+ tree nodes), configurable at initialization time only.</li>
</ul>
<p>This is the answer to "why did B+ trees win over binary search trees (BSTs)?" — BST nodes are tiny (key + 2 pointers = ~24 bytes) and randomly placed in memory/on disk. Loading one BST level on a random-access disk means paying for a full 8KB page to get 24 bytes of useful data, then repeating for 20–30 levels. A B+ tree fits 580 entries in that same 8KB page and traverses only 4 levels. The node-page equivalence is the entire advantage.</p>
</div>

<h3>Fan-out: Why Internal Nodes Must Store Keys Only</h3>

<p><strong>Fan-out</strong> (branching factor) is the number of child pointers an internal B+ tree node holds. Fan-out determines tree depth: depth = ceil(log_fanout(N)) where N is the row count. Higher fan-out = shallower tree = fewer I/Os per lookup.</p>

<div class="box n"><div class="box-lbl">Fan-out Calculation (8KB page)</div>
<table>
  <thead><tr><th>Node type</th><th>Entry size</th><th>Entries per 8KB page</th><th>Fan-out</th><th>Depth for 1B rows</th></tr></thead>
  <tbody>
    <tr><td>B-tree internal (keys + values)</td><td>8B key + 100B value + 6B pointer = 114B</td><td class="rd">~70</td><td class="rd">70</td><td class="rd">5 levels = 5 I/Os</td></tr>
    <tr><td>B+ tree internal (keys only)</td><td>8B key + 6B pointer = 14B</td><td class="g">~580</td><td class="g">580</td><td class="g">3 levels = 3 I/Os</td></tr>
    <tr><td>Binary search tree node</td><td>8B key + 100B value + 16B (2 ptrs) = 124B</td><td class="rd">1 node</td><td class="rd">2</td><td class="rd">30 levels = 30 I/Os</td></tr>
  </tbody>
</table>
</div>

<p>The 8× difference in fan-out (580 vs 70) is the entire reason B+ trees separate internal nodes (keys only) from leaf nodes (keys + values). Without this separation, the tree would need 2 more levels for the same dataset — adding 2 extra I/Os per lookup, every lookup. At 10,000 queries/second, each saving 2 I/Os at 50μs/I/O saves 1 CPU second per second of throughput.</p>

<p><strong>Internal-only key storage enables binary search within a node too:</strong> The sorted key array in an internal node allows binary search — O(log fanout) comparisons to find the right child pointer. With fanout 580: log₂(580) = ~9 comparisons to find the right child among 580 keys. All in RAM (the page is already loaded). This is why the tree is both wide AND fast to search at each level.</p>

<h3>Tuple Header: MVCC Visibility Information</h3>
<p>Every row (tuple) in a PostgreSQL heap page has a 23-byte header before the actual column data:</p>
<ul>
  <li><strong><code>t_xmin</code> (4 bytes):</strong> Transaction ID of the transaction that inserted this tuple. A tuple is visible only to transactions whose snapshot includes t_xmin as committed.</li>
  <li><strong><code>t_xmax</code> (4 bytes):</strong> Transaction ID of the transaction that deleted or updated this tuple (0 if still current). A tuple with non-zero t_xmax has been logically deleted — it remains physically present until VACUUM removes it.</li>
  <li><strong><code>t_cid</code> (4 bytes):</strong> Command ID within the transaction — distinguishes rows visible to different statements within the same transaction.</li>
  <li><strong><code>t_ctid</code> (6 bytes):</strong> "Current TID" — points to the latest version of this row. On update, the old tuple's t_ctid points to the new tuple's location. Forms a version chain for MVCC.</li>
  <li><strong><code>t_infomask</code> (2 bytes) + <code>t_infomask2</code> (2 bytes):</strong> Bit flags indicating visibility hints (xmin committed, xmax committed, etc.), null bitmap present, has OIDs, and column count.</li>
  <li><strong><code>t_hoff</code> (1 byte):</strong> Offset to actual column data (accounts for variable-length null bitmap).</li>
</ul>

<p>These fields are the foundation of PostgreSQL's MVCC implementation (Chapter 5). Understanding the tuple header is essential for understanding why VACUUM is needed and how visibility decisions are made per-tuple without locking.</p>

<h3>MySQL InnoDB Page Format (16KB)</h3>
<p>InnoDB uses a different but conceptually similar layout:</p>
<ul>
  <li><strong>File Header (38 bytes):</strong> Page number, previous/next page pointers (the leaf linked list), checksum, LSN of last flush, page type.</li>
  <li><strong>Page Header (56 bytes):</strong> Slot count, heap top pointer, garbage space, last insert position, page direction.</li>
  <li><strong>Infimum record:</strong> A fixed pseudo-record representing the lowest possible key — the logical "start" of the page's record chain.</li>
  <li><strong>Supremum record:</strong> A fixed pseudo-record representing the highest possible key — the logical "end."</li>
  <li><strong>User records:</strong> Actual data records stored in a singly-linked list in key order. Unlike PostgreSQL's random placement + pointer array, InnoDB maintains records in physical key order within the page — because InnoDB is a clustered index (the table IS the B+ tree).</li>
  <li><strong>Page Directory:</strong> A sparse array of slot pointers (every 4–8 records) enabling binary search within the page without scanning all records sequentially.</li>
  <li><strong>File Trailer (8 bytes):</strong> Checksum for corruption detection.</li>
</ul>

<p><strong>Key difference from PostgreSQL:</strong> InnoDB stores the entire row inside the B+ tree leaf page (clustered index). PostgreSQL stores only the index key in the index page; the full row is in the heap, accessed via the heap pointer (t_ctid). InnoDB's approach means a primary key lookup reads the data in one I/O (leaf page = data). PostgreSQL's approach means a primary key index lookup reads two pages: the index leaf page, then the heap page. However, PostgreSQL index-only scans (when all needed columns are in the index) eliminate the heap read.</p>
</div>

<div class="topic">
<h2>Insertion, Deletion, and Fragmentation</h2>

<h3>Insertion Algorithm</h3>
<ol>
  <li>Check if the page has enough free space for the new tuple (tuple size + 4 bytes for new ItemId).</li>
  <li>Write the new tuple at the current <code>pd_upper</code> position (packing from the end).</li>
  <li>Add a new ItemId entry at <code>pd_lower</code> position, storing the tuple's offset and length.</li>
  <li>Update <code>pd_lower</code> (advance by 4 bytes) and <code>pd_upper</code> (retreat by tuple size).</li>
  <li>If insufficient free space: trigger a page split (for indexes) or find/create another heap page (for tables).</li>
</ol>
<p>The ItemId array is <em>not</em> kept in sorted key order for heap pages — items are appended as rows are inserted. Sorting is the job of index pages, not heap pages. Heap pages are accessed via ItemId number (the physical row location — page number + item offset, called a TID: Tuple IDentifier or CTID in PostgreSQL).</p>

<h3>Deletion: Logical, Not Physical</h3>
<p>PostgreSQL does <strong>not</strong> immediately remove a deleted row from the page. When a row is deleted:</p>
<ol>
  <li>The tuple's <code>t_xmax</code> is set to the deleting transaction's XID — this marks it as logically deleted.</li>
  <li>The ItemId remains in the array — it now points to a "dead" tuple.</li>
  <li>The tuple's storage space is NOT reclaimed. It remains physically on the page.</li>
</ol>

<p><strong>Why not reclaim immediately?</strong> MVCC requires old row versions to remain visible to concurrent transactions that started before the delete. Transaction T1 might have a snapshot that needs to see the row. Physically removing it immediately would break T1's read. The row must remain until no active transaction can possibly need to see it.</p>

<h3>Fragmentation and the Need for VACUUM</h3>
<p>Over time, deleted and updated tuples accumulate as "dead tuples" — consuming page space but holding no visible data. This causes:</p>
<ul>
  <li><strong>Page bloat:</strong> Pages that are logically 30% full are physically 100% full of dead tuples. New inserts must go to new pages. The table's physical size grows beyond its logical data size.</li>
  <li><strong>Scan overhead:</strong> Sequential scans must visit dead tuples, check their visibility, and skip them. A 10GB table that is 50% dead tuples requires reading 10GB to retrieve 5GB of data.</li>
  <li><strong>Index bloat:</strong> Index entries pointing to dead heap tuples remain in the index until the index is vacuumed. Index scans return dead TIDs that require a heap lookup to confirm dead, wasting I/O.</li>
</ul>

<p><strong>VACUUM mechanics:</strong> PostgreSQL's VACUUM scans heap pages, identifies dead tuples that are no longer visible to any active transaction, reclaims their space by updating ItemId flags to "unused," and updates the free space map (FSM) so future inserts can reuse the space. VACUUM also removes dead index entries. It does NOT reorder tuples within the page (no compaction of fragmented free space within a page — that requires <code>VACUUM FULL</code> or <code>CLUSTER</code>).</p>

<div class="box n"><div class="box-lbl">VACUUM vs VACUUM FULL vs CLUSTER</div>
<table>
  <thead><tr><th>Command</th><th>What It Does</th><th>Table Lock?</th><th>Space Returned to OS?</th><th>When to Use</th></tr></thead>
  <tbody>
    <tr><td><code>VACUUM</code></td><td>Marks dead tuples as reusable; updates FSM and visibility map</td><td class="g">No (ShareUpdateExclusive — concurrent reads/writes allowed)</td><td class="rd">No (reused within table file)</td><td>Routine maintenance; run by autovacuum</td></tr>
    <tr><td><code>VACUUM FULL</code></td><td>Rewrites entire table into a new file with no dead tuples</td><td class="rd">Yes (AccessExclusive — all access blocked)</td><td class="g">Yes (OS sees smaller file)</td><td>One-time reclaim after massive deletes; avoid in production</td></tr>
    <tr><td><code>CLUSTER</code></td><td>Rewrites table in index key order (physically sorted)</td><td class="rd">Yes (AccessExclusive)</td><td class="g">Yes</td><td>After bulk import; improves range scan performance; NOT maintained on future writes</td></tr>
  </tbody>
</table>
</div>

<h3>What Triggers VACUUM: Autovacuum Thresholds</h3>

<p>Manual <code>VACUUM</code> is rarely run in production — the autovacuum daemon handles it automatically. Autovacuum monitors dead tuple accumulation and triggers when two thresholds are crossed simultaneously:</p>

<div class="box n"><div class="box-lbl">Autovacuum Trigger Formula</div>
<p><strong>Trigger condition:</strong> <code>dead_tuples > autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor × table_row_count</code></p>
<table>
  <thead><tr><th>Parameter</th><th>Default</th><th>Meaning</th></tr></thead>
  <tbody>
    <tr><td><code>autovacuum_vacuum_threshold</code></td><td>50 rows</td><td>Minimum dead tuples before autovacuum considers running</td></tr>
    <tr><td><code>autovacuum_vacuum_scale_factor</code></td><td>0.20</td><td>Fraction of live rows that must be dead before trigger fires</td></tr>
    <tr><td><code>autovacuum_vacuum_cost_delay</code></td><td>2ms</td><td>Throttle: pause between I/O bursts to avoid starving foreground queries</td></tr>
    <tr><td><code>autovacuum_max_workers</code></td><td>3</td><td>Max concurrent autovacuum workers across all tables</td></tr>
  </tbody>
</table>
<p><strong>Example:</strong> A 1,000,000-row table. Trigger: 50 + (0.20 × 1,000,000) = 200,050 dead tuples. If the table receives 1,000 updates/second, it accumulates 200,050 dead tuples in ~200 seconds. Autovacuum then runs, cleaning dead tuples at ~10,000 rows/second (limited by <code>autovacuum_vacuum_cost_delay</code>). Duration: ~20 seconds of background I/O.</p>
</div>

<div class="box f"><div class="box-lbl">XID Wraparound: The Emergency VACUUM Trigger</div>
<p>PostgreSQL transaction IDs (XIDs) are 32-bit integers — they wrap around at 2³² = 4.3 billion transactions. As a safety net, autovacuum runs an AGGRESSIVE vacuum (ignoring all other thresholds) when a table's oldest unfrozen XID is within 50 million transactions of the wraparound point.</p>
<p>Configuration: <code>autovacuum_freeze_max_age</code> (default 200M). If any table's <code>age(relfrozenxid)</code> &gt; 200M, aggressive autovacuum begins immediately regardless of dead tuple count. If the table cannot be vacuumed (exclusive lock held, autovacuum disabled), PostgreSQL will eventually shut down ALL write operations at 3M transactions from wraparound — a production emergency.</p>
<p><strong>Monitoring:</strong> <code>SELECT relname, age(relfrozenxid) FROM pg_class WHERE relkind='r' ORDER BY age DESC LIMIT 10;</code> — alert when any table exceeds 150M.</p>
</div>
</div>

<div class="mermaid">
graph LR
    V1[Version 1<br/>xmin=100 xmax=200<br/>name=Alice]
    V2[Version 2<br/>xmin=200 xmax=300<br/>name=Bob]
    V3[Version 3<br/>xmin=300 xmax=inf<br/>name=Carol]
    V1 -->|t_ctid| V2
    V2 -->|t_ctid| V3
</div>
<p class="diagram-cap">Figure 4.2 — MVCC version chain. Each UPDATE creates a new tuple version. Transaction sees the version whose xmin &lt;= its snapshot &lt; xmax.</p>

<div class="box xr"><div class="box-lbl">Related Deep Dives — MVCC</div>
<ul>
  <li><strong>vutr — "ACID For Data Engineers"</strong>: Comprehensive taxonomy of transaction anomalies (dirty reads, phantom reads, write skew, lost updates) and how MVCC/SI prevents each. Key insight: MVCC allows reads without read locks, which is why Postgres can have many readers with no lock contention. Also covers Snapshot Isolation (SI) vs Serializable Isolation.</li>
  <li><strong>vutr — "OLTP vs OLAP: Making changes to the data"</strong>: Concrete row-level implementation — PostgreSQL's UPDATE retains existing row version AND creates a new version. Shows how MVCC connects to the slotted page structure (dead tuples, VACUUM need).</li>
</ul>
</div>

<div class="topic">
<h2>HOT Updates: Avoiding Index Churn</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Normally, updating a row means writing a new copy of the row AND updating every index that points to it. HOT (Heap Only Tuple) updates skip the index updates entirely — if the new row fits on the same page and no indexed column changed, PostgreSQL chains the old and new tuples together within the page, and all existing index entries automatically find the new version by following the chain.</p></div>

<p>An update in PostgreSQL is implemented as: insert new tuple + mark old tuple deleted. This means a single <code>UPDATE</code> of one row normally requires writing a new heap tuple <em>and</em> updating every index entry pointing to that row. For a table with 5 indexes, one UPDATE means 6 writes (1 heap + 5 index entries).</p>

<p><strong>HOT update eligibility requires all three conditions:</strong></p>
<ol>
  <li><strong>No indexed column was changed</strong> — if an indexed column changes, index entries must be updated (different key location in the B+ tree).</li>
  <li><strong>The new tuple fits on the same page</strong> — the chain must be on one page for the optimization to work.</li>
  <li><strong>The page has free space</strong> — controlled by <code>fill_factor</code> (see below).</li>
</ol>

<p>When eligible, PostgreSQL sets a bit in the old tuple's <code>t_infomask</code> (HEAP_HOT_UPDATED) and sets the new tuple's <code>t_infomask</code> (HEAP_ONLY_TUPLE). The old tuple's <code>t_ctid</code> points to the new tuple. Index entries still point to the old tuple's TID. When an index scan returns the old TID, PostgreSQL follows the HOT chain to find the current tuple — no index write needed.</p>

<p><strong>fill_factor interaction:</strong> To guarantee same-page placement for future updates, PostgreSQL pages should not be 100% full when initially populated. <code>fill_factor=70</code> on an update-heavy table means pages are 70% full on initial write, leaving 30% headroom for HOT updates. The cost: 30% more storage and I/O for initial reads. The benefit: dramatically fewer index writes under heavy UPDATE workloads.</p>

<div class="box d"><div class="box-lbl">fill_factor Decision Guide</div>
<table>
  <thead><tr><th>Workload</th><th>fill_factor</th><th>Reason</th></tr></thead>
  <tbody>
    <tr><td>Insert-only (append log, time-series)</td><td>100</td><td>No updates → no need for free space headroom</td></tr>
    <tr><td>Read-heavy, rare updates (&lt;5% rows/day)</td><td>90–100</td><td>Dense pages improve scan efficiency; few updates don't justify waste</td></tr>
    <tr><td>Mixed OLTP (typical web app)</td><td>70–80</td><td>HOT update eligibility on most updates; reduces index churn</td></tr>
    <tr><td>Write-heavy, frequent updates to same rows</td><td>50–70</td><td>Maximum HOT eligibility; accept larger physical table size</td></tr>
    <tr><td>B+ tree index with monotonic inserts</td><td>70–80</td><td>Prevents immediate split on rightmost leaf under sustained inserts</td></tr>
  </tbody>
</table>
</div>

<h3>Fill Factor: Leaving Free Space to Enable HOT Updates</h3>

<p><strong>fill_factor</strong> is a PostgreSQL storage parameter (per table, per index) that controls what percentage of each page is used during INSERT operations. The remaining space is reserved for future UPDATE operations.</p>

<div class="box n"><div class="box-lbl">Fill Factor Values and Trade-offs</div>
<table>
  <thead><tr><th>fill_factor</th><th>Usage</th><th>Effect</th><th>Best For</th></tr></thead>
  <tbody>
    <tr><td>100% (default)</td><td>Pack pages completely on INSERT</td><td>Dense storage, but UPDATE must always find a new page if tuple grows</td><td>Append-only / insert-heavy tables (logs, events)</td></tr>
    <tr><td>70–80%</td><td>Leave 20–30% free space per page</td><td>UPDATEs can write new version on same page (HOT update path), no index update needed</td><td>Update-heavy OLTP tables (orders, users, inventory)</td></tr>
    <tr><td>50%</td><td>Leave half the page empty</td><td>Very infrequent page splits, maximum HOT ratio</td><td>Tables with extremely high UPDATE rate and low INSERT rate</td></tr>
  </tbody>
</table>
</div>

<p><strong>Why this matters for indexes:</strong> Every B+ tree index leaf node is also subject to fill_factor. Index fill_factor default is 90% (not 100% — PostgreSQL already reserves 10% for concurrent inserts to reduce index page splits). Setting index fill_factor to 70–80% on high-write indexes reduces B+ tree node splits, which cascade upward and require parent page rewrites.</p>

<p><strong>Page splits in the B+ tree index:</strong> When a leaf page is full (fill_factor threshold reached) and a new key must be inserted: the leaf node splits into two new leaf nodes. Half the keys go to each. The middle key is promoted as a separator key into the parent internal node. If the parent is also full, the split cascades upward. If the root splits, a new root is created and tree depth increases by 1. Fan-out is so high (400–580 keys per internal node) that root splits are exceedingly rare — a 4-level B+ tree requires ~160 billion rows before the root forces a 5th level.</p>

<div class="box d"><div class="box-lbl">Fill Factor Decision Framework</div>
<ul>
  <li><strong>Table is append-only?</strong> fill_factor 100 (default). No space wasted on updates that never come.</li>
  <li><strong>Table updated frequently, same columns?</strong> fill_factor 70–80. Enables HOT path: UPDATE writes new version in same page, no index touch, VACUUM reclaims old version later.</li>
  <li><strong>Index on a column with random value distribution?</strong> Index fill_factor 70–80 to reduce cascading splits under concurrent inserts.</li>
  <li><strong>Table is a reporting / analytics table, rarely updated?</strong> fill_factor 100. Storage density > update performance.</li>
</ul>
<p>Check HOT ratio: <code>SELECT n_tup_hot_upd / NULLIF(n_tup_upd,0) FROM pg_stat_user_tables WHERE relname = 'your_table'</code>. If HOT ratio &lt; 0.5 on an update-heavy table, lower fill_factor.</p>
</div>
</div>

<div class="topic">
<h2>TOAST: Handling Oversized Rows</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>An 8KB page can't hold a 1MB text column. TOAST (The Oversized-Attribute Storage Technique) is PostgreSQL's solution: if a row is too large, it slices off the big columns, compresses them, stores them in a separate hidden table, and puts a tiny pointer in the main row. The main table stays dense; big values live out of the way.</p></div>

<p>PostgreSQL's TOAST kicks in when a row exceeds approximately 2KB (TOAST_TUPLE_THRESHOLD, 25% of a heap page). Large attributes are processed according to their storage strategy before the row is stored:</p>

<div class="box n"><div class="box-lbl">TOAST Storage Strategies</div>
<table>
  <thead><tr><th>Strategy</th><th>Compress?</th><th>Store Out-of-Line?</th><th>Default For</th><th>Best For</th></tr></thead>
  <tbody>
    <tr><td><code>PLAIN</code></td><td>No</td><td>No</td><td>int, bool, float</td><td>Fixed-size types that can't be TOAST'd</td></tr>
    <tr><td><code>EXTENDED</code></td><td>Yes (first)</td><td>Yes (if still large)</td><td>text, bytea, jsonb</td><td>Most variable-length columns</td></tr>
    <tr><td><code>EXTERNAL</code></td><td>No</td><td>Yes (always)</td><td>—</td><td>Binary data you'll always retrieve in full (pre-compressed images)</td></tr>
    <tr><td><code>MAIN</code></td><td>Yes (first)</td><td>Yes (last resort)</td><td>—</td><td>Columns accessed frequently — try to keep in main table</td></tr>
  </tbody>
</table>
</div>

<p><strong>TOAST table structure:</strong> Each table with TOASTable columns has a hidden <code>pg_toast.pg_toast_NNNN</code> table. TOAST values are stored in 2KB chunks, each with a chunk sequence number. Retrieving a TOAST'd value requires an additional heap scan of the TOAST table — typically 1 I/O per chunk, plus index I/O to find the chunks. For a 100KB JSONB column, this is ~50 chunks = ~50+ I/Os just to read one column.</p>

<p><strong>Architectural implication:</strong> Avoid storing large BLOBs (images, PDFs, videos) in PostgreSQL columns. The TOAST overhead (extra table, chunked storage, separate I/O path) adds significant latency compared to storing a URL/path in the database and the actual binary in object storage (S3). A <code>bytea</code> column for a 10MB file means 5,000 TOAST chunks, requiring thousands of I/Os per read.</p>

<div class="box l"><div class="box-lbl">Cross-Connections from This Chapter</div>
<ul>
  <li><strong>→ Ch3 (B+ Tree nodes):</strong> B+ tree index pages use the same slotted page layout. The "special space" at the end of index pages stores the left/right sibling pointers — the leaf linked list that enables range scans.</li>
  <li><strong>→ Ch5 (MVCC):</strong> The t_xmin and t_xmax fields in the tuple header ARE the MVCC mechanism. Chapter 5 explains how these fields are used to determine row visibility for each transaction's snapshot.</li>
  <li><strong>→ Ch5 (Buffer Manager):</strong> VACUUM requires acquiring exclusive access to pages, reading them from the buffer pool, modifying them (marking dead tuples), and writing them back. Heavy VACUUM activity competes with query I/O for buffer pool space.</li>
  <li><strong>→ Ch5 (WAL):</strong> Every page modification — including VACUUM'ing dead tuples — is WAL-logged. A table with high dead tuple accumulation generates significant WAL volume just from autovacuum activity.</li>
</ul>
</div>

<div class="recall">
<div class="recall-head">Architect's Checkpoint</div>
<div class="q"><span class="q-n">Q1 </span>A PostgreSQL table receiving 10,000 updates/sec on non-indexed columns is showing high WAL volume and slow index bloat growth. Diagnose the cause and prescribe the exact changes (table DDL and/or config parameters) that would activate HOT updates for this workload.</div>
<div class="q"><span class="q-n">Q2 </span>Explain why PostgreSQL uses logical deletion (marking t_xmax) rather than physically removing rows immediately. What concurrent access scenario would break if rows were physically removed on delete?</div>
<div class="q"><span class="q-n">Q3 </span>Your PostgreSQL table has a <code>document jsonb</code> column averaging 150KB per row. A read of 1,000 rows is taking 12 seconds. Diagnose the TOAST-related cause and propose two architectural solutions that would fix it.</div>
</div>

<div class="box teach"><div class="box-lbl">How to Teach This Chapter</div>
<p><strong>Junior engineer (5 min):</strong> Show the hotel-desk analogy: numbered key slots on the wall (the ItemId array), rooms of any size on the floors (the tuples). Ask: "Why don't we just store rows sorted in the page?" Because insertion requires shifting — the pointer array lets us put rows anywhere and just update a 4-byte slot. Then show: an UPDATE in PostgreSQL is an INSERT + logical DELETE. That's why VACUUM exists.</p>
<p><strong>Senior engineer (15 min):</strong> Walk through the HOT update conditions: no indexed column changed + fits on same page + page has free space. Ask them to mentally simulate a 10,000 updates/sec workload on a table with <code>fillfactor=100</code> — every update goes off-page, every index gets written, WAL explodes. Then change to <code>fillfactor=70</code> and walk through the same scenario. Quantify the difference: 5 indexes × 10,000 updates × (no HOT) vs 5 indexes × 10,000 updates × (HOT eligible = 0 index writes). That's 50,000 index writes/sec eliminated.</p>
<p><strong>Expert architect (30 min discussion):</strong> "You're seeing autovacuum unable to keep up on your main orders table — dead tuple count keeps growing despite autovacuum running. What are the three possible root causes and how do you diagnose each?" Drive toward: (1) a long-running transaction holding the oldest XID, blocking vacuum from reclaiming; (2) autovacuum cost_delay throttling too aggressively; (3) table bloat already so severe that vacuum I/O budget is exhausted before finishing. Each requires a different fix.</p>
</div>

<div class="box gap"><div class="box-lbl">Questions This Chapter Doesn't Answer</div>
<ul>
  <li>How does InnoDB's clustered index change the page layout trade-offs when the primary key is a UUID vs an auto-increment integer — specifically, page fragmentation patterns?</li>
  <li>What is the exact mechanism by which <code>pg_repack</code> reclaims space without an AccessExclusive lock — and when does it still cause visible latency spikes?</li>
  <li>How does PostgreSQL's visibility map interact with Index-Only Scans — and what query pattern causes the visibility map to be thrashed, eliminating the optimisation?</li>
  <li>At what table size does TOAST chunking overhead become the dominant I/O cost for a <code>jsonb</code> column — and is there a PostgreSQL version or extension that addresses this?</li>
</ul>
</div>
</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 5: STORAGE ENGINE COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────
CH5 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 5 of 5</div>
  <h1>The 5 Core Components of a Storage Engine</h1>
  <div class="ch-src">Source: Data Storage Engines: The 5 Must-Know Components</div>
  <p class="ch-sum">Every relational database storage engine is built from five interlocking subsystems. Understanding each one individually is not enough — the architectural insight comes from understanding how they interact: how MVCC enables lock-free reads, how WAL enables both durability and write performance, how the buffer manager makes the previous four chapters' I/O costs nearly irrelevant in a well-tuned system.</p>
</div>

<div class="box why"><div class="box-lbl">Why This Chapter Matters</div>
<p>You can master every data structure and every page layout in this book — and still misconfigure a production database in a way that loses data on the next server restart. ACID is not a feature you turn on; it is an emergent property of five components working together correctly. When a junior engineer asks "why do we need VACUUM?" or "what does synchronous_commit=off actually risk?" — this chapter is the answer. Understanding how the five components interact is what separates a database administrator from a database architect.</p>
</div>

<div class="topic">
<h2>Component 1: Transaction Manager — ACID Guarantees</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>A transaction is a promise: "Either all of these changes happen together, or none of them do. No one else sees half-finished work. And once I say 'done,' it stays done even if the power cuts out." The transaction manager enforces this promise. Without it, a bank transfer could debit one account and crash before crediting the other — money vanishes.</p></div>

<h3>ACID: The Four Properties in Full</h3>

<p><strong>Atomicity — All or Nothing:</strong> A transaction containing N operations either commits all N or rolls back all N. There is no partial commit. Implementation: the Write-Ahead Log captures every intended change before it's applied. On crash mid-transaction, the Recovery Manager replays the WAL to completion or rolls back incomplete transactions via undo records. The application can also explicitly issue <code>ROLLBACK</code> to abandon a transaction.</p>

<p><strong>Consistency — Valid State to Valid State:</strong> The database transitions from one valid state to another. "Valid" is defined by constraints: primary key uniqueness, foreign key referential integrity, check constraints, not-null constraints, unique indexes. Consistency is partly enforced by the database (constraint checking on commit) and partly the application's responsibility (the database can't know if a transfer amount is logically correct — only if it satisfies declared constraints).</p>

<p><strong>Isolation — Concurrent Transactions Don't Interfere:</strong> Multiple concurrent transactions behave as if they executed serially. In practice, full serialization is too expensive — databases offer configurable isolation levels that trade correctness guarantees for performance. Implementation: MVCC (see below) provides read isolation without blocking. Lock Manager prevents concurrent writes to the same rows.</p>

<p><strong>Durability — Committed Data Survives Crashes:</strong> Once <code>COMMIT</code> returns successfully, the data is permanent — it survives server crashes, power failures, and OS panics. Implementation: WAL is fsynced to disk before <code>COMMIT</code> returns. Even if the database crashes immediately after, the WAL contains all committed changes and can replay them on restart.</p>

<h3>Isolation Levels: The Correctness vs Performance Spectrum</h3>

<div class="box n"><div class="box-lbl">Isolation Levels and the Anomalies They Prevent</div>
<table>
  <thead><tr><th>Level</th><th>Dirty Read</th><th>Non-Repeatable Read</th><th>Phantom Read</th><th>Serialization Anomaly</th><th>Performance</th></tr></thead>
  <tbody>
    <tr><td><strong>Read Uncommitted</strong></td><td class="rd">Possible</td><td class="rd">Possible</td><td class="rd">Possible</td><td class="rd">Possible</td><td class="g">Fastest</td></tr>
    <tr><td><strong>Read Committed</strong> (PG default)</td><td class="g">Prevented</td><td class="rd">Possible</td><td class="rd">Possible</td><td class="rd">Possible</td><td class="g">Fast</td></tr>
    <tr><td><strong>Repeatable Read</strong></td><td class="g">Prevented</td><td class="g">Prevented</td><td class="g">Prevented*</td><td class="rd">Possible</td><td class="y">Medium</td></tr>
    <tr><td><strong>Serializable</strong></td><td class="g">Prevented</td><td class="g">Prevented</td><td class="g">Prevented</td><td class="g">Prevented</td><td class="rd">Slowest</td></tr>
  </tbody>
</table>
<p style="font-size:8pt;margin-top:1mm">*PostgreSQL's Repeatable Read also prevents phantom reads (stronger than SQL standard requires)</p>
</div>

<p><strong>Dirty read:</strong> Transaction T1 reads data written by T2 that has not yet committed. If T2 rolls back, T1 has seen data that never existed. PostgreSQL doesn't implement Read Uncommitted (it silently upgrades to Read Committed).</p>

<p><strong>Non-repeatable read:</strong> T1 reads a row, T2 modifies and commits it, T1 reads the same row again and gets different data. Same query, same transaction, different results.</p>

<p><strong>Phantom read:</strong> T1 reads a set of rows matching a predicate, T2 inserts a new row matching the same predicate and commits, T1 re-executes the query and sees the new "phantom" row.</p>

<p><strong>Serialization anomaly:</strong> Two transactions each read data and write based on what they read — in a way that could not have happened in any serial execution. Classic example: write skew — T1 reads "no doctors on call" and books a day off; simultaneously T2 reads "no doctors on call" and also books a day off. Both commit. Now zero doctors are on call, violating the invariant that at least one must be. Serializable (SSI in PostgreSQL) detects and prevents this.</p>

<p><strong>PostgreSQL's SSI implementation:</strong> Serializable Snapshot Isolation tracks read-write dependencies between concurrent transactions using predicate locks. If a cycle is detected in the dependency graph, one transaction is aborted. Unlike lock-based serializability, SSI allows high concurrency — only transactions that would actually violate serializability are aborted.</p>

<div class="box n"><div class="box-lbl">Storage Engine Component → ACID Property Mapping</div>
<p>Each ACID property is enforced by a specific component. Knowing these mappings lets you answer "what breaks if I remove X?" precisely.</p>
<table>
  <thead><tr><th>ACID Property</th><th>Enforced By</th><th>Mechanism</th><th>What Breaks Without It</th></tr></thead>
  <tbody>
    <tr><td><strong>Atomicity</strong> (all-or-nothing)</td><td>Transaction Manager + Recovery Manager</td><td>WAL records group all changes under one XID; UNDO phase rolls back uncommitted XIDs after crash</td><td>Partial writes survive crashes — half a bank transfer lands, money vanishes</td></tr>
    <tr><td><strong>Consistency</strong> (valid state → valid state)</td><td>Transaction Manager + Access Layer</td><td>Constraint checks (foreign keys, NOT NULL, CHECK) enforced before commit; constraints can be DEFERRED to end of transaction</td><td>Referential integrity violations, invalid data states</td></tr>
    <tr><td><strong>Isolation</strong> (concurrent txns don't interfere)</td><td>Lock Manager + MVCC</td><td>Lock modes prevent conflicting concurrent access; MVCC gives each reader a consistent snapshot without blocking writers</td><td>Dirty reads, non-repeatable reads, phantom reads, write skew, lost updates</td></tr>
    <tr><td><strong>Durability</strong> (committed data survives crashes)</td><td>Recovery Manager (WAL)</td><td>Every commit forces WAL record to disk via fsync before returning success to client; data file writes can be deferred</td><td>Committed transactions disappear after crash — "I got a commit confirmation but my data is gone"</td></tr>
  </tbody>
</table>
<p><strong>The critical insight</strong>: The Lock Manager → Isolation link and the Recovery Manager → Durability link are the two most commonly confused. Students often think the buffer pool ensures durability (it doesn't — the buffer pool is volatile RAM) or that WAL ensures isolation (it doesn't — WAL is for crash recovery; isolation comes from locks and MVCC snapshots).</p>
</div>

<div class="box xr"><div class="box-lbl">Related Deep Dives — ACID &amp; Transactions</div>
<ul>
  <li><strong>lucsystemdesign — "ACID vs BASE"</strong>: Practical trade-offs forcing ACID vs eventual consistency choice. Key quote: "Strong data integrity → You never see half-applied changes. Simpler application logic → The database enforces consistency." Also covers horizontal scaling penalty (locks + constraint checks = expensive across nodes). When ACID matters: payments, inventory. When it doesn't: feeds, analytics.</li>
  <li><strong>vutr — "ACID For Data Engineers"</strong>: Shows how modern cloud systems delegate ACID properties to the storage layer — Amazon S3 and GCS provide 99.999999999% durability without WAL. Relevant for understanding Delta Lake, Iceberg, Hudi which skip WAL entirely by using object storage guarantees.</li>
  <li><strong>vutr — "OLTP vs OLAP: Making changes to the data"</strong>: Contrast between OLTP in-place mutation (B-Tree pages + WAL) and OLAP Copy-on-Write strategy (atomic file replacement + metadata commit). Shows ACID can be implemented many ways depending on architecture.</li>
</ul>
</div>
</div>

<div class="topic">
<h2>MVCC: Multi-Version Concurrency Control</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Traditional locking: when T1 is reading a row, T2 must wait to write it. And when T2 is writing, T1 must wait to read. Everyone blocks everyone. MVCC's insight: keep multiple versions of each row. Readers always see the version that was current when their transaction started — they never block writers. Writers create a new version — they never block readers. The only contention is writer vs writer on the same row.</p></div>

<h3>PostgreSQL MVCC: xmin/xmax on Every Tuple</h3>

<p>PostgreSQL's MVCC stores all versions of a row in the same heap table (not in a separate undo log). Each row version (tuple) has:</p>
<ul>
  <li><strong>t_xmin:</strong> The XID of the transaction that created this version. A reader can see this tuple if t_xmin is a committed transaction in their snapshot.</li>
  <li><strong>t_xmax:</strong> The XID of the transaction that deleted/updated this version (0 if still current). A reader can see this tuple if t_xmax is 0, or t_xmax is a transaction that was not yet committed when the reader's snapshot was taken.</li>
</ul>

<p><strong>Visibility rule:</strong> A tuple is visible to transaction T if: (1) t_xmin is committed and in T's snapshot AND (2) t_xmax is either 0 (not deleted), not committed, or committed after T's snapshot was taken.</p>

<p><strong>Snapshot:</strong> At transaction start (or at each statement for Read Committed), PostgreSQL takes a snapshot: the list of all currently in-progress XIDs. Any XID in the snapshot is "invisible" (in-progress); any committed XID below the snapshot's xmin is visible; XIDs above the snapshot's xmax are invisible (future transactions).</p>

<h3>The Cost of MVCC: Dead Tuples and VACUUM</h3>

<p>Every UPDATE creates a new heap tuple and marks the old one with t_xmax. Every DELETE marks a tuple with t_xmax. These "dead tuples" accumulate — they are logically deleted but physically present. VACUUM removes dead tuples that are no longer visible to any active transaction (those whose t_xmax is committed and older than the oldest active transaction's XID).</p>

<p>Without VACUUM, tables grow unboundedly even if the logical data size is constant. A table receiving 1,000 updates/sec to the same 100,000 rows generates 86.4 billion dead tuples per day — the physical table grows by however much space those dead tuples occupy (23-byte headers + column data). autovacuum must run frequently enough to reclaim space before the table bloats unacceptably.</p>

<div class="box f"><div class="box-lbl">XID Wraparound: The Most Dangerous PostgreSQL Failure</div>
<p>PostgreSQL uses 32-bit transaction IDs (XIDs). After 4,294,967,296 (≈ 4.3 billion) transactions, the XID counter wraps back to zero. PostgreSQL uses modular arithmetic: XIDs within 2¹ = 2.1 billion of the current XID are "in the past" (visible); XIDs further away are "in the future" (invisible).</p>
<p>If a table has rows with t_xmin older than 2.1 billion transactions ago, those rows appear to be "in the future" — <strong>the entire table becomes invisible.</strong> PostgreSQL will refuse to access it to protect data integrity.</p>
<p><strong>Prevention:</strong> autovacuum runs VACUUM FREEZE on tables at risk: it rewrites t_xmin as the special "frozen" XID (2) which is always considered "in the past." This is controlled by <code>autovacuum_freeze_max_age</code> (default: 200 million). Monitor with <code>SELECT relname, age(relfrozenxid) FROM pg_class ORDER BY age DESC</code>. <strong>If age approaches 2.1 billion and autovacuum is not keeping up, you have a production emergency.</strong></p>
</div>

<h3>PostgreSQL vs InnoDB MVCC: Two Philosophies</h3>
<div class="box n"><div class="box-lbl">MVCC Implementation Comparison</div>
<table>
  <thead><tr><th>Aspect</th><th>PostgreSQL</th><th>MySQL InnoDB</th></tr></thead>
  <tbody>
    <tr><td>Old version storage</td><td>Heap table (inline with current data)</td><td>Undo log segments (separate structure)</td></tr>
    <tr><td>Reader overhead</td><td>Check t_xmin/t_xmax per tuple</td><td>Follow undo log chain to find correct version</td></tr>
    <tr><td>VACUUM needed?</td><td class="rd">Yes — dead tuples accumulate in heap</td><td class="g">No — undo log is overwritten automatically</td></tr>
    <tr><td>Long transaction cost</td><td>Dead tuples can't be vacuumed → table bloat</td><td>Undo log grows → can become very large (GB+)</td></tr>
    <tr><td>Crash recovery</td><td>Dead tuples ignored, no undo needed</td><td>Undo log must be applied to reconstruct current state</td></tr>
    <tr><td>UPDATE performance</td><td>Always write new tuple (even for same-size updates, unless HOT)</td><td>Can do in-place update (if no secondary index changes + size fits)</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="topic">
<h2>Component 2: Lock Manager</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Even with MVCC, two writers on the same row must take turns — you can't write two different values to the same cell simultaneously. The lock manager is the traffic controller: it grants locks to transactions, queues those that must wait, detects when two transactions are waiting for each other (a deadlock), and resolves it by terminating one.</p></div>

<h3>Lock Modes in PostgreSQL (8 Modes, Ordered by Strength)</h3>
<div class="box n"><div class="box-lbl">PostgreSQL Lock Modes — Compatibility Matrix</div>
<table>
  <thead><tr><th>Mode</th><th>Acquired By</th><th>Conflicts With</th></tr></thead>
  <tbody>
    <tr><td><strong>AccessShare</strong></td><td><code>SELECT</code></td><td>AccessExclusive only</td></tr>
    <tr><td><strong>RowShare</strong></td><td><code>SELECT FOR UPDATE/SHARE</code></td><td>Exclusive, AccessExclusive</td></tr>
    <tr><td><strong>RowExclusive</strong></td><td><code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code></td><td>Share, ShareRowExclusive, Exclusive, AccessExclusive</td></tr>
    <tr><td><strong>ShareUpdateExclusive</strong></td><td><code>VACUUM</code>, <code>ANALYZE</code>, <code>CREATE INDEX CONCURRENTLY</code></td><td>ShareUpdateExclusive, Share, ShareRowExclusive, Exclusive, AccessExclusive</td></tr>
    <tr><td><strong>Share</strong></td><td><code>CREATE INDEX</code> (non-concurrent)</td><td>RowExclusive, ShareUpdateExclusive, ShareRowExclusive, Exclusive, AccessExclusive</td></tr>
    <tr><td><strong>ShareRowExclusive</strong></td><td>Trigger creation</td><td>RowExclusive and above</td></tr>
    <tr><td><strong>Exclusive</strong></td><td>Rare; some subscription operations</td><td>All except AccessShare</td></tr>
    <tr><td><strong>AccessExclusive</strong></td><td><code>DROP TABLE</code>, <code>TRUNCATE</code>, <code>ALTER TABLE</code>, <code>LOCK TABLE</code></td><td class="rd">Everything — blocks all access</td></tr>
  </tbody>
</table>
</div>

<p>The practical takeaway: <code>SELECT</code> only conflicts with <code>ALTER TABLE</code> (AccessExclusive). Reads and writes don't conflict at the table level — MVCC handles that. But <code>ALTER TABLE</code> blocks everything. This is why schema migrations on live tables are dangerous: even adding a column with a default value (which triggers a full table rewrite in older PostgreSQL versions) holds an AccessExclusive lock for the entire rewrite duration, blocking all queries.</p>

<p><strong>PostgreSQL 11+:</strong> Adding a column with a non-volatile default no longer rewrites the table — the default is stored in the catalog and applied on read. This made many common schema migrations lock-free.</p>

<h3>Row-Level Locks</h3>
<p>Table-level locks are coarse. Row-level locks allow concurrent writes to different rows in the same table. <code>UPDATE</code> and <code>DELETE</code> acquire a RowExclusive table lock (non-conflicting with other writes) plus an exclusive row-level lock on each modified row. Row locks are stored in the tuple's t_infomask — not in a separate lock table — saving memory and lookup overhead.</p>

<p><strong><code>SELECT FOR UPDATE</code>:</strong> Acquires an exclusive row-level lock on selected rows without modifying them. Used to prevent another transaction from updating or deleting rows you intend to update ("optimistic to pessimistic" pattern). All locked rows are held until transaction commit or rollback.</p>

<p><strong><code>SELECT FOR SHARE</code>:</strong> Acquires a shared row-level lock. Multiple transactions can hold a share lock simultaneously; an exclusive lock must wait for all share locks to be released.</p>

<h3>Deadlock Detection and Resolution</h3>

<p>A deadlock occurs when Transaction A holds Lock 1 and waits for Lock 2, while Transaction B holds Lock 2 and waits for Lock 1. Neither can proceed — a cycle in the wait-for graph.</p>

<p><strong>Detection:</strong> PostgreSQL runs a deadlock detector after a configurable wait timeout (<code>deadlock_timeout</code>, default 1 second). When a transaction has been waiting 1 second, the detector checks the wait-for graph for cycles. If a cycle is found, one transaction is chosen as the victim — typically the youngest transaction (lowest cost to abort). The victim receives an error: <code>ERROR: deadlock detected</code>.</p>

<p><strong>Resolution:</strong> The victim transaction is rolled back <em>completely</em> — not just the contested lock, but every lock the transaction holds. Why complete rollback rather than releasing only the deadlocked lock? A transaction's locks form an interdependent set: they represent a consistent, partially-applied unit of work. Releasing only the contested lock would leave the transaction in a half-committed state — some row modifications applied and locked, others not — which is an inconsistent database state by definition. Worse, the remaining locks held by the half-killed transaction would now block other transactions that need those rows, potentially creating new deadlocks from the same victim. Complete rollback atomically releases all locks at once, returns all modified rows to their pre-transaction state, and leaves no orphaned locks. The other transaction(s) in the cycle then see a clean state and can proceed safely.</p>

<div class="box f"><div class="box-lbl">Deadlock Prevention Patterns</div>
<ul>
  <li><strong>Consistent lock ordering:</strong> If all transactions acquire locks on tables/rows in the same order (e.g., always lock table A before table B), cycles cannot form. This is the most reliable prevention strategy.</li>
  <li><strong>Use <code>SELECT FOR UPDATE NOWAIT</code>:</strong> Fails immediately if the row is locked, rather than waiting. The application retries with exponential backoff. Avoids long wait chains but requires application-level retry logic.</li>
  <li><strong>Use <code>SELECT FOR UPDATE SKIP LOCKED</code>:</strong> Skips rows that are already locked. Useful for job queues where multiple workers compete for tasks — each worker gets non-overlapping work.</li>
  <li><strong>Keep transactions short:</strong> Locks are held from acquisition to commit/rollback. A 30-second transaction holding locks on popular rows will cause queue buildup and deadlock probability increases with queue depth.</li>
</ul>
</div>
</div>

<div class="topic">
<h2>Component 3: Access Layer</h2>

<p>The access layer is the internal query-to-storage interface. A query says "give me rows where id = 42"; the access layer decides how to retrieve them. The access layer is where the query planner's decisions materialise into actual I/O operations.</p>

<h3>Scan Types and When the Planner Chooses Each</h3>
<div class="box n"><div class="box-lbl">PostgreSQL Scan Types</div>
<table>
  <thead><tr><th>Scan Type</th><th>How It Works</th><th>Planner Chooses When</th><th>I/Os</th></tr></thead>
  <tbody>
    <tr><td><strong>Sequential Scan</strong></td><td>Reads all heap pages in order; filters rows by predicate</td><td>Selectivity &gt;5–10% of table, or no useful index, or table is tiny (&lt;a few pages)</td><td>Table size / page size</td></tr>
    <tr><td><strong>Index Scan</strong></td><td>Traverses B+ tree to find matching TIDs; fetches each heap page</td><td>High selectivity (&lt;1–5% rows); sorted output needed; index covers predicate</td><td>O(log n) index + 1 heap page per match</td></tr>
    <tr><td><strong>Index-Only Scan</strong></td><td>Uses index leaf data directly; checks visibility map to avoid heap access</td><td>All needed columns are in the index (covering index); &gt;95% of pages are "all-visible"</td><td>O(log n) index only (no heap)</td></tr>
    <tr><td><strong>Bitmap Index Scan</strong></td><td>Collects all matching TIDs from index into a bitmap; sorts by heap page; fetches pages in order</td><td>Medium selectivity (1–10%); multiple indexes to combine (bitmap AND/OR); reduces random I/O</td><td>Index I/Os + sorted heap I/Os</td></tr>
  </tbody>
</table>
</div>

<p><strong>The visibility map:</strong> PostgreSQL maintains a visibility map (one bit per heap page) indicating whether all tuples on a page are visible to all transactions. Index-only scans use this: if the visibility map bit is set, the heap page doesn't need to be fetched to confirm visibility — the index data alone is sufficient. VACUUM sets these bits; any modification to a page clears them. Dense visibility maps are a sign of a well-vacuumed table.</p>

<h3>Index Types in PostgreSQL</h3>
<ul>
  <li><strong>B-tree (default):</strong> All comparison operators (<code>=</code>, <code>&lt;</code>, <code>&gt;</code>, <code>BETWEEN</code>, <code>LIKE 'prefix%'</code>). The right choice 95% of the time.</li>
  <li><strong>Hash:</strong> Equality only (<code>=</code>). Slightly faster than B-tree for equality but no range queries. WAL-logged since PostgreSQL 10. Rarely justified over B-tree.</li>
  <li><strong>GIN (Generalized Inverted Index):</strong> Full-text search (<code>tsvector</code>), array containment (<code>@&gt;</code>, <code>&lt;@</code>), JSONB key/value queries. Stores a posting list per indexed value — excellent for "find all documents containing word X."</li>
  <li><strong>GiST (Generalized Search Tree):</strong> Geometric queries (PostGIS), range types, nearest-neighbor searches. Extensible: any user-defined type can define a GiST operator class.</li>
  <li><strong>BRIN (Block Range INdex):</strong> Stores min/max values per range of heap pages. Tiny index (kilobytes for billion-row tables). Useful only when data has strong physical correlation with the index key (e.g., a timestamp column that's always inserted in order — newer rows are on later pages, so BRIN's min/max per block is accurate). Useless for data with no physical ordering.</li>
</ul>

<div class="box f"><div class="box-lbl">What the Access Layer Abstraction Costs the Query Planner</div>
<p>The Access Layer provides a uniform CRUD interface regardless of the underlying storage structure. This is elegant — but it hides information from the query planner that it could use for optimization.</p>
<ul>
  <li><strong>Planner cannot distinguish B+ tree vs LSM internals.</strong> The Access Layer exposes "index exists on column X" — not "this is an LSM bloom filter vs a B+ tree leaf node." The planner chooses between sequential scan, index scan, and bitmap index scan, but cannot say "use the bloom filter for this point query instead of the B+ tree."</li>
  <li><strong>Planner cannot request specific prefetch patterns.</strong> If the planner knows it will access 10,000 specific heap pages, it could tell the Buffer Manager to prefetch them. The Access Layer abstraction prevents this — the planner can only request pages one-by-one through the standard interface.</li>
  <li><strong>Storage-engine-specific hints require breaking the abstraction.</strong> MySQL's <code>USE INDEX</code>, <code>FORCE INDEX</code>, and <code>IGNORE INDEX</code> hints pass storage-engine knowledge through the abstraction boundary. PostgreSQL's <code>enable_indexscan = off</code> is a crude override. Both are escape hatches that exist because the abstraction loses information the planner sometimes needs.</li>
</ul>
<p><strong>The architect's trade-off:</strong> The Access Layer abstraction enables storage engine pluggability (MySQL can swap InnoDB for MyISAM; PostgreSQL can add new table access methods via the <code>TABLE ACCESS METHOD</code> API). The cost is one level of query optimization opacity. Systems that need maximum query performance (ClickHouse, DuckDB) often tightly couple the query executor and storage engine — sacrificing pluggability for optimizer visibility.</p>
</div>
</div>

<div class="topic">
<h2>Component 4: Buffer Manager</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>The buffer manager is a RAM cache for disk pages. Before accessing any page, every part of the database checks the buffer manager first. A cache hit costs 100 nanoseconds (RAM). A cache miss costs 10 milliseconds (HDD) or 50 microseconds (NVMe) — a 100,000× difference for HDD. Getting 99% of reads from the buffer manager is the single most impactful performance optimization in any database.</p></div>

<h3>Architecture: Shared Buffer Pool</h3>

<p>PostgreSQL's shared buffer pool (<code>shared_buffers</code>) is a fixed-size region of shared memory (accessible to all PostgreSQL processes). It is organized as:</p>
<ul>
  <li><strong>Buffer pool frames:</strong> Fixed-size slots, each holding one 8KB page. The page data itself.</li>
  <li><strong>Buffer descriptors:</strong> One descriptor per frame, containing: page tag (which file, which block number — the cache key), reference count (how many backends have pinned this page), usage count (for LRU approximation), dirty flag, and a spinlock for descriptor access.</li>
  <li><strong>Buffer table:</strong> A hash table mapping (file, block) → frame number. Lookups are O(1) — find the frame holding a given page in nanoseconds.</li>
</ul>

<h3>Clock Sweep Eviction Algorithm</h3>
<p>When all buffer frames are occupied and a new page must be loaded, PostgreSQL must evict an existing page. The eviction policy is <strong>clock sweep</strong> — a lightweight approximation of LRU:</p>
<ol>
  <li>Maintain a "clock hand" that sweeps through all buffer descriptors in a circular fashion.</li>
  <li>Each descriptor has a <strong>usage count</strong> (0–5). Each page access increments the usage count (up to 5).</li>
  <li>The clock sweep decrements the usage count of the current page. If it reaches 0 and the page is not pinned, evict this page (write to disk if dirty, then load the new page).</li>
  <li>Advance the clock hand and repeat.</li>
</ol>
<p>Hot pages (accessed frequently) quickly accumulate high usage counts and survive many clock sweep passes. Cold pages (accessed once) have usage count 1, which the sweep decrements to 0 quickly, making them eviction candidates. This approximates LRU without the overhead of maintaining a precise LRU list.</p>

<h3>Pinned Pages</h3>
<p>A page that is actively being accessed has its reference count &gt; 0 — it is "pinned." The buffer manager will never evict a pinned page. After a backend finishes reading/writing a page, it "unpins" it (decrements reference count). The buffer pool guarantees: a pinned page's data pointer is stable and valid for the duration of the pin.</p>

<h3>Dirty Pages and Checkpoints</h3>
<p>When a page is modified in the buffer pool, it becomes "dirty" — its in-memory content differs from the on-disk content. The dirty flag in the buffer descriptor marks this. Dirty pages must eventually be written to disk for two reasons: (1) space reclamation — evicting a dirty page requires writing it first; (2) checkpoint — periodically, all dirty pages must be flushed to ensure recovery can proceed from a known point (see WAL below).</p>

<div class="box n"><div class="box-lbl">Buffer Manager Configuration Reference</div>
<table>
  <thead><tr><th>Parameter</th><th>Default</th><th>Recommended</th><th>What It Controls</th></tr></thead>
  <tbody>
    <tr><td><code>shared_buffers</code></td><td>128MB</td><td>25% of RAM</td><td>Buffer pool size. Too large: OS has no RAM for its own cache (hurts sequential scans). Too small: poor hit rate.</td></tr>
    <tr><td><code>effective_cache_size</code></td><td>4GB</td><td>50–75% of RAM</td><td>Hint to query planner for how much memory is available for caching (includes OS page cache). Does NOT allocate RAM. Affects planner's choice of index scan vs sequential scan.</td></tr>
    <tr><td><code>work_mem</code></td><td>4MB</td><td>4MB–256MB</td><td>Per-sort, per-hash-join memory budget. Too small: sort/hash spills to disk. Too large: many concurrent complex queries OOM the server (N connections × M operations × work_mem).</td></tr>
    <tr><td><code>maintenance_work_mem</code></td><td>64MB</td><td>256MB–2GB</td><td>Memory for VACUUM, CREATE INDEX, ALTER TABLE. Larger = faster VACUUM and index builds.</td></tr>
  </tbody>
</table>
</div>

<div class="box f"><div class="box-lbl">Buffer Pool Hit Rate Monitoring</div>
<p>Target: &gt;99% for OLTP. Check with:</p>
<pre>SELECT
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS hit_rate
FROM pg_statio_user_tables;</pre>
<p>Below 95%: increase <code>shared_buffers</code> or add RAM. Below 90%: your working set doesn't fit in RAM — investigate data access patterns, consider partitioning to reduce working set, or add RAM. A 1% improvement in hit rate at 10,000 reads/sec on NVMe saves 100 disk reads/sec × 50μs = 5ms of cumulative disk time per second.</p>
</div>

<h3>Buffer Pool Tuning and Observability</h3>

<p><strong>shared_buffers sizing — the 25% rule and its limits:</strong> The conventional advice of setting <code>shared_buffers</code> to 25% of system RAM comes from a real trade-off: set it too high and the OS has insufficient RAM for its own page cache, which hurts sequential scans (PostgreSQL still uses the kernel page cache for table files when using buffered I/O). Set it too low and cache misses drive unnecessary NVMe reads. 25% is a starting point, not a ceiling — on a 256GB server dedicated to PostgreSQL with <code>O_DIRECT</code> data files, <code>shared_buffers=64GB</code> with <code>effective_cache_size=200GB</code> is more appropriate.</p>

<p><strong>Clock sweep vs LRU — why sequential scans can evict hot pages:</strong> PostgreSQL's clock-sweep eviction is vulnerable to sequential scan pollution. A full table scan of a 100GB cold table walks through millions of pages, each getting a usage_count of 1. The sweep quickly evicts them, but not before they temporarily displace hot index pages from the buffer pool. PostgreSQL mitigates this with a "ring buffer" for sequential scans: large sequential scans use a small fixed-size ring of buffer frames (8MB default), so they cannot evict pages outside the ring. This is why a bulk table scan doesn't blow out your buffer pool hit rate — provided the scan is detected as sequential.</p>

<p><strong>pg_prewarm:</strong> After a PostgreSQL restart, the buffer pool is empty — the working set must be rebuilt from disk page faults. The <code>pg_prewarm</code> extension (included in standard PostgreSQL) can restore the buffer pool contents from a saved list: <code>SELECT pg_prewarm('tablename')</code> or configure <code>pg_prewarm</code> in <code>shared_preload_libraries</code> to automatically save and restore the buffer pool on shutdown/startup. This eliminates the "cold start" performance cliff after planned restarts.</p>

<h3>Buffer Pool Sizing Trade-offs: What You Give Up Going Larger</h3>

<div class="box f"><div class="box-lbl">Why Bigger Buffer Pool Is Not Always Better</div>
<p>Increasing <code>shared_buffers</code> beyond the optimal point creates three problems:</p>
<ul>
  <li><strong>OOM (Out-of-Memory) risk.</strong> PostgreSQL's <code>shared_buffers</code> is allocated at startup as shared memory (POSIX shared memory or System V shared memory). On a 64GB server with shared_buffers=48GB, only 16GB remains for: the OS kernel, 200+ PostgreSQL worker processes (each ~10MB), monitoring agents, log collectors, and OS page cache. Under memory pressure, the Linux OOM killer terminates processes — often choosing large PostgreSQL workers or even the postmaster. Rule: shared_buffers ≤ 40% of total RAM on a dedicated database server.</li>
  <li><strong>OS page cache starvation.</strong> PostgreSQL does NOT use O_DIRECT by default — it reads data through the OS page cache. The kernel caches pages it reads, giving PostgreSQL a second cache layer for free. Sequential scans (which bypass the shared_buffers and go directly through the OS page cache with kernel read-ahead) benefit heavily from OS page cache. If shared_buffers consumes 75% of RAM, the OS has almost no memory left for its page cache, killing sequential scan performance.</li>
  <li><strong>Clock sweep eviction overhead.</strong> The buffer pool eviction algorithm (clock sweep) must scan more entries when shared_buffers is larger. At very large shared_buffers, background processes like bgwriter and checkpointer take longer to scan dirty page lists, increasing checkpoint duration and I/O spike risk.</li>
</ul>
<p><strong>Tuning targets:</strong> Start at 25% of RAM. Increase toward 40% while monitoring: (1) OS page cache remaining in <code>free -h</code>, (2) buffer pool hit rate in <code>pg_statio_user_tables</code> (target &gt;99%), (3) checkpoint duration in <code>pg_stat_bgwriter</code>. Stop increasing when hit rate plateaus or OS cache drops below 10% of RAM.</p>
</div>

<p><strong>InnoDB buffer pool — different rules:</strong> MySQL InnoDB uses <code>O_DIRECT</code> for data files, so the full buffer pool can safely be 70–80% of RAM without double-caching waste. Monitor with <code>SHOW STATUS LIKE 'Innodb_buffer_pool%'</code>: key metrics are <code>Innodb_buffer_pool_read_requests</code> (logical reads) vs <code>Innodb_buffer_pool_reads</code> (physical reads from disk) — the hit rate is 1 - (physical/logical). InnoDB also supports multiple buffer pool instances (<code>innodb_buffer_pool_instances</code>) to reduce lock contention on the buffer pool mutex — set to 8 for servers with &gt;8GB buffer pool.</p>

<div class="box n"><div class="box-lbl">Buffer Pool Observability Queries</div>
<table>
  <thead><tr><th>Database</th><th>Query</th><th>What to Look For</th></tr></thead>
  <tbody>
    <tr><td>PostgreSQL — hit rate</td><td><code>SELECT ... FROM pg_statio_user_tables</code></td><td>Target &gt;99%; below 95% = shared_buffers too small</td></tr>
    <tr><td>PostgreSQL — bloated buffer pool</td><td><code>SELECT * FROM pg_buffercache WHERE usagecount = 0</code></td><td>Many usage_count=0 = eviction pressure; increase shared_buffers</td></tr>
    <tr><td>PostgreSQL — prewarm</td><td><code>SELECT pg_prewarm('table_name', 'buffer')</code></td><td>Number of pages loaded; compare to pg_relation_size()</td></tr>
    <tr><td>MySQL InnoDB — hit rate</td><td><code>SHOW STATUS LIKE 'Innodb_buffer_pool%'</code></td><td>read_requests / (read_requests + reads) &gt; 0.99</td></tr>
  </tbody>
</table>
</div>
</div>

<div class="topic">
<h2>Component 5: Recovery Manager — Write-Ahead Log (WAL)</h2>

<div class="box s"><div class="box-lbl">In Simple Terms</div>
<p>Before a database makes any change to a data file, it writes a description of that change to a special sequential log — the Write-Ahead Log. If the system crashes mid-operation, the log contains everything needed to either complete or undo the operation. "Write-ahead" means: the log entry is always written before the data change. This order guarantee is what makes the database recoverable after any crash.</p></div>

<h3>WAL Record Format and LSN</h3>

<p>Every change to any database page generates one or more WAL records before the change is applied to the buffer pool. Each WAL record contains:</p>
<ul>
  <li><strong>Log Sequence Number (LSN):</strong> A monotonically increasing 64-bit number representing the byte offset of this record in the WAL stream. The LSN is the universal currency of WAL: every page in the buffer pool stores the LSN of the last WAL record that modified it (<code>pd_lsn</code> in the page header). On crash recovery, if a page's pd_lsn is less than a WAL record's LSN, the WAL record must be re-applied (redo). LSNs are also used for replication lag measurement.</li>
  <li><strong>Resource manager ID:</strong> Which subsystem generated this record (heap, B-tree, sequence, transaction, etc.).</li>
  <li><strong>Transaction ID:</strong> Which transaction generated this change.</li>
  <li><strong>Before and after images:</strong> For some operations, the full before-image (for undo) and after-image (for redo). For others, a logical description of the change (INSERT into table X the row Y) to save space.</li>
</ul>

<h3>WAL Write Path and fsync</h3>
<p>WAL records are first written to the <strong>WAL buffer</strong> (in shared memory, <code>wal_buffers</code>, default 4MB). On transaction commit (or when the WAL buffer fills), WAL is flushed to WAL segment files (16MB each by default) and fsynced.</p>

<p><strong>fsync vs fdatasync vs O_SYNC:</strong></p>
<ul>
  <li><code>fsync(fd)</code>: Flushes file data and metadata to physical storage. Guaranteed durable after return.</li>
  <li><code>fdatasync(fd)</code>: Flushes file data only (not metadata like modification time). Slightly faster than fsync; sufficient for WAL durability since WAL files don't need metadata updates for recovery.</li>
  <li><code>O_SYNC</code> flag: Each write() call blocks until data reaches physical storage. Equivalent to write() + fsync() per call but potentially slower due to lack of batching opportunity.</li>
</ul>

<p>PostgreSQL uses <code>fdatasync</code> by default for WAL (on Linux). MySQL InnoDB uses <code>fsync</code> for both redo log and data files with <code>innodb_flush_method=fsync</code>, or <code>O_DIRECT</code> + <code>fsync</code> with <code>innodb_flush_method=O_DIRECT</code>.</p>

<div class="mermaid">
graph LR
    TXN[Transaction Commit]
    WB[WAL Buffer<br/>in memory]
    WF[WAL File<br/>sequential on disk]
    DP[Dirty Pages<br/>in buffer pool]
    DI[Data File<br/>on disk]
    TXN --> WB
    WB -->|fsync on commit| WF
    WB -->|later, async| DP
    DP -->|checkpoint flush| DI
</div>
<p class="diagram-cap">Figure 5.1 — WAL write path. WAL is fsynced on every commit for durability. Dirty pages are flushed lazily during checkpoint.</p>

<div class="box xr"><div class="box-lbl">Related Deep Dives — WAL</div>
<ul>
  <li><strong>vutr — "What Makes OLTP Databases So Quick"</strong>: WAL in context of B-Tree crash recovery. "It is an append-only file. The system must write any B-tree modification to this file before it can be applied to the pages. When the database is restored after a crash, this log is used to recover the B-tree to a consistent state." Explains WHY WAL is append-only (sequential writes are fast).</li>
  <li><strong>vutr — "How to choose the right diskless Kafka"</strong>: Modern alternative to WAL — "diskless" Kafka delegates durability to cloud object storage (S3). Shows the architectural evolution from WAL to storage-layer durability. Pair with discussion of synchronous_commit levels and the trade-offs of weakening durability guarantees.</li>
</ul>
</div>

<h3>synchronous_commit: The Durability vs Latency Trade-off</h3>
<div class="box n"><div class="box-lbl">synchronous_commit Levels (PostgreSQL)</div>
<table>
  <thead><tr><th>Level</th><th>COMMIT Returns After</th><th>Data Loss Risk on Crash</th><th>Latency Impact</th><th>Use When</th></tr></thead>
  <tbody>
    <tr><td><code>off</code></td><td>WAL written to buffer (not flushed)</td><td class="rd">Up to wal_writer_delay (200ms) of transactions</td><td class="g">Near-zero commit latency</td><td>Session-level analytics, data you can reconstruct</td></tr>
    <tr><td><code>local</code></td><td>WAL fsynced to local disk</td><td class="g">None (local crash safe)</td><td class="y">~1 fsync latency per commit</td><td>Single-server, durability required</td></tr>
    <tr><td><code>remote_write</code></td><td>Standby received WAL (not fsynced)</td><td class="y">None if primary dies, standby survives; small risk if both die</td><td class="y">Network RTT + write latency</td><td>Streaming replication, standby durable enough</td></tr>
    <tr><td><code>remote_apply</code></td><td>Standby applied WAL (readable)</td><td class="g">None; reads from standby are consistent</td><td class="rd">Network RTT + standby apply time</td><td>Read-from-standby architectures</td></tr>
    <tr><td><code>on</code> (default)</td><td>WAL fsynced to local disk</td><td class="g">None</td><td class="y">~1 fsync latency per commit</td><td>Default; safe for all production workloads</td></tr>
  </tbody>
</table>
</div>

<h3>Checkpoints: Bounding Recovery Time</h3>

<p>A checkpoint is a point at which all dirty buffer pool pages are guaranteed to have been flushed to their data files. After a checkpoint, recovery only needs to replay WAL records from that checkpoint forward — not from the beginning of time.</p>

<p><strong>Checkpoint lifecycle:</strong></p>
<ol>
  <li>Checkpoint is triggered by time (<code>checkpoint_timeout</code>, default 5 minutes) or WAL size (<code>max_wal_size</code>, default 1GB).</li>
  <li>PostgreSQL writes a checkpoint record to WAL.</li>
  <li>All dirty buffer pool pages are written to their data files. This is the expensive part — potentially gigabytes of data being written.</li>
  <li><code>checkpoint_completion_target</code> (default 0.9) spreads this I/O over 90% of the checkpoint interval, smoothing I/O spikes.</li>
  <li>Old WAL segments before this checkpoint can be recycled (or archived for PITR).</li>
</ol>

<p><strong>Checkpoint tuning:</strong> Increasing <code>max_wal_size</code> (e.g., from 1GB to 8GB) reduces checkpoint frequency, reducing I/O spikes — but increases recovery time after a crash (more WAL to replay). The right value depends on your Recovery Time Objective (RTO): how long can you afford to wait for crash recovery?</p>

<h3>ARIES Recovery Algorithm</h3>
<p>PostgreSQL's crash recovery follows the ARIES (Algorithm for Recovery and Isolation Exploiting Semantics) protocol, with three phases:</p>
<ol>
  <li><strong>Analysis Phase:</strong> Scan WAL forward from the last checkpoint to reconstruct the state at crash time — which transactions were active, which pages were dirty. Builds the Active Transaction Table (ATT) and Dirty Page Table (DPT).</li>
  <li><strong>Redo Phase:</strong> Replay all WAL records from the oldest dirty page's LSN forward, unconditionally — including changes by transactions that subsequently rolled back. This restores the exact database state at the moment of crash.</li>
  <li><strong>Undo Phase:</strong> Roll back any transactions that were active at crash time (not committed). Apply compensation log records (CLRs) for each undone change, which are themselves WAL records — making the undo operation itself crash-safe.</li>
</ol>

<div class="mermaid">
graph LR
    Crash[Database Crash]
    A[Phase 1: Analysis<br/>scan WAL from last ckpt<br/>rebuild dirty page table<br/>rebuild active txn table]
    R[Phase 2: Redo<br/>replay all WAL records<br/>restore to crash state<br/>even uncommitted txns]
    U[Phase 3: Undo<br/>rollback uncommitted txns<br/>write CLRs to WAL<br/>idempotent on re-crash]
    Done[Recovery Complete<br/>database online]
    Crash --> A
    A --> R
    R --> U
    U --> Done
</div>
<p class="diagram-cap">Figure 5.2 — ARIES 3 phases. Analysis scans WAL; Redo replays everything; Undo rolls back uncommitted transactions using Compensation Log Records.</p>

<h3>WAL Performance: Sequential Write + Group Commit</h3>

<p>WAL provides both durability and write performance advantages. The WAL write for a transaction that updates three B+ tree indexes is one sequential append (fast). The three B+ tree page modifications are random writes to three different file locations (expensive). WAL defers the random writes: commit the WAL first (sequential, fast), then flush the B+ tree pages at checkpoint time (batched, potentially sequential within a checkpoint flush).</p>

<p><strong>Group commit:</strong> When many transactions commit simultaneously, PostgreSQL batches their WAL records into a single fsync call. One fsync that commits 100 transactions costs the same as one fsync for one transaction (the fsync itself is the expensive part, not the data volume). At high concurrency, group commit dramatically improves throughput: instead of 100 × 1ms fsyncs = 100ms, one group fsync = 1ms for all 100 commits.</p>

<h3>WAL Enables Both REDO and UNDO</h3>

<p>WAL is used for two distinct purposes that are easy to conflate:</p>

<p><strong>REDO (crash recovery forward replay):</strong> After a crash, the Recovery Manager reads WAL records in forward order from the last checkpoint. For each record: if the corresponding data page is older than the WAL record's LSN, apply the change again (redo it). This brings the data file up to the state it should have been in at crash time — including all committed AND some uncommitted transactions. Redo first, undo later.</p>

<p><strong>UNDO (transaction rollback):</strong> After crash recovery's REDO phase completes, the UNDO phase identifies transactions that were in-progress at crash time (from the active transaction table rebuilt during Analysis). Each in-progress transaction is rolled back by reading its WAL records in REVERSE order and applying the "before image" (the data as it was before the transaction changed it). This is how ROLLBACK works during normal operation too: the transaction manager reads WAL backward for that XID and reverses each change.</p>

<div class="box n"><div class="box-lbl">WAL Record Structure Enables Both Directions</div>
<table>
  <thead><tr><th>Field</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td>LSN (Log Sequence Number)</td><td>Monotonic position in WAL — enables ordering and "already applied" check during REDO</td></tr>
    <tr><td>Transaction ID (XID)</td><td>Groups records by transaction — enables finding all records for a given XID during UNDO</td></tr>
    <tr><td>After image (REDO data)</td><td>The new value of the changed data — applied during forward REDO</td></tr>
    <tr><td>Before image (UNDO data)</td><td>The original value before the change — applied during backward UNDO rollback</td></tr>
    <tr><td>Previous LSN (prev_lsn)</td><td>Pointer to the previous record from the same transaction — enables backward traversal for UNDO</td></tr>
    <tr><td>Compensation Log Record (CLR)</td><td>Written during UNDO to record that a change was undone — makes UNDO idempotent if a crash occurs during undo</td></tr>
  </tbody>
</table>
</div>

<p><strong>PostgreSQL's MVCC changes the picture:</strong> In PostgreSQL, UPDATE and DELETE do not modify in-place — they create new tuple versions (for UPDATE) or mark tuples dead (for DELETE). ROLLBACK in PostgreSQL largely just marks the transaction's tuples as aborted via the transaction status bits in pg_clog (now pg_xact) — no physical undo needed. The "before image" is still available (the old tuple was never deleted, just marked with xmax). This is why PostgreSQL ROLLBACK is fast: it just commits the abort, not physically undo rows.</p>

<div class="box l"><div class="box-lbl">How All 5 Components Interact: The Life of a Transaction</div>
<p><strong>BEGIN:</strong> Transaction Manager assigns a new XID; acquires snapshot for isolation level.</p>
<p><strong>SELECT:</strong> Buffer Manager checks shared_buffers for the needed pages (cache hit → 100ns; miss → disk I/O). Access Layer chooses scan type. MVCC visibility check uses the snapshot's XID to filter tuples by t_xmin/t_xmax.</p>
<p><strong>UPDATE:</strong> Lock Manager acquires RowExclusive table lock + exclusive row lock. Buffer Manager loads and pins the target page. Recovery Manager writes a WAL record for the update. Buffer Manager writes the new tuple to the page (dirty), updates pd_lsn. Lock Manager records that this XID holds a lock on this row.</p>
<p><strong>COMMIT:</strong> Recovery Manager flushes WAL buffer to WAL file, calls fsync (if synchronous_commit=on). Transaction Manager records XID as committed in pg_clog (commit log). Lock Manager releases all table and row locks. Buffer Manager unpins pages. The transaction's changes are now visible to new transactions whose snapshot postdates this XID.</p>
<p><strong>CHECKPOINT (background):</strong> Buffer Manager writes all dirty pages to data files in order of LSN. Recovery Manager writes checkpoint record to WAL. Old WAL segments are recycled. After checkpoint, crash recovery only needs to replay WAL from this point.</p>
</div>

<div class="recall">
<div class="recall-head">Architect's Checkpoint</div>
<div class="q"><span class="q-n">Q1 </span>Explain PostgreSQL's XID wraparound problem from first principles: what causes it, what happens when it occurs, what mechanism prevents it, and what monitoring query tells you how close you are to the danger zone. Then explain why a database with 10,000 transactions/second is more at risk than one with 100 transactions/second.</div>
<div class="q"><span class="q-n">Q2 </span>A financial application requires that committed transactions are never lost, even if both the primary and standby servers crash simultaneously. Which <code>synchronous_commit</code> level achieves this? What is the latency cost, and how does group commit affect throughput under this level?</div>
<div class="q"><span class="q-n">Q3 </span>You have a PostgreSQL table receiving 50,000 updates/second to the same 1 million rows. After 24 hours, the table is 40GB despite containing only 5GB of logical data. Diagnose the exact cause (MVCC mechanism), identify which configuration parameters control the cleanup process, and explain why simply running VACUUM doesn't immediately return the disk space to the OS.</div>
<div class="q"><span class="q-n">Q4 </span>Walk through the three phases of ARIES crash recovery. A crash occurs during a checkpoint — specifically, the checkpoint started, 60% of dirty pages were flushed, then the power cut out. What does each ARIES phase do in this specific scenario?</div>
</div>

<div class="box teach"><div class="box-lbl">How to Teach This Chapter</div>
<p><strong>Junior engineer (5 min):</strong> Start with the bank transfer analogy: "I debit your account, the server crashes before I credit mine — what happens?" Walk through how WAL + ARIES makes this impossible: the WAL captured the debit intent, recovery replays it, the uncommitted transaction is rolled back. Then say: "ACID is not a checkbox — it's what these five components produce when they work together." Show the Life of a Transaction box.</p>
<p><strong>Senior engineer (15 min):</strong> Walk through MVCC's cost: every UPDATE creates a new heap tuple. 50,000 updates/sec × 86,400 seconds = 4.32 billion new tuples/day. At even 100 bytes/tuple, that's 432GB of dead tuples before VACUUM can run. Then show the XID wraparound box — this is the failure mode that shuts down the entire database. Ask: "What autovacuum settings would you change to prevent this?" Drive toward <code>autovacuum_vacuum_cost_delay</code>, <code>autovacuum_max_workers</code>, and <code>autovacuum_freeze_max_age</code>.</p>
<p><strong>Expert architect (30 min discussion):</strong> "You're designing a new financial platform. You need: zero data loss on any single failure, 10,000 TPS sustained, and sub-5ms P99 commit latency. Walk me through every trade-off in your WAL + replication configuration." Drive toward the tension between synchronous_commit=remote_apply (zero data loss, but adds standby apply latency to every commit), group commit behaviour at high TPS (helps), and dedicated NVMe for WAL (reduces fsync latency). There is no perfect answer — the point is to reason through the trade-offs explicitly.</p>
</div>

<div class="box gap"><div class="box-lbl">Questions This Chapter Doesn't Answer</div>
<ul>
  <li>How does logical replication differ from physical (WAL streaming) replication in PostgreSQL — and when does logical replication make the ARIES recovery model insufficient for cross-version upgrades?</li>
  <li>What is the actual performance difference between PostgreSQL's heap-based MVCC and InnoDB's undo-log MVCC under a workload with many long-running read transactions — and which bloats more?</li>
  <li>At what transaction rate does PostgreSQL's 32-bit XID become a practical operational risk — and is PostgreSQL 15's 64-bit XID work (in progress) a complete solution?</li>
  <li>How do distributed databases (CockroachDB, TiDB, YugabyteDB) implement ACID across nodes — and what does the Paxos/Raft consensus protocol replace in the five-component model?</li>
</ul>
</div>
</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLY + GENERATION
# ─────────────────────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>Database Internals — A Complete Reference for the Aspiring Architect</title>
<style>{CSS}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function() {{
    mermaid.initialize({{ startOnLoad: true, theme: 'neutral', fontSize: 11 }});
  }});
</script>
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

html_path = f"{OUTPUT_DIR}/ben_dicken_phase1.html"
with open(html_path, "w") as f:
    f.write(HTML)

print(f"HTML written: {html_path}")

try:
    import subprocess, sys
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    pdf_path = f"{OUTPUT_DIR}/ben_dicken_phase1.pdf"
    result = subprocess.run(
        [chrome, "--headless", "--disable-gpu",
         f"--print-to-pdf={pdf_path}",
         "--print-to-pdf-no-header", html_path],
        capture_output=True, text=True
    )
    if "bytes written" in result.stderr or "written to file" in result.stderr:
        import os
        size = os.path.getsize(pdf_path)
        print(f"PDF written: {pdf_path} ({size:,} bytes)")
    else:
        print("Chrome output:", result.stderr[-200:])
        print(f"HTML is ready at {html_path} — open in browser and Print → Save as PDF")
except Exception as e:
    print(f"PDF generation error: {e}")
    print(f"HTML is ready at {html_path}")
