import couponsData from "@/data/coupons.json";

export type CouponType = "percent" | "fixed" | "freeship";

export type Coupon = {
  code: string;
  description: string;
  type: CouponType;
  value: number;
  minSubtotal: number;
  active: boolean;
};

export type CouponValidationResult =
  | {
      ok: true;
      coupon: Coupon;
      discount: number;
      freeShipping: boolean;
      message: string;
    }
  | {
      ok: false;
      error: string;
    };

export const coupons = couponsData as Coupon[];

export function normalizeCouponCode(code: string): string {
  return code.trim().toUpperCase();
}

export function findCoupon(code: string): Coupon | undefined {
  const normalized = normalizeCouponCode(code);
  return coupons.find((coupon) => coupon.code === normalized);
}

export function validateCoupon(code: string, subtotal: number): CouponValidationResult {
  const coupon = findCoupon(code);
  if (!coupon || !coupon.active) {
    return { ok: false, error: "This coupon code is invalid." };
  }

  if (subtotal <= 0) {
    return { ok: false, error: "Add items to your cart before applying a coupon." };
  }

  if (subtotal < coupon.minSubtotal) {
    return {
      ok: false,
      error: `This coupon needs a minimum subtotal of ₹${coupon.minSubtotal}.`,
    };
  }

  if (coupon.type === "freeship") {
    return {
      ok: true,
      coupon,
      discount: 0,
      freeShipping: true,
      message: coupon.description,
    };
  }

  const discount =
    coupon.type === "percent"
      ? Math.round((subtotal * coupon.value) / 100)
      : Math.min(coupon.value, subtotal);

  return {
    ok: true,
    coupon,
    discount,
    freeShipping: false,
    message: coupon.description,
  };
}
