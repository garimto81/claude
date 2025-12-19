import { ProductCard, CategoryFilter, ActionBar } from "@/components/products";
import { Header } from "@/components/layout";
import { getProducts, getCategories } from "@/lib/api/products";
import type { ProductWithInventory } from "@/lib/api/products";
import { ProductsClient } from "./products-client";

// Server Component - Fetch data from Supabase
export default async function ProductsPage() {
  // Fetch products and categories from Supabase
  const [products, categories] = await Promise.all([
    getProducts(),
    getCategories(),
  ]);

  // Transform categories for CategoryFilter component
  const formattedCategories = categories.map((cat) => ({
    id: cat.id,
    name: cat.name,
    slug: cat.slug,
  }));

  return <ProductsClient products={products} categories={formattedCategories} />;
}
