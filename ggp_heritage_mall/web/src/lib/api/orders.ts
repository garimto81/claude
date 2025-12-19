import { createClient } from "@/lib/supabase/server";
import type { Database } from "@/types/database";
import { getVipSession, canVipOrder } from "@/lib/auth";

// Type definitions for API responses
type OrderRow = Database["public"]["Tables"]["orders"]["Row"];
type OrderItemRow = Database["public"]["Tables"]["order_items"]["Row"];
type ProductRow = Database["public"]["Tables"]["products"]["Row"];
type OrderInsert = Database["public"]["Tables"]["orders"]["Insert"];
type OrderItemInsert = Database["public"]["Tables"]["order_items"]["Insert"];

export interface OrderItemWithProduct extends OrderItemRow {
  product: ProductRow | null;
}

export interface OrderWithItems extends OrderRow {
  order_items: OrderItemWithProduct[];
}

// Create order types
export interface CartItem {
  product_id: string;
  size: string;
  quantity: number;
}

export interface CreateOrderInput {
  items: CartItem[];
  shipping_address: {
    recipient_name: string;
    phone: string;
    address_line1: string;
    address_line2?: string;
    city: string;
    state: string;
    postal_code: string;
    country: string;
  };
  notes?: string;
}

export interface CreateOrderResult {
  success: boolean;
  order_id?: string;
  order_number?: string;
  error?: string;
  details?: string;
}

/**
 * 주문 생성 (트랜잭션)
 * 1. VIP 세션 확인
 * 2. 주문 수량 제한 체크
 * 3. 재고 확인
 * 4. 주문 생성 + 주문 아이템 추가 + 재고 차감
 *
 * @param input - 주문 정보 (items, shipping_address, notes)
 * @returns 주문 생성 결과 (order_id, order_number)
 */
export async function createOrder(
  input: CreateOrderInput
): Promise<CreateOrderResult> {
  const supabase = await createClient();

  // 1. VIP 세션 확인
  const vip = await getVipSession();
  if (!vip) {
    return {
      success: false,
      error: "인증 실패",
      details: "VIP 세션이 만료되었습니다. 다시 로그인해주세요.",
    };
  }

  // 2. 주문 아이템 수량 합계 계산
  const totalQuantity = input.items.reduce(
    (sum, item) => sum + item.quantity,
    0
  );

  // 3. 주문 수량 제한 체크
  const canOrder = await canVipOrder(totalQuantity);
  if (!canOrder) {
    const tierLimit = vip.tier === "gold" ? 5 : 3;
    return {
      success: false,
      error: "주문 수량 초과",
      details: `VIP ${vip.tier.toUpperCase()} 등급의 최대 주문 수량은 ${tierLimit}개입니다.`,
    };
  }

  // 4. 재고 확인
  for (const item of input.items) {
    type InventoryQuantity = { quantity: number };
    const { data: inventory, error: inventoryError } = await supabase
      .from("inventory")
      .select("quantity")
      .eq("product_id", item.product_id)
      .eq("size", item.size)
      .single<InventoryQuantity>();

    if (inventoryError || !inventory) {
      return {
        success: false,
        error: "재고 조회 실패",
        details: `상품 ID ${item.product_id} (사이즈: ${item.size})의 재고를 찾을 수 없습니다.`,
      };
    }

    if (inventory.quantity < item.quantity) {
      return {
        success: false,
        error: "재고 부족",
        details: `상품 ID ${item.product_id} (사이즈: ${item.size})의 재고가 부족합니다. (재고: ${inventory.quantity}, 주문: ${item.quantity})`,
      };
    }
  }

  // 5. 주문 생성 (트랜잭션)
  try {
    // 5-1. 주문 생성
    const orderData: OrderInsert = {
      vip_id: vip.id,
      status: "pending",
      shipping_address: input.shipping_address as Database["public"]["Tables"]["orders"]["Insert"]["shipping_address"],
      notes: input.notes,
    };

    const { data: order, error: orderError } = await supabase
      .from("orders")
      .insert(orderData as any)
      .select()
      .single();

    if (orderError || !order) {
      console.error("Order creation error:", orderError);
      return {
        success: false,
        error: "주문 생성 실패",
        details: orderError?.message || "알 수 없는 오류가 발생했습니다.",
      };
    }

    const createdOrder = order as OrderRow;

    // 5-2. 주문 아이템 생성
    const orderItems: OrderItemInsert[] = input.items.map((item) => ({
      order_id: createdOrder.id,
      product_id: item.product_id,
      size: item.size,
      quantity: item.quantity,
    }));

    const { error: orderItemsError } = await supabase
      .from("order_items")
      .insert(orderItems as any);

    if (orderItemsError) {
      console.error("Order items creation error:", orderItemsError);
      // 롤백: 주문 삭제
      await supabase.from("orders").delete().eq("id", createdOrder.id);

      return {
        success: false,
        error: "주문 아이템 생성 실패",
        details: orderItemsError.message,
      };
    }

    // 5-3. 재고 차감
    for (const item of input.items) {
      // 현재 재고 조회
      const { data: currentInventory, error: fetchError } = await supabase
        .from("inventory")
        .select("quantity")
        .eq("product_id", item.product_id)
        .eq("size", item.size)
        .single();

      if (fetchError || !currentInventory) {
        console.error("Inventory fetch error:", fetchError);
        // 롤백: 주문 및 주문 아이템 삭제
        await supabase.from("order_items").delete().eq("order_id", createdOrder.id);
        await supabase.from("orders").delete().eq("id", createdOrder.id);

        return {
          success: false,
          error: "재고 조회 실패",
          details: `상품 ID ${item.product_id} (사이즈: ${item.size})의 재고 조회 중 오류가 발생했습니다.`,
        };
      }

      // 재고 차감
      type InventoryQuantity = { quantity: number };
      const inventoryQuantity = (currentInventory as InventoryQuantity).quantity;
      const newQuantity = inventoryQuantity - item.quantity;

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const { error: updateError } = await (supabase
        .from("inventory")
        .update as any)({ quantity: newQuantity, updated_at: new Date().toISOString() })
        .eq("product_id", item.product_id)
        .eq("size", item.size);

      if (updateError) {
        console.error("Inventory update error:", updateError);
        // 롤백: 주문 및 주문 아이템 삭제
        await supabase.from("order_items").delete().eq("order_id", createdOrder.id);
        await supabase.from("orders").delete().eq("id", createdOrder.id);

        return {
          success: false,
          error: "재고 차감 실패",
          details: `상품 ID ${item.product_id} (사이즈: ${item.size})의 재고 차감 중 오류가 발생했습니다.`,
        };
      }
    }

    // 6. 주문 번호 생성 (예: ORD-20250101-ABC123)
    const orderNumber = `ORD-${new Date().toISOString().slice(0, 10).replace(/-/g, "")}-${createdOrder.id.slice(0, 6).toUpperCase()}`;

    return {
      success: true,
      order_id: createdOrder.id,
      order_number: orderNumber,
    };
  } catch (error) {
    console.error("Unexpected error during order creation:", error);
    return {
      success: false,
      error: "주문 생성 중 오류",
      details: error instanceof Error ? error.message : "알 수 없는 오류",
    };
  }
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
 * @param orderId - 주문 ID
 * @param status - 새로운 주문 상태
 * @param trackingNumber - 송장 번호 (선택)
 * @param carrier - 배송사 (선택)
 */
export async function updateOrderStatus(
  orderId: string,
  status: Database["public"]["Enums"]["order_status"],
  trackingNumber?: string,
  carrier?: string
): Promise<void> {
  const supabase = await createClient();

  const updateData: Partial<OrderRow> = {
    status,
    updated_at: new Date().toISOString(),
  };

  if (trackingNumber) {
    updateData.tracking_number = trackingNumber;
  }

  if (carrier) {
    updateData.carrier = carrier;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const { error } = await (supabase
    .from("orders")
    .update as any)(updateData)
    .eq("id", orderId);

  if (error) {
    console.error("Error updating order status:", error);
    throw new Error(`Failed to update order status: ${error.message}`);
  }
}
