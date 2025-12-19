"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { ProductCard, CategoryFilter, ActionBar } from "@/components/products";
import type { Product } from "@/components/products";
import { Header } from "@/components/layout";
import { useCartStore } from "@/stores/cartStore";
import type { ProductWithInventory } from "@/lib/api/products";

interface Category {
  id: string;
  name: string;
  slug: string;
}

interface ProductsClientProps {
  products: ProductWithInventory[];
  categories: Category[];
}

export function ProductsClient({ products, categories }: ProductsClientProps) {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  // Cart store
  const {
    items,
    maxItems,
    tierName,
    addItem,
    removeItem,
    isInCart,
    getItemSize,
    canAddMore,
  } = useCartStore();

  // Transform Supabase products to ProductCard format
  const transformedProducts: Product[] = useMemo(() => {
    return products.map((product) => ({
      id: product.id,
      name: product.name,
      description: product.description,
      category: product.category?.name || "Unknown",
      images: product.images,
      inventory: product.inventory.map((inv) => ({
        size: inv.size,
        quantity: inv.quantity,
      })),
      isNew: false, // TODO: Add logic to determine if product is new
      isLimited: false, // TODO: Add logic to determine if product is limited
    }));
  }, [products]);

  // Filter products by category
  const filteredProducts = useMemo(() => {
    if (!selectedCategory) return transformedProducts;

    const category = categories.find((c) => c.id === selectedCategory);
    if (!category) return transformedProducts;

    return transformedProducts.filter((p) => p.category === category.name);
  }, [selectedCategory, transformedProducts, categories]);

  const handleSelect = (productId: string, size: string) => {
    const product = transformedProducts.find((p) => p.id === productId);
    if (product) {
      addItem({
        productId,
        productName: product.name,
        category: product.category,
        size,
        image: product.images[0] || "",
      });
    }
  };

  const handleDeselect = (productId: string) => {
    removeItem(productId);
  };

  const handleCheckout = () => {
    router.push("/checkout");
  };

  // Convert cart items to ActionBar format
  const selectedItems = items.map((item) => ({
    productId: item.productId,
    productName: item.productName,
    size: item.size,
  }));

  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="pt-[100px] pb-[120px]">
        {/* Page Header */}
        <div className="py-[60px] text-center bg-[var(--color-surface)] border-b border-[#2A2A2A]">
          <h1 className="font-heading text-[48px] font-normal mb-4">
            Heritage Collection
          </h1>
          <p className="text-[16px] text-[var(--color-text-secondary)] max-w-[600px] mx-auto">
            Premium items curated exclusively for {tierName} Members.
            You may select up to {maxItems} items.
          </p>
        </div>

        {/* Filter Bar */}
        <CategoryFilter
          categories={categories}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
        />

        {/* Products Grid */}
        <section className="p-[60px]">
          <div
            className={
              viewMode === "grid"
                ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-[30px] max-w-[1600px] mx-auto"
                : "flex flex-col gap-4 max-w-[1200px] mx-auto"
            }
          >
            {filteredProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                isSelected={isInCart(product.id)}
                selectedSize={getItemSize(product.id)}
                onSelect={handleSelect}
                onDeselect={handleDeselect}
                disabled={!canAddMore() && !isInCart(product.id)}
              />
            ))}
          </div>

          {filteredProducts.length === 0 && (
            <div className="text-center py-20">
              <p className="text-[var(--color-text-secondary)]">
                No products found in this category.
              </p>
            </div>
          )}
        </section>
      </main>

      {/* Action Bar */}
      <ActionBar
        selectedItems={selectedItems}
        maxItems={maxItems}
        onCheckout={handleCheckout}
      />
    </div>
  );
}
