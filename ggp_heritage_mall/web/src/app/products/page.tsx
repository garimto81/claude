import { getProducts, getCategories } from "@/lib/api/products";
import { ProductsClient } from "./products-client";

export default async function ProductsPage() {
  const [products, categories] = await Promise.all([
    getProducts(),
    getCategories(),
  ]);

  return <ProductsClient products={products} categories={categories} />;
}
