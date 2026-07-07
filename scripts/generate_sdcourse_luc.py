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
    <div class="toc-item"><span class="toc-n">Ch 1</span><span>Quality Attributes, Trade-offs & the Production Reality Gap</span></div>
    <div class="toc-item"><span class="toc-n">Ch 2</span><span>Consistency Models: CAP, ACID vs BASE, Strong vs Eventual & Multi-Region</span></div>
    <div class="toc-item"><span class="toc-n">Ch 3</span><span>Database Selection & Distributed Query Patterns</span></div>
    <div class="toc-item"><span class="toc-n">Ch 4</span><span>Indexing, CDC & Structured Log Data</span></div>
    <div class="toc-item"><span class="toc-n">Ch 5</span><span>Tiered Storage & Caching Economics</span></div>
    <div class="toc-item"><span class="toc-n">Ch 6</span><span>Fast Access: Redis, Consistent Hashing & Bloom Filters</span></div>
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
<p>Most system design failures are not caused by a missing feature. They are caused by a system that cannot hold up once real traffic, real failure rates, and real attackers show up. Luc's framing starts there: slow requests, flaky uptime, tangled code, and weak security are the actual killers, and none of them show up on a feature checklist. Quality attributes are the properties that determine whether a system survives contact with production: <strong>availability</strong> (the fraction of time the system is actually reachable and answering requests), <strong>consistency</strong> (every reader sees the same data at the same moment, no matter which server responds), <strong>latency</strong> (how long a single request takes to get a response), <strong>scalability</strong> (whether the system can handle more traffic by adding resources instead of rewriting code), <strong>reliability</strong> (predictable behavior under unpredictable conditions — not the same thing as availability, which only asks "is it up"; reliability asks "does it behave correctly and consistently while it's up"), and <strong>security</strong> (the system resists and contains attackers rather than assuming they won't show up). Luc insists these be treated as first-class requirements gathered and negotiated up front, not bolted on after the "real" features are built — the verbatim thesis of this lens is that <strong>quality attributes are first-class requirements, not afterthoughts</strong>.</p>
<p>The second half of the lens is a discipline about honesty: you can't have "always up," "always consistent," and "always cheap" simultaneously. Availability competes with cost, and the mechanism is concrete: staying reachable through a data-center outage, a regional network failure, or a traffic spike means paying for redundant infrastructure you hope to never fully use — duplicate servers sitting idle as failover capacity, replicas in multiple regions, and automated failover systems standing by. That standby capacity is a real, ongoing bill; it does not come free just because you want higher uptime. Strong consistency competes with global latency for an equally concrete reason: guaranteeing every reader sees the same data means the system must have replicas confirm a write with each other — quorum confirmation or a consensus protocol — before it can be called durable, and that confirmation round-trip takes real time, more of it the farther apart the confirming replicas are physically located. Flexibility competes with simplicity too: a system built to be maximally adaptable to future unknown requirements carries more moving parts, more configuration surface, and more ways to misuse it than a system built narrowly for the problem in front of it. Every one of these is a dial, and turning one dial up turns another down — there is no configuration where all dials sit at maximum.</p>
<p>Luc separates the vocabulary into three layers so the trade-off is easier to reason about, and it helps to walk one attribute through all three rather than just listing the terms. Take <strong>availability</strong> as the attribute — the goal is "checkout should stay reachable through a regional outage." <strong>Redundancy</strong> is the pillar — the strategy for getting there is "don't depend on any single instance of anything that can fail." <strong>Running two identical checkout servers in different availability zones, so if one goes down the other keeps serving traffic</strong> is the tactic — the concrete mechanism that implements the redundancy pillar for this specific attribute. Notice the layers are genuinely distinct: the attribute names what you want, the pillar names the general strategy, and the tactic names the specific thing you build. A tactic like caching can serve a different attribute's pillar too — caching is usually a tactic under a "reduce load on the source of truth" pillar in service of latency, not availability — which is exactly why naming the attribute and pillar first matters: it disciplines which tactic is even the right candidate, instead of reaching for a familiar tactic and hoping it fits. Skipping straight to tactics without naming the attribute and pillar behind them is how teams end up with a cache that solves the wrong problem.</p>
<p>Vague targets compound the problem. Saying a system should be "highly available" or "scalable" gives an engineer nothing to design against — it is not falsifiable (falsifiable here means the same thing it does in science class: you can run a real test that could fail, not just something you nod along to) and it does not survive a design review. Luc's fix is the attribute scenario: a specific what-if statement ("if the payments region goes down, checkout must fail over within 30 seconds with no data loss") that turns an adjective into a testable requirement. Scalability itself gets the same specificity treatment — a scalable system handles more traffic by adding resources, not by rewriting code, and <strong>statelessness</strong> is what makes that horizontal add-more-boxes move possible in the first place: a stateless server remembers nothing about a user between requests, storing all session data elsewhere (a shared cache or database), so any server can handle any request without needing to know what a previous server did. Because no server holds state that only it knows about, you can add servers freely without coordinating who-knows-what between them — that's the entire mechanism behind "just add more boxes." Reliability, likewise, is reframed away from "it doesn't crash" toward something sharper: predictable behavior under unpredictable conditions. And security is reframed away from a checklist item toward an embedded assumption — secure systems are designed expecting breaches, and the design's job is to constrain the <strong>blast radius</strong> (the portion of the system an attacker can reach, read, or damage once they've broken through one layer of defense — keeping blast radius small means a breach stays contained instead of spreading), not pretend the breach won't happen.</p>
<div class="box s"><div class="box-lbl">Decision Rule</div>
<p>Before choosing a tactic, name the attribute it serves and the pillar it implements — and name what you are giving up. If you cannot state the competing attribute you are trading away (cost, latency, simplicity), you have not made a design decision, you have made a guess. This is also where Luc's broader "start simple, escalate only when complexity demands it" principle bears on the flexibility-vs-simplicity trade-off specifically: don't build the flexible, configurable version of a tactic until a real requirement forces it — a <strong>circuit breaker</strong> (a software switch that automatically stops sending requests to a failing service, preventing one slow or broken component from dragging down the whole system, named by analogy to the electrical safety device that cuts power when current runs too high) is a good tactic to reach for once you've named the reliability attribute and fault-isolation pillar it serves, but a bad one to bolt on speculatively "in case something breaks someday." When NOT to use a tactic: when you cannot yet write the attribute scenario it is supposed to satisfy — reaching for caching, sharding, or circuit breakers before the requirement is falsifiable just adds complexity in search of a problem.</p>
</div>
<div class="quote" data-author="luc">"Many systems fail not because a feature is missing, but because the system buckles under real-world pressure: slow requests, flaky uptime, tangled code, or weak security."<cite>— Luc, lucsystemdesign</cite></div>
</div>

<div class="topic">
<h2>sdcourse's Lens: The Gap Between the Map and the Shovel</h2>
<p>sdcourse's angle is not about naming attributes — it is about what it actually costs to build a system that satisfies them. The curriculum this examiner grounds itself in is a 254-lesson roadmap spanning Days 1–270, building one continuous artifact: <strong>LogStream</strong>, a complete distributed log processing system — in plain terms, a pipeline that ingests millions of small log messages from many sources and reliably routes, stores, and delivers them to the right destination in order, the same category of system that underpins production monitoring and observability at any real company. A Java/Spring Boot track runs in parallel with a Python/JavaScript track over the same material. The course is 80% coding, and the hardware bar is explicit — 16GB RAM required, 8GB minimum "but you'll suffer." None of that detail is decoration; it is sdcourse's way of insisting that quality attributes are not learned by reading about them, they are learned by hitting the failure mode they describe.</p>
<p>That insistence is aimed squarely at a specific failure sdcourse has watched repeatedly: engineers who can recite "CAP theorem" (a foundational result in distributed systems stating that when a network partition occurs, a system can preserve either consistency or availability, but not both simultaneously), "availability vs. consistency," or "circuit breaker" fluently in an interview but have never built the thing that makes those trade-offs real. sdcourse names this same gap from the interview side too: 70% of rejections come from a gap most engineers don't even know exists, and "the gap isn't skill — it's philosophy. Most candidates walk in with a generic playbook. The ones who get offers walk in with company-specific intelligence." It's the identical map-vs-shovel problem restated for a different room — knowing the vocabulary without having built the thing fails you whether the audience is production traffic or an interviewer. Knowing the vocabulary from Luc's lens is necessary but not sufficient — sdcourse's whole curriculum design exists to close the gap between the two. The predictors of who actually closes that gap are concrete and unglamorous: run the code instead of just reading it, treat the GitHub reference repo as a checkpoint rather than a shortcut to copy from, and show up in Discord. Of the three, Discord activity is presented as the single best predictor of who finishes — worth flagging as sdcourse's own claim about its cohort rather than a cited, independently-verified study; it's stated in the source material as a flat assertion, not a data-backed finding with a methodology behind it.</p>
<table>
<thead><tr><th>Signal</th><th>Finisher behavior</th><th>Lurker behavior</th></tr></thead>
<tbody><tr><td>Code execution</td><td>Runs every day's code, hits real errors, debugs them</td><td>Reads the lesson, never executes it</td></tr>
<tr><td>Reference repo</td><td>Uses it as a checkpoint to compare against</td><td>Copies from it as a shortcut</td></tr>
<tr><td>Discord activity</td><td>Active — best single predictor of completion</td><td>Absent</td></tr>
<tr><td>Hardware</td><td>16GB RAM (course-recommended)</td><td>8GB minimum — "but you'll suffer"</td></tr>
<tr><td>Timeline</td><td>270 days, treated as a reference, not a race (the schedule is designed to be stretched and resumed, not completed on a fixed deadline — falling behind and picking back up is the intended way to use it, not a failure of it)</td><td>Falls behind and drops rather than resuming</td></tr>
</tbody>
</table>
<div class="box r"><div class="box-lbl">Production Reality</div>
<p>A student who can define "availability vs. consistency" from a flashcard has not yet paid the cost that makes the definition mean anything. The course is structured around 254 lessons of hands-on output specifically because the failure mode it is designed against is passive consumption — someone who nods along to Luc's attribute/pillar/tactic framework but has never had a tactic fail on them at 2am. sdcourse's answer to "how do I actually learn quality attributes" is not more reading; it is building LogStream day by day and falling behind on purpose, because falling behind and resuming is what the 270-day timeline is built to tolerate — that 254-lesson count against a 270-day window is deliberate slack, not a loose estimate, and it's worth noting the source material doesn't spell out why the Java/Spring Boot and Python/JavaScript tracks run in parallel rather than sequentially; that design choice is left unexplained, a genuine gap rather than something this chapter is omitting.</p>
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
<p><strong>Diverge:</strong> Luc's unit of rigor is a sentence — an attribute scenario you can write down before you build anything — while sdcourse's unit of rigor is elapsed time and executed code across 270 days; one is a pre-design discipline, the other is a post-design endurance test, and a team can ace the first while still failing the second. Concretely: a team writes a precise attribute scenario — "checkout must fail over within 30 seconds with no data loss" — and everyone in the design review nods, satisfied. Then they spend three months building the failover and discover, only once they measure it under real load, that their database replication lag is actually 90 seconds. The scenario itself was correctly written; the gap wasn't in the paper discipline, it was in the building and measuring of the real system — exactly the gap sdcourse's 270-day, hands-on structure exists to force a team to hit before production does.</p>
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

CH3 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 3 of 23</div>
  <h1>Database Selection & Distributed Query Patterns</h1>
  <div class="ch-src">Sources: lucsystemdesign — Database Selection, SQL vs NoSQL · sdcourse — Distributed Query Engine and Caching Patterns</div>
  <p class="ch-sum">Luc supplies the decision framework for picking a store in the first place — stop asking "which database is best" and start asking "what is the hardest question my system asks, every day, under load." sdcourse supplies the production reality of answering that hardest question fast, at scale, on historical data, without the storage bill or the cache exploding.</p>
</div>

<div class="topic">
<h2>Luc's Lens: It's a Question Problem, Not a Schema Problem</h2>
<p>Luc's central reframe is that choosing a database feels like a schema problem — rows and columns versus documents versus key-value pairs — but it usually isn't. It's a question problem. The core decision rule: pick the database that is built for the hardest question you ask most often. No single database answers every hard question well, and that's not a flaw to engineer around — it's the reason the ecosystem has this many categories. Relational databases give ACID guarantees (Atomicity, Consistency, Isolation, Durability — the four properties that guarantee a transaction either fully completes or fully rolls back, with no half-written state left behind) plus rich SQL joins, but they scale up more naturally than they scale out — scaling up means buying a bigger, more powerful single machine, while scaling out means adding more machines and spreading the load between them, and relational databases are built around the assumption that most of the hard work happens on that one machine. Distributed SQL keeps that same SQL-plus-ACID promise — the identical transactional guarantees a single-node relational database gives you — while spreading data across nodes instead of living on one machine, and you pay for that with network latency and operational complexity: every commit now has to coordinate across a network instead of a single process, which is the direct cost of stretching the single-node promise across a cluster. Document databases store each record as a self-contained JSON-like document with no fixed schema, using embedding (nesting related data inside the same document — for example, storing a user's address inside the user record instead of in a separate address table) to cut down on joins. A key-value store is, in Luc's words, basically a distributed dictionary — no schemas, no joins, no complex queries, just fast lookups by key. In-memory databases trade RAM cost and volatility risk for extremely low latency; wide-column stores demand careful up-front modeling because, like key-value stores, you don't get relational joins for free — every access pattern has to be designed into the row-key structure before you write data, not discovered afterward with a join; time-series databases lean on append-only writes, time partitioning, compression, and downsampling; search engines are usually eventually consistent and were never meant to be your transactional source of truth; and vector databases use approximate nearest-neighbor indexes — nearest-neighbor search finds the stored item most similar to a query, the way you might find the song that sounds closest to one you hummed, and "approximate" means the algorithm skips exhaustively checking every single item and instead uses shortcuts to land very close to the true best match — which means the speed comes from approximation: you trade a small, deliberate chance of imperfect accuracy for a large gain in latency, by design, not by accident.</p>
<p>This is why Luc sees most production systems settle on a primary-plus-secondary pattern rather than a single winner: one primary database chosen for correctness, with secondary databases bolted on for access pattern — SQL for transactions, Search for retrieval, Cache for speed, Vector for semantic discovery. Concretely, that usually looks like a single write path into the primary (say, PostgreSQL) for anything that must be correct, with each secondary store receiving its copy of the data afterward — via sync or replication, not via its own independent writes — so Redis can answer fast reads, Elasticsearch can answer search queries, and a vector store like Pinecone can answer semantic-similarity queries, all without any of them being the system of record. The SQL-vs-NoSQL debate is the same question restated at a coarser grain. SQL databases enforce a defined schema and consistent relationships; NoSQL databases relax those rules to handle data that is rapidly changing, wildly varied, or simply massive. SQL scales vertically first and favors strong ACID guarantees; NoSQL scales horizontally through partitioning and replication and often trades strict consistency for availability and speed, favoring the BASE approach — Basically Available, Soft State, Eventually Consistent, where "Soft State" means the system does not guarantee that data looks the same between two reads with no write in between: values can shift as the system quietly propagates updates across nodes in the background. Eventual consistency is the concrete behavior BASE describes — the database will catch up and agree with itself eventually, it just might answer two different reads differently for a moment first. Picture a scoreboard at a stadium: the main scoreboard updates the instant a point is scored, but the smaller screens at the concession stands catch up a second or two later, so for that brief window two screens disagree — that lag, and the guarantee that it resolves, is eventual consistency. Luc's guidance is intentionally plain: choose SQL when data is structured, you need strong consistency, and queries are complex; choose NoSQL when data is flexible, you need horizontal scale, and the application evolves fast. And crucially, many systems use both — SQL for transactions and analytics, NoSQL for caching, sessions, or event data — because the primary-plus-secondary pattern and the SQL-vs-NoSQL choice are really the same underlying move at two different zoom levels. Luc's closing framing for all of this is a general rule, not a list of exceptions: none of these databases is "better" in general — each one is optimized for a specific kind of question, and struggles when pushed outside that use case, whether that's a relational database forced into wide horizontal scale or a key-value store forced into a complex multi-table query it was never built to answer.</p>
<div class="box s"><div class="box-lbl">Decision Rule</div>
<p>Before picking a store, write down the single hardest question your system asks most often under load — not the easiest one, not the one in the demo. Pick the database built for that question, then add secondary stores for the other access patterns instead of forcing one database to be good at everything. When NOT to use this rule as an excuse: "just use the database we always use" is how many systems paint themselves into a corner — reaching for a familiar default without asking the question is a decision, just an unexamined one. Pick intentionally, design for your future scale, and let your data — not trends, not habit — drive the choice.</p>
</div>
<div class="quote" data-author="luc">"Choosing a database feels like a schema problem. It usually isn't. It's a question problem."<cite>— Luc, lucsystemdesign</cite></div>
</div>

<div class="topic">
<h2>sdcourse's Lens: Answering the Hardest Question Fast, at Scale, on a Budget</h2>
<p>sdcourse's angle picks up exactly where Luc's decision rule leaves off: once you know the hardest question your system asks — for a log processing platform, that's usually "give me a sub-second answer over historical data without me paying to keep all of it hot" — the architecture has to separate how you write from how you read. The mechanism is CQRS (Command Query Responsibility Segregation): every write ("command") travels down one path, and every read ("query") travels down a completely separate path, so neither interferes with the other under load. Concretely, the write side is a high-throughput Kafka ingestion path — Kafka is a distributed message queue, a durable high-throughput pipe that accepts a continuous firehose of incoming events (log lines, clicks, transactions) and holds them until downstream systems are ready to process them — and the read side is an optimized query structure with pre-computed aggregations, so reads and writes scale independently instead of contending for the same resources. The cost of that separation is eventual consistency — the same lag Luc's BASE model describes, applied here concretely: query results might be 100–500ms behind real-time events — and the payoff is the ability to handle roughly 10x more concurrent queries than a system that reads and writes against the same live table. sdcourse is explicit that this trade only makes sense once you've named the hard question, echoing Luc's framing from the other direction: the architecture follows the query, not the other way around, and it only works because CQRS preserves the same separation-of-concerns idea Luc applies to whole databases — one path optimized for correctness (the write side), another optimized for the access pattern (the read side) — just applied inside a single store instead of across a primary and its secondaries.</p>
<p>Caching is where sdcourse gets most concrete, and most willing to name an anti-pattern outright: never implement write-through caching for high-velocity log data. Write-through caching means every time the application writes new data, it writes to both the database and the cache at the same time, so the cache is always up to date — the "through" is the write passing through the cache on its way to the database. The cost is that every single write now has to touch two systems instead of one; it's like updating both a whiteboard and a printed handout every time a fact changes — fine if facts change occasionally, exhausting if they change a thousand times a second, which is exactly the velocity of log ingestion. On high-velocity log data this overhead negates the performance benefit and creates consistency nightmares during failure scenarios: for example, a log line arrives, the database write succeeds, but a network blip interrupts the matching cache update. The cache now silently disagrees with the database — cache invalidation (removing or updating the now-stale cached value) never completed — and the next read hits the cache, returns the stale number, and the user sees wrong analytics with no error to warn them. Instead, sdcourse lays out a three-tier Redis caching scheme tuned to how log queries actually behave — a query result cache with a 5-minute TTL, an aggregation cache with a 1-hour TTL, and a hot data cache for the last 15 minutes with a 30-second TTL, where TTL (Time-To-Live) is simply how many seconds a cached entry survives before the cache automatically discards it. Because log queries exhibit strong temporal locality — the pattern where most queries ask about recent data rather than old data, so the last 15 minutes gets far more hits than data from three months ago — cache hit ratios above 95% are achievable with this tiering. A query first checks the 5-minute result cache; on a miss it checks the 1-hour aggregation cache; on another miss it checks the 30-second hot data cache; only a miss at all three tiers reaches the database, so each tier short-circuits the more expensive layer behind it. Pre-computed aggregations are what make the 1-hour tier cheap to serve: the system runs the math — say, counting all error logs from the last hour — on a schedule as new data arrives, and stores the answer, so a query that asks for that count reads the stored number instead of scanning millions of rows in real time, the way a bakery tallies up the day's sales once an hour rather than re-counting every receipt whenever the manager asks. On the storage side, sdcourse names the point at which the naive approach collapses: traditional log tables become unusable beyond 10 million records without a proper indexing strategy, which is the concrete, numeric version of Luc's abstract warning that no single database answers every hard question well.</p>
<table>
<thead><tr><th>Layer</th><th>Value</th><th>Why it matters</th></tr></thead>
<tbody><tr><td>CQRS query capacity gain</td><td>~10x concurrent queries</td><td>Read/write separation lets each side scale independently</td></tr>
<tr><td>CQRS staleness window</td><td>100–500ms</td><td>The eventual-consistency cost of decoupling reads from writes</td></tr>
<tr><td>Query result cache TTL</td><td>5 minutes</td><td>Top tier of the three-tier Redis scheme</td></tr>
<tr><td>Aggregation cache TTL</td><td>1 hour</td><td>Pre-computed rollups change slowly, so they can live longer</td></tr>
<tr><td>Hot data cache TTL</td><td>30 seconds, last 15 min</td><td>Shortest TTL, covers the highest-churn recent window</td></tr>
<tr><td>Achievable cache hit ratio</td><td>&gt;95%</td><td>Driven by temporal locality — most log queries hit recent data</td></tr>
<tr><td>Naive log table failure point</td><td>&gt;10M records</td><td>Traditional tables become unusable without proper indexing beyond this</td></tr>
</tbody>
</table>
<div class="box r"><div class="box-lbl">Production Reality</div>
<p>The anti-pattern sdcourse warns against isn't a style preference — it's a failure mode with a specific shape: a partial failure between the write path and the cache layer leaves you with a cache that silently disagrees with the source of truth and no clean way to reconcile it under load. The three-tier TTL scheme sidesteps this entirely by never trying to keep the cache perfectly in sync with writes; it accepts staleness in fixed, bounded windows (30s / 5min / 1hr) instead, which is a deliberate design choice, not an oversight — the same trade-off Luc's BASE model makes at the whole-database level, applied here at the cache layer.</p>
</div>
<div class="quote" data-author="sdcourse">"Anti-Pattern Warning: Never implement write-through caching for high-velocity log data. The cache invalidation overhead will negate performance benefits and create consistency nightmares during failure scenarios."<cite>— sdcourse</cite></div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <rect x="40" y="40" width="260" height="150" rx="12" fill="#eff6ff"/>
    <rect x="400" y="40" width="260" height="150" rx="12" fill="#fff7ed"/>
  </g>
  <text x="170" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">LUC: Name the Hardest Question</text>
  <text x="170" y="75" text-anchor="middle" font-size="13" fill="#1e3a8a">Not "which DB is best" —</text>
  <text x="170" y="105" text-anchor="middle" font-size="13" fill="#1e3a8a">"what question, under load,</text>
  <text x="170" y="135" text-anchor="middle" font-size="13" fill="#1e3a8a">every day?" Primary for</text>
  <text x="170" y="160" text-anchor="middle" font-size="13" fill="#1e3a8a">correctness, secondaries for access</text>
  <text x="530" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#7c2d12">SDCOURSE: Answer It in &lt;1s</text>
  <text x="530" y="75" text-anchor="middle" font-size="13" fill="#7c2d12">CQRS splits read/write —</text>
  <text x="530" y="105" text-anchor="middle" font-size="13" fill="#7c2d12">10x query capacity, 100-500ms lag</text>
  <text x="530" y="135" text-anchor="middle" font-size="13" fill="#7c2d12">3-tier cache, never write-through —</text>
  <text x="530" y="160" text-anchor="middle" font-size="13" fill="#7c2d12">95%+ hit ratio</text>
</svg>
</div>
<div class="sketch-cap">Luc tells you which store answers your hardest question; sdcourse shows what it takes to keep answering it in under a second once the data no longer fits in one machine's memory. (The primary-plus-secondary pattern from Luc's Lens, made physical: one primary — e.g. PostgreSQL — is the only system anything writes to for correctness; Redis, Elasticsearch, and a vector store like Pinecone each receive their copy afterward via sync/replication and serve their own read pattern, never taking writes of their own.)</div>

<div class="box xr"><div class="box-lbl">Where They Converge / Diverge</div>
<p><strong>Converge:</strong> Both reject a single default as an answer — Luc insists "just use the database we always use" is how systems paint themselves into a corner, and sdcourse insists the naive single-table, write-through-cache approach becomes unusable past a specific, named scale (10M records, or any high-velocity write path); both push the reader toward an intentional, workload-driven choice over a habitual one.</p>
<p><strong>Diverge:</strong> Luc's unit of analysis is the store itself — pick the right category of database for the hardest question, primary plus secondaries, SQL vs NoSQL by data shape and consistency need — while sdcourse's unit of analysis is the query path around whichever store you picked — CQRS to decouple read and write scaling, a tiered cache with named TTLs to keep 95%+ of queries out of the database entirely. A team can correctly apply Luc's framework and choose the right database category, and still get paged because nobody built the CQRS split or the tiered cache that keeps that correct database answering in under a second at 10x the load. Concretely: a team building a log analytics product reads Luc's rule, names their hardest question — sub-second search over 50 million log lines — and correctly picks Elasticsearch as the primary store. Six months later, query latency spikes to 8 seconds at peak load and the team gets paged. The database choice was never the problem; they never built the CQRS split or the three-tier cache, so every query hit Elasticsearch directly, with no pre-computed aggregations absorbing the load. Luc's test: passed. sdcourse's test: failed.</p>
</div>

<div class="recall">
<div class="recall-head">Active Recall</div>
<div class="q"><span class="q-n">Q1.</span> Per Luc's decision rule, what single question should you ask before picking a database, and why does "just use the database we always use" count as a decision rather than a neutral default?</div>
<div class="q"><span class="q-n">Q2.</span> Per sdcourse, why is write-through caching an anti-pattern specifically for high-velocity log data, and what three TTL tiers does the alternative Redis scheme use instead?</div>
<div class="q"><span class="q-n">Q3.</span> Luc frames database selection as picking the store built for your hardest recurring question; sdcourse frames it as keeping that store fast once real query volume arrives. Using CQRS and the 10M-record indexing cliff as evidence, explain how a team could pass Luc's test but still fail sdcourse's.</div>
</div>
</div>
"""

CH4 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 4 of 23</div>
  <h1>Indexing, CDC & Structured Log Data</h1>
  <div class="ch-src">Sources: lucsystemdesign — Database Indexing, Change Data Capture (CDC) · sdcourse — Log Format Normalization and Serialization, Faceted Search and Multi-Dimensional Filtering</div>
  <p class="ch-sum">Luc's angle is the OLTP database deciding what to pre-organize so future reads are cheap — an index, or a change stream tapped off the transaction log. sdcourse's angle is the log pipeline doing the identical trick on a different substrate — normalizing formats and pre-building inverted indexes so a billion-log search doesn't turn into a full scan. Same move, two systems.</p>
</div>

<div class="topic">
<h2>Luc's Lens: Pre-Paying for Reads, Whether the Data Is at Rest or in Motion</h2>
<p>Luc's starting point is that indexing is a reflex, not a decision, and reflexes are where trouble hides. "Slow queries have a reflex fix: add an index. It works often enough that teams keep doing it; until write latency creeps up, storage balloons, and the query planner starts making strange choices." The reflex works often enough to become habit, which is exactly why it needs correcting: every INSERT, UPDATE, and DELETE has to update every index on that table too, so each index is a standing write tax, paid on every future write, in exchange for cheaper reads today. B-trees are the safe default for most OLTP access patterns — equality filters, range filters, ordered reads — but "safe default" is not the same as "free." Luc is also blunt that an index existing doesn't mean it gets used: the query planner only takes the index path when its cost model estimates that path is cheaper than a table scan, and if the table's statistics are stale, that estimate can simply be wrong, silently. Knowing when to remove an index matters as much as knowing when to add one — rarely-used indexes, duplicate indexes, low-selectivity predicates, write-heavy tables, and columns wrapped in functions (which block index use entirely) are all candidates for deletion, not just addition.</p>
<p>Change Data Capture is Luc's second half of the same move, applied to a stream instead of a lookup. CDC taps into the transaction log the database already keeps for durability and crash recovery, and turns every insert, update, and delete into an event other systems can react to within seconds. Of the three capture methods — timestamp polling, database triggers, and log-based capture — log-based capture is "the modern standard" because it's low-latency, minimally invasive to the source database, and preserves exact write order, where polling silently misses hard deletes and triggers add write-path overhead. But CDC is not a free real-time button: it demands idempotent consumers (because log-based delivery is generally at-least-once) and real observability into consumer lag, offsets, and dead-letter queues, or a stalled consumer becomes an invisible correctness bug. CDC also captures the fact that a row changed, not why — it is not an audit trail by default, and treating it as one is a category error. Luc's guidance: use CDC when the dataset is large but the daily delta is small and freshness genuinely matters — live dashboards, personalization, fraud detection — and skip it for append-only feeds, small tolerant-SLA datasets, or strict historical auditing, where the machinery costs more than the freshness is worth.</p>
<div class="box s"><div class="box-lbl">Decision Rule</div>
<p>Before adding an index, name the exact predicate it serves and verify with a real query plan that the optimizer actually chooses it — don't index on reflex, and periodically audit for indexes that are rarely used, duplicated, low-selectivity, or sitting on a write-heavy table, because those are pure write tax with no read payoff. Before adopting CDC, name the fraction of the dataset that changes daily and whether fresh data changes a real decision — if the delta is tiny and freshness matters (fraud, personalization, live dashboards), tap the transaction log; if the data is append-only, small, or the requirement is a durable audit trail, CDC is the wrong tool wearing a real-time costume. When NOT to use either: don't index "just in case," and don't wire up CDC because streaming sounds more modern than batch — "start small, capture what truly benefits from real-time data, prove the value, and expand gradually."</p>
</div>
<div class="quote" data-author="luc">"Indexes are best understood as a trade: you spend extra work on writes so reads can skip unnecessary work. Once you see that trade clearly, index tuning stops feeling like superstition and starts feeling like engineering."<cite>— Luc, lucsystemdesign</cite></div>
</div>

<div class="topic">
<h2>sdcourse's Lens: Pre-Paying for Reads in the Log Pipeline Itself</h2>
<p>sdcourse's log format normalization problem is the pipeline-side mirror of Luc's indexing trade-off: instead of choosing between "index everything" and "index nothing," the choice is between "force every producer onto one format" (politically impossible, technically disruptive) and "build a custom converter for every producer-consumer pair," which is N×M complexity that explodes as sources multiply. The fix is the same shape as an index — do the structuring work once, up front, so every future read is cheap. Converting every incoming format to a canonical intermediate representation first turns N×M direct converters into O(N) — one parser and one serializer per format — and sdcourse names this explicitly as decoupling: "Format normalization is a form of decoupling. Just as message queues decouple producers from consumers in time, format normalization decouples them in representation. This decoupling enables independent evolution — your analytics team can switch from JSON to Avro without coordinating with every upstream producer." Naive conversion handles about 5,000 logs/second per core; layering in object pooling, buffer management, batch processing, parallel conversion, and zero-copy passthrough pushes that past 50,000/second, at which point the bottleneck stops being CPU and becomes memory bandwidth. Production systems avoid guessing at format by trusting Content-Type headers when present, falling back to magic bytes for binary formats, and using heuristics only for text-based formats as a last resort.</p>
<p>Faceted search is the read-side payoff of that up-front structuring, and it is functionally an index built for a different kind of query: "Traditional search requires knowing exactly what you're looking for. Faceted search flips this — it shows you what's available to explore." The mechanism is an inverted index mapping each facet value to matching document IDs, which costs 30-40% additional storage but converts an O(n) full scan into an O(k) lookup — for 1 billion logs, a 10-minute scan becomes a 50ms index lookup. That's Luc's write-tax-for-read-speed trade again, just quantified on the log side: "Inverted indexes map each facet value to document IDs... this transforms a 10-minute scan into a 50ms index lookup. The cost: write amplification. Each log ingestion updates multiple indexes — one per facet." sdcourse also names a concrete anti-pattern — caching final search results per user query, rather than caching aggregations at the dimension level (counts per facet) — and a routing strategy: filter-first when a filter is selective (under 5% of docs), aggregate-first when it's broad (over 50% of docs). At the storage layer, representing 1 million matching document IDs as a sorted integer array costs 4MB, while a compressed bitmap does the same job in 50KB with O(1) intersection. Splunk caps facets at 10,000 unique values per day to keep cardinality bounded; Netflix's cardinality-aware query planning cut search P99 latency from 8 seconds to 400ms.</p>
<table>
<thead><tr><th>Metric</th><th>Value</th><th>Why it matters</th></tr></thead>
<tbody><tr><td>Direct converter complexity</td><td>N×M pairs</td><td>What canonical-format normalization replaces</td></tr>
<tr><td>Canonical-format complexity</td><td>O(N)</td><td>One parser + one serializer per format instead</td></tr>
<tr><td>Naive conversion throughput</td><td>~5,000 logs/sec/core</td><td>Baseline before optimization</td></tr>
<tr><td>Optimized conversion throughput</td><td>50,000+ logs/sec</td><td>Pooling, batching, parallelism, zero-copy passthrough</td></tr>
<tr><td>Inverted index storage overhead</td><td>30-40% extra</td><td>Cost of turning O(n) scans into O(k) lookups</td></tr>
<tr><td>1B-log facet scan, unindexed vs. indexed</td><td>10 min → 50ms</td><td>The concrete payoff of the storage overhead above</td></tr>
<tr><td>1M doc IDs: sorted array vs. compressed bitmap</td><td>4MB vs. 50KB</td><td>Bitmap gives O(1) intersection at a fraction of the size</td></tr>
<tr><td>Netflix search P99 latency</td><td>8s → 400ms</td><td>Cardinality-aware query planning in production</td></tr>
</tbody>
</table>
<div class="box r"><div class="box-lbl">Production Reality</div>
<p>The anti-pattern here has the same shape as Luc's stale-statistics warning: caching final results per user query looks like it should help, but log queries have too much combinatorial variety in their filter combinations for full-result caching to get meaningful hit rates, so the cache mostly misses while still paying its maintenance cost. Caching at the dimension level — counts per facet — reuses across the many different filter combinations users actually issue, the same way a well-chosen index serves many different WHERE clauses instead of one. And write amplification is not a side effect to tolerate quietly: every log ingestion updates one inverted-index entry per facet, so a facet schema chosen carelessly multiplies write cost across every single ingested log, forever, exactly like an over-indexed OLTP table.</p>
</div>
<div class="quote" data-author="sdcourse">"When your system generates millions of logs per hour, finding relevant information becomes like searching for a needle in a haystack. Traditional search requires knowing exactly what you're looking for. Faceted search flips this - it shows you what's available to explore."<cite>— sdcourse</cite></div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <rect x="40" y="40" width="260" height="150" rx="12" fill="#eff6ff"/>
    <rect x="400" y="40" width="260" height="150" rx="12" fill="#fff7ed"/>
  </g>
  <text x="170" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">LUC: Structure the Row Store</text>
  <text x="170" y="75" text-anchor="middle" font-size="13" fill="#1e3a8a">Index = write tax for read speed.</text>
  <text x="170" y="105" text-anchor="middle" font-size="13" fill="#1e3a8a">CDC taps the transaction log —</text>
  <text x="170" y="135" text-anchor="middle" font-size="13" fill="#1e3a8a">small delta, real freshness need,</text>
  <text x="170" y="160" text-anchor="middle" font-size="13" fill="#1e3a8a">idempotent consumers required</text>
  <text x="530" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#7c2d12">SDCOURSE: Structure the Log Stream</text>
  <text x="530" y="75" text-anchor="middle" font-size="13" fill="#7c2d12">Canonical format: O(N) not N×M.</text>
  <text x="530" y="105" text-anchor="middle" font-size="13" fill="#7c2d12">Inverted index: 30-40% storage tax,</text>
  <text x="530" y="135" text-anchor="middle" font-size="13" fill="#7c2d12">10min scan becomes 50ms lookup</text>
  <text x="530" y="160" text-anchor="middle" font-size="13" fill="#7c2d12">— same trade, different substrate</text>
</svg>
</div>
<div class="sketch-cap">Luc's index and sdcourse's inverted index are the same bet made twice: pay a write cost now so a future read doesn't have to scan everything.</div>

<div class="box xr"><div class="box-lbl">Where They Converge / Diverge</div>
<p><strong>Converge:</strong> Both are describing the identical trade — do structuring work up front, on every write, so a specific future read pattern becomes cheap instead of a full scan; Luc's B-tree index and sdcourse's inverted index both cost storage and write amplification, and both only pay off if the read pattern they were built for actually happens.</p>
<p><strong>Diverge:</strong> Luc's structuring targets a single OLTP row store answering point and range queries, and CDC targets exporting that store's changes outward as a stream for other systems to consume; sdcourse's structuring targets a distributed log pipeline ingesting from many heterogeneous producers and answering exploratory, multi-dimensional facet queries over billions of events. Luc worries about the optimizer choosing not to use an index because statistics are stale; sdcourse worries about write amplification across many facets at ingestion-time scale and about caching at the wrong granularity. A team can get Luc's OLTP indexing exactly right and still watch their log-search product time out, because faceted search over a billion-event stream is a different structuring problem with its own index (inverted, bitmap-compressed) and its own anti-pattern (per-query result caching instead of per-dimension aggregation caching).</p>
</div>

<div class="recall">
<div class="recall-head">Active Recall</div>
<div class="q"><span class="q-n">Q1.</span> Per Luc, why can an index exist on a table and still never be used by the query planner, and what two conditions does Luc give for when CDC is worth adopting versus when it's the wrong tool?</div>
<div class="q"><span class="q-n">Q2.</span> Per sdcourse, why does canonical-format normalization reduce N×M converters to O(N), and what specific anti-pattern turns faceted-search caching into a low-hit-rate cost center?</div>
<div class="q"><span class="q-n">Q3.</span> Luc's index and CDC operate on a single OLTP database; sdcourse's format normalization and inverted facet index operate on a distributed log pipeline. Using the write-amplification concept from both lenses, explain why "structure data now so retrieval is fast later" produces a different failure mode in each system.</div>
</div>
</div>
"""

CH5 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 5 of 23</div>
  <h1>Tiered Storage & Caching Economics</h1>
  <div class="ch-src">Sources: lucsystemdesign — Database Caching Strategies, Connection Pooling · sdcourse — Distributed Log Storage and Tiered Architecture</div>
  <p class="ch-sum">Luc's angle is the decision framework: which caching strategy, and how many pooled connections, does this workload actually need. sdcourse's angle is that same question scaled to a distributed log pipeline, where the answer becomes a physical hot/warm/cold tier assignment for every byte you store. Same underlying question — where does this data live, and at what cost — asked at two different altitudes.</p>
</div>

<div class="topic">
<h2>Luc's Lens: Deciding What Lives Close and What Waits</h2>
<p>Luc treats caching as a correctness decision wearing a performance-optimization costume. "Caching is not just a performance optimization. It is part of your system's correctness model." Done poorly, it introduces stale reads, hidden consistency bugs, and memory waste that only shows up in production — the bug doesn't announce itself at cache-miss time, it waits for an eviction, a deployment, or an incident to expose it. Luc lays out five named strategies, each trading consistency for speed differently: Cache-Aside (application checks cache first, falls through to DB on miss, then populates the cache itself), Write-Through (cache and database updated synchronously on every write — strong consistency, higher write latency, possible cache pollution), Write-Behind/Write-Back (cache updated first, database flushed later in the background — fast writes and high throughput, but data loss risk if the cache node crashes before the flush), Read-Through (the cache itself owns the miss-fetch from the DB, giving cleaner application code at the cost of a cold-start penalty), and Write-Around (writes bypass the cache entirely and go straight to the database, with data entering cache only on a later read). None of these is universally correct; the choice has to be driven by read-vs-write ratio, consistency requirements, and how much operational complexity the team can actually own.</p>
<p>Connection pooling is Luc's second half of the same "what stays warm and ready vs. what gets fetched cold" argument, just applied to database connections instead of query results. Every fresh connection to a database pays a TCP handshake, TLS negotiation, and authentication round trip before a single query can run — without pooling, every request starts cold, and that repeated cold-start tax shows up as extra latency, server strain, connection churn, and eventual throughput collapse under load. A pool manages the creation, checkout, release, validation, and cleanup of a standing set of connections so that cost is paid once and amortized, not paid per request. But sizing the pool is its own decision problem, structurally identical to picking a caching strategy: oversized pools can quietly throttle the database's own capacity, while undersized pools leave threads waiting on a connection instead of serving users — and a healthy pool can even mask a deeper problem, since queries that are actually maxing out CPU or I/O still create bottlenecks no amount of pooling fixes. The target isn't "as many connections as possible," it's exactly enough to keep the system steady at peak efficiency.</p>
<div class="box s"><div class="box-lbl">Decision Rule</div>
<p>Pick a caching strategy by naming the read/write ratio and the consistency budget first, not by reaching for whichever one is easiest to bolt on: strong consistency and tolerable write latency point to Write-Through; high write throughput with an accepted small data-loss window points to Write-Behind; simple application code with an accepted cold-start cost points to Read-Through; a write-heavy path that's rarely re-read points to Write-Around. Size a connection pool the same way — against measured peak concurrency, not intuition — and treat "the pool is healthy" as no proof that the underlying queries are cheap; check CPU and I/O separately. In both cases: "Match your caching strategy to your access patterns, failure tolerance, and consistency needs; and your system will scale calmly instead of nervously."</p>
</div>
<div class="quote" data-author="luc">"Caching is not just a performance optimization. It is part of your system's correctness model."<cite>— Luc, lucsystemdesign</cite></div>
</div>

<div class="topic">
<h2>sdcourse's Lens: Hot, Warm, Cold — Caching's Decision Framework at Storage Scale</h2>
<p>sdcourse's tiered architecture is Luc's caching decision applied to an entire storage system rather than a single lookup path. "Most engineers think log storage is solved by 'just use Elasticsearch' or 'dump everything to S3,' but the real complexity emerges when you need sub-second query performance on historical data while maintaining cost-effective storage for compliance retention." The resolution is a three-tier storage design: Hot (Redis, sub-millisecond, last 24h) → Warm (PostgreSQL, sub-second, 30 days) → Cold (file-based, cost-optimized, compliance retention). That's a physical, per-byte version of Luc's cache-strategy choice — Hot tier behaves like an aggressively warmed cache tuned for latency, Cold tier behaves like Luc's Write-Around: data that isn't worth keeping close because it's rarely re-read, only retained because something (compliance) requires it to exist somewhere. sdcourse is explicit that age alone is the wrong axis to tier on: "The key insight: storage tier decisions should be driven by business value, not just age." A log that's two years old but tied to an active compliance investigation may need to move back toward the warm tier regardless of its timestamp — the tiering logic has to be adaptive to value, not a fixed TTL clock.</p>
<p>That adaptivity has a measured payoff: adaptive rotation reduces storage costs by 60-70% compared to naive time-based rotation, because naive rotation keeps paying hot-tier prices for data nobody is querying anymore. The mirror-image failure mode is a caching problem in the Luc sense, not a storage problem: cache hit ratio below 85% indicates either wrong data being cached or TTL too aggressive — which is precisely Luc's warning that the wrong caching strategy quietly accumulates risk rather than announcing itself. And sdcourse flags a specific operational trap unique to this domain: the monitoring system watching the tiered storage pipeline can itself become the largest log producer. "The monitoring system often generates more log data than the applications it's monitoring. This recursive complexity requires careful design to avoid monitoring loops and resource exhaustion." A tiering and caching layer that doesn't account for its own observability traffic can end up filling its hot tier with metrics about the hot tier.</p>
<table>
<thead><tr><th>Metric</th><th>Value</th><th>Why it matters</th></tr></thead>
<tbody><tr><td>Hot tier</td><td>Redis, sub-millisecond, last 24h</td><td>Aggressively warmed, latency-optimized — Luc's Read-/Write-Through territory</td></tr>
<tr><td>Warm tier</td><td>PostgreSQL, sub-second, 30 days</td><td>Middle ground: still queryable, not free</td></tr>
<tr><td>Cold tier</td><td>File-based, cost-optimized, compliance retention</td><td>Rarely re-read, kept because required — Luc's Write-Around analog</td></tr>
<tr><td>Adaptive vs. naive time-based rotation</td><td>60-70% storage cost reduction</td><td>Payoff of tiering by business value, not just age</td></tr>
<tr><td>Cache hit ratio floor</td><td>Below 85%</td><td>Signals wrong data cached or TTL too aggressive</td></tr>
</tbody>
</table>
<div class="box r"><div class="box-lbl">Production Reality</div>
<p>The same wrong-strategy risk Luc describes for application caches shows up here as a hit-ratio number you can actually watch: a cache hit ratio dropping below 85% is the tiered-storage equivalent of Luc's "quietly accumulates risk until a cache eviction, deployment, or incident exposes it" — except here it's directly measurable, so there's no excuse for it to stay hidden. The monitoring-loop trap is the sharper production reality: a tiering system has to budget hot-tier capacity for its own telemetry, or the system meant to keep storage costs down becomes the thing inflating them, consuming the same sub-millisecond Redis capacity it was supposed to be protecting for real query traffic.</p>
</div>
<div class="quote" data-author="sdcourse">"The key insight: storage tier decisions should be driven by business value, not just age."<cite>— sdcourse</cite></div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <rect x="40" y="40" width="260" height="150" rx="12" fill="#eff6ff"/>
    <rect x="400" y="40" width="260" height="150" rx="12" fill="#fff7ed"/>
  </g>
  <text x="170" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">LUC: Pick the Strategy</text>
  <text x="170" y="75" text-anchor="middle" font-size="13" fill="#1e3a8a">5 caching strategies, sized by</text>
  <text x="170" y="105" text-anchor="middle" font-size="13" fill="#1e3a8a">read/write ratio + consistency need.</text>
  <text x="170" y="135" text-anchor="middle" font-size="13" fill="#1e3a8a">Pool connections to just enough,</text>
  <text x="170" y="160" text-anchor="middle" font-size="13" fill="#1e3a8a">not as many as possible</text>
  <text x="530" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#7c2d12">SDCOURSE: Assign the Tier</text>
  <text x="530" y="75" text-anchor="middle" font-size="13" fill="#7c2d12">Hot/Warm/Cold by business value,</text>
  <text x="530" y="105" text-anchor="middle" font-size="13" fill="#7c2d12">not age — 60-70% cost cut vs. naive.</text>
  <text x="530" y="135" text-anchor="middle" font-size="13" fill="#7c2d12">Hit ratio below 85% = wrong data</text>
  <text x="530" y="160" text-anchor="middle" font-size="13" fill="#7c2d12">cached or TTL too aggressive</text>
</svg>
</div>
<div class="sketch-cap">Luc's caching-strategy choice and sdcourse's hot/warm/cold tier are the same "what stays close, what waits" decision — one made per query, one made per byte at storage scale.</div>

<div class="box xr"><div class="box-lbl">Where They Converge / Diverge</div>
<p><strong>Converge:</strong> Both frameworks reject a single default: Luc insists the caching strategy must match access pattern, consistency needs, and failure tolerance rather than being picked by habit, and sdcourse insists tier placement must be driven by business value rather than by age alone — both are "decide deliberately or the wrong choice will quietly cost you" arguments, and both name a measurable early-warning signal (Luc's masked CPU/I/O bottleneck behind a "healthy" pool; sdcourse's sub-85% hit ratio) for when the choice has already gone wrong.</p>
<p><strong>Diverge:</strong> Luc's unit of decision is a single cache or a single connection pool serving one service's access pattern; sdcourse's unit of decision is an entire storage system's worth of data, physically routed across three distinct storage engines (Redis, PostgreSQL, file-based) with different durability and compliance guarantees. Luc's failure mode is stale reads or a pool that silently throttles the database; sdcourse's failure mode is a monitoring system that recursively floods its own hot tier with telemetry about itself — a problem that has no equivalent at the single-cache scale Luc is describing, because it only emerges once you're operating a whole tiered pipeline with its own observability surface.</p>
</div>

<div class="recall">
<div class="recall-head">Active Recall</div>
<div class="q"><span class="q-n">Q1.</span> Per Luc, name the five caching strategies and the one factor he says should never be the deciding one for connection pool sizing (i.e., what is the actual sizing target instead of "as many connections as possible")?</div>
<div class="q"><span class="q-n">Q2.</span> Per sdcourse, what are the three storage tiers and their latency/retention characteristics, and what specific hit-ratio number signals that a tier's caching is misconfigured?</div>
<div class="q"><span class="q-n">Q3.</span> Luc's caching-strategy decision operates on a single cache serving one access pattern; sdcourse's hot/warm/cold tiering operates on a whole storage system with its own observability traffic. Explain why the "monitoring system generates more log data than the applications it's monitoring" failure has no direct equivalent at Luc's single-cache scale.</div>
</div>
</div>
"""

CH6 = """
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter 6 of 23</div>
  <h1>Fast Access: Redis, Consistent Hashing &amp; Bloom Filters</h1>
  <div class="ch-src">Sources: lucsystemdesign — Redis, Consistent Hashing, Bloom Filters · sdcourse — Bloom Filters in Log Processing, Distributed Query Engine and Caching Patterns</div>
  <p class="ch-sum">Both authors independently reach for the same trick: before you pay full price for an answer, ask a cheap, approximate gatekeeper first. Luc names the general-purpose toolkit — an in-RAM store, a stable way to spread keys across it, and a probabilistic filter that says "definitely not" for free. sdcourse shows what happens when that toolkit is wired into one real, high-volume pipeline: exact latency numbers, exact hit-ratio floors, exact TTLs.</p>
</div>

<div class="topic">
<h2>Luc's Lens: RAM, a Ring, and a Bit Array — Three Ways to Skip Work</h2>
<p>Luc's Redis section starts from a correction, not a feature list: Redis is not a general-purpose database replacement, it's a performance layer that solves specific problems extremely well. Everything is stored in RAM as key-value pairs, but the values support richer structures than a plain cache would need — Strings, Hashes, Lists, Sets, and Sorted Sets. A structural detail does a lot of Luc's explanatory work: Redis uses a single-threaded event loop, meaning one command executes at a time, which avoids locking and keeps operations atomic without the coordination overhead a multi-threaded store would need. But the same section is just as clear about when Redis is the wrong tool: don't reach for it when the dataset is large and cold (RAM is expensive), when you need complex queries, when you need strong durability (financial transactions, medical records), or when the workload is stateless and simple enough that a cache buys nothing. "The problem often isn't the database itself. It's that you're asking it to answer the same questions, over and over, thousands of times a second" — Redis exists to absorb that repetition, not to replace the database being asked.</p>
<p>Consistent hashing is Luc's answer to a different question: once you've decided to spread keys across multiple Redis (or cache, or shard) nodes, how do you keep that mapping stable as nodes come and go? Naive hashing — shard = hash(key) % N — looks simple until N changes: the moment a node is added or removed, the entire mapping shifts with it, causing a full cache reset. Consistent hashing fixes this by mapping both keys and servers into the same hash space, a ring, and walking clockwise from a key's position until you hit the first server. When a node is added or removed, only the keys between the new position and the previous node need to move; everything else stays exactly where it was. In practice that means when a cluster grows, only about 1/N of the keys move, so caches stay warm and rebalancing is light — and multiple virtual nodes per physical server spread that load more evenly across the ring. Bloom filters close out Luc's trio by attacking a different kind of waste entirely: most systems spend more time proving what isn't there than what is — every cache miss, every 404, every "not found" query costs real CPU, I/O, and bandwidth. A Bloom filter answers "could this exist?" using a bit array and multiple hash functions, without storing the item itself. It never gives false negatives — if you inserted it, it will always return "maybe" — but it can give false positives; if any queried bit is 0 the item definitely doesn't exist, and if all are 1 it might exist. The false positive rate is tunable by the number of hash functions, and Luc is explicit about where not to use one: exact answers (billing, access control, authentication), frequent deletions, or unpredictably growing data.</p>
<div class="box s"><div class="box-lbl">Decision Rule</div>
<p>Reach for Redis when the same question is being asked repeatedly and RAM cost is justified by request volume — not as a default data layer. Once you're sharding that cache (or any keyed store) across multiple nodes, use consistent hashing instead of modulo hashing the moment node count is expected to change, because consistent hashing trades perfect balance for predictable, bounded churn: only ~1/N of keys move per topology change, not all of them. Put a Bloom filter in front of any expensive "does this exist?" check with a high miss rate — it can only ever save you a lookup (definite no) or cost you one wasted check (false positive maybe), never return a wrong "yes" for something absent. None of the three replace the system of record; all three exist to reduce how often that system of record gets asked.</p>
</div>
<div class="quote" data-author="luc">"Redis is best understood as a performance multiplier, not a database replacement. Used correctly, Redis turns slow paths into fast ones and fragile systems into responsive ones. Used blindly, it becomes an expensive, leaky abstraction."<cite>— Luc, lucsystemdesign</cite></div>
</div>

<div class="topic">
<h2>sdcourse's Lens: The Same Gatekeeper, Wired Into a Log Pipeline</h2>
<p>sdcourse's Bloom filter section is Luc's "definitely not / probably present" idea with the numbers attached. In log processing, a Bloom filter answers "definitely not present" or "probably present" — zero false negatives, tunable false positives typically in the 1-5% range — and the payoff is concrete: without a Bloom filter, an existence query costs 50-200ms; with one, it costs 0.1-1ms, alongside a roughly 95% memory reduction compared to hash-based lookups. sdcourse treats this as more than a speed trick: "Bloom filters transform expensive 'does this exist?' questions into instant responses with minimal memory overhead. They're not just performance optimizations - they're architectural game-changers that enable entirely new query patterns in distributed systems." The operational detail that separates this from Luc's general description is scope discipline — different log types (errors, access logs, security events) each maintain their own separate Bloom filter, rather than one shared filter across categories, because the acceptable false-positive cost differs by log type and mixing them would blur that tuning. The asymmetric payoff is the same logic Luc describes, restated for a pipeline: "if bloom filter says 'error might exist,' you can check the actual storage. But if it says 'error definitely doesn't exist,' you save an expensive lookup entirely."</p>
<p>The fast-access half of sdcourse's caching section is where consistent hashing's underlying goal — spread load across nodes without a full reshuffle on every topology change — shows up as a concrete Redis deployment rather than an abstract ring. Rather than one flat TTL for everything, the layer is split by how fast each kind of result goes stale: query results sit for 5 minutes, rolled-up aggregations get a full hour since they drift slowly, and the most recent 15 minutes of hot data is refreshed every 30 seconds because that window churns the fastest. Because log queries exhibit strong temporal locality, cache hit ratios above 95% are achievable with this tiering — the same "ask the fast layer first" instinct behind both Redis and Bloom filters, just measured as a hit-ratio percentage instead of a latency number. sdcourse is equally blunt about a failure mode unique to this speed and scale: synchronously updating the cache on every write collapses under high-velocity log ingestion, since the invalidation work piles up on the hot path and turns any partial failure into a consistency mess rather than a clean retry — a warning that rhymes with Luc's own list of when not to reach for Redis (strong durability needs, complex queries) even though the two lists don't overlap term-for-term.</p>
<table>
<thead><tr><th>Mechanism</th><th>Value</th><th>Why it matters</th></tr></thead>
<tbody><tr><td>Bloom filter query time without filter</td><td>50-200ms</td><td>Cost of a raw existence check against storage</td></tr>
<tr><td>Bloom filter query time with filter</td><td>0.1-1ms</td><td>Sub-millisecond target once the filter screens the request</td></tr>
<tr><td>Bloom filter memory reduction</td><td>~95% vs. hash-based lookups</td><td>Bit array is far cheaper than storing full keys</td></tr>
<tr><td>Bloom filter false positive rate</td><td>Configurable, typically 1-5%</td><td>Tunable cost of the "maybe" answer</td></tr>
<tr><td>Query result cache TTL</td><td>5 minutes</td><td>Top tier of the three-tier Redis scheme</td></tr>
<tr><td>Hot data cache TTL</td><td>30 seconds, last 15 min</td><td>Shortest TTL, covers the highest-churn recent window</td></tr>
<tr><td>Achievable cache hit ratio</td><td>&gt;95%</td><td>Driven by temporal locality — most log queries hit recent data</td></tr>
</tbody>
</table>
<div class="box r"><div class="box-lbl">Production Reality</div>
<p>Separate Bloom filters per log type is the detail a general description of the data structure would never surface: it exists because a single shared filter would force every log category into the same false-positive tolerance, when in practice a security-event filter and an access-log filter can justify very different tuning. And the write-through anti-pattern is what happens when a team applies Luc's Redis caching instinct without his own "when NOT to use Redis" caveat about complex, high-durability workloads — high-velocity log writes plus synchronous cache invalidation is exactly the kind of workload where the coordination cost swamps the benefit.</p>
</div>
<div class="quote" data-author="sdcourse">"Key Insight: False positives are acceptable in many log processing scenarios. If bloom filter says 'error might exist,' you can check the actual storage. But if it says 'error definitely doesn't exist,' you save an expensive lookup entirely."<cite>— sdcourse</cite></div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <rect x="40" y="40" width="260" height="150" rx="12" fill="#eff6ff"/>
    <rect x="400" y="40" width="260" height="150" rx="12" fill="#fff7ed"/>
  </g>
  <text x="170" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">LUC: Three General Tools</text>
  <text x="170" y="75" text-anchor="middle" font-size="13" fill="#1e3a8a">Redis for repeated questions,</text>
  <text x="170" y="105" text-anchor="middle" font-size="13" fill="#1e3a8a">consistent hashing so only ~1/N</text>
  <text x="170" y="135" text-anchor="middle" font-size="13" fill="#1e3a8a">of keys move, Bloom filter to</text>
  <text x="170" y="160" text-anchor="middle" font-size="13" fill="#1e3a8a">skip proving absence</text>
  <text x="530" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#7c2d12">SDCOURSE: One Wired Pipeline</text>
  <text x="530" y="75" text-anchor="middle" font-size="13" fill="#7c2d12">Bloom filter: 50-200ms to 0.1-1ms,</text>
  <text x="530" y="105" text-anchor="middle" font-size="13" fill="#7c2d12">95% memory saved, per log type.</text>
  <text x="530" y="135" text-anchor="middle" font-size="13" fill="#7c2d12">3-tier Redis TTLs, &gt;95% hit ratio,</text>
  <text x="530" y="160" text-anchor="middle" font-size="13" fill="#7c2d12">never write-through</text>
</svg>
</div>
<div class="sketch-cap">Luc names the gatekeeper pattern once, generically; sdcourse deploys all three tools — fast store, spread load, cheap "no" — inside one log pipeline with numbers attached to each.</div>

<div class="box xr"><div class="box-lbl">Where They Converge / Diverge</div>
<p><strong>Converge:</strong> Bloom filters are the clean 1:1 match — both authors describe the identical mechanism (bit array, multiple hash functions, zero false negatives, tunable false positives) and reach the same conclusion in nearly the same words: Luc says a fast "maybe" is all you need when most of your system's time goes to proving nothing exists; sdcourse says the exact same trade pays off as a 50-200ms-to-0.1-1ms latency win. Both also treat "ask cheap before you ask expensive" as the underlying principle behind Redis/consistent hashing and the three-tier cache alike, not just behind Bloom filters specifically.</p>
<p><strong>Diverge:</strong> Luc's three tools stay general-purpose and independent — Redis, consistent hashing, and Bloom filters are each introduced with their own "when NOT to use" list, as building blocks a reader picks among per problem. sdcourse fuses two of those same tools into one concrete deployment: a three-tier Redis TTL scheme (the caching half) sitting alongside per-log-type Bloom filters (the existence-check half), inside a single system where the exact numbers — TTL values, hit-ratio floor, memory reduction percentage — are the point, not the general mechanism. Luc never quotes a specific latency number for Redis or a specific 1/N fraction beyond "about"; sdcourse's value only exists once bolted into a real pipeline with SLAs attached.</p>
</div>

<div class="recall">
<div class="recall-head">Active Recall</div>
<div class="q"><span class="q-n">Q1.</span> Per Luc, why does Redis's single-threaded event loop avoid the need for locking, and what four conditions does he give for when NOT to reach for Redis?</div>
<div class="q"><span class="q-n">Q2.</span> Per sdcourse, what is the measured latency swing a Bloom filter produces on an existence query (with numbers), and why does the pipeline maintain a separate Bloom filter per log type instead of one shared filter?</div>
<div class="q"><span class="q-n">Q3.</span> Bloom filters are the one topic both authors describe almost identically. Using consistent hashing (Luc) and the three-tier Redis TTL scheme (sdcourse) as evidence, explain how the two authors diverge once the topic moves from "what is this data structure" to "how do I deploy fast-access tools at scale."</div>
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
{CH1}
{CH2}
{CH3}
{CH4}
{CH5}
{CH6}
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
