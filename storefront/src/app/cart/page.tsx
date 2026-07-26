"use client";

import Image from "next/image";
import Link from "next/link";
import { formatINR } from "@/lib/products";
import { useCart } from "@/store/cart";

export default function CartPage() {
  const items = useCart((state) => state.items);
  const setQuantity = useCart((state) => state.setQuantity);
  const removeItem = useCart((state) => state.removeItem);
  const subtotal = items.reduce(
    (sum, item) => sum + item.product.price * item.quantity,
    0
  );

  return (
    <div className="mx-auto max-w-site px-5 py-14 md:px-8 md:py-20">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-leaf">Cart</p>
      <h1 className="mt-3 font-display text-5xl text-ink">Your bag</h1>

      {!items.length ? (
        <div className="mt-12 max-w-lg">
          <p className="text-ink/70">Your cart is empty.</p>
          <Link
            href="/shop"
            className="mt-6 inline-flex rounded-md bg-forest px-5 py-3 text-sm font-semibold text-sand hover:bg-leaf"
          >
            Continue shopping
          </Link>
        </div>
      ) : (
        <div className="mt-12 grid gap-12 lg:grid-cols-[1.4fr_0.8fr]">
          <ul className="space-y-8">
            {items.map(({ product, quantity }) => (
              <li
                key={product.slug}
                className="grid grid-cols-[96px_1fr] gap-4 border-b border-forest/10 pb-8 md:grid-cols-[120px_1fr_auto]"
              >
                <div className="relative aspect-square bg-mist">
                  {product.image ? (
                    <Image
                      src={product.image}
                      alt={product.name}
                      fill
                      className="object-contain p-2"
                      sizes="120px"
                    />
                  ) : null}
                </div>
                <div>
                  <Link href={`/product/${product.slug}`} className="font-display text-2xl text-ink">
                    {product.shortName}
                  </Link>
                  <p className="mt-1 text-sm text-ink/60">{product.category}</p>
                  <p className="mt-2 font-semibold text-forest">{formatINR(product.price)}</p>
                  <div className="mt-4 flex items-center gap-3">
                    <label className="text-xs uppercase tracking-[0.14em] text-ink/50">
                      Qty
                      <input
                        type="number"
                        min={1}
                        value={quantity}
                        onChange={(event) =>
                          setQuantity(product.slug, Number(event.target.value) || 1)
                        }
                        className="ml-2 w-16 rounded border border-forest/20 bg-white px-2 py-1 text-sm text-ink"
                      />
                    </label>
                    <button
                      type="button"
                      onClick={() => removeItem(product.slug)}
                      className="text-sm text-ink/55 underline-offset-4 hover:text-forest hover:underline"
                    >
                      Remove
                    </button>
                  </div>
                </div>
                <p className="hidden font-semibold text-ink md:block">
                  {formatINR(product.price * quantity)}
                </p>
              </li>
            ))}
          </ul>

          <aside className="h-fit border border-forest/15 bg-white/70 p-6">
            <h2 className="font-display text-2xl text-ink">Order summary</h2>
            <div className="mt-6 flex items-center justify-between text-sm">
              <span className="text-ink/70">Subtotal</span>
              <span className="font-semibold text-forest">{formatINR(subtotal)}</span>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-ink/60">
              Checkout with Razorpay is next. For now you can continue on the live store.
            </p>
            <a
              href="https://parambu.in/shop/"
              target="_blank"
              rel="noreferrer"
              className="mt-6 inline-flex w-full items-center justify-center rounded-md bg-forest px-5 py-3 text-sm font-semibold text-sand hover:bg-leaf"
            >
              Complete on parambu.in
            </a>
            <Link
              href="/shop"
              className="mt-3 inline-flex w-full items-center justify-center px-5 py-3 text-sm font-semibold text-forest"
            >
              Keep shopping
            </Link>
          </aside>
        </div>
      )}
    </div>
  );
}
