import { StatsOut } from "@/lib/types";

interface Props { stats: StatsOut }

const STATS = [
  { key: "total_runs" as const,          label: "Total runs",          sub: "all time",     color: "var(--blue)" },
  { key: "passed_this_week" as const,    label: "Passed this week",    sub: "last 7 days",  color: "var(--green)" },
  { key: "avg_passes_to_ship" as const,  label: "Avg passes to ship",  sub: "per pack",     color: "var(--gray-30)" },
  { key: "tokens_this_month" as const,   label: "Tokens this month",   sub: "est. cost",    color: "var(--amber-dk)" },
];

function formatValue(key: keyof StatsOut, val: number): string {
  if (key === "tokens_this_month") return (val / 1_000_000).toFixed(1) + "M";
  if (key === "avg_passes_to_ship") return val.toFixed(1);
  return String(val);
}

export default function StatsRow({ stats }: Props) {
  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      {STATS.map((s) => (
        <div key={s.key} className="bg-white border border-[var(--border)] rounded-lg px-5 py-4">
          <div className="text-[26px] font-semibold" style={{ color: s.color }}>
            {formatValue(s.key, stats[s.key])}
          </div>
          <div className="text-[11px] text-[var(--gray-50)] mt-1">{s.label}</div>
          <div className="text-[10px] text-[var(--gray-70)]">{s.sub}</div>
        </div>
      ))}
    </div>
  );
}
