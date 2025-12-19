import { describe, it, expect, beforeEach } from "vitest";
import { useCartStore } from "../cartStore";

describe("cartStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useCartStore.setState({
      items: [],
      maxItems: 5,
      tierName: "Gold",
    });
  });

  describe("addItem", () => {
    it("should add item to empty cart", () => {
      const { addItem, items } = useCartStore.getState();

      addItem({
        productId: "1",
        productName: "Test Product",
        category: "Test",
        size: "M",
      });

      expect(useCartStore.getState().items).toHaveLength(1);
      expect(useCartStore.getState().items[0].productId).toBe("1");
    });

    it("should update size if product already exists in cart", () => {
      const { addItem } = useCartStore.getState();

      addItem({
        productId: "1",
        productName: "Test Product",
        category: "Test",
        size: "M",
      });

      addItem({
        productId: "1",
        productName: "Test Product",
        category: "Test",
        size: "L",
      });

      const { items } = useCartStore.getState();
      expect(items).toHaveLength(1);
      expect(items[0].size).toBe("L");
    });

    it("should not add item when max limit is reached", () => {
      useCartStore.setState({ maxItems: 2 });
      const { addItem } = useCartStore.getState();

      addItem({ productId: "1", productName: "Product 1", category: "Test", size: "M" });
      addItem({ productId: "2", productName: "Product 2", category: "Test", size: "M" });
      addItem({ productId: "3", productName: "Product 3", category: "Test", size: "M" });

      expect(useCartStore.getState().items).toHaveLength(2);
    });
  });

  describe("removeItem", () => {
    it("should remove item from cart", () => {
      const { addItem, removeItem } = useCartStore.getState();

      addItem({ productId: "1", productName: "Product 1", category: "Test", size: "M" });
      addItem({ productId: "2", productName: "Product 2", category: "Test", size: "M" });

      removeItem("1");

      const { items } = useCartStore.getState();
      expect(items).toHaveLength(1);
      expect(items[0].productId).toBe("2");
    });

    it("should not affect other items when removing one", () => {
      const { addItem, removeItem } = useCartStore.getState();

      addItem({ productId: "1", productName: "Product 1", category: "Test", size: "M" });
      addItem({ productId: "2", productName: "Product 2", category: "Test", size: "L" });

      removeItem("1");

      const { items } = useCartStore.getState();
      expect(items[0].size).toBe("L");
    });
  });

  describe("updateItemSize", () => {
    it("should update size of specific item", () => {
      const { addItem, updateItemSize } = useCartStore.getState();

      addItem({ productId: "1", productName: "Product 1", category: "Test", size: "M" });

      updateItemSize("1", "XL");

      expect(useCartStore.getState().items[0].size).toBe("XL");
    });

    it("should not update size of other items", () => {
      const { addItem, updateItemSize } = useCartStore.getState();

      addItem({ productId: "1", productName: "Product 1", category: "Test", size: "M" });
      addItem({ productId: "2", productName: "Product 2", category: "Test", size: "S" });

      updateItemSize("1", "XL");

      const { items } = useCartStore.getState();
      expect(items[0].size).toBe("XL");
      expect(items[1].size).toBe("S");
    });
  });

  describe("clearCart", () => {
    it("should remove all items from cart", () => {
      const { addItem, clearCart } = useCartStore.getState();

      addItem({ productId: "1", productName: "Product 1", category: "Test", size: "M" });
      addItem({ productId: "2", productName: "Product 2", category: "Test", size: "M" });

      clearCart();

      expect(useCartStore.getState().items).toHaveLength(0);
    });
  });

  describe("setVipInfo", () => {
    it("should update maxItems and tierName", () => {
      const { setVipInfo } = useCartStore.getState();

      setVipInfo(10, "Platinum");

      const state = useCartStore.getState();
      expect(state.maxItems).toBe(10);
      expect(state.tierName).toBe("Platinum");
    });
  });

  describe("isInCart", () => {
    it("should return true for item in cart", () => {
      const { addItem, isInCart } = useCartStore.getState();

      addItem({ productId: "1", productName: "Product 1", category: "Test", size: "M" });

      expect(useCartStore.getState().isInCart("1")).toBe(true);
    });

    it("should return false for item not in cart", () => {
      expect(useCartStore.getState().isInCart("999")).toBe(false);
    });
  });

  describe("getItemSize", () => {
    it("should return size of item in cart", () => {
      const { addItem } = useCartStore.getState();

      addItem({ productId: "1", productName: "Product 1", category: "Test", size: "M" });

      expect(useCartStore.getState().getItemSize("1")).toBe("M");
    });

    it("should return null for item not in cart", () => {
      expect(useCartStore.getState().getItemSize("999")).toBeNull();
    });
  });

  describe("canAddMore", () => {
    it("should return true when cart has space", () => {
      const { addItem } = useCartStore.getState();

      addItem({ productId: "1", productName: "Product 1", category: "Test", size: "M" });

      expect(useCartStore.getState().canAddMore()).toBe(true);
    });

    it("should return false when cart is full", () => {
      useCartStore.setState({ maxItems: 1 });
      const { addItem } = useCartStore.getState();

      addItem({ productId: "1", productName: "Product 1", category: "Test", size: "M" });

      expect(useCartStore.getState().canAddMore()).toBe(false);
    });

    it("should return true for empty cart", () => {
      expect(useCartStore.getState().canAddMore()).toBe(true);
    });
  });
});
