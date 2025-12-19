import { createClient } from "@/lib/supabase/server";
import type { Database } from "@/types/database";

// Type definitions for API responses
type OrderRow = Database["public"]["Tables"]["orders"]["Row"];
type OrderItemRow = Database["public"]["Tables"]["order_items"]["Row"];
type ProductRow = Database["public"]["Tables"]["products"]["Row"];

export interface OrderItemWithProduct extends OrderItemRow {
  product: ProductRow | null;
}

export interface OrderWithItems extends OrderRow {
  order_items: OrderItemWithProduct[];
}

/**
 * VIP의 모든 주문 조회
 * @param vipId - VIP ID
 * @returns 주문 목록 (주문 아이템 및 제품 정보 포함)
 */
export async function getVipOrders(vipId: string): Promise<OrderWithItems[]> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("orders")
    .select(
      `
      *,
      order_items(
        *,
        product:products(*)
      )
    `
    )
    .eq("vip_id", vipId)
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Error fetching VIP orders:", error);
    throw new Error(`Failed to fetch VIP orders: ${error.message}`);
  }

  return (data || []) as OrderWithItems[];
}

/**
 * 주문 ID로 주문 상세 조회
 * @param orderId - 주문 ID
 * @returns 주문 상세 정보 (주문 아이템 및 제품 정보 포함)
 */
export async function getOrderById(
  orderId: string
): Promise<OrderWithItems | null> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("orders")
    .select(
      `
      *,
      order_items(
        *,
        product:products(*)
      )
    `
    )
    .eq("id", orderId)
    .single();

  if (error) {
    if (error.code === "PGRST116") {
      // No rows returned
      return null;
    }
    console.error("Error fetching order:", error);
    throw new Error(`Failed to fetch order: ${error.message}`);
  }

  return data as OrderWithItems;
}

/**
 * 주문 상태 업데이트 (관리자 전용)
 * @todo Supabase 타입 추론 이슈로 인해 임시 주석 처리
 * 관리자 기능은 별도 PR에서 구현 예정
 */
// export async function updateOrderStatus(
//   orderId: string,
//   status: Database["public"]["Enums"]["order_status"],
//   trackingNumber?: string,
//   carrier?: string
// ): Promise<void> {
//   const supabase = await createClient();
//   // Implementation...
// }
