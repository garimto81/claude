"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  CheckoutHeader,
  OrderSummary,
  ShippingForm,
  type OrderItem,
  type ShippingAddress,
} from "@/components/checkout";
import { useCartStore } from "@/stores/cartStore";
import { createOrderAction } from "./actions";
import type { CreateOrderInput } from "@/lib/api/orders";

// Mock saved shipping address (in real app, this would come from Supabase)
const mockSavedAddress: Partial<ShippingAddress> = {
  fullName: "John Smith",
  phone: "+1 (555) 123-4567",
  zipCode: "89101",
  streetAddress: "123 Heritage Boulevard",
  cityState: "Las Vegas, NV",
  notes: "",
};

export default function CheckoutPage() {
  const router = useRouter();
  const { items, maxItems, removeItem, clearCart } = useCartStore();
  const [isClient, setIsClient] = useState(false);
  const [shippingData, setShippingData] = useState<ShippingAddress>({
    fullName: mockSavedAddress.fullName || "",
    phone: mockSavedAddress.phone || "",
    zipCode: mockSavedAddress.zipCode || "",
    streetAddress: mockSavedAddress.streetAddress || "",
    cityState: mockSavedAddress.cityState || "",
    notes: mockSavedAddress.notes || "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle hydration mismatch
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Convert cart items to OrderItem format
  const orderItems: OrderItem[] = items.map((item) => ({
    id: item.productId,
    name: item.productName,
    category: item.category,
    size: item.size,
    image: item.image,
  }));

  const handleRemoveItem = (itemId: string) => {
    removeItem(itemId);
  };

  const handleShippingChange = (data: ShippingAddress) => {
    setShippingData(data);
  };

  const handleConfirmOrder = async () => {
    // Validate required fields
    if (
      !shippingData.fullName ||
      !shippingData.phone ||
      !shippingData.zipCode ||
      !shippingData.streetAddress ||
      !shippingData.cityState
    ) {
      alert("Please fill in all required fields.");
      return;
    }

    if (items.length === 0) {
      alert("Please select at least one item.");
      return;
    }

    setIsSubmitting(true);

    try {
      // Parse cityState (format: "City, State")
      const [city, state] = shippingData.cityState
        .split(",")
        .map((s) => s.trim());

      // Prepare order input
      const orderInput: CreateOrderInput = {
        items: items.map((item) => ({
          product_id: item.productId,
          size: item.size,
          quantity: 1, // Each cart item is quantity 1
        })),
        shipping_address: {
          recipient_name: shippingData.fullName,
          phone: shippingData.phone,
          address_line1: shippingData.streetAddress,
          address_line2: "",
          city: city || "",
          state: state || "",
          postal_code: shippingData.zipCode,
          country: "US", // Default to US
        },
        notes: shippingData.notes,
      };

      // Create order using server action
      const result = await createOrderAction(orderInput);

      // Check if result has error (server action didn't redirect)
      if (result && !result.success) {
        alert(`주문 실패: ${result.error}\n${result.details || ""}`);
        return;
      }

      // Clear cart after successful order
      clearCart();

      // Server action will redirect to /checkout/complete?order_id=...
    } catch (error) {
      console.error("Failed to create order:", error);
      alert("주문 처리 중 오류가 발생했습니다. 다시 시도해주세요.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Redirect to products if cart is empty (after hydration)
  useEffect(() => {
    if (isClient && items.length === 0 && !isSubmitting) {
      // Give a small delay to prevent immediate redirect during order completion
      const timer = setTimeout(() => {
        if (items.length === 0) {
          router.push("/products");
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [isClient, items.length, isSubmitting, router]);

  // Show loading state during hydration
  if (!isClient) {
    return (
      <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      {/* Header with Progress Steps */}
      <CheckoutHeader currentStep={2} />

      {/* Main Content */}
      <main className="pt-[100px] min-h-screen flex">
        {/* Shipping Form */}
        <ShippingForm
          initialData={mockSavedAddress}
          onChange={handleShippingChange}
        />

        {/* Order Summary */}
        <OrderSummary
          items={orderItems}
          maxItems={maxItems}
          onRemoveItem={handleRemoveItem}
          onConfirm={handleConfirmOrder}
          isSubmitting={isSubmitting}
        />
      </main>
    </div>
  );
}
