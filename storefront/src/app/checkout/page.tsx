"use client";

import Image from "next/image";
import Link from "next/link";
import { useMemo, useState, type FormEvent } from "react";
import { CheckoutSteps } from "@/components/CheckoutSteps";
import { OrderTotals } from "@/components/OrderTotals";
import { IconCheck, IconShield, IconTruck } from "@/components/icons";
import { calcOrderTotals } from "@/lib/pricing";
import { formatINR } from "@/lib/products";
import { useCart } from "@/store/cart";

type Step = "details" | "payment" | "done";

export default function CheckoutPage() {
  const items = useCart((state) => state.items);
  const couponCode = useCart((state) => state.couponCode);
  const clear = useCart((state) => state.clear);
  const [step, setStep] = useState<Step>("details");
  const [paymentMethod, setPaymentMethod] = useState<"razorpay" | "external">("razorpay");
  const [form, setForm] = useState({
    name: "",
    phone: "",
    email: "",
    address: "",
    city: "",
    pincode: "",
  });

  const totals = useMemo(
    () => calcOrderTotals(items, couponCode),
    [items, couponCode]
  );

  if (!items.length && step !== "done") {
    return (
      <div className="mx-auto max-w-site px-5 py-16 md:px-8">
        <h1 className="font-display text-4xl text-ink">Checkout</h1>
        <p className="mt-4 text-ink/70">Your cart is empty.</p>
        <Link href="/shop" className="mt-6 inline-flex rounded-md bg-gold px-5 py-3 text-sm font-semibold text-ink">
          Continue shopping
        </Link>
      </div>
    );
  }

  function onDetailsSubmit(event: FormEvent) {
    event.preventDefault();
    setStep("payment");
  }

  function onPlaceOrder(event: FormEvent) {
    event.preventDefault();
    if (paymentMethod === "external") {
      window.open("https://parambu.in/shop/", "_blank", "noopener,noreferrer");
      return;
    }
    clear();
    setStep("done");
  }

  if (step === "done") {
    return (
      <div className="mx-auto max-w-xl px-5 py-20 text-center md:px-8">
        <div className="mx-auto mb-5 inline-flex h-14 w-14 items-center justify-center rounded-full bg-gold text-ink">
          <IconCheck className="h-7 w-7" />
        </div>
        <h1 className="font-display text-4xl text-ink">Order received</h1>
        <p className="mt-4 text-ink/70">
          Thanks for choosing Parambu Organics. Razorpay live payment comes next —
          this demo confirms your checkout flow end-to-end.
        </p>
        <Link href="/shop" className="mt-8 inline-flex rounded-md bg-gold px-5 py-3 text-sm font-semibold text-ink">
          Back to shop
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-site px-5 py-12 md:px-8 md:py-16">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep">Checkout</p>
      <h1 className="mt-3 font-display text-5xl text-ink">Secure checkout</h1>
      <div className="mt-6 max-w-2xl">
        <CheckoutSteps current={step === "details" ? "details" : "payment"} />
      </div>

      <div className="mt-10 grid gap-10 lg:grid-cols-[1.2fr_0.8fr]">
        <div>
          {step === "details" ? (
            <form onSubmit={onDetailsSubmit} className="space-y-4 rounded-xl border border-gold/25 bg-white/80 p-5 md:p-7">
              <div className="flex items-center gap-2 text-forest">
                <IconTruck />
                <h2 className="font-display text-2xl text-ink">Delivery details</h2>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <Field label="Full name" value={form.name} onChange={(value) => setForm({ ...form, name: value })} required />
                <Field label="Phone" value={form.phone} onChange={(value) => setForm({ ...form, phone: value })} required />
                <Field label="Email" type="email" value={form.email} onChange={(value) => setForm({ ...form, email: value })} required className="md:col-span-2" />
                <Field label="Address" value={form.address} onChange={(value) => setForm({ ...form, address: value })} required className="md:col-span-2" />
                <Field label="City" value={form.city} onChange={(value) => setForm({ ...form, city: value })} required />
                <Field label="Pincode" value={form.pincode} onChange={(value) => setForm({ ...form, pincode: value })} required />
              </div>
              <button type="submit" className="mt-2 w-full rounded-md bg-gold px-5 py-3 text-sm font-semibold text-ink hover:bg-gold-light">
                Continue to payment
              </button>
            </form>
          ) : (
            <form onSubmit={onPlaceOrder} className="space-y-4 rounded-xl border border-gold/25 bg-white/80 p-5 md:p-7">
              <div className="flex items-center gap-2 text-forest">
                <IconShield />
                <h2 className="font-display text-2xl text-ink">Payment</h2>
              </div>
              <label className={`flex cursor-pointer gap-3 rounded-lg border p-4 ${paymentMethod === "razorpay" ? "border-gold bg-gold/10" : "border-forest/15"}`}>
                <input
                  type="radio"
                  name="payment"
                  checked={paymentMethod === "razorpay"}
                  onChange={() => setPaymentMethod("razorpay")}
                  className="accent-gold"
                />
                <span>
                  <span className="block font-semibold text-ink">Pay with Razorpay (recommended)</span>
                  <span className="mt-1 block text-sm text-ink/60">UPI, cards, netbanking — simulated confirmation for now.</span>
                </span>
              </label>
              <label className={`flex cursor-pointer gap-3 rounded-lg border p-4 ${paymentMethod === "external" ? "border-gold bg-gold/10" : "border-forest/15"}`}>
                <input
                  type="radio"
                  name="payment"
                  checked={paymentMethod === "external"}
                  onChange={() => setPaymentMethod("external")}
                  className="accent-gold"
                />
                <span>
                  <span className="block font-semibold text-ink">Complete on parambu.in</span>
                  <span className="mt-1 block text-sm text-ink/60">Use the live WooCommerce checkout while we finish native payments.</span>
                </span>
              </label>
              <div className="flex flex-wrap gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setStep("details")}
                  className="rounded-md border border-forest/20 px-5 py-3 text-sm font-semibold text-forest"
                >
                  Back
                </button>
                <button type="submit" className="flex-1 rounded-md bg-gold px-5 py-3 text-sm font-semibold text-ink hover:bg-gold-light">
                  {paymentMethod === "external"
                    ? "Open live checkout"
                    : `Pay ${formatINR(totals.total)}`}
                </button>
              </div>
            </form>
          )}
        </div>

        <aside className="h-fit rounded-xl border border-gold/25 bg-white/80 p-5 md:p-6">
          <h2 className="font-display text-2xl text-ink">Order summary</h2>
          <ul className="mt-5 space-y-4">
            {items.map(({ product, quantity }) => (
              <li key={product.slug} className="flex gap-3">
                <span className="relative h-14 w-14 overflow-hidden bg-mist">
                  {product.image ? (
                    <Image src={product.image} alt={product.shortName} fill className="object-contain p-1" sizes="56px" />
                  ) : null}
                </span>
                <span className="flex-1 text-sm">
                  <span className="block font-medium text-ink">{product.shortName}</span>
                  <span className="text-ink/55">Qty {quantity}</span>
                </span>
                <span className="text-sm font-semibold text-forest">
                  {formatINR(product.price * quantity)}
                </span>
              </li>
            ))}
          </ul>
          <div className="mt-5 border-t border-gold/20 pt-4">
            <OrderTotals showFreeShipHint={false} />
          </div>
        </aside>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  required,
  type = "text",
  className = "",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  type?: string;
  className?: string;
}) {
  return (
    <label className={`block text-sm ${className}`}>
      <span className="mb-1.5 block text-ink/70">{label}</span>
      <input
        type={type}
        required={required}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-md border border-forest/15 bg-white px-3 py-2.5 outline-none ring-gold focus:ring-2"
      />
    </label>
  );
}
