"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { calcOrderTotals, calcSubtotal } from "@/lib/pricing";
import { useCart } from "@/store/cart";

export function CouponForm() {
  const items = useCart((state) => state.items);
  const couponCode = useCart((state) => state.couponCode);
  const setCouponCode = useCart((state) => state.setCouponCode);
  const clearCoupon = useCart((state) => state.clearCoupon);
  const [input, setInput] = useState(couponCode ?? "");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const totals = useMemo(
    () => calcOrderTotals(items, couponCode),
    [items, couponCode]
  );

  useEffect(() => {
    if (couponCode && totals.couponError) {
      clearCoupon();
      setError(totals.couponError);
      setSuccess(null);
    }
  }, [couponCode, totals.couponError, clearCoupon]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    const code = input.trim();
    if (!code) {
      setError("Enter a coupon code.");
      return;
    }

    setPending(true);
    try {
      const response = await fetch("/api/coupons/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, subtotal: calcSubtotal(items) }),
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        clearCoupon();
        setError(data.error ?? "This coupon code is invalid.");
        return;
      }
      setCouponCode(data.code);
      setInput(data.code);
      setSuccess(data.message ?? "Coupon applied.");
    } catch {
      setError("Could not validate coupon. Try again.");
    } finally {
      setPending(false);
    }
  }

  function onRemove() {
    clearCoupon();
    setInput("");
    setError(null);
    setSuccess(null);
  }

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-ink">Coupon code</p>
      {couponCode && !totals.couponError ? (
        <div className="flex items-center justify-between gap-3 rounded-md border border-gold/35 bg-gold/10 px-3 py-2.5 text-sm">
          <div>
            <p className="font-semibold text-forest">{couponCode}</p>
            <p className="text-ink/60">{totals.couponMessage}</p>
          </div>
          <button
            type="button"
            onClick={onRemove}
            className="text-xs font-semibold text-gold-deep underline-offset-2 hover:underline"
          >
            Remove
          </button>
        </div>
      ) : (
        <form onSubmit={onSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value.toUpperCase())}
            placeholder="e.g. PARAMBU10"
            className="min-w-0 flex-1 rounded-md border border-forest/15 bg-white px-3 py-2.5 text-sm uppercase outline-none ring-gold focus:ring-2"
            aria-label="Coupon code"
          />
          <button
            type="submit"
            disabled={pending}
            className="rounded-md border border-gold/50 bg-white px-4 py-2.5 text-sm font-semibold text-gold-deep transition hover:bg-gold/15 disabled:opacity-60"
          >
            {pending ? "…" : "Apply"}
          </button>
        </form>
      )}
      {error ? <p className="text-xs text-red-700">{error}</p> : null}
      {success ? <p className="text-xs text-forest">{success}</p> : null}
      <p className="text-[11px] text-ink/45">Try PARAMBU10, WELCOME50, ORGANIC15, or FREESHIP.</p>
    </div>
  );
}
