#!/usr/bin/env python3
"""
System Design, Two Lenses: Decide Consciously, Build for Production
Dual-lens reference pairing lucsystemdesign (decision frameworks) with
sdcourse (production build) across 23 chapters.
Run: python3 scripts/generate_sdcourse_luc.py
"""
import os

# ─────────────────────────────────────────────────────────────────────────────
# CSS — copied from generate_vutr_spark.py, Mermaid <script> tag NOT included
# (Mermaid does not render in headless-Chrome print — see repo CLAUDE.md /
# spark-pack-scribble-layer memory). All diagrams are inline SVG instead.
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
.cover-title{font-family:'Inter',sans-serif;font-size:26pt;font-weight:700;line-height:1.15;color:var(--ink);margin-bottom:4mm}
.cover-sub{font-size:12pt;color:var(--muted);font-style:italic;margin-bottom:9mm}
.rule{width:14mm;height:3px;background:#3b82f6;margin-bottom:7mm}
.cover-desc{font-family:'Inter',sans-serif;font-size:9pt;color:var(--body);line-height:1.6;max-width:130mm;margin-bottom:10mm}
.cover-toc{margin-top:4mm}
.toc-item{display:flex;align-items:baseline;padding:2mm 0;border-bottom:1px solid var(--border);font-family:'Inter',sans-serif;font-size:8.5pt}
.toc-n{font-weight:700;color:#3b82f6;width:16mm;flex-shrink:0}

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
.box.xr{background:#f5f3ff;border-color:#7c3aed}.box.xr .box-lbl{color:#7c3aed}
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

/* Scribble layer — hand-drawn diagrams (GRINDE: Non-verbal + Emphasized) */
.sketch{margin:4mm 0 1mm;text-align:center;page-break-inside:avoid}
.sketch svg{max-width:100%;height:auto}
.sketch-cap{font-family:'Caveat',cursive;font-size:12pt;color:#44446a;text-align:center;margin:0 0 4mm;line-height:1.25}
"""

# ─────────────────────────────────────────────────────────────────────────────
# COVER
# ─────────────────────────────────────────────────────────────────────────────
COVER = """
<div class="cover">
  <div class="eyebrow">System Design · Two Lenses</div>
  <div class="cover-title">Decide Consciously, Build for Production</div>
  <div class="cover-sub">Pairing lucsystemdesign's decision frameworks with sdcourse's production benchmarks across 23 chapters of distributed-systems fundamentals.</div>
  <div class="rule"></div>
  <div class="cover-desc">Every chapter carries both voices: Luc reframes the misconception and gives a decision rule ("when NOT to use it"); sdcourse grounds the same domain in production failure modes and exact benchmarks. Each chapter closes with an explicit convergence/divergence synthesis.</div>
  <div class="cover-toc">
    <!-- TOC items appended here, one per phase, as chapters land -->
  </div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTERS — appended below, one CH{n} block per chapter, across 4 phases
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 1 — Quality Attributes, Trade-offs & the Production Reality Gap
# ─────────────────────────────────────────────────────────────────────────────
CH1 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 1 of 23</div>
  <h1>Quality Attributes, Trade-offs & the Production Reality Gap</h1>
  <div class="ch-src">Sources: lucsystemdesign — System Design Quality Attributes · sdcourse — Course Structure and Curriculum Design</div>
  <p class="ch-sum">Luc supplies the vocabulary for what "good" even means in a system — attributes, pillars, tactics — and the discipline to admit you cannot maximize all of it at once. sdcourse supplies the reason that vocabulary alone will not save you: there is a gap between knowing the trade-offs and having actually built something that survives them.</p>
</div>

<div class="topic">
<h2>Luc's Lens: Attributes Are Goals, Not Features</h2>
<p>Most system design failures are not caused by a missing feature. They are caused by a system that cannot hold up once real traffic, real failure rates, and real attackers show up. Luc's framing starts there: slow requests, flaky uptime, tangled code, and weak security are the actual killers, and none of them show up on a feature checklist. Quality attributes — availability, consistency, latency, scalability, reliability, security — are the properties that determine whether a system survives contact with production, and Luc insists they be treated as first-class requirements gathered and negotiated up front, not bolted on after the "real" features are built.</p>
<p>The second half of the lens is a discipline about honesty: you cannot maximize everything simultaneously. Availability competes with cost. Strong consistency competes with global latency. Flexibility competes with simplicity. Every one of these is a dial, and turning one dial up turns another down — there is no configuration where all dials sit at maximum. Luc separates the vocabulary into three layers so the trade-off is easier to reason about: attributes are the goals ("this system should be highly available"), pillars are the strategies that get you there (modularity, redundancy, fault tolerance), and tactics are the concrete mechanisms that implement a pillar (caching, sharding, circuit breakers). Skipping straight to tactics without naming the attribute and pillar behind them is how teams end up with a cache that solves the wrong problem.</p>
<p>Vague targets compound the problem. Saying a system should be "highly available" or "scalable" gives an engineer nothing to design against — it is not falsifiable and it does not survive a design review. Luc's fix is the attribute scenario: a specific what-if statement ("if the payments region goes down, checkout must fail over within 30 seconds with no data loss") that turns an adjective into a testable requirement. Scalability itself gets the same specificity treatment — a scalable system handles more traffic by adding resources, not by rewriting code, and statelessness is what makes that horizontal add-more-boxes move possible in the first place. Reliability, likewise, is reframed away from "it doesn't crash" toward something sharper: predictable behavior under unpredictable conditions. And security is reframed away from a checklist item toward an embedded assumption — secure systems are designed expecting breaches, and the design's job is to constrain the blast radius, not pretend the breach won't happen.</p>
<div class="box s"><div class="box-lbl">Decision Rule</div>
<p>Before choosing a tactic, name the attribute it serves and the pillar it implements — and name what you are giving up. If you cannot state the competing attribute you are trading away (cost, latency, simplicity), you have not made a design decision, you have made a guess. When NOT to use a tactic: when you cannot yet write the attribute scenario it is supposed to satisfy — reaching for caching, sharding, or circuit breakers before the requirement is falsifiable just adds complexity in search of a problem.</p>
</div>
<div class="quote" data-author="luc">"Many systems fail not because a feature is missing, but because the system buckles under real-world pressure: slow requests, flaky uptime, tangled code, or weak security."<cite>— Luc, lucsystemdesign</cite></div>
</div>

<div class="topic">
<h2>sdcourse's Lens: The Gap Between the Map and the Shovel</h2>
<p>sdcourse's angle is not about naming attributes — it is about what it actually costs to build a system that satisfies them. The curriculum this examiner grounds itself in is a 254-lesson roadmap spanning Days 1–270, building one continuous artifact: a complete distributed log processing system called LogStream, with a Java/Spring Boot track running in parallel with a Python/JavaScript track over the same material. The course is 80% coding, and the hardware bar is explicit — 16GB RAM required, 8GB minimum "but you'll suffer." None of that detail is decoration; it is sdcourse's way of insisting that quality attributes are not learned by reading about them, they are learned by hitting the failure mode they describe.</p>
<p>That insistence is aimed squarely at a specific failure sdcourse has watched repeatedly: engineers who can recite "CAP theorem," "availability vs. consistency," or "circuit breaker" fluently in an interview but have never built the thing that makes those trade-offs real. Knowing the vocabulary from Luc's lens is necessary but not sufficient — sdcourse's whole curriculum design exists to close the gap between the two. The predictors of who actually closes that gap are concrete and unglamorous: run the code instead of just reading it, treat the GitHub reference repo as a checkpoint rather than a shortcut to copy from, and show up in Discord — of the three, Discord activity is the single best predictor of who finishes.</p>
<table>
<thead><tr><th>Signal</th><th>Finisher behavior</th><th>Lurker behavior</th></tr></thead>
<tbody><tr><td>Code execution</td><td>Runs every day's code, hits real errors, debugs them</td><td>Reads the lesson, never executes it</td></tr>
<tr><td>Reference repo</td><td>Uses it as a checkpoint to compare against</td><td>Copies from it as a shortcut</td></tr>
<tr><td>Discord activity</td><td>Active — best single predictor of completion</td><td>Absent</td></tr>
<tr><td>Hardware</td><td>16GB RAM (course-recommended)</td><td>8GB minimum — "but you'll suffer"</td></tr>
<tr><td>Timeline</td><td>270 days, treated as a reference, not a race</td><td>Falls behind and drops rather than resuming</td></tr>
</tbody>
</table>
<div class="box r"><div class="box-lbl">Production Reality</div>
<p>A student who can define "availability vs. consistency" from a flashcard has not yet paid the cost that makes the definition mean anything. The course is structured around 254 lessons of hands-on output specifically because the failure mode it is designed against is passive consumption — someone who nods along to Luc's attribute/pillar/tactic framework but has never had a tactic fail on them at 2am. sdcourse's answer to "how do I actually learn quality attributes" is not more reading; it is building LogStream day by day and falling behind on purpose, because falling behind and resuming is what the 270-day timeline is built to tolerate.</p>
</div>
<div class="quote" data-author="sdcourse">"There is a massive gap between 'knowing' system design for an interview and 'building' a system that survives a production workload. Most courses give you the map, but they don't give you the shovel."<cite>— sdcourse</cite></div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <rect x="40" y="40" width="260" height="150" rx="12" fill="#eff6ff"/>
    <rect x="400" y="40" width="260" height="150" rx="12" fill="#fff7ed"/>
  </g>
  <text x="170" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">LUC: Name the Trade-off</text>
  <text x="170" y="75" text-anchor="middle" font-size="13" fill="#1e3a8a">Attribute → Pillar → Tactic</text>
  <text x="170" y="105" text-anchor="middle" font-size="13" fill="#1e3a8a">You can't max everything —</text>
  <text x="170" y="130" text-anchor="middle" font-size="13" fill="#1e3a8a">write the attribute scenario</text>
  <text x="170" y="160" text-anchor="middle" font-size="13" fill="#1e3a8a">before picking the tactic</text>
  <text x="530" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#7c2d12">SDCOURSE: Build the Thing</text>
  <text x="530" y="75" text-anchor="middle" font-size="13" fill="#7c2d12">254 lessons, 270 days,</text>
  <text x="530" y="105" text-anchor="middle" font-size="13" fill="#7c2d12">one system: LogStream</text>
  <text x="530" y="130" text-anchor="middle" font-size="13" fill="#7c2d12">Map ≠ Shovel — run the</text>
  <text x="530" y="160" text-anchor="middle" font-size="13" fill="#7c2d12">code, hit the errors</text>
</svg>
</div>
<div class="sketch-cap">Luc hands you the map of trade-offs; sdcourse hands you the shovel to find out what the map didn't show.</div>

<div class="box xr"><div class="box-lbl">Where They Converge / Diverge</div>
<p><strong>Converge:</strong> Both reject vague competence — Luc rejects vague attribute targets like "highly available" in favor of falsifiable scenarios, and sdcourse rejects passive reading in favor of falsifiable execution (run it, hit the error, debug it); each is demanding proof instead of a claim.</p>
<p><strong>Diverge:</strong> Luc's unit of rigor is a sentence — an attribute scenario you can write down before you build anything — while sdcourse's unit of rigor is elapsed time and executed code across 270 days; one is a pre-design discipline, the other is a post-design endurance test, and a team can ace the first while still failing the second.</p>
</div>

<div class="recall">
<div class="recall-head">Active Recall</div>
<div class="q"><span class="q-n">Q1.</span> A teammate proposes adding a Redis cache to "improve performance." Using Luc's attribute → pillar → tactic decision rule, what two questions must be answered before this tactic is approved?</div>
<div class="q"><span class="q-n">Q2.</span> According to sdcourse's curriculum data, what is the single best predictor of whether a student finishes the 254-lesson LogStream course, and why does that beat "reads every lesson"?</div>
<div class="q"><span class="q-n">Q3.</span> Explain the difference between the kind of rigor Luc's attribute scenarios enforce and the kind of rigor sdcourse's 270-day build enforces — why could a team pass one and still fail the other?</div>
</div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 2 — Consistency Models: CAP, ACID vs BASE, Strong vs Eventual & Multi-Region
# ─────────────────────────────────────────────────────────────────────────────
CH2 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 2 of 23</div>
  <h1>Consistency Models: CAP, ACID vs BASE, Strong vs Eventual & Multi-Region</h1>
  <div class="ch-src">Sources: lucsystemdesign — CAP Theorem, ACID vs BASE, Strong vs Eventual Consistency · sdcourse — Multi-Region Replication and Distributed Consistency</div>
  <p class="ch-sum">Luc supplies the decision framework for consistency — CAP is not a permanent trade-off but a question of what happens when the network splits, and ACID/BASE and strong/eventual are the same question asked at the data-model and read-path layers. sdcourse supplies the number that makes the framework operational: what lag is acceptable, measured in seconds, across real regions.</p>
</div>

<div class="topic">
<h2>Luc's Lens: One Question, Asked Three Times</h2>
<p>Luc's core reframe of the CAP theorem is that "pick two of three" is catchy but misleading. CAP is not about permanently giving something up — during normal operation, when nodes can talk to each other reliably, a system can have both consistency and availability at once. The trade-off only appears the moment the network actually breaks. CP systems respond to that moment by refusing or delaying operations rather than risk returning something wrong; AP systems respond by continuing to serve, accepting that some responses may be stale. Luc's decision rule collapses this into one question: what hurts your product more — returning incorrect data, or returning no data at all? If incorrect data hurts more, choose CP. If no data hurts more, choose AP. Most real systems don't answer this once for the whole system — they carry a small CP core for writes that must be correct, wrapped in AP layers that serve and cache data quickly across regions.</p>
<p>ACID vs BASE is the same fork restated at the data-model layer. ACID and BASE sit on opposite ends of a spectrum shaped by CAP: ACID favors consistency and correctness even if it means refusing or delaying requests during failures, while BASE favors availability and scale even if it means serving temporarily inconsistent data. The catch Luc flags is that BASE's weakness shows up exactly where it hurts most — "this must never happen" rules, like double-spend, are hard to enforce in real time under an eventually-consistent model. The resolution is the same pattern as CAP: keep a small ACID core for operations that must always be correct, and use BASE layers to serve that data quickly across regions. ACID and BASE aren't rivals to be argued about in the abstract; they're tools suited to different failure modes and different expectations of the reader.</p>
<p>Strong vs eventual consistency is the same fork again, now asked at the read path. Strong consistency guarantees every read reflects the most recent successful write, no matter which replica answers — enforced through quorum confirmation and consensus algorithms like Paxos or Raft. Eventual consistency drops that guarantee: all replicas will converge to the same state over time, using conflict resolution strategies like last-write-wins or version vectors, but a read in the meantime may return outdated data. Luc's guidance is the same CP/AP question in different clothes: use strong consistency when accuracy is non-negotiable — financial transactions, stock levels, systems that coordinate scarce resources — and use eventual consistency when responsiveness and uptime matter most — user feeds, caching, globally distributed services. A banking system can't risk showing a stale balance, so it stops serving until replicas agree; a social app can't freeze every time replicas lose connection, so it shows "good enough" data and syncs later. Notice one important distinction Luc draws explicitly: CAP consistency (every read returns the most recent write across nodes) and ACID consistency (a transaction leaves the database in a valid state per defined rules) are different guarantees that happen to share a word — conflating them is a common source of muddled design conversations.</p>
<div class="box s"><div class="box-lbl">Decision Rule</div>
<p>Whichever layer you're deciding at — CAP, ACID/BASE, or strong/eventual — ask the same question: what hurts your product more, returning wrong data or returning no data? If wrong data hurts more, choose the consistent side (CP, ACID, strong). If no data hurts more, choose the available side (AP, BASE, eventual). When NOT to force a single global answer: most real systems need both — a small strongly-consistent core for the operations that must never be wrong, wrapped in an eventually-consistent, highly-available layer for everything else. Treating consistency as one system-wide setting instead of a per-operation decision is the mistake.</p>
</div>
<div class="quote" data-author="luc">"The common summary is 'pick two of three.' It's catchy, but misleading. CAP is not about permanently giving something up. It's about what happens when the network splits."<cite>— Luc, lucsystemdesign</cite></div>
</div>

<div class="topic">
<h2>sdcourse's Lens: Consistency Is a Number You Measure, Not a State You Achieve</h2>
<p>sdcourse's angle on consistency starts from a premise that sounds fatalistic but is meant to be operational: network partitions are inevitable, replication lag is normal, and chasing zero lag is a waste of engineering effort because zero lag is impossible. The right move is not to eliminate lag but to design for partition tolerance with eventual consistency, then measure and optimize for an acceptable lag level — a number with an owner and an alert threshold, not an aspiration. That framing turns Luc's CP/AP decision rule into a concrete operational target: once you've decided a subsystem is AP, the next question sdcourse forces is "how stale is too stale, in seconds?"</p>
<p>For a log processing system specifically, sdcourse argues active-active multi-region is almost always the right call, for a reason grounded in the shape of the workload: logs are append-only, high-volume, and latency-sensitive, so the deduplication cost of merging two regions after a split is far less than the cost of dropping events during an outage. The stakes of getting this wrong are concrete — a single-region log system is an availability bet, and delayed logs are nearly as dangerous as missing logs because they break the correlation windows used for incident diagnosis. Ordering compounds the difficulty: physical timestamps fail across regions because of clock skew, which is why sdcourse reaches for vector clocks to track logical event ordering instead of trusting wall-clock time. On the operational side, Kafka's MirrorMaker 2 is the concrete mechanism sdcourse points to for cross-region replication, using topic-offset translation specifically to prevent replication loops between regions.</p>
<table>
<thead><tr><th>Metric</th><th>Value</th><th>Why it matters</th></tr></thead>
<tbody><tr><td>MirrorMaker 2 added latency</td><td>50–200ms</td><td>Depends on network distance between regions; a floor, not a target</td></tr>
<tr><td>Replication lag alert threshold</td><td>&gt;10 seconds behind</td><td>Region B's consumer offset falling &gt;10s behind Region A's producer offset means you're approaching your RPO budget</td></tr>
<tr><td>Ordering guarantee</td><td>None from physical clocks</td><td>Clock skew across regions defeats timestamp ordering — use vector clocks instead</td></tr>
<tr><td>Loop prevention</td><td>Topic-offset translation</td><td>MirrorMaker 2's mechanism to stop replicated events from replicating back and forth forever</td></tr>
</tbody>
</table>
<div class="box r"><div class="box-lbl">Production Reality</div>
<p>Replication lag is the single most important operational metric in a multi-region log pipeline — not uptime, not throughput. The concrete threshold sdcourse gives is that if Region B's consumer offset falls more than 10 seconds behind Region A's producer offset, you are approaching your RPO budget, which means the "acceptable lag" from the decision to go eventually-consistent has stopped being acceptable and has become an incident. This is what separates a team that has merely chosen AP from a team that has operationalized it: the AP choice is a design decision made once, but the lag threshold is a number watched every minute.</p>
</div>
<div class="quote" data-author="sdcourse">"Replication lag is the single most important operational metric: if Region B's consumer offset falls more than 10 seconds behind Region A's producer offset, you are approaching your RPO budget."<cite>— sdcourse</cite></div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <rect x="40" y="40" width="260" height="150" rx="12" fill="#eff6ff"/>
    <rect x="400" y="40" width="260" height="150" rx="12" fill="#fff7ed"/>
  </g>
  <text x="170" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">LUC: One Question, 3 Layers</text>
  <text x="170" y="75" text-anchor="middle" font-size="13" fill="#1e3a8a">CAP / ACID·BASE / strong·eventual —</text>
  <text x="170" y="105" text-anchor="middle" font-size="13" fill="#1e3a8a">wrong data or no data?</text>
  <text x="170" y="135" text-anchor="middle" font-size="13" fill="#1e3a8a">Small consistent core,</text>
  <text x="170" y="160" text-anchor="middle" font-size="13" fill="#1e3a8a">available layer around it</text>
  <text x="530" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#7c2d12">SDCOURSE: Put a Number On It</text>
  <text x="530" y="75" text-anchor="middle" font-size="13" fill="#7c2d12">Zero lag is impossible —</text>
  <text x="530" y="105" text-anchor="middle" font-size="13" fill="#7c2d12">alert past 10s behind</text>
  <text x="530" y="135" text-anchor="middle" font-size="13" fill="#7c2d12">Vector clocks, not timestamps;</text>
  <text x="530" y="160" text-anchor="middle" font-size="13" fill="#7c2d12">active-active for logs</text>
</svg>
</div>
<div class="sketch-cap">Luc tells you which side of the trade-off to stand on; sdcourse tells you the second count at which standing there stops being fine.</div>

<div class="box xr"><div class="box-lbl">Where They Converge / Diverge</div>
<p><strong>Converge:</strong> Both reject the idea that consistency is ever fully "solved" — Luc insists you cannot avoid partitions by trusting your infrastructure, only reduce their frequency, and sdcourse insists network partitions are inevitable and zero replication lag is impossible; both treat the failure mode as permanent background weather to design for, not a bug to eliminate.</p>
<p><strong>Diverge:</strong> Luc's unit of decision is qualitative and made once per operation — CP or AP, ACID or BASE, strong or eventual, chosen by asking which failure hurts more — while sdcourse's unit of decision is quantitative and continuously monitored — a 10-second replication-lag threshold and a 50–200ms MirrorMaker 2 floor; a team can correctly choose "AP, eventual consistency, active-active" using Luc's framework and still get paged at 3am because nobody wired the alert sdcourse says the choice requires.</p>
</div>

<div class="recall">
<div class="recall-head">Active Recall</div>
<div class="q"><span class="q-n">Q1.</span> Using Luc's decision rule, a checkout service's inventory count and a social app's "likes" counter need different consistency models. Which question does Luc say you should ask for each, and what answer points to CP/ACID/strong vs AP/BASE/eventual?</div>
<div class="q"><span class="q-n">Q2.</span> Per sdcourse, why does a single-region log system count as "an availability bet," and what specific operational metric and threshold tells you your multi-region replication has crossed from acceptable lag into an RPO problem?</div>
<div class="q"><span class="q-n">Q3.</span> Luc and sdcourse both treat network partitions as inevitable rather than avoidable. Explain how their responses to that shared premise diverge — one gives a decision you make once, the other gives a number you watch continuously — and why a team could pass Luc's test but still fail sdcourse's.</div>
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
<title>System Design, Two Lenses — lucsystemdesign x sdcourse</title>
<style>{CSS}</style>
</head>
<body>
{COVER}
</body>
</html>"""

os.makedirs('output', exist_ok=True)
with open('output/sdcourse_luc.html', 'w') as f:
    f.write(HTML_CONTENT)
print('Written: output/sdcourse_luc.html')

try:
    import subprocess
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    pdf_path = "output/sdcourse_luc.pdf"
    html_path = "output/sdcourse_luc.html"
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
    print(f"HTML is ready at output/sdcourse_luc.html")
