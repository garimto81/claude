import { cookies } from "next/headers";
import { createClient } from "@/lib/supabase/server";
import type { Database } from "@/types/database";

export type VipSession = Database["public"]["Tables"]["vips"]["Row"];

/**
 * 서버 컴포넌트에서 현재 VIP 세션 가져오기
 * @returns VIP 정보 또는 null
 */
export async function getVipSession(): Promise<VipSession | null> {
  const cookieStore = await cookies();
  const vipSessionId = cookieStore.get("vip_session")?.value;

  if (!vipSessionId) {
    return null;
  }

  const supabase = await createClient();

  const { data: vip, error } = await supabase
    .from("vips")
    .select("*")
    .eq("id", vipSessionId)
    .eq("is_active", true)
    .single();

  if (error || !vip) {
    return null;
  }

  return vip;
}

/**
 * VIP가 특정 등급 이상인지 확인
 * @param requiredTier - 필요한 최소 등급
 * @returns true if VIP tier is sufficient
 */
export async function hasVipTier(
  requiredTier: "silver" | "gold"
): Promise<boolean> {
  const vip = await getVipSession();

  if (!vip) {
    return false;
  }

  // gold > silver
  if (requiredTier === "silver") {
    return true; // silver 또는 gold 모두 접근 가능
  }

  return vip.tier === "gold";
}

/**
 * VIP의 주문 가능한 최대 수량 확인
 * @returns 주문 가능한 최대 수량 (silver: 3, gold: 5)
 */
export async function getVipOrderLimit(): Promise<number> {
  const vip = await getVipSession();

  if (!vip) {
    return 0;
  }

  return vip.tier === "gold" ? 5 : 3;
}

/**
 * VIP의 현재 주문 수량 확인
 * @returns 현재까지 주문한 수량
 */
export async function getVipCurrentOrderCount(): Promise<number> {
  const vip = await getVipSession();

  if (!vip) {
    return 0;
  }

  const supabase = await createClient();

  // 주문 아이템 수량 합계 계산
  const { data: orders } = await supabase
    .from("orders")
    .select("id, vip_id, status")
    .eq("vip_id", vip.id)
    .not("status", "eq", "cancelled");

  if (!orders || orders.length === 0) {
    return 0;
  }

  // 각 주문의 아이템 수량 가져오기
  type OrderRow = { id: string; vip_id: string; status: string };
  type OrderItemRow = { quantity: number };

  const orderIds = (orders as OrderRow[]).map((o) => o.id);
  const { data: orderItems } = await supabase
    .from("order_items")
    .select("quantity")
    .in("order_id", orderIds);

  if (!orderItems) {
    return 0;
  }

  // 모든 주문의 아이템 수량 합계
  const totalQuantity = (orderItems as OrderItemRow[]).reduce(
    (sum, item) => sum + item.quantity,
    0
  );

  return totalQuantity;
}

/**
 * VIP가 추가 주문 가능한지 확인
 * @param quantity - 추가할 수량
 * @returns true if VIP can order more items
 */
export async function canVipOrder(quantity: number = 1): Promise<boolean> {
  const [limit, currentCount] = await Promise.all([
    getVipOrderLimit(),
    getVipCurrentOrderCount(),
  ]);

  return currentCount + quantity <= limit;
}
