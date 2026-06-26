"""
Generate a Justin Sung-style Learning Pack PDF from Ben Dicken video transcripts.

Usage:
    python scripts/generate_learning_pack.py --phase 1 --output output/ben_dicken_phase1.pdf

Each chapter follows Justin Sung's framework:
  - The Problem (WHY before HOW)
  - Core Idea (plain English)
  - Mental Model + Analogy
  - How It Works
  - Connect the Dots (cross-chapter links)
  - Trade-offs
  - Active Recall (close the book, answer these)
  - Key Takeaway
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

CHAPTERS: list[dict] = []  # populated below

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&family=Inter:wght@400;600;700&display=swap');

:root {
  --ink: #1a1a2e;
  --muted: #555570;
  --accent: #e94560;
  --accent-soft: #fff0f3;
  --blue: #2244aa;
  --blue-soft: #eef2ff;
  --green: #1a7a4a;
  --green-soft: #eafaf1;
  --yellow: #7a5c00;
  --yellow-soft: #fffbea;
  --purple: #6c3483;
  --purple-soft: #f5eeff;
  --border: #e2e2ec;
  --page-width: 148mm;  /* A5 — Kindle-friendly proportions */
}

* { box-sizing: border-box; margin: 0; padding: 0; }

@page {
  size: A4;
  margin: 22mm 20mm 22mm 20mm;
}

body {
  font-family: 'Merriweather', Georgia, serif;
  font-size: 10.5pt;
  line-height: 1.75;
  color: var(--ink);
  background: #fff;
}

/* ── Cover ── */
.cover {
  page-break-after: always;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 240mm;
  padding: 0 10mm;
}
.cover-label {
  font-family: 'Inter', sans-serif;
  font-size: 9pt;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 10mm;
}
.cover h1 {
  font-family: 'Inter', sans-serif;
  font-size: 26pt;
  font-weight: 700;
  line-height: 1.2;
  color: var(--ink);
  margin-bottom: 6mm;
}
.cover .subtitle {
  font-size: 12pt;
  color: var(--muted);
  font-style: italic;
  margin-bottom: 12mm;
  line-height: 1.6;
}
.cover-rule { width: 12mm; height: 3px; background: var(--accent); margin-bottom: 8mm; }
.cover .framework-note {
  font-family: 'Inter', sans-serif;
  font-size: 9pt;
  color: var(--muted);
  border-left: 3px solid var(--border);
  padding-left: 5mm;
  line-height: 1.6;
}
.cover .toc { margin-top: 14mm; }
.cover .toc h2 { font-family: 'Inter', sans-serif; font-size: 10pt; font-weight: 700; margin-bottom: 4mm; }
.cover .toc-item {
  display: flex;
  justify-content: space-between;
  font-size: 9.5pt;
  color: var(--muted);
  padding: 2mm 0;
  border-bottom: 1px dotted var(--border);
}
.cover .toc-item .chapter-num { color: var(--accent); font-weight: 700; font-family: 'Inter', sans-serif; }

/* ── Chapter ── */
.chapter { page-break-before: always; }

.chapter-header {
  border-left: 5px solid var(--accent);
  padding: 0 0 0 5mm;
  margin-bottom: 8mm;
}
.chapter-eyebrow {
  font-family: 'Inter', sans-serif;
  font-size: 8.5pt;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 2mm;
}
.chapter-header h2 {
  font-family: 'Inter', sans-serif;
  font-size: 18pt;
  font-weight: 700;
  line-height: 1.2;
  color: var(--ink);
}
.chapter-meta {
  font-family: 'Inter', sans-serif;
  font-size: 8.5pt;
  color: var(--muted);
  margin-top: 2mm;
}

/* ── Section blocks ── */
.section { margin-bottom: 7mm; }

.section-label {
  font-family: 'Inter', sans-serif;
  font-size: 8pt;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 2mm;
}

.section p { margin-bottom: 3mm; }
.section p:last-child { margin-bottom: 0; }

/* Callout boxes */
.callout {
  border-radius: 4px;
  padding: 4mm 5mm;
  margin: 4mm 0;
  border-left: 4px solid;
}
.callout.problem { background: var(--accent-soft); border-color: var(--accent); }
.callout.analogy { background: var(--yellow-soft); border-color: #d4a017; }
.callout.connect { background: var(--blue-soft); border-color: var(--blue); }
.callout.tradeoff { background: var(--green-soft); border-color: var(--green); }

.callout-icon {
  font-family: 'Inter', sans-serif;
  font-size: 8pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .5px;
  margin-bottom: 1.5mm;
}
.callout.problem .callout-icon { color: var(--accent); }
.callout.analogy .callout-icon { color: var(--yellow); }
.callout.connect .callout-icon { color: var(--blue); }
.callout.tradeoff .callout-icon { color: var(--green); }
.callout p { font-size: 10pt; line-height: 1.65; }

/* How it works — numbered steps */
.steps { list-style: none; padding: 0; }
.steps li {
  display: flex;
  gap: 4mm;
  margin-bottom: 3mm;
  align-items: flex-start;
}
.step-num {
  flex-shrink: 0;
  width: 5mm;
  height: 5mm;
  border-radius: 50%;
  background: var(--ink);
  color: #fff;
  font-family: 'Inter', sans-serif;
  font-size: 7.5pt;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 0.5mm;
}
.step-text { font-size: 10pt; line-height: 1.65; }

/* Active Recall */
.recall-box {
  background: var(--ink);
  color: #fff;
  border-radius: 4px;
  padding: 5mm 6mm;
  margin-top: 6mm;
  page-break-inside: avoid;
}
.recall-header {
  font-family: 'Inter', sans-serif;
  font-size: 8.5pt;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 3mm;
}
.recall-instruction {
  font-size: 9pt;
  color: #aab;
  font-style: italic;
  margin-bottom: 4mm;
  line-height: 1.5;
}
.recall-q {
  display: flex;
  gap: 3mm;
  margin-bottom: 3.5mm;
  align-items: flex-start;
}
.q-num {
  flex-shrink: 0;
  font-family: 'Inter', sans-serif;
  font-size: 8pt;
  font-weight: 700;
  color: var(--accent);
  margin-top: 1px;
}
.q-text { font-size: 10pt; line-height: 1.6; color: #f0f0f8; }
.answer-space {
  height: 10mm;
  border-bottom: 1px solid rgba(255,255,255,0.15);
  margin: 2mm 0 4mm 6mm;
}

/* Key Takeaway */
.takeaway {
  background: #f8f8fc;
  border-radius: 4px;
  padding: 4mm 5mm;
  margin-top: 4mm;
  border-top: 2px solid var(--ink);
  page-break-inside: avoid;
}
.takeaway-label {
  font-family: 'Inter', sans-serif;
  font-size: 8pt;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--ink);
  margin-bottom: 2mm;
}
.takeaway p {
  font-size: 10.5pt;
  font-weight: 700;
  font-style: italic;
  line-height: 1.5;
  color: var(--ink);
}

/* Justin quote footer */
.justin-quote {
  margin-top: 8mm;
  padding-top: 4mm;
  border-top: 1px solid var(--border);
  font-size: 9pt;
  color: var(--muted);
  font-style: italic;
  line-height: 1.6;
}
.justin-quote .attribution {
  font-style: normal;
  font-family: 'Inter', sans-serif;
  font-size: 8pt;
  color: #aaa;
  margin-top: 1.5mm;
}
"""

CHAPTERS = [
    {
        "num": 1,
        "title": "How Storage Devices Work",
        "source": "Hard Drives, SSDs, and Tape Storage",
        "duration": "10 min",
        "problem": (
            "Databases store billions of records. The physical device that holds your data "
            "determines whether a search takes 0.001ms or 22 seconds. Before any algorithm or "
            "data structure makes sense, you need to understand the physical rules of the medium "
            "you're working with."
        ),
        "core_idea": (
            "All storage devices — tape, hard drives, SSDs — work in fixed-size chunks called "
            "<strong>pages</strong> (typically 4KB–16KB). You can never read a single byte in "
            "isolation. Every read or write fetches or commits an entire page. Every database "
            "design decision flows from this single constraint."
        ),
        "analogy": (
            "<strong>Analogy — The Library Book Rule:</strong> Imagine a library where the rule is: "
            "you must check out the entire shelf, not a single book. If your data is spread across "
            "many shelves (pages), finding one record means moving many shelves. Databases obsess "
            "over keeping related data on the same shelf — that's what a page-aligned data structure means."
        ),
        "how_it_works": [
            "<strong>Tape (1950s–present):</strong> A literal spool of magnetic tape. Sequential reads are OK. "
            "Random reads are catastrophic — the spool must physically wind/unwind to the right position. "
            "Simulated benchmark: 4 sequential reads = 4s. 4 random reads = 22s. Still used at exabyte scale today (IBM).",
            "<strong>Hard Drive Discs (HDD):</strong> A spinning magnetic platter with a read/write arm. "
            "Pages are fixed sectors on the platter. Random reads require the arm to physically 'seek' to a new position — "
            "this mechanical seek time (5–10ms) is the bottleneck. Sequential reads just follow the spinning platter and are ~100× faster.",
            "<strong>Solid State Drives (SSD):</strong> No moving parts — data is stored in flash memory cells. "
            "Random reads are now only ~4× slower than sequential (vs 100× on HDD), but the page abstraction remains. "
            "You still read/write in 4KB pages. Databases still benefit from sequential patterns.",
            "<strong>The universal rule:</strong> Sequential access always beats random access on every storage medium. "
            "This is why databases use <strong>B+ trees</strong> and LSM trees — both are engineered around sequential page access. "
            "(Most databases use B+ trees specifically, not generic B-trees — the distinction is covered in Chapter 6.) "
            "The SSD's residual 4× penalty over sequential (vs HDD's 100×) comes from electronic overhead in flash access patterns — "
            "not mechanical movement, and not from erase cycles (erasing before writing is a <em>write</em> concern, not a read one). "
            "Without a moving arm there is no seek time, but the flash controller still has per-address lookup latency "
            "and cannot leverage the same sequential parallelism for random reads as it can for a stream. "
            "The penalty is architectural, not mechanical — and far smaller than HDD's 100×.",
        ],
        "connect": (
            "This chapter is the foundation for everything that follows. "
            "In Chapter 3, you'll see why sorted data matters — binary search reads pages sequentially. "
            "In Chapter 5, you'll see why the Buffer Manager exists — it caches recently-read pages in RAM to avoid going back to disk. "
            "Every data structure in Ben Dicken's series is essentially an answer to one question: "
            "<em>how do we minimize random page reads?</em>"
        ),
        "tradeoff": (
            "<strong>Sequential vs Random:</strong> HDD random read ≈ 100× slower than sequential. "
            "SSD random read ≈ 4× slower. RAM is 1,000× faster than SSD for any access pattern. "
            "This is why every performance-sensitive database tries to: "
            "(1) keep hot data in RAM, (2) write to disk sequentially, (3) batch random writes."
        ),
        "recall": [
            "Without looking at anything — what is a 'page' in the context of storage devices, and why do databases care about page size?",
            "Why is a random read on a hard drive dramatically slower than a sequential read? Describe the physical reason.",
            "An SSD is 'faster' than an HDD — but does the page abstraction still apply? What stays the same?",
        ],
        "takeaway": "Every read or write touches a full page, never a single byte. Databases are designed around minimizing the number of pages touched per operation.",
        "justin_quote": (
            "\"Most students just memorize that SSDs are faster than HDDs. But the top 1% understand <em>why</em> — and that understanding lets them design systems, not just describe them.\"",
            "Justin Sung — 16 Note-Taking Secrets of the Top 1% of Learners"
        ),
    },
    {
        "num": 2,
        "title": "The Full Software + Hardware Stack",
        "source": "The Software + Hardware Stack (and how to make it FAST)",
        "duration": "14 min",
        "problem": (
            "Your app is slow. You've optimised your code. But it's still slow. Why? "
            "Because performance problems can originate at any layer of the stack below your code — "
            "and most developers have never thought about what those layers are."
        ),
        "core_idea": (
            "Every application sits on a stack of layers: your code calls system libraries, "
            "which make system calls, which go through the kernel, which talks to physical hardware. "
            "A bottleneck at <em>any</em> layer makes the whole system slow — regardless of how "
            "well-written your application code is."
        ),
        "analogy": (
            "<strong>Analogy — The Restaurant Kitchen:</strong> You're the chef (application). "
            "You might cook brilliantly. But if the delivery truck bringing ingredients (network) is stuck in traffic, "
            "or the fridge (disk I/O) is broken, the meal is late. Your cooking didn't cause the delay — "
            "something in the supply chain did. Performance engineering means understanding every part of the supply chain, not just your kitchen."
        ),
        "how_it_works": [
            "<strong>Application Layer:</strong> Your code — a web app, a database, a game. You control this entirely. "
            "Written in Python, Go, Java, C++. The code can be fast or slow based on your choices.",
            "<strong>System Libraries:</strong> Pre-built code your app relies on (libc on Linux, Foundation on macOS). "
            "You don't write these — they're provided by the OS. A slow library is a bottleneck you can't directly fix.",
            "<strong>System Calls:</strong> The guarded crossing from user-space to kernel-space. "
            "Why guarded? To prevent user processes from directly corrupting kernel memory or each other's address spaces. "
            "Every file read, network request, and memory allocation crosses this boundary. Each crossing has overhead: "
            "the CPU switches privilege levels, saves register state, and switches stacks. "
            "Batching operations reduces system call frequency — real optimisation, but with a cost: "
            "each individual request waits longer before being submitted (higher per-request latency, lower frequency of crossings).",
            "<strong>Kernel:</strong> The core of the OS. Manages CPU scheduling, RAM allocation, disk I/O, networking. "
            "Databases often use kernel-bypass techniques to reduce overhead. "
            "<strong>io_uring</strong> (Linux): instead of one system call per I/O request, the application and kernel share a ring buffer in memory — "
            "a submission queue and a completion queue. The application drops requests into shared memory; the kernel picks them up and returns results, "
            "eliminating most per-call crossings entirely.",
            "<strong>Hardware:</strong> CPU cores, RAM, NVMe SSD, network card. The absolute floor. "
            "No amount of software optimisation beats choosing faster hardware — but hardware is expensive.",
        ],
        "connect": (
            "Chapter 1 lives at the bottom of this stack — disk I/O is a hardware concern. "
            "The rest of Ben Dicken's series is about making decisions in the Application and Kernel layers "
            "that reduce how often you reach the hardware floor. "
            "When Chapter 5 introduces the Buffer Manager, it's specifically an application-layer solution "
            "that caches disk reads in RAM — moving work from the bottom of the stack to near the top."
        ),
        "tradeoff": (
            "<strong>Every layer adds latency:</strong> A user-space cache lookup (nanoseconds) beats a disk read (milliseconds) by 1,000,000×. "
            "The engineer's job is to serve as many requests as possible without going below the system call layer. "
            "The trade-off: keeping data higher in the stack (RAM, CPU cache) costs money and limits data size."
        ),
        "recall": [
            "Name the 5 layers of the software + hardware stack from top to bottom, without notes.",
            "A developer says: 'My code is perfectly optimised — the app must be fast.' What's wrong with this reasoning?",
            "What is a 'system call' and why does reducing the number of system calls improve performance?",
        ],
        "takeaway": "Performance can break at any layer. Good engineers reason about the whole stack, not just their code.",
        "justin_quote": (
            "\"Beginners optimise their code. Advanced learners optimise their mental model of the entire system. "
            "The goal is to see the whole picture before diving into any single component.\"",
            "Justin Sung — How to Learn Really Hard Subjects Easily"
        ),
    },
    {
        "num": 3,
        "title": "Data Organisation: The Read-Write Trade-off",
        "source": "Data Organization: Making Database CRUD Operations Fast",
        "duration": "13 min",
        "problem": (
            "If you dump one billion records onto disk in the order they arrive, "
            "finding any specific record requires scanning every single one. "
            "That's unusable at scale. The way you <em>organise</em> data before storing it "
            "is the single biggest lever on database performance."
        ),
        "core_idea": (
            "There is a fundamental trade-off between read performance and write performance. "
            "Organising data to make reads fast (e.g., sorted order) makes writes more expensive. "
            "Optimising writes (append-only) makes reads expensive. "
            "Every database design is a deliberate position on this spectrum."
        ),
        "analogy": (
            "<strong>Analogy — The Messy Desk vs. The Filing Cabinet:</strong> "
            "Tossing papers on your desk as they arrive is extremely fast to write (O(1)) — "
            "just drop it anywhere. But finding last Tuesday's receipt means searching the whole pile (O(n)). "
            "A filing cabinet sorted alphabetically takes extra work when filing (you must find the right spot), "
            "but finding anything is nearly instant. Databases face this exact choice with every table they design."
        ),
        "how_it_works": [
            "<strong>Unsorted array (append-only):</strong> New records go wherever there's space. "
            "Write = O(1). Read = O(n) full scan. Used in Write-Ahead Logs for exactly this reason — "
            "WAL writes need to be blindingly fast; you'll read them only during crash recovery.",
            "<strong>Sorted array:</strong> Records kept in order as they're inserted. "
            "Read = O(log n) via binary search. Write = O(n) because inserting in the middle shifts everything right. "
            "Good for read-heavy workloads (80–90% reads is common in production databases).",
            "<strong>Binary Search Tree:</strong> Each node has a left subtree (smaller values) and right (larger). "
            "Both read and write = O(log n) on average. But trees become unbalanced over time, "
            "degrading to O(n) in the worst case. Not suitable for disk-based storage (too many random page reads).",
            "<strong>B+ tree — what databases actually use (Chapter 6):</strong> Balances automatically. "
            "Node size deliberately equals one disk page — intentional design, not coincidence. "
            "Both read and write = O(log n) guaranteed. "
            "Three rules that distinguish B+ trees from generic B-trees: "
            "(1) Internal nodes store <em>only keys</em> — no values. "
            "(2) Values live <em>exclusively at leaf nodes</em> — the bottom level of the tree only. "
            "(3) Leaf nodes have <strong>neighbour pointers</strong> — a linked list connecting all leaves left-to-right, "
            "enabling efficient range scans by walking the leaves directly rather than re-traversing from the root. "
            "When a leaf node fills up, a <strong>node split</strong> divides its keys down the middle, "
            "redistributes entries between the old and new node, "
            "and promotes the middle key <em>upward to the parent</em> — this is how balance is maintained across all levels of the tree, "
            "keeping tree depth bounded at O(log n) regardless of how many inserts occur. "
            "This is why Postgres, MySQL, SQLite all use B+ trees as their default index — not generic B-trees.",
        ],
        "connect": (
            "This chapter explains <em>why</em> every data structure in this series exists — "
            "each one is a different answer to the read-write trade-off. "
            "LSM trees (Chapter 8) lean hard toward write performance. "
            "B-trees (Chapter 6) balance both. Sorted arrays work when your data never changes (read-only analytics). "
            "Come back to this chapter whenever a new structure seems confusing — "
            "ask yourself: where does it sit on the read-write spectrum?"
        ),
        "tradeoff": (
            "<strong>The universal database trade-off:</strong> "
            "In most web applications, reads outnumber writes 80:20 or even 95:5. "
            "This is why databases default to read-optimised structures (B+ trees with indexes). "
            "Write-heavy workloads (logging, event streams, metrics) flip the equation — "
            "and use write-optimised structures like LSM trees. "
            "B+ trees achieve O(log n) for both reads <em>and</em> writes because node splits keep the tree depth bounded: "
            "no matter how many rows are inserted, the tree never grows deeper than O(log n) levels, "
            "so both reads and writes touch at most O(log n) pages."
        ),
        "recall": [
            "What is the time complexity of a read and write on an unsorted array? A sorted array? Why the difference?",
            "You're building a database that receives 1 million sensor readings per second but is only queried once per hour. Which end of the read-write trade-off do you optimise for?",
            "A BST gives O(log n) read and write — yet databases never use it as a disk index. Why? And what two structural rules make a B+ tree disk-friendly where the BST fails? Finally: what structural feature distinguishes a B+ tree from a generic B-tree, and why does it matter for range queries?",
        ],
        "takeaway": "Organising data for fast reads costs write performance, and vice versa. Every database structure is a deliberate choice on this spectrum.",
        "justin_quote": (
            "\"The moment you see a trade-off, you're thinking like an engineer, not a student. "
            "Students memorise structures. Engineers ask: what problem does this structure exist to solve?\"",
            "Justin Sung — How to Think Like the Top 1%"
        ),
    },
    {
        "num": 4,
        "title": "The Cell Layout: How a Database Page Works",
        "source": "The BEST Way to Organize Data (in a Database)",
        "duration": "13 min",
        "problem": (
            "A database page is 8KB of raw bytes. You need to store rows of data inside it — "
            "but rows vary in size: a username might be 5 bytes, an address 200 bytes. "
            "How do you organise these variable-length rows inside a fixed-size page so that "
            "insertions, deletions, and scans are all efficient?"
        ),
        "core_idea": (
            "The <strong>cell layout</strong> (used by SQLite, PostgreSQL, and others) stores "
            "two things in every page: a compact sorted array of fixed-size <em>pointers</em> at one end, "
            "and variable-size <em>row values</em> packed at the other end. "
            "The pointers know where each row lives; the rows can be any size. "
            "The two ends grow toward each other as the page fills up."
        ),
        "analogy": (
            "<strong>Analogy — The Hotel Key Rack:</strong> Imagine a hotel where room keys hang on a numbered rack (the pointer array). "
            "The keys are tiny, always in room-number order, and always in the same spot on the wall. "
            "The actual rooms behind the doors (row values) can be suites or closets — wildly different sizes. "
            "The concierge (your database engine) always goes to the key rack first, "
            "finds the right key (pointer/offset), then opens the door (reads the row). "
            "The rack stays neat and sorted regardless of what's behind the doors."
        ),
        "how_it_works": [
            "<strong>Page header:</strong> Stores metadata — page ID, checksum, and crucially: "
            "how many rows are in this page. This count tells the engine how many pointers to read.",
            "<strong>Pointer array (fixed-size):</strong> A tightly-packed array of 2-byte integers, "
            "each storing a byte offset within the page. These stay in sorted order by key. "
            "Sorted pointers enable binary search across rows without reading the rows themselves.",
            "<strong>Row values (variable-size):</strong> Packed from the other end of the page. "
            "Each row stores its own length so the engine knows how many bytes to read. "
            "Rows can have gaps between them (fragmentation) — the pointer array handles this gracefully.",
            "<strong>Insertion:</strong> Write the new row value at the end of the existing values. "
            "Insert a new pointer in sorted order in the pointer array. Only the pointer array shifts — "
            "not the row data itself. O(n) pointer shift but O(1) data write.",
            "<strong>Deletion:</strong> Remove the pointer. Mark the row space as free. "
            "Periodically compact the page to reclaim fragmented space (called a 'vacuum' in PostgreSQL).",
        ],
        "connect": (
            "This chapter zooms into a single B+ tree node and shows what's inside it. "
            "In a B+ tree: internal nodes contain keys only (no values), while leaf nodes contain the actual row values "
            "<em>and</em> a neighbour pointer to the next leaf — enabling range scans by walking leaves left-to-right. "
            "Both node types use this same cell layout: header + pointer array + variable-size content. "
            "Leaf nodes simply pack their content region with actual data rows instead of child pointers. "
            "When a B+ tree page splits (Chapter 6), it is exactly this structure that divides: "
            "the pointer array splits, values migrate, headers update. "
            "VACUUM in PostgreSQL is also explained here: immediate compaction on every deletion would require "
            "rewriting and re-sorting all row data on the page for each delete — prohibitively expensive. "
            "Deferring compaction until VACUUM runs lets the page accumulate many deletions cheaply, "
            "then reclaim all fragmented space in one pass."
        ),
        "tradeoff": (
            "<strong>Space efficiency vs. simplicity:</strong> The cell layout wastes some space due to fragmentation "
            "(gaps between deleted rows). A simpler fixed-size layout wastes no space but can't handle variable-length data. "
            "The cell layout wins in practice because real-world rows (usernames, addresses, descriptions) are never uniform in size."
        ),
        "recall": [
            "Draw from memory: what are the three regions of a database page using the cell layout? Describe what each stores.",
            "Why are the pointers kept in sorted order even when the row values behind them aren't sorted?",
            "What happens to the page when a row is deleted — and why is immediate compaction not done? "
            "In a B+ tree, leaf nodes have one structural addition beyond the standard cell layout header + pointers + values. "
            "What is it, and what operation does it enable?",
        ],
        "takeaway": "A database page separates the index (sorted pointer array) from the data (variable-size rows). This lets you search efficiently without rewriting rows on every change.",
        "justin_quote": (
            "\"Draw it from memory. If you can draw a system accurately from scratch, you own it. "
            "If you can't, you've been reading, not learning.\"",
            "Justin Sung — The Top 1% Think on Paper. Here's How to Do It."
        ),
    },
    {
        "num": 5,
        "title": "The 5 Core Components of a Storage Engine",
        "source": "Data Storage Engines: The 5 Must-Know Components",
        "duration": "10 min",
        "problem": (
            "Knowing how to store rows on disk is only one part of building a database. "
            "What prevents two users from corrupting each other's data simultaneously? "
            "What happens if the power cuts out mid-write? "
            "How does the database avoid hitting disk for every read? "
            "These are five different problems — and each has its own dedicated component."
        ),
        "core_idea": (
            "Every relational database storage engine is composed of five components: "
            "<strong>Transaction Manager, Lock Manager, Access Layer, Buffer Manager, "
            "and Recovery Manager.</strong> "
            "Together they transform a raw collection of pages on disk into a reliable, "
            "concurrent, fast database."
        ),
        "analogy": (
            "<strong>Analogy — A Busy Hospital:</strong> "
            "Think of a hospital with hundreds of patients and staff operating simultaneously. "
            "The <strong>Access Layer</strong> = nurses who fetch and update patient records. "
            "The <strong>Buffer Manager</strong> = the nurses' station where frequently-needed files are kept close by. "
            "The <strong>Lock Manager</strong> = the booking system that prevents two surgeons from claiming the same operating theatre. "
            "The <strong>Transaction Manager</strong> = the surgical checklist that ensures either the full operation completes or none of it does — no half-finished procedures. "
            "The <strong>Recovery Manager</strong> = the black box recorder that logs every action so the full picture can be reconstructed after any incident."
        ),
        "how_it_works": [
            "<strong>Transaction Manager:</strong> Ensures that a sequence of queries behaves as a single atomic unit. "
            "From the database's perspective: either ALL of the changes happen, or NONE of them do. "
            "This is the 'A' in ACID — Atomicity.",
            "<strong>Lock Manager:</strong> When two queries try to modify the same rows simultaneously, "
            "one must wait. The lock manager decides who waits and for how long. "
            "It also detects <strong>deadlocks</strong> — when Transaction A holds a lock Transaction B needs, "
            "while B holds a lock A needs, creating a cycle with no natural exit. "
            "Resolution: the database chooses one transaction to kill (rolling it back completely), "
            "releasing its locks and allowing the other to proceed.",
            "<strong>Access Layer:</strong> The internal CRUD interface. A running query doesn't "
            "need to know whether the storage engine uses a B+ tree or an LSM tree — "
            "it just asks the access layer: 'Give me the row with ID=42.' The access layer handles the details. "
            "The choice of data structure behind it is a trade-off: "
            "<strong>B+ trees</strong> are read-optimised — in-place updates, O(log n) for both reads and writes, "
            "ideal when reads dominate. "
            "<strong>LSM trees</strong> are write-optimised — all writes go to a fast in-memory buffer (memtable) "
            "and are flushed to disk in sorted batches; reads are slower because they may need to merge multiple files. "
            "Postgres, MySQL, and SQLite use B+ trees. RocksDB and Cassandra use LSM trees.",
            "<strong>Buffer Manager:</strong> Keeps recently-read pages in RAM. "
            "When a query needs a page, the buffer manager checks RAM first. "
            "Only on a cache miss does it go to disk. "
            "This is the single biggest performance win in any database — "
            "because RAM access takes ~100 nanoseconds while disk access takes ~10 milliseconds: "
            "a 100,000× difference. Serving even a fraction of reads from RAM transforms performance.",
            "<strong>Recovery Manager:</strong> Maintains a Write-Ahead Log (WAL). "
            "Key term: a <strong>dirty page</strong> = a page modified in RAM but not yet flushed to disk. "
            "The WAL principle: log the intended change BEFORE writing it to the data file. "
            "On crash, replay the WAL to restore any interrupted transaction. "
            "Why WAL exists: updating a single row that has three indexes means three separate B+ tree updates — "
            "each potentially a scattered page write to different locations on disk. "
            "WAL captures all three as one atomic log entry first, then applies them. "
            "One log entry. Multiple data file changes. No partial state ever visible on disk. "
            "Performance insight: the WAL write is <em>sequential</em> (one append to the end of a log file — fast). "
            "The scattered B+ tree page updates are <em>random I/O</em> (expensive). "
            "WAL defers the expensive random writes until the sequential log is safely committed — "
            "giving both crash safety and a write performance advantage.",
        ],
        "connect": (
            "This chapter is the map for the entire rest of Ben Dicken's series. "
            "Upcoming videos zoom into each component: "
            "Write-Ahead Logs (Recovery Manager), Buffer Pool (Buffer Manager), "
            "ACID transactions (Transaction Manager), deadlocks (Lock Manager), "
            "B-trees and LSM trees (Access Layer). "
            "When you watch those videos, remember: you're zooming into one room of the hospital, not learning a separate subject."
        ),
        "tradeoff": (
            "<strong>Complexity vs. capability:</strong> Each component adds overhead. "
            "An in-memory database can skip the Buffer Manager and Recovery Manager entirely — "
            "everything lives in RAM, and if the power cuts out, the data is gone (acceptable for caches). "
            "A read-only analytics database can skip the Lock Manager (no concurrent writes to conflict) — "
            "but this is a permanent architectural commitment: the moment you add any write path, "
            "you must retrofit the entire locking machinery. Skipping a component is not free; "
            "it locks you into the workload you have today. "
            "The 5-component model is the full production-grade design — know which components you actually need."
        ),
        "recall": [
            "Name all 5 storage engine components from memory. For each, describe its job in one sentence.",
            "Your database crashes mid-transaction — 500 rows were supposed to be updated but only 200 were written. Which component prevents this from happening? How?",
            "Why does a cache (Redis, Memcached) not need a Lock Manager or Recovery Manager, but PostgreSQL does?",
        ],
        "takeaway": "A database storage engine is five interlocking systems. Understanding each one lets you reason about why databases behave the way they do under load, failure, and concurrency.",
        "justin_quote": (
            "\"Once you have the map of a system — its components and how they connect — "
            "every detail you learn after that snaps into place instantly. "
            "The map is worth more than a hundred individual facts.\"",
            "Justin Sung — 5 Levels of Learning Every Graduate Must Master"
        ),
    },
]


def render_html(chapters: list[dict]) -> str:
    parts = [f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'>"
             f"<title>Ben Dicken: Database Internals — Phase 1 Learning Pack</title>"
             f"<style>{CSS}</style></head><body>"]

    # Cover
    toc_items = "".join(
        f"<div class='toc-item'>"
        f"<span><span class='chapter-num'>CH{c['num']}</span>&nbsp;&nbsp;{c['title']}</span>"
        f"<span>{c['duration']}</span></div>"
        for c in chapters
    )
    parts.append(f"""
    <div class='cover'>
      <div class='cover-label'>Ben Dicken × Justin Sung Framework</div>
      <h1>Database Internals<br>Phase 1: Foundations</h1>
      <div class='subtitle'>
        How computers store data — and why every design decision<br>flows from the physics of the storage medium.
      </div>
      <div class='cover-rule'></div>
      <div class='framework-note'>
        Each chapter follows Justin Sung's learning framework:<br>
        <strong>Why</strong> the concept exists · <strong>Core Idea</strong> · <strong>Analogy</strong> ·
        <strong>How It Works</strong> · <strong>Connect the Dots</strong> · <strong>Trade-offs</strong> ·
        <strong>Active Recall</strong> · <strong>Key Takeaway</strong>
      </div>
      <div class='toc'>
        <h2>Contents</h2>
        {toc_items}
      </div>
    </div>""")

    for ch in chapters:
        steps_html = "".join(
            f"<li><span class='step-num'>{i+1}</span>"
            f"<span class='step-text'>{s}</span></li>"
            for i, s in enumerate(ch["how_it_works"])
        )
        recall_html = "".join(
            f"<div class='recall-q'><span class='q-num'>Q{i+1}</span>"
            f"<span class='q-text'>{q}</span></div>"
            f"<div class='answer-space'></div>"
            for i, q in enumerate(ch["recall"])
        )
        quote_text, quote_attr = ch["justin_quote"]
        parts.append(f"""
        <div class='chapter'>
          <div class='chapter-header'>
            <div class='chapter-eyebrow'>Chapter {ch['num']} of {len(chapters)}</div>
            <h2>{ch['title']}</h2>
            <div class='chapter-meta'>Source: {ch['source']} &nbsp;·&nbsp; {ch['duration']}</div>
          </div>

          <div class='section'>
            <div class='section-label'>The Problem This Solves</div>
            <div class='callout problem'>
              <div class='callout-icon'>⚡ Why does this exist?</div>
              <p>{ch['problem']}</p>
            </div>
          </div>

          <div class='section'>
            <div class='section-label'>The Core Idea</div>
            <p>{ch['core_idea']}</p>
          </div>

          <div class='section'>
            <div class='callout analogy'>
              <div class='callout-icon'>💡 Mental Model</div>
              <p>{ch['analogy']}</p>
            </div>
          </div>

          <div class='section'>
            <div class='section-label'>How It Works</div>
            <ul class='steps'>{steps_html}</ul>
          </div>

          <div class='section'>
            <div class='callout connect'>
              <div class='callout-icon'>🔗 Connect the Dots</div>
              <p>{ch['connect']}</p>
            </div>
          </div>

          <div class='section'>
            <div class='callout tradeoff'>
              <div class='callout-icon'>⚖️ The Trade-off</div>
              <p>{ch['tradeoff']}</p>
            </div>
          </div>

          <div class='recall-box'>
            <div class='recall-header'>🔁 Active Recall</div>
            <div class='recall-instruction'>
              Close this book. Answer these questions from memory. The struggle of recalling — not re-reading — is what builds permanent memory. (Justin Sung)
            </div>
            {recall_html}
          </div>

          <div class='takeaway'>
            <div class='takeaway-label'>Key Takeaway</div>
            <p>{ch['takeaway']}</p>
          </div>

          <div class='justin-quote'>
            {quote_text}
            <div class='attribution'>— {quote_attr}</div>
          </div>
        </div>""")

    parts.append("</body></html>")
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Generate Ben Dicken Learning Pack PDF")
    parser.add_argument("--output", default="output/ben_dicken_phase1.pdf")
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    html_path = out.with_suffix(".html")
    html = render_html(CHAPTERS)
    html_path.write_text(html, encoding="utf-8")
    print(f"HTML written: {html_path}")

    try:
        from weasyprint import HTML
        HTML(string=html, base_url=str(Path.cwd())).write_pdf(str(out))
        print(f"PDF written: {out}  ({out.stat().st_size // 1024} KB)")
    except Exception as e:
        print(f"weasyprint error: {e}")
        print(f"HTML is ready at {html_path} — open in browser and Print → Save as PDF")


if __name__ == "__main__":
    main()
