import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getProductById } from "@/lib/api/products";
import { ImageGallery } from "@/components/products/ImageGallery";
import { ProductDetail } from "@/components/products/ProductDetail";

interface ProductPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { id } = await params;

  const product = await getProductById(id);

  if (!product) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text-primary)]">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Back Navigation */}
        <Link
          href="/products"
          className="inline-flex items-center gap-2 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-gold)] transition-colors duration-300 mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Products
        </Link>

        {/* Product Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16">
          {/* Left: Image Gallery */}
          <div>
            <ImageGallery images={product.images} productName={product.name} />
          </div>

          {/* Right: Product Details */}
          <div>
            <ProductDetail product={product} />
          </div>
        </div>

        {/* Additional Product Information */}
        {product.description && (
          <div className="mt-16 border-t border-[#2A2A2A] pt-12">
            <h2 className="font-heading text-2xl font-medium mb-6">
              Product Details
            </h2>
            <div className="prose prose-invert max-w-none">
              <p className="text-[var(--color-text-secondary)] leading-relaxed whitespace-pre-line">
                {product.description}
              </p>
            </div>
          </div>
        )}

        {/* Product Specifications */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[#151515] border border-[#2A2A2A] rounded-xl p-6">
            <h3 className="text-sm font-medium text-[var(--color-gold)] uppercase tracking-wider mb-2">
              Category
            </h3>
            <p className="text-base text-[var(--color-text-primary)]">
              {product.category?.name || "Uncategorized"}
            </p>
          </div>

          <div className="bg-[#151515] border border-[#2A2A2A] rounded-xl p-6">
            <h3 className="text-sm font-medium text-[var(--color-gold)] uppercase tracking-wider mb-2">
              Tier Required
            </h3>
            <p className="text-base text-[var(--color-text-primary)] capitalize">
              {product.tier_required} VIP
            </p>
          </div>

          <div className="bg-[#151515] border border-[#2A2A2A] rounded-xl p-6">
            <h3 className="text-sm font-medium text-[var(--color-gold)] uppercase tracking-wider mb-2">
              Available Sizes
            </h3>
            <p className="text-base text-[var(--color-text-primary)]">
              {product.inventory
                .filter(inv => inv.quantity > 0)
                .map(inv => inv.size)
                .join(", ") || "Out of stock"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Generate metadata for SEO
export async function generateMetadata({ params }: ProductPageProps) {
  const { id } = await params;
  const product = await getProductById(id);

  if (!product) {
    return {
      title: "Product Not Found",
    };
  }

  return {
    title: `${product.name} | GGP Heritage Mall`,
    description: product.description || `Shop ${product.name} at GGP Heritage Mall`,
  };
}
