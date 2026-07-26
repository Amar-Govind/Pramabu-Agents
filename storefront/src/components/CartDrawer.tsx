"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect } from "react";
import { CheckoutSteps } from "@/components/CheckoutSteps";
import { QuantitySelector } from "@/components/QuantitySelector";
import { IconClose, IconTrash } from "@/components/icons";
import { formatINR } from "@/lib/products";
import { useCart } from "@/store/cart";

export function CartDrawer() {
  const isOpen = useCart((state) => state.isOpen);
  const closeCart = useCart((state) => state.closeCart);
  const items = useCart((state) => state.items);
  const setQuantity = useCart((state) => state.setQuantity);
  const removeItem = useCart((state) => state.removeItem);
  const subtotal = items.reduce(
    (sum, item) => sum + item.product.price * item.quantity,
    0
  );
  const count = items.reduce((sum, item) => sum + item.quantity, 0);
  const remainingForFreeShip = Math.max(0, 999 - subtotal);

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeCart();
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [isOpen, closeCart]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[80]">
      <button
        type="button"
        aria-label="Close cart overlay"
        className="absolute inset-0 bg-ink/45"
        onClick={closeCart}
      />
      <aside className="animate-drawer absolute inset-y-0 right-0 flex w-full max-w-md flex-col bg-[#fffaf0] shadow-soft">
        <div className="border-b border-gold/20 px-5 py-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-display text-2xl text-ink">Your cart</p>
              <p className="text-xs text-ink/55">{count} item{count === 1 ? "" : "s"}</p>
            </div>
            <button
              type="button"
              onClick={closeCart}
              aria-label="Close cart"
              className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-forest/15 text-ink hover:border-gold"
            >
              <IconClose />
            </button>
          </div>
          <div className="mt-4">
            <CheckoutSteps current="cart" />
          </div>
          <div className="mt-4">
            <div className="mb-1 flex justify-between text-[11px] text-ink/55">
              <span>Free shipping</span>
              <span>
                {remainingForFreeShip === 0
                  ? "Unlocked"
                  : `${formatINR(remainingForFreeShip)} away`}
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-mist">
              <div
                className="h-full rounded-full bg-gold transition-all"
                style={{ width: `${Math.min(100, (subtotal / 999) * 100)}%` }}
              />
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-5">
          {!items.length ? (
            <div className="py-10 text-center">
              <p className="text-ink/70">Your cart is empty.</p>
              <button
                type="button"
                onClick={closeCart}
                className="mt-5 rounded-md bg-gold px-4 py-2 text-sm font-semibold text-ink"
              >
                Continue shopping
              </button>
            </div>
          ) : (
            <ul className="space-y-5">
              {items.map(({ product, quantity }) => (
                <li key={product.slug} className="grid grid-cols-[84px_1fr] gap-3 border-b border-forest/10 pb-5">
                  <Link href={`/product/${product.slug}`} onClick={closeCart} className="relative aspect-square bg-mist">
                    {product.image ? (
                      <Image src={product.image} alt={product.shortName} fill className="object-contain p-1.5" sizes="84px" />
                    ) : null}
                  </Link>
                  <div>
                    <Link href={`/product/${product.slug}`} onClick={closeCart} className="font-medium text-ink hover:text-forest">
                      {product.shortName}
                    </Link>
                    <p className="mt-1 text-sm font-semibold text-forest">
                      {formatINR(product.price)}
                    </p>
                    <div className="mt-3 flex items-center justify-between gap-2">
                      <QuantitySelector
                        value={quantity}
                        onChange={(value) => setQuantity(product.slug, value)}
                      />
                      <button
                        type="button"
                        aria-label="Remove item"
                        onClick={() => removeItem(product.slug)}
                        className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-forest/15 text-ink/60 hover:border-gold hover:text-gold-deep"
                      >
                        <IconTrash className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="border-t border-gold/20 bg-white/70 px-5 py-5">
          <div className="flex items-center justify-between text-sm">
            <span className="text-ink/65">Subtotal</span>
            <span className="text-lg font-semibold text-forest">{formatINR(subtotal)}</span>
          </div>
          <p className="mt-2 text-xs text-ink/50">
            Next: add delivery details, then pay securely.
          </p>
          <Link
            href="/checkout"
            onClick={closeCart}
            className="mt-4 flex w-full items-center justify-center rounded-md bg-gold px-4 py-3 text-sm font-semibold text-ink hover:bg-gold-light"
          >
            Proceed to checkout
          </Link>
          <Link
            href="/cart"
            onClick={closeCart}
            className="mt-3 flex w-full items-center justify-center rounded-md border border-forest/20 px-4 py-3 text-sm font-semibold text-forest hover:border-gold"
          >
            Review full cart
          </Link>
        </div>
      </aside>
    </div>
  );
}
