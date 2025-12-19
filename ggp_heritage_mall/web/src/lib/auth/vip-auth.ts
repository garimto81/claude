import { createClient } from "@/lib/supabase/server";
import type { Database } from "@/types/database";

export type VipSession = Database["public"]["Tables"]["vips"]["Row"];

/**
 * VIP 초대 토큰으로 인증
 * @param token - 초대 토큰 (invite_token)
 * @returns VIP 정보 또는 null (토큰 유효하지 않음)
 */
export async function verifyVipToken(
  token: string
): Promise<VipSession | null> {
  if (!token || token.trim().length === 0) {
    return null;
  }

  const supabase = await createClient();

  // invite_token으로 VIP 조회
  const { data: vip, error } = await supabase
    .from("vips")
    .select("*")
    .eq("invite_token", token.trim())
    .eq("is_active", true)
    .single();

  if (error || !vip) {
    return null;
  }

  return vip;
}

/**
 * 현재 요청의 VIP 세션 가져오기 (쿠키 기반)
 * @returns VIP 정보 또는 null
 */
export async function getVipSession(): Promise<VipSession | null> {
  const supabase = await createClient();

  // Supabase Auth 사용자 확인
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return null;
  }

  // user.id로 VIP 조회
  const { data: vip, error } = await supabase
    .from("vips")
    .select("*")
    .eq("id", user.id)
    .eq("is_active", true)
    .single();

  if (error || !vip) {
    return null;
  }

  return vip;
}

/**
 * VIP 세션 생성 (Supabase Auth 세션 생성)
 * @param vipId - VIP ID
 */
export async function createVipSession(vipId: string): Promise<boolean> {
  const supabase = await createClient();

  // VIP 존재 여부 확인
  const { data: vip, error: vipError } = await supabase
    .from("vips")
    .select("*")
    .eq("id", vipId)
    .eq("is_active", true)
    .single();

  if (vipError || !vip) {
    return false;
  }

  // Supabase Auth 세션 생성
  // 주의: 이 방법은 실제 프로덕션에서는 서버에서 signInWithPassword 또는
  // Magic Link를 사용해야 합니다. 여기서는 간소화된 접근 방식을 사용합니다.
  // 실제로는 VIP 정보를 쿠키/세션에 저장하는 방식으로 구현해야 합니다.

  return true;
}

/**
 * VIP 세션 종료
 */
export async function clearVipSession(): Promise<void> {
  const supabase = await createClient();
  await supabase.auth.signOut();
}
