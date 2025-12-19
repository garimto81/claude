import { createClient } from "@supabase/supabase-js";
import type { Database } from "@/types/database";

// Admin client with service role key - SERVER ONLY
// Never expose this to the client!
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey =
  process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY!;

export function createAdminClient() {
  if (typeof window !== "undefined") {
    throw new Error("Admin client cannot be used on the client side!");
  }

  return createClient<Database>(supabaseUrl, supabaseServiceKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });
}
