"use client";

import { useState } from "react";
import type { Product } from "@/lib/products";
import { useCart } from "@/store/cart";

export function AddToCartButton({
  product,
  quantity = 1,
  className = "",
  label = "Add to cart",
}: {
  product: Product;
  quantity?: number;
  className?: string;
  label?: string;
}) {
  const addItem = useCart((state) => state.addItem);
  const [added, setAdded] = useState(false);

  return (
    <button
      type="button"
      onClick={() => {
        addItem(product, quantity);
        setAdded(true);
        window.setTimeout(() => setAdded(false), 1200);
      }}
      className={`rounded-md bg-gold px-5 py-3 text-sm font-semibold text-ink transition hover:bg-gold-light ${className}`}
    >
      {added ? "Added" : label}
    </button>
  );
}
