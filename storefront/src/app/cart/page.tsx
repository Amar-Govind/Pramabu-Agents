"use client";

import Image from "next/image";
import Link from "next/link";
import { QuantitySelector } from "@/components/QuantitySelector";
import { formatINR, products } from "@/lib/products";
import { ProductRail } from "@/components/ProductRail";
import { useCart } from "@/store/cart";

export default function CartPage() {
  const items = useCart((state) => state.items);
  const setQuantity = useCart((state) => state.setQuantity);
  const removeItem = useCart((state) => state.removeItem);
  const openCart = useCart((state) => state.openCart);
  const subtotal = items.reduce(
    (sum, item) => sum + item.product.price * item.quantity,
    0
  );
  const shipping = subtotal >= 999 || subtotal === 0 ? 0 : 49;
  const total = subtotal + shipping;
  const suggestions = products.filter((product) =>
    ["virgin-coconut-oil", "neem-handcrafted-organic-soap", "coco-pith-low-ec-2", "rose-soap"].includes(
      product.slug
    )
  );

  return (
    <div className="mx-auto max-w-site px-5 py-12 md:px-8 md:py-16">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep">Cart</p>
      <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
        <h1 className="font-display text-5xl text-ink">Your bag</h1>
        <button
          type="button"
          onClick={openCart}
          className="rounded-md border border-gold/40 px-4 py-2 text-sm font-semibold text-gold-deep hover:bg-gold/10"
        >
          Open quick cart
        </button>
      </div>

      {!items.length ? (
        <div className="mt-12 max-w-lg">
          <p className="text-ink/70">Your cart is empty.</p>
          <Link
            href="/shop"
            className="mt-6 inline-flex rounded-md bg-gold px-5 py-3 text-sm font-semibold text-ink hover:bg-gold-light"
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
                className="grid grid-cols-[96px_1fr] gap-4 border-b border-gold/20 pb-8 md:grid-cols-[120px_1fr_auto]"
              >
                <Link href={`/product/${product.slug}`} className="relative aspect-square bg-mist">
                  {product.image ? (
                    <Image
                      src={product.image}
                      alt={product.name}
                      fill
                      className="object-contain p-2"
                      sizes="120px"
                    />
                  ) : null}
                </Link>
                <div>
                  <Link href={`/product/${product.slug}`} className="font-display text-2xl text-ink">
                    {product.shortName}
                  </Link>
                  <p className="mt-1 text-sm text-ink/60">{product.category}</p>
                  <p className="mt-2 font-semibold text-forest">{formatINR(product.price)}</p>
                  <div className="mt-4 flex flex-wrap items-center gap-3">
                    <QuantitySelector
                      value={quantity}
                      onChange={(value) => setQuantity(product.slug, value)}
                    />
                    <button
                      type="button"
                      onClick={() => removeItem(product.slug)}
                      className="text-sm text-ink/55 underline-offset-4 hover:text-gold-deep hover:underline"
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

          <aside className="h-fit rounded-xl border border-gold/25 bg-white/80 p-6">
            <h2 className="font-display text-2xl text-ink">Order summary</h2>
            <div className="mt-6 space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-ink/70">Subtotal</span>
                <span className="font-semibold text-forest">{formatINR(subtotal)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink/70">Shipping</span>
                <span className="font-semibold text-forest">
                  {shipping === 0 ? "Free" : formatINR(shipping)}
                </span>
              </div>
              <div className="gold-rule" />
              <div className="flex items-center justify-between text-base">
                <span className="font-semibold text-ink">Total</span>
                <span className="font-semibold text-forest">{formatINR(total)}</span>
              </div>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-ink/60">
              {subtotal < 999
                ? `Add ${formatINR(999 - subtotal)} more for free shipping.`
                : "You’ve unlocked free shipping."}
            </p>
            <a
              href="https://parambu.in/shop/"
              target="_blank"
              rel="noreferrer"
              className="mt-6 inline-flex w-full items-center justify-center rounded-md bg-gold px-5 py-3 text-sm font-semibold text-ink hover:bg-gold-light"
            >
              Checkout on parambu.in
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

      <ProductRail
        title="You may also like"
        subtitle="Popular adds before checkout."
        products={suggestions}
      />
    </div>
  );
}
