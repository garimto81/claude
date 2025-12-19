import { describe, it, expect, beforeEach } from "vitest";
import { useCartStore } from "../cartStore";
import type { CartItem } from "../cartStore";

describe("useCartStore", () => {
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
      // Arrange
      const store = useCartStore.getState();
      const item: CartItem = {
        productId: "prod-1",
        productName: "Test Product",
        category: "jacket",
        size: "M",
        image: "test.jpg",
      };

      // Act
      store.addItem(item);

      // Assert
      const state = useCartStore.getState();
      expect(state.items).toHaveLength(1);
      expect(state.items[0]).toEqual(item);
    });

    it("should update size if product already exists in cart", () => {
      // Arrange
      const store = useCartStore.getState();
      const item1: CartItem = {
        productId: "prod-1",
        productName: "Test Product",
        category: "jacket",
        size: "M",
      };
      const item2: CartItem = {
        productId: "prod-1",
        productName: "Test Product",
        category: "jacket",
        size: "L",
      };

      // Act
      store.addItem(item1);
      store.addItem(item2);

      // Assert
      const state = useCartStore.getState();
      expect(state.items).toHaveLength(1);
      expect(state.items[0].size).toBe("L");
    });

    it("should not add item when max limit is reached", () => {
      // Arrange
      const store = useCartStore.getState();
      useCartStore.setState({ maxItems: 3 });

      const items: CartItem[] = [
        { productId: "prod-1", productName: "Product 1", category: "jacket", size: "M" },
        { productId: "prod-2", productName: "Product 2", category: "jacket", size: "L" },
        { productId: "prod-3", productName: "Product 3", category: "jacket", size: "S" },
      ];

      // Act - Add 3 items
      items.forEach((item) => store.addItem(item));

      // Try to add 4th item
      const fourthItem: CartItem = {
        productId: "prod-4",
        productName: "Product 4",
        category: "jacket",
        size: "M",
      };
      store.addItem(fourthItem);

      // Assert
      const state = useCartStore.getState();
      expect(state.items).toHaveLength(3);
      expect(state.items.find((i) => i.productId === "prod-4")).toBeUndefined();
    });
  });

  describe("removeItem", () => {
    it("should remove item from cart", () => {
      // Arrange
      const store = useCartStore.getState();
      const item: CartItem = {
        productId: "prod-1",
        productName: "Test Product",
        category: "jacket",
        size: "M",
      };
      store.addItem(item);

      // Act
      store.removeItem("prod-1");

      // Assert
      const state = useCartStore.getState();
      expect(state.items).toHaveLength(0);
    });

    it("should not affect other items when removing one", () => {
      // Arrange
      const store = useCartStore.getState();
      const items: CartItem[] = [
        { productId: "prod-1", productName: "Product 1", category: "jacket", size: "M" },
        { productId: "prod-2", productName: "Product 2", category: "jacket", size: "L" },
      ];
      items.forEach((item) => store.addItem(item));

      // Act
      store.removeItem("prod-1");

      // Assert
      const state = useCartStore.getState();
      expect(state.items).toHaveLength(1);
      expect(state.items[0].productId).toBe("prod-2");
    });
  });

  describe("updateItemSize", () => {
    it("should update size of specific item", () => {
      // Arrange
      const store = useCartStore.getState();
      const item: CartItem = {
        productId: "prod-1",
        productName: "Test Product",
        category: "jacket",
        size: "M",
      };
      store.addItem(item);

      // Act
      store.updateItemSize("prod-1", "XL");

      // Assert
      const state = useCartStore.getState();
      expect(state.items[0].size).toBe("XL");
    });

    it("should not update size of other items", () => {
      // Arrange
      const store = useCartStore.getState();
      const items: CartItem[] = [
        { productId: "prod-1", productName: "Product 1", category: "jacket", size: "M" },
        { productId: "prod-2", productName: "Product 2", category: "jacket", size: "L" },
      ];
      items.forEach((item) => store.addItem(item));

      // Act
      store.updateItemSize("prod-1", "XL");

      // Assert
      const state = useCartStore.getState();
      expect(state.items[0].size).toBe("XL");
      expect(state.items[1].size).toBe("L");
    });
  });

  describe("clearCart", () => {
    it("should remove all items from cart", () => {
      // Arrange
      const store = useCartStore.getState();
      const items: CartItem[] = [
        { productId: "prod-1", productName: "Product 1", category: "jacket", size: "M" },
        { productId: "prod-2", productName: "Product 2", category: "jacket", size: "L" },
      ];
      items.forEach((item) => store.addItem(item));

      // Act
      store.clearCart();

      // Assert
      const state = useCartStore.getState();
      expect(state.items).toHaveLength(0);
    });
  });

  describe("setVipInfo", () => {
    it("should update maxItems and tierName", () => {
      // Arrange
      const store = useCartStore.getState();

      // Act
      store.setVipInfo(3, "Silver");

      // Assert
      const state = useCartStore.getState();
      expect(state.maxItems).toBe(3);
      expect(state.tierName).toBe("Silver");
    });
  });

  describe("isInCart", () => {
    it("should return true for item in cart", () => {
      // Arrange
      const store = useCartStore.getState();
      const item: CartItem = {
        productId: "prod-1",
        productName: "Test Product",
        category: "jacket",
        size: "M",
      };
      store.addItem(item);

      // Act
      const result = store.isInCart("prod-1");

      // Assert
      expect(result).toBe(true);
    });

    it("should return false for item not in cart", () => {
      // Arrange
      const store = useCartStore.getState();

      // Act
      const result = store.isInCart("prod-999");

      // Assert
      expect(result).toBe(false);
    });
  });

  describe("getItemSize", () => {
    it("should return size of item in cart", () => {
      // Arrange
      const store = useCartStore.getState();
      const item: CartItem = {
        productId: "prod-1",
        productName: "Test Product",
        category: "jacket",
        size: "M",
      };
      store.addItem(item);

      // Act
      const result = store.getItemSize("prod-1");

      // Assert
      expect(result).toBe("M");
    });

    it("should return null for item not in cart", () => {
      // Arrange
      const store = useCartStore.getState();

      // Act
      const result = store.getItemSize("prod-999");

      // Assert
      expect(result).toBeNull();
    });
  });

  describe("canAddMore", () => {
    it("should return true when cart has space", () => {
      // Arrange
      const store = useCartStore.getState();
      useCartStore.setState({ maxItems: 5 });
      const items: CartItem[] = [
        { productId: "prod-1", productName: "Product 1", category: "jacket", size: "M" },
        { productId: "prod-2", productName: "Product 2", category: "jacket", size: "L" },
      ];
      items.forEach((item) => store.addItem(item));

      // Act
      const result = store.canAddMore();

      // Assert
      expect(result).toBe(true);
    });

    it("should return false when cart is full", () => {
      // Arrange
      const store = useCartStore.getState();
      useCartStore.setState({ maxItems: 2 });
      const items: CartItem[] = [
        { productId: "prod-1", productName: "Product 1", category: "jacket", size: "M" },
        { productId: "prod-2", productName: "Product 2", category: "jacket", size: "L" },
      ];
      items.forEach((item) => store.addItem(item));

      // Act
      const result = store.canAddMore();

      // Assert
      expect(result).toBe(false);
    });

    it("should return true for empty cart", () => {
      // Arrange
      const store = useCartStore.getState();

      // Act
      const result = store.canAddMore();

      // Assert
      expect(result).toBe(true);
    });
  });
});
