"use client";

import Image from "next/image";
import Link from "next/link";
import {
  IconCart,
  IconClose,
  IconHeart,
  IconMenu,
  IconSearch,
} from "@/components/icons";
import { collections } from "@/lib/collections";
import { useCart } from "@/store/cart";
import { useUI } from "@/store/ui";
import { useWishlist } from "@/store/wishlist";

const links = [
  { href: "/shop", label: "Shop" },
  ...collections.map((collection) => ({
    href: `/shop/${collection.slug}`,
    label: collection.title,
    note: collection.shortLabel,
  })),
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
              className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-forest/15 bg-white text-forest md:hidden"
              onClick={openMobileNav}
              aria-label="Open menu"
            >
              <IconMenu />
            </button>
            <Link href="/" className="flex items-center gap-2.5">
              <Image
                src="/brand/logo-gold.png"
                alt="Parambu Organics rose gold logo"
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
              <Link
                key={link.href}
                href={link.href}
                className="group transition hover:text-gold-deep"
                title={"note" in link ? `${link.label} · ${link.note}` : link.label}
              >
                <span className="block">{link.label}</span>
                {"note" in link && link.note ? (
                  <span className="block text-[10px] font-normal uppercase tracking-[0.14em] text-ink/40 group-hover:text-gold-deep/80">
                    {link.note}
                  </span>
                ) : null}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={openSearch}
              aria-label="Search"
              className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-forest/15 bg-white text-forest hover:border-gold hover:text-gold-deep"
            >
              <IconSearch />
            </button>
            <Link
              href="/wishlist"
              aria-label="Wishlist"
              className="relative inline-flex h-10 w-10 items-center justify-center rounded-md border border-forest/15 bg-white text-forest hover:border-gold hover:text-gold-deep"
            >
              <IconHeart />
              {wishlistCount > 0 ? (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-gold text-[10px] font-bold text-white">
                  {wishlistCount}
                </span>
              ) : null}
            </Link>
            <button
              type="button"
              onClick={openCart}
              aria-label={`Open cart, ${totalItems} items`}
              className="relative inline-flex h-10 w-10 items-center justify-center rounded-full bg-gold text-white transition hover:bg-gold-deep"
            >
              <IconCart className="h-5 w-5" />
              <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-forest text-[10px] font-bold text-sand ring-2 ring-[#faf6ee]">
                {totalItems > 99 ? "99+" : totalItems}
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
              <button type="button" onClick={closeMobileNav} aria-label="Close" className="text-ink/60">
                <IconClose />
              </button>
            </div>
            <nav className="mt-8 flex flex-col gap-4 text-base font-medium text-ink">
              <Link href="/shop" onClick={closeMobileNav}>Shop</Link>
              {collections.map((collection) => (
                <Link key={collection.slug} href={`/shop/${collection.slug}`} onClick={closeMobileNav}>
                  <span className="block">{collection.title}</span>
                  <span className="text-xs font-normal text-ink/45">
                    {collection.shortLabel}
                  </span>
                </Link>
              ))}
              <Link href="/wishlist" onClick={closeMobileNav}>Wishlist</Link>
              <Link href="/cart" onClick={closeMobileNav}>Cart</Link>
              <Link href="/checkout" onClick={closeMobileNav}>Checkout</Link>
            </nav>
          </div>
        </div>
      ) : null}
    </>
  );
}
