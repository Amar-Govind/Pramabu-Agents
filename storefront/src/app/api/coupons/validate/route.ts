import { NextResponse } from "next/server";
import { validateCoupon } from "@/lib/coupons";

export async function POST(request: Request) {
  let body: { code?: string; subtotal?: number };

  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid request body." }, { status: 400 });
  }

  const code = typeof body.code === "string" ? body.code : "";
  const subtotal = typeof body.subtotal === "number" ? body.subtotal : 0;
  const result = validateCoupon(code, subtotal);

  if (!result.ok) {
    return NextResponse.json(result, { status: 400 });
  }

  return NextResponse.json({
    ok: true,
    code: result.coupon.code,
    description: result.coupon.description,
    discount: result.discount,
    freeShipping: result.freeShipping,
    message: result.message,
  });
}
