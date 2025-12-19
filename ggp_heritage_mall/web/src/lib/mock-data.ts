import type { Product } from "@/components/products";

export const mockCategories = [
  { id: "1", name: "Apparel", slug: "apparel" },
  { id: "2", name: "Accessories", slug: "accessories" },
  { id: "3", name: "Collectibles", slug: "collectibles" },
  { id: "4", name: "Lifestyle", slug: "lifestyle" },
];

export const mockProducts: Product[] = [
  {
    id: "1",
    name: "Premium Hoodie",
    description: "Oversized hoodie in premium cotton",
    category: "Apparel",
    images: ["https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400&h=400&fit=crop"],
    inventory: [
      { size: "S", quantity: 5 },
      { size: "M", quantity: 12 },
      { size: "L", quantity: 8 },
      { size: "XL", quantity: 3 },
    ],
    isNew: true,
  },
  {
    id: "2",
    name: "Card Protector Set",
    description: "Premium card protector 3-piece set",
    category: "Accessories",
    images: ["https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop"],
    inventory: [{ size: "One", quantity: 25 }],
  },
  {
    id: "3",
    name: "Signature Chips",
    description: "Limited edition signature chip set",
    category: "Collectibles",
    images: ["https://images.unsplash.com/photo-1596451190630-186aff535bf2?w=400&h=400&fit=crop"],
    inventory: [{ size: "One", quantity: 3 }],
    isLimited: true,
  },
  {
    id: "4",
    name: "Travel Kit",
    description: "Premium travel pouch set",
    category: "Lifestyle",
    images: ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop"],
    inventory: [{ size: "One", quantity: 18 }],
  },
  {
    id: "5",
    name: "Classic Cap",
    description: "Embroidered logo cap",
    category: "Apparel",
    images: ["https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=400&h=400&fit=crop"],
    inventory: [{ size: "One", quantity: 30 }],
  },
  {
    id: "6",
    name: "Leather Wallet",
    description: "Premium leather wallet",
    category: "Accessories",
    images: ["https://images.unsplash.com/photo-1627123424574-724758594e93?w=400&h=400&fit=crop"],
    inventory: [{ size: "One", quantity: 15 }],
    isNew: true,
  },
  {
    id: "7",
    name: "Gold Chip Set",
    description: "24K gold-plated chip set",
    category: "Collectibles",
    images: ["https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=400&h=400&fit=crop"],
    inventory: [{ size: "One", quantity: 0 }],
  },
  {
    id: "8",
    name: "Tumbler Set",
    description: "Insulated tumbler set",
    category: "Lifestyle",
    images: ["https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop"],
    inventory: [{ size: "One", quantity: 22 }],
  },
];

export const mockVipInfo = {
  tier: "gold" as const,
  tierName: "Gold",
  maxItems: 5,
};
