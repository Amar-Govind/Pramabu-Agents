"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import {
  IconCart,
  IconChevronRight,
  IconClose,
  IconHeart,
  IconMenu,
  IconSearch,
} from "@/components/icons";
import { collections } from "@/lib/collections";
import { useCart } from "@/store/cart";
import { useUI } from "@/store/ui";
import { useWishlist } from "@/store/wishlist";

export function SiteHeader() {
  const items = useCart((state) => state.items);
  const openCart = useCart((state) => state.openCart);
  const openSearch = useUI((state) => state.openSearch);
  const mobileNavOpen = useUI((state) => state.mobileNavOpen);
  const openMobileNav = useUI((state) => state.openMobileNav);
  const closeMobileNav = useUI((state) => state.closeMobileNav);
  const wishlistCount = useWishlist((state) => state.slugs.length);
  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [mobileOpen, setMobileOpen] = useState<string | null>(null);

  return (
    <>
      <div className="bg-forest text-center text-xs font-medium tracking-wide text-sand">
        <p className="px-4 py-2">
          Free shipping on orders above ₹999 · Pure heritage care from Parambu Organics
        </p>
      </div>

      <header className="sticky top-0 z-40 border-b border-gold/20 bg-[#faf6ee]/92 backdrop-blur-md">
        <div className="mx-auto flex max-w-site items-center justify-between gap-3 px-4 py-2.5 md:px-8 md:py-3">
          <div className="flex min-w-0 items-center gap-2.5">
            <button
              type="button"
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-forest/15 bg-white text-forest md:hidden"
              onClick={openMobileNav}
              aria-label="Open menu"
            >
              <IconMenu />
            </button>
            <Link href="/" className="flex min-w-0 items-center">
              <Image
                src="/brand/logo-wordmark-transparent.png"
                alt="PARAMBU organics"
                width={2026}
                height={533}
                className="h-8 w-auto max-w-[46vw] object-contain object-left sm:h-9 md:h-11 md:max-w-none lg:h-12"
                priority
              />
            </Link>
          </div>

          <nav className="hidden items-center gap-1 text-sm font-medium text-ink/80 lg:flex">
            <Link href="/shop" className="rounded-md px-3 py-2 transition hover:bg-gold/15 hover:text-gold-deep">
              Shop
            </Link>
            {collections.map((collection) => (
              <div
                key={collection.slug}
                className="relative"
                onMouseEnter={() => setOpenMenu(collection.slug)}
                onMouseLeave={() => setOpenMenu(null)}
              >
                <Link
                  href={`/shop/${collection.slug}`}
                  className="inline-flex items-center gap-1 rounded-md px-3 py-2 transition hover:bg-gold/15 hover:text-gold-deep"
                  aria-expanded={openMenu === collection.slug}
                  aria-haspopup="true"
                >
                  {collection.title}
                  <span className="text-[10px] text-ink/40">▾</span>
                </Link>

                {openMenu === collection.slug ? (
                  <div className="absolute left-0 top-full z-50 min-w-[220px] pt-2">
                    <div className="rounded-xl border border-gold/25 bg-[#fffaf0] p-2 shadow-soft">
                      <Link
                        href={`/shop/${collection.slug}`}
                        className="block rounded-md px-3 py-2 text-sm font-semibold text-forest hover:bg-gold/15"
                        onClick={() => setOpenMenu(null)}
                      >
                        All {collection.title}
                      </Link>
                      <div className="my-1 h-px bg-gold/20" />
                      {collection.children.map((child) => (
                        <Link
                          key={child.slug}
                          href={`/shop/${collection.slug}/${child.slug}`}
                          className="block rounded-md px-3 py-2 text-sm text-ink/80 hover:bg-gold/15 hover:text-gold-deep"
                          onClick={() => setOpenMenu(null)}
                        >
                          {child.title}
                        </Link>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
            ))}
          </nav>

          <div className="flex shrink-0 items-center gap-2">
            <button
              type="button"
              onClick={openSearch}
              aria-label="Search"
              className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-forest/15 bg-white text-forest hover:border-gold hover:text-gold-deep md:h-10 md:w-10"
            >
              <IconSearch />
            </button>
            <Link
              href="/wishlist"
              aria-label="Wishlist"
              className="relative inline-flex h-9 w-9 items-center justify-center rounded-md border border-forest/15 bg-white text-forest hover:border-gold hover:text-gold-deep md:h-10 md:w-10"
            >
              <IconHeart />
              {wishlistCount > 0 ? (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-gold text-[10px] font-bold text-ink">
                  {wishlistCount}
                </span>
              ) : null}
            </Link>
            <button
              type="button"
              onClick={openCart}
              aria-label={`Open cart, ${totalItems} items`}
              className="relative inline-flex h-9 w-9 items-center justify-center rounded-full bg-gold text-ink transition hover:bg-gold-deep hover:text-white md:h-10 md:w-10"
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
          <div className="absolute left-0 top-0 flex h-full w-[84%] max-w-xs flex-col bg-[#fffaf0] p-5 shadow-soft animate-rise">
            <div className="flex items-center justify-between">
              <p className="font-display text-2xl text-forest">Menu</p>
              <button type="button" onClick={closeMobileNav} aria-label="Close" className="text-ink/60">
                <IconClose />
              </button>
            </div>
            <nav className="mt-8 flex flex-col gap-2 text-base font-medium text-ink">
              <Link href="/shop" onClick={closeMobileNav} className="rounded-md px-2 py-2 hover:bg-gold/15">
                Shop
              </Link>
              {collections.map((collection) => {
                const expanded = mobileOpen === collection.slug;
                return (
                  <div key={collection.slug} className="rounded-md">
                    <div className="flex items-center justify-between">
                      <Link
                        href={`/shop/${collection.slug}`}
                        onClick={closeMobileNav}
                        className="flex-1 rounded-md px-2 py-2 hover:bg-gold/15"
                      >
                        {collection.title}
                      </Link>
                      <button
                        type="button"
                        aria-label={`Toggle ${collection.title} submenu`}
                        aria-expanded={expanded}
                        onClick={() =>
                          setMobileOpen(expanded ? null : collection.slug)
                        }
                        className="inline-flex h-9 w-9 items-center justify-center rounded-md text-ink/60 hover:bg-gold/15"
                      >
                        <IconChevronRight
                          className={`h-4 w-4 transition ${expanded ? "rotate-90" : ""}`}
                        />
                      </button>
                    </div>
                    {expanded ? (
                      <div className="ml-3 border-l border-gold/30 pl-3">
                        {collection.children.map((child) => (
                          <Link
                            key={child.slug}
                            href={`/shop/${collection.slug}/${child.slug}`}
                            onClick={closeMobileNav}
                            className="block rounded-md px-2 py-2 text-sm text-ink/70 hover:bg-gold/15 hover:text-gold-deep"
                          >
                            {child.title}
                          </Link>
                        ))}
                      </div>
                    ) : null}
                  </div>
                );
              })}
              <Link href="/wishlist" onClick={closeMobileNav} className="rounded-md px-2 py-2 hover:bg-gold/15">
                Wishlist
              </Link>
              <Link href="/cart" onClick={closeMobileNav} className="rounded-md px-2 py-2 hover:bg-gold/15">
                Cart
              </Link>
              <Link href="/checkout" onClick={closeMobileNav} className="rounded-md px-2 py-2 hover:bg-gold/15">
                Checkout
              </Link>
            </nav>
          </div>
        </div>
      ) : null}
    </>
  );
}
