import { Run, Chapter } from "@/lib/types";

interface Props { run: Run }

function ChapterCell({ chapter, passNum, examiners }: { chapter: Chapter; passNum: number; examiners: string[] }) {
  const latest = chapter.passes.find((p) => p.pass_num === passNum) ?? chapter.passes.at(-1);
  const isJoint = examiners.length > 1;

  const dotColors: Record<string, string> = {
    vutr: "var(--blue)", lucsystemdesign: "var(--teal)",
    "ben-dicken": "var(--blue)", sdcourse: "var(--blue)",
  };

  return (
    <div className="bg-white border border-[var(--border)] rounded-lg p-3 flex flex-col gap-1">
      <div className="text-[11px] font-semibold text-[var(--gray-50)]">Ch {chapter.index + 1}</div>
      {latest ? (
        <>
          {isJoint && (
            <div className="flex gap-1">
              {examiners.map((e) => <span key={e} className="w-2 h-2 rounded-full" style={{ backgroundColor: dotColors[e] ?? "var(--blue)" }} />)}
            </div>
          )}
          <div className="text-[20px] font-semibold text-[var(--gray-10)] leading-tight">
            {latest.acc_score?.toFixed(1)} / {latest.cov_score?.toFixed(1)}
          </div>
          <div className="text-[9px] text-[var(--gray-50)]">acc / cov</div>
          <div className="border-t border-[var(--border)] my-1" />
          <div className="flex items-center gap-2">
            <span className="text-[8px] font-medium px-1.5 py-0.5 rounded bg-[var(--amber-bg)] text-[var(--amber-dk)] border border-[var(--amber)]">alex</span>
            <span className="text-[13px] font-semibold text-[var(--amber-dk)]">{latest.alex_score?.toFixed(1) ?? "—"}</span>
          </div>
          {(() => {
            const pass = (latest.acc_score ?? 0) >= 9.0 && (latest.cov_score ?? 0) >= 9.0 && (latest.alex_score ?? 0) >= 9.0;
            return (
              <div className={`text-[10px] font-semibold mt-1 ${pass ? "text-[var(--green)]" : "text-[var(--red)]"}`}>
                {pass ? "all ✓" : "below threshold"}
              </div>
            );
          })()}
        </>
      ) : (
        <div className="text-[13px] text-[var(--gray-70)] mt-2">queued</div>
      )}
    </div>
  );
}

export default function ScoreGrid({ run }: Props) {
  return (
    <div>
      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide mb-2">
        Chapter Scores · Pass {run.current_pass}
      </div>
      <div className="grid grid-cols-5 gap-3">
        {run.chapters.map((ch) => (
          <ChapterCell key={ch.id} chapter={ch} passNum={run.current_pass} examiners={run.examiners} />
        ))}
      </div>
    </div>
  );
}
