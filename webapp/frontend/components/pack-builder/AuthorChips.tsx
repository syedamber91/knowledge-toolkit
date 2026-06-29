"use client";

const AUTHORS = [
  { handle: "vutr",            posts: 47 },
  { handle: "lucsystemdesign", posts: 31 },
  { handle: "ben-dicken",      posts: 18 },
  { handle: "sdcourse",        posts: 22 },
];

interface Props { selected: string[]; onChange: (s: string[]) => void }

export default function AuthorChips({ selected, onChange }: Props) {
  const toggle = (h: string) =>
    onChange(selected.includes(h) ? selected.filter((x) => x !== h) : [...selected, h]);

  return (
    <div>
      <label className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide block mb-2">Authors</label>
      <div className="flex flex-wrap gap-2">
        {AUTHORS.map((a) => {
          const active = selected.includes(a.handle);
          return (
            <button key={a.handle} onClick={() => toggle(a.handle)}
              className={`px-3 py-1.5 rounded-full border text-left transition-colors ${
                active ? "bg-[var(--blue-bg)] border-[var(--blue)]" : "bg-white border-[var(--border)]"
              }`}>
              <div className={`text-[12px] font-medium ${active ? "text-[var(--blue)]" : "text-[var(--gray-50)]"}`}>{a.handle}</div>
              <div className={`text-[9px] ${active ? "text-[var(--blue)]" : "text-[var(--gray-70)]"}`}>{a.posts} posts</div>
            </button>
          );
        })}
      </div>
      {selected.length > 1 && (
        <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full bg-[var(--blue-bg)] text-[var(--blue)] text-[11px] font-medium">
          Joint mode · {selected.length} authors active
        </div>
      )}
    </div>
  );
}
