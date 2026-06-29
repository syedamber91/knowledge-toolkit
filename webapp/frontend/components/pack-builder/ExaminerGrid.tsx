"use client";

const EXAMINERS = [
  { id: "vutr",            label: "vutr",            color: "var(--blue)" },
  { id: "lucsystemdesign", label: "lucsystemdesign", color: "var(--teal)" },
  { id: "sdcourse",        label: "sdcourse",        color: "var(--gray-50)" },
  { id: "ben-dicken",      label: "ben-dicken",      color: "var(--gray-50)" },
];

interface Props { selected: string[]; onChange: (s: string[]) => void }

export default function ExaminerGrid({ selected, onChange }: Props) {
  const toggle = (id: string) =>
    onChange(selected.includes(id) ? selected.filter((x) => x !== id) : [...selected, id]);
  return (
    <div>
      <label className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide block mb-2">Examiners</label>
      <div className="flex flex-wrap gap-2 mb-2">
        {EXAMINERS.map((e) => {
          const active = selected.includes(e.id);
          return (
            <button key={e.id} onClick={() => toggle(e.id)}
              className={`flex items-center gap-2 px-3 py-2.5 rounded-lg border transition-colors ${
                active ? "bg-[var(--blue-bg)] border-[var(--blue)]" : "bg-white border-[var(--border)]"
              }`}>
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: e.color }} />
              <span className={`text-[11px] font-medium ${active ? "text-[var(--blue)]" : "text-[var(--gray-50)]"}`}>{e.label}</span>
            </button>
          );
        })}
      </div>
      {selected.length > 1 && (
        <div className="inline-flex items-center px-3 py-1 rounded-full bg-[var(--blue-bg)] text-[var(--blue)] text-[11px] font-medium">
          Joint mode · 5 questions each · in parallel
        </div>
      )}
      <p className="text-[10px] text-[var(--gray-70)] mt-2">
        Justin Sung (pedagogy) and Alex Chen (clarity) always included automatically.
      </p>
    </div>
  );
}
