---
title: Classification Using Confidence (SEC Filings to SIC Groups)
kind: cookbook
source: Classification using confidence (cookbooks/classification_using_confidence)
source_url: https://docs.typesafe.ai/cookbooks/classification_using_confidence
tags: [cookbook, confidence, classification]
topics: [topic-calibration, topic-classification, topic-routing]
---
# Classification Using Confidence (SEC Filings to SIC Groups)
> One 75-option `Choice` per document; read its `confidence`; if >= 0.9 report the fine label (industry group), else report the parent label (division). One request per document, no second model, no extra calls.

## What it is / How it works
Task: classify the "Item 1. Business" text of SEC 10-K filings under the Standard Industrial Classification (SIC): 75 industry (major) groups, one `Choice` per document.

**Premise.** The answer to a hard case looks no different from an easy one, and telling them apart is normally where cost goes (second model, extra calls, human review). A `Choice` already tells you: alongside the winner it returns `confidence`, "high when nearly all the probability landed on one option and low when it spread across several".

**Exploit the label hierarchy.** SIC groups roll up into divisions. When unsure of the group, report the division it belongs to; the broad label follows from the narrow one, so there is no second call. Result: `classify()` returns a label plus how specific it is (`level` = group or division).

```
doc (Item 1 "Business") -> [one request: Choice over 75 groups] -> confidence >= 0.9 ?
   yes -> report industry group (e.g. 28)
   no  -> report its division (e.g. manufacturing)
```

### Taxonomy construction (no model involved)
- `sic_codes.tsv`: SEC's published list of industries for filers to pick their code from, fetched 2026-08-10: **444 four-digit codes**, each with a title.
- First two digits = **major group** (75 of them, `01` agricultural production to `99` non-classifiable). Fixed ranges of major groups = **10 divisions**.
- Output: `444 industries -> 75 major groups -> 10 divisions`.

Divisions (major-group ranges):

| Range | Division |
|---|---|
| 01-09 | agriculture, forestry and fishing |
| 10-14 | mining |
| 15-17 | construction |
| 20-39 | manufacturing |
| 40-49 | transportation, communications and utilities |
| 50-51 | wholesale trade |
| 52-59 | retail trade |
| 60-67 | finance, insurance and real estate |
| 70-89 | services |
| 91-99 | public administration |

Example: group 35 = manufacturing (engines & turbines, farm machinery & equipment, lawn & garden tractors ...).

### Describing options
A group's own name is not always available: **42 of the 75** groups carry an umbrella title in the SEC list, the rest carry none. So each group is described by the industries inside it: `"<umbrella> - includes: <up to 8 industries joined by '; '>"` (`MAX_NAMED = 8`; umbrella = the `XX00` code title; umbrella-only or list-only if one is missing). Examples: group 20 "food and kindred products - includes: meat packing plants; sausages & other prepared meat products; poultry slaughtering and processing; dairy product..."; group 65 "real estate - includes: real estate operators (no developers) & lessors; operators of nonresidential buildings; operators of apartment buildings; less...". The option key is the 2-digit group code; the criteria dict maps `group -> describe(group)`.

### The question
Single `Choice`, key `"group"`:
> "Which broad industry does this company operate in? Judge the company's own operations as this filing describes them."
State = the filing text. `model=jev-1.12`. Fields read: `answer.choice` (winning group), `answer.confidence`, `answer.probabilities` (weight on each of the 75).

**Why `confidence` and not the winner's own probability:** a winner at 0.45 with a runner-up at 0.44, and a winner at 0.45 with the rest of the weight scattered thinly, are different situations; `confidence` (how concentrated the spread is) separates them. (See [[confidence]].)

### The four-line recipe
```python
sure = answer["confidence"] >= CONFIDENT   # CONFIDENT = 0.9
level = "group" if sure else "division"
label = answer["group"] if sure else division(answer["group"])
```
Every filing still returns a usable label: an uncertain one comes back one level up instead of being dropped or sent on. "If a division is too coarse for your application to act on, this branch is where you hand it to a person." To port: point `ask()` at your documents and rewrite `describe()` for your own taxonomy; the rest carries over.

## When to use / when NOT to use
Use when (a) labels form a hierarchy (fine -> coarse), (b) you can accept a coarser answer for hard cases, and (c) you want to avoid second-model/human-review cost. The unsure branch can also be a human handoff.
Constraints in source: a `Choice` "works reliably up to roughly 240 options"; 75 is well inside. Caveat on the labels: SIC codes are **self-reported** (picked once by whoever prepared the filing) and go stale when a company sells the business the code names and keeps the code; the 60 filings were filtered to those whose own text supports their code, so numbers measure the recipe, not EDGAR metadata quality. Source does not demonstrate this on flat (non-hierarchical) taxonomies `[inference: the fallback trick depends on a parent level existing]`.

## Worked example(s)
Dataset: `filings.jsonl`, **60 annual reports (10-K)**, each trimmed to Item 1 "Business", spanning **1993-2024**, **700 to 2,200 words** (average **1,438**). Each carries the filer's SIC code and an EDGAR accession number. Example: `1389870_2008` (accession 0001079974-09-000155), filer's code 6163 loan brokers.

Confident answers (confidence 1.00): 310158_1996 -> group 28 chemicals & allied products (a pharmaceutical maker); 33416_1998 -> group 63 life insurance; accident & health insurance (a life insurer); 352541_1996 -> group 49 electric, gas & sanitary services (a utility). All three are holding companies on paper but each has one dominant business the filing names outright.

Unsure answers:

| filing | confidence | model's group | reported as |
|---|---|---|---|
| 1372167_2013 | 0.22 | 38 (search, detection, navigation, guidance, aeronautical) | division manufacturing |
| 1398633_2009 | 0.23 | 50 wholesale-durable goods | division wholesale trade |
| 46653_1999 | 0.29 | 87 services-engineering, accounting, research, management | division services |

Why hard (readable in the text): two are development-stage companies describing a business they intend to start (Nevaeh "intends to operate as a software developer"; Barricode "organized to enter into the computer security software industry"); the third had two segments and sold one weeks before filing.

## Numbers & limits

Scoring: gold = the filer's code truncated to 2 digits. Sure -> correct if label == gold group. Unsure -> correct if label == the division of gold group.

| Policy | Result |
|---|---|
| Force a group every time | **39/60** right (65%) |
| ...of the **30** it was sure about (confidence >= 0.9) | **27/30** (90%) |
| ...of the **30** it was not (< 0.9) | **12/30** (40%) |
| Report the group when sure, division when unsure | **48/60** useful answers (80%) |
| Unsure half reported as division | 40% -> **70%** (21/30) `[21 = 48-27, derived]` |

So a 0.9 cutoff splits the 60 filings exactly in half (30/30). Other numbers: 444 codes, 75 groups, 10 divisions, 42/75 umbrella titles, <=8 industries listed per option, ~240-option Choice ceiling, confidence cutoff 0.9, model `jev-1.12`, run 2026-08-12, 1 request per document. No latency or cost numbers given in this cookbook.

Setup: `pip install ipython matplotlib 'cooksafe>=0.2.0,<0.3.0'`; set `TYPESAFE_API_KEY`; `json_cache.json` ships with the cookbook so re-render replays published numbers; delete to rerun live. Client timeout 120 s.

## Gotchas
- 0.9 is the chosen cutoff, not derived in the source (a single operating point on 60 documents; no sweep reported). Tune it for your coverage/precision tradeoff `[inference]`.
- Sample is small (60) and pre-filtered for label/text agreement; the gold label is self-reported and can be stale.
- Do not rely on the winner's raw probability as a trust signal; use `confidence`.
- Group descriptions must be written from member industries when umbrella titles are missing (33 of 75 have none).
- A coarse division may be too vague to act on; route those to a person.

## Related
[[choice]] · [[confidence]] · [[score]] · [[confidence-gated-routing]] · [[cb-hierarchical-classification]] · [[cb-sde-cascade]] · [[cb-structure-recovery]] · [[patterns-overview]] · [[cookbooks-overview]] · [[topic-calibration]] · [[topic-classification]] · [[topic-routing]]
