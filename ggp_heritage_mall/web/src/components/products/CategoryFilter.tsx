"use client";

import { cn } from "@/lib/utils";
import { LayoutGrid, List } from "lucide-react";

interface Category {
  id: string;
  name: string;
  slug: string;
}

interface CategoryFilterProps {
  categories: Category[];
  selectedCategory: string | null;
  onCategoryChange: (categoryId: string | null) => void;
  viewMode: "grid" | "list";
  onViewModeChange: (mode: "grid" | "list") => void;
}

export function CategoryFilter({
  categories,
  selectedCategory,
  onCategoryChange,
  viewMode,
  onViewModeChange,
}: CategoryFilterProps) {
  return (
    <div className="flex justify-between items-center py-6 px-[60px] border-b border-[#2A2A2A]">
      {/* Category Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => onCategoryChange(null)}
          className={cn(
            "px-5 py-2.5 rounded-full text-[13px] font-medium transition-all duration-300 border",
            selectedCategory === null
              ? "bg-[var(--color-gold)] border-[var(--color-gold)] text-[var(--color-background)]"
              : "bg-transparent border-[#2A2A2A] text-[var(--color-text-secondary)] hover:border-[var(--color-text-secondary)]"
          )}
        >
          All
        </button>
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => onCategoryChange(category.id)}
            className={cn(
              "px-5 py-2.5 rounded-full text-[13px] font-medium transition-all duration-300 border",
              selectedCategory === category.id
                ? "bg-[var(--color-gold)] border-[var(--color-gold)] text-[var(--color-background)]"
                : "bg-transparent border-[#2A2A2A] text-[var(--color-text-secondary)] hover:border-[var(--color-text-secondary)]"
            )}
          >
            {category.name}
          </button>
        ))}
      </div>

      {/* View Toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => onViewModeChange("grid")}
          className={cn(
            "w-10 h-10 rounded-lg border flex items-center justify-center transition-all duration-300",
            viewMode === "grid"
              ? "border-[var(--color-gold)] bg-[rgba(212,175,55,0.1)]"
              : "border-[#2A2A2A] hover:border-[var(--color-text-secondary)]"
          )}
        >
          <LayoutGrid
            className={cn(
              "w-[18px] h-[18px]",
              viewMode === "grid"
                ? "text-[var(--color-gold)]"
                : "text-[var(--color-text-secondary)]"
            )}
          />
        </button>
        <button
          onClick={() => onViewModeChange("list")}
          className={cn(
            "w-10 h-10 rounded-lg border flex items-center justify-center transition-all duration-300",
            viewMode === "list"
              ? "border-[var(--color-gold)] bg-[rgba(212,175,55,0.1)]"
              : "border-[#2A2A2A] hover:border-[var(--color-text-secondary)]"
          )}
        >
          <List
            className={cn(
              "w-[18px] h-[18px]",
              viewMode === "list"
                ? "text-[var(--color-gold)]"
                : "text-[var(--color-text-secondary)]"
            )}
          />
        </button>
      </div>
    </div>
  );
}
