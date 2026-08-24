#!/usr/bin/env python3
"""Build the "Stock Framework" Obsidian vault from the gated lecture briefs.

PURPOSE: context recovery WITHOUT re-reading raw transcripts. A future agent
(or human) should be able to answer "what does SOIC say about X", "why is
company Y questionable", or "is rule Z faithful to the source" by reading a
few notes here, never by re-opening a 178KB transcript.

Every claim in this vault traces to a brief that cleared the 80% verbatim
quote gate (scripts/verify_briefs.py). Nothing is synthesised beyond what the
briefs say; the aggregation is mechanical.

Implements the repo's standing vault contract: index (Home + MOCs) + log
(append-only Log.md) + cross-links (topics/ + inline wikilinks).
"""
from __future__ import annotations

import json, re, sys, yaml
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "docs" / "reassessment"
VAULT = Path.home() / ("Library/Mobile Documents/iCloud~md~obsidian/"
                       "Documents/Stock Framework")
LADDER = Path.home() / "Documents/workspace/Claude_Code/soic-ladder"
TODAY = date.today().isoformat()

COURSES = {
    "level-3": ("Level 3 - How to Value a Company & Portfolio Creation", "L3"),
    "l4":      ("L4 - When to Hold, Buy & Sell using Technicals",        "L4"),
    "l5":      ("Level 5 - How to Screen & Filter Epic Stocks",          "L5"),
    "crash":   ("Crash Course (4 modules)",                              "CC"),
}

SECTIONS = ["CRUX", "MECHANISM", "SIGNALS", "WHAT THE LADDER MISSES",
            "NAMED COMPANIES", "AGAINST THE 38"]

TOPICS = {
    "valuation":        ["p/e", "pe ratio", "peg", "ev/ebitda", "valuation",
                         "multiple", "intrinsic value", "dcf"],
    "entry-timing":     ["rsi", "adx", "entry", "buy trigger", "base formation",
                         "breakout", "pyramid"],
    "exit-discipline":  ["exit", "volatility stop", "vstop", "v-stop", "sell",
                         "parabolic sar", "stage 4", "time stop"],
    "growth-quality":   ["growth", "canslim", "volume growth", "one-off",
                         "base effect", "deleveraging"],
    "forensic":         ["forensic", "cash conversion", "cfo", "promoter pledge",
                         "auditor", "contingent liability", "red flag"],
    "position-sizing":  ["allocation", "position siz", "core", "satellite",
                         "portfolio", "rebalanc"],
    "sector-theme":     ["sector", "theme", "rotation", "capital cycle",
                         "industry structure"],
    "moving-averages":  ["ema", "moving average", "30-week", "200 dma", "dma"],
}


def read_briefs():
    out = []
    for key, (course_title, tag) in COURSES.items():
        refs_p = SRC / key / "refs.json"
        refs = json.loads(refs_p.read_text()) if refs_p.exists() else {}
        gate = {}
        gp = SRC / key / "gate_report.md"
        if gp.exists():
            for m in re.finditer(r"^(\w+)\s+(\d+)/(\d+)\s+([\d.]+)%\s+(\w+)",
                                 gp.read_text(), re.M):
                gate[m.group(1)] = (int(m.group(2)), int(m.group(3)),
                                    float(m.group(4)), m.group(5))
        for f in sorted((SRC / key).glob("*.md")):
            ref = f.stem
            if ref in {"SYNTHESIS", "gate_report", "README"}:
                continue
            text = f.read_text()
            if "## 1. CRUX" not in text:
                continue
            meta = refs.get(ref, {})
            if isinstance(meta, str):
                meta = {"slug": meta}
            secs = {}
            for i, name in enumerate(SECTIONS, 1):
                nxt = rf"\n## {i+1}\." if i < 6 else r"\Z"
                m = re.search(rf"## {i}\.[^\n]*\n(.*?)(?={nxt})", text, re.S)
                secs[name] = (m.group(1).strip() if m else "")
            out.append(dict(ref=ref, course=key, course_title=course_title,
                            tag=tag, meta=meta, secs=secs, gate=gate.get(ref),
                            raw=text))
    return out


def shortlist():
    f = LADDER / "runs/out_v4/shariah-compliant-full-2026-08-22.md"
    rows = {}
    for line in f.read_text().splitlines()[2:]:
        c = [x.strip() for x in line.split("|")]
        if len(c) < 29 or not c[1]:
            continue
        rows[c[1]] = dict(verdict=c[2], rsi=c[11], adx=c[12], pe=c[13],
                          growth3y=c[18], peg=c[19], roce=c[9], de=c[7],
                          exit_triggers=c[28])
    return rows


def rules():
    d = yaml.safe_load((LADDER / "rulebook/soic-ladder-rules-v1.yaml").read_text())
    out = []
    for kind in ("rules", "observations"):
        for e in d.get(kind) or []:
            out.append(dict(kind=kind[:-1], **e))
    return out


def topics_for(text):
    low = text.lower()
    return sorted(t for t, kws in TOPICS.items() if any(k in low for k in kws))


def fm(**kv):
    lines = ["---"]
    for k, v in kv.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            lines += [f"  - {x}" for x in v]
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def log_entry(vault, n_total, label):
    """Append-only ingest log. Contract: parse the last '(N total' to get the
    prior count; word the first-ever entry as a backfill; append only when the
    total actually changed."""
    p = vault / "Log.md"
    if not p.exists():
        p.write_text(
            "# Ingestion Log\n\n"
            "Append-only history of when content entered this vault. Distinct "
            "from [[Home]], which reflects only current state.\n\n"
            f"- {TODAY} — backfill: {n_total} item(s) already in vault "
            f"(log started here). {label}\n")
        return
    prior = 0
    for m in re.finditer(r"\((\d+) total", p.read_text()):
        prior = int(m.group(1))
    if n_total == prior:
        return
    delta = n_total - prior
    word = f"{delta} new item(s) captured" if delta > 0 else f"{-delta} item(s) removed"
    with p.open("a") as fh:
        fh.write(f"- {TODAY} — {word} ({n_total} total). {label}\n")


def build_mentions(briefs, sl):
    """Which lectures genuinely discuss each ticker. Shared by every
    pass so the vault and its own gap report cannot disagree."""
    # A brief's "AGAINST THE 38" section routinely ends with a roster of every
    # ticker it did NOT discuss ("None of the other 33 shortlisted names (ACE,
    # ACUTAAS, ...)"). A plain word-boundary scan therefore reported every one
    # of the 39 companies as "mentioned" -- the exact inverse of the truth, and
    # the same error class the readers kept making: matching a string without
    # reading what the sentence does with it.
    #
    # Two filters, structural first because phrasings are unbounded:
    #   1. a block naming >= ROSTER_MIN tickers is a roster, not a discussion;
    #   2. an explicit negation phrase.
    ROSTER_MIN = 4
    NEG = re.compile(
        r"(?i)(none of the (other|\d+)|all other|all remaining|the remaining|"
        r"none (are |is )?(named|mentioned|raised)|not named|no genuine hit|"
        r"unmentioned|are not (named|mentioned|discussed)|no other|"
        r"never (named|appears)|not the same|do(es)? not appear|"
        r"none of the 38|no shortlist name|^none\b)")

    def blocks(text):
        """Bullet/paragraph units, so a ticker is judged in the sentence that
        actually uses it rather than anywhere in the section."""
        return [x.strip() for x in re.split(r"\n(?=[-*#] )|\n\n", text) if x.strip()]

    tick_re = {t: re.compile(rf"\b{re.escape(t)}\b") for t in sl}

    mentions = defaultdict(list)
    for b in briefs:
        units = blocks(b["secs"]["NAMED COMPANIES"]) + blocks(b["secs"]["AGAINST THE 38"])
        for u in units:
            present = [t for t, rx in tick_re.items() if rx.search(u)]
            if len(present) >= ROSTER_MIN or NEG.search(u):
                continue
            for t in present:
                mentions[t].append((b, u))
    return mentions


def main():
    briefs = read_briefs()
    sl = shortlist()
    rl = rules()
    for sub in ("lectures", "courses", "companies", "rules", "topics", "findings"):
        (VAULT / sub).mkdir(parents=True, exist_ok=True)

    # ---- company -> mentions index (mechanical ticker scan) -----------------
    mentions = build_mentions(briefs, sl)

    topic_hits = defaultdict(list)

    # ---- lecture notes ------------------------------------------------------
    for b in briefs:
        m, s = b["meta"], b["secs"]
        tps = topics_for(s["CRUX"] + s["SIGNALS"] + s["WHAT THE LADDER MISSES"])
        for t in tps:
            topic_hits[t].append(b)
        g = b["gate"]
        cos = sorted({t for t in sl if re.search(
            rf"\b{re.escape(t)}\b", s['NAMED COMPANIES'] + s['AGAINST THE 38'])})
        body = [
            fm(title=f'"{m.get("title", b["ref"])}"', ref=b["ref"],
               course=f'"{b["course_title"]}"',
               module=f'"{m.get("module","")}"',
               lesson_id=m.get("lesson_id", ""),
               transcript_chars=m.get("chars", ""),
               gate=f"{g[2]:.1f}% ({g[0]}/{g[1]})" if g else "n/a",
               topics=tps, topic_links=[f'"[[{t}]]"' for t in tps],
               companies=cos, tags=["lecture", b["tag"].lower()]),
            "",
            f'# {m.get("title", b["ref"])}',
            "",
            f'`{b["ref"]}` · [[{b["course"]}-moc|{b["course_title"]}]]'
            + (f' · {m.get("module","")}' if m.get("module") else ""),
            "",
            "> [!abstract] Crux", "> " + s["CRUX"].replace("\n", "\n> "), "",
            "## Mechanism", "", s["MECHANISM"], "",
            "## Signals", "", s["SIGNALS"], "",
            "## What the ladder misses", "", s["WHAT THE LADDER MISSES"], "",
            "## Named companies", "", s["NAMED COMPANIES"], "",
            "## Against the 38", "", s["AGAINST THE 38"], "",
            "---",
            f'*Every quoted phrase above was machine-verified as verbatim-present '
            f'in this lecture. Gate: {g[2]:.1f}% ({g[0]}/{g[1]}).*' if g else "",
        ]
        (VAULT / "lectures" / f'{b["ref"]}.md').write_text("\n".join(body))

    # ---- company notes ------------------------------------------------------
    for tkr, row in sorted(sl.items()):
        ms = mentions.get(tkr, [])
        lines = [
            fm(ticker=tkr, verdict=row["verdict"],
               pe=row["pe"], peg=row["peg"], roce=row["roce"], de=row["de"],
               rsi=row["rsi"], adx=row["adx"], growth_3y=row["growth3y"],
               exit_triggers=row["exit_triggers"],
               lectures_mentioning=len(ms),
               tags=["company", row["verdict"].lower()]),
            "", f"# {tkr}", "",
            f'**Ladder verdict: {row["verdict"]}** · P/E {row["pe"]} · '
            f'PEG {row["peg"]} · ROCE {row["roce"]} · D/E {row["de"]} · '
            f'RSI {row["rsi"]} · ADX {row["adx"]} · 3y growth {row["growth3y"]}%'
            + (f' · **ExitTriggers {row["exit_triggers"]}**'
               if row["exit_triggers"] not in ("0", "") else ""),
            "",
        ]
        flags = []
        if row["rsi"] and row["rsi"].replace(".", "").isdigit() and float(row["rsi"]) >= 75:
            flags.append(f'RSI {row["rsi"]} sits in the 75-85 "don\'t buy now" '
                         f'zone reported in [[TVPDT]] / [[HGBYH]].')
        et = row["exit_triggers"]
        if et not in ("0", ""):
            # NOT "exits fired": the column counts how many of F23's THREE
            # triggers are currently firing, against a band of `< 3`. F23 fires
            # only at three. Calling 1 or 2 a fired exit was a misreading --
            # see ERRATA E3.
            fired_all = str(et).startswith("3")
            flags.append(
                (f'**All three** of F23\'s exit triggers are firing '
                 if fired_all else
                 f'{et} of F23\'s three exit triggers firing (F23 fires only at 3) ')
                + f'while the verdict is {row["verdict"]}.')
        if flags:
            lines += ["> [!warning] Automatic flags", ""] + \
                     [f"> - {x}" for x in flags] + [""]
        if ms:
            lines += ["## What the lectures say", ""]
            for b, blk in ms:
                lines += [f'### [[{b["ref"]}|{b["meta"].get("title", b["ref"])}]] '
                          f'· {b["tag"]}', "",
                          blk or "*Named in this lecture; see the note for context.*",
                          ""]
        else:
            lines += ["## What the lectures say", "",
                      "**No lecture in the 58-lecture corpus names this company.** "
                      "It reached the shortlist on ratios alone.", ""]
        lines += ["---", "*Ratios from the 2026-08-22 ladder run. Lecture claims "
                  "trace to quote-gated briefs.*"]
        (VAULT / "companies" / f"{tkr}.md").write_text("\n".join(lines))

    # ---- rule notes ---------------------------------------------------------
    for r in rl:
        p = r.get("provenance") or {}
        ref = p.get("ref")
        status = ("**UNSOURCED** — no ref recorded" if not ref
                  else f"cited to `{ref}`")
        quals = [b for b in briefs if r["id"] in b["raw"]]
        lines = [
            fm(rule_id=r["id"], kind=r["kind"], gate=r.get("gate", "(observation)"),
               metric=r.get("metric", ""),
               check=f'"{r.get("check_rule") or r.get("reference_band","")}"',
               provenance_ref=f'"{ref}"' if ref else "null",
               lectures_qualifying=len(quals),
               tags=["rule", "gating" if r["kind"] == "rule" else "observation"]),
            "", f'# `{r["id"]}`', "",
            f'**{"GATE " + r.get("gate","") if r["kind"] == "rule" else "OBSERVATION (never gates)"}** · '
            f'`{r.get("metric","")}` `{r.get("check_rule") or r.get("reference_band","")}`',
            "", f'> {r.get("display_text","")}', "",
            "## Provenance", "", f"- Status: {status}",
            f'- Quote on file: "{p.get("quote","")}"',
            "", "> [!note] The rulebook's `provenance.quote` fields are the "
            "author's paraphrase, not verbatim transcript text. They cannot be "
            "presence-checked; the usable test is whether the cited timestamp "
            "exists and its content supports the rule.", "",
        ]
        if quals:
            lines += ["## Lectures that engage this rule", ""]
            lines += [f'- [[{b["ref"]}|{b["meta"].get("title", b["ref"])}]] ({b["tag"]})'
                      for b in quals]
            lines += [""]
        (VAULT / "rules" / f'{r["id"]}.md').write_text("\n".join(lines))

    # ---- topic notes --------------------------------------------------------
    for t, bs in sorted(topic_hits.items()):
        lines = [fm(topic=t, lectures=len(bs), tags=["topic"]), "",
                 f'# {t.replace("-", " ").title()}', "",
                 f"{len(bs)} lectures across the corpus engage this topic.", ""]
        by_course = defaultdict(list)
        for b in bs:
            by_course[b["course_title"]].append(b)
        for ct, items in by_course.items():
            lines += [f"## {ct}", ""]
            lines += [f'- [[{b["ref"]}|{b["meta"].get("title", b["ref"])}]]'
                      for b in sorted(items, key=lambda x: x["ref"])]
            lines += [""]
        (VAULT / "topics" / f"{t}.md").write_text("\n".join(lines))

    # ---- course MOCs --------------------------------------------------------
    for key, (title, tag) in COURSES.items():
        bs = [b for b in briefs if b["course"] == key]
        syn = SRC / key / "SYNTHESIS.md"
        lines = [fm(course=f'"{title}"', lectures=len(bs), tags=["moc"]), "",
                 f"# {title}", "",
                 f"{len(bs)} lectures, all quote-gated.", "", "## Lectures", ""]
        for b in sorted(bs, key=lambda x: x["ref"]):
            g = b["gate"]
            lines.append(f'- [[{b["ref"]}|{b["meta"].get("title", b["ref"])}]]'
                         + (f' — {g[2]:.0f}%' if g else ""))
        lines += ["", "## Synthesis", ""]
        lines += [syn.read_text() if syn.exists()
                  else "*Synthesis not yet written.*"]
        (VAULT / "courses" / f"{key}-moc.md").write_text("\n".join(lines))

    n = len(briefs) + len(sl) + len(rl)
    log_entry(VAULT, n, f"{len(briefs)} lectures, {len(sl)} companies, {len(rl)} rules.")

    # ---- machine-routable index --------------------------------------------
    idx = {
        "vault": "Stock Framework",
        "purpose": ("Context recovery for the SOIC method reassessment without "
                    "re-reading raw transcripts."),
        "built": TODAY,
        "source_of_truth": "docs/reassessment/ in knowledge-toolkit",
        "gate": "every lecture note derives from a brief at >=80% verbatim quote verification",
        "counts": {"lectures": len(briefs), "companies": len(sl),
                   "rules": len(rl), "topics": len(topic_hits)},
        "routing": {
            "what does SOIC say about X": "topics/<topic>.md then lectures/<REF>.md",
            "why is company Y on the list": "companies/<TICKER>.md",
            "is rule Z faithful to source": "rules/<rule-id>.md",
            "what did a course argue": "courses/<key>-moc.md",
            "what are the headline problems": "findings/",
        },
        "lectures": {b["ref"]: {
            "title": b["meta"].get("title", b["ref"]),
            "course": b["tag"],
            "gate_pct": b["gate"][2] if b["gate"] else None,
            "companies": sorted({t for t in sl if re.search(
                rf"\b{re.escape(t)}\b",
                b["secs"]["NAMED COMPANIES"] + b["secs"]["AGAINST THE 38"])}),
        } for b in briefs},
    }
    (VAULT / "index.yaml").write_text(yaml.safe_dump(idx, sort_keys=False,
                                                     width=100))
    print(f"lectures={len(briefs)} companies={len(sl)} rules={len(rl)} "
          f"topics={len(topic_hits)}")
    print(f"mentioned companies={sum(1 for t in sl if mentions.get(t))}/{len(sl)}")
    return 0


def _run_all():
    main()
    build_findings_and_home()
    build_typed_edges()

# ---------------------------------------------------------------------------
# Findings + Home + START-HERE. Appended as a second pass so the ranked
# findings stay hand-curated (each carries an explicit verification status)
# while everything above stays mechanically derived from the briefs.
# ---------------------------------------------------------------------------

FINDINGS = [
 ("F01", "G0's screen lost a whole leg", "VERIFIED AT SOURCE",
  "The ladder's G0 rules cite `MASTEC 00:09:35`. That resolves to **Tools To "
  "Find Epic Stocks** (L5) 00:09:35, word for word. But at **00:23:47** the "
  "same lecture states the screen as ONE query with **four** legs:\n\n"
  "> year on year quarterly sales growth of more than 15% Year on year "
  "quarterly profit growth of more than 20% ROC of more than 15% **and market "
  "cap of more than 1000** [crore]\n\n"
  "The ladder encodes three and dropped the market-cap floor. At 00:42:15 he "
  "gives its rationale — below ~Rs 100cr \"the businesses have very negative "
  "cash loads or poor business models\" — so it is a **quality proxy**, not an "
  "arbitrary size cutoff. Every one of the 38 passed a three-quarters version "
  "of his screen.", ["TFELT", "FESTF"], []),

 ("F02", "The P/E band is the only unsourced rule — and lost its condition",
  "VERIFIED (ref) / REPORTED (source)",
  "`pe_context-001` is the **only** entry of 16 whose provenance carries "
  "`ref: null`. Every other rule names a lecture and timestamp.\n\n"
  "The band itself is real — [[VALU2]] states 15-35x twice — but **never "
  "standing alone**. It is always paired with the growth rate matching the "
  "multiple, and is explicitly overridden to **5-10x for a no-moat B2B "
  "business**. The rule copied the number and left the condition behind.\n\n"
  "Five L3 lectures contradict a flat band across sectors; 27 of the 38 fail "
  "it. Note also the corpus contains **three distinct P/E numbers** (a 15-30x "
  "personal preference, a <40 optional dial in [[TFELT]], and this 15-35 band) "
  "which must not be merged.", ["VALU2", "BVB", "TFELT", "VALUV"],
  ["pe_context-001"]),

 ("F03", "The ROCE gate dropped 'or trending toward it'", "REPORTED, MULTI-SOURCE",
  "`capital_efficiency_gate-001`'s own provenance quote reads \"ROC/ROE above "
  "15% **or trending toward it**\". Only `>= 15` point-in-time was encoded.\n\n"
  "[[FESTF]] independently reports a **turnaround carve-out**: the ROC "
  "criterion can be removed where a company is inflecting out of a turnaround. "
  "Consequence: the gate structurally prefers peak-economics companies — which "
  "L3 names as the danger zone — and demotes under-earning recovery names, "
  "which it names as the margin-of-safety zone.",
  ["FESTF", "TFELT", "ARTBV"], ["capital_efficiency_gate-001"]),

 ("F04", "G8 gates on two legs of a four-leg setup", "REPORTED / PARTLY CORRECTED",
  "[[SESCS]] states the buying setup as RSI>50 **AND** ADX>20 **AND** relative "
  "strength vs Nifty 500 **>0**.\n\n"
  "**Correction (see [[ERRATA]] E2):** an earlier version of this note claimed "
  "the ladder had \"no concept of relative strength at all\". That was wrong — "
  "`judge.py` computes `nifty500_relative_strength` on every run. The accurate "
  "finding is narrower: the third leg is **computed but does not gate**. G8's "
  "PASS/FAIL rests on RSI and ADX only.\n\n"
  "L4's synthesis adds that the **Volatility Stop** is the load-bearing signal "
  "(the stated bare-minimum entry condition across ~8 lectures) while **ADX** — "
  "which the instructor personally runs at zero and calls whipsaw-prone at 20 — "
  "is the hard gate.\n\n"
  "The RSI floor is also **contested inside the corpus**: 45 in "
  "[[ESRLE]]/[[CSLRC]] (which document the SOIC LTI tool itself), 50 in "
  "[[TVPDT]]/[[TVPD2]]. The rulebook silently picked one source.",
  ["SESCS", "ESRLE", "CSLRC", "TVPDT", "WBPNW", "MAAIM"],
  ["entry_rsi-001", "entry_adx-001"]),

 ("F05", "The exit layer exists and gates nothing", "VERIFIED",
  "**This finding replaces an earlier, wrong one** which claimed the "
  "`ExitTriggers` column was orphaned and that NATIONALUM was a self-"
  "contradiction. Both were controller errors — see [[ERRATA]] E2 and E3.\n\n"
  "`judge.py` computes, and `cli.py` appends on every run, cited to `FRAMEC`:\n\n"
  "| Metric | What it is |\n|---|---|\n"
  "| `ema30_break_pct` | the 30-week EMA break |\n"
  "| `nifty500_relative_strength` | relative strength vs the Nifty 500 |\n"
  "| `weekly_volatility_stop` | the volatility stop |\n"
  "| `exit_triggers_fired_count` | F23's 3-trigger exit count |\n"
  "| `ema_period_used` | flags when the recent-IPO EMA fallback applied |\n\n"
  "`ExitTriggers` is **how many of the three are firing**, against a band of "
  "`< 3`; F23 fires only when all three fire together. Across the 2026-08-22 "
  "run: 222 companies at zero, 43 at one, 54 at two, **151 at three**, 30 "
  "unmeasurable — and **zero CANDIDATEs have all three firing**. The ladder is "
  "internally consistent here.\n\n"
  "The real finding: this whole layer is **observation-only**. It never changes "
  "a verdict, by the same deliberate design that leaves G2 and G6 unoccupied.",
  ["SESCS", "WBPNW"], []),

 ("F06", "Only one rulebook citation is actually defective", "VERIFIED",
  "`scripts/audit_rulebook.py` resolves every rulebook citation and checks the "
  "cited timestamp exists in the lesson the REF names. Result: **15 of 16 "
  "sound**.\n\n"
  "The single defect is `pe_context-001`, whose `provenance.ref` is literally "
  "`null` — no lecture, no timestamp, nothing to check.\n\n"
  "**Two rules were previously reported here as broken and are not** (see "
  "[[ERRATA]] E1):\n\n"
  "- `growth_trap_flag-001` — `TVGPF` was assumed to abbreviate \"TVGP "
  "Framework\" and searched for in the wrong lectures. It resolves to "
  "*18.01.26 Part 1 Valuations*, where the cited window does discuss growth "
  "traps.\n"
  "- `canslim_sales-001` / `canslim_pat-001` — **a REF code is not a unique "
  "key**: 25 of 221 codes map to several lessons (`MODULB` maps to eight). A "
  "last-wins loader picked the wrong `MASTEC`. Resolving the pair `(REF, "
  "timestamp)` lands on *15.12.24 Class 4 How to Filter Epic Stocks*, where "
  "00:09:35 carries the cited sentence verbatim.\n\n"
  "Both are now pinned as regression tests — on the analysis, not the rulebook.",
  ["TVGP2", "TVGPT", "VALU2", "VALUV"], ["pe_context-001", "growth_trap_flag-001"]),

 ("F07", "The corpus teaches exits the ladder computes but never acts on",
  "REPORTED, MULTI-SOURCE",
  "**Corrected** from an earlier claim that there was \"no exit rule anywhere\" "
  "— there is a full exit layer, it simply gates nothing (see [[ERRATA]] E2 and "
  "[[F05-the-exit-layer-exists-and-gates-nothing|F05]]).\n\n"
  "[[SESCS]] alone yields four computable exit triggers: a 10-week EMA break, "
  "price >80% above the 200-DMA, a 30-week EMA breakdown paired with the "
  "Volatility Stop, and relative strength crossing below zero. [[RSSER]] "
  "demonstrates a monthly-RSI<50 multi-year-top signal live on **ASIANPAINT**.\n\n"
  "Three of those are already computed. The gap is that a fired exit cannot "
  "change a verdict, and the 10-week EMA break and 200-DMA extension are not "
  "computed at all.\n\n"
  "Caveat that must survive into any rule: the Volatility Stop multiplier is "
  "horizon- and regime-dependent (2x / 2.5x / lower for cyclicals) and the "
  "corpus disagrees with itself on ATR length (14 in HGBYH, 10 elsewhere). It "
  "must never be hard-coded as a single constant.",
  ["SESCS", "RSSER", "ARTBV", "ODDM", "BUFF"], []),

 ("F08", "Sector selection comes first, and the ladder has no sector dimension",
  "REPORTED, MULTI-SOURCE",
  "[[SGSTS]] states it plainly — \"Stock picking is later\" and \"if we catch "
  "the right theme, then stock picking is overrated\" — and its worked pairs "
  "show **the same absolute growth number means opposite things in different "
  "sectors**. TVGP's own first letter is **T for Theme**, and both TVGP "
  "lectures are Theme-only.\n\n"
  "The ladder screens companies one at a time: no sector index, no rotation, "
  "no peer breadth, no sector-appropriate thresholds, and no sector "
  "concentration cap — while 10 of the 38 are pharma/API (~26%), past the "
  "15-20% cap [[PALLOC]] states.",
  ["SGSTS", "TVGPT", "TVGP2", "MSRTM", "PALLOC"], []),

 ("F09", "G2 should stay mostly empty — the authors were right",
  "REPORTED, MULTI-SOURCE",
  "Two readers who went looking for a forensic veto concluded there isn't one. "
  "[[JFSNJ]] and [[CFSHC]] supply real cross-statement checks but frame every "
  "one as **a caution, never a numeric veto**. [[RSSER]]'s genuine "
  "disqualifiers (criminal case, promoter selling into headwinds) are "
  "judgement-tier.\n\n"
  "The disaster pattern is a **compound**: multi-year zero CFO **and** "
  "exploding debt **and** write-offs — not any single ratio. [[ESRLE]] adds "
  "auditor resignation, contingent liability, and promoter pledge.\n\n"
  "The clearest cost of the empty gate is **CPPLUS**: CFO/EBITDA -1.3%, "
  "CFO/PAT -48%, still CANDIDATE. Verify those figures at source before acting.",
  ["JFSNJ", "CFSHC", "RSSER", "ESRLE"], ["cash_conversion-001", "cfo_to_pat-001"]),

 ("F10", "PAT growth can be fake in two specific ways", "REPORTED",
  "[[SGBT2]] shows a passing PAT-growth number can be entirely "
  "**deleveraging-driven** (falling interest cost, not operations) or "
  "**acquisition-led** (inorganic). It works this through **USHAMART**, which "
  "is in the 38. [[FMODB]] and [[ARTBV]] add one-off income distortion "
  "(termination income, a single molecule, inventory gains).\n\n"
  "`canslim_pat-001` reads the headline number and cannot tell these apart.",
  ["SGBT2", "FMODB", "ARTBV", "ODDM"], ["canslim_pat-001"]),

 ("F11", "The rulebook's provenance cannot be machine-verified",
  "VERIFIED (structural)",
  "The `provenance.quote` fields are the rulebook author's **paraphrase**, not "
  "verbatim transcript text. Compare G0's *\"screen for >15% YoY quarterly "
  "sales growth...\"* against what is actually said: *\"companies which are "
  "showing more than 15% sales growth and more than 20% profit after tax "
  "growth\"*.\n\n"
  "Consequence: the 80% presence check that validated all 58 lecture briefs "
  "**cannot be applied to the rulebook**. The only usable audit is per-rule: "
  "*does the cited timestamp exist, and does the content there support the "
  "rule?* That audit now exists (`scripts/audit_rulebook.py`) and reports "
  "**15 of 16 sound** — see [[F06-only-one-rulebook-citation-is-actually-defective|F06]]. "
  "The single failure is `pe_context-001`, whose ref is `null`.",
  [], []),

 ("F12", "Data-quality issues to resolve before acting", "OPEN",
  "Flagged by readers and by direct inspection; none is a finding about the "
  "method, all are reasons to distrust specific cells:\n\n"
  "- **CPPLUS** CFO/EBITDA -1.33% and CFO/PAT -48% — verify at source, values "
  "this extreme are sometimes a data fault.\n"
  "- **CFO/PAT above 200%** for TMCV (494%), MOTHERSON (226%), EXIDEIND (204%) "
  "— computationally suspect.\n"
  "- **Blank PEG / 3y-growth** cells for six names (NESTLEIND, SPLPETRO, TMCV, "
  "CARBORUNIV, FLUOROCHEM, JUBLINGREA).\n"
  "- **SPLPETRO**'s verdict rests on a G3 **ABSTAIN**.\n"
  "- **ASIANPAINT**'s G0 sales growth 17.93% versus [[FMODB]]'s account of "
  "seven flat quarters — a snapshot-timing question.\n"
  "- **FMNAF**'s transcript ends mid-lecture at 01:08:30; the TVGP module's "
  "notes carry no `duration` field, so truncation cannot be confirmed either "
  "way. All 23 lectures that *could* be checked covered 97-100%.", [], []),
]

FALSE_POSITIVES = [
 ("Chemplus", "CPPLUS", "A PVC manufacturer in [[FMODA]]; CP Plus is a CCTV business."),
 ("Exidus Wellness", "EXIDEIND", "Named in [[FESTF]]; a different company entirely."),
 ("Welspun Corp", "WELSPUNLIV", "Pipes, in [[FESTF]]; WELSPUNLIV is Welspun Living."),
 ("Stallion Fluorochemicals", "FLUOROCHEM", "In [[SGBT2]]; not Gujarat Fluorochemicals."),
]


def slugify(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def build_findings_and_home():
    briefs = read_briefs()
    sl = shortlist()
    fdir = VAULT / "findings"
    fdir.mkdir(parents=True, exist_ok=True)
    # Retitling a finding changes its slug, so a plain rewrite leaves the OLD
    # file behind and the vault ends up carrying the superseded version of a
    # correction beside the corrected one -- the worst possible outcome for a
    # document whose whole purpose is being trustworthy. Prune first.
    expected = {f"{fid}-{slugify(title)}.md" for fid, title, _, _, _, _ in FINDINGS}
    expected.add("false-positive-matches.md")
    for stale in fdir.glob("*.md"):
        if stale.name not in expected:
            stale.unlink()
    fnames = []
    for fid, title, status, body, lects, rules_ in FINDINGS:
        name = f"{fid}-{slugify(title)}"
        fnames.append((fid, title, status, name))
        lines = [fm(finding=fid, status=f'"{status}"', tags=["finding"],
                    lectures=lects, rules=rules_), "",
                 f"# {fid} — {title}", "",
                 f"> [!info] Verification status: **{status}**", "",
                 body, ""]
        if lects:
            lines += ["## Lectures", ""] + [f"- [[{l}]]" for l in lects] + [""]
        if rules_:
            lines += ["## Rules affected", ""] + [f"- [[{r}]]" for r in rules_] + [""]
        (VAULT / "findings" / f"{name}.md").write_text("\n".join(lines))

    fp = ["---", "tags:", "  - reference", "---", "",
          "# False-positive company matches — do not re-derive", "",
          "Names that look like shortlist tickers but are **different "
          "companies**. Each was caught by a reader during the pass. Recorded "
          "here so they cannot resurface later as evidence.", "",
          "| Named in lecture | Looks like | Why it is not |", "|---|---|---|"]
    fp += [f"| {a} | `{b}` | {c} |" for a, b, c in FALSE_POSITIVES]
    (VAULT / "findings" / "false-positive-matches.md").write_text("\n".join(fp))

    mentions = build_mentions(briefs, sl)
    unmentioned = sorted(t for t in sl if not mentions.get(t))

    start = [
        fm(tags=["entry-point"]), "",
        "# START HERE", "",
        "**What this vault is.** A re-read of **58 SOIC lectures**, whole, to "
        "test whether the `soic-ladder` screener's 38-name shortlist contains "
        "the right companies. Built so you never have to reopen a transcript.",
        "",
        "**How far to trust it.** Every lecture note derives from a brief in "
        "which *every quoted phrase was machine-verified as verbatim-present in "
        "the lecture it cites* (>=80% bar; all 58 passed). Findings carry an "
        "explicit verification status — `VERIFIED` means checked at source in "
        "this vault's own build; `REPORTED` means a reader asserted it with a "
        "citation.", "",
        "## The answer in one line", "",
        "The lectures' **doubts cluster in the CANDIDATE column** and their "
        "**endorsements cluster in WATCH**. The screen is a faithful copy of "
        "individual numbers with the conditions stripped off them.", "",
        "## Read these five, in order", "",
    ]
    # Derive slugs from FINDINGS rather than hardcoding them: retitling a
    # finding silently broke this list once, which is a bad failure mode for
    # the vault's own entry point.
    _title = {fid: t for fid, t, _, _, _, _ in FINDINGS}
    for n, (fid, why) in enumerate([
            ("F01", "the screen is missing a leg its own author states"),
            ("F03", "why the filter runs backwards"),
            ("F06", "what is actually wrong with the citations, and what is not"),
            ("F02", "the one unsourced rule"),
            ("F11", "why you cannot automate this audit by quote-matching")], 1):
        start.append(f"{n}. [[{fid}-{slugify(_title[fid])}]] — {why}")
    start += [
        "", "## Where to look for what", "",
        "| Question | Go to |", "|---|---|",
        "| Why is company X on the list? | `companies/X.md` |",
        "| What does SOIC say about topic Y? | `topics/Y.md` -> `lectures/` |",
        "| Is rule Z faithful to the source? | `rules/Z.md` |",
        "| What did a whole course argue? | `courses/*-moc.md` |",
        "| What are the headline problems? | `findings/` |",
        "| Machine routing | `index.yaml` |", "",
        "## Two things this vault deliberately does NOT claim", "",
        "- **It does not say the empty gates are a bug.** Two independent "
        "readers concluded G2 and G6 should stay mostly empty; the authors' "
        "\"better an honest no-veto than a guessed one\" holds up. The real "
        "defect is narrower: **rules recorded without their conditions**.",
        "- **It is not investment advice.** It describes what a course teaches "
        "and where the screening code departs from it.", "",
        "## Known gaps", "",
        f"- **{len(unmentioned)} of the 38 companies are named by no lecture at "
        "all** — they reached the shortlist on ratios alone: "
        + ", ".join(f"`{t}`" for t in unmentioned) + ".",
        "- Level 1, Level 2 and Level 6 are **not** in this pass.",
        "- See [[F12-data-quality-issues-to-resolve-before-acting]] before "
        "acting on any specific cell.",
    ]
    (VAULT / "START-HERE.md").write_text("\n".join(start))

    home = [fm(tags=["moc"]), "", "# Home — Stock Framework", "",
            "Start at [[START-HERE]]. Ingest history in [[Log|Ingestion Log]].",
            "", "## Findings", ""]
    home += [f"- [[{n}|{fid} — {t}]] · *{s}*" for fid, t, s, n in fnames]
    home += ["- [[false-positive-matches]] — names that are not the ticker they resemble", ""]
    home += ["## Courses", ""]
    for key, (title, tag) in COURSES.items():
        n = len([b for b in briefs if b["course"] == key])
        home.append(f"- [[{key}-moc|{title}]] — {n} lectures")
    home += ["", "## Topics", ""]
    home += [f"- [[{p.stem}]]" for p in sorted((VAULT / "topics").glob("*.md"))]
    home += ["", "## Companies under test", ""]
    by_verdict = defaultdict(list)
    for t, r in sorted(sl.items()):
        by_verdict[r["verdict"]].append(t)
    for v, ts in sorted(by_verdict.items()):
        home.append(f"**{v}** ({len(ts)}): " + " · ".join(f"[[{t}]]" for t in ts))
    home += ["", "## Rules under test", ""]
    for p in sorted((VAULT / "rules").glob("*.md")):
        home.append(f"- [[{p.stem}]]")
    (VAULT / "Home.md").write_text("\n".join(home))
    print(f"findings={len(fnames)} unmentioned_companies={len(unmentioned)}")




# ---------------------------------------------------------------------------
# TYPED EDGES (a narrow Level-4 slice over the Level-2 wiki).
#
# A wiki's backlinks say "see also". They do not say HOW two notes relate --
# VALU2 *sources* the P/E band, ARTBV *contradicts* it, FMODA *qualifies* it,
# and a plain link flattens all three into one list. These passes read the
# brief's own wording around each mention and stamp a relation on the edge,
# then emit a flat claims table so a narrow question ("which lectures
# contradict pe_context-001?") is answered without opening a 30KB note.
#
# The classifier is deterministic and conservative: no keyword hit -> the edge
# is typed "mentions"/"neutral", never guessed into a stronger claim.
# ---------------------------------------------------------------------------

SUBJECT_WINDOW = 160   # chars of a block treated as its subject line

RULE_REL = [
    ("contradicts",  r"(?i)\b(contradict|directly contradicts|undercut|"
                     r"is wrong|does not survive|never states|refutes)"),
    ("qualifies",    r"(?i)\b(qualif|condition|carve-?out|caveat|narrow|"
                     r"scope[sd]?\b|only applies|override|softens|exception)"),
    ("corroborates", r"(?i)\b(corroborat|confirms|independently reaches|"
                     r"same threshold|matches|supports the rule|reinforc)"),
    ("sources",      r"(?i)\b(provenance|is the source|states it twice|"
                     r"stated here|word[- ]for[- ]word|verbatim source)"),
]
CO_REL = [
    ("doubt",   r"(?i)(specific doubt|doubt raised|cautionary|negative|"
                r"红|red flag|argues against|expensive|overvalued|"
                r"warning|caution)"),
    ("support", r"(?i)(specific support|positive (example|case|mention)|"
                r"endorse|argues for|textbook (positive|example)|"
                r"real, specific|genuine .{0,20}support)"),
]


def classify(text, table, default):
    for label, pat in table:
        if re.search(pat, text):
            return label
    return default


def one_line(text, limit=190):
    t = re.sub(r"\s+", " ", re.sub(r"^[-*#]+\s*", "", text)).strip()
    return (t[:limit] + "...") if len(t) > limit else t


def build_typed_edges():
    briefs = read_briefs()
    sl = shortlist()
    rl = rules()
    mentions = build_mentions(briefs, sl)
    edges = []

    # lecture -> rule
    rule_ids = [r["id"] for r in rl]
    for b in briefs:
        sec = b["secs"]["WHAT THE LADDER MISSES"]
        for unit in re.split(r"\n(?=[-*#\d] )|\n\n", sec):
            # A block is ABOUT the rule it leads with. Rules named later in the
            # same block are comparisons ("...the way leverage-001 already
            # does"), not claims about them. Attributing the block to every id
            # it contains produced edges asserting a P/E claim against the ROCE
            # and leverage rules -- the same error class as the roster scan:
            # matching a string without checking what the sentence is about.
            head = unit[:SUBJECT_WINDOW]
            for rid in rule_ids:
                if rid in head:
                    edges.append(dict(
                        src=b["ref"], src_title=b["meta"].get("title", b["ref"]),
                        course=b["tag"], kind="rule", dst=rid,
                        relation=classify(unit, RULE_REL, "mentions"),
                        claim=one_line(unit)))

    # lecture -> company
    for tkr, ms in mentions.items():
        for b, blk in ms:
            edges.append(dict(
                src=b["ref"], src_title=b["meta"].get("title", b["ref"]),
                course=b["tag"], kind="company", dst=tkr,
                relation=classify(blk, CO_REL, "neutral"),
                claim=one_line(blk)))

    # dedupe: keep the strongest, longest claim per (src, dst)
    STRENGTH = {"contradicts": 4, "sources": 4, "qualifies": 3,
                "corroborates": 3, "doubt": 4, "support": 4,
                "mentions": 1, "neutral": 1}
    best = {}
    for e in edges:
        k = (e["src"], e["kind"], e["dst"])
        cur = best.get(k)
        if cur is None or (STRENGTH[e["relation"]], len(e["claim"])) > \
                          (STRENGTH[cur["relation"]], len(cur["claim"])):
            best[k] = e
    edges = sorted(best.values(), key=lambda e: (e["kind"], e["dst"], e["src"]))

    # ---- flat claims table (the lightweight lookup) ------------------------
    by_kind = defaultdict(list)
    for e in edges:
        by_kind[e["kind"]].append(e)
    lines = [fm(tags=["reference", "claims-table"], edges=len(edges)), "",
             "# Claims table — typed edges", "",
             "Every edge between a lecture and a rule or a company, with the "
             "**relation** stamped on it. Built for narrow lookups: answer "
             '"which lectures contradict this rule?" here, without opening a '
             "lecture note.", "",
             "Relations are classified from each brief's own wording. Where the "
             "wording is not explicit the edge is typed `mentions` / `neutral` "
             "rather than guessed into a stronger claim.", ""]
    for kind, title in (("rule", "Lecture → Rule"), ("company", "Lecture → Company")):
        lines += [f"## {title}", "",
                  "| Lecture | Course | Relation | Target | Claim |",
                  "|---|---|---|---|---|"]
        for e in by_kind[kind]:
            claim = e["claim"].replace("|", "\\|")   # keep table cells intact
            lines.append(f'| [[{e["src"]}]] | {e["course"]} | `{e["relation"]}` | '
                         f'[[{e["dst"]}]] | {claim} |')
        lines += [""]
    (VAULT / "claims.md").write_text("\n".join(lines))

    # ---- stamp relations back onto rule notes ------------------------------
    for r in rl:
        p = VAULT / "rules" / f'{r["id"]}.md'
        if not p.exists():
            continue
        rel = [e for e in edges if e["kind"] == "rule" and e["dst"] == r["id"]]
        if not rel:
            continue
        grouped = defaultdict(list)
        for e in rel:
            grouped[e["relation"]].append(e)
        block = ["", "## How lectures relate to this rule", ""]
        for label in ("contradicts", "qualifies", "corroborates", "sources", "mentions"):
            if label not in grouped:
                continue
            block += [f"### {label} ({len(grouped[label])})", ""]
            for e in sorted(grouped[label], key=lambda x: x["src"]):
                block.append(f'- [[{e["src"]}|{e["src_title"]}]] ({e["course"]}) — {e["claim"]}')
            block += [""]
        block += ["*See [[claims]] for the full typed-edge table.*", ""]
        txt = p.read_text()
        txt = re.sub(r"\n## Lectures that engage this rule\n.*?(?=\Z)", "\n",
                     txt, flags=re.S)
        p.write_text(txt.rstrip() + "\n" + "\n".join(block))

    # ---- stamp polarity onto company notes ---------------------------------
    for tkr in sl:
        p = VAULT / "companies" / f"{tkr}.md"
        if not p.exists():
            continue
        rel = [e for e in edges if e["kind"] == "company" and e["dst"] == tkr]
        if not rel:
            continue
        counts = defaultdict(int)
        for e in rel:
            counts[e["relation"]] += 1
        summary = " · ".join(f"**{k}** {v}" for k, v in sorted(counts.items()))
        txt = p.read_text()
        txt = txt.replace("## What the lectures say",
                          f"**Lecture verdicts:** {summary}\n\n"
                          "## What the lectures say", 1)
        if counts.get("doubt") and counts.get("support"):
            txt = txt.replace("## What the lectures say",
                              "> [!warning] Contested\n> This company is both "
                              "supported and doubted by different lectures. "
                              "Read both before concluding.\n\n"
                              "## What the lectures say", 1)
        p.write_text(txt)

    # ---- machine index -----------------------------------------------------
    idx = yaml.safe_load((VAULT / "index.yaml").read_text())
    idx["claims"] = {"file": "claims.md", "edges": len(edges),
                     "relations": sorted({e["relation"] for e in edges})}
    idx["routing"]["which lectures contradict rule Z"] = "claims.md (Lecture -> Rule)"
    idx["routing"]["is company Y contested"] = "companies/Y.md front block"
    (VAULT / "index.yaml").write_text(yaml.safe_dump(idx, sort_keys=False, width=100))

    tally = defaultdict(int)
    for e in edges:
        tally[f'{e["kind"]}:{e["relation"]}'] += 1
    print("edges:", len(edges), dict(sorted(tally.items())))
    return edges


if __name__ == "__main__":
    raise SystemExit(_run_all())
