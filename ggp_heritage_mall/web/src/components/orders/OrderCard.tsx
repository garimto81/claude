import type { OrderWithItems } from "@/lib/api/orders-query";
import type { OrderStatus } from "@/types/database";

interface OrderCardProps {
  order: OrderWithItems;
}

const statusConfig: Record<
  OrderStatus,
  { label: string; color: string; bgColor: string }
> = {
  pending: {
    label: "주문 접수",
    color: "text-yellow-400",
    bgColor: "bg-yellow-400/10 border-yellow-400/20",
  },
  processing: {
    label: "주문 확정",
    color: "text-blue-400",
    bgColor: "bg-blue-400/10 border-blue-400/20",
  },
  shipped: {
    label: "배송 중",
    color: "text-purple-400",
    bgColor: "bg-purple-400/10 border-purple-400/20",
  },
  delivered: {
    label: "배송 완료",
    color: "text-green-400",
    bgColor: "bg-green-400/10 border-green-400/20",
  },
  cancelled: {
    label: "취소됨",
    color: "text-gray-400",
    bgColor: "bg-gray-400/10 border-gray-400/20",
  },
};

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}년 ${month}월 ${day}일`;
}

export function OrderCard({ order }: OrderCardProps) {
  const status = statusConfig[order.status];
  const orderDate = formatDate(order.created_at);

  // 총 상품 수량 계산
  const totalQuantity = order.order_items.reduce(
    (sum, item) => sum + item.quantity,
    0
  );

  return (
    <div className="bg-[var(--color-surface)] border border-white/10 rounded-lg p-6 hover:border-[var(--color-gold)]/30 transition-colors">
      {/* 주문 헤더 */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm text-gray-400 mb-1">주문 번호</p>
          <p className="font-mono text-white">{order.id.slice(0, 8)}</p>
        </div>
        <div
          className={`px-3 py-1 rounded-full border ${status.bgColor} ${status.color}`}
        >
          {status.label}
        </div>
      </div>

      {/* 주문 날짜 */}
      <p className="text-sm text-gray-400 mb-4">{orderDate}</p>

      {/* 주문 상품 목록 */}
      <div className="space-y-3 mb-4">
        {order.order_items.map((item) => (
          <div
            key={item.id}
            className="flex items-center gap-4 pb-3 border-b border-white/5 last:border-0"
          >
            {/* 상품 이미지 */}
            {item.product?.images && item.product.images.length > 0 && (
              <div className="w-16 h-16 bg-black/30 rounded-md overflow-hidden flex-shrink-0">
                <img
                  src={item.product.images[0]}
                  alt={item.product.name}
                  className="w-full h-full object-cover"
                />
              </div>
            )}

            {/* 상품 정보 */}
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate">
                {item.product?.name || "상품 정보 없음"}
              </p>
              <p className="text-sm text-gray-400">
                사이즈: {item.size} | 수량: {item.quantity}개
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* 총 수량 */}
      <div className="pt-4 border-t border-white/10">
        <div className="flex justify-between items-center">
          <span className="text-gray-400">총 상품 수량</span>
          <span className="text-[var(--color-gold)] font-semibold">
            {totalQuantity}개
          </span>
        </div>
      </div>

      {/* 배송 정보 (배송 중 또는 배송 완료일 때만 표시) */}
      {(order.status === "shipped" || order.status === "delivered") &&
        order.tracking_number && (
          <div className="mt-4 pt-4 border-t border-white/10">
            <p className="text-sm text-gray-400 mb-1">배송 정보</p>
            <div className="flex items-center gap-2">
              {order.carrier && (
                <span className="text-sm text-white">{order.carrier}</span>
              )}
              <span className="text-sm font-mono text-[var(--color-gold)]">
                {order.tracking_number}
              </span>
            </div>
          </div>
        )}
    </div>
  );
}
