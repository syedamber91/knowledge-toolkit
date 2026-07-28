"""Phase 0 + Phase 1: route the 459 SOIC concept notes against POLYCAB.

Phase 0 pins the subject's ATTRIBUTES (not just its name); Phase 1 admits or
excludes each concept note against those attributes. Admission is per-NOTE,
never per-topic -- the dump proved topic labels mislead badly (9 of the 13
notes under `moated-companies-ai-value-chain` are generic moat theory that
applies to any company, while `premiumisation` is mostly other industries'
case studies with a few genuinely FMEG-relevant notes buried in it).

Every exclusion carries a reason. A silent drop is indistinguishable from an
oversight -- the failure mode that let a loan-to-value lending rule (F12)
score a cables company in the previous framework-based run.
"""
from __future__ import annotations

import json
from collections import Counter

# ---------------------------------------------------------------------------
# PHASE 0 -- subject attributes, from live screener.in (2026-07-28)
# ---------------------------------------------------------------------------
SUBJECT = {
    "symbol": "POLYCAB",
    "cmp": 9122.0, "market_cap_cr": 137429.0, "pe": 48.0,
    "roce": 33.2, "roe": 23.0, "debt_to_equity": 0.02,
    "sales_cagr_3y": 27.0, "profit_cagr_3y": 28.0,
    "q_sales_yoy": 39.01, "q_pat_yoy": 32.83,
    "npm": 9.38, "asset_turnover": 1.41,
    "business": "Cables & Wires (~85% rev) + FMEG (fans/lights/switches) + EPC",
}

# The gate is ATTRIBUTE-based, not name-based. A note is admissible only if
# the mechanism it teaches can act on at least one TRUE attribute here.
ATTRS_TRUE = {
    "b2b_industrial_manufacturer", "b2c_consumer_durable_brand",
    "commodity_rm_input",          # copper/aluminium -> pass-through mechanics
    "infra_capex_linked_demand", "distribution_led_moat",
    "converter_not_producer",      # buys metal, sells engineered product
    "order_book_partial",          # EPC + institutional, not the main engine
    "asset_light_ish", "debt_free",
}
ATTRS_FALSE = {
    "lending_book", "platform_network_effect", "regulated_pharma",
    "natural_monopoly_asset", "commodity_producer", "turnaround_situation",
    "low_float", "cyclical_deep_trough", "capital_markets_intermediary",
}

# ---------------------------------------------------------------------------
# PHASE 1 -- routing
# ---------------------------------------------------------------------------

# Tier A: universal method. Course-level curriculum (L2/L3/L4/L5/Crash Course)
# plus the cross-sector meta topic. These teach HOW to analyse any company.
TIER_A_TOPICS = {
    "module-1-the-need-for-compounding", "module-2-why-equity-analysis",
    "module-3-understanding-financial-statements", "module-4-forensic-analysis",
    "module-5-ratio-analysis", "module-6-how-to-research-and-find-information",
    "module-7-importance-of-industry-structures",
    "module-8-all-about-competitive-advantages", "updated-soic-screener-sheet",
    "how-to-value-a-company-and-portfolio-creation",
    "technical-analysis-masterclass", "additional-classes",
    "framework-for-buying-selling-a-stock", "how-to-screen-and-filter-epic-stocks",
    "tvgp-framework-and-checklist-course",
    "class-1-behavioral-finance-how-to-conquer-yourself", "class-2-to-class-9",
    "mastering-fundamental-analysis", "sector-analysis-framework",
    "how-to-navigate-and-take-best-out-of-soic-membership",
}

# Tier B: cross-sector METHOD that happens to live inside an L6 sector module.
# Admitted on the note's own mechanism, not its topic label.
TIER_B_NOTES = {
    # generic moat theory mislabelled under an AI-sector topic
    "moat-frameworks-and-definitions", "switching-cost-and-customer-lockin-moats",
    "scale-advantage-and-lowest-cost-operator-moats",
    "network-effects-and-platform-monetization-moats",
    "proprietary-asset-and-location-moats", "temporary-and-continuously-rebuilt-moats",
    "moat-quality-checklist-and-investing-heuristics", "moat-erosion-and-ai-disruption-context",
    "sector-cyclicality-without-durable-moats",
    "learning-curve-taste-brand-and-license-moats",
    # scalability / value-chain / turnaround METHOD
    "acquisition-led-growth-and-market-consolidation", "practical-screening-and-valuation-metrics",
    "regulatory-headwinds-and-tailwinds", "scaling-via-capacity-expansion-and-premiumization",
    "the-dynamics-and-risks-of-order-book-driven-growth", "the-four-phases-of-thematic-investing",
    "value-chain-analysis-framework", "hard-asset-stocks-and-natural-monopolies",
    "framework-for-business-turnarounds", "promoter-and-management-stability",
    "turnaround-risk-assessment", "tvgp-framework-applied-to-turnarounds",
    # market-signals METHOD (not dated sector commentary)
    "forensic-accounting-and-spotting-financial-red-flags",
    "bottom-up-stock-screening-frameworks", "screening-for-fundamental-breakouts-margin-expansion",
    "watchlist-creation-and-fundamental-momentum-frameworks", "the-j-curve-hyper-growth-mental-model",
    "the-tvgp-and-new-investing-frameworks", "evaluating-corporate-actions-smart-money-moves",
    "evaluating-demergers-as-value-creation-catalysts", "artificial-intelligence-in-investment-research",
    "using-ai-to-map-value-chains-and-generate-equity-research",
    "global-stock-screening-and-research-tools", "custom-indexing-sectoral-stage-analysis",
    "small-cap-liquidity-and-reflexivity-dynamics",
    "strategic-asset-allocation-and-withdrawal-planning", "portfolio-allocation-strategies",
    "factor-investing-and-mutual-fund-selection-frameworks",
    "m-a-and-capital-allocation-blueprint", "order-book-driven-businesses",
    "deep-value-and-sideways-market-survival", "the-tvgp-investment-framework",
    # market/breadth TIMING context -- can cap a verdict, never promote it
    "macroeconomic-indicators-market-breadth-analysis", "market-breadth-and-sector-rotation-analysis",
    "technical-screening-and-market-breadth-indicators", "macro-corrections-and-time-correction-cycles",
    "indian-market-cycles-sectoral-rotation-and-capex-themes",
    "emerging-sector-rotations-and-disruptive-themes", "geopolitical-macro-shocks-and-market-indicators",
    # --- recovered by the exclusion audit: generic method notes that a topic
    # label had dragged into an excluded sector module. The audit flagged every
    # D-excluded note whose tags were PURELY method tags; these four survived
    # review, the other two were confirmed correct exclusions (see below).
    "fundamentals-of-free-float-and-shareholder-types",   # shareholder-type analysis, any company
    "general-market-timing-heuristics",                   # generic timing, filed under aroma chemicals
    "portfolio-construction-and-risk-heuristics",         # generic sizing, filed under software
    "practical-frameworks-for-evaluating-valuations-fluorine",  # valuation method; fluorine only as worked example
}

# Tier C: sector-ADJACENT. Either a genuine demand driver for cables, or a
# structurally analogous business shape. Each carries its own justification --
# these are the calls most worth challenging.
TIER_C_NOTES = {
    "sector-case-studies-winding-wires-and-auto-ancillary-premiumization":
        "winding wires = adjacent Polycab product line; closest direct-industry note in the vault",
    "ai-power-demand-and-transmission-value-chains":
        "data-centre + grid power demand is a direct cable order driver",
    "renewable-energy-and-power-transmission-super-cycle":
        "transmission capex is a direct cable demand driver",
    "data-center-and-ai-infrastructure-ecosystem":
        "data-centre build-out consumes cabling; demand-side driver",
    "ai-data-center-infrastructure-and-supply-shortages":
        "same demand driver, supply-shortage framing",
    "ai-and-data-center-proxy-beneficiaries":
        "explicitly about proxy beneficiaries of DC capex -- Polycab is one",
    "global-ai-capex-indian-data-center-proxies":
        "Indian DC capex proxies -- direct read-across",
    "capital-goods-mental-models-and-macro-cycles":
        "Polycab's institutional demand rides the capital-goods cycle",
    "the-razor-blade-model-in-fast-moving-industrial-goods":
        "replacement/consumable demand mechanics apply to wires + FMEG",
    "precision-engineering-and-supply-side-dominance":
        "supply-side dominance mechanics for a B2B industrial manufacturer",
    "supply-chain-choke-points-and-the-manufacturing-regime-shift":
        "China+1 / manufacturing regime shift affects Polycab's export ambition",
    "premiumization-macro-thesis":
        "core premiumisation mechanism -- FMEG mix-shift is Polycab's stated strategy",
    "hvac-appliance-and-specialty-materials":
        "appliance premiumisation = direct FMEG read-across",
    "fmcg-penetration-and-value-trap":
        "penetration-led growth + the value-trap warning applies to FMEG expansion",
    "apparel-brand-tier-premiumization":
        "brand-tier ladder mechanics, transferable to FMEG branding",
    "auto-ancillary-premiumization-trend":
        "content-per-unit premiumisation, structurally similar to wire content growth",
    "auto-ancillary-investing-framework":
        "B2B supplier-to-OEM framework; partial analogue for institutional cables",
    "piping-sector-demand-and-value-chain":
        "B2B industrial, commodity-RM, project-linked -- closest structural analogue",
    "power-and-energy-piping-industry-deep-dive":
        "same analogue, power-capex customer overlap",
    "order-cycle-cyclicality-and-margin-dynamics":
        "order-cycle + margin mechanics for the EPC/institutional slice",
    "barriers-to-entry-and-execution-risks":
        "entry barriers + execution risk in a B2B project business",
    "structural-and-cyclical-drivers-in-packaging":
        "converter economics with commodity RM pass-through -- same shape as cables",
    "profit-pool-margin-analysis":
        "where profit sits in a value chain -- applies to the C&W chain",
    "industry-value-chain-mapping":
        "value-chain mapping method for Polycab's own chain",
}

EXCLUDE_TOPIC_REASONS = {
    "gold-nbfcs-niche-financiers": "lending-book mechanics; Polycab has no loan book (the F12 failure mode)",
    "decoding-indian-banking-space-2": "bank/NBFC ROA-tree mechanics; not applicable",
    "understand-insurance-landscape-simplifying-a-complex-sector": "insurance float/VNB mechanics; not applicable",
    "the-capital-code-capital-market-value-chain": "capital-markets intermediary economics; not applicable",
    "decoding-the-hotel-industry": "occupancy/ARR asset-cycle mechanics; not applicable",
    "detailed-analysis-of-real-estate-sector": "real-estate revenue-recognition + land-bank mechanics; not applicable",
    "soic-hospital-sectoral-webinar-analysis": "hospital bed/occupancy unit economics; not applicable",
    "api-sectoral-analysis": "regulated-pharma API mechanics; not applicable",
    "cdmo-a-multiyear-trend": "CDMO contract/regulatory mechanics; not applicable",
    "understanding-speciality-chemical-sector": "chemistry-complexity moat mechanics; not applicable",
    "aroma-chemicals-and-their-hidden-potential": "specialty-chemical niche mechanics; not applicable",
    "fluorine-industry-megatrend-or-fad": "fluorine value-chain mechanics; not applicable",
    "agrochemicals-where-india-is-winning": "agri-cycle + registration mechanics; not applicable",
    "alcohol-sector": "excise/state-regulation mechanics; not applicable",
    "decode-indian-and-global-watch-industry": "luxury-brand/CPO mechanics; not applicable",
    "lab-grown-diamonds-sector-analysis": "LGD commodity/consumer mechanics; not applicable",
    "uncover-hidden-gems-in-metals-and-mining-sector": "commodity PRODUCER mechanics; Polycab is a converter, not a miner",
    "oil-and-gas-sector-simplified": "upstream/refining mechanics; not applicable",
    "fission-to-alpha-indias-nuclear-energy-sector-decoded": "nuclear tech/policy mechanics; demand read-across already captured via transmission notes",
    "future-of-indian-shipyards-from-defence-to-cargo": "shipbuilding order/defence mechanics; not applicable",
    "drone-and-anti-drone-sector": "defence/B2G order mechanics; not applicable",
    "aerospace-and-precision-engineering": "aero-tier qualification mechanics; supply-side note admitted separately",
    "is-software-making-a-comeback": "software/SaaS economics; not applicable",
    "modern-monopolies-platform-businesses": "platform network-effect economics; Polycab is not a platform",
    "commercial-vehicles": "CV replacement-cycle mechanics; generic cyclicality already covered in Tier A",
    "decode-ev-ecosystem-in-india": "EV powertrain/battery mechanics; cable read-across too weak to admit",
    "masterclass-on-low-float-stocks": "low-float reflexivity; Polycab is a large-cap with normal float",
}

# Confirmed-correct exclusions the audit surfaced, recorded so a re-run does not
# re-litigate them: `taxation-mechanics-for-overseas-and-mutual-fund-portfolios`
# is portfolio tax administration, not company analysis; and
# `valuation-distortion-via-float-cornering` needs a cornered low float, which a
# large-cap with normal free float does not have (attribute `low_float` is FALSE).
NOTE_LEVEL_EXCLUDE_REASONS = {
    "taxation-mechanics-for-overseas-and-mutual-fund-portfolios":
        "portfolio tax administration, not company analysis",
    "valuation-distortion-via-float-cornering":
        "requires a cornered low float; attribute low_float is FALSE for a large-cap",
}


def main() -> None:
    rows = json.load(open("/tmp/concept_index.json"))
    routed = []
    for r in rows:
        slug, topics = r["slug"], r["topics"]
        if slug in TIER_C_NOTES:
            routed.append({**r, "tier": "C-adjacent", "reason": TIER_C_NOTES[slug]})
        elif slug in TIER_B_NOTES:
            routed.append({**r, "tier": "B-method", "reason": "cross-sector method living inside a sector module"})
        elif any(t in TIER_A_TOPICS for t in topics):
            routed.append({**r, "tier": "A-universal", "reason": "core curriculum method (L2-L5 / Crash Course / meta)"})
        else:
            why = NOTE_LEVEL_EXCLUDE_REASONS.get(slug) or next(
                (EXCLUDE_TOPIC_REASONS[t] for t in topics if t in EXCLUDE_TOPIC_REASONS), None)
            routed.append({**r, "tier": "D-excluded",
                           "reason": why or f"sector-specific mechanics ({', '.join(topics)}); no admissible attribute"})

    json.dump(routed, open("/tmp/polycab_routing.json", "w"), indent=1)
    c = Counter(x["tier"] for x in routed)
    print("PHASE 0 -- subject:", SUBJECT["symbol"], "|", SUBJECT["business"])
    print(f"  CMP {SUBJECT['cmp']:,.0f}  P/E {SUBJECT['pe']}  ROCE {SUBJECT['roce']}%  "
          f"ROE {SUBJECT['roe']}%  D/E {SUBJECT['debt_to_equity']}")
    print(f"  attributes TRUE={len(ATTRS_TRUE)}  FALSE(gate-blocking)={len(ATTRS_FALSE)}")
    print()
    print("PHASE 1 -- routing of 459 concept notes")
    for tier in ("A-universal", "B-method", "C-adjacent", "D-excluded"):
        print(f"  {tier:14s} {c[tier]:3d}")
    print(f"  {'ADMITTED':14s} {c['A-universal']+c['B-method']+c['C-adjacent']:3d}")
    assert sum(c.values()) == 459, sum(c.values())


if __name__ == "__main__":
    main()
