"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SelectedItem {
  productId: string;
  productName: string;
  size: string;
}

interface ActionBarProps {
  selectedItems: SelectedItem[];
  maxItems: number;
  onCheckout: () => void;
}

export function ActionBar({ selectedItems, maxItems, onCheckout }: ActionBarProps) {
  const selectedCount = selectedItems.length;

  return (
    <motion.div
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed bottom-0 left-0 right-0 z-50 px-[60px] py-5 bg-[rgba(26,26,26,0.95)] border-t border-[#2A2A2A] backdrop-blur-[10px]"
    >
      <div className="flex justify-between items-center max-w-[1600px] mx-auto">
        {/* Selection Summary */}
        <div className="flex items-center gap-6">
          <span className="text-[14px] text-[var(--color-text-secondary)]">
            Selected Items:{" "}
            <strong className="text-[var(--color-gold)] text-[18px]">
              {selectedCount}
            </strong>{" "}
            / {maxItems}
          </span>

          {/* Selected Item Thumbnails */}
          <div className="flex gap-2">
            <AnimatePresence mode="popLayout">
              {selectedItems.map((item, index) => (
                <motion.div
                  key={item.productId}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="w-12 h-12 bg-[#151515] border border-[#2A2A2A] rounded-lg flex items-center justify-center font-heading text-[14px] text-[var(--color-text-secondary)]"
                  title={`${item.productName} (${item.size})`}
                >
                  {String(index + 1).padStart(2, "0")}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>

        {/* Checkout Button */}
        <Button
          onClick={onCheckout}
          disabled={selectedCount === 0}
          className="flex items-center gap-3 px-10 py-6 bg-gradient-to-r from-[var(--color-gold)] to-[var(--color-gold-dark)] border-none rounded-lg text-[14px] font-semibold tracking-[1px] text-[var(--color-background)] hover:shadow-[0_10px_30px_rgba(212,175,55,0.3)] hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:transform-none disabled:hover:shadow-none"
        >
          Proceed to Checkout
          <ArrowRight className="w-[18px] h-[18px]" />
        </Button>
      </div>
    </motion.div>
  );
}
