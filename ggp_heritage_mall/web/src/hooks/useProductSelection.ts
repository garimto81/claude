"use client";

import { useState, useCallback } from "react";

export interface SelectedProduct {
  productId: string;
  productName: string;
  size: string;
}

interface UseProductSelectionOptions {
  maxItems: number;
}

export function useProductSelection({ maxItems }: UseProductSelectionOptions) {
  const [selectedProducts, setSelectedProducts] = useState<Map<string, SelectedProduct>>(
    new Map()
  );

  const selectProduct = useCallback(
    (productId: string, productName: string, size: string) => {
      setSelectedProducts((prev) => {
        const newMap = new Map(prev);

        // If already selected, just update the size
        if (newMap.has(productId)) {
          newMap.set(productId, { productId, productName, size });
          return newMap;
        }

        // If at max capacity, don't add
        if (newMap.size >= maxItems) {
          return prev;
        }

        newMap.set(productId, { productId, productName, size });
        return newMap;
      });
    },
    [maxItems]
  );

  const deselectProduct = useCallback((productId: string) => {
    setSelectedProducts((prev) => {
      const newMap = new Map(prev);
      newMap.delete(productId);
      return newMap;
    });
  }, []);

  const isSelected = useCallback(
    (productId: string) => selectedProducts.has(productId),
    [selectedProducts]
  );

  const getSelectedSize = useCallback(
    (productId: string) => selectedProducts.get(productId)?.size ?? null,
    [selectedProducts]
  );

  const canSelectMore = selectedProducts.size < maxItems;

  const selectedItems = Array.from(selectedProducts.values());

  return {
    selectedProducts,
    selectedItems,
    selectProduct,
    deselectProduct,
    isSelected,
    getSelectedSize,
    canSelectMore,
    selectedCount: selectedProducts.size,
  };
}
