"use client";
import { DeliveryStep } from "@/lib/types";

interface Props { steps: DeliveryStep[]; allApproved: boolean; onShip: () => void; shipping: boolean }

export default function DeliveryChecklist({ steps, allApproved, onShip, shipping }: Props) {
  const note = "Delivery runs automatically once all agents approve. A rejected sign-off triggers one fix round before retry.";

  return (
    <div className="space-y-4">
      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide">Delivery Steps</div>
      <div className="space-y-3">
        {steps.map((step, i) => {
          const isDone = step.status === "done";
          return (
            <div key={step.id} className="flex gap-4 items-start">
              <div
                className={`w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center text-[11px] font-bold ${
                  isDone
                    ? "bg-[var(--green)] text-white"
                    : "bg-[var(--gray-95)] border-2 border-[var(--gray-90)] text-[var(--gray-70)]"
                }`}
              >
                {isDone ? "✓" : i + 1}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-[13px] font-semibold ${isDone ? "text-[var(--green)]" : "text-[var(--gray-30)]"}`}>
                    {step.label}
                  </span>
                  <span
                    className={`text-[9px] font-medium px-2 py-0.5 rounded border ${
                      isDone
                        ? "border-[var(--green)] bg-[var(--green-bg)] text-[var(--green)]"
                        : "border-[var(--gray-90)] bg-[var(--gray-95)] text-[var(--gray-70)]"
                    }`}
                  >
                    {isDone ? "done" : step.status}
                  </span>
                </div>
                {step.detail && (
                  <div className="bg-[var(--gray-10)] rounded px-3 py-2 font-[family-name:var(--font-geist-mono)] text-[10px] text-[var(--gray-95)]">
                    {step.detail}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      <div className="bg-[var(--gray-97)] border border-[var(--border)] rounded-lg p-4 text-[11px] text-[var(--gray-50)]">
        {note}
      </div>
      <div className="flex gap-3">
        <button
          onClick={onShip}
          disabled={!allApproved || shipping}
          className={`flex-1 py-2.5 rounded-lg text-[13px] font-semibold text-white transition-all ${
            allApproved && !shipping
              ? "bg-[var(--blue)] hover:opacity-90"
              : "bg-[var(--gray-90)] cursor-not-allowed text-[var(--gray-70)]"
          }`}
        >
          {shipping ? "Shipping…" : allApproved ? "Ship" : "Ship — awaiting approvals"}
        </button>
      </div>
    </div>
  );
}
