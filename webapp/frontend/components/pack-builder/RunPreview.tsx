interface Props {
  authors: string[]; topic: string; chapters: string[];
  examiners: string[]; postCount: number;
}

const STEPS = [
  "Content ingestion (vault sync)",
  "PDF generation (headless Chrome)",
  "Verification loop (multi-pass)",
  "Tri-agent sign-off gate",
  "Google Drive + git + PR delivery",
];

export default function RunPreview({ authors, topic, chapters, examiners, postCount }: Props) {
  const pdfName = [...authors, topic.toLowerCase().replace(/ /g, "_")].join("_") + ".pdf";
  const fields = [
    ["Authors",    authors.join(" · ") || "—"],
    ["Topic",      topic || "—"],
    ["Posts",      postCount ? `${postCount} matched` : "—"],
    ["Chapters",   chapters.filter(Boolean).length + " defined"],
    ["Examiners",  examiners.length ? examiners.join(" + ") + (examiners.length > 1 ? " (joint)" : "") : "—"],
    ["Questions",  examiners.length > 1 ? "5 each per chapter" : "5 per chapter"],
    ["Threshold",  "≥ 9.0 acc / cov / clarity"],
    ["Output PDF", pdfName],
    ["Drive",      "My Drive / Learning Packs"],
  ];
  return (
    <div className="bg-white border border-[var(--border)] rounded-lg p-5">
      <div className="text-[12px] font-semibold text-[var(--gray-30)] mb-4">Run Preview</div>
      <div className="space-y-1.5 mb-5">
        {fields.map(([k, v]) => (
          <div key={k} className="flex text-[11px]">
            <span className="w-28 flex-shrink-0 text-[var(--gray-50)]">{k}</span>
            <span className="text-[var(--gray-10)] font-medium truncate">{v}</span>
          </div>
        ))}
      </div>
      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide mb-2">Pipeline Steps</div>
      <div className="space-y-1.5">
        {STEPS.map((s) => (
          <div key={s} className="flex items-center gap-2 text-[12px] text-[var(--gray-30)]">
            <span className="w-4 h-4 rounded bg-[var(--green-bg)] border border-[var(--green)] flex items-center justify-center text-[var(--green)] text-[8px] font-bold flex-shrink-0">✓</span>
            {s}
          </div>
        ))}
      </div>
    </div>
  );
}
