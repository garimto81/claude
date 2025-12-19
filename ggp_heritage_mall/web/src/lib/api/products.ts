import { createClient } from "@/lib/supabase/server";
import type { Database } from "@/types/database";

// Type definitions for API responses
type ProductRow = Database["public"]["Tables"]["products"]["Row"];
type CategoryRow = Database["public"]["Tables"]["categories"]["Row"];
type InventoryRow = Database["public"]["Tables"]["inventory"]["Row"];

export interface ProductWithInventory extends ProductRow {
  category: CategoryRow | null;
  inventory: InventoryRow[];
}

export interface GetProductsOptions {
  categoryId?: string;
  tierRequired?: "silver" | "gold";
  isActive?: boolean;
}

/**
 * 제품 목록 조회
 * @param options - 필터링 옵션 (categoryId, tierRequired, isActive)
 * @returns 제품 목록 (카테고리 및 재고 정보 포함)
 */
export async function getProducts(
  options: GetProductsOptions = {}
): Promise<ProductWithInventory[]> {
  const supabase = await createClient();

  // Base query with category and inventory joins
  let query = supabase
    .from("products")
    .select(
      `
      *,
      category:categories(*),
      inventory(*)
    `
    )
    .order("created_at", { ascending: false });

  // Apply filters
  if (options.categoryId) {
    query = query.eq("category_id", options.categoryId);
  }

  if (options.tierRequired) {
    query = query.eq("tier_required", options.tierRequired);
  }

  // Default to active products only
  const isActive = options.isActive !== undefined ? options.isActive : true;
  query = query.eq("is_active", isActive);

  const { data, error } = await query;

  if (error) {
    console.error("Error fetching products:", error);
    throw new Error(`Failed to fetch products: ${error.message}`);
  }

  return (data || []) as ProductWithInventory[];
}

/**
 * 제품 상세 조회 (재고 정보 포함)
 * @param id - 제품 ID
 * @returns 제품 상세 정보 (카테고리 및 재고 정보 포함)
 */
export async function getProductById(
  id: string
): Promise<ProductWithInventory | null> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("products")
    .select(
      `
      *,
      category:categories(*),
      inventory(*)
    `
    )
    .eq("id", id)
    .eq("is_active", true)
    .single();

  if (error) {
    if (error.code === "PGRST116") {
      // No rows returned
      return null;
    }
    console.error("Error fetching product:", error);
    throw new Error(`Failed to fetch product: ${error.message}`);
  }

  return data as ProductWithInventory;
}

/**
 * 카테고리 목록 조회
 * @returns 활성화된 카테고리 목록 (sort_order 순)
 */
export async function getCategories(): Promise<CategoryRow[]> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("categories")
    .select("*")
    .eq("is_active", true)
    .order("sort_order", { ascending: true });

  if (error) {
    console.error("Error fetching categories:", error);
    throw new Error(`Failed to fetch categories: ${error.message}`);
  }

  return data || [];
}

/**
 * 카테고리 ID로 카테고리 조회
 * @param id - 카테고리 ID
 * @returns 카테고리 정보
 */
export async function getCategoryById(
  id: string
): Promise<CategoryRow | null> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("categories")
    .select("*")
    .eq("id", id)
    .eq("is_active", true)
    .single();

  if (error) {
    if (error.code === "PGRST116") {
      return null;
    }
    console.error("Error fetching category:", error);
    throw new Error(`Failed to fetch category: ${error.message}`);
  }

  return data;
}

/**
 * 특정 제품의 재고 정보 조회
 * @param productId - 제품 ID
 * @returns 재고 목록 (사이즈별)
 */
export async function getProductInventory(
  productId: string
): Promise<InventoryRow[]> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("inventory")
    .select("*")
    .eq("product_id", productId)
    .order("size", { ascending: true });

  if (error) {
    console.error("Error fetching inventory:", error);
    throw new Error(`Failed to fetch inventory: ${error.message}`);
  }

  return data || [];
}
