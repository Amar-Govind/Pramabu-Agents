"use client";

import { useState } from "react";
import { AddToCartButton } from "@/components/AddToCartButton";
import { QuantitySelector } from "@/components/QuantitySelector";
import { WishlistButton } from "@/components/WishlistButton";
import { discountPercent, formatINR, type Product } from "@/lib/products";

export function ProductPurchasePanel({ product }: { product: Product }) {
  const [quantity, setQuantity] = useState(1);
  const discount = discountPercent(product);

  return (
    <div>
      <div className="flex items-baseline gap-3">
        <p className="text-3xl font-semibold text-forest">{formatINR(product.price)}</p>
        {product.regularPrice > product.price ? (
          <p className="text-sm text-ink/40 line-through">{formatINR(product.regularPrice)}</p>
        ) : null}
        {discount ? (
          <span className="rounded-sm bg-gold/20 px-2 py-1 text-xs font-bold text-gold-deep">
            Save {discount}%
          </span>
        ) : null}
      </div>

      <p className="mt-3 text-sm text-ink/60">
        ★ {product.rating.toFixed(1)} · {product.reviewCount} reviews ·{" "}
        <span className="text-leaf">{product.inStock ? "In stock" : "Out of stock"}</span>
      </p>

      <div className="mt-8 flex flex-wrap items-center gap-3">
        <QuantitySelector value={quantity} onChange={setQuantity} />
        <AddToCartButton
          product={product}
          quantity={quantity}
          className="min-w-[180px]"
          label="Add to cart"
        />
        <WishlistButton slug={product.slug} />
      </div>

      <div className="mt-8 grid gap-3 rounded-lg border border-gold/20 bg-white/70 p-4 text-sm text-ink/70">
        <p>✓ Handcrafted / cold-processed quality</p>
        <p>✓ Secure checkout on parambu.in</p>
        <p>✓ Pan-India shipping</p>
      </div>
    </div>
  );
}
