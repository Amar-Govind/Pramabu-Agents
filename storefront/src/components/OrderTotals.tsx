"use client";

import { useMemo } from "react";
import { CouponForm } from "@/components/CouponForm";
import { FREE_SHIPPING_THRESHOLD, calcOrderTotals } from "@/lib/pricing";
import { formatINR } from "@/lib/products";
import { useCart } from "@/store/cart";

export function OrderTotals({
  showCoupon = true,
  showFreeShipHint = true,
}: {
  showCoupon?: boolean;
  showFreeShipHint?: boolean;
}) {
  const items = useCart((state) => state.items);
  const couponCode = useCart((state) => state.couponCode);
  const totals = useMemo(
    () => calcOrderTotals(items, couponCode),
    [items, couponCode]
  );

  return (
    <div className="space-y-4">
      {showCoupon ? <CouponForm /> : null}

      <div className="space-y-3 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-ink/70">Subtotal</span>
          <span className="font-semibold text-forest">{formatINR(totals.subtotal)}</span>
        </div>
        {totals.discount > 0 ? (
          <div className="flex items-center justify-between">
            <span className="text-ink/70">Discount</span>
            <span className="font-semibold text-leaf">−{formatINR(totals.discount)}</span>
          </div>
        ) : null}
        <div className="flex items-center justify-between">
          <span className="text-ink/70">Shipping</span>
          <span className="font-semibold text-forest">
            {totals.shipping === 0 ? "Free" : formatINR(totals.shipping)}
          </span>
        </div>
        <div className="gold-rule" />
        <div className="flex items-center justify-between text-base">
          <span className="font-semibold text-ink">Total</span>
          <span className="font-semibold text-forest">{formatINR(totals.total)}</span>
        </div>
      </div>

      {showFreeShipHint ? (
        <p className="text-sm leading-relaxed text-ink/60">
          {totals.subtotal < FREE_SHIPPING_THRESHOLD && totals.shipping > 0
            ? `Add ${formatINR(FREE_SHIPPING_THRESHOLD - totals.subtotal)} more for free shipping.`
            : "You’ve unlocked free shipping."}
        </p>
      ) : null}
    </div>
  );
}
