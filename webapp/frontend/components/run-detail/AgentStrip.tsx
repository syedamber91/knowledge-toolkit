import { Run } from "@/lib/types";

const AGENT_META: Record<string, { color: string; label: string }> = {
  vutr:            { color: "var(--blue)",  label: "vutr" },
  lucsystemdesign: { color: "var(--teal)",  label: "luc" },
  "ben-dicken":    { color: "var(--blue)",  label: "ben" },
  sdcourse:        { color: "var(--blue)",  label: "sdc" },
  justin:          { color: "var(--teal)",  label: "justin" },
  alex:            { color: "var(--amber)", label: "alex" },
};

interface Props { run: Run }

export default function AgentStrip({ run }: Props) {
  const agents = [
    ...run.examiners,
    "justin",
    "alex",
  ];
  const isJoint = run.examiners.length > 1;

  return (
    <div className="flex gap-3 overflow-x-auto pb-1">
      {isJoint ? (
        <div className="flex-shrink-0 w-56 bg-white border border-[var(--border)] rounded-lg p-3 relative overflow-hidden">
          <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-[var(--blue)]" />
          <div className="flex items-center gap-1 mb-2 pl-2">
            {run.examiners.map((e) => {
              const m = AGENT_META[e] ?? { color: "var(--gray-50)", label: e };
              return <span key={e} className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: m.color }} />;
            })}
            <span className="text-[11px] font-semibold text-[var(--gray-10)] ml-1">{run.examiners.map((e) => AGENT_META[e]?.label ?? e).join(" + ")}</span>
          </div>
          <div className="text-[10px] text-[var(--gray-50)] pl-2">Scoring Ch {run.current_pass} · joint</div>
          <div className="flex items-center gap-2 mt-2 pl-2">
            <span className="text-[10px] font-medium text-[var(--green)]">running</span>
            <span className="text-[10px] text-[var(--gray-70)] ml-auto">joint tok</span>
          </div>
        </div>
      ) : (
        run.examiners.map((e) => {
          const m = AGENT_META[e] ?? { color: "var(--gray-50)", label: e };
          return (
            <AgentCard key={e} color={m.color} label={m.label} task={`Scoring · pass ${run.current_pass}`} status="running" tokens="14.2k" />
          );
        })
      )}
      <AgentCard color="var(--teal)" label="justin" task={`Answering pass ${run.current_pass} Qs`} status="queued" tokens="22.1k" />
      <AgentCard color="var(--amber)" label="alex" task="Clarity audit" status="queued" tokens="6.8k" />
    </div>
  );
}

function AgentCard({ color, label, task, status, tokens }: {
  color: string; label: string; task: string; status: "running" | "queued"; tokens: string
}) {
  return (
    <div className="flex-shrink-0 w-48 bg-white border border-[var(--border)] rounded-lg p-3 relative overflow-hidden">
      <div className="absolute left-0 top-0 bottom-0 w-0.5" style={{ backgroundColor: color }} />
      <div className="flex items-center gap-2 mb-2 pl-2">
        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
        <span className="text-[11px] font-semibold text-[var(--gray-10)]">{label}</span>
      </div>
      <div className="text-[10px] text-[var(--gray-50)] pl-2">{task}</div>
      <div className="flex items-center gap-2 mt-2 pl-2">
        <span className={`text-[10px] font-medium ${status === "running" ? "text-[var(--green)]" : "text-[var(--gray-70)]"}`}>{status}</span>
        <span className="text-[10px] text-[var(--gray-70)] ml-auto">{tokens} tok</span>
      </div>
    </div>
  );
}
