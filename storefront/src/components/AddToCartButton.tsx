"use client";

import { useState } from "react";
import type { Product } from "@/lib/products";
import { useCart } from "@/store/cart";

export function AddToCartButton({
  product,
  className = "",
}: {
  product: Product;
  className?: string;
}) {
  const addItem = useCart((state) => state.addItem);
  const [added, setAdded] = useState(false);

  return (
    <button
      type="button"
      onClick={() => {
        addItem(product);
        setAdded(true);
        window.setTimeout(() => setAdded(false), 1400);
      }}
      className={`rounded-md bg-forest px-5 py-3 text-sm font-semibold text-sand transition hover:bg-leaf ${className}`}
    >
      {added ? "Added" : "Add to cart"}
    </button>
  );
}
