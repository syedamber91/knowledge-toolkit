"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Topic } from "@/lib/types";
import AuthorChips from "@/components/pack-builder/AuthorChips";
import TopicBrowser from "@/components/pack-builder/TopicBrowser";
import ChapterFields from "@/components/pack-builder/ChapterFields";
import ExaminerGrid from "@/components/pack-builder/ExaminerGrid";
import RunPreview from "@/components/pack-builder/RunPreview";
import AttentionDigest from "@/components/pack-builder/AttentionDigest";

const EMPTY_CHAPTERS = ["", "", "", "", ""];

export default function NewRunPage() {
  const router = useRouter();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [authors, setAuthors] = useState<string[]>([]);
  const [topic, setTopic] = useState("");
  const [chapters, setChapters] = useState<string[]>(EMPTY_CHAPTERS);
  const [examiners, setExaminers] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { api.topics.list().then(setTopics); }, []);

  const selectedTopic = topics.find((t) => t.name === topic);
  const postCount = selectedTopic?.post_count ?? 0;
  const canStart = authors.length > 0 && topic !== "" && examiners.length > 0;

  function handleTopicSelect(name: string) {
    setTopic(name);
    const t = topics.find((t) => t.name === name);
    if (t?.suggested_chapters?.length) {
      setChapters(t.suggested_chapters.slice(0, 5).concat(EMPTY_CHAPTERS).slice(0, 5));
    } else {
      setChapters(EMPTY_CHAPTERS);
    }
  }

  async function start() {
    if (!canStart) return;
    setLoading(true);
    try {
      const run = await api.runs.create({
        authors, examiners, topic,
        chapter_titles: chapters.map((c, i) => c || `Chapter ${i + 1}`),
      });
      router.push(`/runs/${run.id}`);
    } finally { setLoading(false); }
  }

  return (
    <div className="max-w-[1392px] mx-auto px-6 py-6">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => router.push("/runs")} className="text-[12px] text-[var(--gray-50)] hover:text-[var(--gray-30)]">← Runs</button>
        <h1 className="text-[18px] font-semibold">New Run</h1>
      </div>
      <div className="grid grid-cols-[1fr_460px] gap-8">
        <div className="space-y-6">
          <AuthorChips selected={authors} onChange={setAuthors} />
          <TopicBrowser topics={topics} selected={topic} onSelect={handleTopicSelect} />
          {topic && <ChapterFields chapters={chapters} onChange={setChapters} />}
          <ExaminerGrid selected={examiners} onChange={setExaminers} />
        </div>
        <div className="space-y-4">
          {selectedTopic && (
            <div className="bg-white border border-[var(--border)] rounded-lg px-5 py-4">
              <div className="text-[11px] font-semibold text-[var(--gray-50)] mb-1">Vault status</div>
              <div className="text-[13px] font-medium text-[var(--gray-10)]">{postCount} posts matched to {topic}</div>
              <div className="text-[11px] text-[var(--gray-50)] mt-0.5">
                {Object.entries(selectedTopic.authors_post_count).map(([a, n]) => `${a}: ${n}`).join(" · ")}
              </div>
            </div>
          )}
          <AttentionDigest topics={topics} />
          <RunPreview authors={authors} topic={topic} chapters={chapters} examiners={examiners} postCount={postCount} />
          <div className="flex gap-3">
            <button onClick={start} disabled={!canStart || loading}
              className={`flex-1 py-2.5 rounded-lg text-[13px] font-semibold text-white transition-opacity ${canStart && !loading ? "bg-[var(--blue)]" : "bg-[var(--gray-90)] cursor-not-allowed"}`}>
              {loading ? "Starting…" : "Start pipeline"}
            </button>
            <button onClick={() => router.push("/runs")}
              className="flex-1 py-2.5 rounded-lg text-[13px] font-medium text-[var(--gray-30)] bg-white border border-[var(--border)]">
              Save as draft
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
