import { ProductCard } from "@/components/ProductCard";
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
  if (!products.length) return null;

  return (
    <section className="mt-16">
      <div className="mb-6 max-w-2xl">
        <h2 className="font-display text-3xl text-ink md:text-4xl">{title}</h2>
        {subtitle ? <p className="mt-2 text-sm text-ink/65">{subtitle}</p> : null}
      </div>
      <div className="no-scrollbar -mx-5 flex gap-4 overflow-x-auto px-5 pb-2 md:mx-0 md:grid md:grid-cols-4 md:gap-6 md:overflow-visible md:px-0">
        {products.map((product) => (
          <div key={product.slug} className="min-w-[220px] md:min-w-0">
            <ProductCard product={product} />
          </div>
        ))}
      </div>
    </section>
  );
}
