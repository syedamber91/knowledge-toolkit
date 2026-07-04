"use client";
import { useRouter } from "next/navigation";
import { Run } from "@/lib/types";

interface Props { runs: Run[] }

function StatusDot({ status }: { status: Run["status"] }) {
  const color = status === "done" ? "var(--green)" : status === "stalled" ? "var(--red)" : "var(--amber)";
  return <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />;
}

function StagePill({ stage }: { stage: Run["current_stage"] }) {
  const map: Record<string, { label: string; color: string }> = {
    ingestion:    { label: "Ingestion",    color: "var(--teal)" },
    generation:   { label: "Generating",  color: "var(--teal)" },
    verification: { label: "Verification",color: "var(--blue)" },
    "sign-off":   { label: "Sign-off",    color: "var(--amber-dk)" },
    delivery:     { label: "Delivery",    color: "var(--green)" },
  };
  const { label, color } = map[stage] ?? { label: stage, color: "var(--gray-50)" };
  return (
    <span className="text-[11px] font-medium px-2.5 py-1 rounded-full border"
      style={{ color, borderColor: color, backgroundColor: color + "18" }}>
      {label}
    </span>
  );
}

function ScoreBars({ chapters }: { chapters: Run["chapters"] }) {
  if (!chapters.length) return <span className="text-[var(--gray-90)] text-xs">—</span>;
  const latest = chapters.map((ch) => ch.passes.at(-1));
  const dims = [
    { key: "acc_score" as const, color: "var(--blue)" },
    { key: "cov_score" as const, color: "var(--green)" },
    { key: "alex_score" as const, color: "var(--amber)" },
  ];
  const avg = (key: "acc_score" | "cov_score" | "alex_score") => {
    const vals = latest.filter((p) => p != null && p[key] != null).map((p) => p![key] as number);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  };
  return (
    <div className="flex flex-col gap-1 w-24">
      {dims.map((d) => {
        const v = avg(d.key);
        const pass = v >= 9.0;
        return (
          <div key={d.key} className="h-1 bg-[var(--gray-95)] rounded-full overflow-hidden">
            <div className="h-full rounded-full" style={{
              width: `${Math.round(v * 10)}%`,
              backgroundColor: pass ? d.color : "var(--red)",
            }} />
          </div>
        );
      })}
    </div>
  );
}

const HEADERS = ["", "Pack", "Stage", "Score", "Passes", "Started"];

export default function RunListTable({ runs }: Props) {
  const router = useRouter();
  return (
    <div className="bg-white border border-[var(--border)] rounded-lg overflow-hidden">
      <div className="grid grid-cols-[32px_1fr_140px_110px_70px_160px] px-4 py-2 bg-[var(--gray-95)] text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide">
        {HEADERS.map((h) => <div key={h}>{h}</div>)}
      </div>
      {runs.map((run, i) => (
        <div key={run.id}
          onClick={() => router.push(`/runs/${run.id}`)}
          className={`grid grid-cols-[32px_1fr_140px_110px_70px_160px] px-4 py-3.5 items-center border-t border-[var(--border)] cursor-pointer hover:bg-[var(--gray-97)] transition-colors ${i % 2 === 0 ? "bg-white" : "bg-[var(--gray-97)]"}`}>
          <div><StatusDot status={run.status} /></div>
          <div className="text-[13px] font-medium text-[var(--gray-10)] truncate pr-4">{run.title}</div>
          <div><StagePill stage={run.current_stage} /></div>
          <div><ScoreBars chapters={run.chapters} /></div>
          <div className="text-[13px] text-[var(--gray-30)]">{run.current_pass}</div>
          <div className="text-[12px] text-[var(--gray-50)]">
            {new Date(run.started_at).toLocaleDateString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
          </div>
        </div>
      ))}
      {runs.length === 0 && (
        <div className="px-4 py-8 text-center text-[var(--gray-70)] text-sm">No runs match this filter</div>
      )}
    </div>
  );
}
