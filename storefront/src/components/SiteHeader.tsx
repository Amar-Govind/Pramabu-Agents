"use client";

import Link from "next/link";
import { useCart } from "@/store/cart";

const links = [
  { href: "/shop", label: "Shop" },
  { href: "/shop/oils", label: "Oils" },
  { href: "/shop/soap", label: "Soap" },
  { href: "/shop/gardening", label: "Gardening" },
];

export function SiteHeader() {
  const items = useCart((state) => state.items);
  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <header className="sticky top-0 z-40 border-b border-forest/10 bg-[#f7f4ee]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-site items-center justify-between gap-4 px-5 py-4 md:px-8">
        <Link href="/" className="group">
          <span className="font-display text-2xl tracking-tight text-forest transition group-hover:text-leaf md:text-[1.7rem]">
            Parambu Organics
          </span>
        </Link>

        <nav className="hidden items-center gap-7 text-sm font-medium text-ink/80 md:flex">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="transition hover:text-forest"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <Link
          href="/cart"
          className="inline-flex items-center gap-2 rounded-md bg-forest px-3.5 py-2 text-sm font-semibold text-sand transition hover:bg-leaf"
        >
          Cart
          <span className="min-w-5 text-center tabular-nums">{totalItems}</span>
        </Link>
      </div>
    </header>
  );
}
