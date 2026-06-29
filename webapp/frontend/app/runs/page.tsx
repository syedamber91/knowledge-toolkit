"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Run, StatsOut } from "@/lib/types";
import StatsRow from "@/components/runs/StatsRow";
import FilterPills from "@/components/runs/FilterPills";
import RunListTable from "@/components/runs/RunListTable";

type Filter = "All" | "Running" | "Done" | "Failed";

export default function RunsPage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [stats, setStats] = useState<StatsOut | null>(null);
  const [filter, setFilter] = useState<Filter>("All");

  useEffect(() => {
    api.runs.list().then((d) => { setRuns(d.runs); setStats(d.stats); });
  }, []);

  const filtered = runs.filter((r) => {
    if (filter === "All") return true;
    if (filter === "Running") return r.status === "running";
    if (filter === "Done") return r.status === "done";
    if (filter === "Failed") return r.status === "stalled";
    return true;
  });

  return (
    <div className="max-w-[1392px] mx-auto px-6 py-6">
      <h1 className="text-[22px] font-semibold mb-6">Runs</h1>
      {stats && <StatsRow stats={stats} />}
      <FilterPills active={filter} onChange={setFilter} />
      <RunListTable runs={filtered} />
    </div>
  );
}
