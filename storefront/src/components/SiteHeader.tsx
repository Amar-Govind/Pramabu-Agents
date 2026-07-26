"use client";

import Image from "next/image";
import Link from "next/link";
import { useCart } from "@/store/cart";
import { useUI } from "@/store/ui";
import { useWishlist } from "@/store/wishlist";

const links = [
  { href: "/shop", label: "Shop" },
  { href: "/shop/oils", label: "Oils" },
  { href: "/shop/soap", label: "Soap" },
  { href: "/shop/gardening", label: "Gardening" },
];

export function SiteHeader() {
  const items = useCart((state) => state.items);
  const openCart = useCart((state) => state.openCart);
  const openSearch = useUI((state) => state.openSearch);
  const mobileNavOpen = useUI((state) => state.mobileNavOpen);
  const openMobileNav = useUI((state) => state.openMobileNav);
  const closeMobileNav = useUI((state) => state.closeMobileNav);
  const wishlistCount = useWishlist((state) => state.slugs.length);
  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <>
      <div className="bg-forest text-center text-xs font-medium tracking-wide text-sand">
        <p className="px-4 py-2">
          Free shipping on orders above ₹999 · Pure heritage care from Parambu Organics
        </p>
      </div>

      <header className="sticky top-0 z-40 border-b border-gold/20 bg-[#faf6ee]/92 backdrop-blur-md">
        <div className="mx-auto flex max-w-site items-center justify-between gap-3 px-4 py-3 md:px-8">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="rounded-md border border-forest/15 px-3 py-2 text-sm md:hidden"
              onClick={openMobileNav}
              aria-label="Open menu"
            >
              Menu
            </button>
            <Link href="/" className="flex items-center gap-2.5">
              <Image
                src="/brand/logo-gold.png"
                alt="Parambu Organics golden logo"
                width={44}
                height={44}
                className="h-11 w-11 object-contain"
                priority
              />
              <span className="leading-tight">
                <span className="block font-display text-xl text-forest md:text-2xl">
                  Parambu Organics
                </span>
                <span className="hidden text-[11px] font-semibold uppercase tracking-[0.16em] text-gold-deep sm:block">
                  Everyday Pure & Natural
                </span>
              </span>
            </Link>
          </div>

          <nav className="hidden items-center gap-6 text-sm font-medium text-ink/80 lg:flex">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className="transition hover:text-gold-deep">
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={openSearch}
              className="rounded-md border border-forest/15 bg-white px-3 py-2 text-sm text-ink hover:border-gold"
            >
              Search
            </button>
            <Link
              href="/wishlist"
              className="relative hidden rounded-md border border-forest/15 bg-white px-3 py-2 text-sm text-ink hover:border-gold sm:inline-flex"
            >
              Wishlist
              {wishlistCount > 0 ? (
                <span className="ml-1 inline-flex min-w-5 justify-center rounded-sm bg-gold px-1 text-[11px] font-bold text-ink">
                  {wishlistCount}
                </span>
              ) : null}
            </Link>
            <button
              type="button"
              onClick={openCart}
              className="inline-flex items-center gap-2 rounded-md bg-gold px-3.5 py-2 text-sm font-semibold text-ink transition hover:bg-gold-light"
            >
              Cart
              <span className="inline-flex min-w-5 justify-center rounded-sm bg-forest px-1.5 text-[11px] font-bold text-sand">
                {totalItems}
              </span>
            </button>
          </div>
        </div>
      </header>

      {mobileNavOpen ? (
        <div className="fixed inset-0 z-[60] md:hidden">
          <button type="button" className="absolute inset-0 bg-ink/45" aria-label="Close menu" onClick={closeMobileNav} />
          <div className="absolute left-0 top-0 flex h-full w-[80%] max-w-xs flex-col bg-[#fffaf0] p-5 shadow-soft animate-rise">
            <div className="flex items-center justify-between">
              <p className="font-display text-2xl text-forest">Menu</p>
              <button type="button" onClick={closeMobileNav} className="text-sm text-ink/60">
                Close
              </button>
            </div>
            <nav className="mt-8 flex flex-col gap-4 text-base font-medium text-ink">
              {links.map((link) => (
                <Link key={link.href} href={link.href} onClick={closeMobileNav}>
                  {link.label}
                </Link>
              ))}
              <Link href="/wishlist" onClick={closeMobileNav}>
                Wishlist
              </Link>
              <Link href="/cart" onClick={closeMobileNav}>
                Cart
              </Link>
            </nav>
          </div>
        </div>
      ) : null}
    </>
  );
}
