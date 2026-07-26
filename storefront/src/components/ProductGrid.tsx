import type { Product } from "@/lib/products";
import { ProductCard } from "@/components/ProductCard";

export function ProductGrid({ products }: { products: Product[] }) {
  if (!products.length) {
    return <p className="text-ink/70">No products found.</p>;
  }

  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-10 md:grid-cols-3 md:gap-x-7 lg:grid-cols-4">
      {products.map((product) => (
        <ProductCard key={product.slug} product={product} />
      ))}
    </div>
  );
}
