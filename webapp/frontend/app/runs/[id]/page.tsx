"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Run } from "@/lib/types";
import Sidebar from "@/components/run-detail/Sidebar";
import AgentStrip from "@/components/run-detail/AgentStrip";
import ScoreGrid from "@/components/run-detail/ScoreGrid";

export default function RunDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [run, setRun] = useState<Run | null>(null);

  useEffect(() => {
    api.runs.get(Number(id)).then(setRun);
  }, [id]);

  if (!run) return <div className="p-8 text-[var(--gray-50)]">Loading…</div>;

  if (run.current_stage === "sign-off" || run.status === "done") {
    // Sign-off + Delivery view — added in Task 8
    return <div className="p-8 text-[var(--gray-50)]">Sign-off screen coming in Task 8</div>;
  }

  return (
    <div className="flex h-[calc(100vh-56px)]">
      <Sidebar run={run} />
      <div className="flex-1 overflow-y-auto">
        {/* Top bar */}
        <div className="sticky top-0 bg-white border-b border-[var(--border)] px-6 py-3.5 flex items-center justify-between z-10">
          <span className="text-[14px] font-semibold text-[var(--gray-10)]">
            Verification loop · Pass {run.current_pass}
          </span>
          {run.examiners.length > 1 && (
            <span className="text-[10px] font-medium px-2.5 py-1 rounded-full bg-[var(--blue-bg)] text-[var(--blue)]">
              Joint · {run.examiners.length + 2} agents active
            </span>
          )}
        </div>

        <div className="px-6 py-5 space-y-6">
          <AgentStrip run={run} />
          <ScoreGrid run={run} />
          {/* GapsList + LiveLog added in Task 7 */}
        </div>
      </div>
    </div>
  );
}
