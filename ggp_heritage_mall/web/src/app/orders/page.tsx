import { redirect } from "next/navigation";
import { getVipSession } from "@/lib/auth";
import { getVipOrders, type OrderWithItems } from "@/lib/api/orders-query";
import { OrderList } from "@/components/orders/OrderList";

export const metadata = {
  title: "주문 내역 | GGP Heritage Mall",
  description: "VIP 전용 주문 내역을 확인하세요",
};

export default async function OrdersPage() {
  // VIP 세션 확인
  const vip = await getVipSession();

  if (!vip) {
    redirect("/");
  }

  // VIP 주문 목록 조회
  let orders: OrderWithItems[] = [];
  try {
    orders = await getVipOrders(vip.id);
  } catch (error) {
    console.error("Failed to fetch VIP orders:", error);
    orders = [];
  }

  return (
    <div className="min-h-screen bg-[var(--color-background)] py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-serif text-white mb-2">
            마이 주문
          </h1>
          <p className="text-gray-400">
            주문하신 상품의 배송 상태를 확인하세요
          </p>
        </div>

        {/* VIP 정보 요약 */}
        <div className="bg-[var(--color-surface)] border border-white/10 rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <p className="text-sm text-gray-400 mb-1">VIP 등급</p>
              <p className="text-[var(--color-gold)] font-semibold text-lg uppercase">
                {vip.tier}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">이메일</p>
              <p className="text-white">{vip.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">총 주문</p>
              <p className="text-white font-semibold">{orders.length}건</p>
            </div>
          </div>
        </div>

        {/* 주문 목록 */}
        <OrderList orders={orders} />
      </div>
    </div>
  );
}
