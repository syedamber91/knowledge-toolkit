"use client";

interface Props { chapters: string[]; onChange: (c: string[]) => void }

export default function ChapterFields({ chapters, onChange }: Props) {
  const update = (i: number, v: string) => {
    const next = [...chapters];
    next[i] = v;
    onChange(next);
  };
  return (
    <div>
      <label className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide block mb-2">Chapters</label>
      <div className="space-y-2">
        {chapters.map((ch, i) => (
          <div key={i} className="flex items-center gap-3">
            <span className="text-[10px] font-medium text-[var(--gray-50)] w-10 flex-shrink-0">Ch {i + 1}</span>
            <input value={ch} onChange={(e) => update(i, e.target.value)}
              placeholder={`Chapter ${i + 1} title…`}
              className="flex-1 border border-[var(--border)] rounded-md px-3 py-2 text-[12px] text-[var(--gray-30)] outline-none focus:border-[var(--blue)]" />
          </div>
        ))}
      </div>
    </div>
  );
}
