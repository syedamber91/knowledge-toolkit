import { SignOff } from "@/lib/types";

const AGENT_META: Record<string, { initials: string; role: string; color: string; bgColor: string }> = {
  vutr:            { initials: "V",  role: "Examiner",          color: "var(--blue)",     bgColor: "var(--blue-bg)" },
  lucsystemdesign: { initials: "L",  role: "Examiner",          color: "var(--teal)",     bgColor: "var(--teal-bg)" },
  "ben-dicken":    { initials: "B",  role: "Examiner",          color: "var(--blue)",     bgColor: "var(--blue-bg)" },
  sdcourse:        { initials: "S",  role: "Examiner",          color: "var(--blue)",     bgColor: "var(--blue-bg)" },
  justin:          { initials: "JS", role: "Pedagogy reviewer", color: "var(--teal)",     bgColor: "var(--teal-bg)" },
  alex:            { initials: "AC", role: "Clarity auditor",   color: "var(--amber-dk)", bgColor: "var(--amber-bg)" },
};

interface Props { signOffs: SignOff[] }

export default function SignOffCards({ signOffs }: Props) {
  const allApproved = signOffs.every((s) => s.status === "approved");
  return (
    <div className="space-y-4">
      {allApproved && (
        <div className="flex items-center gap-3 bg-[var(--green-bg)] border border-[var(--green)] rounded-lg px-5 py-3">
          <span className="text-[18px] font-bold text-[var(--green)]">✓</span>
          <div>
            <div className="text-[14px] font-semibold text-[var(--green)]">All chapters passed ≥ 9.0</div>
            <div className="text-[11px] text-[var(--green)]">All agents have approved — delivery is ready</div>
          </div>
        </div>
      )}

      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide">Sign-off Gate</div>
      {signOffs.map((so) => {
        const meta = AGENT_META[so.agent] ?? { initials: so.agent[0].toUpperCase(), role: so.role, color: "var(--gray-50)", bgColor: "var(--gray-95)" };
        const borderColor = so.status === "approved" ? "var(--green)" : so.status === "rejected" ? "var(--red)" : "var(--amber)";
        const badgeBg = so.status === "approved" ? "var(--green-bg)" : so.status === "rejected" ? "var(--red-bg)" : "var(--amber-bg)";
        const badgeColor = so.status === "approved" ? "var(--green)" : so.status === "rejected" ? "var(--red)" : "var(--amber-dk)";
        const badgeLabel = so.status === "approved" ? "Approved ✓" : so.status === "rejected" ? "Rejected ✗" : "Auditing…";
        return (
          <div key={so.id} className="bg-white rounded-lg p-5 border" style={{ borderColor }}>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center text-[13px] font-bold"
                  style={{ backgroundColor: meta.bgColor, color: meta.color }}
                >
                  {meta.initials}
                </div>
                <div>
                  <div className="text-[13px] font-semibold text-[var(--gray-10)]">{so.agent}</div>
                  <div className="text-[11px] text-[var(--gray-50)]">{meta.role}</div>
                </div>
              </div>
              <span
                className="text-[10px] font-semibold px-2.5 py-1 rounded border"
                style={{ backgroundColor: badgeBg, color: badgeColor, borderColor: badgeColor }}
              >
                {badgeLabel}
              </span>
            </div>
            <div className="border-t border-[var(--border)] pt-3">
              {so.status === "approved" && so.criteria.length > 0 ? (
                <div className="space-y-1.5">
                  {so.criteria.map((c) => (
                    <div key={c} className="flex items-center gap-2 text-[11px] text-[var(--gray-30)]">
                      <span className="w-1.5 h-1.5 rounded-full bg-[var(--green)] flex-shrink-0" />
                      {c}
                    </div>
                  ))}
                </div>
              ) : so.status === "pending" ? (
                <p className="text-[11px] text-[var(--amber-dk)]">Auditing final PDF across all 5 chapters…</p>
              ) : (
                <p className="text-[11px] text-[var(--red)]">Rejected — one fix round will run automatically before retry.</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
