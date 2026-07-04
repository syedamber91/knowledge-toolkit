const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export const api = {
  runs: {
    list: () => get<import("./types").RunsListResponse>("/runs"),
    get:  (id: number) => get<import("./types").Run>(`/runs/${id}`),
    create: (body: { authors: string[]; examiners: string[]; topic: string; chapter_titles: string[] }) =>
      post<import("./types").Run>("/runs", body),
  },
  topics: {
    list: () => get<import("./types").Topic[]>("/topics"),
  },
};
