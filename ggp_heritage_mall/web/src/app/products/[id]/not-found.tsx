import Link from "next/link";
import { PackageX } from "lucide-react";

export default function ProductNotFound() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text-primary)] flex items-center justify-center">
      <div className="text-center px-4">
        <PackageX className="w-20 h-20 text-[var(--color-gold)] mx-auto mb-6" />
        <h1 className="font-heading text-4xl font-medium mb-4">
          Product Not Found
        </h1>
        <p className="text-[var(--color-text-secondary)] mb-8 max-w-md mx-auto">
          Sorry, we couldn't find the product you're looking for. It may have been removed or is no longer available.
        </p>
        <Link
          href="/products"
          className="inline-flex items-center justify-center px-6 py-3 bg-[var(--color-gold)] hover:bg-[#C5A028] text-[var(--color-background)] font-medium rounded-xl transition-all duration-300"
        >
          Back to Products
        </Link>
      </div>
    </div>
  );
}
