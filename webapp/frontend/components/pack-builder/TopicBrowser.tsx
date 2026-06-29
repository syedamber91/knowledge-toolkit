"use client";
import { useState } from "react";
import { Topic } from "@/lib/types";

const STATE_STYLES = {
  suggested:   { border: "border-[var(--border)]",  bg: "bg-white",              badge: "text-[var(--gray-50)] border-[var(--gray-90)] bg-[var(--gray-97)]" },
  shipped:     { border: "border-[var(--green)]",   bg: "bg-[var(--green-bg)]",  badge: "text-[var(--green)] border-[var(--green)] bg-white" },
  needsUpdate: { border: "border-[var(--amber)]",   bg: "bg-[var(--amber-bg)]",  badge: "text-[var(--amber-dk)] border-[var(--amber)] bg-white" },
};

interface Props { topics: Topic[]; selected: string; onSelect: (t: string) => void }

export default function TopicBrowser({ topics, selected, onSelect }: Props) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"All" | "Suggested" | "Completed" | "Needs update">("All");

  const FILTER_TABS = ["All", "Suggested", "Completed", "Needs update"] as const;

  const visible = topics.filter((t) => {
    const matchSearch = t.name.toLowerCase().includes(search.toLowerCase());
    const matchFilter =
      filter === "All" ? true :
      filter === "Suggested" ? t.status === "suggested" :
      filter === "Completed" ? t.status === "shipped" :
      t.status === "needsUpdate";
    return matchSearch && matchFilter;
  });

  return (
    <div>
      <label className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide block mb-2">Topic</label>
      <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search topics…"
        className="w-full border border-[var(--border)] rounded-md px-3 py-2 text-[12px] text-[var(--gray-30)] mb-2 outline-none focus:border-[var(--blue)]" />
      <div className="flex gap-1.5 mb-3">
        {FILTER_TABS.map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded-full text-[11px] font-medium border transition-colors ${
              f === filter ? "bg-[var(--blue)] text-white border-[var(--blue)]"
                          : "bg-white text-[var(--gray-50)] border-[var(--border)]"
            }`}>{f}</button>
        ))}
      </div>
      <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
        {visible.map((t) => {
          const s = STATE_STYLES[t.status];
          const isSelected = t.name === selected;
          const badgeLabel = t.status === "shipped" ? "Shipped ✓" : t.status === "needsUpdate" ? "New content" : "Suggested";
          const detail = t.status === "shipped" ? `Shipped · ${t.post_count} posts`
            : t.status === "needsUpdate" ? `+${(t.post_count ?? 0) - (t.post_count_at_ship ?? 0)} new posts since ship`
            : `${t.post_count} posts matched`;
          return (
            <button key={t.id} onClick={() => onSelect(t.name)}
              className={`w-full flex justify-between items-center px-4 py-3 rounded-lg border text-left transition-all ${s.border} ${s.bg} ${isSelected ? "ring-2 ring-[var(--blue)]" : ""}`}>
              <div>
                <div className="text-[13px] font-medium text-[var(--gray-10)]">{t.name}</div>
                <div className="text-[11px] text-[var(--gray-50)]">{detail}</div>
              </div>
              <span className={`text-[10px] font-medium px-2 py-0.5 rounded border ${s.badge}`}>{badgeLabel}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
