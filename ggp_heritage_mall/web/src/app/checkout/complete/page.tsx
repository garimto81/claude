"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { CheckCircle, Package, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CheckoutHeader } from "@/components/checkout";

export const dynamic = "force-dynamic";

function OrderCompleteContent() {
  const searchParams = useSearchParams();
  const orderId = searchParams.get("order_id");
  const [orderNumber, setOrderNumber] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (orderId) {
      // Generate order number from order ID
      const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
      const shortId = orderId.slice(0, 6).toUpperCase();
      setOrderNumber(`ORD-${date}-${shortId}`);
    } else {
      // Fallback for missing order ID
      const num = Math.random().toString(36).substring(2, 8).toUpperCase();
      setOrderNumber(`GGP-${num}`);
    }
    setIsLoading(false);
  }, [orderId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      {/* Header with Progress Steps */}
      <CheckoutHeader currentStep={3} />

      {/* Main Content */}
      <main className="pt-[100px] min-h-screen flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-[600px] mx-auto px-6"
        >
          {/* Success Icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="w-24 h-24 mx-auto mb-8 rounded-full bg-[rgba(46,204,113,0.1)] border-2 border-[#2ECC71] flex items-center justify-center"
          >
            <CheckCircle className="w-12 h-12 text-[#2ECC71]" />
          </motion.div>

          {/* Title */}
          <h1 className="font-heading text-[48px] font-normal mb-4">
            Order Confirmed
          </h1>

          {/* Description */}
          <p className="text-[18px] text-[var(--color-text-secondary)] mb-8 leading-relaxed">
            Thank you for your order! Your exclusive items will be carefully
            prepared and shipped to you.
          </p>

          {/* Order Number */}
          <div className="inline-block px-8 py-4 bg-[var(--color-surface)] border border-[#2A2A2A] rounded-xl mb-8">
            <div className="text-[12px] font-medium tracking-[1px] text-[var(--color-gold)] uppercase mb-1">
              Order Number
            </div>
            <div className="text-[24px] font-heading font-medium">
              {orderNumber}
            </div>
          </div>

          {/* Info Card */}
          <div className="p-6 bg-[var(--color-surface)] border border-[#2A2A2A] rounded-xl mb-10">
            <div className="flex items-center gap-4 text-left">
              <div className="w-12 h-12 rounded-full bg-[rgba(212,175,55,0.1)] flex items-center justify-center">
                <Package className="w-6 h-6 text-[var(--color-gold)]" />
              </div>
              <div>
                <div className="text-[15px] font-medium mb-1">
                  What happens next?
                </div>
                <div className="text-[13px] text-[var(--color-text-secondary)]">
                  You will receive an email confirmation shortly. We&apos;ll notify
                  you when your order ships.
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4 justify-center">
            <Link href="/orders">
              <Button
                variant="outline"
                className="px-8 py-6 border-[#2A2A2A] text-[var(--color-text-primary)] hover:border-[var(--color-gold)] hover:text-[var(--color-gold)]"
              >
                View My Orders
              </Button>
            </Link>
            <Link href="/products">
              <Button className="px-8 py-6 bg-gradient-to-r from-[var(--color-gold)] to-[var(--color-gold-dark)] text-[var(--color-background)] hover:shadow-[0_10px_30px_rgba(212,175,55,0.3)]">
                Continue Shopping
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
        </motion.div>
      </main>
    </div>
  );
}

export default function OrderCompletePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center">
          <div className="text-[var(--color-text-secondary)]">Loading...</div>
        </div>
      }
    >
      <OrderCompleteContent />
    </Suspense>
  );
}
