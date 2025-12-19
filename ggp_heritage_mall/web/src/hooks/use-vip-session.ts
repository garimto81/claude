"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import type { Database } from "@/types/database";

export type VipSession = Database["public"]["Tables"]["vips"]["Row"];

/**
 * 클라이언트 컴포넌트에서 VIP 세션 사용
 */
export function useVipSession() {
  const [vip, setVip] = useState<VipSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadVipSession() {
      try {
        // 쿠키에서 VIP 세션 ID 가져오기
        const vipSessionId = document.cookie
          .split("; ")
          .find((row) => row.startsWith("vip_session="))
          ?.split("=")[1];

        if (!vipSessionId) {
          setVip(null);
          return;
        }

        const supabase = createClient();

        const { data: vipData, error } = await supabase
          .from("vips")
          .select("*")
          .eq("id", vipSessionId)
          .eq("is_active", true)
          .single();

        if (error || !vipData) {
          setVip(null);
          return;
        }

        setVip(vipData);
      } catch (error) {
        console.error("Failed to load VIP session:", error);
        setVip(null);
      } finally {
        setLoading(false);
      }
    }

    loadVipSession();
  }, []);

  return { vip, loading };
}

/**
 * VIP 주문 제한 확인 훅
 */
export function useVipOrderLimit() {
  const { vip } = useVipSession();
  const [currentCount, setCurrentCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOrderCount() {
      if (!vip) {
        setCurrentCount(0);
        setLoading(false);
        return;
      }

      try {
        const supabase = createClient();

        // 주문 아이템 수량 합계 계산
        const { data: orders } = await supabase
          .from("orders")
          .select("id, vip_id, status")
          .eq("vip_id", vip.id)
          .not("status", "eq", "cancelled");

        if (!orders || orders.length === 0) {
          setCurrentCount(0);
          return;
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
          setCurrentCount(0);
          return;
        }

        // 모든 주문의 아이템 수량 합계
        const totalQuantity = (orderItems as OrderItemRow[]).reduce(
          (sum, item) => sum + item.quantity,
          0
        );

        setCurrentCount(totalQuantity);
      } catch (error) {
        console.error("Failed to load order count:", error);
        setCurrentCount(0);
      } finally {
        setLoading(false);
      }
    }

    loadOrderCount();
  }, [vip]);

  const limit = vip?.tier === "gold" ? 5 : 3;
  const remaining = Math.max(0, limit - currentCount);
  const canOrder = (quantity: number = 1) => remaining >= quantity;

  return {
    limit,
    currentCount,
    remaining,
    canOrder,
    loading,
  };
}
