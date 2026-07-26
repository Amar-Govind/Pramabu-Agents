"use client";

import Image from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";
import { AddToCartButton } from "@/components/AddToCartButton";
import { formatINR, getProduct, type Product } from "@/lib/products";
import { useCart } from "@/store/cart";

export function AlsoBought({
  product,
  related,
}: {
  product: Product;
  related: Product[];
}) {
  const addItem = useCart((state) => state.addItem);
  const [selected, setSelected] = useState<string[]>(() =>
    related.slice(0, 2).map((item) => item.slug)
  );

  const chosen = useMemo(
    () =>
      selected
        .map((slug) => getProduct(slug))
        .filter((item): item is Product => Boolean(item)),
    [selected]
  );

  const total = chosen.reduce((sum, item) => sum + item.price, 0) + product.price;

  if (!related.length) return null;

  return (
    <section className="mt-16 rounded-xl border border-gold/25 bg-white/70 p-5 md:p-8">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep">
        Frequently bought together
      </p>
      <h2 className="mt-2 font-display text-3xl text-ink">Also bought with this</h2>

      <div className="mt-8 flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <BundleThumb product={product} locked />
          {related.map((item) => (
            <div key={item.slug} className="flex items-center gap-3">
              <span className="text-xl text-gold-deep">+</span>
              <BundleThumb
                product={item}
                checked={selected.includes(item.slug)}
                onToggle={() =>
                  setSelected((prev) =>
                    prev.includes(item.slug)
                      ? prev.filter((slug) => slug !== item.slug)
                      : [...prev, item.slug]
                  )
                }
              />
            </div>
          ))}
        </div>

        <div className="min-w-[220px]">
          <p className="text-sm text-ink/65">Bundle total</p>
          <p className="mt-1 text-2xl font-semibold text-forest">{formatINR(total)}</p>
          <button
            type="button"
            onClick={() => {
              addItem(product);
              chosen.forEach((item) => addItem(item));
            }}
            className="mt-4 w-full rounded-md bg-gold px-4 py-3 text-sm font-semibold text-ink hover:bg-gold-light"
          >
            Add {1 + chosen.length} items to cart
          </button>
          <div className="mt-3">
            <AddToCartButton product={product} className="w-full bg-forest text-sand hover:bg-leaf" label="Add this only" />
          </div>
        </div>
      </div>
    </section>
  );
}

function BundleThumb({
  product,
  checked,
  onToggle,
  locked,
}: {
  product: Product;
  checked?: boolean;
  onToggle?: () => void;
  locked?: boolean;
}) {
  return (
    <div className="w-[120px]">
      <Link href={`/product/${product.slug}`} className="relative block aspect-square overflow-hidden bg-mist">
        {product.image ? (
          <Image src={product.image} alt={product.shortName} fill className="object-contain p-2" sizes="120px" />
        ) : null}
      </Link>
      <p className="mt-2 line-clamp-2 text-xs font-medium text-ink">{product.shortName}</p>
      <p className="text-xs font-semibold text-forest">{formatINR(product.price)}</p>
      {!locked ? (
        <label className="mt-2 flex items-center gap-2 text-xs text-ink/70">
          <input
            type="checkbox"
            checked={Boolean(checked)}
            onChange={onToggle}
            className="accent-gold"
          />
          Include
        </label>
      ) : (
        <p className="mt-2 text-xs text-gold-deep">This item</p>
      )}
    </div>
  );
}
