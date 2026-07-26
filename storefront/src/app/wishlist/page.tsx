"use client";

import Link from "next/link";
import { ProductGrid } from "@/components/ProductGrid";
import { getProductsBySlugs } from "@/lib/products";
import { useWishlist } from "@/store/wishlist";

export default function WishlistPage() {
  const slugs = useWishlist((state) => state.slugs);
  const products = getProductsBySlugs(slugs);

  return (
    <div className="mx-auto max-w-site px-5 py-12 md:px-8 md:py-16">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep">Wishlist</p>
      <h1 className="mt-3 font-display text-5xl text-ink">Saved for later</h1>
      <p className="mt-4 text-ink/65">{products.length} saved item{products.length === 1 ? "" : "s"}</p>

      {!products.length ? (
        <div className="mt-10">
          <p className="text-ink/70">No saved products yet.</p>
          <Link
            href="/shop"
            className="mt-6 inline-flex rounded-md bg-gold px-5 py-3 text-sm font-semibold text-ink hover:bg-gold-light"
          >
            Browse products
          </Link>
        </div>
      ) : (
        <div className="mt-10">
          <ProductGrid products={products} />
        </div>
      )}
    </div>
  );
}
