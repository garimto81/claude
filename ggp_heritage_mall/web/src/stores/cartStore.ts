import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface CartItem {
  productId: string;
  productName: string;
  category: string;
  size: string;
  image?: string;
}

interface CartState {
  items: CartItem[];
  maxItems: number;
  tierName: string;

  // Actions
  addItem: (item: CartItem) => void;
  removeItem: (productId: string) => void;
  updateItemSize: (productId: string, size: string) => void;
  clearCart: () => void;
  setVipInfo: (maxItems: number, tierName: string) => void;

  // Selectors
  isInCart: (productId: string) => boolean;
  getItemSize: (productId: string) => string | null;
  canAddMore: () => boolean;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      maxItems: 5,
      tierName: "Gold",

      addItem: (item) => {
        const { items, maxItems } = get();
        const existingIndex = items.findIndex(
          (i) => i.productId === item.productId
        );

        if (existingIndex !== -1) {
          const newItems = [...items];
          newItems[existingIndex] = item;
          set({ items: newItems });
          return;
        }

        if (items.length >= maxItems) {
          return;
        }

        set({ items: [...items, item] });
      },

      removeItem: (productId) => {
        set((state) => ({
          items: state.items.filter((i) => i.productId !== productId),
        }));
      },

      updateItemSize: (productId, size) => {
        set((state) => ({
          items: state.items.map((item) =>
            item.productId === productId ? { ...item, size } : item
          ),
        }));
      },

      clearCart: () => {
        set({ items: [] });
      },

      setVipInfo: (maxItems, tierName) => {
        set({ maxItems, tierName });
      },

      isInCart: (productId) => {
        return get().items.some((i) => i.productId === productId);
      },

      getItemSize: (productId) => {
        const item = get().items.find((i) => i.productId === productId);
        return item?.size ?? null;
      },

      canAddMore: () => {
        const { items, maxItems } = get();
        return items.length < maxItems;
      },
    }),
    {
      name: "ggp-cart-storage",
    }
  )
);
