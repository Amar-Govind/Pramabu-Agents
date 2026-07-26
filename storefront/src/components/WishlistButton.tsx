"use client";

import { useWishlist } from "@/store/wishlist";

export function WishlistButton({
  slug,
  className = "",
}: {
  slug: string;
  className?: string;
}) {
  const slugs = useWishlist((state) => state.slugs);
  const toggle = useWishlist((state) => state.toggle);
  const active = slugs.includes(slug);

  return (
    <button
      type="button"
      aria-label={active ? "Remove from wishlist" : "Add to wishlist"}
      onClick={() => toggle(slug)}
      className={`inline-flex h-10 w-10 items-center justify-center rounded-md border transition ${
        active
          ? "border-gold bg-gold/15 text-gold-deep"
          : "border-forest/15 bg-white text-forest hover:border-gold hover:text-gold-deep"
      } ${className}`}
    >
      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current" aria-hidden>
        <path d="M12 21s-6.7-4.35-9.33-8.1C.8 10.1 1.2 6.8 3.7 5.2c2.1-1.35 4.7-.7 6.1 1.15L12 8.2l2.2-1.85c1.4-1.85 4-2.5 6.1-1.15 2.5 1.6 2.9 4.9 1.03 7.7C18.7 16.65 12 21 12 21z" />
      </svg>
    </button>
  );
}
