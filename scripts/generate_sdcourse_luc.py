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
