"use client";

import { useState } from "react";
import { IconCart, IconCheck } from "@/components/icons";
import type { Product } from "@/lib/products";
import { useCart } from "@/store/cart";

export function AddToCartButton({
  product,
  quantity = 1,
  className = "",
  label = "Add",
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
      className={`inline-flex items-center justify-center gap-2 rounded-md bg-gold px-5 py-3 text-sm font-semibold text-ink transition hover:bg-gold-deep hover:text-white ${className}`}
    >
      {added ? <IconCheck className="h-4 w-4" /> : <IconCart className="h-4 w-4" />}
      {added ? "Added" : label}
    </button>
  );
}
