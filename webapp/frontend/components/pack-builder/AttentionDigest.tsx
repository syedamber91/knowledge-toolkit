import { Topic } from "@/lib/types";

interface Props { topics: Topic[] }

export default function AttentionDigest({ topics }: Props) {
  const flagged = topics.filter((t) => t.status === "needsUpdate");
  if (!flagged.length) return null;
  return (
    <div className="border border-[var(--amber)] bg-[var(--amber-bg)] rounded-lg p-4">
      <div className="text-[11px] font-semibold text-[var(--amber-dk)] mb-2">Topics needing attention</div>
      {flagged.map((t) => (
        <div key={t.id} className="text-[11px] text-[var(--amber-dk)] mb-1">
          <span className="font-medium">{t.name}</span>
          {" — "}+{(t.post_count ?? 0) - (t.post_count_at_ship ?? 0)} new posts since ship.{" "}
          <span className="text-[var(--gray-50)]">Re-extraction recommended.</span>
        </div>
      ))}
    </div>
  );
}
