"use client";

import { X, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface OrderItem {
  id: string;
  name: string;
  category: string;
  size: string;
  image?: string;
}

interface OrderSummaryProps {
  items: OrderItem[];
  maxItems: number;
  onRemoveItem: (itemId: string) => void;
  onConfirm: () => void;
  isSubmitting?: boolean;
}

export function OrderSummary({
  items,
  maxItems,
  onRemoveItem,
  onConfirm,
  isSubmitting = false,
}: OrderSummaryProps) {
  const remainingItems = maxItems - items.length;

  return (
    <div className="w-[480px] p-10 bg-[var(--color-surface)] flex flex-col">
      <h2 className="font-heading text-[24px] font-normal mb-8">Order Summary</h2>

      {/* Items List */}
      <div className="flex-1 mb-8">
        {items.map((item, index) => (
          <div
            key={item.id}
            className="flex gap-4 py-4 border-b border-[#2A2A2A]"
          >
            {/* Item Image/Number */}
            <div className="w-[72px] h-[72px] bg-[#151515] rounded-lg flex items-center justify-center font-heading text-[20px] text-[#2A2A2A]">
              {String(index + 1).padStart(2, "0")}
            </div>

            {/* Item Details */}
            <div className="flex-1">
              <div className="text-[10px] font-medium tracking-[1px] text-[var(--color-gold)] uppercase mb-1">
                {item.category}
              </div>
              <div className="text-[15px] font-medium mb-1">{item.name}</div>
              <div className="text-[13px] text-[var(--color-text-secondary)]">
                Size: {item.size}
              </div>
            </div>

            {/* Remove Button */}
            <button
              onClick={() => onRemoveItem(item.id)}
              className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-white/10 transition-colors"
            >
              <X className="w-4 h-4 text-[var(--color-text-secondary)]" />
            </button>
          </div>
        ))}

        {items.length === 0 && (
          <div className="py-8 text-center text-[var(--color-text-secondary)]">
            No items selected
          </div>
        )}
      </div>

      {/* Divider */}
      <div className="h-px bg-[#2A2A2A] my-6" />

      {/* Summary Rows */}
      <div className="space-y-3 mb-6">
        <div className="flex justify-between items-center">
          <span className="text-[14px] text-[var(--color-text-secondary)]">
            Selected Items
          </span>
          <span className="text-[14px] font-medium">
            {items.length} items
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-[14px] text-[var(--color-text-secondary)]">
            Remaining Selection
          </span>
          <span className="text-[14px] font-medium">
            {remainingItems} items
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-[14px] text-[var(--color-text-secondary)]">
            Shipping
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-[rgba(46,204,113,0.1)] border border-[#2ECC71] rounded text-[12px] font-medium text-[#2ECC71]">
            <Check className="w-3.5 h-3.5" />
            Free
          </span>
        </div>
      </div>

      {/* Divider */}
      <div className="h-px bg-[#2A2A2A] my-6" />

      {/* Total */}
      <div className="flex justify-between items-center mb-8">
        <span className="text-[14px] text-[var(--color-text-secondary)]">
          Total
        </span>
        <span className="text-[16px] font-semibold text-[var(--color-gold)]">
          VIP Complimentary
        </span>
      </div>

      {/* Confirm Button */}
      <Button
        onClick={onConfirm}
        disabled={items.length === 0 || isSubmitting}
        className="w-full py-6 bg-gradient-to-r from-[var(--color-gold)] to-[var(--color-gold-dark)] border-none rounded-lg text-[15px] font-semibold tracking-[1px] text-[var(--color-background)] hover:shadow-[0_10px_30px_rgba(212,175,55,0.3)] hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:transform-none disabled:hover:shadow-none"
      >
        {isSubmitting ? "Processing..." : "Confirm Order"}
      </Button>

      {/* Terms */}
      <p className="mt-4 text-[12px] text-[var(--color-text-secondary)] text-center leading-relaxed">
        By confirming, you agree to our{" "}
        <a href="#" className="text-[var(--color-gold)] hover:underline">
          Terms of Service
        </a>{" "}
        and{" "}
        <a href="#" className="text-[var(--color-gold)] hover:underline">
          Privacy Policy
        </a>
        .
      </p>
    </div>
  );
}
