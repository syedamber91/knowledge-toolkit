"use client";
import { Run } from "@/lib/types";

const STAGES: { key: Run["current_stage"]; label: string }[] = [
  { key: "ingestion",    label: "Content ingestion" },
  { key: "generation",  label: "Pack generation" },
  { key: "verification",label: "Verification loop" },
  { key: "sign-off",    label: "Sign-off gate" },
  { key: "delivery",    label: "Delivery" },
];

const STAGE_ORDER = ["ingestion","generation","verification","sign-off","delivery"];

function stageSub(key: string, run: Run): string {
  if (key === "verification") return `Pass ${run.current_pass} · Ch 1–5`;
  if (key === "sign-off") return "Awaiting all agents";
  if (key === "delivery") return run.status === "done" ? "Shipped" : "Not started";
  if (key === "ingestion") return "Vault synced";
  if (key === "generation") return "PDF ready";
  return "";
}

interface Props { run: Run }

export default function Sidebar({ run }: Props) {
  const currentIdx = STAGE_ORDER.indexOf(run.current_stage);

  return (
    <aside className="w-52 flex-shrink-0 bg-white border-r border-[var(--border)] h-full pt-4 pb-6 px-4">
      <div className="mb-4">
        <div className="text-[13px] font-semibold text-[var(--gray-10)] truncate">{run.authors.join(" · ")}</div>
        <div className="text-[11px] text-[var(--gray-50)]">{run.topic} · Pass {run.current_pass}</div>
        <div className="flex gap-1.5 mt-2 flex-wrap">
          {run.authors.map((a) => (
            <span key={a} className="text-[9px] font-medium px-1.5 py-0.5 rounded border border-[var(--blue)] bg-[var(--blue-bg)] text-[var(--blue)]">{a}</span>
          ))}
          <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded border ${
            run.status === "running" ? "border-[var(--amber)] bg-[var(--amber-bg)] text-[var(--amber-dk)]"
            : run.status === "done" ? "border-[var(--green)] bg-[var(--green-bg)] text-[var(--green)]"
            : "border-[var(--red)] bg-[var(--red-bg)] text-[var(--red)]"}`}>
            {run.status}
          </span>
        </div>
      </div>

      <div className="space-y-0">
        {STAGES.map((st, i) => {
          const stIdx = STAGE_ORDER.indexOf(st.key);
          const isDone   = stIdx < currentIdx || (stIdx === currentIdx && run.status === "done");
          const isActive = stIdx === currentIdx && run.status !== "done";

          return (
            <div key={st.key} className="relative">
              {i > 0 && (
                <div className={`absolute left-[15px] -top-3 w-0.5 h-3 ${isDone ? "bg-[var(--green)]" : "bg-[var(--gray-90)]"}`} />
              )}
              {isActive && <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-[var(--blue)]" />}
              <div className={`flex items-start gap-3 py-3 pl-2 ${isActive ? "pl-3" : ""}`}>
                <div className={`w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center text-[11px] font-bold mt-0.5 ${
                  isDone   ? "bg-[var(--green)] text-white" :
                  isActive ? "border-2 border-[var(--blue)] bg-[var(--blue-bg)] text-[var(--blue)]" :
                             "border-2 border-[var(--gray-90)] bg-[var(--gray-95)] text-[var(--gray-70)]"
                }`}>
                  {isDone ? "✓" : isActive ? "●" : i + 1}
                </div>
                <div>
                  <div className={`text-[12px] font-medium leading-tight ${isDone ? "text-[var(--gray-30)]" : isActive ? "text-[var(--blue)] font-semibold" : "text-[var(--gray-70)]"}`}>
                    {st.label}
                  </div>
                  <div className="text-[10px] text-[var(--gray-50)]">{stageSub(st.key, run)}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
