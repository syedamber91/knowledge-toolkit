"use client";
const FILTERS = ["All", "Running", "Done", "Failed"] as const;
type Filter = typeof FILTERS[number];

interface Props { active: Filter; onChange: (f: Filter) => void }

export default function FilterPills({ active, onChange }: Props) {
  return (
    <div className="flex gap-2 mb-4">
      {FILTERS.map((f) => (
        <button key={f} onClick={() => onChange(f)}
          className={`px-3.5 py-1.5 rounded-full text-[12px] font-medium border transition-colors ${
            f === active
              ? "bg-[var(--blue)] text-white border-[var(--blue)]"
              : "bg-white text-[var(--gray-30)] border-[var(--border)] hover:border-[var(--gray-70)]"
          }`}>
          {f}
        </button>
      ))}
    </div>
  );
}
