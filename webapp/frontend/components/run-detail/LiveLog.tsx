"use client";
import { useEffect, useRef, useState } from "react";

interface LogLine { ts: string; agent: string; message: string }

const AGENT_COLORS: Record<string, string> = {
  vutr: "var(--blue)", lucsystemdesign: "var(--teal)", "ben-dicken": "var(--blue)",
  sdcourse: "var(--blue)", justin: "var(--teal)", alex: "var(--amber)", system: "var(--gray-70)",
};

interface Props { runId: number }

export default function LiveLog({ runId }: Props) {
  const [lines, setLines] = useState<LogLine[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const es = new EventSource(`${baseUrl}/runs/${runId}/stream`);
    es.onmessage = (e) => {
      try {
        const line: LogLine = JSON.parse(e.data);
        setLines((prev) => [...prev, line]);
      } catch {}
    };
    es.onerror = () => es.close();
    return () => es.close();
  }, [runId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  return (
    <div>
      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide mb-2">Live Log</div>
      <div className="bg-[var(--gray-10)] rounded-lg p-4 h-40 overflow-y-auto font-mono text-[10px]">
        {lines.length === 0 && <span className="text-[var(--gray-70)]">Waiting for events…</span>}
        {lines.map((l, i) => (
          <div key={i} className="flex gap-3 mb-1">
            <span className="text-[var(--gray-70)] flex-shrink-0">{l.ts}</span>
            <span className="flex-shrink-0" style={{ color: AGENT_COLORS[l.agent] ?? "var(--gray-70)" }}>{l.agent}</span>
            <span className="text-[var(--gray-95)]">{l.message}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
