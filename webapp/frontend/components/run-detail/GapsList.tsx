import { Run } from "@/lib/types";

const TAG_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  joint: { bg: "var(--blue-bg)",   border: "var(--blue)",    text: "var(--blue)" },
  alex:  { bg: "var(--amber-bg)",  border: "var(--amber)",   text: "var(--amber-dk)" },
};

interface Props { run: Run }

export default function GapsList({ run }: Props) {
  const latestPassNum = run.current_pass;
  const gaps = run.chapters.flatMap((ch) => {
    const pr = ch.passes.find((p) => p.pass_num === latestPassNum) ?? ch.passes.at(-1);
    return (pr?.gaps ?? []).map((g) => ({ ...g, chIndex: ch.index }));
  });

  if (!gaps.length) return null;

  return (
    <div>
      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide mb-2">
        Gaps · Pass {latestPassNum}
      </div>
      <div className="space-y-2">
        {gaps.map((g) => {
          const tagType = g.source_tag.includes("alex") ? "alex" : "joint";
          const style = TAG_COLORS[tagType] ?? TAG_COLORS.joint;
          return (
            <div key={g.id} className="flex items-center gap-3 bg-white border border-[var(--border)] rounded-lg px-4 py-2">
              <span className="text-[9px] font-medium px-2 py-0.5 rounded border flex-shrink-0"
                style={{ backgroundColor: style.bg, borderColor: style.border, color: style.text }}>
                {g.source_tag}
              </span>
              <span className="text-[11px] text-[var(--gray-30)] truncate">{g.description}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
