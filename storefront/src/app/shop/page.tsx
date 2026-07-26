import type { Metadata } from "next";
import { ProductGrid } from "@/components/ProductGrid";
import { products } from "@/lib/products";

export const metadata: Metadata = {
  title: "Shop",
  description: "Shop Parambu Organics oils, soaps, and gardening essentials.",
};

export default function ShopPage() {
  return (
    <div className="mx-auto max-w-site px-5 py-14 md:px-8 md:py-20">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-leaf">Shop</p>
      <h1 className="mt-3 font-display text-5xl text-ink">All essentials</h1>
      <p className="mt-4 max-w-xl text-base text-ink/70">
        Pure heritage care across oils, handcrafted soaps, and natural growing media.
      </p>
      <div className="mt-12">
        <ProductGrid products={products} />
      </div>
    </div>
  );
}
