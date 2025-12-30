import { notFound } from "next/navigation";
import { getProductById } from "@/lib/api/products";
import { Header } from "@/components/layout";
import { ImageGallery, ProductDetail } from "@/components/products";

interface ProductPageProps {
  params: Promise<{ id: string }>;
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { id } = await params;
  const product = await getProductById(id);

  if (!product) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      <Header />

      <main className="pt-[100px] pb-[60px]">
        <div className="max-w-[1400px] mx-auto px-[60px]">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 py-12">
            {/* Image Gallery */}
            <ImageGallery images={product.images} productName={product.name} />

            {/* Product Details */}
            <ProductDetail product={product} />
          </div>
        </div>
      </main>
    </div>
  );
}
