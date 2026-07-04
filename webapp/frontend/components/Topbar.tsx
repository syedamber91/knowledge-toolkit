"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Topbar() {
  const path = usePathname();
  const isNew = path === "/runs/new";
  return (
    <header className="fixed top-0 left-0 right-0 h-14 bg-white border-b border-[var(--border)] flex items-center px-6 z-50">
      <span className="text-[15px] font-semibold text-[var(--gray-10)]">Knowledge Toolkit</span>
      <span className="ml-2 text-[10px] font-medium px-1.5 py-0.5 rounded bg-[var(--blue-bg)] text-[var(--blue)]">beta</span>
      <div className="ml-auto">
        {!isNew && (
          <Link href="/runs/new"
            className="px-4 py-2 bg-[var(--blue)] text-white text-[13px] font-medium rounded-md hover:opacity-90">
            + New run
          </Link>
        )}
      </div>
    </header>
  );
}
