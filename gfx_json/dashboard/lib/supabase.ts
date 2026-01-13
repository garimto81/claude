import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;

// 신규 키 (sb_publishable_...) 우선, 레거시 키 fallback
const supabaseKey =
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);

// 타입 정의
export interface GfxSession {
  id: string;
  gfx_pc_id: string;
  session_id: number;
  file_name: string;
  file_hash: string;
  raw_json: Record<string, unknown>;
  table_type: string | null;
  event_title: string | null;
  software_version: string | null;
  hand_count: number;
  sync_source: string;
  sync_status: string;
  created_at: string;
  updated_at: string;
}

export interface SyncEvent {
  id: string;
  gfx_pc_id: string;
  event_type: "sync" | "error" | "batch" | "offline" | "recovery";
  file_count: number;
  error_message: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface PCStatus {
  gfx_pc_id: string;
  total_sessions: number;
  sessions_last_hour: number;
  sessions_last_day: number;
  last_sync_at: string;
  status: "online" | "idle" | "offline";
}

export interface SyncStats {
  total_synced: number;
  synced_last_hour: number;
  synced_last_day: number;
  active_pc_count: number;
  last_sync_at: string;
}
