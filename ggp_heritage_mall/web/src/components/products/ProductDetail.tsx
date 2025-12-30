"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShoppingCart, Check, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { useCartStore } from "@/stores/cartStore";
import type { ProductWithInventory } from "@/lib/api/products";

interface ProductDetailProps {
  product: ProductWithInventory;
}

export function ProductDetail({ product }: ProductDetailProps) {
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  const [showAddedNotification, setShowAddedNotification] = useState(false);

  const { addItem, isInCart, getItemSize, canAddMore, maxItems, items } = useCartStore();

  const isProductInCart = isInCart(product.id);
  const currentCartSize = getItemSize(product.id);
  const totalStock = product.inventory.reduce((sum, inv) => sum + inv.quantity, 0);
  const isOutOfStock = totalStock === 0;
  const isLowStock = totalStock > 0 && totalStock <= 5;

  // Initialize selected size to cart size or first available size
  useEffect(() => {
    if (currentCartSize) {
      setSelectedSize(currentCartSize);
    } else {
      const availableSize = product.inventory.find(inv => inv.quantity > 0)?.size;
      if (availableSize) {
        setSelectedSize(availableSize);
      }
    }
  }, [currentCartSize, product.inventory]);

  const handleAddToCart = () => {
    if (!selectedSize || isOutOfStock) return;

    const selectedInventory = product.inventory.find(inv => inv.size === selectedSize);
    if (!selectedInventory || selectedInventory.quantity === 0) return;

    // Check if cart is full (only if not already in cart)
    if (!isProductInCart && !canAddMore()) {
      return;
    }

    addItem({
      productId: product.id,
      productName: product.name,
      category: product.category?.name || "Uncategorized",
      size: selectedSize,
      image: product.images[0] || undefined,
    });

    // Show notification
    setShowAddedNotification(true);
    setTimeout(() => setShowAddedNotification(false), 3000);
  };

  const getStockText = () => {
    if (isOutOfStock) return "Out of Stock";
    if (isLowStock) return `Only ${totalStock} left in stock`;
    return `${totalStock} items in stock`;
  };

  const getStockColor = () => {
    if (isOutOfStock) return "text-[var(--color-text-muted)]";
    if (isLowStock) return "text-[#E74C3C]";
    return "text-[#2ECC71]";
  };

  const canSelectSize = (inventory: typeof product.inventory[0]) => {
    return inventory.quantity > 0;
  };

  const isCartFull = items.length >= maxItems && !isProductInCart;

  return (
    <div className="space-y-8">
      {/* Category & Badges */}
      <div className="flex items-center gap-3">
        <span className="text-xs font-medium tracking-[2px] text-[var(--color-gold)] uppercase">
          {product.category?.name || "Uncategorized"}
        </span>
        {isOutOfStock ? (
          <Badge variant="secondary" className="bg-[var(--color-text-muted)] text-[var(--color-background)]">
            Sold Out
          </Badge>
        ) : product.tier_required === "gold" ? (
          <Badge className="bg-[var(--color-gold)] text-[var(--color-background)] hover:bg-[var(--color-gold)]">
            Gold Tier
          </Badge>
        ) : (
          <Badge className="bg-[#C0C0C0] text-[var(--color-background)] hover:bg-[#C0C0C0]">
            Silver Tier
          </Badge>
        )}
      </div>

      {/* Product Name */}
      <div>
        <h1 className="font-heading text-4xl md:text-5xl font-medium mb-3">
          {product.name}
        </h1>
        {product.description && (
          <p className="text-base text-[var(--color-text-secondary)] leading-relaxed">
            {product.description}
          </p>
        )}
      </div>

      {/* Stock Status */}
      <div className="flex items-center gap-2">
        <div className={cn("w-2 h-2 rounded-full", isOutOfStock ? "bg-[var(--color-text-muted)]" : isLowStock ? "bg-[#E74C3C]" : "bg-[#2ECC71]")} />
        <span className={cn("text-sm", getStockColor())}>
          {getStockText()}
        </span>
      </div>

      {/* Size Selection */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-[var(--color-text-primary)]">
            Select Size
          </h3>
          {selectedSize && (
            <span className="text-xs text-[var(--color-text-secondary)]">
              Selected: {selectedSize}
            </span>
          )}
        </div>

        <div className="grid grid-cols-4 sm:grid-cols-6 gap-3">
          {product.inventory
            .sort((a, b) => a.size.localeCompare(b.size))
            .map((inv) => {
              const isAvailable = canSelectSize(inv);
              const isSelected = selectedSize === inv.size;

              return (
                <button
                  key={inv.size}
                  onClick={() => isAvailable && setSelectedSize(inv.size)}
                  disabled={!isAvailable}
                  className={cn(
                    "relative aspect-square rounded-xl border-2 transition-all duration-300",
                    "flex flex-col items-center justify-center gap-1",
                    isSelected && isAvailable
                      ? "bg-[var(--color-gold)] border-[var(--color-gold)] text-[var(--color-background)]"
                      : isAvailable
                      ? "border-[#2A2A2A] hover:border-[var(--color-gold)] text-[var(--color-text-primary)]"
                      : "border-[#2A2A2A] text-[var(--color-text-muted)] opacity-40 cursor-not-allowed"
                  )}
                >
                  <span className="text-sm font-medium">{inv.size}</span>
                  <span className={cn("text-[10px]", isSelected && isAvailable ? "text-[var(--color-background)]/80" : "text-[var(--color-text-secondary)]")}>
                    {inv.quantity > 0 ? `${inv.quantity} left` : "Out"}
                  </span>
                  {!isAvailable && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-full h-[2px] bg-[var(--color-text-muted)] rotate-45" />
                    </div>
                  )}
                </button>
              );
            })}
        </div>
      </div>

      {/* Add to Cart Button */}
      <div className="space-y-3">
        {isCartFull && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-2 p-3 bg-[#E74C3C]/10 border border-[#E74C3C]/30 rounded-lg"
          >
            <AlertCircle className="w-4 h-4 text-[#E74C3C]" />
            <span className="text-sm text-[#E74C3C]">
              Cart is full ({maxItems} items max). Remove an item to add this product.
            </span>
          </motion.div>
        )}

        <motion.button
          onClick={handleAddToCart}
          disabled={!selectedSize || isOutOfStock || isCartFull}
          whileHover={!isOutOfStock && !isCartFull ? { scale: 1.02 } : undefined}
          whileTap={!isOutOfStock && !isCartFull ? { scale: 0.98 } : undefined}
          className={cn(
            "w-full py-4 px-6 rounded-xl font-medium text-base transition-all duration-300",
            "flex items-center justify-center gap-3",
            isOutOfStock || isCartFull
              ? "bg-[#2A2A2A] text-[var(--color-text-muted)] cursor-not-allowed"
              : isProductInCart
              ? "bg-[#2ECC71] hover:bg-[#27AE60] text-white"
              : "bg-[var(--color-gold)] hover:bg-[#C5A028] text-[var(--color-background)]"
          )}
        >
          {isProductInCart ? (
            <>
              <Check className="w-5 h-5" />
              Update Cart ({currentCartSize} → {selectedSize})
            </>
          ) : (
            <>
              <ShoppingCart className="w-5 h-5" />
              Add to Cart
            </>
          )}
        </motion.button>

        {/* Current cart info */}
        <div className="text-center text-sm text-[var(--color-text-secondary)]">
          {items.length} / {maxItems} items in cart
        </div>
      </div>

      {/* Added to Cart Notification */}
      <AnimatePresence>
        {showAddedNotification && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed bottom-8 right-8 z-50 p-4 bg-[#2ECC71] text-white rounded-xl shadow-2xl flex items-center gap-3"
          >
            <Check className="w-5 h-5" />
            <span className="font-medium">
              {isProductInCart ? "Cart updated!" : "Added to cart!"}
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
