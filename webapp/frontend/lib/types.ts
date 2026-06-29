export interface Gap {
  id: number;
  source_tag: string;
  description: string;
}

export interface PassRecord {
  id: number;
  pass_num: number;
  acc_score: number | null;
  cov_score: number | null;
  alex_score: number | null;
  gaps: Gap[];
}

export interface Chapter {
  id: number;
  index: number;
  title: string;
  passes: PassRecord[];
}

export interface SignOff {
  id: number;
  agent: string;
  role: string;
  status: "pending" | "approved" | "rejected";
  criteria: string[];
}

export interface DeliveryStep {
  id: number;
  index: number;
  label: string;
  status: "waiting" | "uploading" | "done";
  detail: string | null;
}

export interface Run {
  id: number;
  title: string;
  authors: string[];
  examiners: string[];
  topic: string;
  status: "running" | "done" | "stalled";
  current_stage: "ingestion" | "generation" | "verification" | "sign-off" | "delivery";
  current_pass: number;
  pdf_path: string | null;
  started_at: string;
  chapters: Chapter[];
  sign_offs: SignOff[];
  delivery_steps: DeliveryStep[];
}

export interface StatsOut {
  total_runs: number;
  passed_this_week: number;
  avg_passes_to_ship: number;
  tokens_this_month: number;
}

export interface RunsListResponse {
  stats: StatsOut;
  runs: Run[];
}

export interface Topic {
  id: number;
  name: string;
  authors: string[];
  post_count: number;
  authors_post_count: Record<string, number>;
  suggested_chapters: string[];
  status: "suggested" | "shipped" | "needsUpdate";
  post_count_at_ship: number | null;
  shipped_at: string | null;
}
