"use server";

import { redirect } from "next/navigation";
import { createOrder, type CreateOrderInput } from "@/lib/api/orders";

export async function createOrderAction(input: CreateOrderInput) {
  try {
    await createOrder(input);
    redirect("/checkout/complete");
  } catch (error) {
    console.error("Order creation failed:", error);
    return {
      success: false,
      error: "주문 생성에 실패했습니다.",
      details: error instanceof Error ? error.message : undefined,
    };
  }
}
