"use server";

import { redirect } from "next/navigation";
import { createOrder, type CreateOrderInput } from "@/lib/api/orders";

/**
 * 주문 생성 서버 액션
 * @param formData - 체크아웃 폼 데이터
 * @returns 주문 결과 (성공 시 리다이렉트)
 */
export async function createOrderAction(input: CreateOrderInput) {
  const result = await createOrder(input);

  if (!result.success) {
    return {
      success: false,
      error: result.error,
      details: result.details,
    };
  }

  // 주문 완료 페이지로 리다이렉트
  redirect(`/checkout/complete?order_id=${result.order_id}`);
}
