"""Orchestrates the senses (screener) + the framework layer into one briefing.

Deliberately does NOT write the verdict. Both the Venus Pipes and KEI
Industries experiments showed the reasoning -- picking the right framework,
connecting it to the specific numbers, weighing the risk -- is where the
actual value is, and that's a judgment step for a human or an LLM call, not
something to freeze into a template. This module automates only the
mechanical part: fetch what's live, surface which frameworks apply, and
assemble both into one document that reasoning step can start from instead
of a blank page.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

from soic_senses.framework_router import Framework, load_frameworks, match_frameworks
from soic_senses.screener_client import fetch_screener_ratios
from soic_senses.sector_router import Sector, load_sectors, match_sectors


@dataclass
class Briefing:
    symbol: str
    keywords: List[str]
    live_ratios: Optional[Dict[str, object]] = None
    data_error: Optional[str] = None
    frameworks: List[Framework] = field(default_factory=list)
    sectors: List[Sector] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# Decision Briefing — {self.symbol}", ""]

        lines.append("## Live Data (screener.in)")
        if self.data_error is not None:
            lines.append(f"**FETCH FAILED:** {self.data_error}")
            lines.append(
                "No live numbers are available below -- do not substitute a "
                "wiki value or an estimate; re-fetch or source manually before "
                "using any framework that needs a number."
            )
        elif self.live_ratios:
            for label, value in self.live_ratios.items():
                lines.append(f"- **{label}:** {value}")
        else:
            lines.append("(no ratios returned)")
        lines.append("")

        lines.append("## Applicable Frameworks")
        if self.frameworks:
            for fw in self.frameworks:
                lines.append(f"### {fw.id}. {fw.title}")
                lines.append(fw.body)
                lines.append("")
        else:
            lines.append("(no framework matched the given keywords)")

        lines.append("## Applicable Sector Context")
        if self.sectors:
            for sector in self.sectors:
                lines.append(f"### {sector.title}")
                lines.append(f"NotebookLM notebook: `{sector.notebook_id}`")
                lines.append("")
        else:
            lines.append("(no sector notebook matched the given keywords)")

        return "\n".join(lines)


def build_briefing(
    symbol: str,
    keywords: List[str],
    frameworks_path: Union[str, Path],
    sector_registry_path: Optional[Union[str, Path]] = None,
) -> Briefing:
    """Fetch live ratios + match frameworks + match sector notebooks for one
    company.

    A screener fetch failure is recorded on the briefing (data_error), never
    raised past this point -- the caller still gets the framework matches
    even when the data layer is down, and to_markdown() surfaces the failure
    loudly rather than silently proceeding with no numbers.

    sector_registry_path is optional (default None -> skip sector matching
    entirely, so existing callers that don't pass it are unaffected). When
    given, sectors are matched the same way frameworks are: growing
    configs/sector_notebooks.yaml is the only wiring a new sector needs --
    this function never changes again as more sectors are registered.
    """
    briefing = Briefing(symbol=symbol, keywords=keywords)

    try:
        briefing.live_ratios = fetch_screener_ratios(symbol)
    except Exception as exc:  # noqa: BLE001 - deliberately broad: record, never crash the briefing
        briefing.data_error = str(exc)

    frameworks = load_frameworks(frameworks_path)
    briefing.frameworks = match_frameworks(frameworks, keywords)

    if sector_registry_path is not None:
        sectors = load_sectors(sector_registry_path)
        briefing.sectors = match_sectors(sectors, keywords)

    return briefing
