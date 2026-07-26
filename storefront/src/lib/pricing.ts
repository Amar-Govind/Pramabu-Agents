import { validateCoupon, type Coupon } from "@/lib/coupons";

export const FREE_SHIPPING_THRESHOLD = 999;
export const STANDARD_SHIPPING = 49;

type PricedItem = {
  product: { price: number };
  quantity: number;
};

export function calcSubtotal(items: PricedItem[]): number {
  return items.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
}

export function calcShipping(subtotal: number, freeShipping = false): number {
  if (freeShipping || subtotal === 0 || subtotal >= FREE_SHIPPING_THRESHOLD) return 0;
  return STANDARD_SHIPPING;
}

export type OrderTotals = {
  subtotal: number;
  discount: number;
  shipping: number;
  total: number;
  freeShipping: boolean;
  coupon: Coupon | null;
  couponMessage: string | null;
  couponError: string | null;
};

export function calcOrderTotals(
  items: PricedItem[],
  couponCode: string | null
): OrderTotals {
  const subtotal = calcSubtotal(items);

  if (!couponCode) {
    const shipping = calcShipping(subtotal);
    return {
      subtotal,
      discount: 0,
      shipping,
      total: subtotal + shipping,
      freeShipping: shipping === 0 && subtotal > 0,
      coupon: null,
      couponMessage: null,
      couponError: null,
    };
  }

  const result = validateCoupon(couponCode, subtotal);
  if (!result.ok) {
    const shipping = calcShipping(subtotal);
    return {
      subtotal,
      discount: 0,
      shipping,
      total: subtotal + shipping,
      freeShipping: shipping === 0 && subtotal > 0,
      coupon: null,
      couponMessage: null,
      couponError: result.error,
    };
  }

  const shipping = calcShipping(subtotal, result.freeShipping);
  const total = Math.max(0, subtotal - result.discount + shipping);

  return {
    subtotal,
    discount: result.discount,
    shipping,
    total,
    freeShipping: shipping === 0 && subtotal > 0,
    coupon: result.coupon,
    couponMessage: result.message,
    couponError: null,
  };
}
