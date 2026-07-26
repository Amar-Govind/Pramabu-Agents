import { ProductCarousel } from "@/components/ProductCarousel";
import type { Product } from "@/lib/products";

export function ProductRail({
  title,
  subtitle,
  products,
}: {
  title: string;
  subtitle?: string;
  products: Product[];
}) {
  return <ProductCarousel title={title} subtitle={subtitle} products={products} />;
}
